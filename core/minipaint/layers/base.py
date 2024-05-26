from abc import ABC
from typing import Optional

import numpy as np
from PyQt5 import QtCore

from ..renderable import Renderable


class BaseLayer(Renderable, ABC):

    def __init__(self, size: QtCore.QSize):
        self._size = size

    def setPixelData(self, data: np.ndarray):
        pass

    def pixelData(self) -> Optional[np.ndarray]:
        pass
