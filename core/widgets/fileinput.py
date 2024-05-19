from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtWidgets import QFileDialog

from core.keyboardmanager import KeyboardManager
from core.styling.icon import load_icon


class FileInputMode:
    Open = 1
    Save = 2
    Directory = 3


class FileInput(QtWidgets.QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__iconColor = "#000000"
        self.__icon = load_icon(':/mainwindow/folder-open.svg', fill=self.__iconColor)

        self._mode = FileInputMode.Open
        self._filter = ""
        self._root = ""

        self._action = self.addAction(self.__icon, QtWidgets.QLineEdit.TrailingPosition)
        self._action.triggered.connect(self.on_action_triggered)
        self._action.setToolTip('Browse... (Shift+Enter)')

        KeyboardManager.instance().ShiftEnter_Signal.connect(self._action.trigger)

    def setRoot(self, r: str):
        self._root = r

    def setMode(self, m: FileInputMode):
        self._mode = m

    def setFilter(self, f: str):
        self._filter = f

    def openFileNameDialog(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select File", self._root, self._filter)
        return fn

    def saveFileNameDialog(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save", self._root, self._filter)
        return fn

    def directoryNameDialog(self):
        fn = QFileDialog.getExistingDirectory(self, "Select Directory", self._root)
        return fn

    def on_action_triggered(self):
        if not self.hasFocus():
            return

        match self._mode:
            case FileInputMode.Open:
                path = self.openFileNameDialog()
            case FileInputMode.Save:
                path = self.saveFileNameDialog()
            case FileInputMode.Directory:
                path = self.directoryNameDialog()
            case _:
                return

        if path:
            self.setText(path)

    @pyqtProperty(str)
    def iconColor(self):
        return self.__iconColor

    @iconColor.setter
    def iconColor(self, val):
        self.__iconColor = val
        self.__icon = load_icon(':/mainwindow/folder-open.svg', fill=self.__iconColor)
        self._action.setIcon(self.__icon)
