from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.Models.MCourse import Course, Section, CourseFormat
from app.Models.MForum import Forum
from app.Models.MEnrollment import Enrollment, CourseRole
from app.Models.MUser import User, SystemRole
from app.Models.MAccessLog import AccessItemType
from app.Models.MCompletion import CompletionItemType
from app.Schemas.SCourse import CourseCreate, CourseUpdate, CourseOut, CourseDetailOut, CoursePageOut
from app.dependencies.auth import get_current_active_user, require_role, require_course_role, get_enrollment_or_none
from app.Helper.access_log import log_access
from app.Helper.access_conditions import is_item_accessible
from app.Helper.course_format import section_week_dates

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=CoursePageOut, dependencies=[Depends(require_role([SystemRole.admin]))])
def list_courses(
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Course)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Course.full_name.like(like), Course.short_name.like(like)))

    total = query.count()
    items = (
        query.order_by(Course.full_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return CoursePageOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/mine", response_model=list[CourseOut])
def list_my_courses(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return (
        db.query(Course)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .filter(Enrollment.user_id == current_user.id)
        .order_by(Course.full_name)
        .all()
    )


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    data: CourseCreate,
    current_user: User = Depends(require_role([SystemRole.teacher, SystemRole.admin])),
    db: Session = Depends(get_db),
):
    if db.query(Course).filter(Course.short_name == data.short_name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce code de cours est déjà utilisé")

    course = Course(**data.model_dump(), created_by=current_user.id)
    db.add(course)
    db.commit()
    db.refresh(course)

    # Le créateur devient automatiquement "teacher" sur son propre cours,
    # sinon il ne pourrait plus rien y modifier ensuite (sauf s'il est admin).
    if current_user.system_role != SystemRole.admin:
        db.add(Enrollment(course_id=course.id, user_id=current_user.id,
                           role_in_course=CourseRole.teacher, enrolled_by=current_user.id))
        db.commit()

    return course


@router.get("/{course_id}", response_model=CourseDetailOut)
def get_course(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .options(
            # `selectinload`, pas `joinedload` : 9 collections sœurs sous la
            # même Section jointes simultanément produiraient le produit
            # cartésien complet (SQLAlchemy émet un seul SELECT à N JOIN),
            # pas une union — un cours réel avec suffisamment d'activités
            # variées fait exploser le nombre de lignes intermédiaires
            # (confirmé : >150s sur un cours de test chargé, voir plan
            # Épic 14). `selectinload` fait une requête séparée par
            # collection à la place, en O(N) requêtes plutôt qu'un JOIN
            # géant en O(produit).
            selectinload(Course.sections).selectinload(Section.resources),
            selectinload(Course.sections).selectinload(Section.assignments),
            selectinload(Course.sections).selectinload(Section.quizzes),
            selectinload(Course.sections).selectinload(Section.forums),
            selectinload(Course.sections).selectinload(Section.choices),
            selectinload(Course.sections).selectinload(Section.glossaries),
            selectinload(Course.sections).selectinload(Section.wikis),
            selectinload(Course.sections).selectinload(Section.lessons),
            selectinload(Course.sections).selectinload(Section.workshops),
            selectinload(Course.sections).selectinload(Section.live_sessions),
            selectinload(Course.sections).selectinload(Section.interactive_videos),
        )
        .filter(Course.id == course_id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")

    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    # Redaction en mémoire seulement (jamais commitée dans cette requête en
    # lecture seule) des ressources restreintes par condition d'accès —
    # nécessaire car leur contenu est affiché en ligne dans cette même
    # réponse, pas via un aller-retour séparé (voir plan Épic 7).
    for section in course.sections:
        for resource in section.resources:
            accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.resource, resource.id)
            resource.access_restricted = not accessible
            resource.access_reasons = reasons
            if not accessible:
                resource.page_content = None
                resource.external_url = None
                resource.files = []
        # Dates de semaine calculées en direct, jamais stockées (voir plan
        # Épic 14) — attributs posés en mémoire, jamais commités.
        week_dates = section_week_dates(course, section)
        section.week_start = week_dates[0] if week_dates else None
        section.week_end = week_dates[1] if week_dates else None

    social_forum = None
    if course.format == CourseFormat.social and course.social_forum_id:
        social_forum = db.query(Forum).filter(Forum.id == course.social_forum_id).first()
    course.social_forum = social_forum

    log_access(db, current_user, course_id, AccessItemType.course)
    return course


@router.patch("/{course_id}", response_model=CourseOut,
              dependencies=[Depends(require_course_role([CourseRole.teacher, CourseRole.manager]))])
def update_course(course_id: str, data: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")

    if data.social_forum_id:
        forum = (
            db.query(Forum)
            .join(Section, Section.id == Forum.section_id)
            .filter(Forum.id == data.social_forum_id, Section.course_id == course_id)
            .first()
        )
        if forum is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce forum n'appartient pas à ce cours")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_course_role([CourseRole.manager]))])
def delete_course(course_id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")
    db.delete(course)
    db.commit()
