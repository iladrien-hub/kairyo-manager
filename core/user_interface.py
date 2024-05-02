import typing

if typing.TYPE_CHECKING:
    from mainwindow import MainWindow


class UserInterface:
    def __init__(self, window: 'MainWindow'):
        self._window = window

    def register_tab(self, name, widget):
        self._window.tabs.addTab(widget, name)
