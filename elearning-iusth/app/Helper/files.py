import os
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.config.Config import settings
from app.database import generate_uuid


def save_upload(upload: UploadFile, subdir: str) -> tuple[str, int]:
    """Écrit le fichier sur disque sous UPLOAD_DIR/subdir/<uuid>_<nom
    original> et renvoie (chemin_stocké, taille_en_octets)."""
    target_dir = Path(settings.UPLOAD_DIR) / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{generate_uuid()}_{os.path.basename(upload.filename or 'fichier')}"
    stored_path = target_dir / safe_name

    size = 0
    with open(stored_path, "wb") as out:
        while chunk := upload.file.read(1024 * 1024):
            out.write(chunk)
            size += len(chunk)

    return str(stored_path), size


def resolve_download(stored_path: str, filename: str, mime_type: str | None) -> FileResponse:
    """Sert un fichier déjà uploadé, sous son nom d'origine — jusqu'à
    l'Épic 18, aucun fichier uploadé n'était réellement servable
    (ni montage statique, ni endpoint), corrigé au passage (voir plan)."""
    if not os.path.isfile(stored_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable sur le serveur")
    return FileResponse(stored_path, filename=filename, media_type=mime_type or "application/octet-stream")
