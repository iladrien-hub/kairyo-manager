from PyQt5.QtWidgets import QLabel

from core.extension import KairyoExtension
from core.styling.icon import load_icon
from extensions.projectmanager.widgets.projectamanagertab import ProjectManagerTab
from mainwindow.widgets.windows import FramelessWindow


class ProjectManagerExtension(KairyoExtension):

    def __init__(self, api):
        super().__init__(api)

        self._main_tab = ProjectManagerTab(self.api.settings)

    def on_setup_ui(self):
        # Registering new tab
        self.api.user_interface.register_tab(
            "Management",
            self._main_tab,
            load_icon(':/projectmanager/list.svg', '#cacaca')
        )

        # Registering File menu
        menu = self.api.user_interface.add_menu('File')
        new_project = menu.addAction('New Project...')
        new_project.triggered.connect(self.on_create_project)

    def on_create_project(self):
        dialog = self.api.user_interface.create_dialog('Create Project', QLabel('u sure?'))

        dialog.show()

        # dialog = FramelessWindow(self.api.user_interface._window)
        #
        # dialog.addContentWidget(QLabel('Hello World!'))
        # dialog.show()
