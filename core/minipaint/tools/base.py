from abc import ABC
from typing import TYPE_CHECKING, Optional

from PyQt5 import QtCore

from ..brush.base import BaseBrush
from ..renderable import Renderable

if TYPE_CHECKING:
    from ..editor import ImageEditor


class BaseTool(Renderable, ABC):

    def __init__(self):
        self.__editor: Optional['ImageEditor'] = None

    def editor(self):
        return self.__editor

    def brush(self) -> Optional[BaseBrush]:
        pass

    def setEditor(self, editor: 'ImageEditor'):
        self.__editor = editor

    def mousePressEvent(self, p: QtCore.QPoint) -> bool:
        pass

    def mouseMoveEvent(self, p1: QtCore.QPoint, p2: QtCore.QPoint) -> bool:
        pass

    def mouseReleaseEvent(self, p: QtCore.QPoint) -> bool:
        pass
