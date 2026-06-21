import os
import sys
def get_app_root():
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        root = os.path.dirname(os.path.realpath(sys.argv[0]))
        print(f"  root path {root}")
        return os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return os.path.abspath(".")