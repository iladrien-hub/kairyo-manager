from core.extension import KairyoExtension
from extensions.hello.widgets.hello import Hello


class HelloExtension(KairyoExtension):
    """Simple Hello World! extension"""

    def on_start(self):
        self.api.user_interface.register_tab("hello", Hello())
