import typing

from PyQt5 import QtWidgets, QtGui

if typing.TYPE_CHECKING:
    from mainwindow import MainWindow


class UserInterface:
    def __init__(self, window: 'MainWindow'):
        self._window = window

    def register_tab(self, name: str, widget: QtWidgets.QWidget, icon: QtGui.QIcon = None):
        tab_idx = self._window.tabs.addTab(widget, name)
        if icon:
            self._window.tabs.setTabIcon(tab_idx, icon)
