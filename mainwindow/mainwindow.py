from PyQt5 import QtWidgets

from core.widgets import TabWidget
from mainwindow.widgets.windows import FramelessWindow


class MainWindow(FramelessWindow):

    def __init__(self):
        super().__init__(None)

        self.tabs = TabWidget()
        self.tabs.setAlwaysOpen(True)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.East)

        self.addContentWidget(self.tabs)
