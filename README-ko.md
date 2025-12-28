# comfyui-watdafox-nodes

ComfyUI용 커스텀 노드 모음입니다. 해상도 선택, 정수 선택, 문자열 리스트 처리, 출력 경로 생성, 파라미터 묶음 노드를 제공합니다.

## 설치

1. `ComfyUI/custom_nodes/` 디렉터리로 이동합니다.
2. 아래 명령으로 저장소를 클론합니다.
   ```bash
   git clone https://github.com/OhSeongHyeon/comfyui-watdafox-nodes.git
   ```
3. ComfyUI를 재시작합니다.

## 포함된 노드

- latent > RandomImageSizeAdvancedYAML: YAML 프리셋과 런타임 오버라이드로 랜덤/고정 해상도 선택.
- latent > RandomImageSizeAdvanced: 동일 기능이지만 하드코딩된 프리셋 사용.
- number > IntegerPicker: 고정, 증가, 감소, 랜덤 정수 선택.
- number > RandomInteger: 랜덤 온/오프 토글 정수 선택.
- string > UniqueStringList: 콤마 구분 문자열을 고유/중복 리스트로 분리.
- string > UniqueStringListAdvanced: 정규화 옵션을 포함한 고유/중복 분리.
- string > Output Dir By Model Name: 모델명과 시간 기반 출력 경로 생성.
- parameter > BFParameters: base/ups/dt 파라미터 묶음 출력.
- parameter > BFParametersSimple: 자주 쓰는 파라미터 묶음 출력.
- parameter > Checkpoint Arg: 체크포인트 이름 패스스루 + 문자열 출력.
- parameter > Unet Arg: Unet/weight dtype 패스스루 + 문자열 출력.
- parameter > VAE Arg: VAE 이름 패스스루 + 문자열 출력.
- parameter > Ksampler Sampler Arg: sampler 패스스루 + 문자열 출력.
- parameter > Ksampler Scheduler Arg: scheduler 패스스루 + 문자열 출력.
- parameter > Detailer Scheduler Arg: detailer scheduler 패스스루 + 문자열 출력.

## 노드 상세

### latent > RandomImageSizeAdvancedYAML

빈 LATENT를 생성하고 고정 또는 랜덤 해상도 선택을 지원합니다. 프리셋은 `yaml/model_resolutions.yaml`에서 로드되며, 실행 시점에 임시로 추가/대체할 수 있습니다.

핵심 기능
- 모델 키별 YAML 기반 해상도 프리셋.
- 특정 프리셋 그룹 또는 전체 프리셋에서 랜덤 선택.
- `width_override` / `height_override`가 최우선 적용.
- `add_random_resolutions`로 랜덤 풀에 추가.
- `override_random_resolutions`로 랜덤 풀 완전 대체.
- 해상도 입력은 `NUMBERxNUMBER` 형식이며 콤마, 세미콜론, 공백으로 구분.
- 오버라이드가 없으면 64의 배수로 내림 처리.
- 최종 해상도가 UI의 `str_result_1x_resolution`, `str_result_nx_resolution`에 반영됨.
- YAML 파일이 로컬마다 다를 경우 위젯 옵션을 자동으로 재동기화하려고 시도합니다.

입력(주요)
- `random_pick_state`: `None`, `All`, 또는 YAML 키.
- `image_size`: `random_pick_state`가 `None`일 때 사용.
- `width_override` / `height_override`: 최종 해상도를 강제 지정.
- `resolution_multiplier`: `nx_width`/`nx_height`와 `str_result_nx_resolution` 계산용 배율.

출력
- `LATENT`, `width`, `height`, `NX_LATENT`, `nx_width`, `nx_height`, `resolution_multiplier`, `str_result_1x_resolution`, `str_result_nx_resolution`.

### latent > RandomImageSizeAdvanced

`RandomImageSizeAdvancedYAML`과 동작은 동일하지만 `py/random_image_size.py`에 하드코딩된 해상도 리스트를 사용합니다.

### number > IntegerPicker

모드에 따라 정수를 선택합니다.
- `fixed`: 입력값 유지.
- `increment`: `[min_value, max_value]` 범위 내 순환 증가.
- `decrement`: `[min_value, max_value]` 범위 내 순환 감소.
- `randomize`: `[min_value, max_value]` 범위 내 랜덤.

정수와 문자열 버전을 출력하며, UI의 `integer` 위젯도 갱신합니다.

### number > RandomInteger

`random_on_off`가 true이면 `[min, max]` 범위 내 랜덤 정수를 선택합니다. false이면 입력 정수를 그대로 반환합니다. 정수와 문자열을 출력하고 UI의 `integer` 위젯을 갱신합니다.

### string > UniqueStringList

콤마로 구분된 문자열을 분리해 고유 항목과 중복 항목으로 나눕니다. `BREAK`가 포함된 항목은 항상 고유로 처리됩니다. 공백만 있는 항목도 고유 출력에 그대로 유지됩니다.

출력
- `unique_text`: 고유 항목을 콤마로 연결한 문자열.
- `duplicate_text`: 중복 항목을 콤마로 연결한 문자열.

### string > UniqueStringListAdvanced

콤마 구분 문자열을 정규화 옵션과 함께 고유/중복으로 분리합니다.

주요 동작
- `remove_whitespaces`: 공백 정규화 및 빈 토큰 제거.
- `remove_underscore`: `_`를 공백으로 취급.
- 대문자 `BREAK`가 포함된 항목은 항상 고유로 처리.
- 중복 판별은 정규화된 키 기준이며, 중복 출력은 원본 토큰을 유지.

출력
- `unique_text`: 고유 항목 연결 문자열(공백 정리 시 `, `, 아니면 `,`).
- `duplicate_text`: 중복 항목 연결 문자열(`,` 구분).

### string > Output Dir By Model Name

모델명, 접두사, 시간 정보를 조합해 `output_dir`, `file_name`, `full_path`를 생성합니다. 결과는 웹 이벤트로 UI 위젯에 반영됩니다.

주요 입력
- `model_name`: 모델명 또는 경로 문자열.
- `folder_prefix`, `extra_filename`, `extra_number`: 선택적 구성요소.
- `use_first_dir`, `use_ckpt_name`, `use_time_folder`, `use_time_file_name`: 출력 구성 토글.

출력
- `str_model_name`: 모델명 문자열 그대로 출력.
- `full_path`, `output_dir`, `file_name`.

### parameter > BFParameters

base, 업스케일(`ups_*`), 보조(`dt_*`) 파라미터를 묶어서 출력하며, sampler/scheduler 이름의 문자열 버전도 제공합니다.

### parameter > BFParametersSimple

seed, steps, cfg, sampler/scheduler, detailer scheduler, denoise 2개를 묶어서 출력하며 sampler/scheduler 문자열도 제공합니다.

### parameter > Checkpoint Arg / Unet Arg / VAE Arg / Ksampler Sampler Arg / Ksampler Scheduler Arg / Detailer Scheduler Arg

주요 콤보 위젯 값을 그대로 출력하면서 문자열 버전을 함께 제공합니다.

## model_resolutions.yaml 커스터마이징

`yaml/model_resolutions.yaml`을 편집해 프리셋을 추가/수정할 수 있습니다.

예시:

```yaml
SDXL:
  - "1024x1024"
  - "1152x896"
  - "896x1152"

Custom:
  - "800x1200"
  - "1200x800"
```
