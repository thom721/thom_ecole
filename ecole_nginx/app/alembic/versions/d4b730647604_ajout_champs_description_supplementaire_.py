"""ajout champs description_supplementaire et identifiant

Revision ID: d4b730647604
Revises: a6f9278535bd
Create Date: 2026-02-08 06:56:22.263027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4b730647604'
down_revision: Union[str, Sequence[str], None] = 'a6f9278535bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajout des colonnes
    op.add_column('other_transactions', sa.Column('description_supplementaire', sa.String(length=255), nullable=True))
    op.add_column('other_transactions', sa.Column('identifiant', sa.String(length=100), nullable=True))
    op.create_foreign_key(
    constraint_name=None,
    source_table='other_transactions',
    referent_table='etudiants',
    local_cols=['identifiant'],
    remote_cols=['id'],
    ondelete='SET NULL'
)

def downgrade() -> None:
    # Suppression des colonnes en cas de retour en arrière
    op.drop_column('other_transactions', 'identifiant')
    op.drop_column('other_transactions', 'description_supplementaire')

    # sa.Column('user_id', sa.String(36), sa.ForeignKey('etudiants.id', ondelete='CASCADE'), nullable=False),