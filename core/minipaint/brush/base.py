import abc
from abc import ABC

import numpy as np


class BaseBrush(ABC):
    def __init__(self):
        self.__size = 20
        self.__hardness = 0.5
        self.__stamp = self.createStamp()

    def size(self):
        return self.__size

    def setSize(self, size: int):
        self.__size = max(size, 3)
        self.__stamp = self.createStamp()

    def hardness(self):
        return self.__hardness

    def setHardness(self, hardness: float):
        self.__hardness = min(max(hardness, 0), 1)

    def stamp(self):
        return self.__stamp

    @abc.abstractmethod
    def createStamp(self) -> np.ndarray:
        pass

    def cursor(self, scale: int = 1):
        pass
