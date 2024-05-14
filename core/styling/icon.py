from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor


def load_icon(
        fn: str,
        fill: str = None,
        *,
        active: str = None,
        activeoff: str = None,
        disabled: str = None,
        disabledoff: str = None,
        normal: str = None,
        normaloff: str = None,
        selected: str = None,
        selectedoff: str = None,
):
    modes = [
        (active, QIcon.Active, QIcon.On),
        (activeoff, QIcon.Active, QIcon.Off),
        (disabled, QIcon.Disabled, QIcon.On),
        (disabledoff, QIcon.Disabled, QIcon.Off),
        (normal, QIcon.Normal, QIcon.On),
        (normaloff, QIcon.Normal, QIcon.Off),
        (selected, QIcon.Selected, QIcon.On),
        (selectedoff, QIcon.Selected, QIcon.Off),
    ]

    q_icon = QIcon()
    for color, mode, state in modes:
        img = QPixmap(fn)
        qp = QPainter(img)
        qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
        qp.fillRect(img.rect(), QColor(color or fill))
        qp.end()

        q_icon.addPixmap(img, mode, state)

    # q_icon.addPixmap(img, QIcon.Selected)
    # q_icon.addPixmap(img, QIcon.Active)
    # q_icon.addPixmap(img, QIcon.Disabled)
    # q_icon.addPixmap(img, QIcon.Normal)

    return q_icon
