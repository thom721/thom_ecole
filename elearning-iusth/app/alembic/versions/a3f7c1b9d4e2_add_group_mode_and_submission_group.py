"""add_group_mode_and_submission_group

Revision ID: a3f7c1b9d4e2
Revises: fe9259fd440a
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f7c1b9d4e2'
down_revision = 'fe9259fd440a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('assignments', sa.Column('group_mode', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('submissions', sa.Column('group_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(
        'fk_submissions_group_id_groups', 'submissions', 'groups', ['group_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_submissions_group_id_groups', 'submissions', type_='foreignkey')
    op.drop_column('submissions', 'group_id')
    op.drop_column('assignments', 'group_mode')
