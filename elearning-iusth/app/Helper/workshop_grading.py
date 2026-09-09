"""Agrégation des notes d'atelier — formules reproduites fidèlement depuis
le vrai code source Moodle (`mod/workshop/form/*/lib.php::calculate_peer_grade()`
et `mod/workshop/eval/best/lib.php::update_grading_grades()`, lus
directement dans le conteneur `moodle-iusth`, voir plan Épic 10).

Décision d'architecture : tout est calculé EN DIRECT ici, jamais mis en
cache dans une colonne — cohérent avec `resolve_letter` (Épic 8),
`_best_quiz_attempts`/`_best_lesson_attempts` (Phase 3 / Épic 9). Le vrai
Moodle cache ces valeurs (`workshop_submissions.grade`,
`workshop_assessments.grade`/`gradinggrade`, `workshop_aggregations`) et
les recalcule par lots — un besoin de performance à l'échelle MySQL de
Moodle sans intérêt ici.
"""

from decimal import Decimal

from app.Models.MWorkshop import WorkshopStrategy


def _dim_min_max(dimension):
    """(min, max) de la note BRUTE d'une dimension, selon la stratégie —
    utilisé par `evaluate_best` pour normaliser sur 0-100."""
    strategy = dimension.workshop.strategy
    if strategy == WorkshopStrategy.accumulative:
        return Decimal("0"), (dimension.grade or Decimal("0"))
    if strategy == WorkshopStrategy.numerrors:
        return Decimal("0"), Decimal("1")
    if strategy == WorkshopStrategy.rubric:
        levels = dimension.levels
        if not levels:
            return Decimal("0"), Decimal("0")
        grades = [lvl.grade for lvl in levels]
        return min(grades), max(grades)
    # comments : toujours 100 (voir save_assessment réel, aucune variation possible)
    return Decimal("100"), Decimal("100")


def _errors_to_grade(workshop, error_count: int) -> Decimal:
    """Reproduit `errors_to_grade()` : 0 erreur = 100% toujours ; sinon la
    ligne définie la plus proche EN DESSOUS du nombre d'erreurs s'applique
    (palier descendant), clampé 0-100."""
    if error_count <= 0:
        return Decimal("100")
    grade = Decimal("100")
    rows = sorted(workshop.numerrors_map, key=lambda r: r.error_count)
    for row in rows:
        if row.error_count <= error_count:
            grade = row.grade_percent
        else:
            break
    return max(Decimal("0"), min(Decimal("100"), grade))


def assessment_grade_percent(assessment) -> Decimal | None:
    """Note (0-100%) donnée par CETTE évaluation à la soumission, agrégée
    sur ses dimensions selon la stratégie de l'atelier."""
    workshop = assessment.submission.workshop
    grades = {g.dimension_id: g for g in assessment.grades}
    if not grades:
        return None

    if workshop.strategy == WorkshopStrategy.comments:
        # Comportement réel vérifié dans save_assessment() : toujours 100%,
        # dès qu'au moins une ligne de note existe.
        return Decimal("100")

    if workshop.strategy == WorkshopStrategy.accumulative:
        sum_grades = Decimal("0")
        sum_weights = Decimal("0")
        for dim in workshop.dimensions:
            g = grades.get(dim.id)
            if g is None or g.grade is None:
                continue
            if dim.weight == 0 or not dim.grade:
                continue
            sum_grades += (g.grade / dim.grade) * dim.weight * 100
            sum_weights += dim.weight
        if sum_weights == 0:
            return Decimal("0")
        return sum_grades / sum_weights

    if workshop.strategy == WorkshopStrategy.numerrors:
        sum_errors = 0
        for dim in workshop.dimensions:
            g = grades.get(dim.id)
            if g is None or g.grade is None:
                continue
            if g.grade != 1:
                sum_errors += dim.weight
        return _errors_to_grade(workshop, sum_errors)

    if workshop.strategy == WorkshopStrategy.rubric:
        sum_grades = Decimal("0")
        sum_min = Decimal("0")
        sum_max = Decimal("0")
        for dim in workshop.dimensions:
            g = grades.get(dim.id)
            if g is None or g.grade is None or not dim.levels:
                continue
            level_grades = [lvl.grade for lvl in dim.levels]
            sum_grades += g.grade
            sum_min += min(level_grades)
            sum_max += max(level_grades)
        if sum_max - sum_min <= 0:
            return None
        return 100 * (sum_grades - sum_min) / (sum_max - sum_min)

    return None


def submission_grade_percent(submission) -> Decimal | None:
    """Moyenne pondérée (par `assessment.weight`) des notes (0-100%) de
    toutes les évaluations de cette soumission."""
    sum_grades = Decimal("0")
    sum_weights = Decimal("0")
    for assessment in submission.assessments:
        if assessment.weight == 0:
            continue
        percent = assessment_grade_percent(assessment)
        if percent is None:
            continue
        sum_grades += percent * assessment.weight
        sum_weights += assessment.weight
    if sum_weights == 0:
        return None
    return sum_grades / sum_weights


