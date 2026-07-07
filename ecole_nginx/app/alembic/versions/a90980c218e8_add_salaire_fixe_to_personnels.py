"""add salaire_fixe to personnels

Revision ID: a90980c218e8
Revises: 6af9d208f564
Create Date: 2026-07-05 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a90980c218e8'
down_revision: Union[str, None] = '6af9d208f564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'personnels',
        sa.Column('salaire_fixe', sa.Numeric(10, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('personnels', 'salaire_fixe')
