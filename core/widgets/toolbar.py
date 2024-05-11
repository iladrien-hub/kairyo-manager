from PyQt5 import QtWidgets, QtGui, QtCore


class ToolBar(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addStretch()

        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setSpacing(3)

        self.setLayout(self._layout)
        self.setFixedHeight(27)

    def addButton(self, icon: QtGui.QIcon, tooltip: str = None):
        button = QtWidgets.QToolButton()

        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(16, 16))
        button.setFixedSize(21, 21)

        if tooltip:
            button.setToolTip(tooltip)

        self._layout.addWidget(button)

        return button
