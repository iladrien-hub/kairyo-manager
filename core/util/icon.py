from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor


def load_icon(fn: str, fill: str = None):
    img = QPixmap(fn)
    qp = QPainter(img)
    qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
    qp.fillRect(img.rect(), QColor(fill))
    qp.end()

    q_icon = QIcon()
    q_icon.addPixmap(img, QIcon.Selected)
    q_icon.addPixmap(img, QIcon.Active)
    q_icon.addPixmap(img, QIcon.Disabled)
    q_icon.addPixmap(QPixmap(fn), QIcon.Normal)

    return q_icon
