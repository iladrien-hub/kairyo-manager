from core.extension import KairyoExtension
from core.styling.icon import load_icon
from .widgets.queuetabwidget import QueueTabWidget


class ProgressExtension(KairyoExtension):
    def __init__(self, api):
        super().__init__(api)

        self._queue_tab = QueueTabWidget()

    def on_setup_ui(self):
        self.api.user_interface.register_tab(
            "Queue",
            self._queue_tab,
            load_icon(':/progress/clock.svg', self.api.theme.text_200)
        )
