import cv2
import numpy as np
from PyQt5 import QtCore

from core.minipaint.tools.brushtool import BrushTool


class HealingBrushTool(BrushTool):

    def __init__(self, size: QtCore.QSize):
        super().__init__(size)

        self.brush().setHardness(0.8)
        self.setColor(np.array([[1, 0, 0, 0.5]]))

    def apply(self, hh1, hh2):
        mask = (hh2[..., -1] * 2).clip(0, 255)  # from [0, 127] to [0, 255]

        hh1 = cv2.cvtColor(hh1, cv2.COLOR_RGBA2BGR)
        result = cv2.inpaint(hh1, mask, 3, cv2.INPAINT_TELEA)

        return cv2.cvtColor(result, cv2.COLOR_BGR2RGBA)
