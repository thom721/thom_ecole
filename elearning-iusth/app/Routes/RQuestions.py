import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MQuestion import Question, QuestionOption, QuestionAcceptedAnswer, QuestionType
from app.Models.MQuestionCalculated import QuestionCalculatedDataset
from app.Models.MQuestionCloze import QuestionClozePart, CLOZE_SUB_TYPES
from app.Models.MQuiz import QuizQuestion, QuizResponse
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SQuestion import (
    QuestionCreate, QuestionUpdate, QuestionOut, QuestionOptionOut,
    NumericalAcceptedAnswerOut, QuestionCalculatedDatasetOut, QuestionClozePartOut,
)
from app.dependencies.auth import require_course_role, assert_course_role, get_current_active_user

router = APIRouter(tags=["questions"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]

# Types dont les réponses/options vivent dans QuestionOption (voir modèle) —
# ordering/drag_and_drop réutilisent le même stockage que matching.
_OPTION_BASED_TYPES = (QuestionType.multiple_choice, QuestionType.true_false,
                        QuestionType.matching, QuestionType.ordering, QuestionType.drag_and_drop)


def _to_out(question: Question) -> QuestionOut:
    return QuestionOut(
        id=question.id,
        course_id=question.course_id,
        category_id=question.category_id,
        question_type=question.question_type,
        question_text=question.question_text,
        default_points=question.default_points,
        is_active=question.is_active,
        calculated_formula=question.calculated_formula,
        calculated_tolerance=question.calculated_tolerance,
        options=[QuestionOptionOut.model_validate(o) for o in question.options],
        accepted_answers=[a.answer_text for a in question.accepted_answers if a.tolerance is None],
        numerical_answers=[
            NumericalAcceptedAnswerOut(id=a.id, value=a.answer_text, tolerance=a.tolerance)
            for a in question.accepted_answers if a.tolerance is not None
        ],
        calculated_datasets=[QuestionCalculatedDatasetOut.model_validate(d) for d in question.calculated_datasets],
        cloze_parts=[QuestionClozePartOut.model_validate(p) for p in question.cloze_parts],
    )


def _validate_payload(data: QuestionCreate) -> None:
    qtype = data.question_type

    if qtype == QuestionType.essay:
        return

    if qtype in _OPTION_BASED_TYPES:
        if not data.options:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Ce type de question nécessite des options")
        return

    if qtype == QuestionType.short_answer:
        if not data.accepted_answers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Ce type de question nécessite des réponses acceptées")
        return

    if qtype == QuestionType.numerical:
        if not data.numerical_answers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Ce type de question nécessite au moins une valeur acceptée")
        return

    if qtype == QuestionType.calculated:
        if not data.calculated_datasets:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Ce type de question nécessite au moins une variable")
        if not data.calculated_formula:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Ce type de question nécessite une formule de correction")
        lengths = {len(d.values) for d in data.calculated_datasets}
        if len(lengths) != 1 or 0 in lengths:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Toutes les variables doivent avoir le même nombre de valeurs candidates (non vide)")
        declared = {d.variable_name for d in data.calculated_datasets}
        # Chaque {variable} référencée dans le texte affiché OU dans la
        # formule de correction doit avoir un jeu de valeurs déclaré —
        # sinon substitution/évaluation impossible au moment de la note.
        referenced_in_text = {name for _, name, _, _ in string.Formatter().parse(data.question_text) if name}
        referenced_in_formula = {name for _, name, _, _ in string.Formatter().parse(data.calculated_formula) if name}
        missing = (referenced_in_text | referenced_in_formula) - declared
        if missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail=f"Variable(s) référencée(s) sans jeu de valeurs : {', '.join(missing)}")
        return

    if qtype == QuestionType.multianswer:
        if not data.cloze_parts:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Ce type de question nécessite au moins une sous-question")
        for part in data.cloze_parts:
            if part.sub_type not in CLOZE_SUB_TYPES:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                     detail=f"Sous-type de sous-question non supporté : {part.sub_type}")
        return


