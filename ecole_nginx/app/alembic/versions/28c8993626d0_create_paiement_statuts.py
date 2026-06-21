"""create_paiement_statuts

Revision ID: 28c8993626d0
Revises: f2d97f76ba00
Create Date: 2026-03-05 06:44:17.122838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '28c8993626d0'
down_revision: Union[str, Sequence[str], None] = 'f2d97f76ba00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'paiement_statuts',
        sa.Column('id',               sa.CHAR(36),  nullable=False),
        sa.Column('etudiant_id',      sa.CHAR(36),  nullable=False),
        sa.Column('annee_id',         sa.CHAR(36),  nullable=False),
        sa.Column('montant_mensuel',  sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('montant_verse',    sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('date_limite',      sa.Date(),    nullable=True),
        sa.Column('mois_accessibles', sa.JSON(),    nullable=True),
        sa.Column('mois_bloques',     sa.JSON(),    nullable=True),
        sa.Column('created_at',       sa.DateTime(), nullable=True),
        sa.Column('updated_at',       sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['etudiant_id'], ['etudiants.id']),
        sa.UniqueConstraint('etudiant_id', 'annee_id', name='unique_etudiant_annee'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',  # ← même collation que etudiants
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('paiement_statuts')
    # ### end Alembic commands ###
