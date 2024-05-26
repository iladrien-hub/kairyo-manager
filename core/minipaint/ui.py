import logging
import time
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, Qt

from .callbacks import ImageEditorCallbacks
from .editor import ImageEditor
from .. import imutils
from ..widgets.layout import create_box_layout


class Renderer(QtCore.QObject):

    def __init__(self, editor: 'ImageEditorWidget'):
        super().__init__()
        self.__editor = editor

    def run(self):
        tick = 1 / 60

        while True:
            t_start = time.time()
            try:
                editor = self.__editor.activeEditor()
                if editor:
                    editor.renderCanvas()
            except BaseException as e:
                logging.error("", exc_info=e)
            finally:
                sleep = tick - (time.time() - t_start)
                if sleep > 0:
                    time.sleep(sleep)


class Processor(QtCore.QObject):

    def __init__(self, editor: 'ImageEditorWidget'):
        super().__init__()
        self.__editor = editor

    def run(self):
        tick = 1 / 60

        while True:
            t_start = time.time()
            try:
                editor = self.__editor.activeEditor()
                if editor:
                    editor.processEventQueue()
            except BaseException as e:
                logging.error("", exc_info=e)
            finally:
                sleep = tick - (time.time() - t_start)
                if sleep > 0:
                    time.sleep(sleep)


