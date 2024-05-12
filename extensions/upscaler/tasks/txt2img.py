import asyncio
import base64
import contextlib
import dataclasses
from abc import ABC
from enum import Enum

from core.webui import WebuiApi
from core.worker import BaseTask


class ProgressStatus(Enum):
    InProgress = 0
    Done = 1


@dataclasses.dataclass(frozen=True)
class ProgressItem:
    status: ProgressStatus
    progress: float
    image: bytes


class Txt2ImgTask(BaseTask, ABC):

    def __init__(self):
        super().__init__()

        self._webui_api = WebuiApi('http://127.0.0.1:7860/')

    async def run_txt2img(self, params):
        try:
            return await self._webui_api.txt2img(params)
        except BaseException:
            await self._webui_api.interrupt()
            raise

    async def txt2img(self, params):
        task = asyncio.create_task(self.run_txt2img(params))

        while not task.done():
            progress = await self._webui_api.progress()

            yield ProgressItem(
                status=ProgressStatus.InProgress,
                progress=progress['progress'],
                image=base64.b64decode(progress['current_image'].encode()) if progress['current_image'] else b''
            )

            if self.cancelled():
                task.cancel()

            await asyncio.sleep(0.25)

        with contextlib.suppress(asyncio.exceptions.CancelledError):
            yield ProgressItem(
                status=ProgressStatus.Done,
                progress=1,
                image=base64.b64decode(task.result()['images'][0].encode())
            )
