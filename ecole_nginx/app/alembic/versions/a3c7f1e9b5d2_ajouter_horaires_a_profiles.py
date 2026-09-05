"""ajouter_horaires_a_profiles

Revision ID: a3c7f1e9b5d2
Revises: f9c3b6a1d8e4
Create Date: 2026-08-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c7f1e9b5d2'
down_revision: Union[str, Sequence[str], None] = 'f9c3b6a1d8e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('horaires', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'horaires')
