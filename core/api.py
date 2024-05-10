import logging
import os
import typing

from PyQt5.QtCore import QSettings

from .project import Project
from .worker import Worker

if typing.TYPE_CHECKING:
    from .extension import KairyoExtension
    from .user_interface import UserInterface
    from .styling.theme import DarkTheme

from .storage import KairyoStorage


class KairyoApi:
    __instance = None

    def __init__(self, *, user_interface: 'UserInterface', theme: 'DarkTheme'):
        if KairyoApi.__instance:
            raise RuntimeError(f"only one instance of {self.__class__.__name__} can be created")
        KairyoApi.__instance = self

        self.__extensions: typing.List['KairyoExtension'] = []
        self.__user_interface: 'UserInterface' = user_interface
        self.__storage: 'KairyoStorage' = KairyoStorage()
        self.__settings: QSettings = QSettings('config.ini', QSettings.IniFormat)
        self.__theme: 'DarkTheme' = theme
        self.__worker: Worker = Worker()

    def register_extension(self, ext: 'KairyoExtension'):
        self.__extensions.append(ext)

    def open_project(self, fn: typing.Union[str, os.PathLike]):
        self.__storage.project = Project(fn)
        self.__settings.setValue('openProject/lastProject', fn)

    def open_last_project(self):
        fn = self.__settings.value('openProject/lastProject', None)
        if fn and os.path.isdir(fn):
            self.open_project(fn)

    @classmethod
    def instance(cls) -> 'KairyoApi':
        return cls.__instance

    @property
    def extensions(self):
        return self.__extensions

    @property
    def user_interface(self):
        return self.__user_interface

    @property
    def settings(self):
        return self.__settings

    @property
    def theme(self):
        return self.__theme

    @property
    def storage(self):
        return self.__storage

    @property
    def worker(self):
        return self.__worker
