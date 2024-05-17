from typing import Optional, TYPE_CHECKING

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

if TYPE_CHECKING:
    from ..model.document import Document
    from ..model.brush import Brush


class EditorToolBase:
    hasOverlay: bool = False

    def __init__(self, document: 'Document'):
        self.doc: Optional['Document'] = document
        self.brush: Optional['Brush'] = None

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        pass

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        pass

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        pass

    def wheelEvent(self, evt: Optional[QtGui.QWheelEvent]) -> None:
        pass

    def cursor(self):
        return Qt.ArrowCursor

    def overlay(self):
        pass
