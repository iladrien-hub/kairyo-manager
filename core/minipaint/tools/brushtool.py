import math
from typing import Optional

import cv2
import numpy as np
from PyQt5 import QtCore

from .base import BaseTool
from ..brush.roundbrush import RoundBrush
from ..historymanager import HistoryItem
from ..layers.base import BaseLayer


class BrushToolHistoryItem(HistoryItem):

    def __init__(self, layer: BaseLayer, before: np.ndarray, after: np.ndarray):
        self.after = after
        self.before = before
        self.layer = layer

    def undo(self):
        self.layer.setPixelData(self.before)

    def redo(self):
        self.layer.setPixelData(self.after)


class BrushTool(BaseTool):

    def __init__(self, size: QtCore.QSize):
        super().__init__()

        self._size = size
        self._brush = RoundBrush()

        self._color = np.array([[0, 0, 0, 0.5]])
        self._buffer = self.newBuffer()

    def setColor(self, color: np.ndarray):
        self._color = color

    def newBuffer(self):
        return np.zeros((self._size.height(), self._size.width(), 4), dtype=np.uint8)

    def brush(self):
        return self._brush

    def getRGBA(self) -> Optional[np.ndarray]:
        return self._buffer

    def putStamp(self, stamp, x, y):
        h, w = self._buffer.shape[:2]
        sh, sw = stamp.shape[:2]

        cxs, cys, cxf, cyf = 0, 0, sw, sh

        if x < 0:
            cxs = -x
            x = 0
        if y < 0:
            cys = -y
            y = 0
        if (xf := x + sw) > w:
            cxf = w - xf
        if (yf := y + sh) > h:
            cyf = h - yf

        stamp = stamp[cys:cyf, cxs:cxf]
        sh, sw = stamp.shape[:2]

        if sh == 0 or sw == 0:
            return False

        self._buffer[y:y + sh, x:x + sw] = np.maximum(stamp, self._buffer[y:y + sh, x:x + sw])

    def mouseMoveEvent(self, start: QtCore.QPoint, finish: QtCore.QPoint) -> bool:
        stamp = (self._brush.stamp() * self._color).astype(np.uint8)

        sh, sw = stamp.shape[:2]
        offset = QtCore.QPoint(sw, sh) / 2

        delta = finish - start
        distance = math.sqrt(delta.x() ** 2 + delta.y() ** 2)

        step = self._brush.size() * 0.2
        steps_count = round(distance / step)
        for i in range(steps_count + 1):
            pos = start + delta * i / steps_count - offset

            x = min(max(pos.x(), 1 - sw), self._size.width() - 1)
            y = min(max(pos.y(), 1 - sh), self._size.height() - 1)

            self.putStamp(stamp, x, y)

        return True

    def apply(self, hh1, hh2):
        # store the alpha channels only
        m1 = hh1[:, :, 3]
        m2 = hh2[:, :, 3]

        # invert the alpha channel and obtain 3-channel mask of float data type
        m1i = cv2.bitwise_not(m1)
        alpha1i = cv2.cvtColor(m1i, cv2.COLOR_GRAY2BGRA) / 255.0

        m2i = cv2.bitwise_not(m2)
        alpha2i = cv2.cvtColor(m2i, cv2.COLOR_GRAY2BGRA) / 255.0

        # Perform blending and limit pixel values to 0-255 (convert to 8-bit)
        b1i = cv2.convertScaleAbs(hh2 * (1 - alpha2i) + hh1 * alpha2i)

        # Finding common ground between both the inverted alpha channels
        mul = cv2.multiply(alpha1i, alpha2i)

        # converting to 8-bit
        mulint = cv2.normalize(mul, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # again create 3-channel mask of float data type
        alpha = cv2.cvtColor(mulint[:, :, 2], cv2.COLOR_GRAY2BGRA) / 255.0

        # perform blending using previous output and multiplied result
        return cv2.convertScaleAbs(b1i * (1 - alpha) + mulint * alpha)

    def mouseReleaseEvent(self, p: QtCore.QPoint) -> bool:
        editor = self.editor()

        layer = editor.currentLayer()
        pixels = layer.pixelData()

        if pixels is not None:
            result = self.apply(pixels, self._buffer)
            layer.setPixelData(result)
            editor.imageCanvas().markOutdated(True)
            editor.history().save(BrushToolHistoryItem(
                layer,
                pixels,
                result
            ))

        self._buffer = self.newBuffer()
        return True
