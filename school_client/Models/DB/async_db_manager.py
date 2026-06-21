# from PySide6.QtCore import QObject, QThread, Signal
# import inspect
# import asyncio
# import importlib
# import os
# import sys

# class Worker(QThread):
#     finished = Signal(str, object)
#     error = Signal(str, str)

#     _function_cache = {}

#     def __init__(self, func, *args, search_path=None, **kwargs):
#         super().__init__()
#         self.func = func
#         self.args = args
#         self.kwargs = kwargs
#         self.func_name = func if isinstance(func, str) else func.__name__
#         self.search_path = search_path
#         self._stopped = False  # Flag pour arrêter proprement si nécessaire

#     def run(self):
#         try:
#             if isinstance(self.func, str):
#                 func = self._get_cached_function(self.func)
#                 if not func:
#                     func = self.find_function(self.func)
#                 if not func:
#                     raise ValueError(f"⚠️ Fonction '{self.func}' introuvable.")
#             else:
#                 func = self.func

#             # Exécution de la fonction
#             if inspect.iscoroutinefunction(func):
#                 result = asyncio.run(func(*self.args, **self.kwargs))
#             else:
#                 result = func(*self.args, **self.kwargs)

#             if not self._stopped:
#                 self.finished.emit(self.func_name, result)

#         except Exception as e:
#             if not self._stopped:
#                 self.error.emit(self.func_name, str(e))

#     def stop(self):
#         self._stopped = True
#         if self.isRunning():
#             self.quit()
#             self.wait(2000)
#         self.deleteLater()

#     # Cache et recherche de fonction
#     def _get_cached_function(self, func_name):
#         return self._function_cache.get(func_name)

#     def _cache_function(self, func_name, func):
#         self._function_cache[func_name] = func

#     def find_function(self, func_name):
#         base_path = self.search_path or os.path.abspath(".")
#         if base_path not in sys.path:
#             sys.path.append(base_path)

#         for root, _, files in os.walk(base_path):
#             for file in files:
#                 if file.endswith(".py") and not file.startswith("__"):
#                     module_name = os.path.splitext(file)[0]
#                     rel_path = os.path.relpath(root, os.getcwd()).replace(os.sep, ".")
#                     full_module_name = f"{rel_path}.{module_name}" if rel_path != "." else module_name
#                     try:
#                         module = importlib.import_module(full_module_name)
#                         func = getattr(module, func_name, None)
#                         if func:
#                             self._cache_function(func_name, func)
#                             return func
#                     except Exception:
#                         continue
#         return None


# class AsyncDBManager(QObject):
#     started = Signal(str)
#     finished = Signal(str, object)
#     failed = Signal(str, str)

#     def __init__(self, loader_widget=None, search_path=None):
#         super().__init__()
#         self.loader_widget = loader_widget
#         self.threads = {}
#         self.search_path = search_path or os.path.abspath("Controllers")

#     def run(self, func, *args, **kwargs):
#         worker = Worker(func, *args, search_path=self.search_path, **kwargs)
#         func_name = worker.func_name
#         self.threads[func_name] = worker

#         # Connexions signaux UI
#         if self.loader_widget:
#             self.started.connect(lambda _: self.loader_widget.show())
#             self.finished.connect(lambda *_: self.loader_widget.hide())
#             self.failed.connect(lambda *_: self.loader_widget.hide())

#         worker.finished.connect(self.on_worker_finished)
#         worker.error.connect(self.failed)

#         # Démarrage
#         self.started.emit(func_name)
#         worker.start()

#     def on_worker_finished(self, func_name, result):
#         self.finished.emit(func_name, result)

#         # Arrêt propre du thread
#         worker = self.threads.pop(func_name, None)
#         if worker:
#             worker.stop()

#     def stop_all_threads(self):
#         """Arrête tous les threads en cours sans crash."""
#         for worker in list(self.threads.values()):
#             worker.stop()
#         self.threads.clear()

#     def __del__(self):
#         self.stop_all_threads()











import importlib
import os
import sys
import inspect
import asyncio
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

# --- Worker signals (comme avant)
class WorkerSignals(QObject):
    finished = Signal(str, object)
    error = Signal(str, str)

