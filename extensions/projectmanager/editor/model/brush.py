import cv2
import numpy as np


class Brush:
    def __init__(self):
        self.__size = 20
        self.__stamp = self.createStamp()

    def size(self):
        return self.__size

    def setSize(self, size: int):
        self.__size = max(size, 1)
        self.__stamp = self.createStamp()

    def stamp(self):
        return self.__stamp

    def createStamp(self):
        stamp = np.zeros((self.__size, self.__size, 4), dtype=np.uint8)
        cv2.circle(stamp, (self.__size // 2, self.__size // 2), self.__size // 2, (255, 255, 255, 255), -1)
        cv2.blur(stamp, (3, 3))

        return stamp
