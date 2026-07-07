"""add personnel_id to professeurs

Revision ID: 800e83c5f2d9
Revises: bd9b7a813621
Create Date: 2026-07-07 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = '800e83c5f2d9'
down_revision: Union[str, None] = 'bd9b7a813621'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'professeurs',
        sa.Column('personnel_id', CHAR(36), sa.ForeignKey('personnels.id'), nullable=True, unique=True),
    )


def downgrade() -> None:
    op.drop_constraint('professeurs_personnel_id_foreign', 'professeurs', type_='foreignkey')
    op.drop_column('professeurs', 'personnel_id')
