import keyboard
from PyQt5 import QtCore


class KeyboardManager(QtCore.QObject):
    __instance: 'KeyboardManager' = None

    ShiftEnter_Signal = QtCore.pyqtSignal()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        super().__init__()

        keyboard.add_hotkey("Shift+Enter", self.ShiftEnter_Signal.emit, suppress=True)
