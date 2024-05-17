from PyQt5 import QtGui


def cv2_to_qt(cv_img) -> QtGui.QPixmap:
    height, width, channel = cv_img.shape
    bytes_per_line = 4 * width

    return QtGui.QPixmap.fromImage(
        QtGui.QImage(
            cv_img.data,
            width,
            height,
            bytes_per_line,
            QtGui.QImage.Format.Format_RGBA8888
        )
    )