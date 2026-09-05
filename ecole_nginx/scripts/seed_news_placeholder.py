"""Ajoute 5 actualités génériques de type "brouillon" dans la table `news`,
à la demande explicite de l'utilisateur ("ajouter des articles à votre
choix") — voir la conversation du 2026-08-30. Contenu volontairement
générique (annonces institutionnelles standard, aucune date/chiffre/nom de
partenaire inventé) : à remplacer par le vrai contenu de presse via
Admin > Communauté > Actualités dès qu'il est disponible.

Idempotent : upsert par titre — sans-risque à relancer.

Usage sur le serveur :
    docker compose -f docker-compose.web.yml exec -T app python3 - < seed_news_placeholder.py

Usage en local :
    cd ecole_nginx
    python3 scripts/seed_news_placeholder.py
"""
import os
import sys
from datetime import datetime, timedelta

if os.path.isfile(__file__):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.Models.MRelations import News, AudienceType

NOW = datetime.utcnow()

ARTICLES = [
    {
        "title": "Ouverture de la période d'inscription",
        "content": (
            "L'Institut Universitaire des Sciences et des Technologies d'Haïti (IUSTH) "
            "annonce l'ouverture de la période d'inscription pour ses différentes "
            "facultés. Les candidats intéressés sont invités à se rendre au secrétariat "
            "de la Direction des affaires académiques ou à consulter le volet Admission "
            "du site pour connaître la démarche et les pièces à fournir."
        ),
        "published_at": NOW - timedelta(days=2),
    },
    {
        "title": "Cérémonie de remise de diplômes",
        "content": (
            "L'IUSTH a organisé une cérémonie de remise de diplômes en l'honneur des "
            "étudiants ayant complété avec succès leur cursus. L'institution félicite "
            "l'ensemble des lauréats et leur souhaite plein succès dans la suite de "
            "leur carrière professionnelle au service du développement d'Haïti."
        ),
        "published_at": NOW - timedelta(days=9),
    },
    {
        "title": "Renforcement des partenariats académiques",
        "content": (
            "Dans le cadre de sa mission de coopération universitaire, l'IUSTH "
            "poursuit le développement de partenariats avec des institutions "
            "universitaires et non universitaires d'Amérique et des Caraïbes, en vue "
            "d'enrichir l'offre académique et les opportunités de recherche offertes à "
            "ses étudiants."
        ),
        "published_at": NOW - timedelta(days=16),
    },
    {
        "title": "Journée portes ouvertes à l'IUSTH",
        "content": (
            "L'IUSTH invite les futurs candidats et leurs familles à une journée "
            "portes ouvertes pour découvrir ses facultés, ses programmes et son campus. "
            "Une occasion d'échanger directement avec le corps professoral et "
            "l'administration sur les modalités d'admission et de financement des "
            "études."
        ),
        "published_at": NOW - timedelta(days=23),
    },
    {
        "title": "Investissement dans les équipements pédagogiques",
        "content": (
            "L'IUSTH poursuit ses efforts d'investissement dans les équipements et "
            "ressources pédagogiques mis à la disposition des étudiants, dans le but "
            "d'offrir une formation pratique alignée sur les exigences du monde "
            "professionnel et du développement durable d'Haïti."
        ),
        "published_at": NOW - timedelta(days=30),
    },
]


def main():
    db = SessionLocal()
    try:
        created, updated = 0, 0
        for a in ARTICLES:
            existing = db.query(News).filter(News.title == a["title"]).first()
            if existing:
                existing.content = a["content"]
                existing.published_at = a["published_at"]
                existing.is_published = True
                existing.audience = AudienceType.public
                updated += 1
            else:
                db.add(News(
                    title=a["title"],
                    content=a["content"],
                    published_at=a["published_at"],
                    audience=AudienceType.public,
                    is_published=True,
                ))
                created += 1
        db.commit()
        print(f"OK — {created} article(s) créé(s), {updated} mis à jour.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
