"""Compile les scripts de migration Alembic (env.py + versions/*.py) en
bytecode .pyc puis supprime les .py sources, avant le build Nuitka.

Alembic charge ces fichiers via util.load_python_file(), pas via un import
Python normal (d'où --nofollow-import-to=app.alembic dans les workflows) —
et cette fonction sait nativement charger un .pyc (alembic/util/pyfiles.py).
Le binaire distribué peut donc exécuter les migrations sans exposer leur
code source.
"""
import py_compile
import sys
from pathlib import Path

ALEMBIC_DIR = Path(__file__).resolve().parent.parent / "app" / "alembic"

files = [ALEMBIC_DIR / "env.py", *sorted((ALEMBIC_DIR / "versions").glob("*.py"))]

for src in files:
    pyc = src.with_suffix(".pyc")
    py_compile.compile(str(src), cfile=str(pyc), doraise=True)
    src.unlink()

print(f"{len(files)} script(s) Alembic compilé(s) en .pyc, sources supprimées.", file=sys.stderr)
