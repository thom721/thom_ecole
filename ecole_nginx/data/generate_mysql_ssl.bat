@echo off
set OPENSSL_PATH=C:\Program Files\OpenSSL-Win64\bin\openssl.exe
set OUTPUT_DIR=%~dp0certs

if not exist "%OPENSSL_PATH%" (
    echo ❌ OpenSSL non trouvé. Vérifie que OpenSSL est installé ici : %OPENSSL_PATH%
    pause
    exit /b
)

if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

cd /d "%OUTPUT_DIR%"

echo 📌 Génération de la clé CA...
"%OPENSSL_PATH%" genrsa 2048 > ca-key.pem

echo 📌 Génération du certificat CA...
"%OPENSSL_PATH%" req -new -x509 -nodes -days 3650 -key ca-key.pem -out ca.pem -subj "/CN=MySQL_CA"

echo 📌 Génération de la clé serveur...
"%OPENSSL_PATH%" genrsa 2048 > server-key.pem

echo 📌 Création de la requête de certificat serveur...
"%OPENSSL_PATH%" req -new -key server-key.pem -out server-req.pem -subj "/CN=MySQL_Server"

echo 📌 Signature du certificat serveur avec la CA...
"%OPENSSL_PATH%" x509 -req -in server-req.pem -days 3650 -CA ca.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem

echo ✅ Fichiers générés dans : %OUTPUT_DIR%

pause
