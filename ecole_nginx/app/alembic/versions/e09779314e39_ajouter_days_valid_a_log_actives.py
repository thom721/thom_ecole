"""ajouter_days_valid_a_log_actives

Revision ID: e09779314e39
Revises: e2a4c7f19b3d
Create Date: 2026-07-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e09779314e39'
down_revision: Union[str, Sequence[str], None] = 'e2a4c7f19b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Nullable : les lignes déjà existantes n'ont aucun moyen fiable de
    # retrouver rétroactivement le days_valid utilisé à l'époque — elles
    # restent NULL, et le code qui les relit (vérification HMAC au
    # démarrage de l'API) saute simplement cette revérification pour elles,
    # exactement comme is_license_valid() le fait déjà côté registre
    # Windows pour les clés appliquées avant l'ajout de ce même champ.
    op.add_column('log_actives', sa.Column('days_valid', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('log_actives', 'days_valid')
