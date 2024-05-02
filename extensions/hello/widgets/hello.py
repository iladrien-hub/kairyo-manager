from ..generated.hello import Ui_Hello
from PyQt5 import QtWidgets


class Hello(Ui_Hello, QtWidgets.QWidget):

    def __init__(self):
        super(Hello, self).__init__()
        self.setupUi(self)
