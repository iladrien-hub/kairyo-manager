import copy
import re
import time

from PyQt5 import QtCore

from core.api import KairyoApi
from core.project import Project
from core.worker import Callbacks
from .txt2img import Txt2ImgTask, ProgressStatus
from ..settings.settings import *


class UpscaleProjectTask(Txt2ImgTask):
    __re_eyes_color = re.compile(r'(?P<color>[a-zA-z]*) eyes')

    def __init__(self, project: Project):
        super().__init__()

        self.project = project

    def inflate_params(self, settings: QtCore.QSettings, params: dict):
        params = copy.deepcopy(params)

        eyes_color = self.__re_eyes_color.search(params['prompt'])
        eyes_color = eyes_color.group('color') if eyes_color else ""

        face_features = list(filter(lambda x: x in params['prompt'], settings.value(AD_FACE_FEATURES, [], str)))

        if settings.value(HIRES_FIX_ENABLED, False, bool):
            params |= {
                "enable_hr": True,
                "hr_scale": settings.value(HIRES_FIX_UPSCALE_BY, 1.0, float),
                "hr_upscaler": settings.value(HIRES_FIX_UPSCALER, 'Euler a'),
                "hr_second_pass_steps": settings.value(HIRES_FIX_STEPS, 0, int),
                "denoising_strength": settings.value(HIRES_FIX_DENOISING, 0.4, float),
            }

        for ad_idx in range(5):
            if not settings.value(f"{AD_ENABLED}_{ad_idx}", False, bool):
                continue

            ad = {
                "ad_model": settings.value(f"{AD_MODEL}_{ad_idx}", "", str),
                # "ad_model_classes": "",
                "ad_prompt": settings.value(f"{AD_PROMPT}_{ad_idx}", "", str).format(
                    eyes_color=eyes_color,
                    face_features=", ".join(face_features)
                ),
                "ad_negative_prompt": settings.value(f"{AD_NEG_PROMPT}_{ad_idx}", "", str),
                "ad_confidence": settings.value(f"{AD_MODEL_CONFIDENCE}_{ad_idx}", 0.3, float),
                "ad_mask_k_largest": settings.value(f"{AD_MASK_K_LARGEST}_{ad_idx}", 0, int),
                "ad_mask_min_ratio": settings.value(f"{AD_MASK_MIN_AREA}_{ad_idx}", 0, float),
                "ad_mask_max_ratio": settings.value(f"{AD_MASK_MAX_AREA}_{ad_idx}", 1, float),
                # "ad_dilate_erode": 32,
                # "ad_x_offset": 0,
                # "ad_y_offset": 0,
                # "ad_mask_merge_invert": "None",
                "ad_mask_blur": settings.value(f"{AD_MASK_BLUR}_{ad_idx}", 4, int),
                "ad_denoising_strength": settings.value(f"{AD_DENOISING}_{ad_idx}", 0.4, float),
                # "ad_inpaint_only_masked": True,
                "ad_inpaint_only_masked_padding": settings.value(f"{AD_MASK_PADDING}_{ad_idx}", 0, int),
                "ad_use_inpaint_width_height": settings.value(f"{AD_USE_INPAINT_WIDTH_HEIGHT}_{ad_idx}", False, bool),
                "ad_inpaint_width": settings.value(f"{AD_INPAINT_WIDTH}_{ad_idx}", 512, int),
                "ad_inpaint_height": settings.value(f"{AD_INPAINT_HEIGHT}_{ad_idx}", 512, int),
                # "ad_use_steps": True,
                # "ad_steps": 28,
                # "ad_use_cfg_scale": False,
                # "ad_cfg_scale": 7.0,
                "ad_use_checkpoint": settings.value(f"{AD_USE_CHECKPOINT}_{ad_idx}", False, bool),
                "ad_checkpoint": settings.value(f"{AD_CHECKPOINT}_{ad_idx}", "", str),
                # "ad_use_vae": False,
                # "ad_vae": "Use same VAE",
                "ad_use_sampler": settings.value(f"{AD_USE_SAMPLER}_{ad_idx}", False, bool),
                "ad_sampler": settings.value(f"{AD_SAMPLER}_{ad_idx}", "", str),
                # "ad_use_noise_multiplier": False,
                # "ad_noise_multiplier": 1.0,
                # "ad_use_clip_skip": False,
                # "ad_clip_skip": 1,
                # "ad_restore_face": False,
                # "ad_controlnet_model": "None",
                # "ad_controlnet_module": "None",
                # "ad_controlnet_weight": 1.0,
                # "ad_controlnet_guidance_start": 0.0,
                # "ad_controlnet_guidance_end": 1.0
            }

            alwayson_scripts = params.setdefault('alwayson_scripts', {})
            adetailer = alwayson_scripts.setdefault('ADetailer', {})
            args = adetailer.setdefault('args', [])
            args.append(ad)

        return params

    async def run(self, callbacks: Callbacks):
        settings = KairyoApi.instance().settings

        while not self.cancelled() and (image := self.project.next(upscaled=False)):
            image = self.project.get_image(image)
            params = self.inflate_params(settings, image.params)

            async for item in self.txt2img(params):
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
