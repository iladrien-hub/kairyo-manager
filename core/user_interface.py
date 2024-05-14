import typing

from PyQt5 import QtWidgets, QtGui

from mainwindow.widgets.windows import FramelessWindow

if typing.TYPE_CHECKING:
    from mainwindow import MainWindow


class UserInterface:
    def __init__(self, window: 'MainWindow'):
        self._window = window
        self._settings: typing.Dict[str, typing.Type[QtWidgets.QWidget]] = {}

    def register_settings(self, name: str, widget_type: typing.Type[QtWidgets.QWidget]):
        if name in self._settings:
            raise ValueError(f'\"{name}\" already exists')
        self._settings[name] = widget_type

    def register_tab(self, name: str, widget: QtWidgets.QWidget, icon: QtGui.QIcon = None):
        tab_idx = self._window.tabs.addTab(widget, name)
        if icon:
            self._window.tabs.setTabIcon(tab_idx, icon)

    def add_menu(self, title: str):
        return self._window.titlebar().addMenu(title)

    def create_dialog(self, title: str, w: QtWidgets.QWidget):
        dialog = FramelessWindow(self._window)
        dialog.setWindowIcon(QtGui.QIcon(":/mainwindow/Icon512.ico"))
        dialog.addContentWidget(w)

        titlebar = dialog.titlebar()

        titlebar.setLabel(title)
        titlebar.hideMenu(True)
        titlebar.hideSizeControls(True)

        return dialog

    @property
    def window(self):
        return self._window

    @property
    def settings(self):
        return self._settings
