#!/usr/bin/env python3
"""
Script d'anonymisation : remplace les noms/prénoms réels par des noms latins
dans les tables `etudiants` et `paiements` (champ JSON details_etudiant).

Usage:
    python anonymize_names.py input.sql > output.sql
    # ou directement sur MySQL:
    python anonymize_names.py --mysql --host localhost --user root --password secret --db ma_base
"""

import re
import json
import sys
import random


NOMS_LATINS = [
    # Gentes romaines classiques
    "Aelius", "Aemilius", "Afranius", "Albinus", "Alfenus", "Annius",
    "Antonius", "Appuleius", "Aquillius", "Arrius", "Asinius", "Atilius",
    "Atius", "Aufidius", "Aurelius", "Avilius", "Baebius", "Brutus",
    "Caecilius", "Caelius", "Caesius", "Calpurnius", "Calvisius", "Cassius",
    "Ceionius", "Cicero", "Claudius", "Clodius", "Cluentius", "Cocceius",
    "Cominius", "Considius", "Cornelius", "Cosconius", "Crassus", "Curtius",
    "Decidius", "Decius", "Didius", "Domitius", "Drusus", "Durmius",
    "Egnatius", "Emilius", "Erucius", "Fabius", "Fabricius", "Fadius",
    "Favonius", "Figulus", "Flaccus", "Flavius", "Fonteius", "Fulvius",
    "Fundanius", "Furius", "Gabinius", "Gaius", "Galba", "Gallus",
    "Gellius", "Gracchus", "Grattius", "Hadrianus", "Herennius", "Hirtius",
    "Horatius", "Hortensius", "Hostilius", "Iberius", "Iulius", "Iunius",
    "Iulianus", "Junianus", "Juventius", "Labienus", "Laelius", "Lentulus",
    "Lepidus", "Licinius", "Livius", "Lucanus", "Lucilius", "Lucius",
    "Lucretius", "Lutatius", "Macrinus", "Maecius", "Manilius", "Manlius",
    "Marcius", "Marius", "Memmius", "Messius", "Metellus", "Minucius",
    "Mucius", "Munatius", "Naevius", "Numerius", "Octavius", "Ovidius",
    "Pacuvius", "Papius", "Paulus", "Piso", "Plancius", "Plautius",
    "Pleminius", "Plinius", "Plotius", "Pompeius", "Pomponius", "Pontius",
    "Popillius", "Porcinus", "Porcius", "Postumius", "Publicius", "Quinctius",
    "Quintus", "Rabirius", "Regulus", "Roscius", "Rutilius", "Sallustius",
    "Salpius", "Salvius", "Scribonius", "Sempronius", "Seneca", "Servilius",
    "Servius", "Sextius", "Sicinius", "Statilius", "Suellius", "Sulpicius",
    "Tacitus", "Terentius", "Titinius", "Titus", "Trebatius", "Trebellius",
    "Tullius", "Ulpius", "Ursinius", "Valerius", "Varius", "Vergilius",
    "Verres", "Vibius", "Vinicius", "Volumnius", "Volusius", "Vopiscus",
]

PRENOMS_LATINS = [
    # Prénoms féminins latins
    "Aelia", "Aemilia", "Agrippa", "Alba", "Albina", "Alfia",
    "Antonia", "Appuleia", "Aquillia", "Arria", "Asinia", "Atilia",
    "Aurelia", "Avilia", "Baebia", "Caecilia", "Caelia", "Calpurnia",
    "Claudia", "Clodia", "Cornelia", "Domitia", "Drusilla", "Egnatia",
    "Emilia", "Fabia", "Fabricia", "Fannia", "Flavia", "Fulvia",
    "Gaia", "Galeria", "Gracia", "Helpis", "Hortenia", "Hostilia",
    "Iulia", "Iunia", "Laelia", "Lentula", "Licinia", "Livia",
    "Lucretia", "Lutia", "Maecia", "Manlia", "Marcia", "Minucia",
    "Mucia", "Nonia", "Octavia", "Paulla", "Petronia", "Plautia",
    "Pompeia", "Pomponia", "Porcia", "Postumia", "Publicia", "Quinta",
    "Rufina", "Rutilia", "Sabina", "Salvia", "Sempronia", "Servilia",
    "Sextia", "Sicinia", "Sulpicia", "Terentia", "Titinia", "Titia",
    "Tullia", "Urbana", "Valeria", "Varia", "Vergilia", "Vibiana",
    "Vinicia", "Volumnia", "Zona",
    # Prénoms masculins latins
    "Albinus", "Appius", "Aulus", "Caius", "Calvus", "Decimus",
    "Ennius", "Festus", "Glaucus", "Gnaeus", "Hermes", "Iovinus",
    "Kalvus", "Lucius", "Marcus", "Manius", "Nestor", "Numerius",
    "Orbus", "Postumus", "Publius", "Quartus", "Quintus", "Sextus",
    "Servius", "Spurius", "Titus", "Tiberius", "Urbanus", "Verus",
    "Xenon", "Zosimus",
]

