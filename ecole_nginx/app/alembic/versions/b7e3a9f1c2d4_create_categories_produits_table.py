"""create_categories_produits_table

Revision ID: b7e3a9f1c2d4
Revises: a4d2f7c9e1b3
Create Date: 2026-06-27 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b7e3a9f1c2d4'
down_revision: Union[str, Sequence[str], None] = 'a4d2f7c9e1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'categories_produits',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('nom', sa.String(100), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB',
    )
    # Reprend les catégories utilisées en texte libre par le bureau
    # (add_commande(), Controllers/Main.py:5325) pour que la liste ne soit
    # pas vide au premier démarrage.
    categories_produits = sa.table(
        'categories_produits',
        sa.column('id', sa.CHAR(36)),
        sa.column('nom', sa.String(100)),
    )
    import uuid
    op.bulk_insert(categories_produits, [
        {'id': str(uuid.uuid4()), 'nom': nom}
        for nom in ['Livres', 'Tissus', 'Fournitures', 'Arriéré', 'Inscription']
    ])


def downgrade() -> None:
    op.drop_table('categories_produits')
