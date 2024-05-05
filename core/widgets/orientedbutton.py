from enum import Enum

from PyQt5 import QtWidgets, QtGui, QtCore


# noinspection PyPep8Naming
class OrientedButton(QtWidgets.QPushButton):
    class Orientation(Enum):
        Normal = 0
        West = 1
        East = 2

    def __init__(self, text, parent, orientation: Orientation = Orientation.Normal):
        super(OrientedButton, self).__init__(text, parent)
        self.orientation = orientation
        self.icon_spacing = 6

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        if self.orientation == self.Orientation.East:
            painter.rotate(90)
            painter.translate(0, -1 * self.width())
        elif self.orientation == self.Orientation.West:
            painter.rotate(270)
            painter.translate(-1 * self.height(), 0)

        options = self.getStyleOptions()
        if not options.icon.isNull():
            sz = options.iconSize
            tmp = options.icon.pixmap(sz)

            sz.setWidth(sz.width() + self.icon_spacing)

            exp = QtGui.QPixmap(sz)
            exp.fill(QtCore.Qt.transparent)  # noqa

            p = QtGui.QPainter(exp)
            p.drawPixmap(QtCore.QRect(QtCore.QPoint(), tmp.size()), tmp)
            p.end()

            options.icon = QtGui.QIcon(exp)

        painter.drawControl(QtWidgets.QStyle.CE_PushButton, options)  # noqa

    # def minimumSizeHint(self):
    #     size = super(RotatedButton, self).minimumSizeHint()
    #     if self.orientation in ('east', 'west'):
    #         size.transpose()
    #     return size

    def sizeHint(self):
        size = super(OrientedButton, self).sizeHint()
        if not self.icon().isNull():
            size.setWidth(size.width() + self.icon_spacing)
        if self.orientation in (self.Orientation.East, self.Orientation.West):
            size.transpose()
        return size

    def getStyleOptions(self):
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
            options.state |= QtWidgets.QStyle.State_Sunken  # noqa
        if self.isChecked():
            options.state |= QtWidgets.QStyle.State_On  # noqa
        if not self.isFlat() and not self.isDown():
            options.state |= QtWidgets.QStyle.State_Raised  # noqa

        options.text = self.text()
        options.icon = self.icon()
        options.iconSize = self.iconSize()
        return options

    def setOrientation(self, o: Orientation):
        self.orientation = o
        self.update()
