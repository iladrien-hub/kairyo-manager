import typing

from PyQt5.QtCore import QSettings, Qt

if typing.TYPE_CHECKING:
    from .extension import KairyoExtension
    from .user_interface import UserInterface

from .storage import KairyoStorage


class KairyoApi:

    def __init__(self, *, user_interface: 'UserInterface'):
        self.__extensions: typing.List['KairyoExtension'] = []
        self.__user_interface: 'UserInterface' = user_interface
        self.__storage: 'KairyoStorage' = KairyoStorage()
        self.__settings: QSettings = QSettings('config.ini', QSettings.IniFormat)

    def register_extension(self, ext: 'KairyoExtension'):
        self.__extensions.append(ext)

    @property
    def extensions(self):
        return self.__extensions

    @property
    def user_interface(self):
        return self.__user_interface

    @property
    def settings(self):
        return self.__settings
