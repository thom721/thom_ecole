#!/bin/bash
# Mode HEADLESS (sans fenêtre) : démarre tout en conteneurs Docker, y compris
# l'API (service "app"). Pour un poste Mac/Linux avec écran et une fenêtre de
# contrôle comme sur Windows, utilise plutôt `python3 app_gui.py` (voir ce
# fichier) — ne lance pas les deux en même temps, ils se disputeraient le port
# 9001 (app_gui.py démarre seulement mysql/nginx en Docker et l'API en natif).
#
# Équivalent du rôle joué par app.py + check_mysql_prerequisites() côté Windows :
# vérifie les prérequis avant de lancer, plutôt que de laisser échouer plus loin
# avec une erreur confuse.
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"
echo "==> Dossier du projet : $PROJECT_DIR"

# 1. Docker installé ?
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker n'est pas installé ou pas dans le PATH."
    echo "   Mac    : https://www.docker.com/products/docker-desktop/"
    echo "   Linux  : https://docs.docker.com/engine/install/"
    exit 1
fi
echo "✅ Docker trouvé : $(docker --version)"

# 2. Docker Compose (plugin v2) disponible ?
if ! docker compose version >/dev/null 2>&1; then
    echo "❌ Le plugin 'docker compose' (v2) n'est pas disponible."
    echo "   Mets à jour Docker Desktop, ou installe le plugin docker-compose-v2."
    exit 1
fi
echo "✅ Docker Compose trouvé : $(docker compose version --short)"

# 3. Le daemon Docker tourne-t-il réellement ?
if ! docker info >/dev/null 2>&1; then
    echo "❌ Le démon Docker ne répond pas."
    echo "   Mac    : ouvre l'application Docker Desktop et attends qu'elle soit prête."
    echo "   Linux  : sudo systemctl start docker"
    exit 1
fi
echo "✅ Le démon Docker répond."

# 4. Ports nécessaires libres (avertissement seulement, pas bloquant).
# Ignoré silencieusement si lsof n'est pas installé sur la machine.
if command -v lsof >/dev/null 2>&1; then
    for port in 80 443 3306 9001; do
        if lsof -i ":$port" -sTCP:LISTEN >/dev/null 2>&1; then
            echo "⚠️  Le port $port semble déjà utilisé par un autre processus."
            echo "    docker compose pourrait échouer à démarrer le service correspondant."
        fi
    done
fi

# 5. Adresse MAC de la machine hôte, pour la licence (app/Helper/license_check.py).
# Calculée ici plutôt que dans le conteneur, qui verrait sa propre interface
# réseau virtuelle et non celle de la machine hôte. Même algorithme que
# get_mac_reliable() utilisé partout ailleurs dans le projet (uuid.getnode()).
HOST_MAC_ADDRESS=""
if command -v python3 >/dev/null 2>&1; then
    HOST_MAC_ADDRESS="$(python3 -c "import uuid, re; print(':'.join(re.findall('..', '%012x' % uuid.getnode())).upper())" 2>/dev/null || true)"
fi
if [ -n "$HOST_MAC_ADDRESS" ]; then
    echo "✅ Adresse MAC hôte détectée pour la licence : $HOST_MAC_ADDRESS"
else
    echo "⚠️  Impossible de détecter l'adresse MAC hôte (python3 introuvable) : la licence"
    echo "    utilisera l'adresse MAC vue depuis l'intérieur du conteneur (moins stable)."
fi
export HOST_MAC_ADDRESS

echo ""
echo "==> Démarrage des services (mysql, app, certgen, nginx)..."
docker compose up -d --build

echo ""
echo "✅ Démarré. API directe : http://localhost:9001"
echo "   Pour activer https://aplekol360.local sans avertissement SSL, lance ensuite :"
echo "   ./scripts/setup-local-https.sh"
echo "   Pour voir l'état de la licence et l'activer : ./scripts/activate-license.sh"
echo "   Pour créer le premier compte administrateur (base fraîche) : ./scripts/create-first-admin.sh"
