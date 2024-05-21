import dataclasses
import os.path
from typing import Optional

from PyQt5 import QtWidgets

from core.api import KairyoApi
from core.styling.icon import load_icon
from core.widgets.fileinput import FileInput, FileInputMode
from core.widgets.forms import LabeledDivider
from core.widgets.layout import create_box_layout, layout_to_widget
from .projectinfofrom import ProjectInfoFrom


@dataclasses.dataclass
class CreateProjectResult:
    location: str

    character: str
    use_character_from_lora: bool

    use_custom_source_type: bool
    source_type: str
    custom_source_type: str
    source: str

    description: str


class CreateProject(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._result: Optional[CreateProjectResult] = None

        self._location = FileInput()
        self._location.setMode(FileInputMode.Directory)
        self._location.textChanged.connect(self.checkForErrors)

        self._info = ProjectInfoFrom()

        self._createButton = QtWidgets.QPushButton('Create')
        self._createButton.setProperty('accent', True)
        self._createButton.clicked.connect(self.on_createButton_clicked)

        self._errorLabel = QtWidgets.QLabel()
        self._errorIcon = QtWidgets.QLabel()
        self._errorIcon.setPixmap(load_icon(':/projectmanager/bolt-lightning.svg', '#eedb85').pixmap(12, 12))

        error_layout = create_box_layout([self._errorIcon, self._errorLabel, ], proto=QtWidgets.QHBoxLayout, spacing=4)
        error_layout.addStretch()
        self._errorWidget = layout_to_widget(error_layout)

        layout = create_box_layout([
            create_box_layout([
                QtWidgets.QLabel("Location:"),
                self._location
            ], proto=QtWidgets.QHBoxLayout, spacing=10),
            LabeledDivider('Details'),
            create_box_layout([
                self._info
            ], margins=(16, 0, 0, 0))
        ], spacing=12, margins=(12, 12, 12, 12))

        layout.addStretch()
        layout.addWidget(self._errorWidget)

        footer = create_box_layout([self._createButton], proto=QtWidgets.QHBoxLayout)
        footer.insertStretch(0)

        layout.addItem(footer)

        self.setLayout(layout)
        self.setMinimumHeight(624)
        self.setMinimumWidth(680)

        self.initLocation()
        self.checkForErrors()

    def initLocation(self):
        self._location.setFocus()

        root = KairyoApi.instance().settings.value("projectmanager/lastProjectRoot", None, str)
        if root:
            name = "kairyoProject"
            path = os.path.join(root, name)
            path_len = len(path)

            self._location.setRoot(root)
            self._location.setText(path)
            self._location.setSelection(path_len - len(name), path_len)

    def checkForErrors(self):
        error = ""
        location = self._location.text()

        if not location:
            error = "Project path is empty"
        elif os.path.isfile(location):
            error = "Project location is not directory"
        elif os.path.exists(location) and len(os.listdir(location)) > 0:
            error = "Project location is not empty"

        self._errorLabel.setText(error)
        self._errorWidget.setVisible(bool(error))
        self._createButton.setEnabled(not error)

    def result(self):
        return self._result

    def on_createButton_clicked(self):
        self._result = CreateProjectResult(
            location=self._location.text(),
            character=self._info.character(),
            description=self._info.description(),
            source=self._info.source(),
            source_type=self._info.sourceType(),
            custom_source_type=self._info.customSourceType(),
            use_custom_source_type=self._info.useCustomSourceType(),
            use_character_from_lora=self._info.useCharacterFromLora()
        )
        self.window().close()
