import logging
import queue
from typing import List, Optional

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread

from core.api import KairyoApi
from core.project import ProjectImage
from core.styling.icon import load_icon


class ImageListItem(QtWidgets.QListWidgetItem):

    def __init__(self, icon: QtGui.QIcon, name: str, image: ProjectImage):
        super().__init__(icon, name)
        self.image = image

    def __lt__(self, other: 'ImageListItem'):
        return self.text() < other.text()


class ImageList(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.verticalScrollBar().setSingleStep(20)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def updateGeometries(self) -> None:
        super().updateGeometries()
        self.verticalScrollBar().setSingleStep(20)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def selectedItems(self) -> List[ImageListItem]:
        return super(ImageList, self).selectedItems()  # noqa

    def currentItem(self) -> Optional[ImageListItem]:
        return super(ImageList, self).currentItem()  # noqa

    def item(self, row: int) -> Optional[ImageListItem]:
        return super(ImageList, self).item(row)


class ImageLoader(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self._queue = queue.Queue()

    def schedule(self, image: ProjectImage, list_widget: QtWidgets.QListWidget):
        self._queue.put((image, list_widget))

    def run(self):
        while True:
            try:
                image, list_widget = self._queue.get()

                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(image.read_version())

                item = ImageListItem(QtGui.QIcon(pixmap), image.name, image)
                list_widget.addItem(item)
                list_widget.sortItems()

            except BaseException as e:
                logging.error("", e)


class ImageListToolbar(QtWidgets.QFrame):
    def __init__(self, parent, list_widget: ImageList):
        super().__init__(parent)

        self._listWidget = list_widget
        self._scrollToCurrent = QtWidgets.QToolButton(self)
        self._scrollToCurrent.setIcon(load_icon(
            ':/projectmanager/crosshairs-simple.svg',
            KairyoApi.instance().theme.text_200
        ))
        self._scrollToCurrent.setIconSize(QtCore.QSize(13, 13))
        self._scrollToCurrent.setFixedSize(21, 21)
        self._scrollToCurrent.setToolTip("Scroll to Selected File")
        self._scrollToCurrent.clicked.connect(self.on_scrollToCurrent_clicked)

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self._scrollToCurrent)

        layout.setContentsMargins(2, 2, 2, 2)

        self.setLayout(layout)
        self.setFixedHeight(27)
        # QtCore.QMetaObject.connectSlotsByName(self)

    def on_scrollToCurrent_clicked(self):
        image = KairyoApi.instance().storage.image
        if not image:
            return

        for i in range(self._listWidget.count()):
            item = self._listWidget.item(i)

            if item.image is image:
                self._listWidget.scrollToItem(item)
                return


class ProjectImageList(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self._list = ImageList()
        self._list.setObjectName("projectImageList")
        self._list.setIconSize(QtCore.QSize(128, 128))
        self._list.setViewMode(QtWidgets.QListView.IconMode)
        self._list.setResizeMode(QtWidgets.QListView.Adjust)
        self._list.setFlow(QtWidgets.QListView.LeftToRight)
        self._list.setSizeAdjustPolicy(QtWidgets.QListWidget.AdjustToContents)
        self._list.setSortingEnabled(True)

        self._bar = ImageListToolbar(self, self._list)
        self._bar.setObjectName('imageListToolbar')

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._bar)
        layout.addWidget(self._list)
        self.setLayout(layout)

        self.__loader_thread = QThread()
        self.__loader = ImageLoader()
        self.__loader.moveToThread(self.__loader_thread)

        self.__loader_thread.started.connect(self.__loader.run)
        self.__loader_thread.start()

        QtCore.QMetaObject.connectSlotsByName(self)

    def sync(self):
        try:
            project = KairyoApi.instance().storage.project

            for im_name in project.images():
                image = project.get_image(im_name)
                self.__loader.schedule(image, self._list)

            self._list.sortItems()
        except BaseException as e:
            logging.error("", exc_info=e)

    def on_projectImageList_currentItemChanged(self):
        item = self._list.currentItem()
        KairyoApi.instance().storage.image = item.image if item else None
