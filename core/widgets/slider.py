import contextlib

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt


class FancySlider(QtWidgets.QFrame):
    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super(FancySlider, self).__init__(*args, **kwargs)

        self._label = QtWidgets.QLabel(self)
        self._lineEdit = QtWidgets.QLineEdit(self)
        self._slider = QtWidgets.QSlider()
        self._slider.setOrientation(Qt.Horizontal)

        self._decimals = 0
        self._decimalsMultiplier = 1

        layout1 = QtWidgets.QHBoxLayout()
        layout1.setSpacing(0)
        layout1.setContentsMargins(0, 0, 0, 0)

        layout1.addWidget(self._label)
        layout1.addStretch()
        layout1.addWidget(self._lineEdit)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout1)
        layout.addWidget(self._slider)

        self.setLayout(layout)
        self.setRange(0.5, 1, 2)

        self._slider.valueChanged.connect(self.on_slider_valueChanged)
        self._lineEdit.textEdited.connect(self.on_lineEdit_textEdited)

    def setRange(self, bottom: float, top: float, decimals: int):
        self._decimals = decimals
        self._decimalsMultiplier = 10 ** decimals

        self._lineEdit.setValidator(QtGui.QDoubleValidator(bottom, top, decimals))
        self._slider.setRange(int(bottom * self._decimalsMultiplier), int(top * self._decimalsMultiplier))

    def value(self):
        return self._slider.value() / self._decimalsMultiplier

    def setValue(self, v: float):
        self._slider.setValue(int(v * self._decimalsMultiplier))

    def setLabel(self, t: str):
        self._label.setText(t)

    def on_slider_valueChanged(self):
        if self._lineEdit.hasFocus():
            return
        value = self.value()
        self._lineEdit.setText(str(value))
        self.valueChanged.emit(value)

    def on_lineEdit_textEdited(self):
        value = self.__get_lineEdit_value()
        if value is None:
            return
        value = value * self._decimalsMultiplier
        if -2147483648 < value < 2147483647:
            self._slider.setValue(int(value))
        self.valueChanged.emit(self.value())

    def __get_lineEdit_value(self):
        with contextlib.suppress(ValueError):
            return float(self._lineEdit.text())