random.seed(42)  # reproductible

# Mapping cohérent : même vrai nom → même nom latin
_nom_map = {}
_prenom_map = {}

def get_nom_latin(nom_reel: str) -> str:
    nom_reel = nom_reel.strip()
    if nom_reel not in _nom_map:
        _nom_map[nom_reel] = random.choice(NOMS_LATINS) + str(len(_nom_map) + 1)
    return _nom_map[nom_reel]

def get_prenom_latin(prenom_reel: str) -> str:
    prenom_reel = prenom_reel.strip()
    if prenom_reel not in _prenom_map:
        _prenom_map[prenom_reel] = random.choice(PRENOMS_LATINS) + str(len(_prenom_map) + 1)
    return _prenom_map[prenom_reel]


def process_sql_file(content: str) -> str:
    content = process_etudiants(content)
    content = process_paiements(content)
    return content


def process_etudiants(content: str) -> str:
    """
    Dans INSERT INTO `etudiants` VALUES (...)
    La structure des colonnes d'après le dump :
    col 1  : uuid
    col 2  : identifiant  (ex: '1-01798')
    col 3  : nom          ← à anonymiser
    col 4  : prenom       ← à anonymiser
    col 5  : sexe
    ...
    """
    # On traite ligne par ligne les tuples de valeurs
    def replace_tuple(m):
        raw = m.group(0)
        # Extraire les valeurs de ce tuple
        # On cherche col3 (nom) et col4 (prenom) = 3e et 4e champ SQL
        parts = split_sql_values(raw)
        if len(parts) >= 4:
            parts[2] = "'" + get_nom_latin(unquote(parts[2])) + "'"
            parts[3] = "'" + get_prenom_latin(unquote(parts[3])) + "'"
        return '(' + ','.join(parts) + ')'

    # Repère chaque tuple VALUES dans INSERT INTO `etudiants`
    in_etudiants = False
    lines = []
    for line in content.split('\n'):
        if 'INSERT INTO `etudiants`' in line or "INSERT INTO 'etudiants'" in line:
            in_etudiants = True
        if in_etudiants:
            line = re.sub(r'\(([^()]*)\)', replace_tuple, line)
            if line.rstrip().endswith(';'):
                in_etudiants = False
        lines.append(line)
    return '\n'.join(lines)


def process_paiements(content: str) -> str:
    """
    Dans la table paiements, le JSON dans la dernière colonne contient :
    "details_etudiant": {"nom": "...", "prenom": "...", ...}
    On remplace ces valeurs par les mêmes noms latins (cohérence avec etudiants).
    """
    def replace_json_field(m):
        raw_json_str = m.group(1)
        # Decode l'escape SQL (les \" internes)
        try:
            # Le JSON est entouré de quotes SQL, on le parse
            data = json.loads(raw_json_str)
        except Exception:
            return m.group(0)

        def fix_details(obj):
            if isinstance(obj, dict):
                if 'details_etudiant' in obj:
                    d = obj['details_etudiant']
                    if 'nom' in d:
                        d['nom'] = get_nom_latin(d['nom'])
                    if 'prenom' in d:
                        d['prenom'] = get_prenom_latin(d['prenom'])
                for v in obj.values():
                    fix_details(v)
            elif isinstance(obj, list):
                for item in obj:
                    fix_details(item)

        fix_details(data)
        new_json = json.dumps(data, ensure_ascii=False)
        return "'" + new_json.replace("'", "\\'") + "'"

    # Remplace les gros JSON dans les lignes INSERT INTO `paiements`
    in_paiements = False
    result_lines = []
    for line in content.split('\n'):
        if 'INSERT INTO `paiements`' in line or "INSERT INTO 'paiements'" in line:
            in_paiements = True
        if in_paiements:
            # Les JSON sont encadrés par '{' et '}' dans des strings SQL
            # On cible le champ paiement_details JSON (colonne avec details_etudiant)
            line = re.sub(
                r"'(\{.*?\"details_etudiant\".*?\})'",
                replace_json_field,
                line,
                flags=re.DOTALL
            )
            if line.rstrip().endswith(';'):
                in_paiements = False
        result_lines.append(line)
    return '\n'.join(result_lines)


