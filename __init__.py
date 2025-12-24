from .py import random_image_size, watda_number, util_nodes

NODE_CLASS_MAPPINGS = {
    "RandomImageSizeAdvancedYAML": random_image_size.RandomImageSizeAdvancedYAML,
    "RandomImageSizeAdvanced": random_image_size.RandomImageSizeAdvanced,
    "IntegerPicker": watda_number.IntegerPicker,
    "RandomInteger": watda_number.RandomInteger,
    "UniqueStringList": util_nodes.UniqueStringList,
    "UniqueStringListAdvanced": util_nodes.UniqueStringListAdvanced,
    "OuputDirByModelName": util_nodes.OuputDirByModelName,
    "BFParameters": util_nodes.BFParameters,
    "BFParametersSimple": util_nodes.BFParametersSimple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomImageSizeAdvancedYAML": "Random Image Size YAML (watdafox)",
    "RandomImageSizeAdvanced": "Random Image Size Advanced (watdafox)",
    "IntegerPicker": "Integer Picker (watdafox)",
    "RandomInteger": "Random Integer (watdafox)",
    "UniqueStringList": "Unique Text (watdafox)",
    "UniqueStringListAdvanced": "Unique Text Advanced (watdafox)",
    "OuputDirByModelName": "Output Dir By Model Name (watdafox)",
    "BFParameters": "BF Parameters (watdafox)",
    "BFParametersSimple": "BF Parameters Simple (watdafox)",
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
