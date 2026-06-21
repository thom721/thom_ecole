#!/bin/bash
# Affiche l'état de la licence et permet d'en saisir une nouvelle.
# Équivalent Mac/Linux de l'écran d'activation Windows (Helper/verify_key.py
# ask_for_activation_key()), mais en ligne de commande puisqu'il n'y a pas de
# fenêtre PySide6 dans l'installation Docker.
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

if ! docker compose ps app >/dev/null 2>&1; then
    echo "❌ Le service 'app' ne semble pas démarré. Lance d'abord ./scripts/start.sh"
    exit 1
fi

echo "==> État actuel de la licence :"
docker compose exec -T app python -c "
from app.Helper.license_check import ensure_trial_license, is_license_valid, get_host_mac
key, expiration_date = ensure_trial_license()
print(f'  Adresse MAC utilisée : {get_host_mac()}')
print(f'  Clé enregistrée      : {key}')
print(f'  Expire le            : {expiration_date}')
print(f'  Valide               : {is_license_valid()}')
"

echo ""
read -rp "Entrer une nouvelle clé d'activation (laisser vide pour ne rien changer) : " NEW_KEY

if [ -z "$NEW_KEY" ]; then
    echo "Aucun changement."
    exit 0
fi

docker compose exec -T app python -c "
from app.Helper.license_check import verify_and_save_activation_key
ok = verify_and_save_activation_key('$NEW_KEY')
print('✅ Clé acceptée et enregistrée.' if ok else '❌ Clé invalide pour cette machine (ou pas générée aujourd\'hui).')
"