# --- Worker basé sur QRunnable (pas de QThread à gérer)
class DBRunnable(QRunnable):
    def __init__(self, func, *args, search_path=None, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.func_name = func if isinstance(func, str) else func.__name__
        self.search_path = search_path or os.path.abspath("Controllers")
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            # Recherche de la fonction à exécuter
            func = self.func
            if isinstance(func, str):
                func = self.find_function(func)
                if not func:
                    raise ValueError(f"⚠️ Fonction '{self.func}' introuvable.")
            
            # Exécution asynchrone/synchrone
            if inspect.iscoroutinefunction(func):
                result = asyncio.run(func(*self.args, **self.kwargs))
            else:
                result = func(*self.args, **self.kwargs)
            
            self.signals.finished.emit(self.func_name, result)

        except Exception as e:
            self.signals.error.emit(self.func_name, str(e))

    # Recherche dans Controllers
    def find_function(self, func_name):
        base_path = self.search_path
        if base_path not in sys.path:
            sys.path.append(base_path)

        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_name = os.path.splitext(file)[0]
                    rel_path = os.path.relpath(root, os.getcwd()).replace(os.sep, ".")
                    full_module_name = f"{rel_path}.{module_name}" if rel_path != "." else module_name
                    try:
                        module = importlib.import_module(full_module_name)
                        func = getattr(module, func_name, None)
                        if func:
                            return func
                    except Exception:
                        continue
        return None


# --- Gestionnaire principal (identique à ton AsyncDBManager actuel)
class AsyncDBManager(QObject):
    started = Signal(str)
    finished = Signal(str, object)
    failed = Signal(str, str)

    def __init__(self, loader_widget=None, search_path=None):
        super().__init__()
        self.loader_widget = loader_widget
        self.pool = QThreadPool.globalInstance()
        self.search_path = search_path or os.path.abspath("Controllers")

    def run(self, func, *args, **kwargs):
        worker = DBRunnable(func, *args, search_path=self.search_path, **kwargs)

        # Connexion signaux
        worker.signals.finished.connect(self.on_worker_finished)
        worker.signals.error.connect(self.failed)

        if self.loader_widget:
            self.started.connect(lambda _: self.loader_widget.show())
            self.finished.connect(lambda *_: self.loader_widget.hide())
            self.failed.connect(lambda *_: self.loader_widget.hide())

        # Démarrage
        self.started.emit(worker.func_name)
        self.pool.start(worker)

    def on_worker_finished(self, func_name, result):
        self.finished.emit(func_name, result)

    def stop_all_threads(self):
        """
        Pas vraiment utile avec QRunnable, mais tu peux l’appeler pour vider le pool.
        """
        self.pool.waitForDone(2000)


















# import importlib
# import os
# import sys
# import inspect
# import asyncio
# from PySide6.QtCore import QObject, QThread, Signal


# class Worker(QThread):
#     finished = Signal(str, object)
#     error = Signal(str, str)

#     _function_cache = {}

#     def __init__(self, func, *args, search_path=None, **kwargs):
#         super().__init__()
#         self.func = func
#         self.args = args
#         self.kwargs = kwargs
#         self.func_name = func if isinstance(func, str) else func.__name__
#         self.search_path = search_path

#     def run(self):
#         print(f" self.search_path    {self.search_path }")
#         try:
#             if isinstance(self.func, str):
#                 func = self._get_cached_function(self.func)
#                 if not func:
#                     func = self.find_function(self.func)
#                 if not func:
#                     raise ValueError(f"⚠️ Fonction '{self.func}' introuvable dans le projet.")
#             else:
#                 func = self.func

#             # 🔍 Si la fonction est asynchrone, on utilise asyncio.run
#             if inspect.iscoroutinefunction(func):
#                 result = asyncio.run(func(*self.args, **self.kwargs))
#             else:
#                 result = func(*self.args, **self.kwargs)

#             self.finished.emit(self.func_name, result)

#         except Exception as e:
#             self.error.emit(self.func_name, str(e))

#     def get_path(self, relative_path):
#         """ Récupère le chemin des fichiers inclus avec PyInstaller """
#         if getattr(sys, 'frozen', False):  # Si l'application est packagée
#             base_path = sys._MEIPASS
#         else:
#             base_path = os.path.abspath(".")  # Mode développement

#         return os.path.join(base_path, relative_path)

#     # ---------- FONCTIONS INTERNES ---------- #

#     def _get_cached_function(self, func_name):
#         return self._function_cache.get(func_name)

#     def _cache_function(self, func_name, func):
#         self._function_cache[func_name] = func

#     def find_function(self, func_name):
#         base_path = self.search_path or self.get_path(os.path.join("Controllers"))
#         if base_path not in sys.path:
#             sys.path.append(base_path)

#         for root, _, files in os.walk(base_path):
#             for file in files:
#                 if file.endswith(".py") and not file.startswith("__"):
#                     module_name = os.path.splitext(file)[0]
#                     rel_path = os.path.relpath(root, os.getcwd()).replace(os.sep, ".")
#                     full_module_name = f"{rel_path}.{module_name}" if rel_path != "." else module_name

#                     try:
#                         module = importlib.import_module(full_module_name)
#                         func = getattr(module, func_name, None)
#                         if func:
#                             self._cache_function(func_name, func)
#                             return func
#                     except Exception:
#                         continue
#         return None


# class AsyncDBManager(QObject):
    # started = Signal(str)
    # finished = Signal(str, object)
    # failed = Signal(str, str)

    # def __init__(self, loader_widget=None, search_path=None):
    #     super().__init__()
    #     self.loader_widget = loader_widget
    #     self.threads = {}
    #     self.search_path = search_path or self.get_path(os.path.join("Controllers"))

    # def stop_all_threads(self):
    #     for func_name, worker in list(self.threads.items()):
    #         if worker.isRunning():
    #             worker.quit()
    #             worker.wait(2000)  # max 2s
    #         worker.deleteLater()
    #     self.threads.clear()

    # def __del__(self):
    #     self.stop_all_threads()

    # def get_path(self, relative_path):
    #     """ Récupère le chemin des fichiers inclus avec PyInstaller """
    #     if getattr(sys, 'frozen', False):  # Si l'application est packagée
    #         base_path = sys._MEIPASS
    #     else:
    #         base_path = os.path.abspath(".")  # Mode développement

    #     return os.path.join(base_path, relative_path)

    # def run00(self, func, *args, **kwargs):
    #     worker = Worker(func, *args, search_path=self.search_path, **kwargs)
    #     func_name = worker.func_name
    #     self.threads[func_name] = worker

    #     if self.loader_widget:
    #         self.started.connect(lambda _: self.loader_widget.show())
    #         self.finished.connect(lambda *_: self.loader_widget.hide())
    #         self.failed.connect(lambda *_: self.loader_widget.hide())

    #     worker.finished.connect(self.on_worker_finished)
    #     worker.error.connect(self.failed)

    #     self.started.emit(func_name)
    #     worker.start() 

    # def run(self, func, *args, **kwargs):
    #     worker = Worker(func, *args, search_path=self.search_path, **kwargs)
    #     func_name = worker.func_name
    #     self.threads[func_name] = worker

    #     if self.loader_widget:
    #         self.started.connect(lambda _: self.loader_widget.show())
    #         self.finished.connect(lambda *_: self.loader_widget.hide())
    #         self.failed.connect(lambda *_: self.loader_widget.hide())

    #     # Connexions
    #     worker.finished.connect(self.on_worker_finished)
    #     worker.error.connect(self.failed)

    #     # 🧩 Ajouts essentiels : fermeture automatique du QThread
    #     worker.finished.connect(worker.quit)
    #     # worker.finished.connect(worker.wait)
    #     worker.finished.connect(worker.deleteLater)

    #     self.started.emit(func_name)
    #     worker.start()


    # def on_worker_finished(self, func_name, result):
    #     self.finished.emit(func_name, result)

    #     worker = self.threads.pop(func_name, None)
    #     if worker and worker.isRunning():
    #         print(f"🧵 Arrêt propre du thread {func_name}")
    #         worker.quit()
    #         # worker.wait(2000)  # attend max 2 secondes pour la fermeture