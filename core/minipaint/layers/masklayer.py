from typing import Optional

import numpy as np
from PyQt5 import QtCore

from core.minipaint.layers.base import BaseLayer


class MaskLayer(BaseLayer):

    def __init__(self, size: QtCore.QSize):
        super().__init__(size)
        self._buffer = np.ones((self._size.height(), self._size.width(), 4), dtype=np.uint8) * 255

    def getRGBA(self) -> Optional[np.ndarray]:
        buffer = self._buffer.copy()
        return buffer

    def setPixelData(self, data: np.ndarray):
        self._buffer = data

    def pixelData(self) -> Optional[np.ndarray]:
        return self._buffer.copy()

    def clear(self):
        self._buffer = np.ones((self._size.height(), self._size.width(), 4), dtype=np.uint8) * np.array((0, 0, 0, 255), dtype=np.uint8)
