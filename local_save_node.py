import os
import torch
from PIL import Image
import numpy as np
from datetime import datetime
from server import PromptServer

class LocalSaveNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "save_path": ("STRING", {"default": "C:/ComfyUI/outputs"}),
                "filename_pattern": ("STRING", {"default": "generated_{date}_{index}"}),
                "file_format": (["PNG", "JPEG"], {"default": "PNG"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "save_images"
    CATEGORY = "image"
    OUTPUT_NODE = True

    def save_images(self, images, save_path, filename_pattern, file_format):
        results = []
        try:
            # 保存先ディレクトリの作成（存在しない場合）
            os.makedirs(save_path, exist_ok=True)
            
            # 現在の日時を取得
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            
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
                
                # ファイル拡張子の設定
                ext = file_format.lower()
                full_path = os.path.join(save_path, f"{filename}.{ext}")
                
                # 画像の保存
                if file_format == "PNG":
                    img.save(full_path, format="PNG")
                else:
                    img.save(full_path, format="JPEG", quality=95)
                
                results.append(full_path)
            
            # 保存完了メッセージの送信
            PromptServer.instance.send_sync("local_save_complete", {
                "message": f"Images saved successfully at: {save_path}",
                "paths": results
            })
            
            return (images,)
            
        except Exception as e:
            error_msg = f"Error saving images: {str(e)}"
            PromptServer.instance.send_sync("local_save_error", {
                "message": error_msg
            })
            raise Exception(error_msg)