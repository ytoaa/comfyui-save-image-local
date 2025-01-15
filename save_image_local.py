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
        
        results = []
        for i, image in enumerate(images):
            # Convert the image from torch tensor to PIL Image
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"{filename_prefix}_{timestamp}_{i}.png"
            filepath = os.path.join(output_path, filename)
            
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