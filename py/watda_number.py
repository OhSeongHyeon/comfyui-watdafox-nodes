import random
from server import PromptServer
import hashlib


class CyclicInteger:

    def __init__(self):
        self._before_integer = 0
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
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/number"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("result_integer", "str_result_integer")
    FUNCTION = "execute"

    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        # return float("NaN")  # 항상 재실행
        mode = kwargs.get("mode", None)
        min_value = kwargs.get("min_value", 0)
        max_value = kwargs.get("max_value", 0)

        if mode == "fixed" or min_value == max_value:
            return False
        return float("NaN")

    def execute(self, integer: int = 0, mode: str = "randomize", min_value: int = 0, max_value: int = 0, unique_id = None,):
        if mode == "fixed" or min_value == max_value:
            return (integer, str(integer))

        if min_value > max_value:
            min_value, max_value = max_value, min_value
        
        result_integer = integer
        current_range = max_value - min_value + 1

        match mode:
            case "increment":
                result_integer = (integer - min_value + 1) % current_range + min_value
            case "decrement":
                result_integer = (integer - min_value - 1 + current_range) % current_range + min_value
            case _:  # randomize
                rdint = random.randint(min_value, max_value)
                loop_exit = 100

                # 똑같은거 나올확률 제거
                while loop_exit > 0 and min_value != max_value and rdint == self._before_integer:
                    rdint = random.randint(min_value, max_value)
                    loop_exit -= 1

                result_integer = rdint

        PromptServer.instance.send_sync("watdafox-api", {
            "node_id": unique_id,
            "target_widget_name": "integer",
            "data_type": "text",
            "data": result_integer
        })

        self._before_integer = result_integer
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
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    CATEGORY = "watdafox/number"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("result_integer", "str_result_integer")
    FUNCTION = "execute"

    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(self, *args, **kwargs):
        random_on_off = kwargs.get("random_on_off", True)
        min_value = kwargs.get("min_value", 0)
        max_value = kwargs.get("max_value", 0)

        if not random_on_off or min_value == max_value:
            return False
        return float("NaN")

    def execute(self, integer: int = 0, random_on_off: bool = True, min_value: int = 0, max_value: int = 0, unique_id = None,):
        if random_on_off:
            if min_value > max_value:
                min_value, max_value = max_value, min_value

            # CyclicInteger 과 다르게 똑같은거 나와도 ㄱㅊ
            result_integer = random.randint(min_value, max_value)

            PromptServer.instance.send_sync("watdafox-api", {
                "node_id": unique_id,
                "target_widget_name": "integer",
                "data_type": "text",
                "data": result_integer
            })

            return (result_integer, str(result_integer))

        return (integer, str(integer))