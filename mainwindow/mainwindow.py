from PyQt5 import QtWidgets

from core.styling import make_stylesheet, Style
from core.widgets import TabWidget
from mainwindow.widgets.windows import FramelessWindow


class MainWindow(FramelessWindow):
    _STYLE = make_stylesheet([
        Style('*', {
            'background-color': '#2e2e2e'
        })
    ])

    def __init__(self):
        super().__init__(None)
        self.setStyleSheet(self._STYLE)

        self.tabs = TabWidget()
        self.tabs.setAlwaysOpen(True)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.East)

        self.addContentWidget(self.tabs)
