from .api import KairyoApi


class KairyoExtension:
    def __init__(self, api: KairyoApi):
        self.api = api

    def on_start(self):
        pass
