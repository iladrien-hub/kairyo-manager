from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from core.api import KairyoApi
from core.project import Project
from core.widgets.layout import create_box_layout, create_grid_layout, layout_to_widget
from .projectinfofrom import ProjectInfoFrom


class InfoWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._nameLabel = QtWidgets.QLabel()
        self._nameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self._timeCreatedLabel = QtWidgets.QLabel()

        self._form = ProjectInfoFrom()

        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(layout_to_widget(create_box_layout([
            create_grid_layout([
                [QtWidgets.QLabel('Name:'), self._nameLabel],
                [QtWidgets.QLabel('Created:'), self._timeCreatedLabel],
            ], spacing=12),
            self._form
        ], margins=(8, 8, 8, 8), spacing=12)))

        self.setLayout(create_box_layout([self._scroll]))

    def clear(self):
        self._nameLabel.clear()
        self._timeCreatedLabel.clear()

        self._form.setCharacter("")
        self._form.setDescription("")
        self._form.setSource("")
        self._form.setSourceType("Anime")
        self._form.setCustomSourceType("")
        self._form.setUseCustomSourceType(False)
        self._form.setUseCharacterFromLora(False)

    def fill(self, project: Project):
        if project is None:
            self.clear()

        date_fmt = "%A, %d %b %Y %I:%M %p"

        self._nameLabel.setText(f"<b>{project.meta.name}</b>")
        self._timeCreatedLabel.setText(f"<b>{datetime.fromtimestamp(project.meta.time_created).strftime(date_fmt)}</b>")

        self._form.setCharacter(project.meta.character)
        self._form.setDescription(project.meta.description)
        self._form.setSource(project.meta.source)
        self._form.setSourceType(project.meta.source_type)
        self._form.setCustomSourceType(project.meta.custom_source_type)
        self._form.setUseCustomSourceType(project.meta.use_custom_source_type)
        self._form.setUseCharacterFromLora(project.meta.use_character_from_lora)

    def sync(self):
        self.fill(KairyoApi.instance().storage.project)
