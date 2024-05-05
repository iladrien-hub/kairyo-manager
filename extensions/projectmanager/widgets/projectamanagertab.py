from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QSizePolicy

from core.styling import make_stylesheet, Style
from core.styling.icon import load_icon
from core.widgets import TabWidget


# noinspection PyPep8Naming
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

    def __init__(self):
        super().__init__()

        self._left_tabs = TabWidget()
        self._bottom_tabs = TabWidget()

        self.setupUi()

    def setupUi(self):
        self._left_tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self._left_tabs.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self._left_tabs.setMaximumWidth(300)

        self._bottom_tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self._bottom_tabs.setMaximumHeight(300)

        q_label = QLabel("Files list...")
        q_label.setStyleSheet(self._LEFT_TAB_STYLE)
        self._left_tabs.setTabIcon(
            self._left_tabs.addTab(q_label, "Files"),
            load_icon(":/projectmanager/folder.svg", "#cacaca")
        )

        q_label = QLabel("Project and image information...")
        q_label.setStyleSheet(self._LEFT_TAB_STYLE)
        self._left_tabs.setTabIcon(
            self._left_tabs.addTab(q_label, "Info"),
            load_icon(":/projectmanager/memo-circle-info.svg", "#cacaca")
        )

        q_label = QLabel("Bookmarks (?)...")
        q_label.setStyleSheet(self._LEFT_TAB_STYLE)
        self._left_tabs.setTabIcon(
            self._left_tabs.addTab(q_label, "Bookmarks"),
            load_icon(":/projectmanager/bookmark.svg", "#cacaca")
        )

        q_label = QLabel("Image version history...")
        q_label.setStyleSheet(self._BOTTOM_TAB_STYLE)
        self._bottom_tabs.setTabIcon(
            self._bottom_tabs.addTab(q_label, "History"),
            load_icon(":/projectmanager/code-branch.svg", "#cacaca")
        )

        central_layout = QtWidgets.QHBoxLayout()
        central_layout.addWidget(self._left_tabs)

        label = QLabel("Image preview...")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central_layout.addWidget(label)
        central_layout.setSpacing(0)

        central_layout.setContentsMargins(0, 0, 0, 0)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addItem(QtWidgets.QSpacerItem(21, 1, QSizePolicy.Fixed, QSizePolicy.Fixed))
        bottom_layout.addWidget(self._bottom_tabs)

        # self._bottom_tabs.setStyleSheet()

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(central_layout)
        layout.addLayout(bottom_layout)
        # layout.addWidget(self._bottom_tabs)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
