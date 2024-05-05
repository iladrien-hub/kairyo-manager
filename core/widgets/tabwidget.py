from functools import partial
from typing import List

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QSizePolicy

from core.styling import make_stylesheet, Style
from .orientedbutton import OrientedButton


class TabWidget(QtWidgets.QWidget):
    _STYLE_TAB = make_stylesheet([
        Style("QPushButton", {
            'color': '#cacaca',
            'background-color': '#2e2e2e',
            'border': 'none',
            'border-radius': '0',
            'padding': '4px 10px',
        }),
        Style("QPushButton:checked", {
            'background-color': '#272727',
            'border': 'none',
        }),
        Style("QPushButton:hover", {
            'background-color': '#272727',
            'border': 'none',
        }),
    ])

    _TAB_POSITION_PARAMS = {
        QtWidgets.QTabWidget.TabPosition.North: (
            QtWidgets.QBoxLayout.Direction.Down,
            QtWidgets.QBoxLayout.Direction.LeftToRight,
            OrientedButton.Orientation.Normal
        ),
        QtWidgets.QTabWidget.TabPosition.South: (
            QtWidgets.QBoxLayout.Direction.Up,
            QtWidgets.QBoxLayout.Direction.LeftToRight,
            OrientedButton.Orientation.Normal
        ),
        QtWidgets.QTabWidget.TabPosition.West: (
            QtWidgets.QBoxLayout.Direction.LeftToRight,
            QtWidgets.QBoxLayout.Direction.Down,
            OrientedButton.Orientation.West
        ),
        QtWidgets.QTabWidget.TabPosition.East: (
            QtWidgets.QBoxLayout.Direction.RightToLeft,
            QtWidgets.QBoxLayout.Direction.Down,
            OrientedButton.Orientation.East
        ),
    }

    _SPACER_ORIENTATION = {
        QtWidgets.QTabWidget.TabPosition.North: (
            QSizePolicy.Expanding, QSizePolicy.Minimum
        ),
        QtWidgets.QTabWidget.TabPosition.South: (
            QSizePolicy.Expanding, QSizePolicy.Minimum
        ),
        QtWidgets.QTabWidget.TabPosition.East: (
            QSizePolicy.Minimum, QSizePolicy.Expanding
        ),
        QtWidgets.QTabWidget.TabPosition.West: (
            QSizePolicy.Minimum, QSizePolicy.Expanding
        ),
    }

    def __init__(self):
        super().__init__()

        self._tabs: List[OrientedButton] = []
        self._tabs_rotation: OrientedButton.Orientation = OrientedButton.Orientation.Normal

        self._always_open: bool = False
        self._stack_widget = QtWidgets.QStackedWidget()

        self._tabs_layout = QtWidgets.QHBoxLayout()
        self._layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.Up)

        self.setTabPosition(QtWidgets.QTabWidget.North)
        self.setupUi()

    # noinspection PyPep8Naming
    def setupUi(self):
        self._stack_widget.setVisible(False)

        self._tabs_layout.setContentsMargins(0, 0, 0, 0)
        self._tabs_layout.setSpacing(0)

        spacer = QtWidgets.QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._tabs_layout.addItem(spacer)

        self._layout.addLayout(self._tabs_layout)
        self._layout.addWidget(self._stack_widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.setLayout(self._layout)

    # noinspection PyPep8Naming
    def addTab(self, w: QtWidgets.QWidget, name: str):
        # button = QtWidgets.QPushButton(name)
        button = OrientedButton(name, self, orientation=self._tabs_rotation)
        button.setText(name)
        button.setCheckable(True)
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button.setStyleSheet(self._STYLE_TAB)

        self._tabs_layout.insertWidget(self._tabs_layout.count() - 1, button)
        self._tabs.append(button)

        self._stack_widget.addWidget(w)

        button.clicked.connect(partial(self.onTabClicked, button))  # noqa
        self.updateState()

        return self._tabs.index(button)

    # noinspection PyPep8Naming
    def updateState(self):
        checked = next(filter(lambda x: x.isChecked(), self._tabs), None)
        if checked is None:
            if self._always_open and self._tabs:
                checked = self._tabs[0]
                checked.setChecked(True)
            else:
                self._stack_widget.setVisible(False)
                return

        self._stack_widget.setVisible(True)
        index = self._tabs.index(checked)
        self._stack_widget.setCurrentIndex(index)
        self._stack_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # noinspection PyPep8Naming
    def onTabClicked(self, b: QtWidgets.QPushButton):
        try:
            if self._always_open and not b.isChecked():
                b.setChecked(True)
                return

            for btn in self._tabs:
                if btn is not b:
                    btn.setChecked(False)

            self.updateState()
        except BaseException as e:
            print(e)

    # noinspection PyPep8Naming
    def setTabPosition(self, a0: QtWidgets.QTabWidget.TabPosition):
        layout_direction, tab_direction, self._tabs_rotation = self._TAB_POSITION_PARAMS[a0]

        for i in range(self._tabs_layout.count()):
            item = self._tabs_layout.itemAt(i)
            if isinstance(item, QtWidgets.QSpacerItem):
                self._tabs_layout.removeItem(item)
                spacer = QtWidgets.QSpacerItem(1, 1, *self._SPACER_ORIENTATION[a0])
                self._tabs_layout.insertItem(i, spacer)

        self._layout.setDirection(layout_direction)
        self._tabs_layout.setDirection(tab_direction)
        for b in self._tabs:
            b.setOrientation(self._tabs_rotation)

    # noinspection PyPep8Naming
    def setAlwaysOpen(self, b: bool):
        self._always_open = b
        if self._always_open:
            self.updateState()

    # noinspection PyPep8Naming
    def setTabIcon(self, index: int, icon: QtGui.QIcon):
        btn = self._tabs[index]
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(12, 12))
