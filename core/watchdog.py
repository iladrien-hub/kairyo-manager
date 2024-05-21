import time
from threading import Thread
from typing import Optional, TYPE_CHECKING

from PyQt5 import QtCore

if TYPE_CHECKING:
    from .api import KairyoApi


class Watchdog(QtCore.QObject):
    fileChanged = QtCore.pyqtSignal(str)

    def __init__(self, api: 'KairyoApi'):
        super().__init__()

        self.__api = api
        self.__thread: Optional[Thread] = None
        self.__is_running = False

    def _run(self):
        self.__is_running = True

        mtime = {}

        while self.__is_running:
            try:
                project = self.__api.storage.project
                if project is None:
                    continue

                for image in project.images():
                    image = project.get_image(image)

                    if image.path not in mtime:
                        mtime[image.path] = image.mtime
                    elif mtime[image.path] < image.mtime:
                        self.fileChanged.emit(image.name)
                        mtime[image.path] = image.mtime
            finally:
                time.sleep(0.05)

    def start(self):
        if self.__thread is not None:
            return

        self.__thread = Thread(target=self._run)
        self.__thread.start()

    def stop(self):
        self.__is_running = False
        self.__thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
