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

    # Define default resolutions first as a fallback.
    ALL_RESOLUTIONS_LIST = []
    RESOLUTIONS_KEY_LIST = ['None', 'All']
    MODEL_RESOLUTIONS = {
        "SDXL": [
            "704x1344", "768x1280", "832x1216", "896x1152",
            "1024x1024",
            "1152x896", "1216x832", "1280x768", "1344x704"
        ]
    }

    try:
        yaml_path = Path(__file__).parent.parent / 'yaml' / 'model_resolutions.yaml'
        if yaml_path.is_file():
            with open(yaml_path, 'r', encoding = 'utf-8') as f:
                loaded_resolutions = yaml.safe_load(f)
                if not loaded_resolutions:
                    raise KeyError("file is invalid.")
                if isinstance(loaded_resolutions, dict):
                    MODEL_RESOLUTIONS = loaded_resolutions
    except (yaml.YAMLError, IOError, KeyError) as e:
        print(f"Warning: Could not load or parse model_resolutions.yaml ({e}). Using default resolutions.")

    for k, v in MODEL_RESOLUTIONS.items():
        RESOLUTIONS_KEY_LIST.append(k)
        for i in v:
            ALL_RESOLUTIONS_LIST.append(f'{k} {i}')

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "step": 1,
                    "display": "number"
                }),
                "random_pick_state": (self.RESOLUTIONS_KEY_LIST, {
                    # "default": self.RESOLUTIONS_KEY_LIST[0],
                }),
                "image_size": (self.ALL_RESOLUTIONS_LIST, {
                    # "default": self.ALL_RESOLUTIONS_LIST[0],
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
                "resolution_multiplier": ("FLOAT", {
                    "default": 1.5,
                    "min": 0.01,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001, 
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
                "str_result_1x_resolution": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "str_result_nx_resolution": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/latent"
    RETURN_TYPES = ("LATENT", "INT", "INT", "INT", "INT", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("LATENT", "width", "height", "nx_width", "nx_height", "resolution_multiplier", "str_result_1x_resolution", "str_result_nx_resolution")
    FUNCTION = "execute"

    OUTPUT_NODE = True

    # 좀 위험...???
    # 사용 로컬마다 yaml 파일 다를 경우 노드위젯 교정시도
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
        random_pick_state = kwargs.get("random_pick_state")
        image_size = kwargs.get("image_size")
        unique_id = kwargs.get("unique_id")
        #print(f"random_pick_state: {random_pick_state}, image_size: {image_size}, unique_id: {unique_id}")

        if random_pick_state not in self.RESOLUTIONS_KEY_LIST or image_size not in self.ALL_RESOLUTIONS_LIST:
            print('[watdafox-node-fix] Attempted node widget calibration')
            PromptServer.instance.send_sync("watdafox-node-fix", {
                "node_id": unique_id,
                "fix_target_widgets": ["random_pick_state", "image_size"],
                "data_type": "json",
                "data": {
                    "random_pick_state": self.RESOLUTIONS_KEY_LIST,
                    "image_size": self.ALL_RESOLUTIONS_LIST
                },
            })
        return True

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
        resolution_multiplier: float = 1.5,
        add_random_resolutions: str = "",
        override_random_resolutions: str = "",
        str_result_1x_resolution: str = "",
        str_result_nx_resolution: str = "",
        unique_id = None,
        # extra_pnginfo = None,
    ) -> tuple:
        
        resolution = ''
        width, height = 0, 0

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

        str_result_1x_resolution = f'{width}x{height}'

        nx_width, nx_height = int(width * resolution_multiplier), int(height * resolution_multiplier)
        str_result_nx_resolution = f'{nx_width}x{nx_height}'

        # WEB_DIRECTORY 에 정의된 js 파일에서 프론트엔드 데이터처리
        PromptServer.instance.send_sync("watdafox-various-api", {
            "node_id": unique_id,
            "target_widget_names": ["str_result_1x_resolution", "str_result_nx_resolution"],
            "data_type": "json",
            "data": {
                "str_result_1x_resolution": str_result_1x_resolution,
                "str_result_nx_resolution": str_result_nx_resolution,
            },
        })

        return ({"samples": latent}, width, height, nx_width, nx_height, resolution_multiplier, str_result_1x_resolution, str_result_nx_resolution)


# YAML 파일이 아닌 해상도 하드코딩값 사용
class RandomImageSizeAdvanced:
    """You can select a specific image resolution or have one chosen at random.
    """

    def __init__(self):
        """Initialize the node with the appropriate device."""
        self.device = comfy.model_management.intermediate_device()

    ALL_RESOLUTIONS_LIST = []
    RESOLUTIONS_KEY_LIST = ['None', 'All']
    MODEL_RESOLUTIONS = {
        "SDXL": [
            "704x1408", "704x1344", "768x1344", "768x1280", "832x1216", "832x1152", "896x1152", 
            "896x1088", "960x1088", "960x1024", "1024x1024", "1024x960", "1088x960", "1088x896", 
            "1152x896", "1152x832", "1216x832", "1280x768", "1280x704", "1344x768", "1344x704", 
            "1408x704", "1408x640", "1472x704", "1536x640", "1600x640", "1664x576", "1728x576",
        ],
        "Qwen": [
            "928x1664", "1056x1584", "1140x1472", "1328x1328", "1664x928", "1584x1056", 
            "1472x1140",
        ],
        "Flux": [
            "768x1024", "960x1280", "960x1440", "1024x1536", "512x512", "768x768", "1024x1024", 
            "1536x1536", "1024x768", "1280x960", "1440x960", "1536x1024",
        ],
        "Flux2": [
            "1408x2816", "1408x2688", "1536x2688", "1536x2560", "1664x2432", "1664x2304", 
            "1792x2304", "1792x2176", "1920x2176", "1920x2048", "2048x2048", "2048x1920", 
            "2176x1920", "2176x1792", "2304x1792", "2304x1664", "2432x1664", "2560x1536", 
            "2560x1408", "2688x1536", "2688x1408", "2816x1408", "2816x1280", "2944x1408", 
            "3072x1280", "3200x1280", "3328x1152", "3456x1152",
        ]
    }

    for k, v in MODEL_RESOLUTIONS.items():
        RESOLUTIONS_KEY_LIST.append(k)
        for i in v:
            ALL_RESOLUTIONS_LIST.append(f'{k} {i}')

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "step": 1,
                    "display": "number"
                }),
                "random_pick_state": (self.RESOLUTIONS_KEY_LIST, {
                    # "default": self.RESOLUTIONS_KEY_LIST[0],
                }),
                "image_size": (self.ALL_RESOLUTIONS_LIST, {
                    # "default": self.ALL_RESOLUTIONS_LIST[0],
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
                "resolution_multiplier": ("FLOAT", {
                    "default": 1.5,
                    "min": 0.01,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001, 
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
                "str_result_1x_resolution": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "str_result_nx_resolution": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/latent"
    RETURN_TYPES = ("LATENT", "INT", "INT", "INT", "INT", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("LATENT", "width", "height", "nx_width", "nx_height", "resolution_multiplier", "str_result_1x_resolution", "str_result_nx_resolution")
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
        resolution_multiplier: float = 1.5,
        add_random_resolutions: str = "",
        override_random_resolutions: str = "",
        str_result_1x_resolution: str = "",
        str_result_nx_resolution: str = "",
        unique_id = None,
        # extra_pnginfo = None,
    ) -> tuple:
        
        resolution = ''
        width, height = 0, 0

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

        str_result_1x_resolution = f'{width}x{height}'

        nx_width, nx_height = int(width * resolution_multiplier), int(height * resolution_multiplier)
        str_result_nx_resolution = f'{nx_width}x{nx_height}'

        # WEB_DIRECTORY 에 정의된 js 파일에서 프론트엔드 데이터처리, param1: event-listener-name, param2: data(json)
        PromptServer.instance.send_sync("watdafox-various-api", {
            "node_id": unique_id,
            "target_widget_names": ["str_result_1x_resolution", "str_result_nx_resolution"],
            "data_type": "json",
            "data": {
                "str_result_1x_resolution": str_result_1x_resolution,
                "str_result_nx_resolution": str_result_nx_resolution,
            },
        })

        return ({"samples": latent}, width, height, nx_width, nx_height, resolution_multiplier, str_result_1x_resolution, str_result_nx_resolution)