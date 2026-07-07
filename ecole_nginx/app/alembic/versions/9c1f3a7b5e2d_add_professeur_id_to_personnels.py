"""add professeur_id to personnels

Revision ID: 9c1f3a7b5e2d
Revises: 800e83c5f2d9
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = '9c1f3a7b5e2d'
down_revision: Union[str, None] = '800e83c5f2d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'personnels',
        sa.Column('professeur_id', CHAR(36), sa.ForeignKey('professeurs.id'), nullable=True, unique=True),
    )


def downgrade() -> None:
    op.drop_constraint('personnels_professeur_id_foreign', 'personnels', type_='foreignkey')
    op.drop_column('personnels', 'professeur_id')
