import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import QEvent

from core.api import KairyoApi
from core.widgets import TabWidget
from mainwindow.widgets.windows import FramelessWindow


class MainWindow(FramelessWindow):

    def __init__(self):
        super().__init__(None)

        self.tabs = TabWidget()
        self.tabs.setAlwaysOpen(True)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.East)

        self.addContentWidget(self.tabs)

    def resizeEvent(self, a0):
        super(MainWindow, self).resizeEvent(a0)
        try:
            api = KairyoApi.instance()
            if api:
                api.settings.setValue('mainWindow/size', self.size())
        except BaseException as e:
            logging.error("", exc_info=e)
            raise

    def moveEvent(self, a0):
        super(MainWindow, self).moveEvent(a0)
        try:
            api = KairyoApi.instance()
            if api:
                api.settings.setValue('mainWindow/position', self.pos())
        except BaseException as e:
            logging.error("", exc_info=e)
            raise

    def changeEvent(self, a0):
        if a0.type() == QEvent.WindowStateChange:
            api = KairyoApi.instance()
            if api:
                api.settings.setValue('mainWindow/maximized', self.isMaximized())
