"""ajouter_champs_a_log_actives

Revision ID: a6f9278535bd
Revises: 861e3478f0cb
Create Date: 2026-02-03 09:32:15.227708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6f9278535bd'
down_revision: Union[str, Sequence[str], None] = '861e3478f0cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
     # pass
    # Ajout des deux colonnes à la table log_actives
    op.add_column('log_actives', sa.Column('f_key', sa.String(length=255), nullable=True))
    op.add_column('log_actives', sa.Column('f_day', sa.Integer(), nullable=True))

def downgrade():
     # pass
    # Suppression des colonnes en cas de retour en arrière
    op.drop_column('log_actives', 'f_key')
    op.drop_column('log_actives', 'f_day')
