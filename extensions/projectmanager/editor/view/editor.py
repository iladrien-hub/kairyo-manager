from PyQt5 import QtWidgets

from core.project import ProjectImage
from .scene import EditorScene
from ..model.document import Document
from ..tools.healingbrush import HealingBrushTool


class EditorWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._scene = EditorScene()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._scene)

        self.setLayout(layout)

    def scene(self):
        return self._scene

    def setImage(self, image: ProjectImage):
        doc = Document.from_image(image)
        self._scene.setDocument(doc)
        self._scene.fitIntoView()
        # doc.switchTool(HealingBrushTool)
