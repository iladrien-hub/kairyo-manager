from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt


class ComparerWindowWidget(QtWidgets.QWidget):

    # ----------------------- Constructor ------------------------

    def __init__(self):
        super().__init__()

        self._left = None
        self._right = None

        self._position = 0.5
        self._pressed = False

    # ---------------------- Public Methods ----------------------

    def set_left(self, p: QtGui.QPixmap):
        self._left = p
        self.update()

    def set_right(self, p: QtGui.QPixmap):
        self._right = p
        self.update()

    # -------------- Protected and Private Methods ---------------

    def _update_position(self, x):
        rect = self._get_rect(self._left)

        new_position = min(max((x - rect.x()) / rect.width(), 0), 1)
        new_position = round(new_position, 4)

        if new_position != self._position:
            self._position = new_position
            self.update()

    def _get_rect(self, pixmap: QtGui.QPixmap):
        width = pixmap.width()
        height = pixmap.height()

        aspect_ratio = width / height

        self_width = self.rect().width()
        self_height = self.rect().height()

        new_width = self_width
        new_height = int(new_width / aspect_ratio)

        if new_height > self_height:
            new_height = self_height
            new_width = int(new_height * aspect_ratio)

        return QtCore.QRect((self_width - new_width) // 2, (self_height - new_height) // 2, new_width, new_height)

    # ----------------- Overrides and Interfaces -----------------

    def paintEvent(self, e):
        if self._left is None or self._right is None:
            return

        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('white'))
        brush.setStyle(Qt.SolidPattern)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QtGui.QPainter.LosslessImageRendering)

        painter.drawPixmap(self._get_rect(self._right), self._right)

        rect = self._get_rect(self._left)
        rect_width = rect.width()
        rect_height = rect.height()

        rect.setWidth(round(rect_width * self._position))

        painter.drawPixmap(rect, self._left, QtCore.QRect(
            0, 0, int(self._left.width() * self._position), self._left.height()
        ))

        line = QtCore.QRect(rect.x() + int(rect_width * self._position), rect.y(), 2, rect.height())
        painter.fillRect(line, brush)

        center = QtCore.QPoint(rect.x() + int(rect_width * self._position) + 1, rect.y() + rect_height // 2)
        painter.setBrush(brush)
        painter.drawEllipse(center, 12, 12)

    def mousePressEvent(self, e):
        self._pressed = True
        self._update_position(e.x())

    def mouseReleaseEvent(self, a0):
        self._pressed = False

    def mouseMoveEvent(self, a0):
        if self._pressed:
            self._update_position(a0.x())
