from server import PromptServer
from .utils import get_time
from pathlib import Path
import folder_paths
import random
import comfy.sd

class CheckpointLoaderWithOuputDirByModelName:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        ckpts = folder_paths.get_filename_list("checkpoints")
        # unets = folder_paths.get_filename_list("diffusion_models")
        # all_models = ckpts + unets

        return {
            "required": {
                "ckpt_name": (ckpts, {
                    "default": ckpts[0],
                }),
                "enable_output_path": ("BOOLEAN", {
                    "default": True,
                }),
                "folder_prefix": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "extra_filename": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "extra_number": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "display": "number"
                }),
                "use_first_dir": ("BOOLEAN", {
                    "default": True,
                }),
                "use_ckpt_name": ("BOOLEAN", {
                    "default": True,
                }),
                "use_time_folder": ("BOOLEAN", {
                    "default": True,
                }),
                "use_time_file_name": ("BOOLEAN", {
                    "default": True,
                }),
                "full_path": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "output_dir": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
                "file_name": ("STRING", {
                    "default": "",
                    "dynamicPrompts": False,
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "ckpt_name", "full_path", "output_dir", "file_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/loader"

    OUTPUT_NODE = True

    def execute(
        self,
        ckpt_name: str = "",
        output_vae=True,
        output_clip=True,
        enable_output_path: bool = True,
        folder_prefix: str = "",
        extra_filename: str = "",
        extra_number: int = -1,
        use_first_dir: bool = True,
        use_ckpt_name: bool = True,
        use_time_folder: bool = True,
        use_time_file_name: bool = True,
        full_path: str = "",
        output_dir: str = "",
        file_name: str = "",
        unique_id = None,
        extra_pnginfo = None
    ):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        # add checkpoint name to the output tuple (without the ClipVisionModel)
        #out = (*out[:3], ckpt_name)

        if enable_output_path:
            p = Path(ckpt_name)
            first_dir = p.parts[0] if use_first_dir and len(p.parts) > 1 else ""
            _ckpt_name = p.stem if use_ckpt_name else ""
            ymd_hms = get_time("%Y-%m-%d %H%M%S").split(" ")

            output_dir = "/".join([x for x in [folder_prefix + first_dir, _ckpt_name, ymd_hms[0] if use_time_folder else ""] if x.strip()])
            file_name = "-".join([x for x in ["-".join(ymd_hms) if use_time_file_name else "", extra_filename, str(extra_number) if extra_number > -1 else ""] if x.strip()])
            if not file_name:
                file_name = str(random.randint(0, 0xFFFFFFFFFFFFFFFF))

            full_path = "/".join([x for x in [output_dir, file_name] if x.strip()])

            PromptServer.instance.send_sync("watdafox-api-list", {
                "node_id": unique_id,
                "target_widget_names": ["output_dir", "file_name", "full_path"],
                "data_type": "json",
                "data": {
                    "full_path": full_path,
                    "output_dir": output_dir,
                    "file_name": file_name,
                },
            })
        else:
            full_path = ""
            output_dir = ""
            file_name = ""

        return (*out[:3], ckpt_name, full_path, output_dir, file_name,)

