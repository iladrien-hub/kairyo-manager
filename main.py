import ctypes
import inspect
import logging
import os
import sys
from glob import glob
from pathlib import Path

from PyQt5 import QtWidgets, QtGui

from core.api import KairyoApi
from core.extension import KairyoExtension
from core.styling import make_stylesheet, Style
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

    for ext in os.listdir("./extensions"):
        fn = os.path.join("./extensions", ext, f"{ext}.py")

        if not os.path.isfile(fn):
            continue

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


def start_app():
    from mainwindow import MainWindow
    myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(make_stylesheet([Style('QLabel', {'color': 'white'})]))

    win = MainWindow()

    api = KairyoApi(
        user_interface=UserInterface(win)
    )
    load_extensions(api)

    for ext in api.extensions:
        ext.on_setup_ui()

    win.setWindowIcon(QtGui.QIcon(":/mainwindow/Icon512.ico"))

    win.show()
    win.resize(1024, 640)

    app.exec_()


if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s | %(levelname)7s | %(name)16s | %(module)s.%(funcName)s.%(lineno)d: %(message)s",
        level=logging.INFO
    )

    compile_ui()
    start_app()
