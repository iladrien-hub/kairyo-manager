from PyQt5 import QtWidgets

from core.settings import PHOTOSHOP_PATH, AUTOMATIC_PATH, AUTOMATIC_URL
from core.widgets.fileinput import FileInputMode
from core.widgets.forms import LabeledDivider
from core.widgets.settings import FileSetting, TextSetting


class PathSettingsWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._photoshopPath = FileSetting(PHOTOSHOP_PATH)
        self._photoshopPath.setMode(FileInputMode.Open)
        self._photoshopPath.setFilter("Executable (*.exe)")

        self._automaticPath = FileSetting(AUTOMATIC_PATH)
        self._automaticPath.setMode(FileInputMode.Directory)

        self._automaticUrl = TextSetting(AUTOMATIC_URL)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(LabeledDivider('Photoshop'))

        form = QtWidgets.QFormLayout()
        form.setContentsMargins(16, 0, 0, 0)
        form.setSpacing(16)

        form.addRow("Path to Photoshop executable: ", self._photoshopPath)

        layout.addLayout(form)
        layout.addWidget(LabeledDivider('Automatic1111', add_top_margin=True))

        form = QtWidgets.QFormLayout()
        form.setContentsMargins(16, 0, 0, 0)
        form.setSpacing(16)

        form.addRow("Automatic1111 root folder: ", self._automaticPath)
        form.addRow("Automatic1111 Url: ", self._automaticUrl)

        layout.addLayout(form)
        layout.addStretch()

        self.setLayout(layout)
