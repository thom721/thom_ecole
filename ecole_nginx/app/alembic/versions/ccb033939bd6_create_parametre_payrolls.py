"""create parametre_payrolls

Revision ID: ccb033939bd6
Revises: cf6332f37959
Create Date: 2026-07-03 00:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = 'ccb033939bd6'
down_revision: Union[str, None] = 'cf6332f37959'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'parametre_payrolls',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('cours_id', CHAR(36), sa.ForeignKey('cours.id'), nullable=False),
        sa.Column('taux_horaire', sa.Numeric(10, 2), nullable=False),
        sa.Column('annee_academique', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('cours_id', 'annee_academique', name='uq_parametre_payroll_cours_annee'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('parametre_payrolls')
