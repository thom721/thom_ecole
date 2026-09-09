from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCompetency import (
    CompetencyFramework, Competency, CourseCompetency, ModuleCompetency,
    UserCompetency, UserCompetencyCourse, CompetencyEvidence, PlanCompetency, EvidenceAction,
)
from app.Models.MCompletion import CompletionItemType
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SCompetency import (
    CompetencyFrameworkCreate, CompetencyFrameworkUpdate, CompetencyFrameworkOut,
    CompetencyCreate, CompetencyUpdate, CompetencyOut,
    CourseCompetencyCreate, CourseCompetencyOut, ModuleCompetencyCreate, ModuleCompetencyOut,
    GradeCompetencyIn, StudentCompetencyStatusOut, MyCompetencyOut, EvidenceOut,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role, require_role
from app.Helper.competencies import set_grade

router = APIRouter(tags=["competencies"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_framework_or_404(db: Session, framework_id: str) -> CompetencyFramework:
    framework = db.query(CompetencyFramework).filter(CompetencyFramework.id == framework_id).first()
    if framework is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Référentiel introuvable")
    return framework


def _get_competency_or_404(db: Session, competency_id: str) -> Competency:
    competency = db.query(Competency).filter(Competency.id == competency_id).first()
    if competency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compétence introuvable")
    return competency


# --- Référentiels (admin) ---

@router.get("/competency-frameworks", response_model=list[CompetencyFrameworkOut])
def list_frameworks(db: Session = Depends(get_db)):
    return db.query(CompetencyFramework).all()


@router.post("/competency-frameworks", response_model=CompetencyFrameworkOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role([SystemRole.admin]))])
def create_framework(
    data: CompetencyFrameworkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if db.query(CompetencyFramework).filter(CompetencyFramework.idnumber == data.idnumber).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce numéro d'identification est déjà utilisé")
    framework = CompetencyFramework(created_by=current_user.id, **data.model_dump())
    db.add(framework)
    db.commit()
    db.refresh(framework)
    return framework


@router.get("/competency-frameworks/{framework_id}", response_model=CompetencyFrameworkOut)
def get_framework(framework_id: str, db: Session = Depends(get_db)):
    return _get_framework_or_404(db, framework_id)


@router.patch("/competency-frameworks/{framework_id}", response_model=CompetencyFrameworkOut,
              dependencies=[Depends(require_role([SystemRole.admin]))])
def update_framework(framework_id: str, data: CompetencyFrameworkUpdate, db: Session = Depends(get_db)):
    framework = _get_framework_or_404(db, framework_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(framework, field, value)
    db.commit()
    db.refresh(framework)
    return framework


@router.delete("/competency-frameworks/{framework_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(require_role([SystemRole.admin]))])
def delete_framework(framework_id: str, db: Session = Depends(get_db)):
    framework = _get_framework_or_404(db, framework_id)
    if framework.competencies:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce référentiel contient des compétences — suppression bloquée")
    db.delete(framework)
    db.commit()


@router.get("/competency-frameworks/{framework_id}/competencies", response_model=list[CompetencyOut])
def list_competencies(framework_id: str, db: Session = Depends(get_db)):
    return db.query(Competency).filter(Competency.framework_id == framework_id).order_by(Competency.sort_order).all()


@router.post("/competency-frameworks/{framework_id}/competencies", response_model=CompetencyOut,
              status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([SystemRole.admin]))])
def create_competency(framework_id: str, data: CompetencyCreate, db: Session = Depends(get_db)):
    _get_framework_or_404(db, framework_id)
    competency = Competency(framework_id=framework_id, **data.model_dump())
    db.add(competency)
    db.commit()
    db.refresh(competency)
    return competency


# --- Compétences ---

@router.get("/competencies/mine", response_model=list[MyCompetencyOut])
def my_competencies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Déclarée AVANT /competencies/{competency_id} — une route statique
    après une route dynamique de même profondeur serait masquée par elle
    (même bug déjà rencontré et corrigé aux Épics 4/12)."""
    rows = db.query(UserCompetency).filter(UserCompetency.user_id == current_user.id).all()
    out = []
    for r in rows:
        evidence = db.query(CompetencyEvidence).filter(
            CompetencyEvidence.user_competency_id == r.id,
        ).order_by(CompetencyEvidence.created_at.desc()).all()
        out.append(MyCompetencyOut(
            competency_id=r.competency_id, competency_name=_competency_name(db, r.competency_id),
            status=r.status, proficiency=r.proficiency, grade_rank=r.grade_rank,
            evidence=[EvidenceOut.model_validate(e) for e in evidence],
        ))
    return out


def _competency_name(db: Session, competency_id: str) -> str:
    c = db.query(Competency).filter(Competency.id == competency_id).first()
    return c.name if c else "?"


@router.get("/competencies/{competency_id}", response_model=CompetencyOut)
def get_competency(competency_id: str, db: Session = Depends(get_db)):
    return _get_competency_or_404(db, competency_id)


@router.patch("/competencies/{competency_id}", response_model=CompetencyOut,
              dependencies=[Depends(require_role([SystemRole.admin]))])
def update_competency(competency_id: str, data: CompetencyUpdate, db: Session = Depends(get_db)):
    competency = _get_competency_or_404(db, competency_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(competency, field, value)
    db.commit()
    db.refresh(competency)
    return competency


@router.delete("/competencies/{competency_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(require_role([SystemRole.admin]))])
def delete_competency(competency_id: str, db: Session = Depends(get_db)):
    competency = _get_competency_or_404(db, competency_id)
    linked_course = db.query(CourseCompetency).filter(CourseCompetency.competency_id == competency_id).first()
    linked_module = db.query(ModuleCompetency).filter(ModuleCompetency.competency_id == competency_id).first()
    linked_plan = db.query(PlanCompetency).filter(PlanCompetency.competency_id == competency_id).first()
    if linked_course or linked_module or linked_plan or competency.children:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cette compétence est utilisée (cours, activité, plan ou sous-compétence) — suppression bloquée")
    db.delete(competency)
    db.commit()


# --- Liaison à un cours / une activité ---

@router.get("/courses/{course_id}/competencies", response_model=list[CourseCompetencyOut])
def list_course_competencies(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if get_enrollment_or_none(db, course_id, current_user.id) is None and current_user.system_role != SystemRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return db.query(CourseCompetency).filter(CourseCompetency.course_id == course_id).order_by(CourseCompetency.sort_order).all()


@router.post("/courses/{course_id}/competencies", response_model=CourseCompetencyOut, status_code=status.HTTP_201_CREATED)
def link_course_competency(
    course_id: str, data: CourseCompetencyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if db.query(CourseCompetency).filter(CourseCompetency.course_id == course_id, CourseCompetency.competency_id == data.competency_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà liée à ce cours")
    link = CourseCompetency(course_id=course_id, competency_id=data.competency_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/course-competencies/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_course_competency(
    link_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    link = db.query(CourseCompetency).filter(CourseCompetency.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lien introuvable")
    assert_course_role(db, current_user, link.course_id, _TEACHING_ROLES)
    db.delete(link)
    db.commit()


@router.post("/activities/{item_type}/{item_id}/competencies", response_model=ModuleCompetencyOut, status_code=status.HTTP_201_CREATED)
def link_module_competency(
    item_type: CompletionItemType, item_id: str, data: ModuleCompetencyCreate,
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if db.query(ModuleCompetency).filter(
        ModuleCompetency.item_type == item_type, ModuleCompetency.item_id == item_id,
        ModuleCompetency.competency_id == data.competency_id,
    ).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà liée à cette activité")
    link = ModuleCompetency(course_id=course_id, item_type=item_type, item_id=item_id, competency_id=data.competency_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/module-competencies/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_module_competency(
    link_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    link = db.query(ModuleCompetency).filter(ModuleCompetency.id == link_id).first()
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lien introuvable")
    assert_course_role(db, current_user, link.course_id, _TEACHING_ROLES)
    db.delete(link)
    db.commit()


# --- Notation ---

@router.patch("/courses/{course_id}/competencies/{competency_id}/students/{student_id}", response_model=StudentCompetencyStatusOut)
def grade_student_competency(
    course_id: str, competency_id: str, student_id: str, data: GradeCompetencyIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    competency = _get_competency_or_404(db, competency_id)

    set_grade(db, student_id, competency, course_id, data.grade_rank, actor_id=current_user.id,
              action=EvidenceAction.override, note=data.note)

    ucc = db.query(UserCompetencyCourse).filter(
        UserCompetencyCourse.user_id == student_id, UserCompetencyCourse.course_id == course_id,
        UserCompetencyCourse.competency_id == competency_id,
    ).first()
    uc = db.query(UserCompetency).filter(UserCompetency.user_id == student_id, UserCompetency.competency_id == competency_id).first()
    return StudentCompetencyStatusOut(
        competency_id=competency_id, competency_name=competency.name,
        course_proficiency=ucc.proficiency if ucc else None, course_grade_rank=ucc.grade_rank if ucc else None,
        global_proficiency=uc.proficiency if uc else None, global_grade_rank=uc.grade_rank if uc else None,
    )


@router.get("/courses/{course_id}/competencies/mine", response_model=list[StudentCompetencyStatusOut])
def my_course_competencies(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    links = db.query(CourseCompetency).filter(CourseCompetency.course_id == course_id).all()
    out = []
    for link in links:
        competency = link.competency
        ucc = db.query(UserCompetencyCourse).filter(
            UserCompetencyCourse.user_id == current_user.id, UserCompetencyCourse.course_id == course_id,
            UserCompetencyCourse.competency_id == competency.id,
        ).first()
        uc = db.query(UserCompetency).filter(
            UserCompetency.user_id == current_user.id, UserCompetency.competency_id == competency.id,
        ).first()
        out.append(StudentCompetencyStatusOut(
            competency_id=competency.id, competency_name=competency.name,
            course_proficiency=ucc.proficiency if ucc else None, course_grade_rank=ucc.grade_rank if ucc else None,
            global_proficiency=uc.proficiency if uc else None, global_grade_rank=uc.grade_rank if uc else None,
        ))
    return out
