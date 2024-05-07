import typing

from PyQt5.QtCore import QSettings

if typing.TYPE_CHECKING:
    from .extension import KairyoExtension
    from .user_interface import UserInterface

from .storage import KairyoStorage


class KairyoApi:
    __instance = None

    def __init__(self, *, user_interface: 'UserInterface'):
        if KairyoApi.__instance:
            raise RuntimeError(f"only one instance of {self.__class__.__name__} can be created")
        KairyoApi.__instance = self

        self.__extensions: typing.List['KairyoExtension'] = []
        self.__user_interface: 'UserInterface' = user_interface
        self.__storage: 'KairyoStorage' = KairyoStorage()
        self.__settings: QSettings = QSettings('config.ini', QSettings.IniFormat)

    def register_extension(self, ext: 'KairyoExtension'):
        self.__extensions.append(ext)

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
