# comfyui-watdafox-nodes

A collection of custom nodes for ComfyUI, adding useful functionalities to your workflows.

## 📥 Installation

1.  Navigate to your `ComfyUI/custom_nodes/` directory.
2.  Clone this repository:
    ```bash
    git clone https://github.com/OhSeongHyeon/comfyui-watdafox-nodes.git
    ```
3.  Restart ComfyUI.

## ✨ Included Nodes

###  latent > RandomImageSizeAdvancedYAML

This node generates an empty latent and offers **flexible image resolution settings through predefined lists or random selection**. It also supports manual resolution override. The final selected resolution is immediately displayed in the node's UI for convenience.


#### Key Features

*   **YAML-based Resolution Presets**: Define and manage your own resolution lists for specific models (e.g., SDXL, SD 1.5) in the `yaml/model_resolutions.yaml` file.
*   **Random Resolution Selection**: Choose resolutions randomly from a defined list to increase diversity.
*   **Instant Resolution Override**: Use `width_override` and `height_override` to forcefully set desired resolutions, overriding all other settings. This takes the highest precedence.
*   **Dynamic Resolution Addition/Replacement**: Temporarily add resolutions to the random pool or completely replace it at workflow execution time.
*   **Real-time Result Display**: The final selected resolution (especially useful for random picks) is immediately updated in the `str_result_resolution` field, allowing you to see the result before queuing.

#### Parameters (Inputs)

*   `batch_size`: The batch size for the generated latent.
*   `random_pick_state`: Specifies the group of resolutions for random selection. (`None`, `All`, or a key defined in `model_resolutions.yaml`). Setting to `None` disables random picking.
*   `image_size`: Selects a specific resolution to use when `random_pick_state` is set to `None`.
*   `width_override` / `height_override`: If a value greater than 0 is entered, it will override the final resolution. It has the highest priority.
*   `add_random_resolutions`: A list of resolutions to temporarily add to the existing pool for random selection. (e.g., `704x1344, 1024x1024`)
*   `override_random_resolutions`: If provided, only resolutions from this list will be used for random selection. (e.g., `704x1344, 1024x1024`)
*   `str_result_resolution`: This field displays the final selected resolution. (Appears as an input in the UI, but shows the output value).

#### Outputs

*   `LATENT`: An empty latent sample with the determined resolution.
*   `width`: The final determined width value.
*   `height`: The final determined height value.
*   `str_result_resolution`: The final resolution as a string in `widthxheight` format.

#### 💡 Customizing `model_resolutions.yaml`

You can modify the `yaml/model_resolutions.yaml` file directly to create your own resolution presets.

**Example:**

```yaml
SDXL:
  - "1024x1024"
  - "1152x896"
  - "896x1152"

Hope_Your_Custom_Resolutions:
  - "800x1200"
  - "1200x800"
```
