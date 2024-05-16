from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from core.widgets.toolbar import ToolBar


class ImageEditorSceneWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(ImageEditorSceneWidget, self).__init__(*args, **kwargs)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._pixmap = None

        self._zoom = 1.0
        self._viewport = QtCore.QRect()

        self._isPanActive = False
        self._panAnchor = QtCore.QPoint()
        self._panOrigin = QtCore.QPoint()

        self.key_Pan = Qt.Key_Space
        self.key_Zoom = Qt.Key_Control

        self._activeKeys = {
            self.key_Pan: False,
            self.key_Zoom: False
        }

    def fit(self):
        width = self._pixmap.width()
        height = self._pixmap.height()

        self_width = self.width()
        self_height = self.height()

        aspect_ratio = width / height

        new_width = self_width
        new_height = int(new_width / aspect_ratio)

        if new_height > self_height:
            new_height = self_height

        self.setZoom(new_height / height)

        self._viewport.moveCenter(self.rect().center())
        self.update()

    def updateCursor(self):
        if self._isPanActive:
            self.setCursor(Qt.ClosedHandCursor)
        elif self._activeKeys[self.key_Pan]:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def setPixmap(self, pixmap: QtGui.QPixmap):
        self._pixmap = pixmap
        self.fit()

    def setZoom(self, new_zoom: float, anchor: QtCore.QPoint = None):
        # save the old zoom value, we'll need it later
        old_zoom = self._zoom

        # update the zoom value. if it has not changed, do nothing
        self._zoom = new_zoom
        self._zoom = max(min(self._zoom, 3.0), 0.1)
        if old_zoom == self._zoom:
            return

        # save the old center of the viewport and update its dimensions based on the zoom and image size
        old_center = self._viewport.center()
        self._viewport.setSize(self._pixmap.size() * self._zoom)

        # Now for the tricky part...
        if anchor is not None:
            # When zooming, all distances in the image change their size.
            # Therefore, in order to fix a point on the image relative to the cursor position, you need to shift
            # the center of the image by the amount of zoom.
            #
            # Find the vector between the point under the cursor and the OLD center of the viewport.
            # It's important to save this center before resizing, because it will change afterwards.
            vector = old_center - anchor

            # Next, we multiply this vector by the amount of zoom change, which is expressed as the ratio of the new
            # value to the old one
            #
            # After that, we return this vector to the global coordinate system by adding it to the cursor position.
            # Voilà, the new center of the viewport.
            new_pos = anchor + vector * self._zoom / old_zoom

            self._viewport.moveCenter(new_pos)

        self.update()

    def resetZoom(self):
        old_pos = self._viewport.center()
        self.setZoom(1)
        self._viewport.moveCenter(old_pos)

    def paintEvent(self, a0: Optional[QtGui.QPaintEvent]):
        if not self._pixmap:
            return

        painter = QtGui.QPainter(self)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.LosslessImageRendering)

        painter.drawPixmap(self._viewport, self._pixmap)

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self._activeKeys[self.key_Pan] and evt.button() == Qt.LeftButton:
            self._isPanActive = True
            self._panAnchor = evt.pos()
            self._panOrigin = self._viewport.center()

        self.updateCursor()

    def keyPressEvent(self, evt: Optional[QtGui.QKeyEvent]) -> None:
        key = evt.key()
        if key in self._activeKeys:
            self._activeKeys[key] = True

        if key == Qt.Key_S:
            self.fit()

        self.updateCursor()

    def keyReleaseEvent(self, evt: Optional[QtGui.QKeyEvent]) -> None:
        key = evt.key()
        if key in self._activeKeys:
            self._activeKeys[key] = False

        self.updateCursor()

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self._isPanActive:
            self._viewport.moveCenter(self._panOrigin + evt.pos() - self._panAnchor)
            self.update()

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self._isPanActive:
            self._isPanActive = False

        self.updateCursor()

    def enterEvent(self, a0: Optional[QtCore.QEvent]) -> None:
        self.setFocus()

    def leaveEvent(self, a0: Optional[QtCore.QEvent]) -> None:
        self.clearFocus()

    def wheelEvent(self, evt: Optional[QtGui.QWheelEvent]):
        steps = evt.angleDelta().y()
        if steps != 0:
            steps //= abs(steps)

        if self._activeKeys[self.key_Zoom]:
            self.setZoom(self._zoom + 0.1 * steps, anchor=evt.pos())


class ImageEditorWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._toolBar = ToolBar()
        self._toolBar.setFixedHeight(26)
        self._actualSizeButton = self._toolBar.addButton(':/projectmanager/arrows-maximize.svg', 'Actual Size')
        self._fitButton = self._toolBar.addButton(':/projectmanager/aspect-ratio.svg', 'Fit Zoom to View')

        self._scene = ImageEditorSceneWidget()

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._toolBar)
        self._layout.addWidget(self._scene)

        self.setLayout(self._layout)

        self._actualSizeButton.clicked.connect(self.on_actualSizeButton_clicked)
        self._fitButton.clicked.connect(self.on_fitButton_clicked)

    def scene(self):
        return self._scene

    def on_actualSizeButton_clicked(self):
        self._scene.resetZoom()

    def on_fitButton_clicked(self):
        self._scene.fit()
