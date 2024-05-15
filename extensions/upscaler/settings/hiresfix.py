import ujson
from PyQt5 import QtWidgets
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply

from core.api import KairyoApi
from core.settings import AUTOMATIC_URL
from core.webui import WebuiApi
from core.widgets import settings as sw
from core.widgets.forms import LabeledDivider
from .settings import HIRES_FIX_UPSCALER, HIRES_FIX_ENABLED, HIRES_FIX_STEPS, HIRES_FIX_DENOISING, HIRES_FIX_UPSCALE_BY


class HiresFixSettings(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._enabled = sw.BooleanSetting(HIRES_FIX_ENABLED)
        self._enabled.setText('Enabled')

        self._upscaler = sw.OptionsSetting(HIRES_FIX_UPSCALER)

        self._steps = sw.SliderSetting(HIRES_FIX_STEPS)
        self._steps.setRange(1, 150, 0)
        self._steps.setLabel('Hires steps')
        self._steps.setDefault(20)

        self._denoising = sw.SliderSetting(HIRES_FIX_DENOISING)
        self._denoising.setRange(0, 1, 2)
        self._denoising.setLabel('Denoising strength')
        self._denoising.setDefault(0.4)

        self._upscale_by = sw.SliderSetting(HIRES_FIX_UPSCALE_BY)
        self._upscale_by.setRange(1, 4, 2)
        self._upscale_by.setLabel('Upscale by')
        self._upscale_by.setDefault(2)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        self._layout.addWidget(self._enabled)

        self._layout.addWidget(LabeledDivider('Parameters', add_top_margin=True))

        self._form = QtWidgets.QFrame()
        self._form.setEnabled(False)

        form_layout = QtWidgets.QVBoxLayout()
        form_layout.setContentsMargins(16, 0, 0, 0)
        form_layout.setSpacing(12)

        form_layout.addWidget(self._upscaler)
        form_layout.addWidget(self._steps)
        form_layout.addWidget(self._denoising)
        form_layout.addWidget(self._upscale_by)

        self._form.setLayout(form_layout)
        self._layout.addWidget(self._form)

        self._layout.addStretch()

        self.setLayout(self._layout)

        self._enabled.stateChanged.connect(self.on_enabled_stateChanged)

        self.loadUpscalers()

    def loadUpscalers(self):
        self._upscaler.setEnabled(False)

        url = KairyoApi.instance().settings.value(AUTOMATIC_URL)
        if not url:
            return

        qnam = QNetworkAccessManager(self)
        qnam.finished.connect(self.on_upscalers_reply)

        WebuiApi(url, qnam).upscalers()

    def on_upscalers_reply(self, reply: QNetworkReply):
        if (error := reply.error()) == QNetworkReply.NoError:
            self._upscaler.clear()

            data = reply.readAll()
            data = ujson.loads(data)

            items = [i['name'] for i in data]

            self._upscaler.setEnabled(True)
            self._upscaler.addItems(items)
            self._upscaler.restore()
        else:
            print(error)

    def on_enabled_stateChanged(self):
        self._form.setEnabled(self._enabled.isChecked())
