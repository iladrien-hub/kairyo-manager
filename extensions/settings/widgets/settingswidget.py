from typing import Dict, Type, List

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

from core.user_interface import SettingsNode
from core.widgets.settings import Setting, SettingCallbacks


class SettingsFooter(QtWidgets.QFrame):
    def __init__(self, *args, **kwargs):
        super(SettingsFooter, self).__init__(*args, **kwargs)

        self.save = QtWidgets.QPushButton(self)
        self.save.setText('Save')
        self.save.setProperty('accent', True)

        self.cancel = QtWidgets.QPushButton(self)
        self.cancel.setText('Cancel')

        self.apply = QtWidgets.QPushButton(self)
        self.apply.setText('Apply')
        self.apply.setEnabled(False)

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.save)
        layout.addWidget(self.cancel)
        layout.addWidget(self.apply)

        self.setLayout(layout)


class SettingsWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)

        self._settings = None
        self._callbacks = SettingCallbacks()

        self._tree = QtWidgets.QTreeWidget()
        self._tree.setFixedWidth(220)
        self._tree.setMinimumHeight(624)
        self._tree.header().setVisible(False)

        self._stack = QtWidgets.QStackedWidget()
        self._stack.setMinimumWidth(680)

        self._breadCrumbs = QtWidgets.QLabel(self)
        self._breadCrumbs.setFixedHeight(25)

        self._footer = SettingsFooter(self)

        central = QtWidgets.QHBoxLayout()
        central.setContentsMargins(0, 8, 0, 0)
        central.setSpacing(0)

        central.addWidget(self._tree)

        right = QtWidgets.QVBoxLayout()
        right.setContentsMargins(19, 0, 19, 0)
        right.setSpacing(16)

        right.addWidget(self._breadCrumbs)
        right.addWidget(self._stack)

        central.addLayout(right)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addLayout(central)
        layout.addWidget(self._footer)

        self.setLayout(layout)

        self._tree.itemSelectionChanged.connect(self.on_model_itemChanged)
        self._callbacks.settingChanged.connect(self.on_callbacks_settingChanged)
        self._footer.apply.clicked.connect(self.on_applyButton_clicked)
        self._footer.save.clicked.connect(self.on_saveButton_clicked)
        self._footer.cancel.clicked.connect(self.on_cancelButton_clicked)

    def populateTree(self, settings: List[SettingsNode], root=None):
        root = root if root else self._tree

        for item in settings:
            child = QTreeWidgetItem(root)
            child.setText(0, item.title)

            constructor = item.constructor or QtWidgets.QLabel
            widget = constructor()

            self._stack.addWidget(widget)
            child.setData(0, Qt.UserRole, widget)

            if item.children:
                self.populateTree(item.children, child)

        self._tree.setSortingEnabled(True)
        self._tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self._tree.setSortingEnabled(False)

    def updateUi(self):
        self._tree.setCurrentIndex(self._tree.model().index(0, 0))

        for child in self.findChildren(Setting):
            child.setSettings(self._settings)
            child.restore()
            child.setCallbacks(self._callbacks)

    def setSettings(self, s: QtCore.QSettings):
        self._settings = s

    def on_model_itemChanged(self):
        item = self._tree.currentItem()
        widget = item.data(0, Qt.UserRole)
        self._stack.setCurrentIndex(self._stack.indexOf(widget))

        breadcrumbs = [item.text(0)]
        parent = item.parent()
        while parent:
            breadcrumbs.append(parent.text(0))
            parent = parent.parent()

        self._breadCrumbs.setText(" > ".join(breadcrumbs[::-1]))

    def on_callbacks_settingChanged(self):
        any_changed = any(i.changed() for i in self.findChildren(Setting))
        self._footer.apply.setEnabled(any_changed)

    def on_applyButton_clicked(self):
        for i in self.findChildren(Setting):
            i.save()

        any_changed = any(i.changed() for i in self.findChildren(Setting))
        self._footer.apply.setEnabled(any_changed)

    def on_saveButton_clicked(self):
        for i in self.findChildren(Setting):
            i.save()
        self.window().close()

    def on_cancelButton_clicked(self):
        self.window().close()
