import queue
from typing import Optional

import cv2
import numpy as np
from PyQt5 import QtCore

from .brush.base import BaseBrush
from .callbacks import ImageEditorCallbacks
from .canvas import Canvas
from .event import MousePressEvent, MouseMoveEvent, MouseReleaseEvent
from .historymanager import HistoryManager
from .layergroup import LayerGroup
from .layers.base import BaseLayer
from .layers.imagelayer import ImageLayer
from .toolmanager import ToolManager
from .tools.base import BaseTool
from .viewport import Viewport


class ImageEditor:

    def __init__(self, image: np.ndarray):
        self.__image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
        self.__size = QtCore.QSize(*image.shape[:2][::-1])

        self.__layers = LayerGroup()
        layer = ImageLayer(self.__size)
        layer.setPixelData(self.__image)
        self.__layers.addLayer(layer)
        self.__layers.setCurrentLayer(layer)

        self.__toolManager = ToolManager()
        self.__imageCanvas = Canvas(self.__size)
        self.__imageCanvas.render(self.__layers.layers())

        self.__historyManager = HistoryManager()

        self.__toolCanvas = Canvas(self.__size)

        self.__callbacks = ImageEditorCallbacks()
        self.__viewport = Viewport()
        self.__viewport.setPixmapSize(self.__size)

        self.__eventQueue = queue.Queue()

    def history(self):
        return self.__historyManager

    def undo(self):
        self.__imageCanvas.markOutdated(self.__historyManager.undo())

    def redo(self):
        self.__imageCanvas.markOutdated(self.__historyManager.redo())

    def currentLayer(self) -> Optional[BaseLayer]:
        return self.__layers.currentLayer()

    def setCurrentLayer(self, layer: BaseLayer):
        self.__layers.setCurrentLayer(layer)

    def addLayer(self, layer: BaseLayer):
        self.__layers.addLayer(layer)

    def activeBrush(self) -> Optional[BaseBrush]:
        if (tool := self.__toolManager.activeTool()) and (brush := tool.brush()):
            return brush

    def viewport(self):
        return self.__viewport

    def imageCanvas(self) -> Canvas:
        return self.__imageCanvas

    def toolCanvas(self) -> Canvas:
        return self.__toolCanvas

    def renderCanvas(self):
        self.__imageCanvas.renderIfNeeded(self.__layers.layers())
        self.__toolCanvas.renderIfNeeded([self.__toolManager.activeTool()])
        self.__callbacks.renderCanvas()

    def installCallbacks(self, callbacks: ImageEditorCallbacks):
        self.__callbacks = callbacks

    def addTool(self, tool: BaseTool):
        self.__toolManager.addTool(tool)
        tool.setEditor(self)
        return tool

    def setActiveTool(self, tool: BaseTool):
        self.__toolManager.setActiveTool(tool)

    def resetTool(self):
        self.__toolManager.setActiveTool(None)

    def size(self):
        return self.__size

    def mousePressEvent(self, p: QtCore.QPoint):
        self.__eventQueue.put(MousePressEvent(p))

    def mouseMoveEvent(self, p1: QtCore.QPoint, p2: QtCore.QPoint):
        self.__eventQueue.put(MouseMoveEvent(p1, p2))

    def mouseReleaseEvent(self, p: QtCore.QPoint):
        self.__eventQueue.put(MouseReleaseEvent(p))

    def processEventQueue(self):
        while not self.__eventQueue.empty():
            evt = self.__eventQueue.get()

            if isinstance(evt, MousePressEvent):
                self.__toolCanvas.markOutdated(self.__toolManager.mousePressEvent(evt.pos))
            elif isinstance(evt, MouseMoveEvent):
                self.__toolCanvas.markOutdated(self.__toolManager.mouseMoveEvent(evt.start, evt.finish))
            elif isinstance(evt, MouseReleaseEvent):
                self.__toolCanvas.markOutdated(self.__toolManager.mouseReleaseEvent(evt.pos))
