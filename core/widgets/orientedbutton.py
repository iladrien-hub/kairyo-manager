from enum import Enum

from PyQt5 import QtWidgets


class OrientedButton(QtWidgets.QPushButton):
    class Orientation(Enum):
        Normal = 0
        West = 1
        East = 2

    def __init__(self, text, parent, orientation: Orientation = Orientation.Normal):
        super(OrientedButton, self).__init__(text, parent)
        self.orientation = orientation

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        if self.orientation == self.Orientation.East:
            painter.rotate(90)
            painter.translate(0, -1 * self.width())
        elif self.orientation == self.Orientation.West:
            painter.rotate(270)
            painter.translate(-1 * self.height(), 0)
        painter.drawControl(QtWidgets.QStyle.CE_PushButton, self.getSyleOptions())

    # def minimumSizeHint(self):
    #     size = super(RotatedButton, self).minimumSizeHint()
    #     if self.orientation in ('east', 'west'):
    #         size.transpose()
    #     return size

    def sizeHint(self):
        size = super(OrientedButton, self).sizeHint()
        if self.orientation in (self.Orientation.East, self.Orientation.West):
            size.transpose()
        return size

    def getSyleOptions(self):
        options = QtWidgets.QStyleOptionButton()
        options.initFrom(self)
        size = options.rect.size()
        if self.orientation in (self.Orientation.East, self.Orientation.West):
            size.transpose()
        options.rect.setSize(size)
        options.features = QtWidgets.QStyleOptionButton.None_
        if self.isFlat():
            options.features |= QtWidgets.QStyleOptionButton.Flat
        if self.menu():
            options.features |= QtWidgets.QStyleOptionButton.HasMenu
        if self.autoDefault() or self.isDefault():
            options.features |= QtWidgets.QStyleOptionButton.AutoDefaultButton
        if self.isDefault():
            options.features |= QtWidgets.QStyleOptionButton.DefaultButton
        if self.isDown() or (self.menu() and self.menu().isVisible()):
            options.state |= QtWidgets.QStyle.State_Sunken
        if self.isChecked():
            options.state |= QtWidgets.QStyle.State_On
        if not self.isFlat() and not self.isDown():
            options.state |= QtWidgets.QStyle.State_Raised

        options.text = self.text()
        options.icon = self.icon()
        options.iconSize = self.iconSize()
        return options

    def setOrientation(self, o: Orientation):
        self.orientation = o
        self.update()
