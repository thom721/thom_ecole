from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MResource import Resource
from app.Models.MAssignment import Assignment
from app.Models.MQuiz import Quiz
from app.Models.MForum import Forum
from app.Models.MChoice import Choice
from app.Models.MLesson import Lesson
from app.Models.MWorkshop import Workshop
from app.Models.MLiveSession import LiveSession
from app.Models.MInteractiveVideo import InteractiveVideo
from app.Models.MCompletion import CompletionItemType
from app.Models.MAccessCondition import AccessCondition
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SAccessCondition import AccessConditionCreate, AccessConditionOut
from app.dependencies.auth import get_current_active_user, assert_course_role

router = APIRouter(tags=["access-conditions"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]

_ITEM_MODELS = {
    CompletionItemType.resource: Resource,
    CompletionItemType.assignment: Assignment,
    CompletionItemType.quiz: Quiz,
    CompletionItemType.forum: Forum,
    CompletionItemType.choice: Choice,
    CompletionItemType.lesson: Lesson,
    CompletionItemType.workshop: Workshop,
    CompletionItemType.live_session: LiveSession,
    CompletionItemType.interactive_video: InteractiveVideo,
}


def _resolve_course_id(db: Session, item_type: CompletionItemType, item_id: str) -> str:
    model = _ITEM_MODELS.get(item_type)
    if model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Type d'activité non pris en charge")
    item = db.query(model).filter(model.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activité introuvable")
    section = db.query(Section).filter(Section.id == item.section_id).first()
    return section.course_id


@router.get("/access-conditions/{item_type}/{item_id}", response_model=list[AccessConditionOut])
def list_conditions(
    item_type: CompletionItemType, item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course_id = _resolve_course_id(db, item_type, item_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return db.query(AccessCondition).filter(AccessCondition.item_type == item_type, AccessCondition.item_id == item_id).all()


@router.post("/access-conditions/{item_type}/{item_id}", response_model=AccessConditionOut, status_code=status.HTTP_201_CREATED)
def create_condition(
    item_type: CompletionItemType, item_id: str, data: AccessConditionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course_id = _resolve_course_id(db, item_type, item_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    # Toutes les conditions d'une même activité partagent la même logique
    # ET/OU (voir MAccessCondition.py) — imposée ici, pas laissée au hasard
    # de l'ordre de création.
    existing = db.query(AccessCondition).filter(AccessCondition.item_type == item_type, AccessCondition.item_id == item_id).first()
    if existing is not None and existing.logic != data.logic:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"Cette activité utilise déjà la logique « {existing.logic.value} » — toutes ses conditions doivent la partager")

    condition = AccessCondition(item_type=item_type, item_id=item_id, **data.model_dump())
    db.add(condition)
    db.commit()
    db.refresh(condition)
    return condition


@router.delete("/access-conditions/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_condition(
    condition_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    condition = db.query(AccessCondition).filter(AccessCondition.id == condition_id).first()
    if condition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition introuvable")
    course_id = _resolve_course_id(db, condition.item_type, condition.item_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    db.delete(condition)
    db.commit()
