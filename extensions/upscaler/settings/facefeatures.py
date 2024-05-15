from PyQt5 import QtWidgets

from core.widgets.settings import ListSetting
from .settings import AD_FACE_FEATURES


class FaceFeaturesSettings(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._list = ListSetting(AD_FACE_FEATURES)

        self._layout.addWidget(self._list)
        self.setLayout(self._layout)
