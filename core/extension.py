from .api import KairyoApi


class KairyoExtension:
    def __init__(self, api: KairyoApi):
        self.api = api

    def on_setup_ui(self):
        pass
