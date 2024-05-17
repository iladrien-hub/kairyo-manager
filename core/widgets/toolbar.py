from typing import Optional, Any

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty

from core.styling.icon import load_icon


class ToolbarButtonEventFiler(QtCore.QObject):

    def eventFilter(self, a0: Optional[QtCore.QObject], a1: Optional[QtCore.QEvent]) -> bool:
        print(a0, a1)

        return super().eventFilter(a0, a1)


class ToolbarButton(QtWidgets.QToolButton):
    def __init__(self, icon: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__icon_path = icon
        self.__iconColor = '#000000'
        self.__icon = load_icon(self.__icon_path, fill=self.__iconColor)

        self.__iconDisabledColor = '#000000'
        self.__disabledIcon = load_icon(self.__icon_path, fill=self.__iconDisabledColor)

        self.__data = None

        self.setIcon(self.__icon)

    @pyqtProperty(str)
    def iconColor(self):
        return self.__iconColor

    @iconColor.setter
    def iconColor(self, val):
        self.__iconColor = val
        self.__icon = load_icon(self.__icon_path, fill=self.__iconColor)
        if self.isEnabled():
            self.setIcon(self.__icon)

    @pyqtProperty(str)
    def iconDisabledColor(self):
        return self.__iconColor

    @iconDisabledColor.setter
    def iconDisabledColor(self, val):
        self.__iconDisabledColor = val
        self.__disabledIcon = load_icon(self.__icon_path, fill=self.__iconDisabledColor)
        if not self.isEnabled():
            self.setIcon(self.__disabledIcon)

    def changeEvent(self, a0: Optional[QtCore.QEvent]) -> None:
        self.setIcon(self.__icon if self.isEnabled() else self.__disabledIcon)

    def setData(self, data: Any):
        self.__data = data

    def data(self):
        return self.__data


class ToolBarSeparator(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)


class ToolBar(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addStretch()

        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setSpacing(3)

        self.setLayout(self._layout)
        self.setFixedHeight(27)

    def addButton(self, icon: str, tooltip: str = None):
        button = ToolbarButton(icon)
        # button.installEventFilter(ToolbarButtonEventFiler())

        # button.setIcon(icon)
        button.setIconSize(QtCore.QSize(16, 16))
        button.setFixedSize(21, 21)

        if tooltip:
            button.setToolTip(tooltip)

        self._layout.addWidget(button)

        return button

    def addSeparator(self):
        self._layout.addWidget(ToolBarSeparator())
