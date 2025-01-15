import os
import time
import numpy as np
from PIL import Image
import comfy.utils

class SaveImageLocal:
    def __init__(self):
        self.output_dir = None
        self.last_image_path = None

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "images": ("IMAGE",),
            "filename_prefix": ("STRING", {"default": "generated"}),
        }}
    
    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"

    def save_images(self, images, filename_prefix):
        # Clean filename prefix
        filename_prefix = "".join(x for x in filename_prefix if x.isalnum() or x in ('-', '_'))
        if not filename_prefix:
            filename_prefix = "image"
            
        results = []
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Create progress bar for better user feedback
        pbar = comfy.utils.ProgressBar(images.shape[0])
        
        for i, image in enumerate(images):
            # Convert to PNG format
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Generate unique filename
            filename = f"{filename_prefix}_{timestamp}_{i:03d}.png"
            
            # Update progress bar with the current image and filename
            pbar.update_absolute(i, images.shape[0], ("PNG", img, filename))
        
        return {"ui": {"images": results}}

# Node registration
NODE_CLASS_MAPPINGS = {
    "SaveImageLocal": SaveImageLocal
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageLocal": "Save Image (Local)"
}