import torch
import comfy.model_management
from nodes import MAX_RESOLUTION
import random
import yaml
from pathlib import Path
from .utils import validate_and_parse_resolutions
from server import PromptServer


class RandomImageSizeAdvancedYAML:
    """You can select a specific image resolution or have one chosen at random.
    """
    
    def __init__(self):
        """Initialize the node with the appropriate device."""
        self.device = comfy.model_management.intermediate_device()

    # Load resolutions from YAML file
    MODEL_RESOLUTIONS = {}
    ALL_RESOLUTIONS_LIST = []
    RESOLUTIONS_KEY_LIST = []

    try:
        yaml_path = Path(__file__).parent.parent / 'yaml' / 'model_resolutions.yaml'
        with open(yaml_path, 'r') as f:
            MODEL_RESOLUTIONS = yaml.safe_load(f)
            if not isinstance(MODEL_RESOLUTIONS, dict):
                raise KeyError("file is invalid.")
    except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
        print(f"Warning: Could not load model_resolutions.yaml ({e}). Using default resolutions.")
        MODEL_RESOLUTIONS["SDXL"] = [
            "704x1344", "768x1280", "832x1216", "896x1152",
            "1024x1024",
            "1152x896", "1216x832", "1280x768", "1344x704"
        ]
    
    RESOLUTIONS_KEY_LIST.extend(['None', 'All'])
    for k, v in MODEL_RESOLUTIONS.items():
        RESOLUTIONS_KEY_LIST.append(k)
        for i in v:
            ALL_RESOLUTIONS_LIST.append(f'{k} {i}')

    @classmethod
    def INPUT_TYPES(s):
        all_res = s.ALL_RESOLUTIONS_LIST
        all_res_keys = s.RESOLUTIONS_KEY_LIST

        return {
            "required": {
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "step": 1,
                    "display": "number"
                }),
                "random_pick_state": (all_res_keys, {
                    "default": all_res_keys[0],
                }),
                "image_size": (all_res, {
                    "default": all_res[0],
                }),
                "width_override": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": MAX_RESOLUTION,
                    "step": 8,
                    "display": "number"
                }),
                "height_override": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": MAX_RESOLUTION,
                    "step": 8,  
                    "display": "number"
                }),
                "add_random_resolutions": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "add_random_resolutions\nWhen the random selection feature is enabled, it is added to the resolution list. Use commas, semicolons, and spaces to separate. Examples: 704x1344, 1024x1024; 1280x768",
                    "dynamicPrompts": False,
                }),
                "override_random_resolutions": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "override_random_resolutions\nWhen the random selection feature is enabled, resolutions are chosen from the list you provide here. Use commas, semicolons, and spaces to separate them. Example: 704x1344, 1024x1024; 1280x768",
                    "dynamicPrompts": False,
                }),
                "str_result_resolution": ("STRING", {
                    "default": "",
                    # "multiline": True,
                    # "placeholder": "",
                    "dynamicPrompts": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/latent"
    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING")
    RETURN_NAMES = ("LATENT", "width", "height", "str_result_resolution")
    FUNCTION = "execute"

    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(s, *args, **kwargs):
        return float("NaN")

    def execute(
        self,
        batch_size: int,
        random_pick_state: str,
        image_size: str,
        width_override: int = 0,
        height_override: int = 0,
        add_random_resolutions: str = "",
        override_random_resolutions: str = "",
        str_result_resolution: str = "",
        unique_id = None,
        # extra_pnginfo = None,
    ) -> tuple:
        
        resolution = ''
        width, height = 0, 0

        # YAML 파일 로컬마다 다를 경우 오류수정, (validation check 에서 잡히므로 여기 안탐)
        # if random_pick_state not in self.RESOLUTIONS_KEY_LIST or image_size not in self.ALL_RESOLUTIONS_LIST:
        #     PromptServer.instance.send_sync("watdafox-node-fix", {
        #         "node_id": unique_id,
        #         "fix_target_widgets": ["random_pick_state", "image_size"],
        #         "data_type": "json",
        #         "data": {
        #             "random_pick_state": self.RESOLUTIONS_KEY_LIST,
        #             "image_size": self.ALL_RESOLUTIONS_LIST
        #         },
        #     })

        if random_pick_state == 'None':
            resolution = image_size.split(' ', 1)[1]
        else:
            selected_res_list = []

            # 해상도 목록 결정. override 최우선, override 없으면 기본 목록을 가져옴.
            if override_random_resolutions.strip():
                selected_res_list = validate_and_parse_resolutions(override_random_resolutions)
            else:
                if random_pick_state == 'All':
                    selected_res_list = [item.split(' ', 1)[1] for item in self.ALL_RESOLUTIONS_LIST]
                else:
                    selected_res_list = [item for item in self.MODEL_RESOLUTIONS[random_pick_state]]

                if add_random_resolutions.strip():
                    selected_res_list.extend(validate_and_parse_resolutions(add_random_resolutions))

            if not selected_res_list:
                raise ValueError("No resolutions available to choose from. Check your settings.")
            
            resolution = random.choice(selected_res_list)

        try:
            width_str, height_str = resolution.split("x")
            width = int(width_str)
            height = int(height_str)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid resolution format: {resolution}. Expected format: 'NUMBERxNUMBER'")

        # 랜덤기능 활성화 여부 상관없이 w, h 가 0보다 크면 덮어씀 (사용자 입력을 받는 값을 최우선으로 함)
        if width_override > 0:
            width = width_override
        if height_override > 0:
            height = height_override
        
        if not (width_override > 0 or height_override > 0):
            width = (width // 64) * 64
            height = (height // 64) * 64

        latent = torch.zeros([max(1, batch_size), 4, height // 8, width // 8], device=self.device)

        str_result_resolution = f'{width}x{height}'

        # WEB_DIRECTORY 에 정의된 js 파일에서 프론트엔드 데이터처리, param1: event-listener-name, param2: data(json)
        PromptServer.instance.send_sync("watdafox-api", {
            "node_id": unique_id,
            "target_widget_name": "str_result_resolution",
            "data_type": "text",
            "data": str_result_resolution
        })

        return ({"samples": latent}, width, height, str_result_resolution)

