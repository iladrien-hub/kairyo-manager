from enum import Enum

from PyQt5 import QtCore


class EditorEvent:
    pass


class MousePressEvent(EditorEvent):
    def __init__(self, pos: QtCore.QPoint):
        self.pos = pos


class MouseMoveEvent(EditorEvent):
    def __init__(self, start: QtCore.QPoint, finish: QtCore.QPoint):
        self.finish = finish
        self.start = start


class MouseReleaseEvent(EditorEvent):
    def __init__(self, pos: QtCore.QPoint):
        self.pos = pos
