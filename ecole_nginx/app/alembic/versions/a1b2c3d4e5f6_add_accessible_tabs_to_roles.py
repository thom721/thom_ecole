"""add accessible_tabs to roles

Revision ID: a1b2c3d4e5f6
Revises: f4b6c1e8a3d2
Create Date: 2026-06-29 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f4b6c1e8a3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Nullable : null = accès à tous les onglets (comportement admin).
    # Quand renseigné : liste JSON des IDs d'onglet autorisés pour ce rôle,
    # e.g. ["home","paiement","vente","profile"].
    op.add_column('roles', sa.Column('accessible_tabs', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('roles', 'accessible_tabs')
