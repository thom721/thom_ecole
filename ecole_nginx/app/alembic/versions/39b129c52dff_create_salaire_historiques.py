"""create salaire_historiques

Revision ID: 39b129c52dff
Revises: a90980c218e8
Create Date: 2026-07-06 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = '39b129c52dff'
down_revision: Union[str, None] = 'a90980c218e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'salaire_historiques',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('employe_type', sa.String(20), nullable=False),
        sa.Column('employe_id', CHAR(36), nullable=False),
        sa.Column('ancien_montant', sa.Numeric(10, 2), nullable=True),
        sa.Column('nouveau_montant', sa.Numeric(10, 2), nullable=False),
        sa.Column('modifie_par', CHAR(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('salaire_historiques')
