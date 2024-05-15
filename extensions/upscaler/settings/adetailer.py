import contextlib
import os.path
from typing import List

import inflect
import ujson
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtNetwork import QNetworkReply

from core.api import KairyoApi
from core.settings import AUTOMATIC_PATH, AUTOMATIC_URL
from core.webui import WebuiApi, HttpBackend
from core.widgets import TabWidget
from core.widgets import settings as sw
from core.widgets.forms import LabeledDivider
from .settings import AD_ENABLED, AD_PROMPT, AD_NEG_PROMPT, AD_MASK_BLUR, AD_DENOISING, AD_MASK_PADDING, AD_MODEL, \
    AD_MASK_K_LARGEST, AD_MODEL_CONFIDENCE, AD_MASK_MIN_AREA, AD_MASK_MAX_AREA, AD_USE_INPAINT_WIDTH_HEIGHT, \
    AD_INPAINT_WIDTH, AD_INPAINT_HEIGHT, AD_CHECKPOINT, AD_SAMPLER, AD_USE_CHECKPOINT, AD_USE_SAMPLER


class ADetailerItemSettings(QtWidgets.QFrame):
    def __init__(self, suffix, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._enabled = sw.BooleanSetting(f"{AD_ENABLED}_{suffix}")
        self._enabled.setText('Enabled')

        self._prompt = sw.MultilineTextSetting(f"{AD_PROMPT}_{suffix}")
        self._prompt.setPlaceholderText('ADetailer prompt (if blank main is used)')
        self._prompt.setMinimumHeight(96)

        self._prompt_neg = sw.MultilineTextSetting(f"{AD_NEG_PROMPT}_{suffix}")
        self._prompt_neg.setPlaceholderText('ADetailer negative prompt (if blank main is used)')
        self._prompt_neg.setMinimumHeight(96)

        self._mask_blur = sw.SliderSetting(f"{AD_MASK_BLUR}_{suffix}")
        self._mask_blur.setLabel('Mask blur')
        self._mask_blur.setDefault(4)
        self._mask_blur.setRange(0, 64, 0)

        self._denoising = sw.SliderSetting(f"{AD_DENOISING}_{suffix}")
        self._denoising.setLabel('Inpaint denoising strength')
        self._denoising.setDefault(0.4)
        self._denoising.setRange(0, 1, 2)

        self._padding = sw.SliderSetting(f"{AD_MASK_PADDING}_{suffix}")
        self._padding.setLabel('Mask padding')
        self._padding.setDefault(24)
        self._padding.setRange(0, 256, 0)
        self._padding.layout().addStretch()  # noqa

        self._mask_k_largest = sw.SliderSetting(f"{AD_MASK_K_LARGEST}_{suffix}")
        self._mask_k_largest.setLabel('Mask only the top k largest (0 to disable)')
        self._mask_k_largest.setDefault(0)
        self._mask_k_largest.setRange(0, 10, 0)

        self._confidence = sw.SliderSetting(f"{AD_MODEL_CONFIDENCE}_{suffix}")
        self._confidence.setLabel('Detection model confidence threshold')
        self._confidence.setDefault(0.3)
        self._confidence.setRange(0, 1, 2)

        self._mask_min_area = sw.SliderSetting(f"{AD_MASK_MIN_AREA}_{suffix}")
        self._mask_min_area.setLabel('Mask min area ratio')
        self._mask_min_area.setDefault(0)
        self._mask_min_area.setRange(0, 1, 2)

        self._mask_max_area = sw.SliderSetting(f"{AD_MASK_MAX_AREA}_{suffix}")
        self._mask_max_area.setLabel('Mask min area ratio')
        self._mask_max_area.setDefault(1)
        self._mask_max_area.setRange(0, 1, 2)

        self._model = sw.OptionsSetting(f"{AD_MODEL}_{suffix}")

        self._use_separate_size = sw.BooleanSetting(f"{AD_USE_INPAINT_WIDTH_HEIGHT}_{suffix}")
        self._use_separate_size.setText('Use separate width/height')

        self._width = sw.SliderSetting(f"{AD_INPAINT_WIDTH}_{suffix}")
        self._width.setLabel('Inpaint width')
        self._width.setDefault(512)
        self._width.setRange(64, 2048, 0)

        self._height = sw.SliderSetting(f"{AD_INPAINT_HEIGHT}_{suffix}")
        self._height.setLabel('Inpaint height')
        self._height.setDefault(512)
        self._height.setRange(64, 2048, 0)

        self._width_height = self._asWidget(self._layoutWidgets([
            self._width,
            self._height,
        ]))
        self._width_height.setEnabled(False)
        self._use_separate_size.stateChanged.connect(
            lambda: self._width_height.setEnabled(self._use_separate_size.isChecked()))

        self._checkpoint = sw.OptionsSetting(f"{AD_CHECKPOINT}_{suffix}")
        self._checkpoint.setEnabled(False)
        self._use_checkpoint = sw.BooleanSetting(f"{AD_USE_CHECKPOINT}_{suffix}")
        self._use_checkpoint.setText('Use separate checkpoint')
        self._use_checkpoint.stateChanged.connect(lambda: self._checkpoint.setEnabled(self._use_checkpoint.isChecked()))

        self._sampler = sw.OptionsSetting(f"{AD_SAMPLER}_{suffix}")
        self._sampler.setEnabled(False)
        self._use_sampler = sw.BooleanSetting(f"{AD_USE_SAMPLER}_{suffix}")
        self._use_sampler.setText('Use separate sampler')
        self._use_sampler.stateChanged.connect(lambda: self._sampler.setEnabled(self._use_sampler.isChecked()))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._enabled)

        form_layout = self._layoutWidgets([
            self._model,
            self._prompt,
            self._prompt_neg,

            LabeledDivider('Detection', add_top_margin=True),
            self._gridLayout([
                [self._confidence, self._mask_min_area],
                [self._mask_k_largest, self._mask_max_area],
            ]),

            LabeledDivider('Inpainting', add_top_margin=True),
            self._gridLayout([
                [self._mask_blur, self._denoising],
                [self._padding, self._layoutWidgets([
                    self._use_separate_size,
                    self._width_height
                ])],
                [
                    self._layoutWidgets([
                        self._use_checkpoint,
                        self._checkpoint
                    ]),
                    self._layoutWidgets([
                        self._use_sampler,
                        self._sampler
                    ]),
                ]
            ]),
        ])

        self._form = QtWidgets.QWidget()
        self._form.setLayout(form_layout)
        self._form.setEnabled(False)

        self._enabled.stateChanged.connect(lambda: self._form.setEnabled(self._enabled.isChecked()))
        layout.addWidget(self._form)
        self.setLayout(layout)

    def setModels(self, models: List[str]):
        self._model.clear()
        self._model.addItems(models)

    def setSamplerEnabled(self, v: bool):
        if v:
            self._use_sampler.setEnabled(True)
            self._sampler.setEnabled(self._use_sampler.isChecked())
        else:
            self._use_sampler.setEnabled(False)
            self._sampler.setEnabled(False)

    def setSamplers(self, samplers: List[str]):
        self._sampler.clear()
        self._sampler.addItems(samplers)
        self._sampler.restore()

    def setCheckpointEnabled(self, v: bool):
        if v:
            self._use_checkpoint.setEnabled(True)
            self._checkpoint.setEnabled(self._use_checkpoint.isChecked())
        else:
            self._use_checkpoint.setEnabled(False)
            self._checkpoint.setEnabled(False)

    def setCheckpoints(self, samplers: List[str]):
        self._checkpoint.clear()
        self._checkpoint.addItems(samplers)
        self._checkpoint.restore()

    def _layoutWidgets(self, items: List[QtCore.QObject], vertical=True):
        layout = QtWidgets.QVBoxLayout() if vertical else QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        for item in items:
            if isinstance(item, QtWidgets.QWidget):
                layout.addWidget(item)
            elif isinstance(item, QtWidgets.QLayout):
                layout.addLayout(item)

        return layout

    def _gridLayout(self, items: List[List[QtCore.QObject]]):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(16, 0, 0, 0)
        layout.setSpacing(12)

        for r_id, row in enumerate(items):
            for c_id, item in enumerate(row):
                if item is None:
                    continue
                if isinstance(item, QtWidgets.QWidget):
                    layout.addWidget(item, r_id, c_id)
                elif isinstance(item, QtWidgets.QLayout):
                    layout.addLayout(item, r_id, c_id)

        return layout

    def _asWidget(self, layout: QtWidgets.QLayout):
        w = QtWidgets.QWidget()
        w.setLayout(layout)
        return w


