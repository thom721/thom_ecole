"""create annulations_arriere

Revision ID: e2a4c7f19b3d
Revises: 9c1f3a7b5e2d
Create Date: 2026-07-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR

revision: str = 'e2a4c7f19b3d'
down_revision: Union[str, None] = '9c1f3a7b5e2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'annulations_arriere',
        sa.Column('id', CHAR(36), primary_key=True),
        sa.Column('etudiant_id', CHAR(36), sa.ForeignKey('etudiants.id'), nullable=False),
        sa.Column('annee_academique_id', CHAR(36), sa.ForeignKey('annee_academiques.id'), nullable=False),
        sa.Column('annee_academique', sa.String(255), nullable=False),
        sa.Column('type_annulation', sa.String(20), nullable=False),
        sa.Column('montant_annule', sa.Numeric(10, 2), nullable=False),
        sa.Column('ordonne_par', sa.String(255), nullable=False),
        sa.Column('ordonne_par_fonction', sa.String(255), nullable=False),
        sa.Column('executant_user_id', CHAR(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('executant_nom', sa.String(255), nullable=False),
        sa.Column('executant_role', sa.String(255), nullable=True),
        sa.Column('raison', sa.String(255), nullable=False),
        sa.Column('contrat_accepte', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('statut', sa.String(20), nullable=False, server_default='actif'),
        sa.Column('annule_le', sa.DateTime(), nullable=True),
        sa.Column('annule_par_user_id', CHAR(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('annule_raison', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    op.drop_table('annulations_arriere')
