# Save Image (Local) Node for ComfyUI

This custom node allows you to save generated images directly to your local machine in a specified directory.

## Installation

1. Clone or download this repository into your `ComfyUI/custom_nodes` directory
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Restart ComfyUI

## Usage

1. In the ComfyUI workflow editor, find the node under the "image" category named "Save Image (Local)"
2. Connect your image generation output to this node
3. Configure the following parameters:
   - `output_path`: Directory where images will be saved (default: "outputs")
   - `filename_prefix`: Prefix for the saved image files (default: "generated")
4. Run your workflow. Images will be saved with timestamps in the specified directory

## Output Format

Images are saved with the following naming convention:
`[prefix]_[YYYYMMDD-HHMMSS]_[index].png`

## Requirements

- Python 3.7+
- Pillow
- numpy
- PyTorch