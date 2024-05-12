from core.extension import KairyoExtension
from core.styling.icon import load_icon

from .tasks.upscale import UpscaleProjectTask


class UpscalerExtension(KairyoExtension):

    def on_setup_ui(self):
        menu = self.api.user_interface.add_menu("Run")

        action = menu.addAction('Run Upscaler')
        action.setIcon(load_icon(':/upscaler/sparkles.svg', fill="#51f66f"))
        action.triggered.connect(self.on_upscale_triggered)

    def on_upscale_triggered(self):
        project = self.api.storage.project
        if project:
            self.api.worker.add_task(UpscaleProjectTask(project))
