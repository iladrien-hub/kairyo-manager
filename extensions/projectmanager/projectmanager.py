from core.extension import KairyoExtension
from extensions.projectmanager.widgets.projectamanagertab import ProjectManagerTab


class ProjectManagerExtension(KairyoExtension):

    def on_start(self):
        self.api.user_interface.register_tab("Project", ProjectManagerTab())
