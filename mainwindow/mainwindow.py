from PyQt5 import QtWidgets

from .generated.mainwindow import Ui_MainWindow


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
