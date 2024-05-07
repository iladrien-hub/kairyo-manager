import os
import time
from typing import Union, Callable, Any

import ujson

_MISSING = object()


class field:  # noqa

    def __init__(self, *, default: Any = _MISSING, default_factory: Callable = _MISSING):
        if default is not _MISSING and default_factory is not _MISSING:
            raise ValueError('cannot specify both default and default_factory')

        self._default = default
        self._default_factory = default_factory
        self._name = None
        self._type = None

    def __get__(self, instance, owner):
        try:
            return instance[self._name]
        except KeyError:
            if self._default is not _MISSING:
                instance[self._name] = self._default
                return instance[self._name]
            if self._default_factory is not _MISSING:
                instance[self._name] = self._default_factory()
                return instance[self._name]
            raise

    def __set__(self, instance, value):
        if not isinstance(value, self._type):
            raise ValueError(f"{value!r} is not of type {self._type}")
        instance[self._name] = value

    def __set_name__(self, owner, name):
        self._name = name


class FileDict:

    def __init__(self, fn: Union[str, os.PathLike]):
        self._fn = fn
        self._last_access = None
        self._data = dict()

        if not os.path.isfile(self._fn):
            self.__dump()

    def __dump(self):
        with open(self._fn, "w", encoding="utf-8") as f:
            ujson.dump(self._data, f)
        self._last_access = time.time()

    def __load(self):
        if self._last_access is None or self._last_access < os.path.getmtime(self._fn):
            with open(self._fn, 'r', encoding="utf-8") as f:
                try:
                    self._data = ujson.load(f)
                except Exception as e:
                    raise Exception(self._fn) from e
            self._last_access = time.time()
        return self._data

    def __setitem__(self, key, value):
        self.__load().__setitem__(key, value)
        self.__dump()

    def __getitem__(self, item):
        return self.__load()[item]

    def __repr__(self):
        return f"FileDict<{self.__load().__repr__()}>"

    @property
    def path(self):
        return self._fn


class NamedFileDictMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls_annotations = attrs.get('__annotations__', {})
        cls_fields = {}

        for k, v in cls_annotations.items():
            if k in attrs:
                cls_fields[k] = attrs[k]
            else:
                cls_fields[k] = field()
            setattr(cls_fields[k], '_type', v)

        missing = set(k for k, v in attrs.items() if isinstance(v, field)) - set(cls_fields)
        if missing:
            raise TypeError(f'{missing!r} is a field(s) but has no type annotation')

        attrs.update(cls_fields)
        return super().__new__(mcs, name, bases, attrs)


class NamedFileDict(FileDict, metaclass=NamedFileDictMeta):
    pass
