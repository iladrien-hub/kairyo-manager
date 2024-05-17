from functools import partial
from typing import Optional

from PyQt5 import QtWidgets

from core.project import ProjectImage
from core.widgets.toolbar import ToolBar, ToolbarButton
from .scene import EditorScene
from ..model.document import Document, EditorCallbacks
from ..tools.healingbrush import HealingBrushTool


class EditorWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scene = EditorScene()
        self._document: Optional[Document] = None

        self._toolBar = ToolBar()
        self._tools = []

        self._healingToolButton = self._toolBar.addButton(':/projectmanager/virus-slash.svg', 'Healing Brush (J)')
        self._healingToolButton.setCheckable(True)
        self._healingToolButton.setData(HealingBrushTool)
        self._healingToolButton.setShortcut('J')
        self._healingToolButton.clicked.connect(partial(self.on_toolButton_clicked, self._healingToolButton))
        self._tools.append(self._healingToolButton)

        self._toolBar.addSeparator()

        self._resetScaleButton = self._toolBar.addButton(':/projectmanager/arrows-maximize.svg', 'Actual Size (Ctrl+2)')
        self._resetScaleButton.clicked.connect(self.on_resetScaleButton_clicked)
        self._resetScaleButton.setShortcut('Ctrl+2')

        self._fitIntoViewButton = self._toolBar.addButton(':/projectmanager/aspect-ratio.svg',
                                                          'Fit Zoom to View (Ctrl+1)')
        self._fitIntoViewButton.clicked.connect(self.on_fitIntoViewButton_clicked)
        self._fitIntoViewButton.setShortcut('Ctrl+1')

        self._toolBar.addSeparator()

        self._undoButton = self._toolBar.addButton(':/projectmanager/rotate-left.svg', 'Undo (Ctrl+Z)')
        self._undoButton.clicked.connect(self.on_undoButton_clicked)
        self._undoButton.setShortcut('Ctrl+Z')

        self._redoButton = self._toolBar.addButton(':/projectmanager/rotate-right.svg', 'Redo (Ctrl+R)')
        self._redoButton.clicked.connect(self.on_redoButton_clicked)
        self._redoButton.setShortcut('Ctrl+R')

        self._toolBar.addSeparator()

        self._saveButton = self._toolBar.addButton(':/projectmanager/floppy-disk.svg', 'Save (Ctrl+S)')
        self._saveButton.clicked.connect(self.on_saveButton_clicked)
        self._saveButton.setShortcut('Ctrl+S')

        self._callbacks = EditorCallbacks()
        self._callbacks.stateUpdated.connect(self.updateButtons)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._toolBar)
        layout.addWidget(self._scene)

        self.setLayout(layout)
        self.updateButtons()

    def updateButtons(self):
        has_doc = self._document is not None

        self._fitIntoViewButton.setEnabled(has_doc)
        self._resetScaleButton.setEnabled(has_doc)

        self._undoButton.setEnabled(has_doc and self._document.hasUndo())
        self._redoButton.setEnabled(has_doc and self._document.hasRedo())
        self._saveButton.setEnabled(has_doc and not self._document.saved())

        self._healingToolButton.setEnabled(has_doc)
        self._healingToolButton.setChecked(has_doc and isinstance(self._document.tool(), HealingBrushTool))

    def scene(self):
        return self._scene

    def setImage(self, image: ProjectImage):
        self._document = Document.from_image(image)
        self._document.setCallbacks(self._callbacks)
        self._scene.setDocument(self._document)
        self._scene.fitIntoView()
        self.updateButtons()

    def on_fitIntoViewButton_clicked(self):
        self._scene.fitIntoView()

    def on_resetScaleButton_clicked(self):
        self._scene.resetScale()

    def on_toolButton_clicked(self, sender: ToolbarButton, checked: bool):
        if checked:
            for btn in self._tools:
                btn.setChecked(btn == sender)

            tool = sender.data()
        else:
            tool = None

        if self._document:
            self._document.switchTool(tool)

    def on_undoButton_clicked(self):
        if self._document:
            self._document.undo()
            self._scene.update()

    def on_redoButton_clicked(self):
        if self._document:
            self._document.redo()
            self._scene.update()

    def on_saveButton_clicked(self):
        if self._document:
            self._document.save()
