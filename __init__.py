from typing import Any
from .py.random_image_size import RandomImageSizeAdvancedYAML


NODE_CLASS_MAPPINGS: dict[str, Any] = {
    "RandomImageSizeAdvancedYAML": RandomImageSizeAdvancedYAML,
}

NODE_DISPLAY_NAME_MAPPINGS: dict[str, Any] = {
    "RandomImageSizeAdvancedYAML": "RandomImageSizeAdvancedYAML",
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
