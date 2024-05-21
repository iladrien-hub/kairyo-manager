import io
import json
import os
import time
from typing import Union, Dict

from PIL import Image

from core.project.image import ProjectImage
from core.util.filedict import NamedFileDict, field
from core.util.params import parse_generation_parameters


class ProjectMeta(NamedFileDict):
    name: str = field(default="")
    time_created: float = field(default=0)

    character: str = field(default="")
    use_character_from_lora: bool = field(default=False)

    use_custom_source_type: bool = field(default=False)
    source_type: str = field(default="")
    custom_source_type: str = field(default="")
    source: str = field(default="")

    description: str = field(default="")


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
        if self._meta.time_created == 0:
            self._meta.time_created = time.time()

    def create_image(self, name: str):
        if name in self._images:
            raise ValueError(f"image with name \"{name}\" already exists")

        image = ProjectImage(self, name)
        image.meta.time_created = time.time()

        return image

    def add_image(self, name: str, data: bytes, params: dict = None):
        if not params:
            with io.BytesIO(data) as buffer:
                pil = Image.open(buffer)
                params = parse_generation_parameters(pil.info['parameters'])

        image = self.create_image(name)
        image.meta.time_created = time.time()
        image.params = params

        image.update(content=data)
        image.save_snapshot(description="initial")

        return image

    def get_image(self, name: str):
        return self._images[name]

    def images(self):
        return list(self._images.keys())

    def next(self, **tags):
        ret = next(filter(lambda x: all(x[1].has_tag(t) == v for t, v in tags.items()), self._images.items()), None)
        if ret:
            return ret[0]

    @property
    def root_dir(self):
        return self._root_dir

    @property
    def images_dir(self):
        return self._images_dir

    @property
    def meta(self) -> ProjectMeta:
        return self._meta
