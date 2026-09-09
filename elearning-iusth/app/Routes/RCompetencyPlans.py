from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCompetency import Plan, PlanCompetency, UserCompetency, Competency
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SCompetency import PlanCreate, PlanUpdate, PlanOut, PlanDetailOut, PlanCompetencyOut
from app.dependencies.auth import get_current_active_user

router = APIRouter(tags=["competency-plans"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _is_teacher_or_admin(current_user: User) -> bool:
    return current_user.system_role in (SystemRole.teacher, SystemRole.admin)


def _to_detail(db: Session, plan: Plan) -> PlanDetailOut:
    competencies = []
    for pc in plan.competencies:
        uc = db.query(UserCompetency).filter(
            UserCompetency.user_id == plan.user_id, UserCompetency.competency_id == pc.competency_id,
        ).first()
        competencies.append(PlanCompetencyOut(
            id=pc.id, competency_id=pc.competency_id, competency_name=pc.competency.name,
            proficiency=uc.proficiency if uc else None, grade_rank=uc.grade_rank if uc else None,
        ))
    return PlanDetailOut(
        id=plan.id, user_id=plan.user_id, name=plan.name, description=plan.description,
        status=plan.status, due_date=plan.due_date, reviewer_id=plan.reviewer_id, competencies=competencies,
    )


@router.get("/plans/mine", response_model=list[PlanOut])
def my_plans(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return db.query(Plan).filter(Plan.user_id == current_user.id).all()


@router.post("/plans", response_model=PlanOut, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: PlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    target_user_id = data.user_id or current_user.id
    if data.user_id and data.user_id != current_user.id and not _is_teacher_or_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seul un professeur ou un administrateur peut créer un plan pour un autre utilisateur")

    plan = Plan(user_id=target_user_id, name=data.name, description=data.description)
    db.add(plan)
    db.flush()
    for i, cid in enumerate(data.competency_ids):
        db.add(PlanCompetency(plan_id=plan.id, competency_id=cid, sort_order=i))
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/users/{user_id}/plans", response_model=list[PlanOut])
def user_plans(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if user_id != current_user.id and not _is_teacher_or_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé à un professeur ou un administrateur")
    return db.query(Plan).filter(Plan.user_id == user_id).all()


def _get_plan_or_404(db: Session, plan_id: str) -> Plan:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan introuvable")
    return plan


def _assert_can_manage_plan(current_user: User, plan: Plan):
    if plan.user_id != current_user.id and not _is_teacher_or_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce plan ne vous appartient pas")


@router.get("/plans/{plan_id}", response_model=PlanDetailOut)
def get_plan(
    plan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    plan = _get_plan_or_404(db, plan_id)
    _assert_can_manage_plan(current_user, plan)
    return _to_detail(db, plan)


@router.patch("/plans/{plan_id}", response_model=PlanOut)
def update_plan(
    plan_id: str, data: PlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    plan = _get_plan_or_404(db, plan_id)
    _assert_can_manage_plan(current_user, plan)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    plan = _get_plan_or_404(db, plan_id)
    _assert_can_manage_plan(current_user, plan)
    db.delete(plan)
    db.commit()


@router.post("/plans/{plan_id}/competencies", response_model=PlanCompetencyOut, status_code=status.HTTP_201_CREATED)
def add_plan_competency(
    plan_id: str, competency_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    plan = _get_plan_or_404(db, plan_id)
    _assert_can_manage_plan(current_user, plan)
    if db.query(PlanCompetency).filter(PlanCompetency.plan_id == plan_id, PlanCompetency.competency_id == competency_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà dans ce plan")

    competency = db.query(Competency).filter(Competency.id == competency_id).first()
    if competency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compétence introuvable")

    link = PlanCompetency(plan_id=plan_id, competency_id=competency_id, sort_order=len(plan.competencies))
    db.add(link)
    db.commit()
    db.refresh(link)

    uc = db.query(UserCompetency).filter(UserCompetency.user_id == plan.user_id, UserCompetency.competency_id == competency_id).first()
    return PlanCompetencyOut(id=link.id, competency_id=competency_id, competency_name=competency.name,
                              proficiency=uc.proficiency if uc else None, grade_rank=uc.grade_rank if uc else None)


@router.delete("/plan-competencies/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_plan_competency(
    link_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    link = db.query(PlanCompetency).filter(PlanCompetency.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lien introuvable")
    _assert_can_manage_plan(current_user, link.plan)
    db.delete(link)
    db.commit()
