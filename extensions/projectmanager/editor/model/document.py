from typing import Dict, Optional, Type, List

import cv2
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

from core import imutils
from core.project import ProjectImage
from .viewport import Viewport
from ..tools.base import EditorToolBase


class Document:
    __CACHE: Dict[str, 'Document'] = {}

    def __init__(self, image: ProjectImage):
        super().__init__()

        self.__image = image

        self.__original: Optional[np.ndarray] = None
        self.__stack: List[np.ndarray] = []
        self.__stack_cursor: int = -1

        self.reloadFromDisk()

        self.__viewport = Viewport()
        self.__viewport.setSize(self.size())
        self.__viewport.setPixmapSize(self.size())
        self.__viewport.setScale(1)

        self.__tool: Optional[EditorToolBase] = None

    @classmethod
    def from_image(cls, image: ProjectImage):
        if image.path not in cls.__CACHE:
            cls.__CACHE[image.path] = cls(image)
        return cls.__CACHE[image.path]

    def image(self):
        if len(self.__stack) == 0 or self.__stack_cursor < 0:
            return self.__original
        return self.__stack[self.__stack_cursor]

    def size(self):
        h, w, _ = self.__original.shape
        return QtCore.QSize(w, h)

    def viewport(self):
        return self.__viewport

    def switchTool(self, factory: Optional[Type[EditorToolBase]]):
        self.__tool = factory(self) if factory is not None else None

    def cursor(self):
        return self.__tool.cursor() if self.__tool is not None else Qt.ArrowCursor

    def tool(self):
        return self.__tool

    def reloadFromDisk(self):
        arr = np.frombuffer(self.__image.read_version(), np.uint8)
        self.__original = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        self.__original = cv2.cvtColor(self.__original, cv2.COLOR_BGR2RGBA)

        self.__stack.clear()
        self.__stack_cursor = -1

    def mapToViewport(self, pos: QtCore.QPoint):
        return (pos - self.__viewport.topLeft()) / self.__viewport.scale()

    def currentBrush(self):
        if self.__tool is not None:
            return self.__tool.brush

    def saveToStack(self, cv_img):
        self.__stack = self.__stack[:self.__stack_cursor + 1]
        self.__stack.append(cv_img)
        self.__stack_cursor = len(self.__stack) - 1