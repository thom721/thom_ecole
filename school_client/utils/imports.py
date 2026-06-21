# 🛠 Importations générales
import sys
import os
import re
import json
import base64
import webbrowser
import tempfile
# import win32api
# import win32print
import ipaddress
import subprocess
from functools import partial
from io import BytesIO
import requests
import getpass
 
from datetime import datetime, timedelta
# from jinja2 import Environment, FileSystemLoader

import os
import traceback
from pathlib import Path
# 🛠 PySide6 : Base
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


def get_user_data_dir() -> str:
    """Équivalent cross-platform de %APPDATA% (Windows) pour les données utilisateur
    de l'application (icônes, templates...). Comportement Windows inchangé ;
    Mac/Linux utilisent l'emplacement idiomatique de la plateforme au lieu de
    planter sur un os.environ["APPDATA"] absent."""
    if sys.platform == "win32":
        return os.environ.get("APPDATA", os.path.join(str(Path.home()), "AppData", "Roaming"))
    elif sys.platform == "darwin":
        return os.path.join(str(Path.home()), "Library", "Application Support")
    return os.path.join(str(Path.home()), ".config")


def get_local_data_dir() -> str:
    """Équivalent cross-platform de %LOCALAPPDATA% (Windows) pour les données
    semi-permanentes (certificats...). Comportement Windows inchangé."""
    if sys.platform == "win32":
        return os.environ.get("LOCALAPPDATA", os.path.join(str(Path.home()), "AppData", "Local"))
    elif sys.platform == "darwin":
        return os.path.join(str(Path.home()), "Library", "Application Support")
    return os.path.join(str(Path.home()), ".local", "share")
