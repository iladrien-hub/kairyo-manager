import logging

import cv2
import numpy as np

from .base import BaseBrush


class RoundBrush(BaseBrush):

    def createStamp(self) -> np.ndarray:
        hardness = self.hardness()
        diameter = self.size()

        radius = cx = cy = diameter // 2

        x, y = np.meshgrid(np.arange(diameter), np.arange(diameter))
        img = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

        img[img > radius] = radius
        img[img < radius * hardness] = 0

        mask = img > radius * hardness

        img /= np.max(img)
        img = 1 - img

        if np.any(mask):
            img[mask] /= np.max(img[mask])

        img = (img * 255).astype(np.uint8)

        ones = np.ones_like(img) * 255
        img = np.stack([ones, ones, ones, img], axis=-1)

        return img

    def cursor(self, scale: int = 1):
        diameter = int(self.size() * scale)
        radius = max(diameter // 2, 1)

        cursor = np.zeros((diameter, diameter, 4), dtype=np.uint8)
        cv2.circle(cursor, (radius, radius), radius, (255, 255, 255, 255), 1)
        cv2.circle(cursor, (radius, radius), radius - 1, (0, 0, 0, 255), 1)

        return cursor
