#!/bin/bash
# À lancer manuellement (pas automatisé) APRES un premier `docker compose up -d`,
# une fois que le service "certgen" a généré les certificats.
# Modifie /etc/hosts et le magasin de certificats de confiance du système —
# nécessite sudo. Équivalent Mac/Linux de add_or_update_host() +
# update_windows_certificate_store() dans Controllers/Main_run.py (Windows).
set -e

DOMAIN="aplekol360.local"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EXPORT_DIR="$PROJECT_DIR/docker-certs-export"
HOSTS_FILE="/etc/hosts"

echo "==> Système détecté : $(uname -s)"

# 1. Ajoute aplekol360.local -> 127.0.0.1 dans /etc/hosts si absent
if ! grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
    echo "==> Ajout de '127.0.0.1 $DOMAIN' dans $HOSTS_FILE (mot de passe sudo requis)"
    echo "127.0.0.1 $DOMAIN" | sudo tee -a "$HOSTS_FILE" > /dev/null
else
    echo "==> $DOMAIN est déjà présent dans $HOSTS_FILE"
fi

# 2. Récupère le certificat de la CA généré par le conteneur "certgen"
mkdir -p "$EXPORT_DIR"
echo "==> Récupération du certificat de la CA (ca.pem) depuis le conteneur certgen..."
(cd "$PROJECT_DIR" && docker compose cp certgen:/certs/ca.pem "$EXPORT_DIR/ca.pem")

# 3. Installe la CA dans le magasin de confiance du système
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
    echo "==> Installation de la CA dans le Keychain système (mot de passe sudo requis)"
    sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$EXPORT_DIR/ca.pem"
elif [ "$OS" = "Linux" ]; then
    echo "==> Installation de la CA dans le magasin de certificats Linux (mot de passe sudo requis)"
    sudo cp "$EXPORT_DIR/ca.pem" /usr/local/share/ca-certificates/aplekol360-ca.crt
    sudo update-ca-certificates
else
    echo "❌ OS non supporté pour l'installation automatique de la CA : $OS"
    exit 1
fi

echo "✅ Terminé. https://$DOMAIN devrait être accessible sans avertissement SSL."
echo "   (Pour un accès depuis d'autres postes du réseau, relancez 'docker compose up' avec"
echo "   SERVER_IP=<ip_lan_du_serveur> dans l'environnement du service certgen, et ajoutez"
echo "   '<ip_lan_du_serveur> $DOMAIN' dans le fichier hosts de chaque poste client.)"
