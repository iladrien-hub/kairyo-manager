from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QIODevice

from core.util.icon import load_icon
from ..generated.projectmanager import Ui_ProjectManagerTab


class ProjectManagerTab(QtWidgets.QWidget, Ui_ProjectManagerTab):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # self.tabWidget.setTabIcon(0, qtawesome.icon("fa5.folder", color='white'))
        # self.tabWidget.setTabIcon(1, qtawesome.icon("fa5s.info", color='white'))
