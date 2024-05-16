from typing import TYPE_CHECKING

from PyQt5 import QtCore

from editor.model import ImageModel


class BaseEditorTool:

    def __init__(self, model: ImageModel):
        self.__model = model
        self.__size: QtCore.QSize = QtCore.QSize()

    def model(self):
        return self.__model

    def size(self):
        return self.__size

    def setSize(self, s: QtCore.QSize):
        self.__size = s

    def clear(self):
        pass

    def mousePressEvent(self, pos: QtCore.QPoint):
        pass

    def mouseMoveEvent(self, pos: QtCore.QPoint):
        pass

    def mouseReleaseEvent(self, pos: QtCore.QPoint):
        pass

    def paintEvent(self):
        pass
