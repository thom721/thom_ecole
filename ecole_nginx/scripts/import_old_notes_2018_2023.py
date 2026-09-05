"""Reproduit en Python la logique de notes_old/old_eleves_notes_export.php
(script Laravel, jamais réexécuté avec succès depuis la migration vers
FastAPI — voir la discussion qui a mené à ce script) pour importer les
notes 2018/2019 -> 2023/2024 dans CoursEtudiant.data_etudiant.

Logique reproduite à l'identique depuis le fichier PHP source :
  - Source : le tableau $notes de notes_old/old_eleves_notes_export.php,
    lignes [id, code, note_sept..note_juin (10 mois), matiere,
    annee_academique, classe, coefficient, type_matiere].
  - Résout CoursEtudiant par la clé composite (code, annee_academique) —
    NE CRÉE JAMAIS de ligne manquante, ignore et compte seulement (comme
    l'original : "SI L'ÉTUDIANT N'EXISTE PAS, ON IGNORE").
  - Fusionne dans data_etudiant[identifiant][base|orale][matiere], sans
    écraser les mois déjà présents pour une autre matière/année.
  - Une valeur de note égale à '', None ou '0' n'est jamais écrite (comme
    l'original : ces zéros représentent "pas de note", pas une vraie note
    de 0).

data_etudiant est un Column(JSON, ...) SQLAlchemy sur une colonne MySQL
LONGTEXT (voir app/Models/MRelations.py) : SQLAlchemy fait UN SEUL niveau
d'encodage JSON automatique. Les données réelles en base sont donc
doublement encodées (json.dumps appliqué une fois par l'app, puis une
seconde fois par SQLAlchemy à l'écriture) — confirmé empiriquement sur une
ligne 2024/2025 réelle. On écrit donc `row.data_etudiant = json.dumps(dict)`
(une chaîne), jamais le dict directement, pour rester cohérent avec ce que
lit déjà le reste de l'app (BulletinPrint.py fait lui-même un second
json.loads() sur cette chaîne).

Usage (dry-run par défaut — n'écrit rien) :
    cd ecole_nginx
    python3 scripts/import_old_notes_2018_2023.py

Pour appliquer réellement les changements :
    python3 scripts/import_old_notes_2018_2023.py --commit
"""
import ast
import json
import os
import re
import sys

if os.path.isfile(__file__):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.Models.MModels import AnneeAcademique
from app.Models.MRelations import CoursEtudiant

PHP_SOURCE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "notes_old", "old_eleves_notes_export.php",
)

