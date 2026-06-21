# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('Controllers', 'Controllers'), ('Helper', 'Helper'), ('Helper/.env', 'Helper'), ('api.zip', '.')],
    hiddenimports=[],    hookspath=[],    hooksconfig={},    runtime_hooks=[],
    excludes=[],    noarchive=False,    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,    a.scripts,    a.binaries,    a.datas,    [],    name='app',   debug=False,    bootloader_ignore_signals=False,    strip=False,    upx=True,    upx_exclude=[],    runtime_tmpdir=None,    console=True,    disable_windowed_traceback=False,    argv_emulation=False,    target_arch=None,    codesign_identity=None,    entitlements_file=None,
)
#--windows-disable-console --windows-disable-console

nuitka app.py --standalone --enable-plugin=pyside6 --include-data-dir=Controllers=Controllers --include-data-dir=Helper=Helper --include-data-file=Helper/.env=Helper/.env --include-data-file=api.zip=data/ --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware-server" --windows-product-name="School Server" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire server" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile

 #--include-data-file=Helper/.env=Helper/.env   --include-data-file=data/api.zip=data/api.zip #--include-data-file=data/Win64OpenSSL_Light-3_5_1.msi=data/Win64OpenSSL_Light-3_5_1.msi  

nuitka --standalone --onefile  --enable-plugin=pyside6  --include-data-dir=Controllers=Controllers   --include-data-dir=Helper=Helper --include-package-data=cryptography   --include-module=win32api   --include-module=win32security   --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico   --windows-company-name="Infini-Software-server"   --windows-product-name="ecole Serveur"   --windows-product-version="1.0.0"   --windows-file-version="1.0.0.0"   --windows-file-description="Logiciel de gestion scolaire server"   --output-dir=build   --remove-output   --nofollow-import-to=tkinter,test   --assume-yes-for-downloads   --lto=yes  app.py

nuitka --standalone --onefile  --enable-plugin=pyside6  --include-data-dir=Controllers=Controllers  --include-data-dir=Helper=Helper --include-package-data=cryptography  --include-module=win32api   --include-module=win32security   --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico   --windows-company-name="Infini-Software-server" --windows-product-name="ecole Serveur"   --windows-product-version="1.0.3"   --windows-file-version="1.0.0.3"   --windows-file-description="Logiciel de gestion scolaire server"  --output-dir=build   --remove-output   --nofollow-import-to=tkinter,test  --assume-yes-for-downloads   --lto=yes  app.py


nuitka --standalone --onefile  --enable-plugin=pyside6  --include-package=jinja2 --include-package=jinja2.ext --include-module=jinja2.ext --include-data-dir=Controllers=Controllers --include-data-dir=gtk_runtime=gtk_runtime --include-data-dir=app=app  --include-data-dir=Helper=Helper --include-package-data=cryptography  --include-module=win32api --include-module=win32security   --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico   --windows-company-name="Infini-Software-server" --windows-product-name="ecole Serveur"   --windows-product-version="1.0.3"   --windows-file-version="1.0.0.3"   --windows-file-description="Logiciel de gestion scolaire server"  --output-dir=build   --remove-output   --nofollow-import-to=tkinter,test  --assume-yes-for-downloads   --lto=yes  app.py

--nofollow-import-to=PyQt5 \
       --nofollow-import-to=PyQt6 \
       --nofollow-import-to=PySide2 \


--enable-plugin=pandas

