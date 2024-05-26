import time
from typing import Optional, List

import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter

from .layers.maskablelayer import MaskableLayer
from .renderable import Renderable
from .. import imutils


class Canvas:

    def __init__(self, size: QtCore.QSize):
        self.__size = size
        self.__pixmap: Optional[QPixmap] = None

        self.__outdated: bool = False
        self.__lastRender: float = 0

    def render(self, items: List[Renderable]):
        pixmap = QPixmap(self.__size)
        pixmap.fill(Qt.transparent)
        rect = QtCore.QRect(QtCore.QPoint(), self.__size)

        painter = QPainter(pixmap)

        for item in items:
            if item is None:
                continue

            cv_img = item.getRGBA()
            if cv_img is None:
                continue

            if isinstance(item, MaskableLayer):
                mask = item.mask().getRGBA()
                mask = cv2.cvtColor(mask, cv2.COLOR_RGBA2GRAY)
                cv_img[..., 3] = mask

                # print(mask.shape)

            painter.drawPixmap(rect, imutils.cv2_to_qt(cv_img))

        painter.end()
        self.__pixmap = pixmap
        self.__outdated = False
        self.__lastRender = time.time()

    def renderIfNeeded(self, items: List[Renderable]):
        if self.__outdated and (time.time() - self.__lastRender) > 0.05:
            self.render(items)

    def pixmap(self):
        return self.__pixmap

    def markOutdated(self, b: bool):
        self.__outdated = self.__outdated or b