MOIS = ['Septembre', 'Octobre', 'Novembre', 'Décembre', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin']


def _join_wrapped_strings(block: str) -> str:
    """Certaines entrées du fichier PHP source sont enroulées sur 2 lignes
    en plein milieu d'une chaîne (retour à la ligne "physique" du fichier,
    pas un \\n voulu dans le texte — ex: 'Matiere de\\nbase'). Un retour à
    la ligne brut à l'intérieur d'une chaîne entre guillemets simples n'est
    valide ni en PHP ni en syntaxe littérale Python : on le remplace par un
    espace, seulement quand on est bien À L'INTÉRIEUR d'une chaîne (en
    suivant l'échappement \\' comme le ferait un vrai tokenizer)."""
    out = []
    in_string = False
    escaped = False
    for ch in block:
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == "'":
                in_string = False
            elif ch == '\n':
                out.append(' ')
                continue
        else:
            if ch == "'":
                in_string = True
        out.append(ch)
    return ''.join(out)


def load_notes(path: str) -> list[list[str]]:
    """Extrait le tableau $notes = [ ... ]; du fichier PHP source.
    Le contenu (que des chaînes/entre guillemets simples et des crochets)
    est une syntaxe de liste Python valide une fois les retours à la ligne
    internes aux chaînes recollés — ast.literal_eval le parse ensuite tel
    quel, sans autre transformation."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"\$notes\s*=\s*(\[.*?\n\]);", content, re.DOTALL)
    if not match:
        raise RuntimeError(f"Bloc \"$notes = [...]\" introuvable dans {path}")

    return ast.literal_eval(_join_wrapped_strings(match.group(1)))


def main(commit: bool) -> None:
    notes = load_notes(PHP_SOURCE)
    print(f"Lignes de notes chargées depuis le PHP : {len(notes)}")

    db = SessionLocal()
    try:
        annees_presentes = {row[13] for row in notes}
        annees_valides = {
            a for (a,) in db.query(AnneeAcademique.annee_academique)
                            .filter(AnneeAcademique.annee_academique.in_(annees_presentes))
                            .all()
        }
        annees_manquantes = annees_presentes - annees_valides
        if annees_manquantes:
            print(f"⚠️  Années absentes de annee_academiques (lignes ignorées) : {sorted(annees_manquantes)}")

        codes = {row[1] for row in notes if row[1]}
        existants = (
            db.query(CoursEtudiant)
              .filter(CoursEtudiant.code.in_(codes))
              .all()
        )
        cours_par_cle = {(c.code, c.annee_academique): c for c in existants}
        print(f"CoursEtudiant existants chargés pour ces codes : {len(existants)}")

        # dict Python en mémoire (pas encore json.dumps) pour accumuler les
        # modifications par ligne CoursEtudiant avant la sauvegarde finale.
        merges: dict[str, dict] = {}   # cours_etudiant.id -> dict data_etudiant en cours de fusion
        touched_rows: dict[str, CoursEtudiant] = {}

        total = len(notes)
        ignores_code_vide = 0
        ignores_annee = 0
        ignores_non_trouve = 0
        lignes_appliquees = 0
        notes_ecrites = 0
        exemples_ignores = []

        for item in notes:
            code = item[1]
            annee = item[13]
            matiere = item[12]
            type_matiere_raw = item[16] if len(item) > 16 else ''
            coef = item[15] if len(item) > 15 else None
            classe = item[14] if len(item) > 14 else None

            if not code:
                ignores_code_vide += 1
                continue

            if annee not in annees_valides:
                ignores_annee += 1
                continue

            cours = cours_par_cle.get((code, annee))
            if not cours:
                ignores_non_trouve += 1
                if len(exemples_ignores) < 10:
                    exemples_ignores.append(f"{code} / {annee}")
                continue

            identifiant = cours.identifiant or 'notes'

            if cours.id not in merges:
                raw = cours.data_etudiant
                try:
                    decoded = json.loads(raw) if raw else {}
                except (TypeError, ValueError):
                    decoded = {}
                if not isinstance(decoded, dict):
                    decoded = {}
                merges[cours.id] = decoded
                touched_rows[cours.id] = cours

            data = merges[cours.id]
            if identifiant not in data or not isinstance(data.get(identifiant), dict):
                data[identifiant] = {}

            type_matiere = 'orale' if type_matiere_raw == 'Matiere orale' else 'base'
            if type_matiere not in data[identifiant]:
                data[identifiant][type_matiere] = {}
            if matiere not in data[identifiant][type_matiere]:
                data[identifiant][type_matiere][matiere] = {
                    'type_matiere': type_matiere,
                    'professeur_id': None,
                    'coefficients': coef,
                    'note_de_passage': None,
                    'classe': classe,
                    'notes': {},
                }

            notes_dict = data[identifiant][type_matiere][matiere]['notes']
            for i, mois in enumerate(MOIS):
                valeur = item[2 + i] if len(item) > 2 + i else None
                if valeur not in ('', None, '0'):
                    notes_dict[mois] = valeur
                    notes_ecrites += 1

            lignes_appliquees += 1

        print(f"\n=== RÉSUMÉ (dry-run={'non' if commit else 'oui'}) ===")
        print(f"Total lignes sources        : {total}")
        print(f"Lignes appliquées           : {lignes_appliquees}")
        print(f"Valeurs de notes écrites    : {notes_ecrites}")
        print(f"Ignorées (code vide)        : {ignores_code_vide}")
        print(f"Ignorées (année inconnue)   : {ignores_annee}")
        print(f"Ignorées (CoursEtudiant introuvable) : {ignores_non_trouve}")
        if exemples_ignores:
            print(f"  Exemples (code/année) non trouvés : {exemples_ignores}")
        print(f"Lignes CoursEtudiant qui seraient mises à jour : {len(touched_rows)}")

        if commit:
            for cid, cours in touched_rows.items():
                cours.data_etudiant = json.dumps(merges[cid], ensure_ascii=False)
            db.commit()
            print(f"\n✅ Commit effectué : {len(touched_rows)} lignes CoursEtudiant mises à jour.")
        else:
            print("\n(dry-run : aucune écriture en base — relancer avec --commit pour appliquer)")
            # Aperçu des identifiants qui seraient modifiés, groupés par année,
            # pour vérification manuelle avant le vrai commit.
            par_annee: dict[str, list[str]] = {}
            for cours in touched_rows.values():
                par_annee.setdefault(cours.annee_academique, []).append(cours.identifiant or cours.code)
            for annee in sorted(par_annee):
                idents = par_annee[annee]
                print(f"  {annee} : {len(idents)} élève(s) — ex: {idents[:5]}")
    finally:
        db.close()


if __name__ == "__main__":
    main(commit="--commit" in sys.argv)
