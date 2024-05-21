from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy

from core.widgets.layout import create_box_layout, create_grid_layout


class ProjectInfoFrom(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.setLayout(create_box_layout([
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
        ], spacing=12, margins=(0, 0, 0, 0)))

        self.updateFranchiseControls()
        self.updateCharacterNameInput()

    def updateFranchiseControls(self):
        self._sourceType.setEnabled(self._sourceTypeRadio_default.isChecked())
        self._sourceTypeCustom.setEnabled(self._sourceTypeRadio_custom.isChecked())

    def updateCharacterNameInput(self):
        self._characterName.setEnabled(not self._loadCharacterFromLora.isChecked())
        self._characterNameLabel.setEnabled(not self._loadCharacterFromLora.isChecked())

    def character(self):
        return self._characterName.text()

    def description(self):
        return self._description.toPlainText()

    def source(self):
        return self._sourceName.text()

    def sourceType(self):
        return self._sourceType.currentText()

    def customSourceType(self):
        return self._sourceTypeCustom.text()

    def useCustomSourceType(self):
        return self._sourceTypeRadio_custom.isChecked()

    def useCharacterFromLora(self):
        return self._loadCharacterFromLora.isChecked()

    def setCharacter(self, character_name):
        self._characterName.setText(character_name)

    def setDescription(self, description_text):
        self._description.setPlainText(description_text)

    def setSource(self, source_name):
        self._sourceName.setText(source_name)

    def setSourceType(self, source_type):
        index = self._sourceType.findText(source_type)
        if index != -1:
            self._sourceType.setCurrentIndex(index)

    def setCustomSourceType(self, custom_source_type):
        self._sourceTypeCustom.setText(custom_source_type)

    def setUseCustomSourceType(self, use_custom):
        self._sourceTypeRadio_custom.setChecked(use_custom)
        self._sourceTypeRadio_default.setChecked(not use_custom)
        self.updateFranchiseControls()

    def setUseCharacterFromLora(self, use_lora):
        self._loadCharacterFromLora.setChecked(use_lora)
        self.updateCharacterNameInput()
