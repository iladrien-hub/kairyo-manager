from functools import partial

from PyQt5 import QtWidgets

from core.widgets.layout import create_box_layout


class Question(QtWidgets.QFrame):
    class Buttons:
        YES = 1 << 0
        NO = 1 << 1
        CANCEL = 1 << 2

    def __init__(self, text: str, buttons: int = Buttons.YES | Buttons.NO):
        super().__init__()

        self._result = self.Buttons.CANCEL
        self._buttons = []

        if buttons & self.Buttons.YES:
            btn = QtWidgets.QPushButton("Yes")
            btn.setProperty('accent', True)
            btn.clicked.connect(partial(self.on_button_clicked, self.Buttons.YES))
            self._buttons.append(btn)

        if buttons & self.Buttons.NO:
            btn = QtWidgets.QPushButton("No")
            btn.clicked.connect(partial(self.on_button_clicked, self.Buttons.NO))
            self._buttons.append(btn)

        if buttons & self.Buttons.CANCEL:
            btn = QtWidgets.QPushButton("Cancel")
            btn.clicked.connect(partial(self.on_button_clicked, self.Buttons.CANCEL))
            self._buttons.append(btn)

        buttons = create_box_layout(self._buttons, proto=QtWidgets.QHBoxLayout, spacing=8)
        buttons.insertStretch(0)
        self.setLayout(create_box_layout([
            QtWidgets.QLabel(text),
            buttons
        ], spacing=12, margins=(12, 12, 12, 12)))

    def on_button_clicked(self, btn: int):
        self._result = btn
        self.window().close()

    def result(self):
        return self._result
