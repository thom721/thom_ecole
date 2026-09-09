"""live_session_notification_kind

Revision ID: 3acd35aad748
Revises: 3f7a4d7aaa12
Create Date: 2026-09-08 04:36:49.337578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3acd35aad748'
down_revision = '3f7a4d7aaa12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('notifications', 'kind',
        existing_type=sa.Enum('new_grade', 'new_forum_post', 'new_message', name='notificationkind'),
        type_=sa.Enum('new_grade', 'new_forum_post', 'new_message', 'new_live_session', name='notificationkind'),
        existing_nullable=False)


def downgrade() -> None:
    op.alter_column('notifications', 'kind',
        existing_type=sa.Enum('new_grade', 'new_forum_post', 'new_message', 'new_live_session', name='notificationkind'),
        type_=sa.Enum('new_grade', 'new_forum_post', 'new_message', name='notificationkind'),
        existing_nullable=False)