def submission_final_grade(submission) -> Decimal | None:
    if submission.grade_override is not None:
        return submission.grade_override
    percent = submission_grade_percent(submission)
    if percent is None:
        return None
    return (percent * submission.workshop.grade / 100).quantize(Decimal("0.01"))


def evaluate_best(submission) -> dict[str, Decimal]:
    """Reproduit `workshop_best_evaluation::process_assessments()` pour
    UNE soumission : renvoie {assessment_id: note_qualité (0-100)}."""
    workshop = submission.workshop
    comparison = Decimal(workshop.comparison)
    assessments = [a for a in submission.assessments if a.weight != 0]
    if not assessments:
        return {}

    dims = {d.id: d for d in workshop.dimensions}
    dim_bounds = {did: _dim_min_max(d) for did, d in dims.items()}

    # normalise chaque note de dimension sur 0-100
    norm = {}  # assessment_id -> {dimension_id: note normalisée}
    weights = {}
    for a in assessments:
        weights[a.id] = Decimal(a.weight)
        norm[a.id] = {}
        for g in a.grades:
            if g.grade is None or g.dimension_id not in dim_bounds:
                continue
            dmin, dmax = dim_bounds[g.dimension_id]
            if dmin == dmax:
                norm[a.id][g.dimension_id] = dmax
            else:
                norm[a.id][g.dimension_id] = (g.grade - dmin) / (dmax - dmin) * 100

    dim_ids = list(dims.keys())

    # évaluation moyenne hypothétique (pondérée)
    sum_weight = sum(weights.values())
    if sum_weight == 0:
        return {}
    average = {}
    for did in dim_ids:
        s = sum(norm[aid].get(did, Decimal("0")) * weights[aid] for aid in norm)
        average[did] = s / sum_weight

    # variance pondérée par dimension (population), plancher 0.01
    variance = {}
    for did in dim_ids:
        mean = average[did]
        s = sum(weights[aid] * (norm[aid].get(did, Decimal("0")) - mean) ** 2 for aid in norm)
        variance[did] = max(s / sum_weight, Decimal("0.01"))

    def distance(a_grades: dict, ref_grades: dict) -> Decimal | None:
        # `dimension.weight` vaut toujours 1 pour comments/rubric (jamais
        # exposé comme réglable pour ces stratégies, comme le vrai
        # get_dimensions_info() de Moodle) — pas de cas particulier ici.
        total = Decimal("0")
        n = Decimal("0")
        for did in dim_ids:
            weight = Decimal(dims[did].weight)
            n += weight
            agrade = a_grades.get(did, Decimal("0"))
            rgrade = ref_grades.get(did, Decimal("0"))
            if agrade != rgrade:
                var = variance[did]
                reldelta = (agrade - rgrade) ** 2 / (comparison * var)
                total += abs(agrade - rgrade) * reldelta * weight
        if n == 0:
            return None
        return total / n

    # distance de chaque évaluation à la moyenne hypothétique
    distances_to_average = {aid: distance(norm[aid], average) for aid in norm}
    valid = {aid: d for aid, d in distances_to_average.items() if d is not None}
    if not valid:
        return {}
    best_distance = min(valid.values())
    best_ids = [aid for aid, d in valid.items() if d == best_distance]

    # distance de chaque évaluation à la plus proche des "meilleures"
    final_distances = {}
    for best_id in best_ids:
        for aid in norm:
            d = distance(norm[aid], norm[best_id])
            if d is not None and (aid not in final_distances or d < final_distances[aid]):
                final_distances[aid] = d

    result = {}
    for aid, d in final_distances.items():
        grading_grade = max(Decimal("0"), min(Decimal("100"), Decimal("100") - d))
        result[aid] = grading_grade
    return result


def assessment_final_gradinggrade_percent(assessment) -> Decimal | None:
    if assessment.gradinggrade_override is not None:
        return assessment.gradinggrade_override
    scores = evaluate_best(assessment.submission)
    return scores.get(assessment.id)


def reviewer_final_gradinggrade(workshop, reviewer_id: str) -> Decimal | None:
    """Moyenne des notes de qualité (ou leur remplacement) de toutes les
    évaluations de ce reviewer sur cet atelier, mise à l'échelle par
    `workshop.gradinggrade`."""
    percents = []
    for submission in workshop.submissions:
        for assessment in submission.assessments:
            if assessment.reviewer_id != reviewer_id:
                continue
            percent = assessment_final_gradinggrade_percent(assessment)
            if percent is not None:
                percents.append(percent)
    if not percents:
        return None
    mean_percent = sum(percents) / len(percents)
    return (mean_percent * workshop.gradinggrade / 100).quantize(Decimal("0.01"))
