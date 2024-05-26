from typing import List, Optional

from PyQt5 import QtCore

from core.minipaint.tools.base import BaseTool


class ToolManager:

    def __init__(self):
        self.__tools: List[BaseTool] = []
        self.__activeTool: Optional[BaseTool] = None

    def addTool(self, tool: BaseTool):
        if tool not in self.__tools:
            self.__tools.append(tool)

    def setActiveTool(self, tool: Optional[BaseTool]):
        if tool is None or tool in self.__tools:
            self.__activeTool = tool

    def activeTool(self):
        return self.__activeTool

    def mousePressEvent(self, p: QtCore.QPoint):
        if self.__activeTool is not None:
            return self.__activeTool.mousePressEvent(p)

    def mouseMoveEvent(self, p1: QtCore.QPoint, p2: QtCore.QPoint):
        if self.__activeTool is not None:
            return self.__activeTool.mouseMoveEvent(p1, p2)

    def mouseReleaseEvent(self, p: QtCore.QPoint):
        if self.__activeTool is not None:
            return self.__activeTool.mouseReleaseEvent(p)
