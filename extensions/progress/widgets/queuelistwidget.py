import dataclasses

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QListWidgetItem

from core.api import KairyoApi
from core.styling.icon import load_icon
from core.worker import TaskStatus


@dataclasses.dataclass
class StatusExtras:
    text: str
    icon: QtGui.QIcon
    color: str


class QueueItemWidget(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._nameLabel = QtWidgets.QLabel(self)
        self._nameLabel.setObjectName('queueItemName')

        self._descriptionLabel = QtWidgets.QLabel(self)
        self._descriptionLabel.setObjectName('queueItemDescription')

        self._iconLabel = QtWidgets.QLabel(self)
        self._statusLabel = QtWidgets.QLabel(self)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        name_layout = QtWidgets.QVBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(4)

        name_layout.addWidget(self._nameLabel)
        name_layout.addWidget(self._descriptionLabel)

        status_layout = QtWidgets.QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)
        status_layout.addWidget(self._statusLabel)
        status_layout.addWidget(self._iconLabel)

        layout.addLayout(name_layout)
        layout.addStretch()
        layout.addLayout(status_layout)

        self.setLayout(layout)

    def setName(self, name: str):
        self._nameLabel.setText(name)

    def setDescription(self, description: str):
        self._descriptionLabel.setText(description)

    def setStatus(self, status: StatusExtras):
        if not status:
            return
        self._statusLabel.setText(f'<b style="color: {status.color}">{status.text}</b>')
        self._iconLabel.setPixmap(status.icon.pixmap(16, 16))


class QueueListWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._api = KairyoApi.instance()
        self._statuses = {
            TaskStatus.Pending: StatusExtras(
                text='Pending',
                icon=load_icon(':/progress/clock.svg', self._api.theme.text_200),
                color=self._api.theme.text_200
            ),
            TaskStatus.Executing: StatusExtras(
                text='Executing',
                icon=load_icon(':/progress/play.svg', self._api.theme.text_200),
                color=self._api.theme.text_200
            ),
            TaskStatus.Cancelled: StatusExtras(
                text='Cancelled',
                icon=load_icon(':/progress/ban.svg', self._api.theme.danger_200),
                color=self._api.theme.danger_200
            ),
            TaskStatus.Cancelling: StatusExtras(
                text='Cancelling',
                icon=load_icon(':/progress/ban.svg', self._api.theme.danger_200),
                color=self._api.theme.danger_200
            ),
            TaskStatus.Finished: StatusExtras(
                text='Finished',
                icon=load_icon(':/progress/badge-check.svg', self._api.theme.success_200),
                color=self._api.theme.success_200
            ),
            TaskStatus.Error: StatusExtras(
                text='Error',
                icon=load_icon(':/progress/circle-exclamation.svg', self._api.theme.danger_200),
                color=self._api.theme.danger_200
            ),
        }
        self._order = {v: idx for idx, v in enumerate([
            TaskStatus.Executing,
            TaskStatus.Pending
        ])}

        self._list = QtWidgets.QListWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._list)

        self.setLayout(layout)

        self._api.worker.statusChanged.connect(self.on_worker_statusChanged)
        self.syncList()

    def syncList(self):
        self._list.clear()

        # for status in self._statuses.values():
        tasks = self._api.worker.status
        tasks_sorted = sorted(tasks, key=lambda x: (self._order.get(x.status, 2 ** 16), x.time))

        for task in tasks_sorted:
            # print(item)
            widget = QueueItemWidget(self)
            widget.setName(f'<b style="color: {self._api.theme.text_100}">[{tasks.index(task)}]</b> {task.name}')
            widget.setDescription(task.description)
            widget.setStatus(self._statuses.get(task.status))

            item = QListWidgetItem(self._list)
            item.setSizeHint(widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)

    def on_worker_statusChanged(self):
        self.syncList()
