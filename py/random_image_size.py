import torch
import comfy.model_management
from nodes import MAX_RESOLUTION
import random
import re
import yaml
import os
from pathlib import Path

class RandomImageSize:
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
        script_path = os.path.realpath(__file__)
        script_dir = os.path.dirname(script_path)
        cst_node_dir = Path(script_dir).resolve().parent
        yaml_path = cst_node_dir / 'yaml' / 'model_resolutions.yaml'

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

    for k, v in MODEL_RESOLUTIONS.items():
        RESOLUTIONS_KEY_LIST.append(k)
        for i in v:
            ALL_RESOLUTIONS_LIST.append(f'{k} {i}')

    @classmethod
    def INPUT_TYPES(s):
        all_res = s.ALL_RESOLUTIONS_LIST
        all_res_keys = ['None', 'All'] + s.RESOLUTIONS_KEY_LIST

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
                "add_random_resolutions": ("STRING",{
                    "default": "",
                    "multiline": True,
                    "placeholder": "add_random_resolutions"
                }),
                "override_random_resolutions": ("STRING",{
                    "default": "",
                    "multiline": True,
                    "placeholder": "override_random_resolutions"
                }),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING")
    RETURN_NAMES = ("LATENT", "width", "height", "str_result_resolution")
    FUNCTION = "execute"
    CATEGORY = "latent/resolution"

    @classmethod
    def IS_CHANGED(s, *args, **kwargs):
        return float("NaN")

    # 콤마, 세미콜론, 공백(하나 이상)을 구분자로 split
    @staticmethod
    def str_split_to_list(input_str):
        parts = re.split(r'[,\s;]+', input_str)
        arr_list = [p.strip() for p in parts if p.strip()]
        return arr_list

    def execute(
        self,
        batch_size: int,
        random_pick_state: str,
        image_size: str,
        width_override: int = 0,
        height_override: int = 0,
        add_random_resolutions: str = "",
        override_random_resolutions: str = "",
    ) -> tuple:
        
        resolution = image_size.split(' ', 1)[1]
        width, height = 0, 0
        
        if random_pick_state != 'None':
            selected_res_list = []
            if random_pick_state == 'All':
                selected_res_list = [item.split(' ', 1)[1] for item in self.ALL_RESOLUTIONS_LIST]
            else:
                selected_res_list = [item.split(' ', 1)[1] for item in self.MODEL_RESOLUTIONS[random_pick_state]]

            if override_random_resolutions == "" and add_random_resolutions != "":
                selected_res_list.extend(RandomImageSize.str_split_to_list(add_random_resolutions))

            if override_random_resolutions != "":
                selected_res_list = RandomImageSize.str_split_to_list(override_random_resolutions)

            resolution = random.choice([res for res in selected_res_list])

        try:
            width_str, height_str = resolution.split("x")
            width = int(width_str)
            height = int(height_str)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid resolution format: {resolution}. Expected format: 'WIDTHxHEIGHT'")

        # 랜덤기능 활성화 여부 상관없이 w, h 가 0보다 크면 덮어씀 (사용자 입력을 받는 값을 최우선으로 함)
        if width_override > 0:
            width = width_override
        if height_override > 0:
            height = height_override
        
        if not (width_override > 0 or height_override > 0):
            width = (width // 64) * 64
            height = (height // 64) * 64

        latent = torch.zeros([max(1, batch_size), 4, height // 8, width // 8], device=self.device)

        return ({"samples": latent}, width, height, f'{width}x{height}') 

