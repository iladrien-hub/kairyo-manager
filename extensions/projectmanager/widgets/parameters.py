import jmespath
import pyperclip
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal

from core.api import KairyoApi
from core.project import ProjectImage
from core.widgets.layout import create_box_layout, layout_to_widget
from core.widgets.toolbar import ToolbarButton


class PromptHeaderWidget(QtWidgets.QFrame):
    copyRequested = pyqtSignal()

    def __init__(self, title):
        super().__init__()

        self._title = QtWidgets.QLabel(title)

        self._copyBtn = ToolbarButton(':/projectmanager/copy.svg')
        self._copyBtn.setIconSize(QtCore.QSize(16, 16))
        self._copyBtn.setFixedSize(20, 20)
        self._copyBtn.clicked.connect(self.copyRequested.emit)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._title)
        layout.addStretch()
        layout.addWidget(self._copyBtn)

        self.setLayout(layout)


class PromptBodyWidget(QtWidgets.QLabel):

    def __init__(self):
        super().__init__()

        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)


class ParamWidget(QtWidgets.QFrame):

    def __init__(self, title):
        super().__init__()

        self._title = QtWidgets.QLabel(title)
        self._title.setObjectName('paramTitle')

        self._value = QtWidgets.QLabel()
        self._value.setObjectName('paramValue')
        self._value.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._title)
        layout.addStretch()
        layout.addWidget(self._value)

        self.setLayout(layout)

    def setValue(self, v):
        self._value.setText(str(v))


class ParametersWidget(QtWidgets.QFrame):
    __OTHER_PARAMS = {
        'Checkpoint': jmespath.compile('override_settings.sd_model_checkpoint'),

        'Cfg Scale': jmespath.compile('cfg_scale'),
        'Clip Skip': jmespath.compile('override_settings.CLIP_stop_at_last_layers'),
        'Sampler': jmespath.compile('sampler_name'),
        'Seed': jmespath.compile('seed'),
        'Steps': jmespath.compile('steps'),
        'VAE': jmespath.compile('override_settings.sd_vae'),
    }

    def __init__(self):
        super().__init__()

        self._promptLabel = PromptHeaderWidget('Prompt:')
        self._promptData = PromptBodyWidget()
        self._promptLabel.copyRequested.connect(lambda: pyperclip.copy(self._promptData.text()))

        self._negativePromptLabel = PromptHeaderWidget('NegativePrompt:')
        self._negativePromptData = PromptBodyWidget()
        self._negativePromptLabel.copyRequested.connect(lambda: pyperclip.copy(self._negativePromptData.text()))

        self._params = {k: ParamWidget(f"{k}:") for k in self.__OTHER_PARAMS}

        layout = create_box_layout([
            self._promptLabel,
            self._promptData,
            self._negativePromptLabel,
            self._negativePromptData,
            *self._params.values()
        ], margins=(8, 8, 8, 8), spacing=12)
        layout.addStretch()

        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(layout_to_widget(layout))

        self.setLayout(create_box_layout([self._scroll]))
        self.clear()

        KairyoApi.instance().storage.imageChanged.connect(self.sync)

    def clear(self):
        self.setEnabled(False)
        self._promptData.setVisible(False)
        self._negativePromptData.setVisible(False)

        self._promptData.clear()
        self._negativePromptData.clear()

    def fill(self, image: ProjectImage):
        self.setEnabled(True)
        self._promptData.setVisible(True)
        self._negativePromptData.setVisible(True)

        self._promptData.setText(image.params['prompt'])
        self._negativePromptData.setText(image.params['negative_prompt'])

        for key, expr in self.__OTHER_PARAMS.items():
            value = expr.search(image.params)
            self._params[key].setVisible(value is not None)
            self._params[key].setValue(value)

    def sync(self):
        image = KairyoApi.instance().storage.image
        if image is None:
            self.clear()
        else:
            self.fill(image)
