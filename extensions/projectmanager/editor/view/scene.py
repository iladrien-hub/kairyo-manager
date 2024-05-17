from typing import Optional, Dict, Type

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from core import imutils
from ..model.brush import Brush
from ..model.document import Document


class EditorSceneTool:
    def __init__(self):
        self.doc: Optional[Document] = None

    def withDocument(self, doc: Document):
        self.doc = doc
        return self

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


class PanTool(EditorSceneTool):

    def __init__(self):
        super().__init__()

        self.__isPanning: bool = False
        self.__anchor: QtCore.QPoint = QtCore.QPoint()
        self.__origin: QtCore.QPoint = QtCore.QPoint()

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not self.doc:
            return
        if evt.button() == Qt.LeftButton:
            self.__isPanning = True
            self.__anchor = evt.pos()
            self.__origin = self.doc.viewport().center()

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if self.__isPanning:
            self.doc.viewport().moveCenter(self.__origin + evt.pos() - self.__anchor)

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if evt.button() == Qt.LeftButton:
            self.__isPanning = False

    def cursor(self):
        return Qt.ClosedHandCursor if self.__isPanning else Qt.OpenHandCursor


class ZoomTool(EditorSceneTool):

    def wheelEvent(self, evt: Optional[QtGui.QWheelEvent]) -> None:

        if not self.doc:
            return

        steps = evt.angleDelta().y()
        if steps != 0:
            steps //= abs(steps)

        scale = self.doc.viewport().scale()
        self.doc.viewport().setScale(scale + 0.1 * steps, anchor=evt.pos())


class BrushResizeTool(EditorSceneTool):
    def __init__(self):
        super().__init__()

        self.__isResizing: bool = False
        self.__anchor: QtCore.QPoint = QtCore.QPoint()
        self.__brush: Optional[Brush] = None
        self.__originSize: int = 0

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not self.doc:
            return
        if evt.button() == Qt.RightButton and self.doc.currentBrush():
            self.__brush = self.doc.currentBrush()
            self.__originSize = self.__brush.size()
            self.__isResizing = True
            self.__anchor = evt.pos()

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if self.__isResizing:
            delta = (evt.pos() - self.__anchor) / self.doc.viewport().scale()
            self.__brush.setSize(self.__originSize + delta.x() * 2)

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if evt.button() == Qt.RightButton:
            self.__brush = None
            self.__isResizing = False

    def brush(self):
        return self.__brush

    def anchor(self):
        return self.__anchor


