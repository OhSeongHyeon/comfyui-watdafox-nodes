from server import PromptServer
from .utils import get_time, get_detailer_scheduler_list, get_ksampler_samplers, get_ksampler_schedulers
from pathlib import Path
import random
from typing import Any
import comfy
import re


class UniqueStringList:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("unique_text", "duplicate_text",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/string"

    def execute(self, text: str):
        items = text.split(',')
        
        unique_items = []
        duplicate_items = []
        seen_stripped = set()

        for item in items:
            stripped_item_for_check = item.strip()

            if "BREAK" in stripped_item_for_check:
                # 대문자 'BREAK' 키워드가 포함된 항목은 중복 검사에서 제외하고 항상 고유한 것으로 취급
                unique_items.append(item)
            else:
                # 'BREAK' 키워드가 없는 항목에 대해서만 기존 중복 검사 로직을 적용
                stripped_item = stripped_item_for_check
                
                # 공백 제거 후 비어있는 문자열은 중복 검사의 대상이 아니지만,
                # 원본 문자열의 형태를 유지하기 위해 그대로 추가
                if not stripped_item:
                    unique_items.append(item)
                    continue

                if stripped_item not in seen_stripped:
                    unique_items.append(item)
                    seen_stripped.add(stripped_item)
                else:
                    duplicate_items.append(item)
        
        unique_text = ",".join(unique_items)
        duplicate_text = ",".join(duplicate_items)
        
        return (unique_text, duplicate_text,)

class UniqueStringListAdvanced:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "remove_whitespaces": ("BOOLEAN", {
                    "default": True,
                }),
                "remove_underscore": ("BOOLEAN", {
                    "default": False,
                }),
                "text": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("unique_text", "duplicate_text",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/string"

    def execute(self, text: str, remove_whitespaces: bool = True, remove_underscore: bool = False):
        if not text:
            return "", ""

        items = text.split(',')

        unique_items = []
        duplicate_items = []
        seen = set()

        def normalize_for_key(s: str) -> str:
            # 중복 판별용 정규화(비교용)
            if remove_underscore:
                s = s.replace("_", " ")
            if remove_whitespaces:
                # 줄바꿈은 삭제하면 토큰이 붙으니 "공백"으로 바꿔야 함
                s = s.replace("\r", " ").replace("\n", " ")
                s = s.strip()
                s = re.sub(r"\s+", " ", s)  # 내부 공백도 1칸으로
            return s.strip()

        def format_unique(s: str) -> str:
            # Unique 출력용 정규화(표시용)
            if remove_underscore:
                s = s.replace("_", " ")
            if remove_whitespaces:
                s = s.replace("\r", " ").replace("\n", " ")
                s = s.strip()
                s = re.sub(r"\s+", " ", s)
            return s

        for raw in items:
            # Duplicate는 원본을 유지해야 하므로 raw는 손대지 않고 보관용으로만 씀
            key = normalize_for_key(raw)

            # remove_whitespaces=True일 때 ",," 같은 빈 토큰 제거
            if remove_whitespaces and key == "":
                continue

            # 오직 대문자 'BREAK'만 예외 처리 (case-sensitive)
            if "BREAK" in key:
                unique_items.append(format_unique(raw))
                continue

            if key not in seen:
                seen.add(key)
                unique_items.append(format_unique(raw))
            else:
                # duplicate는 원본 그대로
                duplicate_items.append(raw)

        delim_unique = ", " if remove_whitespaces else ","
        delim_dup = ","

        unique_text = delim_unique.join(unique_items)
        duplicate_text = delim_dup.join(duplicate_items)

        return unique_text, duplicate_text


class OuputDirByModelName:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "model_name": ("STRING", {
                    "default": "",
                }),
                "folder_prefix": ("STRING", {
                    "default": "",
                    # "dynamicPrompts": False,
                }),
                "extra_filename": ("STRING", {
                    "default": "",
                    # "dynamicPrompts": False,
                }),
                "extra_number": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "display": "number"
                }),
                "use_first_dir": ("BOOLEAN", {
                    "default": True,
                }),
                "use_ckpt_name": ("BOOLEAN", {
                    "default": True,
                }),
                "use_time_folder": ("BOOLEAN", {
                    "default": True,
                }),
                "use_time_file_name": ("BOOLEAN", {
                    "default": True,
                }),
                "full_path": ("STRING", {
                    "default": "",
                    # "dynamicPrompts": False,
                }),
                "output_dir": ("STRING", {
                    "default": "",
                    # "dynamicPrompts": False,
                }),
                "file_name": ("STRING", {
                    "default": "",
                    # "dynamicPrompts": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("str_model_name", "full_path", "output_dir", "file_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/string"

    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(self, *args, **kwargs):
        return float("NaN")

    def execute(
        self,
        model_name: str = "",
        folder_prefix: str = "",
        extra_filename: str = "",
        extra_number: int = -1,
        use_first_dir: bool = True,
        use_ckpt_name: bool = True,
        use_time_folder: bool = True,
        use_time_file_name: bool = True,
        full_path: str = "",
        output_dir: str = "",
        file_name: str = "",
        unique_id = None,
        # extra_pnginfo = None
    ):
        p = Path(model_name)
        first_dir = p.parts[0] if use_first_dir and len(p.parts) > 1 else ""
        ckpt_file_name = p.stem if use_ckpt_name else ""
        ymd_hms = get_time("%Y-%m-%d %H%M%S").split(" ")

        output_dir = "/".join([x for x in [folder_prefix + first_dir, ckpt_file_name, ymd_hms[0] if use_time_folder else ""] if x.strip()])
        file_name = "-".join([x for x in ["-".join(ymd_hms) if use_time_file_name else "", extra_filename, str(extra_number) if extra_number > -1 else ""] if x.strip()])
        if not file_name:
            file_name = str(random.randint(0, 0xFFFFFFFFFFFFFFFF))

        full_path = "/".join([x for x in [output_dir, file_name] if x.strip()])

        PromptServer.instance.send_sync("watdafox-various-api", {
            "node_id": unique_id,
            "target_widget_names": ["output_dir", "file_name", "full_path"],
            "data_type": "json",
            "data": {
                "full_path": full_path,
                "output_dir": output_dir,
                "file_name": file_name,
            },
        })

        return (model_name, full_path, output_dir, file_name,)


class BFParameters:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "control_after_generate": True, }),

                "steps": ("INT", {"default": 30, "min": 1, "max": 1000, }),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01, }),
                "sampler": (get_ksampler_samplers(), ),
                "scheduler": (get_ksampler_schedulers(), ),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, }),

                "ups_steps": ("INT", {"default": 20, "min": 1, "max": 1000, }),
                "ups_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01, }),
                "ups_sampler": (get_ksampler_samplers(), ),
                "ups_scheduler": (get_ksampler_schedulers(), ),
                "ups_denoise": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, }),

                "dt_steps": ("INT", {"default": 20, "min": 1, "max": 1000, }),
                "dt_cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01, }),
                "dt_sampler": (get_ksampler_samplers(), ),
                "dt_scheduler": (get_detailer_scheduler_list(), ),
                "dt_denoise": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, }),
            }
        }

    RETURN_TYPES = (
        "INT", 
        "INT", "FLOAT", get_ksampler_samplers(), get_ksampler_schedulers(), "FLOAT", 
        "INT", "FLOAT", get_ksampler_samplers(), get_ksampler_schedulers(), "FLOAT", 
        "INT", "FLOAT", get_ksampler_samplers(), get_detailer_scheduler_list(), "FLOAT", 
        "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", 
    )
    RETURN_NAMES = (
        "seed", 
        "steps", "cfg", "sampler", "scheduler", "denoise", 
        "ups_steps", "ups_cfg", "ups_sampler", "ups_scheduler", "ups_denoise", 
        "dt_steps", "dt_cfg", "dt_sampler", "dt_scheduler", "dt_denoise", 
        "str_sampler", "str_scheduler", "str_ups_sampler", "str_ups_scheduler", "str_dt_sampler", "str_dt_scheduler", 
    )
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    # DESCRIPTION = ""

    def execute(
        self, 
        seed: int, 
        steps: int, cfg: float, sampler: str, scheduler: str, denoise: float, 
        ups_steps: int, ups_cfg: float, ups_sampler: str, ups_scheduler: str, ups_denoise: float, 
        dt_steps: int, dt_cfg: float, dt_sampler: str, dt_scheduler: str, dt_denoise: float, 
    ):

        return (
            seed, 
            steps, cfg, sampler, scheduler, denoise, 
            ups_steps, ups_cfg, ups_sampler, ups_scheduler, ups_denoise, 
            dt_steps, dt_cfg, dt_sampler, dt_scheduler, dt_denoise, 
            sampler, scheduler, ups_sampler, ups_scheduler, dt_sampler, dt_scheduler,
        )

class BFParametersSimple:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "control_after_generate": True, }),

                "steps": ("INT", {"default": 30, "min": 1, "max": 1000, }),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01, }),
                "sampler": (get_ksampler_samplers(), ),
                "scheduler": (get_ksampler_schedulers(), ),
                "dt_scheduler": (get_detailer_scheduler_list(), ),
                "denoise1": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, }),
                "denoise2": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.01, "round": 0.001, }),
            }
        }

    RETURN_TYPES = (
        "INT", 
        "INT", "FLOAT", get_ksampler_samplers(), get_ksampler_schedulers(), get_detailer_scheduler_list(), "FLOAT", "FLOAT",
        "STRING", "STRING", 
    )
    RETURN_NAMES = (
        "seed", 
        "steps", "cfg", "sampler", "scheduler", "dt_scheduler", "denoise1", "denoise2",
        "str_sampler", "str_scheduler", 
    )
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    # DESCRIPTION = ""

    def execute(
        self, 
        seed: int, 
        steps: int, cfg: float, sampler: str, scheduler: str, dt_scheduler: str, denoise1: float, denoise2: float,
    ):

        return (
            seed, 
            steps, cfg, sampler, scheduler, dt_scheduler, denoise1, denoise2,
            sampler, scheduler,
        )


