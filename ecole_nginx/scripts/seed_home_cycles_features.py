"""Insère (ou met à jour) le contenu réel des sections "Nos Offres
Académiques" et "Pourquoi nous rejoindre ?" de la page d'accueil — voir
la conversation du 2026-08-30 pour les captures d'écran source (contenu
du vrai site iusth.edu.ht).

Idempotent : upsert par (page, section_key) — sans-risque à relancer.

Usage sur le serveur (pointe vers la vraie base de production, via le
conteneur Docker) :
    docker compose -f docker-compose.web.yml exec -T app python3 - < seed_home_cycles_features.py

Usage en local (pointe vers la base configurée dans ecole_nginx/.env —
DB_HOST/DB_USER/DB_PASSWORD/DB_NAME, lue par app/database.py) :
    cd ecole_nginx
    python3 scripts/seed_home_cycles_features.py
"""
import os
import sys

if os.path.isfile(__file__):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.Models.MPageSection import PageSection

CYCLES_ITEMS = [
    {
        "img": "/images/iusth-president-horat.jpg",
        "badge": "Vaste sélection de",
        "t": "Programmes diversifiés",
        "bouton": "EXPLORER",
        "lien": "/formations",
    },
    {
        "img": "/images/iusth-sciences-infirmieres.jpg",
        "badge": "",
        "t": "Faculté experte & Instructeurs de premier plan",
        "bouton": "APPRENDRE",
        "lien": "/facultes",
    },
    {
        "img": "/images/iusth-sciences-infirmieres.jpg",
        "badge": "Campus actif",
        "t": "Communauté dynamique",
        "bouton": "S'ENGAGER",
        "lien": "/a-propos",
    },
]

FEATURES_ITEMS = [
    {
        "t": "Environnement Innovant",
        "d": (
            "À l'ère de la transformation numérique et de la mondialisation, "
            "les universités jouent un rôle clé dans la formation de leaders "
            "et de penseurs innovants capables de relever les défis complexes "
            "de notre société. Pour se distinguer, IUSTH s'engage à offrir un "
            "environnement qui favorise l'innovation sous toutes ses formes, "
            "en intégrant les dernières avancées technologiques et "
            "pédagogiques."
        ),
        "lien_texte": "En savoir plus",
        "lien": "/formations",
    },
    {
        "t": "Grandir Avec Nous",
        "d": (
            "« Grandir avec nous » signifie bien plus que suivre des cours et "
            "obtenir un diplôme ; c'est un engagement à développer vos "
            "compétences, à explorer vos passions et à devenir un acteur du "
            "changement dans un monde en constante évolution."
        ),
        "lien_texte": "Nous rejoindre",
        "lien": "/admission",
    },
    {
        "t": "Culture d'Équipe Collaborative",
        "d": (
            "À IUSTH, nous croyons que la collaboration est la clé du succès "
            "dans tous les domaines académiques et professionnels. Notre "
            "culture d'équipe collaborative est conçue pour encourager le "
            "partage des idées, la diversité des perspectives et la synergie "
            "entre les membres de notre communauté."
        ),
        "lien_texte": "En savoir plus",
        "lien": "/a-propos",
    },
    {
        "t": "Impact Significatif",
        "d": (
            "À l'IUSTH, notre mission va bien au-delà de l'éducation et de la "
            "recherche. Nous sommes déterminés à avoir un impact significatif "
            "sur la société, à travers nos initiatives éducatives, nos "
            "projets de recherche et notre engagement communautaire."
        ),
        "lien_texte": "En savoir plus",
        "lien": "/a-propos",
    },
    {
        "t": "Récompenses Totales",
        "d": (
            "Nous sommes fiers de reconnaître et de célébrer les réalisations "
            "exceptionnelles de nos étudiants, enseignants, chercheurs et "
            "partenaires. Les récompenses totales que nous décernons "
            "reflètent notre engagement à encourager l'excellence académique "
            "et l'innovation."
        ),
        "lien_texte": "En savoir plus",
        "lien": "/evenements",
    },
    {
        "t": "Communauté Inclusive",
        "d": (
            "Nous organisons des événements culturels tout au long de "
            "l'année pour célébrer la diversité de notre communauté. Ces "
            "événements incluent des festivals, des conférences, des "
            "expositions et des journées thématiques qui mettent en valeur "
            "différentes cultures et traditions."
        ),
        "lien_texte": "En savoir plus",
        "lien": "/evenements",
    },
]

SECTIONS = [
    {"section_key": "cycles", "titre": "Nos Offres Académiques", "items": CYCLES_ITEMS},
    {"section_key": "features", "titre": "Pourquoi nous rejoindre ?", "items": FEATURES_ITEMS},
]


def main():
    db = SessionLocal()
    try:
        created, updated = 0, 0
        for s in SECTIONS:
            existing = (
                db.query(PageSection)
                .filter(PageSection.page == "home", PageSection.section_key == s["section_key"])
                .first()
            )
            if existing:
                existing.titre = s["titre"]
                existing.sous_titre = None
                existing.items = s["items"]
                existing.is_visible = True
                updated += 1
            else:
                db.add(PageSection(
                    page="home",
                    section_key=s["section_key"],
                    titre=s["titre"],
                    items=s["items"],
                    is_visible=True,
                ))
                created += 1
        db.commit()
        print(f"OK — {created} section(s) créée(s), {updated} mise(s) à jour.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
