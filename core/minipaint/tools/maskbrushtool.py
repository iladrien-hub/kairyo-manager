from PyQt5 import QtCore

from .brushtool import BrushTool, BrushToolHistoryItem
from ..layers.maskablelayer import MaskableLayer


class MaskBrushTool(BrushTool):
    def mouseReleaseEvent(self, p: QtCore.QPoint) -> bool:
        editor = self.editor()

        layer = editor.currentLayer()
        if not isinstance(layer, MaskableLayer):
            return False

        layer = layer.mask()
        pixels = layer.pixelData()

        if pixels is not None:
            result = self.apply(pixels, self._buffer)
            layer.setPixelData(result)
            editor.imageCanvas().markOutdated(True)
            editor.history().save(BrushToolHistoryItem(
                layer,
                pixels,
                result
            ))

        self._buffer = self.newBuffer()
        return True
