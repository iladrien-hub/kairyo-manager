from typing import Dict

from core.project import ProjectImage
from editor.model import ImageModel, ImageModelCallbacks


class ImageEditorCache:

    def __init__(self, callbacks: ImageModelCallbacks):
        self.__callbacks = callbacks
        self.__storage: Dict[str, ImageModel] = {}

    def get(self, image: ProjectImage):
        if image.path not in self.__storage:
            self.__storage[image.path] = ImageModel(self.__callbacks, image)
        return self.__storage[image.path]
