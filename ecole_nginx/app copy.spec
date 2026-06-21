# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('Controllers', 'Controllers'), ('Helper', 'Helper'), ('Helper/.env', 'Helper'), ('api.zip', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

nuitka --standalone --onefile --windows-console-mode=force `
    --enable-plugin=pyside6 `
    --include-data-files="Controllers/*.*=Controllers/" `
    --include-data-files="Helper/*.*=Helper/" `
    --include-data-file="Helper/.env=Helper/.env" `
    --include-data-file="api.zip=api.zip" `
    --nofollow-import-to="tkinter,unittest,PyQt5,numpy,matplotlib" `
    --output-dir=dist app.py

    upx --best --lzma --force dist/app.exe

