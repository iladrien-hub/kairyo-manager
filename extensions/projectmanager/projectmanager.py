from core.extension import KairyoExtension
from core.styling.icon import load_icon
from extensions.projectmanager.widgets.projectamanagertab import ProjectManagerTab


class ProjectManagerExtension(KairyoExtension):

    def on_start(self):
        self.api.user_interface.register_tab("Management",
                                             ProjectManagerTab(),
                                             load_icon(':/projectmanager/list.svg', '#cacaca'))
