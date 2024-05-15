import typing

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .toolbar import ToolBar
from ..api import KairyoApi
from ..styling.icon import load_icon


class EditableListItemDelegate(QtWidgets.QStyledItemDelegate):
    editFinished = pyqtSignal(QtCore.QModelIndex)

    def destroyEditor(self, editor: typing.Optional[QWidget], index: QtCore.QModelIndex) -> None:
        self.editFinished.emit(index)
        return super().destroyEditor(editor, index)


class EditableList(QtWidgets.QFrame):
    listChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(EditableList, self).__init__(*args, **kwargs)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._toolBar = ToolBar()

        self._list = QtWidgets.QListWidget()

        self._delegate = EditableListItemDelegate()
        self._list.setItemDelegate(self._delegate)

        self._addButton = self._toolBar.addButton(':/mainwindow/plus.svg', 'Add item')
        self._removeButton = self._toolBar.addButton(':/mainwindow/minus.svg', 'Remove item')
        self._upButton = self._toolBar.addButton(':/mainwindow/up.svg', 'Move up')
        self._downButton = self._toolBar.addButton(':/mainwindow/down.svg', 'Move down')

        self._layout.addWidget(self._toolBar)
        self._layout.addWidget(self._list)

        self.setLayout(self._layout)

        self._addButton.clicked.connect(self.on_addButton_clicked)
        self._removeButton.clicked.connect(self.on_removeButton_clicked)
        self._upButton.clicked.connect(self.on_upButton_clicked)
        self._downButton.clicked.connect(self.on_downButton_clicked)
        self._list.itemSelectionChanged.connect(self.updateControls)
        self._delegate.editFinished.connect(self.listChanged.emit)

        self.updateControls()

    def addItem(self, text):

        item = QtWidgets.QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        row = self._list.count()
        if idx := self._list.selectedIndexes():
            row = idx[0].row() + 1

        self._list.insertItem(row, item)
        self.listChanged.emit()  # noqa

        return item

    def moveItem(self, offset: int):
        selected = self._list.selectedIndexes()
        if not selected:
            return

        row = selected[0].row()
        item = self._list.takeItem(row)
        self._list.insertItem(row + offset, item)
        self._list.setCurrentItem(item)

        self.listChanged.emit()  # noqa

    def updateControls(self):
        selected = self._list.selectedIndexes()

        has_selection = bool(selected)
        self._removeButton.setEnabled(has_selection)
        if has_selection:
            row = selected[0].row()

            self._upButton.setEnabled(row > 0)
            self._downButton.setEnabled(row < self._list.count() - 1)
        else:
            self._upButton.setEnabled(False)
            self._downButton.setEnabled(False)

    def value(self):
        return [self._list.item(i).text() for i in range(self._list.count())]

    def clear(self):
        self._list.clear()
        self.listChanged.emit()  # noqa

    def on_addButton_clicked(self):
        text = "New item"

        count = self._list.count()
        if count > 0:
            text += f" ({count})"

        item = self.addItem(text)
        self._list.setCurrentItem(item)

    def on_removeButton_clicked(self):
        selected = self._list.selectedIndexes()
        if selected:
            self._list.takeItem(selected[0].row())

        self.listChanged.emit()  # noqa

    def on_upButton_clicked(self):
        self.moveItem(-1)

    def on_downButton_clicked(self):
        self.moveItem(1)
