# ckpt, unet, vae,
# int, float, string, 
# sampler, scheduler, detailer scheduler

from .utils import get_checkpoints_list, get_diffusion_models_list, get_weight_dtype_list, get_vae_list, get_ksampler_samplers, get_ksampler_schedulers, get_detailer_scheduler_list

class CheckpointComboParameter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ckpt_name": (get_checkpoints_list(), {
                }),
            }
        }
    
    RETURN_TYPES = (get_checkpoints_list(), "STRING",)
    RETURN_NAMES = ("ckpt_name", "str_ckpt_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    def execute(self, ckpt_name: str,):
        return (ckpt_name, ckpt_name,)
    
class UnetComboParameter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "unet_name": (get_diffusion_models_list(), {
                }),
                "weight_dtype": (get_weight_dtype_list(), {
                })
            }
        }
    
    RETURN_TYPES = (get_diffusion_models_list(), get_weight_dtype_list(), "STRING", "STRING",)
    RETURN_NAMES = ("unet_name", "weight_dtype", "str_unet_name", "str_weight_dtype")
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    def execute(self, unet_name: str, weight_dtype: str,):
        return (unet_name, weight_dtype, unet_name, weight_dtype)

class VAEComboParameter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "vae_name": (get_vae_list(), {
                }),
            }
        }
    
    RETURN_TYPES = (get_vae_list(), "STRING",)
    RETURN_NAMES = ("vae_name", "str_vae_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    def execute(self, vae_name: str,):
        return (vae_name, vae_name,)

class KsamplerSamplersComboParameter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "sampler_name": (get_ksampler_samplers(), {
                }),
            }
        }
    
    RETURN_TYPES = (get_ksampler_samplers(), "STRING",)
    RETURN_NAMES = ("sampler_name", "str_sampler_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    def execute(self, sampler_name: str,):
        return (sampler_name, sampler_name,)

class KsamplerSchedulersComboParameter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "scheduler": (get_ksampler_schedulers(), {
                }),
            }
        }
    
    RETURN_TYPES = (get_ksampler_schedulers(), "STRING",)
    RETURN_NAMES = ("scheduler", "str_scheduler",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    def execute(self, scheduler: str,):
        return (scheduler, scheduler,)
    
class DetailerSchedulerComboParameter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "scheduler": (get_detailer_scheduler_list(), {
                }),
            }
        }
    
    RETURN_TYPES = (get_detailer_scheduler_list(), "STRING",)
    RETURN_NAMES = ("scheduler", "str_scheduler",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/parameter"

    def execute(self, scheduler: str,):
        return (scheduler, scheduler,)
