from multiprocessing import Event

class FlagPkg:
    def __init__(self, name: str):
        self.name = name
        self.loading = Event()
        self.sys_ready = Event()
        self.enable = Event()
        self.processing = Event()
        self.complete = Event()
        self.error = Event()

    def clear_all(self):
        # self.loading.clear()
        # self.sys_ready.clear()
        self.enable.clear()
        self.complete.clear()
        self.error.clear()