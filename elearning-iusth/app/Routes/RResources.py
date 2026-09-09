from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MResource import Resource, ResourceFile, ResourceType
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SResource import ResourceUpdate, ResourceOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Models.MUser import SystemRole
from app.Models.MAccessLog import AccessItemType
from app.Helper.files import save_upload, resolve_download
from app.Helper.access_log import log_access
from app.Helper.access_conditions import is_item_accessible
from app.Helper.completion_config import get_completion_mode
from app.Helper.completion import mark_complete_if_absent
from app.Models.MCompletion import CompletionItemType, CompletionMode

router = APIRouter(tags=["resources"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.post("/sections/{section_id}/resources", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
async def create_resource(
    section_id: str,
    resource_type: ResourceType = Form(...),
    title: str = Form(...),
    description: str | None = Form(None),
    external_url: str | None = Form(None),
    page_content: str | None = Form(None),
    sort_order: int = Form(0),
    files: list[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    resource = Resource(
        section_id=section_id, resource_type=resource_type, title=title,
        description=description, external_url=external_url, page_content=page_content,
        sort_order=sort_order,
    )
    db.add(resource)
    db.flush()  # obtenir resource.id avant de créer les ResourceFile enfants

    for upload in files:
        stored_path, size = save_upload(upload, subdir=f"resources/{resource.id}")
        db.add(ResourceFile(
            resource_id=resource.id, original_filename=upload.filename or "fichier",
            stored_path=stored_path, mime_type=upload.content_type, size_bytes=size,
        ))

    db.commit()
    db.refresh(resource)
    return resource


@router.get("/resource-files/{file_id}/download")
def download_resource_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Corrige un gap réel (voir plan Épic 18) : aucun fichier de
    ressource n'était servable avant cet epic, seulement affiché en texte
    brut côté frontend."""
    resource_file = db.query(ResourceFile).filter(ResourceFile.id == file_id).first()
    if resource_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable")
    resource = db.query(Resource).filter(Resource.id == resource_file.resource_id).first()
    section = db.query(Section).filter(Section.id == resource.section_id).first()
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, section.course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return resolve_download(resource_file.stored_path, resource_file.original_filename, resource_file.mime_type)


def _get_resource_or_404(db: Session, resource_id: str) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ressource introuvable")
    return resource


@router.get("/resources/{resource_id}", response_model=ResourceOut)
def get_resource(
    resource_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    resource = _get_resource_or_404(db, resource_id)
    section = db.query(Section).filter(Section.id == resource.section_id).first()
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, section.course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    accessible, reasons = is_item_accessible(db, current_user, section.course_id, CompletionItemType.resource, resource_id)
    resource.access_restricted = not accessible
    resource.access_reasons = reasons
    if not accessible:
        resource.page_content = None
        resource.external_url = None
        resource.files = []
        return resource

    log_access(db, current_user, section.course_id, AccessItemType.resource, resource_id)
    if get_completion_mode(db, CompletionItemType.resource, resource_id) == CompletionMode.automatic:
        mark_complete_if_absent(db, current_user.id, CompletionItemType.resource, resource_id)
    return resource


@router.patch("/resources/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: str, data: ResourceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    resource = _get_resource_or_404(db, resource_id)
    section = db.query(Section).filter(Section.id == resource.section_id).first()
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    resource = _get_resource_or_404(db, resource_id)
    section = db.query(Section).filter(Section.id == resource.section_id).first()
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)
    db.delete(resource)
    db.commit()
