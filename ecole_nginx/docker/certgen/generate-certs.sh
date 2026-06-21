#!/bin/sh
# Génère une CA locale + un certificat serveur pour aplekol360.local,
# avec la même logique que genere_ssl_key() dans Controllers/Main_run.py
# (l'installateur Windows natif), adaptée pour tourner dans un conteneur Alpine.
# Idempotent : si les certificats existent déjà dans le volume, ne refait rien.
set -e

CERTS_DIR=/certs
CA_KEY="$CERTS_DIR/ca.key"
CA_CERT="$CERTS_DIR/ca.pem"
KEY_PATH="$CERTS_DIR/aplekol360.local-key.pem"
CERT_PATH="$CERTS_DIR/aplekol360.local.pem"
DOMAIN="aplekol360.local"

if [ -f "$CERT_PATH" ] && [ -f "$KEY_PATH" ] && [ -f "$CA_CERT" ]; then
    echo "Certificats déjà présents dans $CERTS_DIR, rien à faire."
    exit 0
fi

apk add --no-cache openssl >/dev/null 2>&1

mkdir -p "$CERTS_DIR"

# SERVER_IP (optionnel) : adresse LAN du serveur, pour que les postes clients
# du réseau local puissent aussi se connecter sans avertissement SSL.
EXTRA_IP_LINE=""
if [ -n "$SERVER_IP" ]; then
    EXTRA_IP_LINE="IP.2 = $SERVER_IP"
fi

cat > "$CERTS_DIR/ca.cnf" <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = ${DOMAIN} Root CA

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
EOF

cat > "$CERTS_DIR/san.cnf" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = ${DOMAIN}

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = localhost
IP.1 = 127.0.0.1
${EXTRA_IP_LINE}
EOF

echo "🔐 Génération de la CA locale..."
openssl genrsa -out "$CA_KEY" 2048
openssl req -x509 -new -nodes -key "$CA_KEY" -sha256 -days 3650 \
    -out "$CA_CERT" -config "$CERTS_DIR/ca.cnf" -extensions v3_ca

echo "🔐 Génération du certificat serveur pour ${DOMAIN}..."
openssl genrsa -out "$KEY_PATH" 2048
openssl req -new -key "$KEY_PATH" -out "$CERTS_DIR/${DOMAIN}.csr" -config "$CERTS_DIR/san.cnf"
# 825 jours max pour le certificat serveur (pas la CA) : au-delà, macOS/iOS le
# rejette comme "non conforme aux normes" (politique Apple depuis 10.15/iOS 13),
# même si la CA est correctement installée comme racine de confiance.
openssl x509 -req -in "$CERTS_DIR/${DOMAIN}.csr" -CA "$CA_CERT" -CAkey "$CA_KEY" \
    -CAcreateserial -out "$CERT_PATH" -days 825 -sha256 \
    -extfile "$CERTS_DIR/san.cnf" -extensions v3_req

chmod 644 "$CA_CERT" "$CERT_PATH"
chmod 600 "$CA_KEY" "$KEY_PATH"

echo "✅ Certificats générés dans $CERTS_DIR"
