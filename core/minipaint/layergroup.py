from typing import Optional, List

from core.minipaint.layers.base import BaseLayer


class LayerGroup:

    def __init__(self):
        self.__layers: List[BaseLayer] = []
        self.__currentLayer: Optional[BaseLayer] = None

    def addLayer(self, layer: BaseLayer):
        if layer not in self.__layers:
            self.__layers.append(layer)

    def removeLayer(self, layer: BaseLayer):
        if layer in self.__layers:
            self.__layers.remove(layer)

    def layers(self):
        return self.__layers

    def layer(self, idx: int):
        return self.__layers[idx]

    def setCurrentLayer(self, layer: BaseLayer):
        if layer not in self.__layers:
            raise ValueError(f"{layer!r} is not a part of {self}")
        self.__currentLayer = layer

    def currentLayer(self) -> BaseLayer:
        return self.__currentLayer
