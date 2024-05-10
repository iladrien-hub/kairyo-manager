import abc
import asyncio
import contextlib
import ctypes
import inspect
import logging
import queue
import threading
from typing import Optional

from PyQt5 import QtCore


class Thread(threading.Thread):

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for _id, thread in threading._active.items():  # noqa
            if thread is self:
                return _id

    def terminate(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)


class Callbacks(QtCore.QObject):
    progress = QtCore.pyqtSignal(int)


class BaseTask(abc.ABC):

    @abc.abstractmethod
    def run(self, callbacks: Callbacks):
        pass


class Worker:

    def __init__(self):
        self.__tasks = queue.Queue()
        self.__thread: Optional[Thread] = None
        self.__is_running = False
        self.__callbacks = Callbacks()

    def add_task(self, task: BaseTask):
        self.__tasks.put(task)

    def start(self):
        if self.__thread is not None:
            return

        self.__thread = Thread(target=self._run)
        self.__thread.start()

    def stop(self):
        self.__is_running = False
        self.__thread.join(5)
        if self.__thread.is_alive():
            self.__thread.terminate()

    def _poll(self):
        with contextlib.suppress(queue.Empty):
            return self.__tasks.get(timeout=1)

    def _run(self):
        logging.info("starting worker...")

        self.__is_running = True
        loop = asyncio.new_event_loop()

        while self.__is_running:
            task: BaseTask = self._poll()
            if task is None:
                continue

            try:
                if inspect.iscoroutinefunction(task.run):
                    loop.run_until_complete(task.run(self.__callbacks))
                else:
                    task.run(self.__callbacks)
            except BaseException as e:
                logging.error(f"failed to execute task: {task!r}", exc_info=e)

    @property
    def callbacks(self):
        return self.__callbacks

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
