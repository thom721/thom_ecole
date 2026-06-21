# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('Models', 'Models'), ('Views', 'Views'), ('Controllers', 'Controllers'), ('assets', 'assets'), ('Config.py', '.'), ('Helper', 'Helper'), ('utils', 'utils')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'PyQt5', 'numpy', 'matplotlib', PySide6.QtMultimedia, PySide6.QtWebEngineWidgets],
    noarchive=False,
    optimize=0,

)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher, compressed=True)


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
exe = EXE(
    pyi_archive,
    a.scripts,
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False
)



nuitka --standalone --onefile --windows-console-mode=force `
    --enable-plugin=pyside6 `
    --include-data-dir="Models=Models" `
    --include-data-dir="Views=Views" `
    --include-data-dir="Controllers=Controllers" `
    --include-data-dir="assets=assets" `
    --include-data-dir="Helper=Helper" `
    --include-data-dir="utils=utils" `
    --include-data-file="Config.py=Config.py" `
    --nofollow-import-to="tkinter,unittest,PyQt5,numpy,matplotlib" `
    --output-dir=dist app.py


nuitka --standalone --onefile --windows-console-mode=force `
    --enable-plugin=pyside6 `
    --include-data-files="Models/*.*=Models/"`
    --include-data-files="Views/*.*=Views/"
    --include-data-files="Controllers/*.*=Controllers/"`
    --include-data-files="Helper/*.*=Helper/"`
    --include-data-files="utils/*.*=utils/"`
    --include-data-dir="assets=assets" `
    --include-data-file="Config.py=Config.py" `
    --nofollow-import-to="tkinter,unittest,PyQt5,numpy,matplotlib" `
    --output-dir=dist app.py

nuitka --standalone --onefile --windows-console-mode=force `
    --enable-plugin=pyside6 `
    --include-data-files="Models/*.*=Models/" `
    --include-data-files="Views/*.*=Views/" `
    --include-data-files="Controllers/*.*=Controllers/" `
    --include-data-files="Helper/*.*=Helper/" `
    --include-data-files="utils/*.*=utils/" `
    --include-data-dir="assets=assets" `
    --include-data-file="Config.py=Config.py" `
    --nofollow-import-to="tkinter,unittest,PyQt5,numpy,matplotlib" `
    --output-dir=dist app.py


    upx --best --lzma dist/app.exe
upx --best --lzma dist/*.dll


nuitka app.py `
--standalone `
--enable-plugin=numpy `
--enable-plugin=cv2 `
--include-data-dir=Models=Models `
--include-data-dir=Views=Views `
--include-data-dir=Controllers=Controllers `
--include-data-dir=assets=assets `
--include-data-file=Config.py=. `
--include-data-dir=Helper=Helper `
--include-data-dir=utils=utils `
--output-dir=build `
--remove-output `
--windows-disable-console=no `
--nofollow-import-to=tkinter,test `
--assume-yes-for-downloads `
--onefile


nuitka app.py --standalone --enable-plugin=numpy --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=. --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build --remove-output --nofollow-import-to=tkinter,test --assume-yes-for-downloads --onefile


nuitka app.py --standalone --enable-plugin=numpy --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=. --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build --remove-output --nofollow-import-to=tkinter,test --assume-yes-for-downloads --windows-disable-console --onefile


nuitka app.py --standalone --enable-plugin=numpy `
--include-data-dir=Models=Models `
--include-data-dir=Views=Views `
--include-data-dir=Controllers=Controllers `
--include-data-dir=assets=assets `
--include-data-file=Config.py=. `
--include-data-dir=Helper=Helper `
--include-data-dir=utils=utils `
--output-dir=build `
--remove-output `
--nofollow-import-to=tkinter,test `
--assume-yes-for-downloads `
--windows-company-name="Mon École" `
--windows-product-name="School Client" `
--windows-product-version="1.0.0" `
--windows-file-version="1.0.0.0" `
--windows-file-description="Logiciel de gestion scolaire"` 
--onefile


