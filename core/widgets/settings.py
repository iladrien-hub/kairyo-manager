from typing import Optional, Any

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy

from .fileinput import FileInput
from .slider import FancySlider


class SettingCallbacks(QtCore.QObject):
    settingChanged = QtCore.pyqtSignal()


class Setting(QtCore.QObject):
    _defaultValue: Any

    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.key = key
        self._callbacks: Optional[SettingCallbacks] = None
        self._settings: Optional[QtCore.QSettings] = None
        self._default: Any = self.defaultFactory()

        self.init()

    def setCallbacks(self, v: SettingCallbacks):
        self._callbacks = v

    def setSettings(self, v: QtCore.QSettings):
        self._settings = v

    def setDefault(self, v: Any):
        self._default = v

    def defaultFactory(self):
        return None

    def emit_settingChanged(self):
        if self._callbacks:
            self._callbacks.settingChanged.emit()

    def init(self):
        raise NotImplementedError()

    def value(self) -> Any:
        raise NotImplementedError()

    def changed(self) -> bool:
        raise NotImplementedError()

    def restore(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()


class TextSetting(QtWidgets.QLineEdit, Setting):

    def init(self):
        self.textChanged.connect(self.emit_settingChanged)  # noqa

    def value(self) -> str:
        return self.text()

    def changed(self) -> bool:
        return self._settings.value(self.key, self._default) != self.text()

    def restore(self):
        self.setText(self._settings.value(self.key, self._default))

    def save(self):
        self._settings.setValue(self.key, self.text())

    def defaultFactory(self):
        return ''


class MultilineTextSetting(QtWidgets.QTextEdit, Setting):

    def init(self):
        self.textChanged.connect(self.emit_settingChanged)

    def value(self) -> Any:
        return self.toPlainText()

    def changed(self) -> bool:
        return self.toPlainText() != self._settings.value(self.key, self._default)

    def restore(self):
        self.setText(self._settings.value(self.key, self._default))

    def save(self):
        self._settings.setValue(self.key, self.toPlainText())

    def defaultFactory(self):
        return ''


class NumberSetting(Setting):
    pass


class SliderSetting(FancySlider, Setting):
    def init(self):
        self.valueChanged.connect(self.emit_settingChanged)

    def changed(self) -> bool:
        return self.value() != self._settings.value(self.key, self._default, float)

    def restore(self):
        self.setValue(self._settings.value(self.key, self._default, float))

    def save(self):
        self._settings.setValue(self.key, self.value())

    def defaultFactory(self):
        return 0


class BooleanSetting(QtWidgets.QCheckBox, Setting):

    def init(self):
        self.stateChanged.connect(self.emit_settingChanged)

    def value(self) -> Any:
        return self.isChecked()

    def changed(self) -> bool:
        return self.isChecked() != self._settings.value(self.key, self._default, bool)

    def restore(self):
        self.setChecked(self._settings.value(self.key, self._default, bool))

    def save(self):
        self._settings.setValue(self.key, self.isChecked())

    def defaultFactory(self):
        return False


class ListSetting(Setting):
    pass


class OptionsSetting(QtWidgets.QComboBox, Setting):
    def __init__(self, key: str, *args, **kwargs):
        super().__init__(*args, key=key, **kwargs)
        self.setItemDelegate(QtWidgets.QStyledItemDelegate(self))

    def init(self):
        self.currentTextChanged.connect(self.emit_settingChanged)

    def value(self) -> Any:
        return self.currentText()

    def changed(self) -> bool:
        return self.currentText() != self._settings.value(self.key, self._default)

    def restore(self):
        value = self._settings.value(self.key, self._default)
        if value is not None:
            self.setCurrentText(value)

    def save(self):
        self._settings.setValue(self.key, self.value())

    def defaultFactory(self):
        return None


class FileSetting(FileInput, TextSetting):

    def defaultFactory(self):
        return ""
