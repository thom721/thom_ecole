def normaliser_mac(mac: str) -> str:
    """Normalise une adresse MAC (espaces + casse) avant toute lecture/écriture
    en base : deux clients ne doivent jamais pouvoir coexister sous 'AA:BB:...'
    et 'aa:bb:...' — l'index UNIQUE SQLite sur `clients.mac` est sensible à la
    casse et ne les distinguerait pas comme un doublon."""
    return mac.strip().upper()
