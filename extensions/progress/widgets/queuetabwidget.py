import logging

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from core.api import KairyoApi
from extensions.projectmanager.widgets.history import PreviewGraphicsWidget
from .queuelistwidget import QueueListWidget


class QueueTabWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self._listWidget = QueueListWidget(self)

        self._progres = QtWidgets.QProgressBar(self)
        self._progres.setTextVisible(False)
        self._progres.setVisible(False)

        self._previewWidget = PreviewGraphicsWidget(self)
        self._previewWidget.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self._previewWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._previewWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._previewScene = QtWidgets.QGraphicsScene()
        self._previewPixmapItem = self._previewScene.addPixmap(QtGui.QPixmap())
        self._previewPixmapItem.setTransformationMode(Qt.SmoothTransformation)
        self._previewWidget.setScene(self._previewScene)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self._previewWidget)
        top.addWidget(self._listWidget)
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(0)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addLayout(top)
        layout.addWidget(self._progres)

        self.setLayout(layout)

        api = KairyoApi.instance()
        api.worker.callbacks.progress.connect(self.on_workerCallbacks_progress)
        api.worker.callbacks.progressImage.connect(self.on_workerCallbacks_progressImage)

    def on_workerCallbacks_progress(self, val: int):
        self._progres.setVisible(val != 0)
        self._progres.setValue(val)

    def on_workerCallbacks_progressImage(self, val: bytes):
        pixmap = QtGui.QPixmap()
        if val:
            pixmap.loadFromData(val)

        self._previewPixmapItem.setPixmap(pixmap)
        self._previewWidget.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self._previewWidget.fitInView(self._previewPixmapItem, Qt.KeepAspectRatio)
