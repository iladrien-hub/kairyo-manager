import os

from PyQt5 import QtWidgets

from core.extension import KairyoExtension
from core.styling.icon import load_icon
from extensions.projectmanager.widgets.projectamanagertab import ProjectManagerTab


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
        print("asd")
