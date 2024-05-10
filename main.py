import ctypes
import inspect
import logging
import os
import sys
from glob import glob
from pathlib import Path

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSize, QPoint

from core.api import KairyoApi
from core.extension import KairyoExtension
from core.styling.theme import DarkTheme
from core.user_interface import UserInterface


def compile_ui():
    logging.info("compiling ui...")

    # Ui Files
    for fn in glob("./**/resources/*.ui", recursive=True):
        fn = Path(fn)
        logging.info(f"found *.ui file in {fn}...")

        parent = fn.parent.parent.absolute()
        basename = os.path.splitext(fn.name)[0]

        generated = os.path.join(parent, "generated")
        os.makedirs(generated, exist_ok=True)

        output = os.path.join(generated, f"{basename}.py")

        cmd = f"pyuic5 {fn.absolute()} -o {Path(output).absolute()} --import-from=."
        os.system(cmd)

    # Resources
    for fn in glob("./**/resources/*.qrc", recursive=True):
        fn = Path(fn)
        logging.info(f"found *.qrc file in {fn}...")

        parent = fn.parent.parent.absolute()
        basename = os.path.splitext(fn.name)[0]

        generated = os.path.join(parent, "generated")
        os.makedirs(generated, exist_ok=True)

        output = os.path.join(generated, f"{basename}_rc.py")

        cmd = f"pyrcc5 {fn.absolute()} -o {Path(output).absolute()}"
        os.system(cmd)

    logging.info("ui compiled")


def load_extensions(api: KairyoApi):
    logging.info("loading extensions...")

    order = {k: i for i, k in enumerate([
        'projectmanager.py',
        'progress.py',
        'upscaler.py',
    ])}
    extensions = []

    for ext in os.listdir("./extensions"):
        fn = os.path.join("./extensions", ext, f"{ext}.py")

        if not os.path.isfile(fn):
            continue
        extensions.append(fn)

    extensions.sort(key=lambda x: order.get(os.path.basename(x), 65536))

    for fn in extensions:
        with open(fn, encoding="utf-8") as f:
            code = compile(f.read(), fn, "exec")

            tmp = {}
            exec(code, tmp)

            for item in tmp.values():
                if not inspect.isclass(item):
                    continue

                if issubclass(item, KairyoExtension) and item != KairyoExtension:
                    logging.info(f"loading {item.__name__}...")
                    api.register_extension(item(api))

    logging.info(f"extensions loaded: {len(api.extensions)}")


def on_focus_changed(old_widget: QtWidgets.QWidget, new_widget: QtWidgets.QWidget):
    try:
        if old_widget:
            old_widget.window().titlebar().setActive(False)
        if new_widget:
            new_widget.window().titlebar().setActive(True)
    except BaseException as e:
        logging.error("", exc_info=e)


def qtMessageHandler(type: QtCore.QtMsgType, context: QtCore.QMessageLogContext, msg: str):
    if type == QtCore.QtCriticalMsg:  # noqa
        level = logging.CRITICAL
    elif type == QtCore.QtFatalMsg:  # noqa
        level = logging.ERROR
    elif type == QtCore.QtWarningMsg:  # noqa
        level = logging.WARNING
    elif type == QtCore.QtInfoMsg:  # noqa
        level = logging.INFO
    elif type == QtCore.QtDebugMsg:  # noqa
        level = logging.DEBUG
    else:
        level = logging.DEBUG

    logging.log(level, msg)


def start_app():
    from mainwindow import MainWindow
    myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    QtCore.qInstallMessageHandler(qtMessageHandler)
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(make_stylesheet([Style('QLabel', {'color': 'white'})]))

    win = MainWindow()

    api = KairyoApi(
        user_interface=UserInterface(win),
        theme=DarkTheme.from_xml("colors.xml")
    )
    size = api.settings.value('mainWindow/size', QSize(1024, 640), QSize)
    pos = api.settings.value('mainWindow/position', None, QPoint)
    maximized = api.settings.value('mainWindow/maximized', False, bool)

    load_extensions(api)

    win.init()
    win.setStyleSheet(api.theme.make_stylesheet())

    for ext in api.extensions:
        ext.on_setup_ui()

    win.setWindowIcon(QtGui.QIcon(":/mainwindow/Icon512.ico"))
    win.show()

    if maximized:
        win.showMaximized()
    else:
        win.resize(size)
        if pos:
            win.move(pos)

    win.titlebar().updateButtons()

    app.focusChanged.connect(on_focus_changed)
    api.open_last_project()

    with api.worker:
        app.exec_()


if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s | %(levelname)7s | %(name)16s | %(module)s.%(funcName)s.%(lineno)d: %(message)s",
        level=logging.INFO
    )

    compile_ui()
    start_app()
