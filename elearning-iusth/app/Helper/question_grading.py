from decimal import Decimal

from app.Models.MQuestion import Question, QuestionType
from app.Models.MQuiz import QuizResponse


def _grade_choice(question: Question, response: QuizResponse, data: dict) -> None:
    selected_id = data.get("option_id")
    correct_option = next((o for o in question.options if o.is_correct), None)
    is_correct = selected_id is not None and correct_option is not None and selected_id == correct_option.id
    response.is_correct = is_correct
    response.points_awarded = response.points if is_correct else 0


def _grade_short_answer(question: Question, response: QuizResponse, data: dict) -> None:
    submitted = (data.get("text") or "").strip().lower()
    accepted = {a.answer_text.strip().lower() for a in question.accepted_answers if a.tolerance is None}
    is_correct = submitted != "" and submitted in accepted
    response.is_correct = is_correct
    response.points_awarded = response.points if is_correct else 0


def _grade_matching_or_drag(question: Question, response: QuizResponse, data: dict) -> None:
    pairs = data.get("pairs") or {}
    all_correct = len(pairs) == len(question.options) and all(
        pairs.get(o.id) == o.match_text for o in question.options
    )
    response.is_correct = all_correct
    response.points_awarded = response.points if all_correct else 0


def _grade_numerical(question: Question, response: QuizResponse, data: dict) -> None:
    try:
        submitted = float(data.get("value"))
    except (TypeError, ValueError):
        response.is_correct = False
        response.points_awarded = 0
        return

    is_correct = False
    for accepted in question.accepted_answers:
        if accepted.tolerance is None:
            continue
        try:
            target = float(accepted.answer_text)
        except ValueError:
            continue
        if abs(submitted - target) <= float(accepted.tolerance):
            is_correct = True
            break
    response.is_correct = is_correct
    response.points_awarded = response.points if is_correct else 0


def _grade_calculated(question: Question, response: QuizResponse, data: dict) -> None:
    """La valeur attendue est recalculée depuis `calculated_formula` avec
    les variables figées dans `response.resolved_data` au démarrage de la
    tentative — jamais un nouveau tirage. Évaluation arithmétique restreinte
    (aucun builtin, uniquement les variables substituées en littéraux)."""
    try:
        submitted = float(data.get("value"))
    except (TypeError, ValueError):
        response.is_correct = False
        response.points_awarded = 0
        return

    try:
        formula = question.calculated_formula.format(**(response.resolved_data or {}))
        expected = float(eval(formula, {"__builtins__": {}}, {}))
    except Exception:
        response.is_correct = False
        response.points_awarded = 0
        return

    tolerance = float(question.calculated_tolerance) if question.calculated_tolerance is not None else 0.0
    is_correct = abs(submitted - expected) <= tolerance
    response.is_correct = is_correct
    response.points_awarded = response.points if is_correct else 0


def _grade_multianswer(question: Question, response: QuizResponse, data: dict) -> None:
    """Chaque sous-question cloze est corrigée indépendamment ;
    points_awarded = somme pondérée des sous-questions correctes (jamais
    tout-ou-rien, contrairement aux autres types objectifs)."""
    submitted_parts = data.get("parts") or {}
    total_points = sum(p.points for p in question.cloze_parts) or 1
    earned = 0
    all_correct = True

    for part in question.cloze_parts:
        submitted = submitted_parts.get(str(part.position))
        correct = False
        if part.sub_type == QuestionType.multiple_choice:
            correct = submitted is not None and int(submitted) == part.correct_answers.get("correct_index")
        elif part.sub_type == QuestionType.short_answer:
            accepted = {a.strip().lower() for a in part.correct_answers.get("accepted", [])}
            correct = submitted is not None and str(submitted).strip().lower() in accepted
        elif part.sub_type == QuestionType.numerical:
            try:
                value = float(submitted)
                target = float(part.correct_answers.get("value"))
                tolerance = float(part.correct_answers.get("tolerance", 0))
                correct = abs(value - target) <= tolerance
            except (TypeError, ValueError):
                correct = False

        if correct:
            earned += float(part.points)
        else:
            all_correct = False

    response.is_correct = all_correct
    fraction = Decimal(str(earned)) / Decimal(str(total_points))
    response.points_awarded = (response.points * fraction).quantize(Decimal("0.01"))


def _longest_increasing_subsequence_length(ranks: list[int]) -> int:
    """O(n log n), n toujours petit ici (nombre d'options d'une question)."""
    import bisect

    tails: list[int] = []
    for rank in ranks:
        i = bisect.bisect_left(tails, rank)
        if i == len(tails):
            tails.append(rank)
        else:
            tails[i] = rank
    return len(tails)


def _grade_ordering(question: Question, response: QuizResponse, data: dict) -> None:
    """Note partielle par « plus longue sous-séquence bien ordonnée » —
    jamais tout-ou-rien : un item mal placé ne pénalise pas ses voisins
    correctement enchaînés (voir plan Épic 1)."""
    correct_order = [o.id for o in sorted(question.options, key=lambda o: o.sort_order)]
    rank_of = {option_id: i for i, option_id in enumerate(correct_order)}
    submitted_order = data.get("order") or []

    if sorted(submitted_order) != sorted(correct_order):
        response.is_correct = False
        response.points_awarded = 0
        return

    ranks = [rank_of[option_id] for option_id in submitted_order]
    lis_length = _longest_increasing_subsequence_length(ranks)
    fraction = Decimal(lis_length) / Decimal(len(correct_order)) if correct_order else Decimal(0)

    response.is_correct = fraction == 1
    response.points_awarded = (response.points * fraction).quantize(Decimal("0.01"))


_GRADERS = {
    QuestionType.multiple_choice: _grade_choice,
    QuestionType.true_false: _grade_choice,
    QuestionType.short_answer: _grade_short_answer,
    QuestionType.matching: _grade_matching_or_drag,
    QuestionType.drag_and_drop: _grade_matching_or_drag,
    QuestionType.numerical: _grade_numerical,
    QuestionType.calculated: _grade_calculated,
    QuestionType.multianswer: _grade_multianswer,
    QuestionType.ordering: _grade_ordering,
}


def auto_grade(question: Question, response: QuizResponse) -> None:
    """Corrige automatiquement tous les types objectifs. L'essai reste
    toujours non noté (is_correct=None, points_awarded=None) — correction
    manuelle obligatoire (voir RQuizAttempts.py::grade_response)."""
    if question.question_type == QuestionType.essay:
        return
    grader = _GRADERS.get(question.question_type)
    if grader is None:
        return
    grader(question, response, response.answer_data or {})