def _persist_type_specific(db: Session, question: Question, data: QuestionCreate | QuestionUpdate, is_create: bool) -> None:
    """Remplacement intégral des collections fournies (même convention que
    options/accepted_answers déjà en place)."""
    if is_create or data.options is not None:
        for opt in question.options:
            db.delete(opt)
        db.flush()
        for opt in (data.options or []):
            db.add(QuestionOption(question_id=question.id, **opt.model_dump()))

    if is_create or data.accepted_answers is not None or data.numerical_answers is not None:
        for ans in question.accepted_answers:
            db.delete(ans)
        db.flush()
        for ans in (data.accepted_answers or []):
            db.add(QuestionAcceptedAnswer(question_id=question.id, answer_text=ans))
        for num in (data.numerical_answers or []):
            db.add(QuestionAcceptedAnswer(question_id=question.id, answer_text=str(num.value), tolerance=num.tolerance))

    if is_create or data.calculated_datasets is not None:
        for ds in question.calculated_datasets:
            db.delete(ds)
        db.flush()
        for ds in (data.calculated_datasets or []):
            db.add(QuestionCalculatedDataset(
                question_id=question.id, variable_name=ds.variable_name,
                values=[float(v) for v in ds.values],
            ))

    if is_create or data.cloze_parts is not None:
        for part in question.cloze_parts:
            db.delete(part)
        db.flush()
        for part in (data.cloze_parts or []):
            db.add(QuestionClozePart(
                question_id=question.id, position=part.position, sub_type=part.sub_type,
                correct_answers=part.correct_answers, points=part.points,
            ))


@router.get("/courses/{course_id}/questions", response_model=list[QuestionOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def list_questions(
    course_id: str,
    category_id: str | None = None,
    question_type: QuestionType | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Question).filter(Question.course_id == course_id)
    if category_id:
        query = query.filter(Question.category_id == category_id)
    if question_type:
        query = query.filter(Question.question_type == question_type)
    return [_to_out(q) for q in query.all()]


@router.post("/courses/{course_id}/questions", response_model=QuestionOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def create_question(
    course_id: str, data: QuestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _validate_payload(data)

    question = Question(
        course_id=course_id, category_id=data.category_id, question_type=data.question_type,
        question_text=data.question_text, default_points=data.default_points,
        is_active=data.is_active, created_by=current_user.id,
        calculated_formula=data.calculated_formula, calculated_tolerance=data.calculated_tolerance,
    )
    db.add(question)
    db.flush()

    _persist_type_specific(db, question, data, is_create=True)

    db.commit()
    db.refresh(question)
    return _to_out(question)


def _get_question_or_404(db: Session, question_id: str) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question introuvable")
    return question


@router.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(
    question_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    question = _get_question_or_404(db, question_id)
    assert_course_role(db, current_user, question.course_id, _TEACHING_ROLES)
    return _to_out(question)


@router.patch("/questions/{question_id}", response_model=QuestionOut)
def update_question(
    question_id: str, data: QuestionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    question = _get_question_or_404(db, question_id)
    assert_course_role(db, current_user, question.course_id, _TEACHING_ROLES)

    simple_fields = data.model_dump(exclude_unset=True, exclude={
        "options", "accepted_answers", "numerical_answers", "calculated_datasets", "cloze_parts",
    })
    for field, value in simple_fields.items():
        setattr(question, field, value)

    _persist_type_specific(db, question, data, is_create=False)

    db.commit()
    db.refresh(question)
    return _to_out(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    question = _get_question_or_404(db, question_id)
    assert_course_role(db, current_user, question.course_id, _TEACHING_ROLES)

    referenced = (
        db.query(QuizQuestion).filter(QuizQuestion.question_id == question_id).first() is not None
        or db.query(QuizResponse).filter(QuizResponse.question_id == question_id).first() is not None
    )
    if referenced:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Question utilisée dans un quiz ou une tentative — désactivez-la plutôt que de la supprimer")

    db.delete(question)
    db.commit()
