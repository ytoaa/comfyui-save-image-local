English | [日本語](./README_ja.md)

# ComfyUI Local Save Node

This is a custom node for ComfyUI that allows you to directly download generated images to your local PC.

## Features

- Directly save images generated in ComfyUI to your local PC
- Supports downloading in PNG, JPEG, and WebP formats
- Customizable file name prefix
- Automatic generation of file names including timestamps and serial numbers
- Batch processing for downloading multiple images at once
- Custom EXIF text input for image metadata
- Advanced format-specific settings:
  - PNG: Compression level control (0-9)
  - JPEG: Quality control (1-100)
  - WebP: Quality control (1-100) and lossless mode
- Feedback display when saving is complete

## Installation

1. Navigate to the ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes
```

2. Clone this repository:
```bash
git clone https://github.com/your-username/comfyui_local_save.git
```

3. Restart ComfyUI

## How to Use

1. Search for "Local Save Image" in the ComfyUI node browser
2. Add the node and set the following parameters:
   - `prefix`: Prefix for the file name to be saved (default: "generated")
   - `file_format`: Select the save format (PNG/JPEG/WebP)
   - `exif_text`: Custom text to embed in image EXIF metadata (optional)
3. Advanced format-specific settings (dynamically shown based on selected format):

   **PNG Settings:**
   - `png_compression`: PNG compression level (0-9, default: 6)
   - `png_optimize`: Enable PNG optimization (default: true)

   **JPEG Settings:**
   - `jpeg_quality`: JPEG quality (1-100, default: 95)
   - `jpeg_optimize`: Enable JPEG optimization (default: true)
   - `jpeg_progressive`: Enable progressive JPEG (default: false)
   - `jpeg_subsampling`: Color subsampling (4:4:4, 4:2:2, 4:2:0, 4:1:1, default: 4:2:0)

   **WebP Settings:**
   - `webp_quality`: WebP quality (1-100, default: 95)
   - `webp_lossless`: Enable lossless WebP compression (default: false)
   - `webp_method`: WebP compression method (0-6, default: 6)
4. Connect the output of the image generation node to the input of the "Local Save Image" node
5. When you run the workflow, the generated image will be downloaded automatically

## File Name Format

The file name of the saved image is generated in the following format:
```
{prefix}_{timestamp}_{number}.{ext}
```

Example:
```
generated_20250115_112814_001.png
generated_20250115_112814_002.webp
generated_20250115_112814_003.jpeg
```

- `prefix`: Prefix specified by the user
- `timestamp`: Timestamp in YYYYMMdd_HHmmss format
- `number`: 3-digit serial number starting from 001
- `ext`: Selected format (png/jpeg/webp)

## Metadata Support

The node can embed custom text into image metadata using format-appropriate methods:

### JPEG Format
- **EXIF Metadata**: Standard EXIF format
  - **UserComment**: Your custom text from the `exif_text` parameter
  - **DateTime**: Creation timestamp
  - **Software**: "ComfyUI Local Save Node"

### PNG Format
- **Text Chunks**: PNG standard text chunks
  - **Comment**: Your custom text
  - **Software**: "ComfyUI Local Save Node"
  - **Creation Time**: Creation timestamp
  - **Description**: Combined description with your text
  - **Title**: "ComfyUI Generated Image"
  - **Author**: "ComfyUI Local Save Node"
  - **Copyright**: Generation date

### WebP Format
- **EXIF Metadata**: EXIF chunk with UserComment field
  - **UserComment**: Your custom text (with UNICODE encoding)
  - **ImageDescription**: Your custom text
  - **DateTime**: Creation timestamp
  - **DateTimeOriginal**: Creation timestamp
  - **Artist**: "ComfyUI Local Save Node"
  - **Software**: "ComfyUI Local Save Node"

## Viewing Metadata in Honeyview (꿀뷰)

To view the embedded metadata in Honeyview:

1. **Open the saved image** in Honeyview
2. **Right-click** on the image and select **"Properties"** or press **F2**
3. **Go to the "Details" tab** to view EXIF/metadata information
4. **For JPEG**: Look for "User Comment", "Image Description", "Artist", "Software" in the EXIF section
5. **For PNG**: Look for "Comment", "Software", "Description", "Title", "Author" in the metadata section
6. **For WebP**: Look for "User Comment", "Image Description", "Artist", "Software" in the EXIF section

Alternatively, you can use **Ctrl+I** to quickly open the properties dialog.

### Metadata Storage Details

- **JPEG**: EXIF format with UNICODE encoding for UserComment (37510) for maximum compatibility
- **PNG**: Standard PNG text chunks (tEXt/iTXt) for metadata storage
- **WebP**: EXIF chunk with UserComment field for maximum compatibility

## Advanced Settings Guide

### PNG Settings
- **Compression Level (0-9)**: 0 = no compression (largest file), 9 = maximum compression (smallest file)
- **Optimize**: Enables PNG optimization for better compression

### JPEG Settings
- **Quality (1-100)**: 100 = best quality (largest file), 1 = lowest quality (smallest file)
- **Optimize**: Enables JPEG optimization for better compression
- **Progressive**: Creates progressive JPEG for faster loading
- **Subsampling**: Color compression method
  - 4:4:4 = no color compression (best quality)
  - 4:2:2 = moderate color compression
  - 4:2:0 = standard color compression (default)
  - 4:1:1 = high color compression

### WebP Settings
- **Quality (1-100)**: 100 = best quality (largest file), 1 = lowest quality (smallest file)
- **Lossless**: Preserves all image data (ignores quality settings)
- **Method (0-6)**: Compression method, higher values = better compression but slower

## Notes

- **Dynamic UI**: Advanced settings are automatically shown/hidden based on the selected file format
- Depending on your browser settings, downloading multiple files may be restricted
- Please be aware of memory usage when processing a large number of images at once
- WebP format provides excellent compression with quality control
- PNG compression level 0 = no compression (largest file), 9 = maximum compression (smallest file)
- JPEG quality 100 = best quality (largest file), 1 = lowest quality (smallest file)
- WebP lossless mode ignores quality settings and preserves all image data

## License

[MIT License](LICENSE)

## Information for Developers

Dependencies:
```
torch>=2.0.0
Pillow>=9.0.0
numpy>=1.22.0
piexif>=1.1.3
```

Most packages are included in the standard ComfyUI installation. You may need to install `piexif` separately:
```bash
pip install piexif>=1.1.3
```

## Contact

Please submit bug reports and feature requests via GitHub Issues.