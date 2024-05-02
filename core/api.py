import typing

if typing.TYPE_CHECKING:
    from .extension import KairyoExtension
    from .user_interface import UserInterface


class KairyoApi:

    def __init__(self, *, user_interface: 'UserInterface'):
        self.__extensions: typing.List['KairyoExtension'] = []
        self.__user_interface: 'UserInterface' = user_interface

    def register_extension(self, ext: 'KairyoExtension'):
        self.__extensions.append(ext)

    @property
    def extensions(self):
        return self.__extensions

    @property
    def user_interface(self):
        return self.__user_interface
