from server import PromptServer
from .utils import get_time
from pathlib import Path
import random


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
                # 'BREAK' 키워드가 포함된 항목은 중복 검사에서 제외하고 항상 고유한 것으로 취급
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


class OuputDirByModelName:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ckpt_name": ("STRING", {
                    "default": "",
                }),
                "folder_prefix": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "extra_filename": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
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
                    "dynamicPrompts": False,
                }),
                "output_dir": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "file_name": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("ckpt_name", "full_path", "output_dir", "file_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/string"

    OUTPUT_NODE = True

    def execute(
        self,
        ckpt_name: str = "",
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
        extra_pnginfo = None
    ):
        p = Path(ckpt_name)
        first_dir = p.parts[0] if use_first_dir and len(p.parts) > 1 else ""
        _ckpt_name = p.stem if use_ckpt_name else ""
        ymd_hms = get_time("%Y-%m-%d %H%M%S").split(" ")

        output_dir = "/".join([x for x in [folder_prefix + first_dir, _ckpt_name, ymd_hms[0] if use_time_folder else ""] if x.strip()])
        file_name = "-".join([x for x in ["-".join(ymd_hms) if use_time_file_name else "", extra_filename, str(extra_number) if extra_number > -1 else ""] if x.strip()])
        if not file_name:
            file_name = str(random.randint(0, 0xFFFFFFFFFFFFFFFF))

        full_path = "/".join([x for x in [output_dir, file_name] if x.strip()])

        PromptServer.instance.send_sync("watdafox-api-list", {
            "node_id": unique_id,
            "target_widget_names": ["output_dir", "file_name", "full_path"],
            "data_type": "json",
            "data": {
                "full_path": full_path,
                "output_dir": output_dir,
                "file_name": file_name,
            },
        })

        return (ckpt_name, full_path, output_dir, file_name,)


# BF파라미터 노드, ksam|디테일러 샘플러 안들어가는거 콤보 합치기, string concat 노드 만들기