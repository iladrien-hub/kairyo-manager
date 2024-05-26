from threading import Lock
from typing import TYPE_CHECKING

from PyQt5 import QtCore

from core.project import ProjectImage
from .layergroup import LayerGroup
from .layers.imagelayer import ImageLayer
from .. import imutils

if TYPE_CHECKING:
    from .editor import ImageEditor


class Document:

    def __init__(self, editor: 'ImageEditor', image: ProjectImage):
        self.__editor = editor
        self.__image = image

        image_data = imutils.bytes_to_cv2(self.__image.read_version())
        self.__size = QtCore.QSize(image_data.shape[1], image_data.shape[0])

        layer = ImageLayer(self.__size)
        layer.setPixelData(image_data)

        self.__layers = LayerGroup()
        self.__layers.addLayer(layer)
        self.__layers.setCurrentLayer(layer)

        self.__reloadLock = Lock()
        self.__lastMtime = self.__image.mtime

    def size(self):
        return self.__size

    def reloadFromDisk(self):
        with self.__reloadLock:
            if self.__lastMtime == self.__image.mtime:
                return

            self.__lastMtime = self.__image.mtime

            image_data = imutils.bytes_to_cv2(self.__image.read_version())
            new_size = QtCore.QSize(image_data[1], image_data[0])

            if new_size != self.__size:
                pass  # TODO: clear history, reset size, reset all tools
            else:
                pass
