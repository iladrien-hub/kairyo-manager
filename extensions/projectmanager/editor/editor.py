import threading
from functools import partial
from typing import Dict, Optional

import cv2
from PyQt5 import QtWidgets

from core import imutils
from core.minipaint.callbacks import ImageEditorCallbacks
from core.minipaint.editor import ImageEditor
from core.minipaint.ui import ImageEditorWidget
from core.project import ProjectImage
from core.widgets.layout import create_box_layout
from core.widgets.toolbar import ToolBar, ToolbarButton
from editor.tools.healingbrushtool import HealingBrushTool


class EditorWidget(QtWidgets.QFrame, ImageEditorCallbacks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__toolBar = ToolBar()
        self.__toolBar.setFixedHeight(26)

        self.__healingBrushBtn = self.__toolBar.addButton(':/projectmanager/virus-slash.svg', 'Healing Brush Tool (J)')
        self.__healingBrushBtn.setCheckable(True)
        self.__healingBrushBtn.setData(HealingBrushTool)
        self.__healingBrushBtn.setShortcut('J')
        self.__healingBrushBtn.clicked.connect(partial(self.on_toolButton_clicked, self.__healingBrushBtn))

        self.__toolBar.addSeparator()

        self.__resetScaleButton = self.__toolBar.addButton(':/projectmanager/arrows-maximize.svg',
                                                           'Actual Size (Ctrl+1)')
        self.__resetScaleButton.clicked.connect(self.on_resetScaleButton_clicked)

        self.__fitIntoViewButton = self.__toolBar.addButton(':/projectmanager/aspect-ratio.svg',
                                                            'Fit Zoom to View (Ctrl+0)')
        self.__fitIntoViewButton.clicked.connect(self.on_fitIntoViewButton_clicked)

        self.__toolBar.addSeparator()

        self.__undoBtn = self.__toolBar.addButton(':/projectmanager/rotate-left.svg', 'Undo (Ctrl+Z)')
        self.__undoBtn.clicked.connect(self.on_undo_clicked)
        self.__redoBtn = self.__toolBar.addButton(':/projectmanager/rotate-right.svg', 'Redo (Ctrl+R)')
        self.__redoBtn.clicked.connect(self.on_redo_clicked)

        self.__saveBtn = self.__toolBar.addButton(':/projectmanager/floppy-disk.svg', 'Save (Ctrl+S)')
        self.__saveBtn.clicked.connect(self.on_saveButton_clicked)
        self.__saveBtn.setShortcut('Ctrl+S')

        self.__editorInner = ImageEditorWidget()

        self.__editors: Dict[str, ImageEditor] = {}
        self.__mtime: Dict[str, float] = {}
        self.__mtimeLock = threading.Lock()

        self.__currentImage: Optional[ProjectImage] = None

        self.setLayout(create_box_layout([
            self.__toolBar,
            self.__editorInner
        ]))

        self.updateButtons()

    def updateToolButton(self, editor, btn):
        if editor is None:
            btn.setEnabled(False)
            btn.setChecked(False)
            return

        tool = editor.activeTool()
        cls = btn.data()

        btn.setEnabled(True)
        btn.setChecked(bool(tool) and bool(cls) and isinstance(tool, cls))

    def updateButtons(self):
        editor = self.__editorInner.activeEditor()

        self.updateToolButton(editor, self.__healingBrushBtn)
        self.__redoBtn.setEnabled(bool(editor) and editor.history().hasRedo())
        self.__undoBtn.setEnabled(bool(editor) and editor.history().hasUndo())
        self.__saveBtn.setEnabled(bool(editor))

    def setImage(self, image: ProjectImage):
        do_fit = False
        if image.path not in self.__editors:
            editor = ImageEditor(imutils.bytes_to_cv2(image.read_version()))
            editor.installCallbacks(self)

            tool = HealingBrushTool(editor.size())
            editor.addTool(tool)

            self.__editors[image.path] = editor
            do_fit = True

        self.__editorInner.setActiveEditor(self.__editors[image.path])
        if do_fit:
            self.__editorInner.fitIntoView()
        else:
            self.__editorInner.fitIntoViewIfNeeded()
        self.__currentImage = image

        self.updateButtons()

    def reloadFromDisk(self, image: ProjectImage):
        with self.__mtimeLock:
            self._reloadFromDisk(image)

    def _reloadFromDisk(self, image: ProjectImage):
        if image.mtime == self.__mtime.get(image.path, 0):
            return
        if image.path not in self.__editors:
            return

        editor = self.__editors.pop(image.path)
        if editor is self.__editorInner.activeEditor():
            self.setImage(image)

        self.__mtime[image.path] = image.mtime

    def save(self):
        with self.__mtimeLock:
            self._save()

    def _save(self):
        image = self.__currentImage
        if not image:
            return
        editor = self.__editorInner.activeEditor()
        if not editor:
            return

        cv_img = cv2.cvtColor(editor.render(), cv2.COLOR_RGBA2BGR)

        image.update(imutils.cv2_to_bytes(cv_img))
        self.__mtime[image.path] = image.mtime
        self.__saveBtn.setEnabled(False)

    def on_toolButton_clicked(self, sender: ToolbarButton):
        editor = self.__editorInner.activeEditor()
        if editor is None:
            return

        tool_cls = sender.data()

        if sender.isChecked() and bool(tool_cls):
            editor.setActiveTool(editor.tool(tool_cls))
        else:
            editor.setActiveTool(None)

        self.__editorInner.updateCursor()

    def on_saveButton_clicked(self):
        self.save()

    def on_undo_clicked(self):
        editor = self.__editorInner.activeEditor()
        if editor is None:
            return
        editor.undo()

    def on_redo_clicked(self):
        editor = self.__editorInner.activeEditor()
        if editor is None:
            return
        editor.redo()

    def on_resetScaleButton_clicked(self):
        self.__editorInner.on_resetScale_triggered()

    def on_fitIntoViewButton_clicked(self):
        self.__editorInner.on_fitIntoView_triggered()

    def renderCanvas(self):
        self.__editorInner.renderCanvas()

    def historyUpdated(self):
        self.updateButtons()
