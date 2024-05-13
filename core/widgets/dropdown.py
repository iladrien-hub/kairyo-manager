from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy


class DropdownWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._button = QtWidgets.QToolButton(self)
        self._button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self._button.setMenu(QtWidgets.QMenu(self._button))
        self._button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self.textBox = QtWidgets.QTextBrowser(self)

        self._list = QtWidgets.QListWidget()
        self._list.addItems(['one', 'two', 'three', 'four'])

        action = QtWidgets.QWidgetAction(self._button)
        action.setDefaultWidget(self._list)

        self._button.menu().addAction(action)
        layout.addWidget(self._button)

        self.setLayout(layout)
