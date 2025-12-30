from server import PromptServer
from .utils import get_time, get_checkpoints_list, get_vae_list
from pathlib import Path
import folder_paths
import random
import comfy.sd
from comfy.sd import VAE, CLIP
from comfy.clip_vision import ClipVisionModel
from comfy.model_patcher import ModelPatcher

# 저장경로 생성때문에 로라 다시 로딩하는 현상있음...
class CheckpointLoaderWithOuputDirByModelName:
    def __init__(self):
        self._cache_ckpt: ModelPatcher = None
        self._cache_clip: CLIP = None
        self._cache_vae: VAE = None
        self._cache_ckpt_path: str = None
        self._cache_clip_skip: int = None
        self._cache_vae_name: str = None

    def _sync_paths(self, unique_id, full_path, output_dir, file_name):
        PromptServer.instance.send_sync("watdafox-various-api", {
            "node_id": unique_id,
            "target_widget_names": ["output_dir", "file_name", "full_path"],
            "data_type": "json",
            "data": {
                "full_path": full_path,
                "output_dir": output_dir,
                "file_name": file_name,
            },
        })
    
    def _load_vae(self, vae_name):
        """
        ckpt 에 bake 된 vae 를 사용하고 싶지 않을 경우, 사용자가 선택한 vae 로 로딩
        """
        # print("************** _load_vae 실행 **************")
        vae_path = folder_paths.get_full_path_or_raise("vae", vae_name)
        sd = comfy.utils.load_torch_file(vae_path)
        vae = comfy.sd.VAE(sd=sd)
        vae.throw_exception_if_invalid()
        return vae

    def _load_ckpt(self, ckpt_path: str, output_vae: bool) -> (tuple[ModelPatcher, None, VAE, None] | tuple[ModelPatcher | None, CLIP | None, VAE | None, ClipVisionModel | None] | None):
        """
        model, clip (기본적으로 로딩해야함), vae (선택적 로딩 해도됨)
        """
        # print("************** _load_ckpt 실행 **************")
        # without the ClipVisionModel
        # out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        return comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))

    def _set_last_layer(self, clip, stop_at_clip_layer):
        """
        ckpt 를 로딩했을때 기본 clip skip 이 몇인지는 잘 모르지만, sdxl 은 -2 (a1111 에선 2) 를 고정으로 사용하는게 메인 사용 지침
        """
        # print("************** _set_last_layer 실행 **************")
        clip = clip.clone()  # 원본은 클론인데 여기서도 해야하나?
        clip.clip_layer(stop_at_clip_layer)
        return clip

    @classmethod
    def INPUT_TYPES(self):
        ckpts = get_checkpoints_list()
        vaes = ["Baked VAE"] + get_vae_list()

        return {
            "required": {
                "ckpt_name": (ckpts, {
                }),
                "vae_name": (vaes, {
                }),
                "stop_at_clip_layer": ("INT", {
                    "default": -2, 
                    "min": -24, 
                    "max": 0,  # CLIPSetLastLayer -> original value -1
                    "step": 1
                }),
                "enable_make_path": ("BOOLEAN", {
                    "default": True,
                }),
                "folder_prefix": ("STRING", {
                    "default": "",
                }),
                "extra_filename": ("STRING", {
                    "default": "",
                }),
                "extra_number": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "display": "number",
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
                }),
                "output_dir": ("STRING", {
                    "default": "",
                }),
                "file_name": ("STRING", {
                    "default": "",
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                # "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "ckpt_name", "full_path", "output_dir", "file_name",)
    FUNCTION = "execute"
    CATEGORY = "watdafox/loader"

    # OUTPUT_NODE = True

    """
    loader_nodes.py 의 CheckpointLoaderWithOuputDirByModelName 클래스의 excute 메서드 로직 검증요청
    Checkpoint Load 규칙, 체크포인트 로딩 함수 _load_ckpt, clip layer 수정 함수 _set_last_layer, VAE 로딩 함수 _load_vae
    1. 캐시(_cache_ckpt, _cache_clip, _cache_vae)들 중 하나라도 None 일 경우,
        모델을 로딩하고 캐시에 _cache_ckpt, _cache_clip, _cache_vae, _cache_ckpt_path(ckpt 경로), _cache_clip_skip(stop_at_clip_layer), _cache_vae_name (vae 이름)을 캐싱함
    2. case: 사용자가 체크포인트를 변경하면
    2-1. 캐시의 체크포인트와 사용자가 선택한 체크포인트가 같은지 비교함, 같으면 캐시된 체크포인트를 반환
    2-2. 다르면 사용자가 선택한 체크포인트로 로딩하고 로딩된 체크포인트로 캐싱을함
    2-2-1. 사용자가 Baked VAE 를 선택한 경우 로딩된 체크포인트의 vae 를 사용
    2-2-2. Baked VAE 가 아닐 경우 사용자가 지정한 vae (vae_name)를 로딩함 (_load_vae)
    2-2-3. stop_at_clip_layer 가 0 일 경우 로딩된 체크포인트의 clip 을 그대로 사용
    2-2-4. stop_at_clip_layer 가 0 이 아닐 경우 로딩된 체크포인트의 clip 을 수정 (_set_last_layer)
    3. case: 사용자가 체크포인트는 변경 하지 않고 vae 를 변경한 경우
    3-1. 캐싱된 vae 를 비교 후 같으면 캐싱 vae 반환 아니면 사용자 지정 vae 를 로딩, Baked VAE 일 경우 모델을 다시 로딩하고 2번 규칙을 따름
    4. case: 사용자가 체크포인트는 변경 하지 않고 stop_at_clip_layer 값을 변경한 경우
    4-1. 이전 값과 다르면 항상 체크포인트를 다시 로딩하고 2번 규칙을 따른다
    5. 체크포인트 변경 or stop_at_clip_layer 변경 or Baked VAE 변경 인 경우 이전 값과 비교 했을때 다르면 항상 사용자가 지정한 체크포인트로 다시 로딩해야됨, 
        체크포인트를 로딩할 경우에는 2번 규칙들을 따름
    6. 사용자가 Baked VAE or stop_at_clip_layer 변경 했을때 체크포인트를 다시 캐싱하는 로직이 불편하다면, 
        사용자가 위젯값을 Baked VAE, stop_at_clip_layer = 0 설정 해두고
        comfy 의 기본노드 VAE 로드, CLIP 레이어 설정 노드들을 따로 붙여 놓고 사용하는 방식이 바람직해보임
    """
    def execute(
        self,
        ckpt_name: str = "",
        vae_name: str = "",
        stop_at_clip_layer: int = -2,
        enable_make_path: bool = True,
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
        # extra_pnginfo = None
    ):
        if enable_make_path:
            p = Path(ckpt_name)
            first_dir = p.parts[0] if use_first_dir and len(p.parts) > 1 else ""
            ckpt_file_name = p.stem if use_ckpt_name else ""
            ymd_hms = get_time("%Y-%m-%d %H%M%S").split(" ")

            output_dir = "/".join([x for x in [folder_prefix + first_dir, ckpt_file_name, ymd_hms[0] if use_time_folder else ""] if x.strip()])
            file_name = "-".join([x for x in ["-".join(ymd_hms) if use_time_file_name else "", extra_filename, str(extra_number) if extra_number > -1 else ""] if x.strip()])
            if not file_name:
                file_name = str(random.randint(0, 0xFFFFFFFFFFFFFFFF))

            full_path = "/".join([x for x in [output_dir, file_name] if x.strip()])

            self._sync_paths(unique_id, full_path, output_dir, file_name)
        else:
            if full_path or output_dir or file_name:
                full_path, output_dir, file_name = "", "", ""
                self._sync_paths(unique_id, full_path, output_dir, file_name)

        # print("[BEFORE] self._cache_ckpt:", self._cache_ckpt)
        # print("[BEFORE] self._cache_clip:", self._cache_clip)
        # print("[BEFORE] self._cache_vae:", self._cache_vae)
        # print("[BEFORE] self._cache_ckpt_path:", self._cache_ckpt_path.split("\\")[-1] if self._cache_ckpt_path else self._cache_ckpt_path)
        # print("[BEFORE] self._cache_clip_skip:", self._cache_clip_skip)
        # print("[BEFORE] self._cache_vae_name:", self._cache_vae_name)

        ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)
        is_cache_none = True if (not self._cache_ckpt or not self._cache_clip or not self._cache_vae) else False
        is_using_default_clip = True if (stop_at_clip_layer == 0) else False
        is_using_default_vae = True if (vae_name == "Baked VAE") else False

        # 비교 후 캐시값으로 사용
        if (
            not is_cache_none and 
            self._cache_ckpt_path == ckpt_path and
            self._cache_clip_skip == stop_at_clip_layer and
            self._cache_vae_name == vae_name
        ) :
            return (self._cache_ckpt, self._cache_clip, self._cache_vae, ckpt_name, full_path, output_dir, file_name,)

        if (
            is_cache_none or 
            self._cache_ckpt_path != ckpt_path or 
            self._cache_clip_skip != stop_at_clip_layer or
            (self._cache_vae_name != vae_name and is_using_default_vae)
        ):
            # print(f"모델로딩, is_cache_none: {is_cache_none} or is_using_default_clip: {is_using_default_clip} or is_using_default_vae: {is_using_default_vae}")
            out = self._load_ckpt(ckpt_path, is_using_default_vae)

            self._cache_ckpt = out[0]
            if is_using_default_clip: 
                # print("모델 clip 로딩:", stop_at_clip_layer)
                self._cache_clip = out[1]
            else: 
                # print("수정된 clip 사용:", stop_at_clip_layer)
                self._cache_clip = self._set_last_layer(out[1], stop_at_clip_layer)

            if is_using_default_vae:
                # print("Baked VAE 로딩:", vae_name)
                self._cache_vae = out[2]
            else:
                # print("사용자 VAE 로딩:", vae_name)
                self._cache_vae = self._load_vae(vae_name)

            self._cache_ckpt_path = ckpt_path
            self._cache_clip_skip = stop_at_clip_layer
            self._cache_vae_name = vae_name

        if (
            not is_cache_none and 
            self._cache_ckpt_path == ckpt_path and 
            not is_using_default_vae and 
            self._cache_vae_name != vae_name
        ):
            # print("사용자 VAE 로딩:", vae_name)
            self._cache_vae = self._load_vae(vae_name)
            self._cache_vae_name = vae_name

        # print("[AFTER] self._cache_ckpt:", self._cache_ckpt)
        # print("[AFTER] self._cache_clip:", self._cache_clip)
        # print("[AFTER] self._cache_vae:", self._cache_vae)
        # print("[AFTER] self._cache_ckpt_path:", self._cache_ckpt_path.split("\\")[-1] if self._cache_ckpt_path else self._cache_ckpt_path)
        # print("[AFTER] self._cache_clip_skip:", self._cache_clip_skip)
        # print("[AFTER] self._cache_vae_name:", self._cache_vae_name)

        return (self._cache_ckpt, self._cache_clip, self._cache_vae, ckpt_name, full_path, output_dir, file_name,)

