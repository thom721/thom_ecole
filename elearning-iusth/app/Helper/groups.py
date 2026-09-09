from sqlalchemy.orm import Session

from app.Models.MGroup import Group, GroupMember, GroupingGroup


def get_user_group_ids(db: Session, course_id: str, user_id: str, grouping_id: str | None = None) -> set[str]:
    """Groupes du cours auxquels appartient user_id — restreint aux
    groupes du groupement `grouping_id` si fourni (null = tous les
    groupes du cours, voir plan Épic 5)."""
    query = (
        db.query(Group.id)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(Group.course_id == course_id, GroupMember.user_id == user_id)
    )
    if grouping_id:
        query = query.join(GroupingGroup, GroupingGroup.group_id == Group.id).filter(
            GroupingGroup.grouping_id == grouping_id
        )
    return {row[0] for row in query.all()}


def users_share_a_group(db: Session, user_a_id: str, user_b_id: str, course_id: str, grouping_id: str | None = None) -> bool:
    if user_a_id == user_b_id:
        return True
    groups_a = get_user_group_ids(db, course_id, user_a_id, grouping_id)
    if not groups_a:
        return False
    groups_b = get_user_group_ids(db, course_id, user_b_id, grouping_id)
    return not groups_a.isdisjoint(groups_b)
