import os
import time
from typing import Union, Dict

from core.project.image import ProjectImage
from core.util.filedict import NamedFileDict, field


class ProjectMeta(NamedFileDict):
    name: str = field(default="")


class Project:

    def __init__(self, path: Union[str, os.PathLike]):
        self._root_dir = os.path.abspath(path)
        self._images_dir = os.path.join(self._root_dir, "images")

        os.makedirs(self._root_dir, exist_ok=True)
        os.makedirs(self._images_dir, exist_ok=True)

        self._images: Dict[str, ProjectImage] = dict()
        for dir_name in os.listdir(self._images_dir):
            self._images[dir_name] = ProjectImage(self, dir_name)

        self._meta = ProjectMeta(os.path.join(self._root_dir, 'project.meta.json'))

    def create_image(self, name: str):
        if name in self._images:
            raise ValueError(f"image with name \"{name}\" already exists")

        image = ProjectImage(self, name)
        image.meta.time_created = time.time()

        return image

    def get_image(self, name: str):
        return self._images[name]

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def images_dir(self):
        return self._images_dir

    @property
    def meta(self) -> ProjectMeta:
        return self._meta
