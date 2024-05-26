from abc import ABC

from PyQt5 import QtCore

from core.minipaint.layers.base import BaseLayer
from core.minipaint.layers.masklayer import MaskLayer


class MaskableLayer(BaseLayer, ABC):

    def __init__(self, size: QtCore.QSize):
        super().__init__(size)
        self.__mask: MaskLayer = MaskLayer(size)

    def mask(self):
        return self.__mask

    def setMask(self, mask: MaskLayer):
        self.__mask = mask
