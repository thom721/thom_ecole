"""add_photo_fields_to_etudiants

Revision ID: 861e3478f0cb
Revises: dc9c98be1a37
Create Date: 2026-01-30 06:50:03.966962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '861e3478f0cb'
down_revision: Union[str, Sequence[str], None] = 'dc9c98be1a37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

 

def upgrade() -> None:
    #  pass
    # Ajout des deux colonnes
    op.add_column('etudiants', sa.Column('photo_base64', mysql.LONGTEXT, nullable=True))
    op.add_column('etudiants', sa.Column('photo_path', sa.String(length=255), nullable=True))

def downgrade() -> None:
    #  pass
    # Suppression des colonnes en cas de retour en arrière
    op.drop_column('etudiants', 'photo_path')
    op.drop_column('etudiants', 'photo_base64')
