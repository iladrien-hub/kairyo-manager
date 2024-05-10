import abc
import asyncio
import contextlib
import inspect
import logging
import queue
import threading

from PyQt5 import QtCore


class BaseTask(abc.ABC):

    @abc.abstractmethod
    def run(self, callbacks: 'Worker.Callbacks'):
        pass


class Worker:
    class Callbacks(QtCore.QObject):
        progress = QtCore.pyqtSignal(int)

    def __init__(self):
        self.__tasks = queue.Queue()
        self.__thread = None
        self.__is_running = False
        self.__callbacks = Worker.Callbacks()

    def add_task(self, task: BaseTask):
        self.__tasks.put(task)

    def start(self):
        if self.__thread is not None:
            return

        self.__thread = threading.Thread(target=self._run)
        self.__thread.start()

    def stop(self):
        self.__is_running = False

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
