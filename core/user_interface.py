import dataclasses
import typing

from PyQt5 import QtWidgets, QtGui

from mainwindow.widgets.windows import FramelessWindow

if typing.TYPE_CHECKING:
    from mainwindow import MainWindow


@dataclasses.dataclass
class SettingsNode:
    title: str
    constructor: typing.Type[QtWidgets.QWidget] = None
    children: typing.List['SettingsNode'] = dataclasses.field(default_factory=list)


class SettingsTree:

    def __init__(self):
        self._tree: typing.List[SettingsNode] = []

    def find_node_or_create(self, name: str, nodes: typing.List[SettingsNode]):
        ret = next(filter(lambda x: x.title == name, nodes), None)
        if ret is None:
            ret = SettingsNode(name)
            nodes.append(ret)
        return ret.children

    def add_node(self, path: typing.List[str], name: str, constructor: typing.Type[QtWidgets.QWidget]):
        target = self._tree
        for item in path:
            target = self.find_node_or_create(item, target)

        target.append(SettingsNode(name, constructor))

    @property
    def nodes(self) -> typing.List[SettingsNode]:
        return self._tree


class UserInterface:
    def __init__(self, window: 'MainWindow'):
        self._window = window
        self._settings: SettingsTree = SettingsTree()

    def register_settings(self, path: typing.List[str], name: str, constructor: typing.Type[QtWidgets.QWidget]):
        # if name in self._settings:
        #     raise ValueError(f'\"{name}\" already exists')
        # self._settings[name] = widget_type
        self._settings.add_node(path, name, constructor)

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
    def settings(self) -> typing.List[SettingsNode]:
        return self._settings.nodes
