import hashlib
import logging
import os.path
import pickle
import time
from typing import Optional, Dict, BinaryIO, Union

import ujson

from core.util.filedict import NamedFileDict, field


class RepositoryMeta(NamedFileDict):
    head: Optional[str] = field(default=None)
    current: Optional[str] = field(default=None)


class Repository:
    _VCS_DIRNAME = ".vcs"
    _SNAPSHOTS_DIR = os.path.join(_VCS_DIRNAME, "snapshots")
    _BLOBS_DIR = os.path.join(_VCS_DIRNAME, "blobs")

    # ----------------------- Constructor ------------------------

    def __init__(self, path: str):
        self._path = os.path.abspath(path)

        self._vcs_path = os.path.join(self._path, self._VCS_DIRNAME)
        self._snapshots_path = os.path.join(self._path, self._SNAPSHOTS_DIR)
        self._blobs_path = os.path.join(self._path, self._BLOBS_DIR)
        self._snapshots: Dict[str, dict] = {}

        os.makedirs(self._vcs_path, exist_ok=True)
        os.makedirs(self._snapshots_path, exist_ok=True)
        os.makedirs(self._blobs_path, exist_ok=True)

        self.meta = RepositoryMeta(os.path.join(self._vcs_path, "repository.json"))
        self._load_history()

    # ---------------------- Public Methods ----------------------

    def has_unsaved(self):
        snapshot_data = {
            'tree': {},
        }

        for root, _, files in os.walk(self._path):
            if self._VCS_DIRNAME in root:
                continue

            for basename in files:
                fn = os.path.join(root, basename)

                with open(fn, 'rb') as f:
                    data = f.read()

                file_id = hashlib.sha256(data).hexdigest()
                snapshot_data['tree'][fn] = file_id

        if self.meta.current:
            current = self._snapshots[self.meta.current]
            return set(current['tree'].items()) != set(snapshot_data['tree'].items())

        return True

    def save_snapshot(self, description: str = ""):
        snapshot_hash = hashlib.sha256()
        snapshot_data = {
            'tree': {},
            'description': description,
            'parent': self.meta.current
        }

        for root, _, files in os.walk(self._path):
            if self._VCS_DIRNAME in root:
                continue

            for basename in files:
                fn = os.path.join(root, basename)

                with open(fn, 'rb') as f:
                    data = f.read()

                snapshot_hash.update(data)

                file_id = hashlib.sha256(data).hexdigest()
                snapshot_data['tree'][fn] = file_id

                blob_fn = os.path.join(self._blobs_path, file_id)
                if not os.path.isfile(blob_fn):
                    with open(blob_fn, 'wb') as f:
                        f.write(data)

        if self.meta.current:
            current = self._snapshots[self.meta.current]
            if set(current['tree'].items()) == set(snapshot_data['tree'].items()):
                logging.warning("nothing to commit")
                return

        snapshot_hash.update(ujson.dumps(snapshot_data).encode("utf-8"))
        snapshot_hash = snapshot_hash.hexdigest()

        snapshot_data['hash'] = snapshot_hash
        snapshot_data['timestamp'] = time.time()

        with open(os.path.join(self._snapshots_path, snapshot_hash), 'wb') as f:
            pickle.dump(snapshot_data, f)

        self.meta.current = snapshot_hash
        self._snapshots[snapshot_hash] = snapshot_data

    def load_snapshot(self, snapshot_hash: str):
        if self.meta.current == snapshot_hash and not self.has_unsaved():
            logging.warning(f"currently at '{snapshot_hash}'")
            return

        snapshot_data = self._snapshots[snapshot_hash]

        for fn, file_id in snapshot_data['tree'].items():
            with (
                open(os.path.join(self._blobs_path, file_id), 'rb') as f_in,
                open(fn, 'wb') as f_out,
            ):
                for chunk in self.read_big(f_in):
                    f_out.write(chunk)

        existing_files = set()
        for root, _, files in os.walk(self._path):
            if self._VCS_DIRNAME in root:
                continue
            for basename in files:
                existing_files.add(os.path.join(root, basename))

        files_to_remove = existing_files - set(snapshot_data['tree'].keys())
        for fn in files_to_remove:
            os.unlink(fn)

        self.meta.current = snapshot_hash

    def open_file(self, fn: str, snapshot_hash: str = None):
        fn = self.normpath(fn)
        if snapshot_hash:
            snapshot_data = self._snapshots[snapshot_hash]
            try:
                file = os.path.join(self._blobs_path, snapshot_data['tree'][fn])
            except KeyError as e:
                raise FileNotFoundError(fn) from e
        else:
            file = fn

        return open(file, 'rb')

    # -------------- Protected and Private Methods ---------------

    def _load_history(self):
        for snapshot in os.listdir(self._snapshots_path):
            fn = os.path.join(self._snapshots_path, snapshot)
            with open(fn, 'rb') as f:
                self._snapshots[snapshot] = pickle.load(f)

    # ---------------------- Static Methods ----------------------

    # ------------------------ Properties ------------------------

    @property
    def history(self):
        return sorted(self._snapshots.values(), key=lambda x: x['timestamp'], reverse=True)

    @property
    def current(self):
        return self.meta.current

    # ---------------------- Helper Methods ----------------------

    @staticmethod
    def read_big(f: BinaryIO, chunk_size=4096):
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data

    @staticmethod
    def normpath(path: Union[str, os.PathLike]):
        return os.path.abspath(os.path.realpath(path))
