# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('Models', 'Models'), ('Views', 'Views'), ('Controllers', 'Controllers'), ('assets', 'assets'), ('Config.py', '.'), ('Helper', 'Helper'), ('utils', 'utils')],

    hiddenimports=[
        'cv2', 
        'numpy'
    ],
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


le "back" pour pyside c'est avant tout QT, donc il faut (pas sûr des noms hors manjaro/archlinux) simplement installer la dépendance optionnelle qt6-multimedia et sa dépendance qui va suivre automatiquement à l'install "qt6-multimedia-backend" (soit qt6-multimedia-ffmpeg ou qt6-multimedia-gstreamer)


ps2exe -fileName "Lekol360.exe" -inputFile "Splash.ps1" -iconFile "C:\Users\fritz\OneDrive\Desktop\school_client\assets\icons\favicon.ico" -noConsole

ps2exe -input "screen_launcher.ps1" -output "Lekol360.exe" -icon "C:\Users\fritz\OneDrive\Desktop\school_client\assets\icons\favicon.ico" -noConsole

ps2exe -input "screen_launcher.ps1" -output "Lekol360.exe" -icon "C:\Users\fritz\OneDrive\Desktop\school_client\assets\icons\favicon.ico" -company "Infini-software" -description "Gestion Scolaire" -version "1.0.0.0" -noConsole

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\TonProjet\dist\Lekol360_Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\TonProjet\dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
; N'oublie pas d'inclure l'image de fond du splash ici aussi !

[Icons]
; Le raccourci pointe sur le Launcher, PAS sur l'app directement
Name: "{autodesktop}\Lekol 360"; Filename: "{app}\Lekol360_Launcher.exe"; IconFilename: "{app}\logo.ico"





nuitka app.py --standalone --enable-plugin=pyside6 --onefile-tempdir-spec="{CACHE_DIR}/ESysClient/cache" --include-qt-plugins=multimedia,platforms,imageformats --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py  --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build  --remove-output --nofollow-import-to=tkinter,test,unittest,pydoc --noinclude-qt-translation --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.1.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\OneDrive\Desktop\school_client\assets\icons\favicon.ico --windows-disable-console --onefile --lto=yeslto=yes

nuitka app.py --standalone --enable-plugin=pyside6 --onefile-tempdir-spec="{CACHE_DIR}/ESysClient/cache" --include-qt-plugins=multimedia,platforms,imageformats --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build --remove-output --nofollow-import-to=tkinter,test,unittest,pydoc --noinclude-qt-translation --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.1.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=assets\icons\favicon.ico --windows-disable-console --onefile --assume-yes-for-downloads --lto=yes app.py
