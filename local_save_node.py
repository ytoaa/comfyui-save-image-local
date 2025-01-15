import torch
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
from server import PromptServer

class LocalSaveNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_pattern": ("STRING", {"default": "generated_{date}_{index}"}),
                "file_format": (["PNG", "JPEG"], {"default": "PNG"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_images"
    CATEGORY = "image"
    OUTPUT_NODE = True

    def process_images(self, images, filename_pattern, file_format):
        try:
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_data_list = []
            
            # バッチ内の各画像を処理
            for i, image in enumerate(images):
                # 画像データの変換
                i = 255. * image.cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                
                # ファイル名の生成
                filename = filename_pattern.format(
                    date=current_date,
                    index=str(i).zfill(3)
                )
                full_filename = f"{filename}.{file_format.lower()}"
                
                # 画像をbase64エンコード
                buffered = BytesIO()
                if file_format == "PNG":
                    img.save(buffered, format="PNG")
                else:
                    img.save(buffered, format="JPEG", quality=95)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # データをリストに追加
                image_data_list.append({
                    "filename": full_filename,
                    "data": img_str,
                    "format": file_format.lower()
                })
            
            # クライアントにデータを送信
            PromptServer.instance.send_sync("local_save_data", {
                "images": image_data_list
            })
            
            return (images,)
            
        except Exception as e:
            error_msg = f"Error processing images: {str(e)}"
            PromptServer.instance.send_sync("local_save_error", {
                "message": error_msg
            })
            raise Exception(error_msg)