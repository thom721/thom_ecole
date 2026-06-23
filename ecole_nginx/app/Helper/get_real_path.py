import os
import sys
from pathlib import Path

def get_real_path1(relative_path): 
    # PyInstaller (onefile)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    elif '__compiled__' in globals():
        # Nuitka
        base_path = os.path.dirname(sys.executable)
    # Mode normal (Python)
    else:
        # Utiliser le dossier du fichier main.py plutôt que abspath(".") 
        # pour éviter les erreurs si on lance l'app depuis un autre dossier
     #    base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_real_path(relative_path): 

        # PyInstaller (onefile)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS

        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable)
            # print(f"base_path {base_path}    relative_path   {relative_path}")

        # Mode normal (Python)
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

def get_app_root():
    if "NUITKA_ONEFILE_PARENT" in os.environ or '__compiled__' in globals():
        return os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return os.path.abspath(".")


def is_compiled() -> bool:
    return (
        "NUITKA_ONEFILE_PARENT" in os.environ
        or '__compiled__' in globals()
        or getattr(sys, 'frozen', False)
    )











# import os
# import sys    
# def get_real_path(relative_path): 

#         # PyInstaller (onefile)
#         if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
#             base_path = sys._MEIPASS

#         elif '__compiled__' in globals():
#             # Nuitka
#             base_path = os.path.dirname(sys.executable)
#             print(f"base_path {base_path}    relative_path   {relative_path}")

#         # Mode normal (Python)
#         else:
#             base_path = os.path.abspath(".")

#         return os.path.join(base_path, relative_path)