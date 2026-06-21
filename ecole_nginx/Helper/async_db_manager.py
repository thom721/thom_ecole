import importlib
import os
import sys
import inspect
import asyncio
from PySide6.QtCore import QObject, QThread, Signal


class Worker(QThread):
    finished = Signal(str, object)
    error = Signal(str, str)

    _function_cache = {}

    def __init__(self, func, *args, search_path=None, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.func_name = func if isinstance(func, str) else func.__name__
        self.search_path = search_path

    def run(self):
        try:
            if isinstance(self.func, str):
                func = self._get_cached_function(self.func)
                if not func:
                    func = self.find_function(self.func)
                if not func:
                    raise ValueError(f"⚠️ Fonction '{self.func}' introuvable dans le projet.")
            else:
                func = self.func

            # 🔍 Si la fonction est asynchrone, on utilise asyncio.run
            if inspect.iscoroutinefunction(func):
                result = asyncio.run(func(*self.args, **self.kwargs))
            else:
                result = func(*self.args, **self.kwargs)

            self.finished.emit(self.func_name, result)

        except Exception as e:
            self.error.emit(self.func_name, str(e))

    # ---------- FONCTIONS INTERNES ---------- #

    def _get_cached_function(self, func_name):
        return self._function_cache.get(func_name)

    def _cache_function(self, func_name, func):
        self._function_cache[func_name] = func

    def find_function(self, func_name):
        base_path = self.search_path or os.path.join(os.getcwd(), "Controllers")
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
                            self._cache_function(func_name, func)
                            return func
                    except Exception:
                        continue
        return None


class AsyncDBManager(QObject):
    started = Signal(str)
    finished = Signal(str, object)
    failed = Signal(str, str)

    def __init__(self, loader_widget=None, search_path=None):
        super().__init__()
        self.loader_widget = loader_widget
        self.threads = {}
        self.search_path = search_path or os.path.join(os.getcwd(), "Controllers")

    def run(self, func, *args, **kwargs):
        worker = Worker(func, *args, search_path=self.search_path, **kwargs)
        func_name = worker.func_name
        self.threads[func_name] = worker

        if self.loader_widget:
            self.started.connect(lambda _: self.loader_widget.show())
            self.finished.connect(lambda *_: self.loader_widget.hide())
            self.failed.connect(lambda *_: self.loader_widget.hide())

        worker.finished.connect(self.on_worker_finished)
        worker.error.connect(self.failed)

        self.started.emit(func_name)
        worker.start()

    def on_worker_finished(self, func_name, result):
        self.finished.emit(func_name, result)
        self.threads.pop(func_name, None)