import abc
import asyncio
import contextlib
import ctypes
import dataclasses
import inspect
import logging
import queue
import threading
import time
from enum import Enum
from typing import Optional, List

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
    progressImage = QtCore.pyqtSignal(bytes)


class BaseTask(abc.ABC):

    def __init__(self):
        self.__cancelled = False

    @abc.abstractmethod
    def run(self, callbacks: Callbacks):
        pass

    def description(self):
        return "Some kind of task. Idk, the developer didn't provide a detailed description."

    def name(self):
        return "Task"

    def cancelled(self):
        return self.__cancelled

    def cancel(self):
        self.__cancelled = True


class TaskStatus(Enum):
    Pending = 1
    Executing = 2
    Finished = 3
    Cancelled = 4
    Cancelling = 5
    Error = 6


@dataclasses.dataclass
class TaskMeta:
    status: TaskStatus
    name: str
    description: str
    task: BaseTask
    time: float


class Worker(QtCore.QObject):
    statusChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.__tasks = queue.Queue()
        self.__tasks_meta = []
        self.__current_task: Optional[TaskMeta] = None

        self.__thread: Optional[Thread] = None
        self.__is_running = False
        self.__callbacks = Callbacks()

    def add_task(self, task: BaseTask):
        task = TaskMeta(
            status=TaskStatus.Pending,
            name=task.name(),
            description=task.description(),
            task=task,
            time=time.time()
        )

        self.__tasks.put(task)
        self.__tasks_meta.append(task)
        self.statusChanged.emit()

    def skip(self):
        if not self.__current_task:
            return

        self.__current_task.status = TaskStatus.Cancelling
        self.__current_task.task.cancel()
        self.statusChanged.emit()

    def start(self):
        if self.__thread is not None:
            return

        self.__thread = Thread(target=self._run)
        self.__thread.start()

    def stop(self):
        self.__is_running = False

        for task in self.__tasks_meta:
            if task.status in (TaskStatus.Pending, TaskStatus.Executing):
                task.task.cancel()

        self.__thread.join(5)
        if self.__thread.is_alive():
            self.__thread.terminate()

    def _poll(self):
        self.__current_task = None
        with contextlib.suppress(queue.Empty):
            self.__current_task = self.__tasks.get(timeout=1)
            if self.__current_task.status != TaskStatus.Pending:
                self.__current_task = None

        return self.__current_task

    def _run(self):
        logging.info("starting worker...")

        self.__is_running = True
        loop = asyncio.new_event_loop()

        while self.__is_running:
            task: TaskMeta = self._poll()
            if task is None:
                continue

            task.status = TaskStatus.Executing
            self.statusChanged.emit()

            try:
                if inspect.iscoroutinefunction(task.task.run):
                    loop.run_until_complete(task.task.run(self.__callbacks))
                else:
                    task.task.run(self.__callbacks)

                task.status = TaskStatus.Cancelled if task.task.cancelled() else TaskStatus.Finished
            except BaseException as e:
                logging.error(f"failed to execute task: {task!r}", exc_info=e)
                task.status = TaskStatus.Error
            finally:
                self.statusChanged.emit()
                self.__callbacks.progress.emit(0)
                self.__callbacks.progressImage.emit(b'')

    @property
    def status(self) -> List[TaskMeta]:
        return list(self.__tasks_meta)

    @property
    def callbacks(self):
        return self.__callbacks

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
