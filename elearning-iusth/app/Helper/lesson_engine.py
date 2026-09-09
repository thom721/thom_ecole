from decimal import Decimal

from app.Models.MLesson import LessonPage, LessonPageType, LessonAnswer, LessonJumpType, LessonPageAttempt


def resolve_answer(page: LessonPage, answer_id: str | None, answer_text: str | None):
    """Résout la réponse retenue pour cette soumission + sa correction.
    Renvoie (matched_answer, is_correct, points_awarded, stored_text).
    Voir plan Épic 9 : pour short_answer/numerical, aucune correspondance
    -> la DERNIÈRE réponse (tri par sort_order) sert de générique/par
    défaut, comportement réel de Moodle."""
    answers = sorted(page.answers, key=lambda a: a.sort_order)

    if page.page_type == LessonPageType.content:
        matched = next((a for a in answers if a.id == answer_id), None)
        return matched, None, None, None

    if page.page_type == LessonPageType.essay:
        matched = answers[0] if answers else None
        return matched, None, None, answer_text

    if page.page_type in (LessonPageType.true_false, LessonPageType.multiple_choice):
        matched = next((a for a in answers if a.id == answer_id), None)
        is_correct = matched is not None and matched.is_correct
        points = page.points if is_correct else Decimal("0")
        return matched, is_correct, points, None

    if page.page_type == LessonPageType.short_answer:
        submitted = (answer_text or "").strip().lower()
        matched = next(
            (a for a in answers if a.answer_text and a.answer_text.strip().lower() == submitted),
            None,
        )
        if matched is None and answers:
            matched = answers[-1]
        is_correct = matched is not None and matched.is_correct
        points = page.points if is_correct else Decimal("0")
        return matched, is_correct, points, answer_text

    if page.page_type == LessonPageType.numerical:
        try:
            submitted_value = float(answer_text)
        except (TypeError, ValueError):
            submitted_value = None
        matched = None
        if submitted_value is not None:
            for a in answers:
                if a.tolerance is None or a.answer_text is None:
                    continue
                try:
                    target = float(a.answer_text)
                except ValueError:
                    continue
                if abs(submitted_value - target) <= float(a.tolerance):
                    matched = a
                    break
        if matched is None and answers:
            matched = answers[-1]
        is_correct = matched is not None and matched.is_correct
        points = page.points if is_correct else Decimal("0")
        return matched, is_correct, points, answer_text

    return None, None, None, answer_text


def resolve_next_page(page: LessonPage, matched_answer: LessonAnswer | None) -> tuple[str | None, bool]:
    """Renvoie (next_page_id, end_of_lesson) à partir de la réponse
    retenue. Les pages sont ordonnées par sort_order au sein de la leçon."""
    all_pages = sorted(page.lesson.pages, key=lambda p: p.sort_order)
    index = next((i for i, p in enumerate(all_pages) if p.id == page.id), None)

    jump_type = matched_answer.jump_type if matched_answer else LessonJumpType.next_page
    jump_to_page_id = matched_answer.jump_to_page_id if matched_answer else None

    if jump_type == LessonJumpType.end_of_lesson:
        return None, True
    if jump_type == LessonJumpType.specific_page:
        return jump_to_page_id, False
    if jump_type == LessonJumpType.previous_page:
        if index is None or index == 0:
            return page.id, False  # pas de page précédente : reste sur place
        return all_pages[index - 1].id, False
    # next_page (défaut)
    if index is None or index + 1 >= len(all_pages):
        return None, True  # dernière page : fin de leçon implicite
    return all_pages[index + 1].id, False


def compute_score(attempt) -> tuple[Decimal, bool]:
    """(score, has_pending_essay). Le dernier essai (try_number le plus
    élevé) par page compte pour la note — comportement fixe, pas de
    bascule `modattempts` (voir plan Épic 9)."""
    last_by_page: dict[str, LessonPageAttempt] = {}
    for pa in attempt.page_attempts:
        current = last_by_page.get(pa.page_id)
        if current is None or pa.try_number > current.try_number:
            last_by_page[pa.page_id] = pa

    has_pending_essay = False
    score = Decimal("0")
    for pa in last_by_page.values():
        if pa.page.page_type == LessonPageType.essay and pa.points_awarded is None:
            has_pending_essay = True
            continue
        score += pa.points_awarded or Decimal("0")
    return score, has_pending_essay
