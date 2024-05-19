import os

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from core.extension import KairyoExtension
from core.project import Project
from core.styling.icon import load_icon
from .widgets.createproject import CreateProject
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
        wid = CreateProject()

        dialog = self.api.user_interface.create_dialog('Create Project', wid)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.show()
        dialog.exec_()

        result = wid.result()
        if not result:
            return

        os.makedirs(result.location, exist_ok=True)
        root, name = os.path.split(result.location)

        project = Project(result.location)
        project.meta.name = name
        project.meta.character = result.character
        project.meta.description = result.description
        project.meta.source = result.source
        project.meta.source_type = result.source_type
        project.meta.custom_source_type = result.custom_source_type
        project.meta.use_custom_source_type = result.use_custom_source_type
        project.meta.use_character_from_lora = result.use_character_from_lora

        self.api.open_project(result.location)

    def on_open_project(self):
        root = ""
        if last_project := self.api.settings.value('openProject/lastProject', None):
            root = os.path.split(last_project)[0]

        path = QtWidgets.QFileDialog.getExistingDirectory(self.api.user_interface.window, 'Select Folder', root)
        if path:
            self.api.open_project(path)

    def on_storage_imageChanged(self):
        self._main_tab.editor().setImage(self.api.storage.image)
