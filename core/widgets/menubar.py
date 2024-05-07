from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy


class MenuBar(QtWidgets.QMenuBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
