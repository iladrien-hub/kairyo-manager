from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QSizePolicy

from core.styling import make_stylesheet, Style
from .buttons import TitleBarButtons


class TitleBar(QtWidgets.QFrame):
    _STYLE = make_stylesheet([Style('QFrame', {
        'border-bottom': '1px solid #515151'
    })])

    def __init__(self, parent):
        super().__init__(parent)

        self._buttons = TitleBarButtons()
        self._layout = QtWidgets.QHBoxLayout()

        self.setupUi()

    def setupUi(self):
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.insertStretch(50)
        self._layout.addWidget(self._buttons)

        self.setLayout(self._layout)
        self.setFixedHeight(28)

        self.setStyleSheet(self._STYLE)

    def mouseOverTitlebar(self, x, y):
        if self.childAt(QPoint(x, y)):
            return False
        else:
            return QRect(0, 0,
                         self.width(),
                         self.height()).contains(QPoint(x, y))
            # return QRect(self.appLogoLabel.width(), 0,
            #              self.width() - self.appLogoLabel.width(),
            #              self.height()).contains(QPoint(x, y))
