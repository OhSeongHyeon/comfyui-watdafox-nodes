import random
from server import PromptServer


class IntegerPicker:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):

        # 0xFFFFFFFFFFFFFFFF = 18446744073709551615 (unsigned 64-bit integer 최대값, 2**64 - 1)
        # MAX_UINT32 = 0xFFFFFFFF  # 4294967295 (unsigned 32-bit max, 2**32 - 1)
        return {
            "required": {
                "integer": ("INT", {
                    "default": 1,
                    "min": -0x80000000,
                    "max": 0x7FFFFFFF,
                }),
                "mode": (["fixed", "increment", "decrement", "randomize"], {
                    "default": "randomize",
                }),
                "min_value": ("INT", {
                    "default": 1,
                    "min": -0x80000000,
                    "max": 0x7FFFFFFF,
                }),
                "max_value": ("INT", {
                    "default": 3,
                    "min": -0x80000000,
                    "max": 0x7FFFFFFF,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/number"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("result_integer", "str_result_integer")
    FUNCTION = "execute"

    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(self, *args, **kwargs):
        return float("NaN")

    def execute(self, integer: int = 0, mode: str = "randomize", min_value: int = 0, max_value: int = 0, unique_id = None, extra_pnginfo = None):
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        
        result_integer = integer
        current_range = max_value - min_value + 1

        if mode == "randomize":
            result_integer = random.randint(min_value, max_value)
        elif mode == "increment":
            result_integer = (integer - min_value + 1) % current_range + min_value
        elif mode == "decrement":
            result_integer = (integer - min_value - 1 + current_range) % current_range + min_value

        PromptServer.instance.send_sync("watdafox-api", {
            "node_id": unique_id,
            "target_widget_name": "integer",
            "data_type": "text",
            "data": result_integer
        })

        return (result_integer, str(result_integer))
    

class RandomInteger:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):

        # 0xFFFFFFFFFFFFFFFF = 18446744073709551615 (unsigned 64-bit integer 최대값, 2**64 - 1)
        # MAX_UINT32 = 0xFFFFFFFF  # 4294967295 (unsigned 32-bit max, 2**32 - 1)
        return {
            "required": {
                "integer": ("INT", {
                    "default": 1,
                    "min": -0x80000000,
                    "max": 0x7FFFFFFF,
                }),
                "random_on_off": ("BOOLEAN", {
                    "default": True,
                }),
                "min": ("INT", {
                    "default": 1,
                    "min": -0x80000000,
                    "max": 0x7FFFFFFF,
                }),
                "max": ("INT", {
                    "default": 3,
                    "min": -0x80000000,
                    "max": 0x7FFFFFFF,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/number"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("result_integer", "str_result_integer")
    FUNCTION = "execute"

    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(self, *args, **kwargs):
        return float("NaN")

    def execute(self, integer: int = 0, random_on_off: bool = True, min: int = 0, max: int = 0, unique_id = None, extra_pnginfo = None):
        if min > max:
            min, max = max, min
        
        result_integer = random.randint(min, max) if random_on_off else integer

        PromptServer.instance.send_sync("watdafox-api", {
            "node_id": unique_id,
            "target_widget_name": "integer",
            "data_type": "text",
            "data": result_integer
        })

        return (result_integer, str(result_integer))