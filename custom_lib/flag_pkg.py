from multiprocessing import Event

class FlagPkg:
    def __init__(self, name: str):
        self.name = name
        self.loading = Event()
        self.loaded = Event()
        self.enable = Event()
        self.processing = Event()
        self.complete = Event()
        self.error = Event()