class CanvasWidget(QtWidgets.QFrame):
    def __init__(self, parent: 'ImageEditorWidget'):
        super().__init__()

        self.__parent = parent
        self.__keepFit = False

        self.__lastMousePosition: Optional[QtCore.QPoint] = None

        self.__keyPressed = {
            Qt.Key_Alt: False,
            Qt.Key_Control: False,
            Qt.Key_Space: False
        }

        self.__brushResizePoint: QtCore.QPoint = QtCore.QPoint()
        self.__resizingBrush: bool = False

    def updateCursor(self):
        if self.__keyPressed[Qt.Key_Space]:
            self.setCursor(Qt.OpenHandCursor)
        elif self.__keyPressed[Qt.Key_Control] or self.__keyPressed[Qt.Key_Alt]:
            self.setCursor(Qt.ArrowCursor)
        elif (editor := self.__parent.activeEditor()) and editor.activeBrush():
            self.setCursor(Qt.BlankCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def drawBrushCursor(self, painter, pos):
        editor = self.__parent.activeEditor()
        if not editor:
            return

        viewport = editor.viewport()

        if (brush := editor.activeBrush()) and (cursor := brush.cursor(viewport.scale())) is not None:
            h, w = cursor.shape[:2]

            cursor = imutils.cv2_to_qt(cursor)
            painter.drawPixmap(QtCore.QRect(pos.x() - w // 2, pos.y() - w // 2, w, h), cursor)

    def paintEvent(self, a0):
        try:
            editor = self.__parent.activeEditor()
            if not editor:
                return

            painter = QtGui.QPainter(self)
            viewport = editor.viewport()

            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
            painter.setRenderHint(QtGui.QPainter.LosslessImageRendering)

            image = editor.imageCanvas().pixmap()
            if image is not None:
                painter.drawPixmap(viewport, image)

            overlay = editor.toolCanvas().pixmap()
            if overlay is not None:
                painter.drawPixmap(viewport, overlay)

            if self.__keyPressed[Qt.Key_Space] or self.__keyPressed[Qt.Key_Control]:
                pass
            elif self.__keyPressed[Qt.Key_Alt] and self.__resizingBrush:
                self.drawBrushCursor(painter, self.__brushResizePoint)
            elif self.__keyPressed[Qt.Key_Alt]:
                pass
            else:
                self.drawBrushCursor(painter, self.mapFromGlobal(self.cursor().pos()))

        except BaseException as e:
            logging.error("", exc_info=e)

    def fitIntoView(self):
        editor = self.__parent.activeEditor()
        if not editor:
            return
        size = editor.size()

        width = size.width()
        height = size.height()

        self_width = self.width()
        self_height = self.height()

        aspect_ratio = width / height

        new_width = self_width
        new_height = int(new_width / aspect_ratio)

        if new_height > self_height:
            new_height = self_height

        viewport = editor.viewport()
        viewport.setScale(new_height / height)
        viewport.moveCenter(self.rect().center())

        self.__keepFit = True
        self.update()

    def resizeEvent(self, a0) -> None:
        if self.__keepFit:
            self.fitIntoView()

    def enterEvent(self, a0) -> None:
        super(CanvasWidget, self).enterEvent(a0)
        self.setFocus()

    def leaveEvent(self, a0) -> None:
        super(CanvasWidget, self).leaveEvent(a0)
        self.clearFocus()

    def mousePressEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        pos = a0.pos()
        editor = self.__parent.activeEditor()
        if not editor:
            return
        elif self.__keyPressed[Qt.Key_Alt] and bool(a0.buttons() & Qt.RightButton) and not self.__resizingBrush:
            self.__resizingBrush = True
            self.__brushResizePoint = pos
        elif not any(self.__keyPressed.values()):
            editor.mousePressEvent(editor.viewport().normalizePoint(pos))
        self.__lastMousePosition = pos

    def mouseMoveEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        pos = a0.pos()
        editor = self.__parent.activeEditor()

        if not editor:
            return
        elif bool(a0.buttons() & Qt.LeftButton) and self.__keyPressed[Qt.Key_Space]:
            delta = pos - self.__lastMousePosition
            editor.viewport().pan(delta.x(), delta.y())
            self.__keepFit = False
        elif bool(a0.buttons() & Qt.RightButton) and self.__keyPressed[Qt.Key_Alt]:
            if brush := editor.activeBrush():
                delta = pos.x() - self.__lastMousePosition.x()
                brush.setSize(brush.size() + delta * 2 / editor.viewport().scale())
        elif not any(self.__keyPressed.values()):
            editor.mouseMoveEvent(
                editor.viewport().normalizePoint(self.__lastMousePosition),
                editor.viewport().normalizePoint(pos),
            )
        self.__lastMousePosition = pos

    def mouseReleaseEvent(self, a0: Optional[QtGui.QMouseEvent]) -> None:
        pos = a0.pos()
        editor = self.__parent.activeEditor()

        if not editor:
            return
        elif not any(self.__keyPressed.values()):
            editor.mouseReleaseEvent(editor.viewport().normalizePoint(pos))

        if self.__resizingBrush:
            self.__resizingBrush = bool(a0.buttons() & Qt.RightButton)

        self.__lastMousePosition = pos

    def keyPressEvent(self, a0: Optional[QtGui.QKeyEvent]) -> None:
        key = a0.key()
        if key in self.__keyPressed:
            self.__keyPressed[key] = True
        self.updateCursor()

    def keyReleaseEvent(self, a0: Optional[QtGui.QKeyEvent]) -> None:
        key = a0.key()
        if key in self.__keyPressed:
            self.__keyPressed[key] = False
        self.updateCursor()

    def wheelEvent(self, a0: Optional[QtGui.QWheelEvent]) -> None:
        editor = self.__parent.activeEditor()
        if not editor:
            return

        if self.__keyPressed[Qt.Key_Control]:  # horizontal pan
            delta = a0.angleDelta().y()
            if delta != 0:
                delta //= abs(delta)
            editor.viewport().pan(10 * delta, 0)

            self.__keepFit = False

        elif self.__keyPressed[Qt.Key_Alt]:  # zoom
            steps = a0.angleDelta().x()
            if steps != 0:
                steps //= abs(steps)

            scale = editor.viewport().scale()
            editor.viewport().setScale(scale + 0.1 * steps, anchor=a0.pos())

            self.__keepFit = False

        else:  # vertical pan
            delta = a0.angleDelta().y()
            if delta != 0:
                delta //= abs(delta)
            editor.viewport().pan(0, 10 * delta)

            self.__keepFit = False


class ImageEditorWidget(QtWidgets.QWidget, ImageEditorCallbacks):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__activeEditor: Optional[ImageEditor] = None

        self.__canvas = CanvasWidget(self)

        self.__processor_thread = QThread()
        self.__processor = Processor(self)
        self.__processor.moveToThread(self.__processor_thread)

        self.__processor_thread.started.connect(self.__processor.run)
        self.__processor_thread.start()

        self.__renderer_thread = QThread()
        self.__renderer = Renderer(self)
        self.__renderer.moveToThread(self.__renderer_thread)

        self.__renderer_thread.started.connect(self.__renderer.run)
        self.__renderer_thread.start()

        self.setLayout(create_box_layout([self.__canvas]))

        self.__undo = QtWidgets.QShortcut("Ctrl+Z", self, self.on_undo_triggered)
        self.__redo = QtWidgets.QShortcut("Ctrl+R", self, self.on_redo_triggered)

    def activeEditor(self) -> Optional[ImageEditor]:
        return self.__activeEditor

    def setActiveEditor(self, editor: Optional[ImageEditor]):
        self.__activeEditor = editor
        self.__canvas.updateCursor()

    def fitIntoView(self):
        self.__canvas.fitIntoView()

    def renderCanvas(self):
        self.__canvas.update()

    def on_undo_triggered(self):
        editor = self.activeEditor()
        if editor is None:
            return

        editor.undo()

    def on_redo_triggered(self):
        editor = self.activeEditor()
        if editor is None:
            return

        editor.redo()
