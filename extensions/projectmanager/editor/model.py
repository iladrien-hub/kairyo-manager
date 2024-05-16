import cv2
import numpy as np
from PyQt5 import QtGui, QtCore

from core.project import ProjectImage


class ImageModelCallbacks(QtCore.QObject):
    bufferUpdated = QtCore.pyqtSignal()


class ImageModel(QtCore.QObject):

    def __init__(self, callbacks: ImageModelCallbacks, image: ProjectImage):
        super().__init__()

        self.__callbacks = callbacks
        self.__image: ProjectImage = image
        self.__original: bytes = image.read_version()
        self.__stack: list = []
        self.__stack_cursor = -1

        self.__saved = True

    def data(self) -> bytes:
        if len(self.__stack) > 0 and self.__stack_cursor >= 0:
            return self.__stack[self.__stack_cursor]
        return self.__original

    def cv2(self) -> np.ndarray:
        data = self.data()
        arr = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    def pixmap(self) -> QtGui.QPixmap:
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(self.data())
        return pixmap

    def saveCv2(self, im: np.ndarray):
        self.__stack = self.__stack[:self.__stack_cursor + 1]
        self.__stack.append(cv2.imencode('.png', im)[1].tostring())
        self.__stack_cursor = len(self.__stack) - 1

        self.__saved = False
        self.__callbacks.bufferUpdated.emit()

    def hasUndo(self):
        return self.__stack_cursor >= 0

    def hasRedo(self):
        return self.__stack_cursor < len(self.__stack) - 1

    def undo(self):
        self.__stack_cursor = max(self.__stack_cursor - 1, -1)
        self.__saved = False
        self.__callbacks.bufferUpdated.emit()

    def redo(self):
        self.__stack_cursor = min(self.__stack_cursor + 1, len(self.__stack) - 1)
        self.__saved = False
        self.__callbacks.bufferUpdated.emit()

    def saved(self):
        return self.__saved

    def save(self):
        self.__saved = True
        self.__image.update(self.data())
        self.__callbacks.bufferUpdated.emit()


