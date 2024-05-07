from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize

from core.styling.icon import load_icon


class TitleBarButton(QtWidgets.QPushButton):

    def __init__(self):
        super().__init__()

        self.setFixedHeight(28)
        self.setFixedWidth(48)
        self.setIconSize(QSize(12, 12))


class TitleBarButtons(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._closeButton = TitleBarButton()
        self._closeButton.setObjectName('titleBarClose')
        self._resizeButton = TitleBarButton()
        self._resizeButton.setObjectName('titleBarResize')
        self._minimizeButton = TitleBarButton()
        self._minimizeButton.setObjectName('titleBarMinimize')

        self._closeIcon = load_icon(':/mainwindow/xmark.svg', '#b1b1b1')
        self._minimizeIcon = load_icon(':/mainwindow/window-minimize.svg', '#b1b1b1')
        self._maximizeIcon = load_icon(':/mainwindow/window-maximize.svg', '#b1b1b1')
        self._restoreIcon = load_icon(':/mainwindow/window-restore.svg', '#b1b1b1')

        self._layout = QtWidgets.QHBoxLayout()

        self.setupUi()

    def setupUi(self):
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._minimizeButton.setIcon(self._minimizeIcon)
        self._closeButton.setIcon(self._closeIcon)

        self._layout.addWidget(self._minimizeButton)
        self._layout.addWidget(self._resizeButton)
        self._layout.addWidget(self._closeButton)
        self.setLayout(self._layout)

        self._closeButton.clicked.connect(self.on_closeButton_clicked)
        self._resizeButton.clicked.connect(self.on_resizeButton_clicked)
        self._minimizeButton.clicked.connect(self.on_minimizeButton_clicked)

        self.updateMaximized()

    def updateMaximized(self):
        maximized = self.window().isMaximized()
        if maximized:
            self._resizeButton.setIcon(self._restoreIcon)
        else:
            self._resizeButton.setIcon(self._maximizeIcon)

    def on_closeButton_clicked(self):
        self.window().close()

    def on_resizeButton_clicked(self):
        maximized = self.window().isMaximized()
        if maximized:
            self.window().showNormal()
        else:
            self.window().showMaximized()
        self.updateMaximized()

    def on_minimizeButton_clicked(self):
        self.window().showMinimized()
        self.updateMaximized()