class EditorScene(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.__doc: Optional[Document] = None
        self.__activeTool: Optional[EditorSceneTool] = None
        self.__tools: Dict[int, EditorSceneTool] = {
            Qt.Key_Space: PanTool(),
            Qt.Key_Control: ZoomTool(),
            Qt.Key_Shift: BrushResizeTool(),
        }

        self.__keepFit = False
        self.__keepFitResetButtons = [Qt.Key_Space, Qt.Key_Control]

        self.setMouseTracking(True)

    def setDocument(self, document: Document):
        self.__doc = document
        self.update()

    def updateCursor(self):
        if self.__activeTool is not None:
            self.setCursor(self.__activeTool.cursor())
        elif self.__doc is not None:
            self.setCursor(self.__doc.cursor())
        else:
            self.setCursor(Qt.ArrowCursor)

    def paintEvent(self, evt: Optional[QtGui.QPaintEvent]):
        if self.__doc is None:
            return

        painter = QtGui.QPainter(self)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.LosslessImageRendering)

        painter.drawPixmap(self.__doc.viewport(), imutils.cv2_to_qt(self.__doc.image()))

        if self.__activeTool:
            if isinstance(self.__activeTool, BrushResizeTool) and (brush := self.__activeTool.brush()):
                stamp = (brush.stamp() * (1, 0, 0, 1)).astype(np.uint8)
                stamp = imutils.resize(stamp, self.__doc.viewport().scale())
                stamp = imutils.cv2_to_qt(stamp)

                anchor = self.__activeTool.anchor()
                rect = QtCore.QRect(QtCore.QPoint(0, 0), stamp.size())

                rect.moveCenter(anchor)
                painter.drawPixmap(rect, stamp)

        if self.__doc.tool():
            if self.__doc.tool().hasOverlay:
                overlay = self.__doc.tool().overlay()
                overlay = imutils.cv2_to_qt(overlay)

                painter.drawPixmap(self.__doc.viewport(), overlay)

            if self.__activeTool is None and (brush := self.__doc.currentBrush()):
                size = int(brush.size() * self.__doc.viewport().scale())

                circle = np.zeros((size or 1, size or 1, 4), dtype=np.uint8)
                radius = size // 2 or 1
                cv2.circle(circle, (radius, radius), radius, (255, 255, 255, 255), 1)
                cv2.circle(circle, (radius, radius), radius - 1, (0, 0, 0, 255), 1)

                circle = imutils.cv2_to_qt(circle)

                rect = QtCore.QRect(QtCore.QPoint(0, 0), circle.size())
                rect.moveCenter(self.mapFromGlobal(self.cursor().pos()))

                painter.drawPixmap(rect, circle)

        painter.end()

    def enterEvent(self, a0: Optional[QtCore.QEvent]) -> None:
        self.setFocus()

    def leaveEvent(self, a0: Optional[QtCore.QEvent]) -> None:
        self.clearFocus()

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self.__activeTool is not None:
            self.__activeTool.mousePressEvent(evt)
        elif self.__doc is not None and (tool := self.__doc.tool()):
            tool.mousePressEvent(evt)

        self.updateCursor()
        self.update()

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self.__activeTool is not None:
            self.__activeTool.mouseMoveEvent(evt)
        elif self.__doc is not None and (tool := self.__doc.tool()):
            tool.mouseMoveEvent(evt)

        self.updateCursor()
        self.update()

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return
        if self.__activeTool is not None:
            self.__activeTool.mouseReleaseEvent(evt)
        elif self.__doc is not None and (tool := self.__doc.tool()):
            tool.mouseReleaseEvent(evt)

        self.updateCursor()
        self.update()

    def wheelEvent(self, evt: Optional[QtGui.QWheelEvent]):
        if not evt:
            return
        if self.__activeTool is not None:
            self.__activeTool.wheelEvent(evt)
        self.updateCursor()
        self.update()

    def keyPressEvent(self, evt: Optional[QtGui.QKeyEvent]) -> None:
        key = evt.key()
        if key in self.__tools and self.__activeTool is None:
            self.__activeTool = self.__tools[key].withDocument(self.__doc)
            self.__keepFit = self.__keepFit and key not in self.__keepFitResetButtons

        self.updateCursor()

    def keyReleaseEvent(self, evt: Optional[QtGui.QKeyEvent]) -> None:
        if self.__activeTool is None:
            return

        key = evt.key()
        if key in self.__tools and self.__activeTool is self.__tools[key]:
            self.__activeTool = None
        self.updateCursor()

    def resizeEvent(self, a0: Optional[QtGui.QResizeEvent]) -> None:
        if self.__keepFit:
            self.fitIntoView()

    def fitIntoView(self):
        if self.__doc is None:
            return
        size = self.__doc.size()

        width = size.width()
        height = size.height()

        self_width = self.width()
        self_height = self.height()

        aspect_ratio = width / height

        new_width = self_width
        new_height = int(new_width / aspect_ratio)

        if new_height > self_height:
            new_height = self_height

        viewport = self.__doc.viewport()
        viewport.setScale(new_height / height)
        viewport.moveCenter(self.rect().center())

        self.__keepFit = True
        self.update()

    def resetScale(self):
        viewport = self.__doc.viewport()
        center = viewport.center()
        viewport.setScale(1)
        viewport.moveCenter(center)

        self.update()
