from PySide6.QtCore import QThread, Signal

class Worker(QThread):
    finished = Signal(str, object)
    error = Signal(str, str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.func_name = func.__name__

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(self.func_name, result)
        except Exception as e:
            self.error.emit(self.func_name, str(e))
