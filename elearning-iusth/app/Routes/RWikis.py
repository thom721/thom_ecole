import difflib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MWiki import Wiki, Subwiki, WikiPage, WikiVersion, WikiMode
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SWiki import (
    WikiCreate, WikiUpdate, WikiOut, SubwikiOut, WikiPageSummaryOut,
    WikiPageCreate, WikiPageOut, WikiVersionCreate, WikiVersionSummaryOut, WikiDiffOut,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role

router = APIRouter(tags=["wikis"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_wiki_and_course(db: Session, wiki_id: str) -> tuple[Wiki, str]:
    wiki = db.query(Wiki).filter(Wiki.id == wiki_id).first()
    if wiki is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wiki introuvable")
    section = db.query(Section).filter(Section.id == wiki.section_id).first()
    return wiki, section.course_id


def _get_subwiki_and_course(db: Session, subwiki_id: str) -> tuple[Subwiki, str]:
    subwiki = db.query(Subwiki).filter(Subwiki.id == subwiki_id).first()
    if subwiki is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sous-wiki introuvable")
    _wiki, course_id = _get_wiki_and_course(db, subwiki.wiki_id)
    return subwiki, course_id


def _get_page_and_course(db: Session, page_id: str) -> tuple[WikiPage, str]:
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")
    _subwiki, course_id = _get_subwiki_and_course(db, page.subwiki_id)
    return page, course_id


def _is_teaching(db: Session, current_user: User, course_id: str) -> bool:
    if current_user.system_role == SystemRole.admin:
        return True
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    return enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES


def _create_root_page(db: Session, subwiki: Subwiki, wiki: Wiki, user_id: str | None) -> WikiPage:
    page = WikiPage(subwiki_id=subwiki.id, title=wiki.first_page_title, cached_content="", created_by=user_id)
    db.add(page)
    db.flush()
    db.add(WikiVersion(page_id=page.id, content="", version=1, created_by=user_id))
    return page


def _get_or_create_subwiki(db: Session, wiki: Wiki, current_user: User) -> Subwiki:
    owner_id = None if wiki.mode == WikiMode.collaborative else current_user.id
    subwiki = db.query(Subwiki).filter(Subwiki.wiki_id == wiki.id, Subwiki.owner_id == owner_id).first()
    if subwiki is None:
        subwiki = Subwiki(wiki_id=wiki.id, owner_id=owner_id)
        db.add(subwiki)
        db.flush()
        _create_root_page(db, subwiki, wiki, current_user.id)
        db.commit()
        db.refresh(subwiki)
    return subwiki


def _can_edit(db: Session, current_user: User, wiki: Wiki, subwiki: Subwiki, course_id: str) -> bool:
    if _is_teaching(db, current_user, course_id):
        return True
    if wiki.mode == WikiMode.collaborative:
        return get_enrollment_or_none(db, course_id, current_user.id) is not None
    return subwiki.owner_id == current_user.id


def _subwiki_out(db: Session, subwiki: Subwiki) -> SubwikiOut:
    owner_name = None
    if subwiki.owner_id:
        owner = db.query(User).filter(User.id == subwiki.owner_id).first()
        if owner:
            owner_name = f"{owner.first_name} {owner.last_name}"
    root_page = next((p for p in subwiki.pages if p.title == subwiki.wiki.first_page_title), None)
    return SubwikiOut(
        id=subwiki.id, wiki_id=subwiki.wiki_id, owner_id=subwiki.owner_id, owner_name=owner_name,
        root_page_id=root_page.id if root_page else None,
        pages=[WikiPageSummaryOut(id=p.id, title=p.title) for p in subwiki.pages],
    )


@router.post("/sections/{section_id}/wikis", response_model=WikiOut, status_code=status.HTTP_201_CREATED)
def create_wiki(
    section_id: str, data: WikiCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    wiki = Wiki(section_id=section_id, **data.model_dump())
    db.add(wiki)
    db.flush()

    if wiki.mode == WikiMode.collaborative:
        subwiki = Subwiki(wiki_id=wiki.id, owner_id=None)
        db.add(subwiki)
        db.flush()
        _create_root_page(db, subwiki, wiki, current_user.id)

    db.commit()
    db.refresh(wiki)
    return wiki


@router.get("/wikis/{wiki_id}", response_model=SubwikiOut)
def get_wiki(
    wiki_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Résout la sous-wiki DE L'UTILISATEUR COURANT (partagée en mode
    collaboratif, la sienne en mode individuel — créée à la volée au
    premier accès)."""
    wiki, course_id = _get_wiki_and_course(db, wiki_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    subwiki = _get_or_create_subwiki(db, wiki, current_user)
    return _subwiki_out(db, subwiki)


@router.get("/wikis/{wiki_id}/subwikis", response_model=list[SubwikiOut])
def list_subwikis(
    wiki_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Enseignant uniquement — liste les sous-wikis individuelles de tous
    les étudiants (capacité réelle Moodle : consulter/éditer le wiki de
    n'importe quel étudiant)."""
    wiki, course_id = _get_wiki_and_course(db, wiki_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if wiki.mode != WikiMode.individual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce wiki n'est pas en mode individuel")

    subwikis = db.query(Subwiki).filter(Subwiki.wiki_id == wiki_id).all()
    return [_subwiki_out(db, s) for s in subwikis]


@router.get("/subwikis/{subwiki_id}", response_model=SubwikiOut)
def get_subwiki(
    subwiki_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    subwiki, course_id = _get_subwiki_and_course(db, subwiki_id)
    is_teaching = _is_teaching(db, current_user, course_id)
    if not is_teaching and subwiki.owner_id is not None and subwiki.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas accès à cette sous-wiki")
    if not is_teaching and get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return _subwiki_out(db, subwiki)


@router.post("/subwikis/{subwiki_id}/pages", response_model=WikiPageOut, status_code=status.HTTP_201_CREATED)
def create_page(
    subwiki_id: str, data: WikiPageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    subwiki, course_id = _get_subwiki_and_course(db, subwiki_id)
    wiki = db.query(Wiki).filter(Wiki.id == subwiki.wiki_id).first()
    if not _can_edit(db, current_user, wiki, subwiki, course_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez pas modifier cette sous-wiki")

    if db.query(WikiPage).filter(WikiPage.subwiki_id == subwiki_id, WikiPage.title == data.title).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Une page avec ce titre existe déjà")

    page = WikiPage(subwiki_id=subwiki_id, title=data.title, cached_content=data.content, created_by=current_user.id)
    db.add(page)
    db.flush()
    db.add(WikiVersion(page_id=page.id, content=data.content, version=1, created_by=current_user.id))
    db.commit()
    db.refresh(page)
    return WikiPageOut(
        id=page.id, subwiki_id=page.subwiki_id, title=page.title, cached_content=page.cached_content,
        is_readonly=page.is_readonly, created_by=page.created_by, updated_at=page.updated_at, current_version=1,
    )


def _page_out(db: Session, page: WikiPage) -> WikiPageOut:
    current_version = db.query(WikiVersion).filter(WikiVersion.page_id == page.id).count()
    return WikiPageOut(
        id=page.id, subwiki_id=page.subwiki_id, title=page.title, cached_content=page.cached_content,
        is_readonly=page.is_readonly, created_by=page.created_by, updated_at=page.updated_at,
        current_version=current_version,
    )


def _get_page_detail(page_id: str, current_user: User, db: Session) -> WikiPageOut:
    page, course_id = _get_page_and_course(db, page_id)
    subwiki = db.query(Subwiki).filter(Subwiki.id == page.subwiki_id).first()
    is_teaching = _is_teaching(db, current_user, course_id)
    if not is_teaching and subwiki.owner_id is not None and subwiki.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas accès à cette page")
    return _page_out(db, page)


# IMPORTANT : ce chemin statique DOIT être déclaré avant "/wiki-pages/{page_id}"
# ci-dessous — sinon Starlette fait matcher {page_id}="by-title" en premier
# (ordre de déclaration = ordre de priorité de résolution des routes) et ce
# endpoint ne serait jamais atteint (bug réel rencontré et corrigé ici).
@router.get("/wiki-pages/by-title", response_model=WikiPageOut)
def get_page_by_title(
    subwiki_id: str = Query(...), title: str = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    page = db.query(WikiPage).filter(WikiPage.subwiki_id == subwiki_id, WikiPage.title == title).first()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")
    return _get_page_detail(page.id, current_user, db)


@router.get("/wiki-pages/{page_id}", response_model=WikiPageOut)
def get_page(
    page_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return _get_page_detail(page_id, current_user, db)


@router.post("/wiki-pages/{page_id}/versions", response_model=WikiPageOut)
def create_version(
    page_id: str, data: WikiVersionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    page, course_id = _get_page_and_course(db, page_id)
    subwiki = db.query(Subwiki).filter(Subwiki.id == page.subwiki_id).first()
    wiki = db.query(Wiki).filter(Wiki.id == subwiki.wiki_id).first()
    is_teaching = _is_teaching(db, current_user, course_id)

    if page.is_readonly and not is_teaching:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette page est en lecture seule")
    if not _can_edit(db, current_user, wiki, subwiki, course_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez pas modifier cette sous-wiki")

    last_version = db.query(WikiVersion).filter(WikiVersion.page_id == page_id).count()
    db.add(WikiVersion(page_id=page_id, content=data.content, version=last_version + 1, created_by=current_user.id))
    page.cached_content = data.content
    db.commit()
    db.refresh(page)
    return _page_out(db, page)


@router.get("/wiki-pages/{page_id}/versions", response_model=list[WikiVersionSummaryOut])
def list_versions(
    page_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _page, _course_id = _get_page_and_course(db, page_id)
    versions = db.query(WikiVersion).filter(WikiVersion.page_id == page_id).order_by(WikiVersion.version.desc()).all()
    return [WikiVersionSummaryOut(version=v.version, created_by=v.created_by, created_at=v.created_at) for v in versions]


@router.get("/wiki-pages/{page_id}/diff", response_model=WikiDiffOut)
def diff_versions(
    page_id: str, from_: int = Query(..., alias="from"), to: int = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _page, _course_id = _get_page_and_course(db, page_id)
    v_from = db.query(WikiVersion).filter(WikiVersion.page_id == page_id, WikiVersion.version == from_).first()
    v_to = db.query(WikiVersion).filter(WikiVersion.page_id == page_id, WikiVersion.version == to).first()
    if v_from is None or v_to is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version introuvable")

    lines = list(difflib.unified_diff(
        v_from.content.splitlines(), v_to.content.splitlines(),
        fromfile=f"v{from_}", tofile=f"v{to}", lineterm="",
    ))
    return WikiDiffOut(from_version=from_, to_version=to, lines=lines)
