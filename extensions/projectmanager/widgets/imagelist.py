import logging
import queue
from enum import Enum
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
        match self.listWidget().sortOrder():
            case ImageList.SortOrder.Name_AZ:
                return self.text() < other.text()
            case ImageList.SortOrder.Name_ZA:
                return self.text() > other.text()
            case ImageList.SortOrder.TimeCreated_Newer:
                return self.image.meta.time_created > other.image.meta.time_created
            case ImageList.SortOrder.TimeCreated_Older:
                return self.image.meta.time_created < other.image.meta.time_created


class ImageList(QtWidgets.QListWidget):
    class SortOrder(Enum):
        Name_AZ = 1
        Name_ZA = 2
        TimeCreated_Newer = 3
        TimeCreated_Older = 4

    sortOrderChanged = QtCore.pyqtSignal(SortOrder)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.verticalScrollBar().setSingleStep(20)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self._sortOrder = self.SortOrder.Name_AZ

    def setSortOrder(self, order: SortOrder):
        if self._sortOrder != order:
            self._sortOrder = order
            self.sortItems()
            self.sortOrderChanged.emit(order)

    def sortOrder(self):
        return self._sortOrder

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
    __PULL_TIMEOUT = object()

    def __init__(self, list_widget: ImageList):
        super().__init__()
        self._list_widget = list_widget
        self._queue = queue.Queue()
        self._items = []

    def schedule(self, image: ProjectImage):
        self._queue.put(image)

    def pull(self):
        try:
            return self._queue.get(timeout=0.15)
        except queue.Empty:
            return self.__PULL_TIMEOUT

    def flush(self):
        if self._items:
            for item in self._items:
                self._list_widget.addItem(item)
            self._list_widget.sortItems()
            self._items.clear()

    def run(self):
        while True:
            try:
                image = self.pull()
                if image is self.__PULL_TIMEOUT:
                    self.flush()
                    continue

                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(image.read_version())

                self._items.append(ImageListItem(QtGui.QIcon(pixmap), image.name, image))
                if len(self._items) > 100:
                    self.flush()

            except BaseException as e:
                logging.error("", e)


class ImageListToolbarButton(QtWidgets.QToolButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QtCore.QSize(16, 16))
        self.setFixedSize(21, 21)


class ScrollToSelectedButton(ImageListToolbarButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIcon(load_icon(
            ':/projectmanager/crosshairs-simple.svg',
            KairyoApi.instance().theme.text_200
        ))
        self.setToolTip("Scroll to Selected File")


class SetSortOrderButton(ImageListToolbarButton):
    changed = QtCore.pyqtSignal(ImageList.SortOrder)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIcon(load_icon(
            ':/projectmanager/arrow-down-wide-short.svg',
            KairyoApi.instance().theme.text_200
        ))
        self.setToolTip("Change Sort Order")

        self._toolMenu = QtWidgets.QMenu(self)
        self._actions = QtWidgets.QActionGroup(self)
        self._order = ImageList.SortOrder.Name_AZ

        options = (
            ('Name (A-z)', ImageList.SortOrder.Name_AZ),
            ('Name (z-A)', ImageList.SortOrder.Name_ZA),
            ('Time Created (Newer)', ImageList.SortOrder.TimeCreated_Newer),
            ('Time Created (Older)', ImageList.SortOrder.TimeCreated_Older),
        )

        for name, val in options:
            action = self._actions.addAction(name)
            action.setCheckable(True)
            action.setData(val)

            if val == self._order:
                action.setChecked(True)

        self._actions.setExclusive(True)
        self._actions.setExclusionPolicy(QtWidgets.QActionGroup.ExclusionPolicy.Exclusive)

        self._toolMenu.addActions(self._actions.actions())
        self._actions.triggered.connect(self.on_actions_triggered)

        self.setMenu(self._toolMenu)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

    def setOrder(self, val: ImageList.SortOrder):
        if val != self._order:
            self._order = val
            for action in self._actions.actions():
                action.setChecked(val == action.data())
            self.changed.emit(self._order)

    def on_actions_triggered(self):
        self.setOrder(self._actions.checkedAction().data())


class ImageListToolbar(QtWidgets.QFrame):
    def __init__(self, parent, list_widget: ImageList):
        super().__init__(parent)

        self._listWidget = list_widget
        self._scrollToSelected = ScrollToSelectedButton(self)
        self._scrollToSelected.clicked.connect(self.on_scrollToCurrent_clicked)

        self._sortOrder = SetSortOrderButton(self)
        self._sortOrder.changed.connect(self.on_sortOrder_changed)
        self._listWidget.sortOrderChanged.connect(self._sortOrder.setOrder)

        order = KairyoApi.instance().settings.value('projectmanager/imageListSortOrder', None, str)
        if order in ImageList.SortOrder.__members__:
            self._listWidget.setSortOrder(ImageList.SortOrder[order])

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self._sortOrder)
        layout.addWidget(self._scrollToSelected)

        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)

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

    def on_sortOrder_changed(self, order: ImageList.SortOrder):
        self._listWidget.setSortOrder(order)
        KairyoApi.instance().settings.setValue('projectmanager/imageListSortOrder', order.name)


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
        self._list.setMovement(QtWidgets.QListView.Movement.Static)
        self._list.setSortingEnabled(True)

        self._bar = ImageListToolbar(self, self._list)
        self._bar.setObjectName('imageListToolbar')

        self._footer = QtWidgets.QFrame()
        self._footerLabel = QtWidgets.QLabel('')
        self._footer.setObjectName('imageListFooter')
        self._footer.setFixedHeight(26)

        footer = QtWidgets.QVBoxLayout()
        footer.addWidget(self._footerLabel)
        footer.setContentsMargins(4, 0, 0, 0)
        footer.setSpacing(0)

        self._footer.setLayout(footer)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._bar)
        layout.addWidget(self._list)
        layout.addWidget(self._footer)
        self.setLayout(layout)

        self.__loader_thread = QThread()
        self.__loader = ImageLoader(self._list)
        self.__loader.moveToThread(self.__loader_thread)

        self.__loader_thread.started.connect(self.__loader.run)
        self.__loader_thread.start()

        QtCore.QMetaObject.connectSlotsByName(self)
        self._list.model().rowsInserted.connect(self.updateFooter)
        self._list.model().rowsRemoved.connect(self.updateFooter)

        self.updateFooter()

    def sync(self):
        try:
            project = KairyoApi.instance().storage.project

            for im_name in project.images():
                image = project.get_image(im_name)
                self.__loader.schedule(image)

            self._list.sortItems()
        except BaseException as e:
            logging.error("", exc_info=e)

    def updateFooter(self):
        count = self._list.count()
        label = 'item' if count == 1 else 'items'
        self._footerLabel.setText(f"{count} {label}")

    def on_projectImageList_currentItemChanged(self):
        item = self._list.currentItem()
        KairyoApi.instance().storage.image = item.image if item else None
