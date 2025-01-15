import os
from PIL import Image
import numpy as np
import torch
import time

class SaveImageLocal:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "images": ("IMAGE",),
            "output_path": ("STRING", {"default": "outputs"}),
            "filename_prefix": ("STRING", {"default": "generated"}),
        }}
    
    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"

    def save_images(self, images, output_path, filename_prefix):
        # Convert relative path to absolute path
        output_path = os.path.abspath(os.path.expanduser(output_path))
        
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Validate filename prefix (remove any problematic characters)
        filename_prefix = "".join(x for x in filename_prefix if x.isalnum() or x in ('-', '_'))
        if not filename_prefix:
            filename_prefix = "image"
            
        results = []
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        for i, image in enumerate(images):
            # Convert the image from torch tensor to PIL Image
            img_data = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(img_data, 0, 255).astype(np.uint8))
            
            # Generate filename with timestamp and index
            filename = f"{filename_prefix}_{timestamp}_{i:03d}.png"
            filepath = os.path.join(output_path, filename)
            
            # Ensure filepath is not too long
            if len(filepath) >= 255:  # Maximum filename length for most filesystems
                # Use shorter filename format if needed
                short_filename = f"img_{timestamp}_{i:03d}.png"
                filepath = os.path.join(output_path, short_filename)
            
            # Save the image
            img.save(filepath)
            results.append(filepath)
            
        return {"ui": {"images": results}}

# Node registration
NODE_CLASS_MAPPINGS = {
    "SaveImageLocal": SaveImageLocal
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageLocal": "Save Image (Local)"
}