nuitka app.py --standalone --enable-plugin=numpy `
--include-data-dir=Models=Models `
--include-data-dir=Views=Views `
--include-data-dir=Controllers=Controllers `
--include-data-dir=assets=assets `
--include-data-file=Config.py=. `
--include-data-dir=Helper=Helper `
--include-data-dir=utils=utils `
--output-dir=build `
--remove-output `
--nofollow-import-to=tkinter,test `
--assume-yes-for-downloads `
--windows-company-name="Mon École" `
--windows-product-name="School Client" `
--windows-product-version="1.0.0" `
--windows-file-version="1.0.0.0" `
--windows-file-description="Logiciel de gestion scolaire" `
--onefile


nuitka app.py --standalone --enable-plugin=pyside6 --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=data/Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico
 --onefile

nuitka --standalone --onefile --windows-console-mode=force `
    --enable-plugin=pyside6 `
    --include-data-dir="Models=Models" `
    --include-data-dir="Views=Views" `
    --include-data-dir="Controllers=Controllers" `
    --include-data-dir="assets=assets" `
    --include-data-dir="Helper=Helper" `
    --include-data-dir="utils=utils" `
    --include-data-file="Config.py=Config.py" `
    --nofollow-import-to="tkinter,unittest,PyQt5,numpy,matplotlib" `
    --windows-file-description="Logiciel de gestion scolaire"`
    --windows-product-name="School Client"`
    --output-dir=dist app.py


nuitka app.py --standalone --enable-plugin=numpy --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=data/Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --include-data-dir="C:\Users\fritz\AppData\Local\Programs\Python\Python310\Lib\site-packages\PySide6\plugins\platforms=platforms" --output-dir=build --remove-output --nofollow-import-to=tkinter,test --assume-yes-for-downloads --windows-company-name="Mon École" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --onefile


nuitka app.py --standalone --enable-plugin=pyside6 --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=data/Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --windows-disable-console  --onefile


 --include-package=weasyprint  --include-package=cairocffi --include-package=tinycss2 --include-package=cssselect2 --include-package=html5lib 
    --include-data-dir="c:\users\fritz\onedrive\desktop\school_client\lib\site-packages\weasyprint\resources=weasyprint\resources" 

--include-data-dir=Weasyprint=Weasyprint

    nuitka app.py --standalone --enable-plugin=pyside6  --include-package=weasyprint  --include-package=cairocffi --include-package=tinycss2 --include-package=cssselect2 --include-package=html5lib    --include-data-dir="c:\users\fritz\onedrive\desktop\school_client\lib\site-packages\weasyprint\resources=weasyprint\resources"  --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=data/Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico  --onefile

  
  --include-data-file=C:/msys64/mingw64/bin/libgobject-2.0-0.dll=libgobject-2.0-0.dll 
  --include-data-file=C:/msys64/mingw64/bin/libpango-1.0-0.dll=libpango-1.0-0.dll 
  --include-data-file=C:/msys64/mingw64/bin/libcairo-2.dll=libcairo-2.dll 
  --include-data-file=C:/msys64/mingw64/bin/libgdk_pixbuf-2.0-0.dll=libgdk_pixbuf-2.0-0.dll 
  --include-data-file=C:/msys64/mingw64/bin/libfontconfig-1.dll=libfontconfig-1.dll 
  --include-data-file=C:/msys64/mingw64/bin/libfreetype-6.dll=libfreetype-6.dll 
  --include-data-file=C:/msys64/mingw64/bin/libharfbuzz-0.dll=libharfbuzz-0.dll 
  --include-data-file=C:/msys64/mingw64/bin/libfribidi-0.dll=libfribidi-0.dll  



nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia,audio,mediaservice --include-data-dir=/Lib/site-packages/PySide6/plugins/multimedia=PySide6/plugins/multimedia --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --include-data-dir=templates=templates --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile


nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia --include-data-dir=C:/Users/fritz/OneDrive/Desktop/school_client/Lib/site-packages/PySide6/plugins/multimedia=PySide6/plugins/multimedia --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --include-data-dir=templates=templates --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile


nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia,platforms --include-data-dir=C:/Users/fritz/OneDrive/Desktop/school_client/Lib/site-packages/PySide6=PySide6 --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py --include-data-dir=Helper=Helper --include-data-dir=utils=utils --include-data-dir=templates=templates --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile


 nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia,platforms --include-data-dir=C:/Users/fritz/OneDrive/Desktop/school_client/Lib/site-packages/PySide6=PySide6 --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py --include-data-dir=WeasyPrint=WeasyPrint --include-data-dir=Helper=Helper --include-data-dir=utils=utils --include-data-dir=templates=templates --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile


 nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia,platforms --include-data-dir=C:/Users/fritz/OneDrive/Desktop/school_client/Lib/site-packages/PySide6=PySide6 --include-data-dir=C:/Users/fritz/OneDrive/Desktop/school_client/Lib/site-packages/jinja2=jinja2 --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py --include-data-dir=WeasyPrint=WeasyPrint --include-data-dir=Helper=Helper --include-data-dir=utils=utils --include-data-dir=templates=templates --output-dir=build --remove-output --nofollow-import-to=tkinter,test --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile
 

 --include-data-dir=C:/Users/fritz/OneDrive/Desktop/school_client/Lib/site-packages/PySide6=PySide6

###################################################################################
  nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia,platforms --include-package=jinja2 --include-package=jinja2.ext --include-module=jinja2.ext --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py  --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build  --remove-output --nofollow-import-to=tkinter,test,unittest,pydoc --noinclude-qt-translation --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile --lto=yes

  --include-data-dir=templates=templates --include-data-dir=WeasyPrint=WeasyPrint
  ###################################################################################
  nuitka app.py --standalone --enable-plugin=pyside6 --include-qt-plugins=multimedia,platforms --include-package=jinja2 --include-package=jinja2.ext --include-module=jinja2.ext --include-data-dir=Models=Models --include-data-dir=Views=Views --include-data-dir=Controllers=Controllers --include-data-dir=assets=assets --include-data-file=Config.py=Config.py  --include-data-dir=Helper=Helper --include-data-dir=utils=utils --output-dir=build  --remove-output --nofollow-import-to=tkinter,test,unittest,pydoc --noinclude-qt-translation --windows-company-name="Infini-Sofware" --windows-product-name="School Client" --windows-product-version="1.0.0" --windows-file-version="1.0.0.0" --windows-file-description="Logiciel de gestion scolaire" --windows-icon-from-ico=C:\Users\fritz\Downloads\favicon.ico --onefile --lto=yes
  
  ====================================================================================================================================

  nuitka app.py ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyside6 ^
    --include-qt-plugins=multimedia,platforms ^
    --include-package=jinja2 ^
    --include-package=jinja2.ext ^
    --include-data-dir=Models=Models ^
    --include-data-dir=Views=Views ^
    --include-data-dir=Controllers=Controllers ^
    --include-data-dir=assets=assets ^
    --include-data-dir=WeasyPrint=WeasyPrint ^
    --include-data-dir=Helper=Helper ^
    --include-data-dir=utils=utils ^
    --include-data-dir=templates=templates ^
    --include-data-file=Config.py=Config.py ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libgobject-2.0-0.dll"=libgobject-2.0-0.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libpango-1.0-0.dll"=libpango-1.0-0.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libcairo-2.dll"=libcairo-2.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libgdk_pixbuf-2.0-0.dll"=libgdk_pixbuf-2.0-0.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libfontconfig-1.dll"=libfontconfig-1.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libfreetype-6.dll"=libfreetype-6.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libharfbuzz-0.dll"=libharfbuzz-0.dll ^
    --include-data-file="C:\Program Files\GTK3-Runtime Win64\bin\libfribidi-0.dll"=libfribidi-0.dll ^
    --remove-output ^
    --nofollow-import-to=tkinter,test,unittest,pydoc ^
    --noinclude-qt-translation ^
    --windows-company-name="Infini-Software" ^
    --windows-product-name="School Client" ^
    --windows-product-version="1.0.0" ^
    --windows-file-version="1.0.0.0" ^
    --windows-file-description="Logiciel de gestion scolaire" ^
    --windows-icon-from-ico="C:\Users\fritz\Downloads\favicon.ico" ^
    --lto=yes



  npm init -y
  npm install -D tailwindcss@^3.4.0 postcss autoprefixer
  npx tailwindcss init -p

  Créez le fichier input.css :

css
@tailwind base;
@tailwind components;
@tailwind utilities;


Configurez tailwind.config.js :
javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/*.html",
    "./**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

npx tailwindcss -i input.css -o templates/tailwind.css --watch

<link href="{{ url_for('static', filename='css/tailwind.css') }}" rel="stylesheet">

npx tailwindcss -i input.css -o templates/tailwind.css --minify

 




 