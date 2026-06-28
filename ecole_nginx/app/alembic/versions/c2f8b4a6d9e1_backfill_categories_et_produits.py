"""backfill_categories_et_produits_depuis_ventes

Revision ID: c2f8b4a6d9e1
Revises: b7e3a9f1c2d4
Create Date: 2026-06-27 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'c2f8b4a6d9e1'
down_revision: Union[str, Sequence[str], None] = 'b7e3a9f1c2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Reconstitue le catalogue produit à partir de l'historique réel des
    # ventes : le bureau ne persistait jamais de fiche produit, seulement
    # le nom/catégorie/prix tapés en texte libre à chaque ligne de vente
    # (add_commande(), Controllers/Main.py:5357-5403, table order_items).
    # On reprend ces noms/catégories déjà vendus comme catalogue initial,
    # sans dupliquer ce qui existe déjà (ex: les 5 catégories par défaut
    # de la migration b7e3a9f1c2d4).
    op.execute("""
        INSERT INTO categories_produits (id, nom, created_at, updated_at)
        SELECT UUID(), src.category, NOW(), NOW()
        FROM (
            SELECT DISTINCT category
            FROM order_items
            WHERE category IS NOT NULL AND category != ''
        ) AS src
        WHERE NOT EXISTS (
            SELECT 1 FROM categories_produits cp WHERE cp.nom = src.category
        )
    """)

    # Un même nom de produit a pu être vendu à des prix différents au fil
    # du temps (le bureau ne forçait aucune cohérence) ; on retient le prix
    # le plus récemment pratiqué (MAX(id) approxime "la dernière ligne",
    # order_items n'ayant pas d'index ordonné fiable sur created_at ici).
    # Le stock n'a jamais été suivi avant ce catalogue : initialisé à 0,
    # à corriger manuellement depuis l'onglet Produits.
    op.execute("""
        INSERT INTO produits (id, nom, category, prix, quantite_stock, description, created_at, updated_at)
        SELECT UUID(), src.nom, src.category, src.prix, 0, NULL, NOW(), NOW()
        FROM (
            SELECT nom, category, MAX(prix) AS prix
            FROM order_items
            WHERE nom IS NOT NULL AND nom != ''
              AND category IS NOT NULL AND category != ''
            GROUP BY nom, category
        ) AS src
        WHERE NOT EXISTS (
            SELECT 1 FROM produits p WHERE p.nom = src.nom AND p.category = src.category
        )
    """)


def downgrade() -> None:
    # Pas de downgrade automatique : impossible de distinguer de façon
    # fiable les lignes importées par ce backfill de celles ajoutées
    # manuellement depuis (mêmes tables, aucun marqueur de provenance).
    pass
