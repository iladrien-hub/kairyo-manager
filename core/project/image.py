import os.path
import shutil
from typing import TYPE_CHECKING

import ujson

from ..util.filedict import NamedFileDict, field
from ..vcs import Repository

if TYPE_CHECKING:
    from .project import Project


class ImageMeta(NamedFileDict):
    time_created: float = field()
    time_upscaled: float = field()
    tags: list = field(default_factory=list)


class ProjectImage:

    # ----------------------- Constructor ------------------------

    def __init__(self, parent: 'Project', name: str):
        self._name = name
        self._parent = parent

        self._full_path = os.path.join(self._parent.images_dir, self._name)
        self._image_path = os.path.join(self._full_path, "image.png")

        os.makedirs(self._full_path, exist_ok=True)

        self._meta = ImageMeta(os.path.join(self._full_path, "meta.json"))
        self._vcs = Repository(self._full_path)
        self._params = None

    # ---------------------- Public Methods ----------------------

    def delete(self):
        shutil.rmtree(self._full_path)

    def update(self, content: bytes):
        with open(self._image_path, 'wb') as f:
            f.write(content)

    def save_snapshot(self, description: str = ""):
        self._vcs.save_snapshot(description)

    def read_version(self, snapshot: str = None):
        return self.read_file("image.png", snapshot)

    def read_file(self, fn: str, snapshot: str = None):
        with self._vcs.open_file(os.path.join(self._full_path, fn), snapshot) as f:
            return f.read()

    def add_tag(self, tag: str):
        if not self.has_tag(tag):
            with self._meta:
                self._meta.tags.append(tag)

    def remove_tag(self, tag: str):
        if self.has_tag(tag):
            with self._meta:
                self._meta.tags.remove(tag)

    def has_tag(self, tag: str):
        return tag in self._meta.tags

    # ------------------------ Properties ------------------------

    @property
    def vcs(self):
        return self._vcs

    @property
    def meta(self) -> ImageMeta:
        return self._meta

    @property
    def history(self):
        return self._vcs.history

    @property
    def head(self):
        return self._vcs.current

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._full_path

    @property
    def params(self):
        if self._params is None:
            with open(os.path.join(self._full_path, 'params.json'), 'r', encoding='utf-8') as f:
                self._params = ujson.load(f)

        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        with open(os.path.join(self._full_path, 'params.json'), 'w', encoding='utf-8') as f:
            ujson.dump(self._params, f)

    @property
    def mtime(self):
        return os.path.getmtime(self._image_path)
