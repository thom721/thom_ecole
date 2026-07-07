"""add montant_du/remaining_balance/type_calcul/details_horaires to payrolls

Revision ID: 7e23faa1c08d
Revises: 9297cfbabf1b
Create Date: 2026-07-03 00:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7e23faa1c08d'
down_revision: Union[str, None] = '9297cfbabf1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payrolls', sa.Column('type_calcul', sa.String(20), nullable=False, server_default='fixe'))
    op.add_column('payrolls', sa.Column('montant_du', sa.Numeric(10, 2), nullable=True))
    op.add_column('payrolls', sa.Column('remaining_balance', sa.Numeric(10, 2), nullable=True))
    op.add_column('payrolls', sa.Column('details_horaires', sa.JSON(), nullable=True))
    op.add_column('payrolls', sa.Column('heures_pointees_ref', sa.Numeric(8, 2), nullable=True))

    # Backfill : les lignes existantes n'ont jamais eu de notion de montant
    # dû distinct du montant versé — on fige montant_du = montant, et le
    # solde restant à 0 pour les lignes déjà "Payé", au montant complet
    # sinon (comportement historique inchangé : rien n'était payé avant
    # que le statut ne bascule).
    op.execute("UPDATE payrolls SET montant_du = montant")
    op.execute("UPDATE payrolls SET remaining_balance = 0 WHERE statut = 'Payé'")
    op.execute("UPDATE payrolls SET remaining_balance = montant WHERE statut != 'Payé'")


def downgrade() -> None:
    op.drop_column('payrolls', 'heures_pointees_ref')
    op.drop_column('payrolls', 'details_horaires')
    op.drop_column('payrolls', 'remaining_balance')
    op.drop_column('payrolls', 'montant_du')
    op.drop_column('payrolls', 'type_calcul')
