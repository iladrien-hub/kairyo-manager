from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy


class LabeledDivider(QtWidgets.QFrame):

    def __init__(self, label, *args, add_top_margin: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        self._label = QtWidgets.QLabel(self)
        self._label.setText(label)

        self._line = QtWidgets.QFrame()
        self._line.setFrameShape(QtWidgets.QFrame.HLine)
        self._line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, int(add_top_margin) * 16, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(self._label)
        layout.addWidget(self._line)

        self.setLayout(layout)
