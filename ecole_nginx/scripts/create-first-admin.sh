#!/bin/bash
# Crée le premier compte administrateur si aucun n'existe encore sur ce serveur.
# Équivalent Mac/Linux de insert_user()/ask_for_user_data() dans
# Controllers/Main_run.py (installateur Windows natif), en ligne de commande
# puisqu'il n'y a pas de fenêtre PySide6 dans l'installation headless. Pour le
# mode GUI natif (app_gui.py), voir gui/first_account.py — fait automatiquement
# la même chose au premier lancement.
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"
API_URL="http://localhost:9001/api/v1"

if ! docker compose ps app >/dev/null 2>&1; then
    echo "❌ Le service 'app' ne semble pas démarré. Lance d'abord ./scripts/start.sh"
    exit 1
fi

STATUS="$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/first-check" || echo "000")"
if [ "$STATUS" = "200" ]; then
    echo "✅ Un compte administrateur existe déjà, rien à faire."
    exit 0
fi

echo "==> Aucun compte administrateur trouvé. Création du premier compte."
read -rp "Nom : " NOM
read -rp "Prénom : " PRENOM
read -rp "Email : " EMAIL
read -rsp "Mot de passe : " PASSWORD
echo ""

echo "==> Initialisation des rôles/permissions..."
FILL_STATUS="$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/first-account-fill")"
if [ "$FILL_STATUS" != "200" ]; then
    echo "❌ Échec de l'initialisation des rôles/permissions (HTTP $FILL_STATUS)."
    exit 1
fi

echo "==> Création du compte..."
ACCOUNT_STATUS="$(NOM="$NOM" PRENOM="$PRENOM" EMAIL="$EMAIL" PASSWORD="$PASSWORD" API_URL="$API_URL" python3 -c "
import os, json, urllib.request

payload = json.dumps({
    'nom': os.environ['NOM'], 'prenom': os.environ['PRENOM'],
    'email': os.environ['EMAIL'], 'first': True, 'password': os.environ['PASSWORD'],
}).encode()
req = urllib.request.Request(
    f\"{os.environ['API_URL']}/first-account\", data=payload,
    headers={'Content-Type': 'application/json'}, method='POST',
)
try:
    with urllib.request.urlopen(req) as resp:
        print('OK')
except urllib.error.HTTPError as e:
    print(f'ERREUR ({e.code}) : {e.read().decode(errors=\"replace\")}')
")"

if [ "$ACCOUNT_STATUS" != "OK" ]; then
    echo "❌ Création du compte échouée : $ACCOUNT_STATUS"
    exit 1
fi
echo "✅ Compte administrateur créé. Vous pouvez maintenant vous connecter depuis school_client."

# Comme Windows (insert_user() dans Controllers/Main_run.py) : enregistre le
# premier compte côté infini-software.cloud. Exécuté dans le conteneur "app"
# (dépendances déjà présentes là, pas forcément sur l'hôte). Un échec ici ne
# doit jamais faire échouer ce script (même comportement que Windows).
docker compose exec -T -e NOM="$NOM" -e PRENOM="$PRENOM" -e EMAIL="$EMAIL" app python3 -c "
import os, json, urllib.request
from app.Helper.license_check import get_host_mac

payload = json.dumps({
    'nom': os.environ['NOM'], 'prenom': os.environ['PRENOM'],
    'email': os.environ['EMAIL'], 'mac': get_host_mac(),
}).encode()
req = urllib.request.Request(
    'https://www.infini-software.cloud/api/save-data', data=payload,
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST',
)
try:
    urllib.request.urlopen(req, timeout=15)
except Exception:
    pass
" 2>/dev/null || true
