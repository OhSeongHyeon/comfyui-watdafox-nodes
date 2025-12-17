from typing import Any

from .py.random_image_size import RandomImageSize

NODE_CLASS_MAPPINGS: dict[str, Any] = {
    "RandomImageSize": RandomImageSize,
}

NODE_DISPLAY_NAME_MAPPINGS: dict[str, Any] = {
    "RandomImageSize": "Random Image Size",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
