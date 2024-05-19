from typing import List, Type, Tuple

from PyQt5 import QtCore, QtWidgets


def create_box_layout(
        items: List[QtCore.QObject],
        *,
        proto=QtWidgets.QVBoxLayout,
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 0
):
    layout = proto()
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)

    for item in items:
        if isinstance(item, QtWidgets.QWidget):
            layout.addWidget(item)
        elif isinstance(item, QtWidgets.QLayout):
            layout.addLayout(item)

    return layout


def create_grid_layout(
        items: List[List[QtCore.QObject]],
        *,
        margins: Tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 0
):
    layout = QtWidgets.QGridLayout()
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)

    for r_id, row in enumerate(items):
        for c_id, item in enumerate(row):
            if item is None:
                continue
            if isinstance(item, QtWidgets.QWidget):
                layout.addWidget(item, r_id, c_id)
            elif isinstance(item, QtWidgets.QLayout):
                layout.addLayout(item, r_id, c_id)

    return layout


def layout_to_widget(layout: QtWidgets.QLayout, *, proto=QtWidgets.QWidget):
    wid = proto()
    wid.setLayout(layout)
    return wid
