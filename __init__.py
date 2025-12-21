from typing import Any
from .py.random_image_size import RandomImageSizeAdvancedYAML, RandomImageSizeAdvanced
from .py.watda_number import IntegerPicker, RandomInteger



NODE_CLASS_MAPPINGS: dict[str, Any] = {
    "RandomImageSizeAdvancedYAML": RandomImageSizeAdvancedYAML,
    "RandomImageSizeAdvanced": RandomImageSizeAdvanced,
    "IntegerPicker": IntegerPicker,
    "RandomInteger": RandomInteger,
}

NODE_DISPLAY_NAME_MAPPINGS: dict[str, Any] = {
    "RandomImageSizeAdvancedYAML": "RandomImageSizeAdvancedYAML",
    "RandomImageSizeAdvanced": "RandomImageSizeAdvanced",
    "IntegerPicker": "IntegerPicker",
    "RandomInteger": "RandomInteger",
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
