import json
import logging
from datetime import datetime
from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from core.project import ProjectImage

from pygments import highlight, lexers, formatters


class PreviewGraphicsWidget(QtWidgets.QGraphicsView):
    pass


class HistoryInfoBox(QtWidgets.QTextEdit):
    pass


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

        self._previewWidget = PreviewGraphicsWidget(self)
        self._previewWidget.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        self._previewScene = QtWidgets.QGraphicsScene()
        self._previewPixmapItem = self._previewScene.addPixmap(QtGui.QPixmap())
        self._previewPixmapItem.setTransformationMode(Qt.SmoothTransformation)
        self._previewWidget.setScene(self._previewScene)

        self._infoBox = HistoryInfoBox(self)
        self._infoBox.setReadOnly(True)
        self._infoFormatter = formatters.HtmlFormatter(full=True, style='stata-dark', nobackground=True)

        self._infoBoxCss = self._infoFormatter.get_style_defs('.highlight')

        self._image: Optional[ProjectImage] = None

        self._layout.addWidget(self._infoBox)
        self._layout.addWidget(self._commitsList)
        self._layout.addWidget(self._previewWidget)
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
        item.setData(Qt.UserRole, snapshot_hash)

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

        if is_head:
            self._commitsList.setCurrentItem(item)

    def updateItemsProperties(self):
        selected = self._commitsList.selectedItems()

        for i in range(self._commitsList.count()):
            item = self._commitsList.item(i)
            widget = self._commitsList.itemWidget(item)

            widget.setProperty('selected', item in selected)

    def updatePreview(self):
        try:
            item = self._commitsList.selectedItems()
            if not item:
                self._previewPixmapItem.setPixmap(QtGui.QPixmap())
                self._infoBox.clear()
            else:
                item = item[0]
                snapshot_hash = item.data(Qt.UserRole)

                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(self._image.read_version(snapshot_hash))

                self._previewPixmapItem.setPixmap(pixmap)
                self._previewWidget.setSceneRect(0, 0, pixmap.width(), pixmap.height())
                self._previewWidget.fitInView(self._previewPixmapItem, Qt.KeepAspectRatio)

                meta = self._image.read_file("meta.json", snapshot_hash)
                meta = json.loads(meta)
                meta = dict(sorted(meta.items(), key=lambda x: x[0]))
                meta = json.dumps(meta, ensure_ascii=False, indent=4)
                meta = highlight(meta, lexers.JsonLexer(), self._infoFormatter)

                self._infoBox.setText(f"<style>{self._infoBoxCss}</style>{meta}")

        except BaseException as e:
            logging.error("", exc_info=e)

    def setImage(self, v: Optional[ProjectImage]):
        if self._image != v:
            self._image = v
            self.syncList()

    def resizeEvent(self, a0):
        self._previewWidget.fitInView(self._previewPixmapItem, Qt.KeepAspectRatio)
        return super(ImageHistoryWidget, self).resizeEvent(a0)

    def on_commitsList_itemSelectionChanged(self):
        self.updateItemsProperties()
        self.updatePreview()
