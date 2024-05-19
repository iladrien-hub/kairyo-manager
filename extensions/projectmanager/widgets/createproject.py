import dataclasses
import os.path
from typing import Optional

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy

from core.api import KairyoApi
from core.styling.icon import load_icon
from core.widgets.fileinput import FileInput, FileInputMode
from core.widgets.forms import LabeledDivider
from core.widgets.layout import create_box_layout, create_grid_layout, layout_to_widget


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

        self._createButton = QtWidgets.QPushButton('Create')
        self._createButton.setProperty('accent', True)
        self._createButton.clicked.connect(self.on_createButton_clicked)

        self._sourceTypeRadio_default = QtWidgets.QRadioButton('Source Type:')
        self._sourceTypeRadio_default.setChecked(True)

        self._sourceTypeRadio_custom = QtWidgets.QRadioButton('Custom Source:')

        self._sourceTypeRadioGroup = QtWidgets.QButtonGroup()
        self._sourceTypeRadioGroup.addButton(self._sourceTypeRadio_default)
        self._sourceTypeRadioGroup.addButton(self._sourceTypeRadio_custom)
        self._sourceTypeRadioGroup.setExclusive(True)
        self._sourceTypeRadioGroup.buttonClicked.connect(self.updateFranchiseControls)

        self._sourceType = QtWidgets.QComboBox(self)
        self._sourceType.setItemDelegate(QtWidgets.QStyledItemDelegate(self))
        self._sourceType.addItems(['Anime', 'Game', 'Franchise'])
        self._sourceType.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self._sourceTypeCustom = QtWidgets.QLineEdit()
        self._sourceTypeCustom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        self._characterName = QtWidgets.QLineEdit()
        self._characterName.setPlaceholderText('E.g. Sakura Haruno')
        self._loadCharacterFromLora = QtWidgets.QCheckBox("Use character from LoRa")
        self._loadCharacterFromLora.stateChanged.connect(self.updateCharacterNameInput)
        self._loadCharacterFromLora.setVisible(False)

        self._characterNameLabel = QtWidgets.QLabel('Character Name:')

        self._sourceName = QtWidgets.QLineEdit()
        self._sourceName.setPlaceholderText("E.g. Naruto: Shippūden")

        self._description = QtWidgets.QTextEdit()
        self._description.setPlaceholderText('write something...')

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
                create_grid_layout([
                    [self._characterNameLabel],
                    [self._characterName, self._loadCharacterFromLora]
                ], spacing=6),
                create_grid_layout([
                    [self._sourceTypeRadio_default, self._sourceType],
                    [self._sourceTypeRadio_custom, self._sourceTypeCustom]
                ], spacing=10),
                create_box_layout([
                    QtWidgets.QLabel("Source Name:"),
                    self._sourceName
                ], proto=QtWidgets.QHBoxLayout, spacing=10),
                create_box_layout([
                    QtWidgets.QLabel("Description:"),
                    self._description
                ], spacing=6),
            ], spacing=12, margins=(16, 0, 0, 0))
        ], spacing=12, margins=(12, 12, 12, 12))

        layout.addStretch()
        layout.addWidget(self._errorWidget)

        footer = create_box_layout([self._createButton], proto=QtWidgets.QHBoxLayout)
        footer.insertStretch(0)

        layout.addItem(footer)

        self.setLayout(layout)
        self.setMinimumHeight(624)
        self.setMinimumWidth(680)

        self.updateFranchiseControls()
        self.updateCharacterNameInput()
        self.initLocation()
        self.checkForErrors()

    def updateFranchiseControls(self):
        self._sourceType.setEnabled(self._sourceTypeRadio_default.isChecked())
        self._sourceTypeCustom.setEnabled(self._sourceTypeRadio_custom.isChecked())

    def updateCharacterNameInput(self):
        self._characterName.setEnabled(not self._loadCharacterFromLora.isChecked())
        self._characterNameLabel.setEnabled(not self._loadCharacterFromLora.isChecked())

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
            character=self._characterName.text(),
            description=self._description.toPlainText(),
            source=self._sourceName.text(),
            source_type=self._sourceType.currentText(),
            custom_source_type=self._sourceTypeCustom.text(),
            use_custom_source_type=self._sourceTypeRadio_custom.isChecked(),
            use_character_from_lora=self._loadCharacterFromLora.isChecked()
        )
        self.window().close()
