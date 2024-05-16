from typing import Optional

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui

from editor.tools.base import BaseEditorTool


class HealingTool(BaseEditorTool):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__buffer: Optional[np.ndarray] = None
        self._active: bool = False

    def process(self):
        mask = cv2.cvtColor(self.__buffer, cv2.COLOR_BGRA2GRAY)
        image = self.model().cv2()
        result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)

        self.model().save_cv2(result)

    def clear(self):
        size = self.size()
        self.__buffer = np.zeros((size.height(), size.width(), 4), dtype=np.uint8)

    def mousePressEvent(self, pos: QtCore.QPoint):
        self._active = True

    def mouseMoveEvent(self, pos: QtCore.QPoint):
        if self._active:
            cv2.circle(self.__buffer, (pos.x(), pos.y()), 20, (255, 255, 255, 255), -1)

    def mouseReleaseEvent(self, pos: QtCore.QPoint):
        self._active = False
        self.process()
        self.clear()

    def paintEvent(self):
        buffer = (self.__buffer * (0, 0, 1, 0.5)).astype(np.uint8)
        buffer = cv2.cvtColor(buffer, cv2.COLOR_BGRA2RGBA)

        height, width, channel = buffer.shape
        bytes_per_line = 4 * width

        image = QtGui.QImage(buffer.data, width, height, bytes_per_line, QtGui.QImage.Format.Format_RGBA8888)
        return QtGui.QPixmap.fromImage(image)
