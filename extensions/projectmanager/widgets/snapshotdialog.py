from PyQt5 import QtWidgets

from core.widgets.layout import create_box_layout


class SnapshotDialog(QtWidgets.QFrame):

    def __init__(self):
        super().__init__()

        self._result = ""

        self._message = QtWidgets.QLineEdit()
        self._message.setPlaceholderText('Snapshot Message')

        self._save = QtWidgets.QPushButton('Save')
        self._save.setProperty('accent', True)

        self._cancel = QtWidgets.QPushButton('Cancel')

        buttons = create_box_layout([
            self._save,
            self._cancel
        ], proto=QtWidgets.QHBoxLayout, spacing=8)

        buttons.insertStretch(0)

        layout = create_box_layout([
            QtWidgets.QLabel('Enter snapshot message:'),
            self._message,
            buttons
        ], spacing=8, margins=(8, 8, 8, 8))
        layout.addStretch()

        self.setLayout(layout)
        self.updateButtons()

        self._message.textChanged.connect(self.updateButtons)
        self._save.clicked.connect(self.on_save_clicked)
        self._cancel.clicked.connect(self.on_cancel_clicked)

    def updateButtons(self):
        self._save.setEnabled(self._message.text().strip() != "")

    def message(self):
        return self._message.text().strip()

    def result(self):
        return self._result

    def on_save_clicked(self):
        self._result = self.message()
        self.window().close()

    def on_cancel_clicked(self):
        self._result = None
        self.window().close()
