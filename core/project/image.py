import os.path
from typing import TYPE_CHECKING

from ..util.filedict import NamedFileDict, field
from ..vcs import Repository

if TYPE_CHECKING:
    from .project import Project


class ImageMeta(NamedFileDict):
    time_created: float = field()
    time_upscaled: float = field()


class ProjectImage:

    # ----------------------- Constructor ------------------------

    def __init__(self, parent: 'Project', name: str):
        self._name = name
        self._parent = parent

        self._full_path = os.path.join(self._parent.images_dir, self._name)

        os.makedirs(self._full_path, exist_ok=True)

        self._meta = ImageMeta(os.path.join(self._full_path, "meta.json"))
        self._vcs = Repository(self._full_path)

    # ---------------------- Public Methods ----------------------

    def update(self, content: bytes):
        with open(os.path.join(self._full_path, "image.png"), 'wb') as f:
            f.write(content)

    def save_snapshot(self, description: str = ""):
        self._vcs.save_snapshot(description)

    def read_version(self, snapshot: str = None):
        with self._vcs.open_file(os.path.join(self._full_path, "image.png"), snapshot) as f:
            return f.read()

    # ------------------------ Properties ------------------------

    @property
    def meta(self) -> ImageMeta:
        return self._meta

    @property
    def history(self):
        return self._vcs.history
