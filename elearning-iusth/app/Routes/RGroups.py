from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MGroup import Group, GroupMember, Grouping, GroupingGroup
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SGroup import (
    GroupCreate, GroupUpdate, GroupOut, GroupDetailOut, GroupMemberOut,
    GroupingCreate, GroupingUpdate, GroupingOut, GroupingDetailOut,
    AddMemberIn, AddGroupToGroupingIn,
)
from app.dependencies.auth import get_current_active_user, assert_course_role, get_enrollment_or_none

router = APIRouter(tags=["groups"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_group_or_404(db: Session, group_id: str) -> Group:
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable")
    return group


def _get_grouping_or_404(db: Session, grouping_id: str) -> Grouping:
    grouping = db.query(Grouping).filter(Grouping.id == grouping_id).first()
    if grouping is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupement introuvable")
    return grouping


def _group_detail(db: Session, group: Group) -> GroupDetailOut:
    members = []
    for m in group.members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            members.append(GroupMemberOut(user_id=user.id, name=f"{user.first_name} {user.last_name}", email=user.email))
    return GroupDetailOut(id=group.id, course_id=group.course_id, name=group.name, description=group.description, members=members)


@router.get("/courses/{course_id}/groups", response_model=list[GroupDetailOut])
def list_groups(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    groups = db.query(Group).filter(Group.course_id == course_id).all()
    return [_group_detail(db, g) for g in groups]


@router.post("/courses/{course_id}/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
    course_id: str, data: GroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    group = Group(course_id=course_id, **data.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.patch("/groups/{group_id}", response_model=GroupOut)
def update_group(
    group_id: str, data: GroupUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    group = _get_group_or_404(db, group_id)
    assert_course_role(db, current_user, group.course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    group = _get_group_or_404(db, group_id)
    assert_course_role(db, current_user, group.course_id, _TEACHING_ROLES)
    db.delete(group)
    db.commit()


@router.post("/groups/{group_id}/members", response_model=GroupDetailOut, status_code=status.HTTP_201_CREATED)
def add_member(
    group_id: str, data: AddMemberIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    group = _get_group_or_404(db, group_id)
    assert_course_role(db, current_user, group.course_id, _TEACHING_ROLES)

    if get_enrollment_or_none(db, group.course_id, data.user_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet utilisateur n'est pas inscrit à ce cours")
    if db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == data.user_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà membre de ce groupe")

    db.add(GroupMember(group_id=group_id, user_id=data.user_id))
    db.commit()
    db.refresh(group)
    return _group_detail(db, group)


@router.delete("/groups/{group_id}/members/{user_id}", response_model=GroupDetailOut)
def remove_member(
    group_id: str, user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    group = _get_group_or_404(db, group_id)
    assert_course_role(db, current_user, group.course_id, _TEACHING_ROLES)

    member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).first()
    if member:
        db.delete(member)
        db.commit()
    db.refresh(group)
    return _group_detail(db, group)


def _grouping_detail(db: Session, grouping: Grouping) -> GroupingDetailOut:
    groups = [db.query(Group).filter(Group.id == link.group_id).first() for link in grouping.group_links]
    return GroupingDetailOut(
        id=grouping.id, course_id=grouping.course_id, name=grouping.name, description=grouping.description,
        groups=[GroupOut.model_validate(g) for g in groups if g],
    )


@router.get("/courses/{course_id}/groupings", response_model=list[GroupingDetailOut])
def list_groupings(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    groupings = db.query(Grouping).filter(Grouping.course_id == course_id).all()
    return [_grouping_detail(db, g) for g in groupings]


@router.post("/courses/{course_id}/groupings", response_model=GroupingOut, status_code=status.HTTP_201_CREATED)
def create_grouping(
    course_id: str, data: GroupingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    grouping = Grouping(course_id=course_id, **data.model_dump())
    db.add(grouping)
    db.commit()
    db.refresh(grouping)
    return grouping


@router.patch("/groupings/{grouping_id}", response_model=GroupingOut)
def update_grouping(
    grouping_id: str, data: GroupingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    grouping = _get_grouping_or_404(db, grouping_id)
    assert_course_role(db, current_user, grouping.course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(grouping, field, value)
    db.commit()
    db.refresh(grouping)
    return grouping


@router.delete("/groupings/{grouping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grouping(
    grouping_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    grouping = _get_grouping_or_404(db, grouping_id)
    assert_course_role(db, current_user, grouping.course_id, _TEACHING_ROLES)
    db.delete(grouping)
    db.commit()


@router.post("/groupings/{grouping_id}/groups", response_model=GroupingDetailOut, status_code=status.HTTP_201_CREATED)
def add_group_to_grouping(
    grouping_id: str, data: AddGroupToGroupingIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    grouping = _get_grouping_or_404(db, grouping_id)
    assert_course_role(db, current_user, grouping.course_id, _TEACHING_ROLES)

    group = _get_group_or_404(db, data.group_id)
    if group.course_id != grouping.course_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce groupe n'appartient pas au même cours")
    if db.query(GroupingGroup).filter(GroupingGroup.grouping_id == grouping_id, GroupingGroup.group_id == data.group_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce groupe fait déjà partie de ce groupement")

    db.add(GroupingGroup(grouping_id=grouping_id, group_id=data.group_id))
    db.commit()
    db.refresh(grouping)
    return _grouping_detail(db, grouping)


@router.delete("/groupings/{grouping_id}/groups/{group_id}", response_model=GroupingDetailOut)
def remove_group_from_grouping(
    grouping_id: str, group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    grouping = _get_grouping_or_404(db, grouping_id)
    assert_course_role(db, current_user, grouping.course_id, _TEACHING_ROLES)

    link = db.query(GroupingGroup).filter(GroupingGroup.grouping_id == grouping_id, GroupingGroup.group_id == group_id).first()
    if link:
        db.delete(link)
        db.commit()
    db.refresh(grouping)
    return _grouping_detail(db, grouping)
