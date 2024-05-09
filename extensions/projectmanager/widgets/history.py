import time
from datetime import datetime
from typing import Optional

from PyQt5 import QtWidgets, QtCore

from core.project import ProjectImage


class SnapshotItemWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._label = QtWidgets.QLabel()
        self._label.setText('hello!')
        self._label.setFixedHeight(24)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self._label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

    def setText(self, text: str):
        self._label.setText(text)

    def setProperty(self, name, value):
        ret = super(SnapshotItemWidget, self).setProperty(name, value)
        self.style().unpolish(self._label)
        self.style().polish(self._label)

        return ret


class ImageHistoryWidget(QtWidgets.QFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._commitsList = QtWidgets.QListWidget(self)
        self._commitsList.setObjectName('commitsList')

        self._image: Optional[ProjectImage] = None

        # self.addItem("89af261", time.time(), '*(projectmanager): sorting orders', True)
        # self.addItem("89af261", time.time() - 3600 * 4, '*(projectmanager): sorting orders', False)

        self._layout.addWidget(self._commitsList)
        self.setLayout(self._layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    def syncList(self):
        self._commitsList.clear()

        if not self._image:
            return

        head = self._image.head
        for item in self._image.history:
            self.addItem(item['hash'], item['timestamp'], item['description'], item['hash'] == head)

    def addItem(self, snapshot_hash: str, timestamp: float, title: str, is_head: bool):
        item = QtWidgets.QListWidgetItem()
        w = SnapshotItemWidget(self)

        item.setSizeHint(w.sizeHint())

        time_dt = datetime.fromtimestamp(timestamp)
        time_fmt = "Today %H:%M" if time_dt.date() == datetime.today().date() else "%m/%d/%Y %H:%M"
        time_str = time_dt.strftime(time_fmt)
        label = f'\u2022 <b style="color: #ADCACB">{snapshot_hash[-8:]}</b> - ' \
                f'<b style="color: #42f56e">{time_str}</b> ' \
                f'{title}'

        if is_head:
            label += ' <b style="color: #FAD074">(HEAD)</b>'

        w.setText(label)

        self._commitsList.addItem(item)
        self._commitsList.setItemWidget(item, w)

    def updateItemsProperties(self):
        selected = self._commitsList.selectedItems()

        for i in range(self._commitsList.count()):
            item = self._commitsList.item(i)
            widget = self._commitsList.itemWidget(item)

            widget.setProperty('selected', item in selected)

    def setImage(self, v: Optional[ProjectImage]):
        if self._image != v:
            self._image = v
            self.syncList()

    def on_commitsList_itemSelectionChanged(self):
        self.updateItemsProperties()
