# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\projects\sd\kairyo-manager\extensions\projectmanager\resources\projectmanager.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProjectManagerTab(object):
    def setupUi(self, ProjectManagerTab):
        ProjectManagerTab.setObjectName("ProjectManagerTab")
        ProjectManagerTab.resize(789, 595)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ProjectManagerTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(ProjectManagerTab)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/projectmanager/folder.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab, icon, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.tabWidget)

        self.retranslateUi(ProjectManagerTab)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ProjectManagerTab)

    def retranslateUi(self, ProjectManagerTab):
        _translate = QtCore.QCoreApplication.translate
        ProjectManagerTab.setWindowTitle(_translate("ProjectManagerTab", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ProjectManagerTab", "Project"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ProjectManagerTab", "Tab 2"))
from . import resources_rc
