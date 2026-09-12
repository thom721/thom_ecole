"""add_intra_final_credits

Revision ID: e8c4f2a9b1d6
Revises: d5b8e2f4a7c1
Create Date: 2026-09-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8c4f2a9b1d6'
down_revision = 'd5b8e2f4a7c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cours', sa.Column('poids_intra_percent', sa.Numeric(5, 2), nullable=False, server_default='50'))
    op.add_column('cours_inscriptions', sa.Column('note_intra', sa.Numeric(5, 2), nullable=True))
    op.add_column('cours_inscriptions', sa.Column('note_globale', sa.Numeric(5, 2), nullable=True))

    # Backfill : préserve le statut déjà décidé des inscriptions saisies
    # avant cette fonctionnalité (traitées comme si note_finale était déjà
    # la note globale, cohérent avec le comportement affiché jusqu'ici).
    op.execute(
        "UPDATE cours_inscriptions SET note_globale = note_finale "
        "WHERE note_globale IS NULL AND note_finale IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column('cours_inscriptions', 'note_globale')
    op.drop_column('cours_inscriptions', 'note_intra')
    op.drop_column('cours', 'poids_intra_percent')
