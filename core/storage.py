from typing import Optional

from PyQt5 import QtCore

from .project import Project, ProjectImage


class KairyoStorage(QtCore.QObject):
    projectChanged = QtCore.pyqtSignal()
    imageChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__project: Optional[Project] = None
        self.__image: Optional[ProjectImage] = None

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, value: Optional[Project]):
        if value != self.__project:
            self.__project = value
            self.projectChanged.emit()
            self.image = None

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value: Optional[ProjectImage]):
        if value != self.__image:
            self.__image = value
            self.imageChanged.emit()
