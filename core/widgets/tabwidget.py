from functools import partial
from typing import List, Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QSizePolicy

from .orientedbutton import OrientedButton


class TabButton(OrientedButton):
    pass


class TabWidget(QtWidgets.QWidget):
    currentTabChanged = QtCore.pyqtSignal(int)

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

    _TABS_WIDGET_STYLES = {
        QtWidgets.QTabWidget.TabPosition.North: 'tabPaneNorth',
        QtWidgets.QTabWidget.TabPosition.South: 'tabPaneSouth',
        QtWidgets.QTabWidget.TabPosition.East: 'tabPaneEast',
        QtWidgets.QTabWidget.TabPosition.West: 'tabPaneWest',
    }

    _TABS_WIDGET_CONTENT_MARGINS = {
        QtWidgets.QTabWidget.TabPosition.North: (0, 0, 0, 1),
        QtWidgets.QTabWidget.TabPosition.South: (0, 1, 0, 0),
        QtWidgets.QTabWidget.TabPosition.West: (0, 0, 1, 0),
        QtWidgets.QTabWidget.TabPosition.East: (1, 0, 0, 0),
    }

    def __init__(self):
        super().__init__()

        self._tabs: List[TabButton] = []
        self._tabsRotation: OrientedButton.Orientation = OrientedButton.Orientation.Normal
        self._currentTab: Optional[int] = None

        self._alwaysOpen: bool = False
        self._stackWidget = QtWidgets.QStackedWidget()

        self._tabsLayout = QtWidgets.QHBoxLayout()
        self._tabsWidget = QtWidgets.QWidget()
        self._layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.Up)

        self.setTabPosition(QtWidgets.QTabWidget.North)
        self.setupUi()

    def setupUi(self):
        # self._stackWidget.setVisible(False)

        self._tabsLayout.setContentsMargins(1, 1, 1, 1)
        self._tabsLayout.setSpacing(0)

        spacer = QtWidgets.QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._tabsLayout.addItem(spacer)

        self._tabsWidget.setLayout(self._tabsLayout)

        self._layout.addWidget(self._tabsWidget)
        self._layout.addWidget(self._stackWidget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self.setLayout(self._layout)

    def addTab(self, w: QtWidgets.QWidget, name: str):
        button = TabButton(name, self, orientation=self._tabsRotation)
        button.setText(name)
        button.setCheckable(True)
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        button.setObjectName("tabButton")
        button.setMinimumSize(21, 21)

        self._tabsLayout.insertWidget(self._tabsLayout.count() - 1, button)
        self._tabs.append(button)

        self._stackWidget.addWidget(w)

        button.clicked.connect(partial(self.onTabClicked, button))  # noqa
        if self._currentTab is None:
            self.setCurrentTab(self._tabs.index(button))

        return self._tabs.index(button)

    def currentTab(self):
        return self._currentTab if self._currentTab is not None else -1

    def setCurrentTab(self, new_tab: Optional[int]):
        # check if new tab is none and has alwaysOpen flag
        if new_tab is None:
            if self._alwaysOpen and self._tabs:
                new_tab = 0

        if self._currentTab != new_tab:
            # uncheck all tabs except for new one
            for idx, tab in enumerate(self._tabs):
                tab.setChecked(idx == new_tab)

            # check if new_tab still None
            if new_tab is None:
                self._stackWidget.setVisible(False)
                if self._tabsRotation == OrientedButton.Orientation.Normal:
                    self.setFixedHeight(22)
                    self.setMaximumWidth(2147483647)
                else:
                    self.setFixedWidth(22)
                    self.setMaximumHeight(2147483647)

            else:
                self._stackWidget.setVisible(True)
                self._stackWidget.setCurrentIndex(new_tab)
                self._stackWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                self.setMaximumSize(2147483647, 2147483647)
                self.setMinimumSize(50, 50)

            self._currentTab = new_tab
            self.currentTabChanged.emit(self.currentTab())

    def updateState(self):
        checked = next(filter(lambda x: x.isChecked(), self._tabs), None)

        # check if there is active tab
        if checked is None:
            # if there is always open flag - checks the first tab
            if self._alwaysOpen and self._tabs:
                checked = self._tabs[0]
                checked.setChecked(True)

            # else hides stack widget and returns
            else:
                self._stackWidget.setVisible(False)

                if self._tabsRotation == OrientedButton.Orientation.Normal:
                    self.setFixedHeight(22)
                    self.setMaximumWidth(2147483647)
                else:
                    self.setFixedWidth(22)
                    self.setMaximumHeight(2147483647)
                return

        self.setMaximumSize(2147483647, 2147483647)
        self.setMinimumSize(50, 50)

        self._stackWidget.setVisible(True)
        index = self._tabs.index(checked)
        self._stackWidget.setCurrentIndex(index)
        self._stackWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def onTabClicked(self, b: QtWidgets.QPushButton):
        try:
            if b.isChecked():
                idx = self._tabs.index(b)
                self.setCurrentTab(idx)
            else:
                if self._alwaysOpen:
                    b.setChecked(True)
                else:
                    self.setCurrentTab(None)
        except BaseException as e:
            print(e)

    def setTabPosition(self, a0: QtWidgets.QTabWidget.TabPosition):
        layout_direction, tab_direction, self._tabsRotation = self._TAB_POSITION_PARAMS[a0]

        for i in range(self._tabsLayout.count()):
            item = self._tabsLayout.itemAt(i)
            if isinstance(item, QtWidgets.QSpacerItem):
                self._tabsLayout.removeItem(item)
                spacer = QtWidgets.QSpacerItem(1, 1, *self._SPACER_ORIENTATION[a0])
                self._tabsLayout.insertItem(i, spacer)

        self._layout.setDirection(layout_direction)
        self._tabsLayout.setDirection(tab_direction)
        for b in self._tabs:
            b.setOrientation(self._tabsRotation)

        self._tabsWidget.setObjectName(self._TABS_WIDGET_STYLES[a0])
        self._tabsLayout.setContentsMargins(*self._TABS_WIDGET_CONTENT_MARGINS[a0])

    def setAlwaysOpen(self, b: bool):
        self._alwaysOpen = b

    def setTabIcon(self, index: int, icon: QtGui.QIcon):
        btn = self._tabs[index]
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(12, 12))
