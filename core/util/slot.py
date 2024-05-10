import functools
import logging

from PyQt5 import QtCore


def safeSlot(*args, suppress=None, **kwargs):
    def _decor(func):
        slot = QtCore.pyqtSlot(*args, **kwargs)

        @functools.wraps(func)
        def _foo(*a, **kw):
            try:
                return func(*a, **kw)
            except BaseException as e:
                logging.error("", exc_info=e)
                if not suppress or not isinstance(e, suppress):
                    raise

        return slot(_foo)

    return _decor
