from PyQt5 import QtWidgets

from .generated.mainwindow import Ui_MainWindow
from core.styling import make_stylesheet, Style


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    _STYLE = make_stylesheet([
        Style('*', {
            'background-color': '#2e2e2e'
        })
    ])

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setStyleSheet(self._STYLE)
