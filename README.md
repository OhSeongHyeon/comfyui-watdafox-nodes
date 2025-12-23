# comfyui-watdafox-nodes

A collection of custom nodes for ComfyUI. Adds utility nodes for resolution selection, integer picking, string list processing, output path helpers, and parameter packs.

## Installation

1. Navigate to your `ComfyUI/custom_nodes/` directory.
2. Clone this repository:
   ```bash
   git clone https://github.com/OhSeongHyeon/comfyui-watdafox-nodes.git
   ```
3. Restart ComfyUI.

## Included Nodes

- latent > RandomImageSizeAdvancedYAML: Random or fixed resolution with YAML presets and runtime overrides.
- latent > RandomImageSizeAdvanced: Same behavior, but uses hardcoded presets.
- number > IntegerPicker: Fixed, increment, decrement, or random integer selection.
- number > RandomInteger: Randomize integer on/off toggle.
- string > UniqueStringList: Split comma-separated strings into unique vs duplicate lists.
- string > UniqueStringListAdvanced: Unique/duplicate split with normalization options.
- string > OuputDirByModelName: Build output path components from model name and time.
- parameter > BFParameters: Sampling parameter pack for base/ups/dt groups.

## Node Details

### latent > RandomImageSizeAdvancedYAML

Generates an empty latent and supports fixed or random resolution selection. Presets are loaded from `yaml/model_resolutions.yaml` and can be temporarily extended or overridden at runtime.

Key features
- YAML-based resolution presets per model key.
- Random selection from a preset group or from all presets.
- `width_override` and `height_override` take highest precedence.
- `add_random_resolutions` extends the random pool.
- `override_random_resolutions` replaces the random pool.
- Resolutions accept `NUMBERxNUMBER` entries separated by commas, semicolons, or spaces.
- Width/height are rounded down to multiples of 64 unless overrides are provided.
- The final resolutions are pushed into `str_result_1x_resolution` and `str_result_nx_resolution` in the UI.

Inputs (main)
- `random_pick_state`: `None`, `All`, or a YAML key.
- `image_size`: Used when `random_pick_state` is `None`.
- `width_override` / `height_override`: Force final resolution.
- `resolution_multiplier`: Scale factor used for `nx_width`/`nx_height` and `str_result_nx_resolution`.

Outputs
- `LATENT`, `width`, `height`, `nx_width`, `nx_height`, `str_result_1x_resolution`, `str_result_nx_resolution`.

### latent > RandomImageSizeAdvanced

Same behavior as `RandomImageSizeAdvancedYAML`, but uses hardcoded resolution lists inside `py/random_image_size.py`.

### number > IntegerPicker

Selects an integer based on a mode:
- `fixed`: Keep the incoming value.
- `increment`: Wrap around within `[min_value, max_value]`.
- `decrement`: Wrap around within `[min_value, max_value]`.
- `randomize`: Random integer within `[min_value, max_value]`.

Outputs the integer and a string version of it. Also updates the `integer` widget in the UI.

### number > RandomInteger

When `random_on_off` is true, picks a random integer in `[min, max]`. Otherwise passes through the input integer. Outputs the integer and a string version of it, and updates the `integer` widget in the UI.

### string > UniqueStringList

Splits a comma-separated string and separates unique and duplicate items. Items containing `BREAK` are always treated as unique. Whitespace-only items are preserved in the unique output.

Outputs
- `unique_text`: Comma-joined unique items.
- `duplicate_text`: Comma-joined duplicates.

### string > UniqueStringListAdvanced

Splits a comma-separated string into unique and duplicate lists with normalization options.

Key behavior
- `remove_whitespaces`: Collapses whitespace and removes empty tokens.
- `remove_underscore`: Treats `_` as spaces for comparison/output.
- Items containing uppercase `BREAK` are always treated as unique.
- Duplicate detection uses normalized keys, while duplicate output keeps the raw tokens.

Outputs
- `unique_text`: Joined unique items (`, ` when whitespace removal is enabled, otherwise `,`).
- `duplicate_text`: Joined duplicates (`,` delimiter).

### string > OuputDirByModelName

Builds `output_dir`, `file_name`, and `full_path` from a model name, optional prefixes, and a timestamp. Values are pushed to the UI widgets via the web event listener.

Key inputs
- `model_name`: Model name or path string.
- `folder_prefix`, `extra_filename`, `extra_number`: Optional components.
- `use_first_dir`, `use_ckpt_name`, `use_time_folder`, `use_time_file_name`: Toggle output parts.

### parameter > BFParameters

Parameter pack that outputs base, upscaling (`ups_*`), and secondary (`dt_*`) sampling values plus string versions of sampler/scheduler names for logging or UI use.

## Customizing model_resolutions.yaml

Edit `yaml/model_resolutions.yaml` to define your own resolution presets.

Example:

```yaml
SDXL:
  - "1024x1024"
  - "1152x896"
  - "896x1152"

Custom:
  - "800x1200"
  - "1200x800"
```
