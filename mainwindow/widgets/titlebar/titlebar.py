from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QPoint, QRect

from core.styling import make_stylesheet, Style
from core.widgets.menubar import MenuBar
from .buttons import TitleBarButtons


class TitleBar(QtWidgets.QFrame):
    _STYLE = make_stylesheet([Style('QFrame', {
        'border-bottom': '1px solid #515151'
    })])

    _ICON_STYLE = make_stylesheet([Style('QLabel', {
        'padding-left': '12px',
        'padding-right': '12px'
    })])

    _LABEL_STYLE = make_stylesheet([Style('QLabel', {
        'padding-left': '18px',
        'font-size': '11px',
        'color': '#7a7a7a'
    })])

    def __init__(self, parent):
        super().__init__(parent)

        self._buttons = TitleBarButtons()
        self._layout = QtWidgets.QHBoxLayout()

        self._menuBar = MenuBar()
        self._label = QtWidgets.QLabel("aqua - 00013-3064614141.png")

        self._appIcon = QtGui.QIcon(":/mainwindow/Icon512.ico").pixmap(18, 18)
        self._appIconLabel = QtWidgets.QLabel()
        self._appIconLabel.setPixmap(self._appIcon)
        self._appIconLabel.setStyleSheet(self._ICON_STYLE)

        self.setupUi()

    def setupUi(self):
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._appIconLabel)

        menu = QtWidgets.QMenu(self._menuBar)
        menu.setTitle("File")
        self._menuBar.addMenu(menu)

        self._label.setStyleSheet(self._LABEL_STYLE)

        self._layout.addWidget(self._menuBar)
        self._layout.addWidget(self._label)

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
