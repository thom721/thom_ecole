"""ajouter_description_a_facultes

Revision ID: c4d9e2f6a8b1
Revises: b8e2f4a6c1d3
Create Date: 2026-08-29 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d9e2f6a8b1'
down_revision: Union[str, Sequence[str], None] = 'b8e2f4a6c1d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('facultes', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('facultes', 'description')
