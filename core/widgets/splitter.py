from PyQt5 import QtWidgets, QtCore


class Splitter(QtWidgets.QSplitter):
    resized = QtCore.pyqtSignal()

    def resizeEvent(self, a0):
        super(Splitter, self).resizeEvent(a0)
        self.resized.emit()
