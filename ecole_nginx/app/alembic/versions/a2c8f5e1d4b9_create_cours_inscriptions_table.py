"""create cours_inscriptions table

Revision ID: a2c8f5e1d4b9
Revises: f4e9b6d2a8c3
Create Date: 2026-09-10 00:00:03.000000

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2c8f5e1d4b9'
down_revision: Union[str, Sequence[str], None] = 'f4e9b6d2a8c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'cours_inscriptions',
        sa.Column('id', sa.CHAR(36), primary_key=True, default=uuid.uuid4),
        sa.Column('etudiant_id', sa.CHAR(36), sa.ForeignKey('etudiants.id'), nullable=False),
        sa.Column('cours_id', sa.CHAR(36), sa.ForeignKey('cours.id'), nullable=False),
        sa.Column('programme_id', sa.CHAR(36), sa.ForeignKey('programmes.id'), nullable=True),
        sa.Column('annee_academique_id', sa.CHAR(36), sa.ForeignKey('annee_academiques.id'), nullable=False),
        sa.Column('niveau_id', sa.CHAR(36), sa.ForeignKey('niveaux.id'), nullable=False),
        sa.Column('credits', sa.Numeric(4, 1), nullable=False),
        sa.Column('note_finale', sa.Numeric(5, 2), nullable=True),
        sa.Column('credits_obtenus', sa.Numeric(4, 1), nullable=True),
        sa.Column('statut', sa.String(20), nullable=False, server_default='en_cours'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('etudiant_id', 'cours_id', 'annee_academique_id', name='uq_cours_inscription'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('cours_inscriptions')
