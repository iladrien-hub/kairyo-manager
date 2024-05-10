import contextlib
import json
import logging
import re

re_param_code = r'\s*([\w ]+):\s*("(?:\\.|[^\\"])+"|[^,]*)(?:,|$)'
re_param = re.compile(re_param_code)
re_imagesize = re.compile(r"^(\d+)x(\d+)$")


def unquote(text):
    if len(text) == 0 or text[0] != '"' or text[-1] != '"':
        return text

    with contextlib.suppress(Exception):
        return json.loads(text)
    return text


def api_request(params: dict):
    return {
        "prompt": params['Prompt'],
        "negative_prompt": params['Negative prompt'],
        # "styles": [
        #     "string"
        # ],
        "seed": int(params['Seed']),
        # "subseed": -1,
        # "subseed_strength": 0,
        # "seed_resize_from_h": -1,
        # "seed_resize_from_w": -1,
        "sampler_name": params['Sampler'],
        # "batch_size": 1,
        # "n_iter": 1,
        "steps": int(params['Steps']),
        "cfg_scale": float(params['CFG scale']),
        "width": int(params['Size-1']),
        "height": int(params['Size-2']),
        # "restore_faces": True,
        # "tiling": True,
        # "do_not_save_samples": False,
        # "do_not_save_grid": False,
        # "eta": 0,
        # "denoising_strength": 0,
        # "s_min_uncond": 0,
        # "s_churn": 0,
        # "s_tmax": 0,
        # "s_tmin": 0,
        # "s_noise": 0,
        "override_settings": {
            "sd_model_checkpoint": f"{params['Model']}.safetensors [{params['Model hash']}]",
            "CLIP_stop_at_last_layers": int(params['Clip skip']),
            "sd_vae": params['VAE']
        },
        # "override_settings_restore_afterwards": False,
        # "refiner_checkpoint": "string",
        # "refiner_switch_at": 0,
        # "disable_extra_networks": False,
        # "comments": {},
        # "enable_hr": False,
        # "firstphase_width": 0,
        # "firstphase_height": 0,
        # "hr_scale": 2,
        # "hr_upscaler": "string",
        # "hr_second_pass_steps": 0,
        # "hr_resize_x": 0,
        # "hr_resize_y": 0,
        # "hr_checkpoint_name": "string",
        # "hr_sampler_name": "string",
        # "hr_prompt": "",
        # "hr_negative_prompt": "",
        # "sampler_index": "Euler",
        # "script_name": "string",
        # "script_args": [],
        # "send_images": True,
        # "save_images": False,
        # "alwayson_scripts": {}
    }


def parse_generation_parameters(x: str):
    res = {}

    prompt = ""
    negative_prompt = ""

    done_with_prompt = False

    *lines, lastline = x.strip().split("\n")
    if len(re_param.findall(lastline)) < 3:
        lines.append(lastline)
        lastline = ''

    for line in lines:
        line = line.strip()
        if line.startswith("Negative prompt:"):
            done_with_prompt = True
            line = line[16:].strip()
        if done_with_prompt:
            negative_prompt += ("" if negative_prompt == "" else "\n") + line
        else:
            prompt += ("" if prompt == "" else "\n") + line

    res["Prompt"] = prompt
    res["Negative prompt"] = negative_prompt

    for k, v in re_param.findall(lastline):
        try:
            if v[0] == '"' and v[-1] == '"':
                v = unquote(v)

            m = re_imagesize.match(v)
            if m is not None:
                res[f"{k}-1"] = m.group(1)
                res[f"{k}-2"] = m.group(2)
            else:
                res[k] = v
        except Exception as e:
            logging.error(f"Error parsing \"{k}: {v}\"", exc_info=e)

    # Missing CLIP skip means it was set to 1 (the default)
    if "Clip skip" not in res:
        res["Clip skip"] = "1"

    hypernet = res.get("Hypernet", None)
    if hypernet is not None:
        res["Prompt"] += f"""<hypernet:{hypernet}:{res.get("Hypernet strength", "1.0")}>"""

    if "Hires resize-1" not in res:
        res["Hires resize-1"] = 0
        res["Hires resize-2"] = 0

    if "Hires sampler" not in res:
        res["Hires sampler"] = "Use same sampler"

    if "Hires checkpoint" not in res:
        res["Hires checkpoint"] = "Use same checkpoint"

    if "Hires prompt" not in res:
        res["Hires prompt"] = ""

    if "Hires negative prompt" not in res:
        res["Hires negative prompt"] = ""

    # restore_old_hires_fix_params(res)

    # Missing RNG means the default was set, which is GPU RNG
    if "RNG" not in res:
        res["RNG"] = "GPU"

    if "Schedule type" not in res:
        res["Schedule type"] = "Automatic"

    if "Schedule max sigma" not in res:
        res["Schedule max sigma"] = 0

    if "Schedule min sigma" not in res:
        res["Schedule min sigma"] = 0

    if "Schedule rho" not in res:
        res["Schedule rho"] = 0

    if "VAE Encoder" not in res:
        res["VAE Encoder"] = "Full"

    if "VAE Decoder" not in res:
        res["VAE Decoder"] = "Full"

    return api_request(res)
