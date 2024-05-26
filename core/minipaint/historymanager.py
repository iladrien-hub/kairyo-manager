from abc import ABC, abstractmethod

import numpy as np

from core.minipaint.layers.base import BaseLayer


class HistoryItem(ABC):

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def redo(self):
        pass


class HistoryManager:

    def __init__(self):
        self.history = []
        self.pointer = -1

    def save(self, item: HistoryItem):
        self.history = self.history[:self.pointer + 1]
        self.history.append(item)
        self.pointer += 1

    def undo(self) -> bool:
        if self.pointer < 0:
            return False

        self.history[self.pointer].undo()
        self.pointer -= 1
        return True

    def redo(self) -> bool:
        if self.pointer >= len(self.history) - 1:
            return False

        self.pointer += 1
        self.history[self.pointer].redo()
        return True
