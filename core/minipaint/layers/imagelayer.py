from typing import Optional

import numpy as np
from PyQt5 import QtCore

from .maskablelayer import MaskableLayer


class ImageLayer(MaskableLayer):

    def __init__(self, size: QtCore.QSize):
        super().__init__(size)
        self._buffer = np.ndarray((self._size.height(), self._size.width(), 4))

    def setPixelData(self, data: np.ndarray):
        self._buffer = data

    def pixelData(self) -> Optional[np.ndarray]:
        return self._buffer.copy()

    def getRGBA(self) -> Optional[np.ndarray]:
        buffer = self._buffer.copy()
        return buffer