def split_sql_values(tuple_str: str):
    """Sépare les valeurs d'un tuple SQL ex: ('a','b','c',NULL,...)"""
    # Enlève les parenthèses extérieures
    inner = tuple_str.strip()
    if inner.startswith('('):
        inner = inner[1:]
    if inner.endswith(')'):
        inner = inner[:-1]

    parts = []
    current = ''
    in_string = False
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == "'" and not in_string:
            in_string = True
            current += c
        elif c == "'" and in_string:
            # check escaped quote
            if i + 1 < len(inner) and inner[i+1] == "'":
                current += "''"
                i += 2
                continue
            in_string = False
            current += c
        elif c == ',' and not in_string:
            parts.append(current.strip())
            current = ''
        else:
            current += c
        i += 1
    if current.strip():
        parts.append(current.strip())
    return parts


def unquote(val: str) -> str:
    val = val.strip()
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1].replace("''", "'")
    return val


# ─── Mode MySQL direct ──────────────────────────────────────────────────────

def run_mysql_mode(host, user, password, db, port=3306):
    try:
        import mysql.connector
    except ImportError:
        print("Installez mysql-connector-python : pip install mysql-connector-python")
        sys.exit(1)

    conn = mysql.connector.connect(
        host=host, user=user, password=password, database=db, port=port
    )
    cur = conn.cursor()

    # 1. Charger tous les étudiants
    cur.execute("SELECT id, nom, prenom FROM etudiants")
    rows = cur.fetchall()

    updates_etudiant = []
    for (eid, nom, prenom) in rows:
        new_nom = get_nom_latin(nom or '')
        new_prenom = get_prenom_latin(prenom or '')
        updates_etudiant.append((new_nom, new_prenom, eid))

    print(f"  → {len(updates_etudiant)} étudiants à mettre à jour...")
    cur.executemany(
        "UPDATE etudiants SET nom=%s, prenom=%s WHERE id=%s",
        updates_etudiant
    )

    # 2. Mettre à jour les JSON dans paiements
    cur.execute("SELECT id, paiement_details FROM paiements WHERE paiement_details IS NOT NULL")
    paiement_rows = cur.fetchall()

    updates_paiement = []
    for (pid, paiement_details) in paiement_rows:
        try:
            if isinstance(paiement_details, str):
                data = json.loads(paiement_details)
            else:
                data = paiement_details

            def fix_details(obj):
                if isinstance(obj, dict):
                    if 'details_etudiant' in obj:
                        d = obj['details_etudiant']
                        if 'nom' in d:
                            d['nom'] = get_nom_latin(d['nom'])
                        if 'prenom' in d:
                            d['prenom'] = get_prenom_latin(d['prenom'])
                    for v in obj.values():
                        fix_details(v)
                elif isinstance(obj, list):
                    for item in obj:
                        fix_details(item)

            fix_details(data)
            updates_paiement.append((json.dumps(data, ensure_ascii=False), pid))
        except Exception as e:
            print(f"  ⚠ Paiement {pid} ignoré : {e}")

    print(f"  → {len(updates_paiement)} paiements à mettre à jour...")
    cur.executemany(
        "UPDATE paiements SET paiement_details=%s WHERE id=%s",
        updates_paiement
    )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Terminé !")
    print(f"\n📋 Mapping noms ({len(_nom_map)}) :")
    for k, v in _nom_map.items():
        print(f"   {k:30s} → {v}")
    print(f"\n📋 Mapping prénoms ({len(_prenom_map)}) :")
    for k, v in _prenom_map.items():
        print(f"   {k:40s} → {v}")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]

    if '--mysql' in args:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--mysql', action='store_true')
        parser.add_argument('--host', default='localhost')
        parser.add_argument('--port', type=int, default=3306)
        parser.add_argument('--user', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--db', required=True)
        parsed = parser.parse_args()
        run_mysql_mode(parsed.host, parsed.user, parsed.password, parsed.db, parsed.port)
    else:
        # Mode fichier SQL
        if len(args) < 1:
            print("Usage:")
            print("  Fichier SQL  : python anonymize_names.py dump.sql > dump_anonymise.sql")
            print("  MySQL direct : python anonymize_names.py --mysql --host localhost --user root --password secret --db ma_base")
            sys.exit(1)

        input_file = args[0]
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        result = process_sql_file(content)
        sys.stdout.write(result)

        # Affiche le mapping dans stderr pour référence
        print(f"\n-- Mapping noms ({len(_nom_map)}) :", file=sys.stderr)
        for k, v in _nom_map.items():
            print(f"--   {k:30s} → {v}", file=sys.stderr)
        print(f"-- Mapping prénoms ({len(_prenom_map)}) :", file=sys.stderr)
        for k, v in _prenom_map.items():
            print(f"--   {k:40s} → {v}", file=sys.stderr)