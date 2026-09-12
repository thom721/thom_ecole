"""create rattrapage_sessions table

Revision ID: e7d3a9c1f6b4
Revises: a2c8f5e1d4b9
Create Date: 2026-09-10 00:00:04.000000

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7d3a9c1f6b4'
down_revision: Union[str, Sequence[str], None] = 'a2c8f5e1d4b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'rattrapage_sessions',
        sa.Column('id', sa.CHAR(36), primary_key=True, default=uuid.uuid4),
        sa.Column('etudiant_id', sa.CHAR(36), sa.ForeignKey('etudiants.id'), nullable=False),
        sa.Column('annee_academique_id', sa.CHAR(36), sa.ForeignKey('annee_academiques.id'), nullable=False),
        sa.Column('classes_id', sa.CHAR(36), sa.ForeignKey('classes.id'), nullable=False),
        sa.Column('niveau_id', sa.CHAR(36), sa.ForeignKey('niveaux.id'), nullable=False),
        sa.Column('matieres_a_repasser', sa.JSON(), nullable=False),
        sa.Column('date_limite', sa.Date(), nullable=True),
        sa.Column('notes_rattrapage', sa.JSON(), nullable=True),
        sa.Column('moyenne_recalculee', sa.Numeric(5, 2), nullable=True),
        sa.Column('statut', sa.String(20), nullable=False, server_default='en_attente'),
        sa.Column('decision_finale', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('etudiant_id', 'annee_academique_id', name='uq_rattrapage_session'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('rattrapage_sessions')
