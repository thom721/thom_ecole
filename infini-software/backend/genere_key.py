import hashlib
import base64
import hmac
import os
import uuid
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("KEY_SECRET", "CLE_SECRETE_PERSO")

def generate_activation_key(mac_address, days_valid=30):
    """Génère une clé d'activation alphanumérique avec tirets (XXXX-XXXX-XXXX-XXXX)."""

    expiration_date =(datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    raw_data = f"{mac_address}-{expiration_date}-{days_valid}-{SECRET_KEY}".encode()

    hashed = hmac.new(SECRET_KEY.encode(), raw_data, hashlib.sha256).digest()
    encoded_key = base64.b32encode(hashed).decode().upper()

    clean_key = ''.join(filter(str.isalnum, encoded_key))[:16]

    formatted_key = '-'.join(clean_key[i:i+4] for i in range(0, len(clean_key), 4))

    return formatted_key, expiration_date,days_valid



if __name__ == "__main__":
    mac = input("Entrez l'adresse MAC du client (ex: 4C:CC:6A:3F:A1:42): ").strip()

    openssl = shutil.which('openssl')
    if openssl:
        print(Path(openssl))
    
    if mac:
        key, expiration_date, days_valid = generate_activation_key(mac_address=mac, days_valid=30)
        print("\n✅ Clé d'activation générée :")
        print("Clé :", key)
        print("expiration_date :", expiration_date)
        print("mac :", mac)
        print("days_valid :", days_valid)
    else:
        print("⚠️ Adresse MAC invalide.")

# B4:B5:2F:7F:F6:AF
# 00:45:e2:3d:c1:af
# 84:A6:C8:F3:D5:B8