nuitka --standalone --onefile --onefile-tempdir-spec="{CACHE_DIR}/Esystem/cache" --enable-plugin=pyside6 --nofollow-import-to=PyQt5 --nofollow-import-to=PyQt6 --nofollow-import-to=PySide2 --include-package=jinja2 --include-package=uvicorn --include-package=limits --include-package=slowapi --include-data-dir=Controllers=Controllers --include-data-dir=app=app --include-data-dir=app/alembic=app/alembic --include-data-dir=c:\users\fritz\appdata\local\programs\python\python310\lib\site-packages\limits\resources=limits/resources --include-data-files=app/alembic.ini=app/alembic.ini --include-data-files=app/alembic/versions/*.py=app/alembic/versions/ --include-data-file=app/alembic/env.py=app/alembic/env.py --nofollow-import-to=app.alembic --include-module=logging.config --include-data-dir=Helper=Helper --include-package-data=cryptography --include-module=win32api --include-module=win32security --windows-icon-from-ico=C:\ecole_nginx\icon_server.ico --windows-company-name="Infini-Software-server" --windows-product-name="ecole Serveur" --windows-product-version="1.0.3" --windows-file-version="1.0.4" --windows-file-description="Logiciel de gestion scolaire server" --output-dir=build --remove-output --nofollow-import-to=tkinter,test --assume-yes-for-downloads --lto=yes app.py

nuitka --standalone --onefile  --onefile-tempdir-spec="{CACHE_DIR}/Esystem/cache"  --enable-plugin=pyside6  --nofollow-import-to=PyQt5 --nofollow-import-to=PyQt6 --nofollow-import-to=PySide2  --include-package=jinja2 --include-package=uvicorn --include-data-dir=Controllers=Controllers --include-data-dir=app=app --include-data-dir=app/alembic=app/alembic --include-data-files=app/alembic.ini=app/alembic.ini --include-data-files=app/alembic/versions/*.py=app/alembic/versions/  --include-data-file=app/alembic/env.py=app/alembic/env.py --nofollow-import-to=app.alembic --include-module=logging.config  --include-data-dir=Helper=Helper --include-package-data=cryptography  --include-module=win32api --include-module=win32security --windows-icon-from-ico=C:\ecole_nginx\icon_server.ico   --windows-company-name="Infini-Software-server" --windows-product-name="ecole Serveur"   --windows-product-version="1.0.3"   --windows-file-version="1.0.4"   --windows-file-description="Logiciel de gestion scolaire server"  --output-dir=build   --remove-output   --nofollow-import-to=tkinter,test  --assume-yes-for-downloads --lto=yes  app.py


nuitka --standalone --onefile --onefile-tempdir-spec="{CACHE_DIR}/Esystem/cache" --enable-plugin=pyside6 --nofollow-import-to=PyQt5 --nofollow-import-to=PyQt6 --nofollow-import-to=PySide2 --include-package=jinja2 --include-package=uvicorn --include-data-dir=Controllers=Controllers --include-data-dir=app=app --include-data-dir=app/alembic=app/alembic --include-data-files=app/alembic.ini=app/alembic.ini --include-data-files=app/alembic/versions/*.py=app/alembic/versions/ --include-data-file=app/alembic/env.py=app/alembic/env.py --nofollow-import-to=app.alembic --include-module=logging.config --include-data-dir=Helper=Helper --include-package-data=cryptography --include-module=win32api --include-module=win32security --windows-icon-from-ico=C:\ecole_nginx\icon_server.ico --windows-company-name="Infini-Software-server" --windows-product-name="ecole Serveur" --windows-product-version="1.0.3" --windows-file-version="1.0.4" --windows-file-description="Logiciel de gestion scolaire server" --output-dir=build --remove-output --nofollow-import-to=tkinter,test --assume-yes-for-downloads --lto=yes app.py




#!/bin/bash

echo "🚀 Démarrage du build Linux..."

# Vérifier les dépendances
command -v gcc >/dev/null 2>&1 || { echo "❌ gcc manquant : sudo apt install gcc"; exit 1; }
command -v patchelf >/dev/null 2>&1 || { echo "❌ patchelf manquant : sudo apt install patchelf"; exit 1; }

# Build
nuitka \
  --standalone \
  --onefile \
  --onefile-tempdir-spec="{TEMP}/Esystem/cache" \
  --nofollow-import-to=PyQt5 \
  --nofollow-import-to=PyQt6 \
  --nofollow-import-to=PySide2 \
  --include-package=jinja2 \
  --include-package=uvicorn \
  --include-data-dir=Controllers=Controllers \
  --include-data-dir=app=app \
  --include-data-dir=app/alembic=app/alembic \
  --include-data-files=app/alembic.ini=app/alembic.ini \
  --include-data-files=app/alembic/versions/*.py=app/alembic/versions/ \
  --include-data-file=app/alembic/env.py=app/alembic/env.py \
  --nofollow-import-to=app.alembic \
  --include-module=logging.config \
  --include-data-dir=Helper=Helper \
  --include-package-data=cryptography \
  --output-dir=build \
  --remove-output \
  --nofollow-import-to=tkinter,test \
  --assume-yes-for-downloads \
  --lto=yes \
  app.py

echo "✅ Build terminé : build/app"