from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QLabel

from core.extension import KairyoExtension
from core.styling.icon import load_icon
from .widgets.projectamanagertab import ProjectManagerTab


class ProjectManagerExtension(KairyoExtension):

    def __init__(self, api):
        super().__init__(api)

        self._main_tab = ProjectManagerTab(api.user_interface.window, self.api.settings)

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

        open_project = menu.addAction('Open...')
        open_project.triggered.connect(self.on_open_project)
        open_project.setIcon(load_icon(':projectmanager/folder-open.svg', self.api.theme.text_200))

        self.api.storage.imageChanged.connect(self.on_storage_imageChanged)

    def on_create_project(self):
        dialog = self.api.user_interface.create_dialog('Create Project', QLabel('u sure?'))
        dialog.show()

    def on_open_project(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self.api.user_interface.window, 'Select Folder')
        if path:
            self.api.open_project(path)

    def on_storage_imageChanged(self):
        self._main_tab.editor().setImage(self.api.storage.image)
