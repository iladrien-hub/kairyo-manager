import math
from typing import Optional

import cv2
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

from core import imutils
from .base import EditorToolBase
from ..model.brush import Brush


class HealingBrushTool(EditorToolBase):
    hasOverlay = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = self.doc.size()
        self.__buffer = np.zeros((size.height(), size.width()), dtype=float)

        self.__overlay = np.ones((size.height(), size.width(), 4), dtype=np.uint8)
        self.__overlay *= np.array([255, 0, 0, 0], dtype=np.uint8)

        self.brush = Brush()

        self.__pressed = False
        self.__last_point = None

    def process(self):
        h, w = self.__buffer.shape[:2]
        mask = self.__buffer.reshape((h, w, 1)).astype(np.uint8)

        image = cv2.cvtColor(self.doc.image(), cv2.COLOR_RGBA2BGR)
        result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGBA)

        self.doc.saveToStack(result)

        self.__buffer = np.zeros((h, w), dtype=np.uint8)
        self.__overlay[:, :, 3] = np.zeros_like(self.__buffer, dtype=np.uint8)

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if evt.button() == Qt.LeftButton:
            self.__pressed = True
            self.__last_point = self.doc.mapToViewport(evt.pos())

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if self.__pressed:
            finish = self.doc.mapToViewport(evt.pos())
            if self.__last_point is None:
                self.__last_point = finish
                return

            size = self.doc.size()

            stamp = cv2.cvtColor(self.brush.stamp(), cv2.COLOR_RGBA2GRAY)
            sh, sw = stamp.shape[:2]
            offset = QtCore.QPoint(sw, sh) / 2

            start = self.__last_point
            delta = finish - start
            distance = math.sqrt(delta.x() ** 2 + delta.y() ** 2)

            steps_count = round(distance / 3)
            for i in range(steps_count + 1):
                pos = start + delta * i / steps_count - offset
                x = min(max(pos.x(), 1 - sw), size.width() - 1)
                y = min(max(pos.y(), 1 - sh), size.height() - 1)

                imutils.maximum(self.__buffer, stamp, (x, y))

            self.__overlay[:, :, 3] = self.__buffer / 2
            self.__last_point = finish

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if evt.button() == Qt.LeftButton:
            self.__pressed = False
            self.__last_point = None
            self.process()

    def cursor(self):
        return Qt.BlankCursor

    def overlay(self):
        return self.__overlay
