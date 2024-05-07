from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QSizePolicy

from core.widgets.menubar import MenuBar
from .buttons import TitleBarButtons


class TitleBar(QtWidgets.QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self._buttons = TitleBarButtons()
        self._layout = QtWidgets.QHBoxLayout()

        self._menuBar = MenuBar()
        self._label = QtWidgets.QLabel()
        self._label.setObjectName('appTitle')
        self.setLabel("aqua - 00013-3064614141.png")

        self._spacer = QtWidgets.QSpacerItem(24, 1, QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._appIconLabel = QtWidgets.QLabel()
        self._appIconLabel.setObjectName("appIcon")

        self.setupUi()

    def setupUi(self):
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._appIconLabel)
        self._layout.addWidget(self._menuBar)
        self._layout.addItem(self._spacer)
        self._layout.addWidget(self._label)

        self._layout.insertStretch(50)
        self._layout.addWidget(self._buttons)

        self.setLayout(self._layout)
        self.setFixedHeight(28)
        self.setObjectName("titlebar")

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

    def setLabel(self, text: str):
        self._label.setText(text)
        self.window().setWindowTitle(text)

    def setWindowIcon(self, icon: QtGui.QIcon):
        self._appIconLabel.setPixmap(icon.pixmap(18, 18))

    def addMenu(self, title: str):
        children = self._menuBar.children()
        for child in children:
            if not isinstance(child, QtWidgets.QMenu):
                continue

            if child.title() == title:
                return child

        return self._menuBar.addMenu(title)

    def setActive(self, b: bool):
        self._label.setEnabled(b)

    def updateButtons(self):
        self._buttons.updateMaximized()

    def hideMenu(self, b: bool):
        self._menuBar.setVisible(not b)
        self._spacer.changeSize(0, 24 if b else 0)

    def hideSizeControls(self, b: bool):
        self._buttons.setResizeButtonVisible(not b)
        self._buttons.setMinimizeButtonVisible(not b)