class ADetailerSettings(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tabs = TabWidget()
        self._tabs.setAlwaysOpen(True)
        self._items = []

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._tabs)

        engine = inflect.engine()
        for i in range(5):
            ordinal = engine.ordinal(i + 1)
            scroll = QtWidgets.QScrollArea()
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setWidgetResizable(True)

            item = ADetailerItemSettings(ordinal)
            scroll.setWidget(item)
            self._items.append(item)

            self._tabs.addTab(scroll, ordinal)

        self.setLayout(layout)
        self.loadModels()
        self.loadSamplers()
        self.loadCheckpoints()

    def loadModels(self):
        models = {
            "face_yolov8n.pt",
            "face_yolov8s.pt",
            "hand_yolov8n.pt",
            "person_yolov8n-seg.pt",
            "person_yolov8s-seg.pt",
            "mediapipe_face_full",
            "mediapipe_face_short",
            "mediapipe_face_mesh",
        }

        with contextlib.suppress(BaseException):
            root = KairyoApi.instance().settings.value(AUTOMATIC_PATH)
            root = os.path.join(root, 'models/adetailer')
            if os.path.isdir(root):
                models.update(os.listdir(root))

        models = list(models)
        for item in self._items:
            item.setModels(models)

    def loadSamplers(self):
        for item in self._items:
            item.setSamplerEnabled(False)

        with contextlib.suppress(BaseException):
            url = KairyoApi.instance().settings.value(AUTOMATIC_URL)
            if not url:
                return

            WebuiApi(url, HttpBackend.Qt).samplers().connect(self, self.onSamplersReady).perform()

    def onSamplersReady(self, reply: QNetworkReply):
        if (error := reply.error()) == QNetworkReply.NoError:
            data = reply.readAll()
            data = ujson.loads(data)

            items = [i['name'] for i in data]
            for item in self._items:
                item.setSamplerEnabled(True)
                item.setSamplers(items)
        else:
            print(error)

    def loadCheckpoints(self):
        for item in self._items:
            item.setCheckpointEnabled(False)

        with contextlib.suppress(BaseException):
            url = KairyoApi.instance().settings.value(AUTOMATIC_URL)
            if not url:
                return

            WebuiApi(url, HttpBackend.Qt).sd_models().connect(self, self.onCheckpointsReady).perform()

    def onCheckpointsReady(self, reply: QNetworkReply):
        if (error := reply.error()) == QNetworkReply.NoError:
            data = reply.readAll()
            data = ujson.loads(data)

            items = [i['title'] for i in data]
            for item in self._items:
                item.setCheckpointEnabled(True)
                item.setCheckpoints(items)
        else:
            print(error)
