"""Insère (ou met à jour) les 6 vraies facultés de l'IUSTH — voir
iusth/Les Facultés.docx et iusth/Programmes offerts.docx pour les sources.

Idempotent : si une faculté du même nom existe déjà, elle est mise à jour
(nb_annee/description/status) plutôt que dupliquée — sans-risque à relancer.

Usage sur le serveur (pointe vers la vraie base de production, via le
conteneur Docker) :
    docker compose -f docker-compose.web.yml exec -T app python3 - < seed_facultes_iusth.py

Usage en local (pointe vers la base configurée dans ecole_nginx/.env —
DB_HOST/DB_USER/DB_PASSWORD/DB_NAME, lue par app/database.py) :
    cd ecole_nginx
    python3 scripts/seed_facultes_iusth.py
"""
import os
import sys

# python3 scripts/seed_facultes_iusth.py place le dossier du script
# (ecole_nginx/scripts/) dans sys.path, pas ecole_nginx/ lui-même — donc
# "import app.database" échoue tel quel. On ajoute la racine du projet
# (le dossier ecole_nginx/, parent de scripts/) explicitement — seulement
# quand ce fichier tourne comme un vrai fichier (__file__ est alors un chemin
# réel). Via stdin (docker compose exec -T ... python3 - < ...), __file__
# vaut "<stdin>" (pas un chemin) : on ne touche pas à sys.path, inutile —
# le cwd est déjà /srv/ecole_nginx dans le conteneur.
if os.path.isfile(__file__):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.Models.MModels import Faculte

FACULTES = [
    {
        "nom": "Sciences Infirmières",
        "nb_annee": "4",
        "description": (
            "Faculté des Sciences de la Santé (FSSA). Créée en 2021, sa licence "
            "est délivrée par le Ministère de la Santé Publique et de la "
            "Population (MSPP). Cette formation vise à mettre sur le marché de "
            "l'emploi des professionnels capables d'analyser une situation de "
            "santé, de prendre des décisions dans les limites de leur "
            "compétence et de mener des interventions seuls ou en équipe "
            "multidisciplinaire."
        ),
    },
    {
        "nom": "Sciences Administratives",
        "nb_annee": "4",
        "description": (
            "Faculté des Sciences Économiques et Administratives (FSEA). Créée "
            "en 2021, l'une des premières facultés de l'IUSTH. Elle a formé "
            "plusieurs générations de gestionnaires, financiers et économistes "
            "pendant près d'une décennie, et prépare à plusieurs programmes de "
            "licences, diplômes et certificats professionnels."
        ),
    },
    {
        "nom": "Sciences Informatiques",
        "nb_annee": "4",
        "description": (
            "Faculté des Sciences Informatiques et de la Technologie (FSIT). Se "
            "distingue par son engagement à l'excellence académique, à la "
            "recherche de pointe et à la formation des leaders de demain dans "
            "le domaine des technologies de l'information."
        ),
    },
    {
        "nom": "Sciences Agronomiques",
        "nb_annee": "5",
        "description": (
            "Faculté des Sciences Agronomiques et de l'Environnement (FSAE). "
            "L'une des toutes premières facultés de l'IUSTH."
        ),
    },
    {
        "nom": "Génie Civil & Architecture",
        "nb_annee": "5",
        "description": (
            "Faculté des Sciences, de Génie Civil et d'Architecture (FGCA). "
            "Créée en mai 2021, elle prépare les étudiants à intervenir dans la "
            "planification, l'étude et la supervision des infrastructures de "
            "développement, en tenant compte des normes et principes "
            "fondamentaux du génie et des spécificités haïtiennes en matière "
            "de construction et d'aménagement."
        ),
    },
    {
        "nom": "Sciences Juridiques et Politiques",
        "nb_annee": "4",
        "description": (
            "Faculté des Sciences Juridiques et Politiques (FSJP), anciennement "
            "Faculté des Sciences Juridiques (FSJU) créée en 2021, renommée en "
            "2023."
        ),
    },
]


def main():
    db = SessionLocal()
    try:
        created, updated = 0, 0
        for f in FACULTES:
            existing = db.query(Faculte).filter(Faculte.nom == f["nom"]).first()
            if existing:
                existing.nb_annee = f["nb_annee"]
                existing.description = f["description"]
                existing.status = True
                updated += 1
            else:
                db.add(Faculte(
                    nom=f["nom"],
                    nb_annee=f["nb_annee"],
                    description=f["description"],
                    status=True,
                ))
                created += 1
        db.commit()
        print(f"OK — {created} faculté(s) créée(s), {updated} mise(s) à jour.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
