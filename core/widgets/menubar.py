from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy

from core.styling import make_stylesheet, Style


class MenuBar(QtWidgets.QMenuBar):
    _STYLE = make_stylesheet([
        Style('QMenuBar::item', {
            'color': '#cacaca'
        }),
        Style('QMenuBar::item:selected, QMenuBar::item:pressed', {
            'background-color': '#4b6eaf'
        }),
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet(self._STYLE)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
