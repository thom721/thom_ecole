"""add_evaluation_phase_to_grade_categories

Revision ID: b6d2e8f1c3a5
Revises: a3f7c1b9d4e2
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6d2e8f1c3a5'
down_revision = 'a3f7c1b9d4e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('grade_categories', sa.Column('evaluation_phase', sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column('grade_categories', 'evaluation_phase')
