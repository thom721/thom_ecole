from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MChoice import Choice, ChoiceOption, ChoiceAnswer, ChoiceResultsDisplay
from app.Models.MGroup import GroupMode
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SChoice import (
    ChoiceCreate, ChoiceUpdate, ChoiceOut, ChoiceDetailOut, ChoiceOptionResultOut, ChoiceRespondIn,
)
from app.Models.MCompletion import CompletionItemType, CompletionMode
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.groups import users_share_a_group
from app.Helper.access_conditions import is_item_accessible
from app.Helper.completion_config import get_completion_mode
from app.Helper.completion import mark_complete_if_absent

router = APIRouter(tags=["choices"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_choice_and_course(db: Session, choice_id: str) -> tuple[Choice, str]:
    choice = db.query(Choice).filter(Choice.id == choice_id).first()
    if choice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sondage introuvable")
    section = db.query(Section).filter(Section.id == choice.section_id).first()
    return choice, section.course_id


def _results_visible_for(choice: Choice, is_teaching: bool, has_answered: bool) -> bool:
    """Enseignant/manager/admin voient toujours les résultats (comme le
    rapport de réponses Moodle) — results_display ne restreint que la vue
    étudiant."""
    if is_teaching:
        return True
    if choice.results_display == ChoiceResultsDisplay.always:
        return True
    if choice.results_display == ChoiceResultsDisplay.after_answering:
        return has_answered
    if choice.results_display == ChoiceResultsDisplay.after_close:
        now = datetime.now(timezone.utc)
        return choice.closes_at is not None and now > choice.closes_at.replace(tzinfo=timezone.utc)
    return False  # never


def _is_teaching(db: Session, current_user: User, course_id: str) -> bool:
    if current_user.system_role == SystemRole.admin:
        return True
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    return enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES


def _serialize_detail(db: Session, choice: Choice, current_user: User, course_id: str) -> ChoiceDetailOut:
    my_answers = db.query(ChoiceAnswer).filter(
        ChoiceAnswer.choice_id == choice.id, ChoiceAnswer.user_id == current_user.id,
    ).all()
    has_answered = len(my_answers) > 0
    is_teaching = _is_teaching(db, current_user, course_id)
    visible = _results_visible_for(choice, is_teaching, has_answered)
    accessible, access_reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.choice, choice.id)

    options_out = []
    for option in choice.options:
        vote_count = None
        respondents = None
        if visible:
            answers = [a for a in choice.answers if a.option_id == option.id]
            if choice.group_mode == GroupMode.separate_groups and not is_teaching:
                # Filtré à la lecture par appartenance de groupe du
                # répondant — jamais un tag figé sur la réponse (voir plan
                # Épic 5), cohérent avec le filtrage forum ci-dessus.
                answers = [
                    a for a in answers
                    if users_share_a_group(db, current_user.id, a.user_id, course_id, choice.grouping_id)
                ]
            vote_count = len(answers)
            if not choice.anonymous_results:
                users = db.query(User).filter(User.id.in_([a.user_id for a in answers])).all()
                respondents = [f"{u.first_name} {u.last_name}" for u in users]
        options_out.append(ChoiceOptionResultOut(
            id=option.id, option_text=option.option_text, max_answers=option.max_answers,
            sort_order=option.sort_order, vote_count=vote_count, respondents=respondents,
        ))

    return ChoiceDetailOut(
        id=choice.id, section_id=choice.section_id, title=choice.title, description=choice.description,
        is_visible=choice.is_visible, allow_multiple=choice.allow_multiple, allow_update=choice.allow_update,
        limit_answers=choice.limit_answers, results_display=choice.results_display,
        anonymous_results=choice.anonymous_results, show_unanswered=choice.show_unanswered,
        opens_at=choice.opens_at, closes_at=choice.closes_at,
        group_mode=choice.group_mode, grouping_id=choice.grouping_id,
        options=options_out, my_answer_option_ids=[a.option_id for a in my_answers], results_visible=visible,
        access_restricted=not accessible, access_reasons=access_reasons,
    )


@router.post("/sections/{section_id}/choices", response_model=ChoiceOut, status_code=status.HTTP_201_CREATED)
def create_choice(
    section_id: str, data: ChoiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    payload = data.model_dump(exclude={"options"})
    choice = Choice(section_id=section_id, **payload)
    db.add(choice)
    db.flush()

    for opt in data.options:
        db.add(ChoiceOption(choice_id=choice.id, **opt.model_dump()))

    db.commit()
    db.refresh(choice)
    return choice


@router.get("/choices/{choice_id}", response_model=ChoiceDetailOut)
def get_choice(
    choice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    choice, course_id = _get_choice_and_course(db, choice_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return _serialize_detail(db, choice, current_user, course_id)


@router.patch("/choices/{choice_id}", response_model=ChoiceOut)
def update_choice(
    choice_id: str, data: ChoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    choice, course_id = _get_choice_and_course(db, choice_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    payload = data.model_dump(exclude_unset=True)
    options = payload.pop("options", None)
    for field, value in payload.items():
        setattr(choice, field, value)

    if options is not None:
        for opt in list(choice.options):
            db.delete(opt)
        db.flush()
        for opt in options:
            db.add(ChoiceOption(choice_id=choice.id, **opt))

    db.commit()
    db.refresh(choice)
    return choice


@router.delete("/choices/{choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_choice(
    choice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    choice, course_id = _get_choice_and_course(db, choice_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if db.query(ChoiceAnswer).filter(ChoiceAnswer.choice_id == choice_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce sondage a déjà des réponses — suppression bloquée")
    db.delete(choice)
    db.commit()


@router.post("/choices/{choice_id}/respond", response_model=ChoiceDetailOut)
def respond(
    choice_id: str, data: ChoiceRespondIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    choice, course_id = _get_choice_and_course(db, choice_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    if not choice.is_visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sondage introuvable")

    accessible, access_reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.choice, choice_id)
    if not accessible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="; ".join(access_reasons) or "Accès restreint")

    now = datetime.now(timezone.utc)
    if choice.opens_at and now < choice.opens_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce sondage n'est pas encore ouvert")
    if choice.closes_at and now > choice.closes_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce sondage est fermé")

    if not data.option_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choisissez au moins une option")
    if not choice.allow_multiple and len(data.option_ids) > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce sondage n'accepte qu'une seule réponse")

    valid_option_ids = {o.id for o in choice.options}
    if not set(data.option_ids).issubset(valid_option_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Option invalide pour ce sondage")

    existing = db.query(ChoiceAnswer).filter(
        ChoiceAnswer.choice_id == choice_id, ChoiceAnswer.user_id == current_user.id,
    ).all()
    if existing and not choice.allow_update:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vous avez déjà répondu à ce sondage")

    if choice.limit_answers:
        for option_id in data.option_ids:
            already_mine = any(a.option_id == option_id for a in existing)
            if already_mine:
                continue
            option = next(o for o in choice.options if o.id == option_id)
            if option.max_answers is not None:
                current_count = db.query(ChoiceAnswer).filter(ChoiceAnswer.option_id == option_id).count()
                if current_count >= option.max_answers:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                         detail=f"L'option « {option.option_text} » est complète")

    for a in existing:
        db.delete(a)
    db.flush()
    for option_id in data.option_ids:
        db.add(ChoiceAnswer(choice_id=choice_id, option_id=option_id, user_id=current_user.id))
    db.commit()
    db.refresh(choice)

    if get_completion_mode(db, CompletionItemType.choice, choice_id) == CompletionMode.automatic:
        mark_complete_if_absent(db, current_user.id, CompletionItemType.choice, choice_id)

    return _serialize_detail(db, choice, current_user, course_id)


@router.delete("/choices/{choice_id}/respond", response_model=ChoiceDetailOut)
def retract(
    choice_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    choice, course_id = _get_choice_and_course(db, choice_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    if not choice.allow_update:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce sondage n'autorise pas la modification du vote")

    for a in list(choice.answers):
        if a.user_id == current_user.id:
            db.delete(a)
    db.commit()
    db.refresh(choice)

    return _serialize_detail(db, choice, current_user, course_id)
