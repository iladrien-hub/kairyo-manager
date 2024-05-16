from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QMetaObject, QSettings
from PyQt5.QtWidgets import QLabel, QSizePolicy

from core.api import KairyoApi
from core.styling import make_stylesheet, Style
from core.styling.icon import load_icon
from core.widgets import TabWidget
from core.widgets.splitter import Splitter
from .history import ImageHistoryWidget
from .imageeditor import ImageEditorWidget
from .imagelist import ProjectImageList


class ProjectManagerTab(QtWidgets.QWidget):
    _BOTTOM_TAB_STYLE = make_stylesheet([Style(
        'QWidget', {
            'border-left': '1px solid #212121',
            'border-top': '1px solid #212121',
        }
    )])
    _LEFT_TAB_STYLE = make_stylesheet([Style(
        'QWidget', {
            'border-right': '1px solid #212121',
        }
    )])

    def __init__(self, parent, settings: QSettings):
        super().__init__(parent)

        self._settings = settings

        self._leftTabs = TabWidget()
        self._leftTabs.setObjectName('leftTabs')

        self._bottomTabs = TabWidget()
        self._bottomTabs.setObjectName('bottomTabs')

        self._topSplitter = Splitter(Qt.Horizontal)
        self._topSplitter.setObjectName('topSplitter')

        self._bottomSplitter = Splitter(Qt.Vertical)
        self._bottomSplitter.setObjectName('bottomSplitter')

        self._imageList = ProjectImageList(self)
        self._imageList.setObjectName('projectImageList')

        self._history = ImageHistoryWidget(self)
        self._history.setObjectName('imageHistoryView')

        self._editor = ImageEditorWidget()

        self.setupUi()
        QMetaObject.connectSlotsByName(self)

    def setupUi(self):
        self._leftTabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self._bottomTabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)

        KairyoApi.instance().storage.projectChanged.connect(self._imageList.sync)
        self._leftTabs.setTabIcon(
            self._leftTabs.addTab(self._imageList, "Files"),
            load_icon(":/projectmanager/folder.svg", "#cacaca")
        )

        q_label = QLabel("Project and image information...")
        q_label.setStyleSheet(self._LEFT_TAB_STYLE)
        self._leftTabs.setTabIcon(
            self._leftTabs.addTab(q_label, "Info"),
            load_icon(":/projectmanager/memo-circle-info.svg", "#cacaca")
        )

        q_label = QLabel("Bookmarks (?)...")
        q_label.setStyleSheet(self._LEFT_TAB_STYLE)
        self._leftTabs.setTabIcon(
            self._leftTabs.addTab(q_label, "Bookmarks"),
            load_icon(":/projectmanager/bookmark.svg", "#cacaca")
        )

        KairyoApi.instance().storage.imageChanged.connect(
            lambda: self._history.setImage(KairyoApi.instance().storage.image)
        )
        self._bottomTabs.setTabIcon(
            self._bottomTabs.addTab(self._history, "History"),
            load_icon(":/projectmanager/code-branch.svg", "#cacaca")
        )

        self._topSplitter.addWidget(self._leftTabs)

        # label = QLabel("Image preview...")
        # label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._topSplitter.addWidget(self._editor)
        self._topSplitter.setChildrenCollapsible(False)
        self._topSplitter.setHandleWidth(0)
        self._topSplitter.setMinimumHeight(224)
        self._topSplitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addItem(QtWidgets.QSpacerItem(21, 1, QSizePolicy.Fixed, QSizePolicy.Fixed))
        bottom_layout.addWidget(self._bottomTabs)

        self._bottomSplitter.addWidget(self._topSplitter)
        w = QtWidgets.QWidget()
        w.setLayout(bottom_layout)
        self._bottomSplitter.addWidget(w)
        self._bottomSplitter.setChildrenCollapsible(False)
        self._bottomSplitter.setHandleWidth(0)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._bottomSplitter)

        self.setLayout(layout)
        self.loadState()

    def loadState(self):
        left_tab = int(self._settings.value('projectmanager/leftTabs_last', 0, int))
        self._leftTabs.setCurrentTab(left_tab if left_tab >= 0 else None)

        left_tab = int(self._settings.value('projectmanager/bottomTabs_last', 0, int))
        self._bottomTabs.setCurrentTab(left_tab if left_tab >= 0 else None)

        if self._leftTabs.currentTab() < 0:
            self._topSplitter.handle(1).setEnabled(False)
        if self._bottomTabs.currentTab() < 0:
            self._bottomSplitter.handle(1).setEnabled(False)

    def editor(self):
        return self._editor

    # Top tabs

    def on_topSplitter_splitterMoved(self, pos, index):
        if (idx := self._leftTabs.currentTab()) >= 0:
            self._settings.setValue(f'projectmanager/leftTabs_{idx}_size', self._topSplitter.sizes()[0])

    def on_topSplitter_resized(self):
        if (idx := self._leftTabs.currentTab()) >= 0:
            size = self._settings.value(f'projectmanager/leftTabs_{idx}_size', 300, int)
            self._topSplitter.setSizes([size, self._topSplitter.width() - size])

    def on_leftTabs_currentTabChanged(self, idx: int):
        if idx >= 0:
            size = self._settings.value(f'projectmanager/leftTabs_{idx}_size', 300, int)
            self._topSplitter.setSizes([size, self._topSplitter.width() - size])
            self._topSplitter.handle(1).setEnabled(True)
        else:
            self._topSplitter.handle(1).setEnabled(False)
        self._settings.setValue('projectmanager/leftTabs_last', idx)

    # Bottom tabs

    def on_bottomSplitter_splitterMoved(self, pos, index):
        if (idx := self._bottomTabs.currentTab()) >= 0:
            self._settings.setValue(f'projectmanager/bottomTabs_{idx}_size', self._bottomSplitter.sizes()[1])

    def on_bottomSplitter_resized(self):
        if (idx := self._bottomTabs.currentTab()) >= 0:
            size = self._settings.value(f'projectmanager/bottomTabs_{idx}_size', 300, int)
            self._bottomSplitter.setSizes([self._bottomSplitter.height() - size, size])
        else:
            self._bottomSplitter.setSizes([self._bottomSplitter.height(), 22])

    def on_bottomTabs_currentTabChanged(self, idx: int):
        if idx >= 0:
            size = self._settings.value(f'projectmanager/bottomTabs_{idx}_size', 300, int)
            self._bottomSplitter.setSizes([self._bottomSplitter.height() - size, size])
            self._bottomSplitter.handle(1).setEnabled(True)
        else:
            self._bottomSplitter.setSizes([self._bottomSplitter.height(), 22])
            self._bottomSplitter.handle(1).setEnabled(False)
        self._settings.setValue('projectmanager/bottomTabs_last', idx)
