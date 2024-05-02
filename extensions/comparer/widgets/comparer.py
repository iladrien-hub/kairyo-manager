from typing import TYPE_CHECKING, Optional

from PyQt5 import QtWidgets, QtGui

from .window import ComparerWindowWidget

if TYPE_CHECKING:
    from core.project.image import ProjectImage


class ComparerWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._image: Optional['ProjectImage'] = None

        self._cb_left = QtWidgets.QComboBox()
        self._cb_right = QtWidgets.QComboBox()

        cb_layout = QtWidgets.QHBoxLayout()
        cb_layout.addWidget(self._cb_left)
        cb_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        cb_layout.addWidget(self._cb_right)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(cb_layout)

        self._window = ComparerWindowWidget()
        self._window.setMinimumSize(480, 640)

        layout.addWidget(self._window)
        self.setLayout(layout)

        self._cb_left.currentTextChanged.connect(self.handle_left_option_change)
        self._cb_right.currentTextChanged.connect(self.handle_right_option_change)

    def set_image(self, image: 'ProjectImage'):
        self._image = image

        self._cb_right.clear()
        self._cb_left.clear()

        self._cb_left.addItem(f"local", None)
        self._cb_right.addItem(f"local", None)

        for item in image.history:
            self._cb_left.addItem(f"[{item['hash'][:8]}] {item['description']}", item['hash'])
            self._cb_right.addItem(f"[{item['hash'][:8]}] {item['description']}", item['hash'])

    def handle_left_option_change(self):
        snapshot_hash = self._cb_left.currentData()
        image_data = self._image.read_version(snapshot_hash)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_data)

        self._window.set_left(pixmap)

    def handle_right_option_change(self):
        snapshot_hash = self._cb_right.currentData()
        image_data = self._image.read_version(snapshot_hash)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(image_data)

        self._window.set_right(pixmap)
