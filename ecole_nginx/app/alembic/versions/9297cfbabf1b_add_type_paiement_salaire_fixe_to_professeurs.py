"""add type_paiement and salaire_fixe to professeurs

Revision ID: 9297cfbabf1b
Revises: ccb033939bd6
Create Date: 2026-07-03 00:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9297cfbabf1b'
down_revision: Union[str, None] = 'ccb033939bd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'professeurs',
        sa.Column('type_paiement', sa.String(20), nullable=False, server_default='fixe'),
    )
    op.add_column(
        'professeurs',
        sa.Column('salaire_fixe', sa.Numeric(10, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('professeurs', 'salaire_fixe')
    op.drop_column('professeurs', 'type_paiement')
