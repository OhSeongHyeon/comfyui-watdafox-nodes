import re
import time
import folder_paths
from typing import List
from datetime import datetime
import comfy

def str_split_to_list(input_str: str) -> List[str]:
    """
    Splits a string by commas, semicolons, and one or more spaces,
    and returns a list of non-empty, stripped strings.
    
    Args:
        input_str: The string to be split.
        
    Returns:
        A list of strings.
    """
    if not input_str:
        return []
    # 콤마, 세미콜론, 공백(하나 이상)을 구분자로 split
    parts = re.split(r'[,\s;]+', input_str)
    arr_list = [p.strip() for p in parts if p.strip()]
    return arr_list

def validate_and_parse_resolutions(input_str: str) -> List[str]:
    """
    Splits a string of resolution values (e.g., "1024x768, 800x600") by common delimiters,
    validates each part against a "NUMBERxNUMBER" format, and returns a list of valid resolutions.
    Raises ValueError if any part does not match the expected format.

    Args:
        input_str: A string containing one or more resolution values, separated by commas, semicolons, or spaces.

    Returns:
        A list of strings, where each string is a valid resolution in "NUMBERxNUMBER" format.
    
    Raises:
        ValueError: If any part of the input string does not conform to the "NUMBERxNUMBER" format.
    """
    if not input_str.strip(): # 빈 문자열이거나 공백만 있는 경우 빈 리스트 반환
        return []

    valid_resolutions = []
    # Re-using str_split_to_list for initial splitting
    resolution_parts = str_split_to_list(input_str)

    resolution_pattern = re.compile(r"^\d+x\d+$")

    for res_str in resolution_parts:
        if resolution_pattern.match(res_str):
            valid_resolutions.append(res_str)
        else:
            raise ValueError(f"Invalid resolution format: '{res_str}'. Expected format: 'NUMBERxNUMBER'")
            
    return valid_resolutions

def get_time(pattern: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Returns the current local time formatted with the given strftime pattern.

    Args:
        pattern: A datetime.strftime-compatible format string.

    Returns:
        A formatted timestamp string for the current local time.
    """
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime(pattern)

# 디테일러 스케줄러는 리스트요소가 ksam과 다름
ADDITIONAL_SCHEDULERS = ['AYS SDXL', 'AYS SD1', 'AYS SVD', 'GITS[coeff=1.2]', 'LTXV[default]', 'OSS FLUX', 'OSS Wan', 'OSS Chroma']
DETAILER_SCHEDULERS = list(comfy.samplers.SCHEDULER_HANDLERS) + ADDITIONAL_SCHEDULERS
def get_detailer_scheduler_list():
    return DETAILER_SCHEDULERS

def get_checkpoints_list():
    return folder_paths.get_filename_list("checkpoints")

def get_diffusion_models_list():
    return folder_paths.get_filename_list("diffusion_models")

WEIGHT_DTYPES = ["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"]
def get_weight_dtype_list():
    return WEIGHT_DTYPES

def get_vae_list():
    return folder_paths.get_filename_list("vae")

def get_ksampler_samplers():
    return comfy.samplers.KSampler.SAMPLERS

def get_ksampler_schedulers():
    return comfy.samplers.KSampler.SCHEDULERS