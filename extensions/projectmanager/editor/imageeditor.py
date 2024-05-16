from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from core.project import ProjectImage
from core.widgets.toolbar import ToolBar
from editor.model import ImageModel, ImageModelCallbacks
from editor.tools.base import BaseEditorTool
from editor.tools.heal import HealingTool


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

        self._tool: Optional[BaseEditorTool] = None

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

    def clearTool(self):
        if self._tool is not None:
            if self._pixmap is not None:
                self._tool.setSize(self._pixmap.size())
            self._tool.clear()

    def setTool(self, tool: Optional[BaseEditorTool]):
        self._tool = tool
        self.clearTool()

    def setPixmap(self, pixmap: QtGui.QPixmap):
        self._pixmap = pixmap
        self.update()

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

        if self._tool and (pixmap := self._tool.paintEvent()):
            painter.drawPixmap(self._viewport, pixmap)

    def keyPressEvent(self, evt: Optional[QtGui.QKeyEvent]) -> None:
        key = evt.key()
        if key in self._activeKeys:
            self._activeKeys[key] = True

        self.updateCursor()

    def keyReleaseEvent(self, evt: Optional[QtGui.QKeyEvent]) -> None:
        key = evt.key()
        if key in self._activeKeys:
            self._activeKeys[key] = False

        self.updateCursor()

    def mousePressEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self._activeKeys[self.key_Pan] and evt.button() == Qt.LeftButton:
            self._isPanActive = True
            self._panAnchor = evt.pos()
            self._panOrigin = self._viewport.center()

        elif self._tool is not None:
            self._tool.mousePressEvent((evt.pos() - self._viewport.topLeft()) / self._zoom)
            self.update()

        self.updateCursor()

    def mouseMoveEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self._isPanActive:
            self._viewport.moveCenter(self._panOrigin + evt.pos() - self._panAnchor)
            self.update()
        elif self._tool is not None:
            self._tool.mouseMoveEvent((evt.pos() - self._viewport.topLeft()) / self._zoom)
            self.update()

    def mouseReleaseEvent(self, evt: Optional[QtGui.QMouseEvent]) -> None:
        if not evt:
            return

        if self._isPanActive:
            self._isPanActive = False
        elif self._tool is not None:
            self._tool.mouseReleaseEvent((evt.pos() - self._viewport.topLeft()) / self._zoom)
            self.update()

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

        self._image: Optional[ImageModel] = None
        self._image_callbacks = ImageModelCallbacks()

        self._toolBar = ToolBar()
        self._toolBar.setFixedHeight(26)

        self._toolsGroup = QtWidgets.QButtonGroup()
        self._toolsGroup.setExclusive(True)

        self._healingToolButton = self._toolBar.addButton(':/projectmanager/virus-slash.svg', 'Healing Brush (J)')
        self._healingToolButton.setCheckable(True)
        self._healingToolButton.setShortcut('J')
        self._toolsGroup.addButton(self._healingToolButton)

        self._tools = {
            self._toolsGroup.id(self._healingToolButton): HealingTool
        }

        self._actualSizeButton = self._toolBar.addButton(':/projectmanager/arrows-maximize.svg', 'Actual Size')
        self._fitButton = self._toolBar.addButton(':/projectmanager/aspect-ratio.svg', 'Fit Zoom to View (Ctrl+0)')
        self._fitButton.setShortcut('Ctrl+0')

        self._undoButton = self._toolBar.addButton(':/projectmanager/rotate-left.svg', 'Undo (Ctrl+Shift+Z)')
        self._undoButton.setShortcut('Ctrl+Shift+Z')
        self._redoButton = self._toolBar.addButton(':/projectmanager/rotate-right.svg', 'Redo (Ctrl+Shift+R)')
        self._redoButton.setShortcut('Ctrl+Shift+R')

        self._saveButton = self._toolBar.addButton(':/projectmanager/floppy-disk.svg', 'Save (Ctrl+S)')
        self._saveButton.setShortcut('Ctrl+S')

        self._scene = ImageEditorSceneWidget()

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._toolBar)
        self._layout.addWidget(self._scene)

        self.setLayout(self._layout)

        self._actualSizeButton.clicked.connect(self.on_actualSizeButton_clicked)
        self._fitButton.clicked.connect(self.on_fitButton_clicked)
        self._undoButton.clicked.connect(self.on_undoButton_clicked)
        self._redoButton.clicked.connect(self.on_redoButton_clicked)
        self._saveButton.clicked.connect(self.on_saveButton_clicked)

        self._toolsGroup.buttonPressed.connect(self.on_buttonGroup_pressed)
        self._toolsGroup.buttonClicked.connect(self.on_buttonGroup_clicked)

        self._image_callbacks.bufferUpdated.connect(self.on_callbacks_bufferUpdated)
        self.updateButtons()

    def setImage(self, image: ProjectImage):
        self._image = ImageModel(self._image_callbacks, image)
        self.updateScene()
        self._scene.clearTool()
        self._scene.fit()
        self.updateButtons()

    def updateScene(self):
        self._scene.setPixmap(self._image.pixmap())

    def updateButtons(self):
        if self._image is None:
            self._undoButton.setEnabled(False)
            self._redoButton.setEnabled(False)
            self._fitButton.setEnabled(False)
            self._actualSizeButton.setEnabled(False)
            self._healingToolButton.setEnabled(False)
            self._saveButton.setEnabled(False)
            return

        self._undoButton.setEnabled(self._image.hasUndo())
        self._redoButton.setEnabled(self._image.hasRedo())
        self._fitButton.setEnabled(True)
        self._actualSizeButton.setEnabled(True)
        self._healingToolButton.setEnabled(True)
        self._saveButton.setEnabled(not self._image.saved())

    def on_actualSizeButton_clicked(self):
        self._scene.resetZoom()

    def on_fitButton_clicked(self):
        self._scene.fit()

    def on_undoButton_clicked(self):
        self._image.undo()

    def on_redoButton_clicked(self):
        self._image.redo()

    def on_saveButton_clicked(self):
        self._image.save()
        self._saveButton.setEnabled(not self._image.saved())

    def on_buttonGroup_pressed(self, button: QtWidgets.QToolButton):
        self._toolsGroup.setExclusive(not button.isChecked())

    def on_buttonGroup_clicked(self, button: QtWidgets.QToolButton):
        self._toolsGroup.setExclusive(True)
        if button.isChecked():
            constructor = self._tools.get(self._toolsGroup.id(button))
            self._scene.setTool(constructor(self._image))
        else:
            self._scene.setTool(None)

    def on_callbacks_bufferUpdated(self):
        self.updateScene()
        self.updateButtons()
