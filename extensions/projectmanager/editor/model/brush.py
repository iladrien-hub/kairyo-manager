import cv2
import numpy as np


class Brush:
    def __init__(self):
        self.__size = 20
        self.__hardness = 0.5
        self.__stamp = self.createStamp()

    def size(self):
        return self.__size

    def setSize(self, size: int):
        self.__size = max(size, 1)
        self.__stamp = self.createStamp()

    def stamp(self):
        return self.__stamp

    def createStamp(self):
        diameter = self.__size
        radius = cx = cy = diameter // 2

        x, y = np.meshgrid(np.arange(diameter), np.arange(diameter))
        img = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

        img[img > radius] = radius
        img[img < radius * self.__hardness] = 0

        mask = img > radius * self.__hardness

        img /= np.max(img)
        img = 1 - img

        if np.any(mask):
            img[mask] /= np.max(img[mask])

        img = (img * 255).astype(np.uint8).reshape((diameter, diameter, 1))

        return cv2.cvtColor(img.reshape((diameter, diameter, 1)), cv2.COLOR_GRAY2RGBA)
