# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\projects\sd\kairyo-manager\mainwindow\resources\header.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(654, 379)
        self.toolButton = QtWidgets.QToolButton(Form)
        self.toolButton.setGeometry(QtCore.QRect(320, 180, 31, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/mainwindow/xmark.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon)
        self.toolButton.setObjectName("toolButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.toolButton.setText(_translate("Form", "..."))
from . import resources_rc