from threading import Lock

class SharedState:
    def __init__(self):
        self.lock = Lock()
        self.name = None
        self.url = None
        self.len_source = None
        self.idx = None

    def update(self, name, idx, len_sources):
        with self.lock:
            self.name = name
            self.idx = idx
            self.len_source = len_sources

    def get_data(self):
        with self.lock:
            return {"name": self.name, "idx": self.idx, "len_sources": self.len_source}

shared_state = SharedState()