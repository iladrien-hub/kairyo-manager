import time

from core.project import Project
from core.worker import Callbacks
from .txt2img import Txt2ImgTask, ProgressStatus


class UpscaleProjectTask(Txt2ImgTask):

    def __init__(self, project: Project):
        super().__init__()

        self.project = project

    async def run(self, callbacks: Callbacks):
        while not self.cancelled() and (image := self.project.next(upscaled=False)):
            image = self.project.get_image(image)

            async for item in self.txt2img(image.params):
                match item.status:
                    case ProgressStatus.InProgress:
                        callbacks.progressImage.emit(item.image)
                        callbacks.progress.emit(int(item.progress * 100))
                    case ProgressStatus.Done:
                        image.update(item.image)
                        image.meta.time_upscaled = time.time()
                        image.add_tag('upscaled')
                        image.save_snapshot('upscaled')

    def description(self):
        return self.project.meta.name

    def name(self):
        return "Upscale Project"
