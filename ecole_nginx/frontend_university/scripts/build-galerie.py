"""Génère les images de la galerie publique (/galerie) à partir des originaux.

Usage (depuis frontend_university/) :
    python3 scripts/build-galerie.py [dossier_source]

Par défaut, lit c-photo-download-1of1/Highlights/ (originaux 3600px, hors git)
et écrit :
  - public/images/galerie/full/<n>.webp   (côté long 1600px, pour la lightbox)
  - public/images/galerie/thumb/<n>.webp  (côté long 600px, pour la grille)
  - src/data/galerie.js                   (manifeste : src, miniature, dimensions)

Relancer le script après avoir ajouté des photos : tout est régénéré.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'c-photo-download-1of1' / 'Highlights'
OUT = ROOT / 'public' / 'images' / 'galerie'
MANIFEST = ROOT / 'src' / 'data' / 'galerie.js'

SIZES = {'full': (1600, 80), 'thumb': (600, 72)}


def main():
    files = sorted(p for p in SRC.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'})
    if not files:
        sys.exit(f'Aucune image trouvée dans {SRC}')

    if OUT.exists():
        shutil.rmtree(OUT)
    for name in SIZES:
        (OUT / name).mkdir(parents=True)

    photos = []
    for i, path in enumerate(files, 1):
        img = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        name = f'{i:03d}.webp'
        for folder, (edge, quality) in SIZES.items():
            copy = img.copy()
            copy.thumbnail((edge, edge), Image.LANCZOS)
            copy.save(OUT / folder / name, 'WEBP', quality=quality, method=6)
            if folder == 'full':
                w, h = copy.size
        photos.append({
            'src': f'/images/galerie/full/{name}',
            'thumb': f'/images/galerie/thumb/{name}',
            'w': w,
            'h': h,
        })
        print(f'{path.name} -> {name} ({w}x{h})')

    MANIFEST.write_text(
        '// Généré par scripts/build-galerie.py — ne pas modifier à la main.\n'
        f'export const GALERIE = {json.dumps(photos, indent=2)}\n',
        encoding='utf-8',
    )
    print(f'{len(photos)} photos -> {OUT.relative_to(ROOT)}, manifeste -> {MANIFEST.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
