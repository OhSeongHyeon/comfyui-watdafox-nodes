from typing import Any
from .py.random_image_size import RandomImageSizeAdvancedYAML, RandomImageSizeAdvanced
from .py.watda_number import IntegerPicker, RandomInteger
from .py.util_nodes import UniqueStringList, UniqueStringListAdvanced, OuputDirByModelName, BFParameters
# from .py.loader_nodes import CheckpointLoaderWithOuputDirByModelName



NODE_CLASS_MAPPINGS = {
    "RandomImageSizeAdvancedYAML": RandomImageSizeAdvancedYAML,
    "RandomImageSizeAdvanced": RandomImageSizeAdvanced,
    "IntegerPicker": IntegerPicker,
    "RandomInteger": RandomInteger,
    "UniqueStringList": UniqueStringList,
    "UniqueStringListAdvanced": UniqueStringListAdvanced,
    "OuputDirByModelName": OuputDirByModelName,
    # "CheckpointLoaderWithOuputDirByModelName": CheckpointLoaderWithOuputDirByModelName,
    "BFParameters": BFParameters,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomImageSizeAdvancedYAML": "Random Image Size YAML (watdafox)",
    "RandomImageSizeAdvanced": "Random Image Size Advanced (watdafox)",
    "IntegerPicker": "Integer Picker (watdafox)",
    "RandomInteger": "Random Integer (watdafox)",
    "UniqueStringList": "Unique Text (watdafox)",
    "UniqueStringListAdvanced": "Unique Text Advanced (watdafox)",
    "OuputDirByModelName": "Output Dir By Model Name (watdafox)",
    # "CheckpointLoaderWithOuputDirByModelName": "Checkpoint Loader With Dir (watdafox)",
    "BFParameters": "BF Parameters (watdafox)",
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
