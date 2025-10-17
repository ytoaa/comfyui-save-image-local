import torch
import numpy as np
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import base64
from io import BytesIO
from datetime import datetime
from server import PromptServer
import struct
import piexif

class LocalSaveNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "prefix": ("STRING", {"default": "generated"}),
                "file_format": (["PNG", "JPEG", "WEBP"], {"default": "PNG"}),
                "exif_text": ("STRING", {"default": "", "multiline": True}),
                
                # PNG 설정
                "png_compression": ("INT", {"default": 6, "min": 0, "max": 9, "step": 1}),
                "png_optimize": ("BOOLEAN", {"default": True}),
                
                # JPEG 설정
                "jpeg_quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "jpeg_optimize": ("BOOLEAN", {"default": True}),
                "jpeg_progressive": ("BOOLEAN", {"default": False}),
                "jpeg_subsampling": (["4:4:4", "4:2:2", "4:2:0", "4:1:1"], {"default": "4:2:0"}),
                
                # WebP 설정
                "webp_quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "webp_lossless": ("BOOLEAN", {"default": False}),
                "webp_method": ("INT", {"default": 6, "min": 0, "max": 6, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_images"
    CATEGORY = "image"
    OUTPUT_NODE = True

    def process_images(self, images, prefix, file_format, exif_text="", 
                      png_compression=6, png_optimize=True,
                      jpeg_quality=95, jpeg_optimize=True, jpeg_progressive=False, jpeg_subsampling="4:2:0",
                      webp_quality=95, webp_lossless=False, webp_method=6):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_data_list = []
            
            # 배치에 포함된 각 이미지를 처리
            for i in range(len(images)):
                # 이미지 텐서를 PIL 이미지로 변환
                img_tensor = images[i]
                img_numpy = 255. * img_tensor.cpu().numpy()
                img = Image.fromarray(np.clip(img_numpy, 0, 255).astype(np.uint8))
                
                # 메타데이터 준비(실제 삽입은 저장 시점에 수행)
                exif_bytes = None
                pnginfo = None
                xmp_bytes = None
                if exif_text.strip():
                    if file_format == "JPEG":
                        exif_bytes = self._build_jpeg_exif_bytes(img, exif_text)
                    elif file_format == "PNG":
                        pnginfo = self._build_png_text_info(exif_text)
                    elif file_format == "WEBP":
                        # WebP는 EXIF 청크의 UserComment 필드에 직접 저장
                        exif_bytes = self._build_jpeg_exif_bytes(img, exif_text)
                
                # シンプルなファイル名の生成
                filename = f"{prefix}_{timestamp}_{i+1:03d}"
                full_filename = f"{filename}.{file_format.lower()}"
                
                # 이미지를 메모리에 저장한 뒤 Base64로 인코딩
                buffered = BytesIO()
                # 저장 전에 포맷에 맞는 색 공간으로 변환
                if file_format in ("JPEG", "WEBP") and img.mode not in ("RGB",):
                    img = img.convert("RGB")
                save_kwargs = self._get_save_kwargs(file_format, 
                                                   png_compression, png_optimize,
                                                   jpeg_quality, jpeg_optimize, jpeg_progressive, jpeg_subsampling,
                                                   webp_quality, webp_lossless, webp_method)
                # 형식별로 적절한 메타데이터 파라미터를 부여하여 저장
                if file_format == "JPEG" and exif_bytes is not None:
                    img.save(buffered, format="JPEG", exif=exif_bytes, **save_kwargs)
                elif file_format == "PNG" and pnginfo is not None:
                    img.save(buffered, format="PNG", pnginfo=pnginfo, **save_kwargs)
                elif file_format == "WEBP":
                    # WebP는 EXIF 청크의 UserComment 필드에 직접 저장
                    if exif_bytes is not None:
                        img.save(buffered, format="WEBP", exif=exif_bytes, **save_kwargs)
                    else:
                        img.save(buffered, format="WEBP", **save_kwargs)
                else:
                    img.save(buffered, format=file_format, **save_kwargs)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # データをリストに追加
                image_data_list.append({
                    "filename": full_filename,
                    "data": img_str,
                    "format": file_format.lower()
                })
            
            # 클라이언트(브라우저)로 데이터 전송
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
    
    def _add_metadata(self, img, exif_text, file_format):
        """파일 형식에 맞는 메타데이터를 추가"""
        try:
            if file_format == "JPEG":
                return self._add_jpeg_exif(img, exif_text)
            elif file_format == "PNG":
                return self._add_png_metadata(img, exif_text)
            elif file_format == "WEBP":
                return self._add_webp_metadata(img, exif_text)
            else:
                print(f"Warning: Metadata not supported for format {file_format}")
                return img
        except Exception as e:
            print(f"Warning: Could not add metadata for {file_format}: {str(e)}")
            return img
    
    def _add_jpeg_exif(self, img, exif_text):
        """JPEG용 EXIF 메타데이터를 추가"""
        try:
            # 기존 EXIF 데이터를 가져옴
            exif_dict = img.getexif()
            
            # 사용자 주석(UserComment = 37510) 추가
            exif_dict[37510] = exif_text.encode('utf-8')
            
            # 생성 시각 추가
            exif_dict[306] = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            
            # 소프트웨어 정보 추가
            exif_dict[305] = "ComfyUI Local Save Node"
            
            # EXIF 데이터를 이미지에 설정
            img.info['exif'] = exif_dict.tobytes()
            
        except Exception as e:
            print(f"Warning: Could not add JPEG EXIF: {str(e)}")
        
        return img

    def _build_jpeg_exif_bytes(self, img, exif_text):
        """JPEG/WebP용 EXIF 바이트 생성 (piexif 사용)"""
        try:
            # piexif를 사용한 EXIF 데이터 구성
            exif_dict = {
                "0th": {
                    #piexif.ImageIFD.Software: "ComfyUI Local Save Node",
                    #piexif.ImageIFD.Artist: "ComfyUI Local Save Node",
                    piexif.ImageIFD.ImageDescription: exif_text,
                    piexif.ImageIFD.DateTime: datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                },
                "Exif": {
                    piexif.ExifIFD.UserComment: exif_text.encode('utf-8'),
                    piexif.ExifIFD.DateTimeOriginal: datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
                    piexif.ExifIFD.DateTimeDigitized: datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                },
                "GPS": {},
                "1st": {},
                "thumbnail": None
            }
            
            # EXIF 데이터를 바이트로 변환
            return piexif.dump(exif_dict)
            
        except Exception as e:
            print(f"Warning: Could not create EXIF with piexif: {str(e)}")
            return None
    
    def _add_png_metadata(self, img, exif_text):
        """PNG용 텍스트 청크 메타데이터를 추가"""
        try:
            # PNG 텍스트 청크로 메타데이터를 추가
            metadata = {
                'Comment': exif_text,
                'Creation Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Title': 'ComfyUI Generated Image',
                'Author': 'ComfyUI Local Save Node',
                'Copyright': f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
            }
            
            # PNG info에 메타데이터를 추가
            for key, value in metadata.items():
                img.info[key] = value
                
        except Exception as e:
            print(f"Warning: Could not add PNG metadata: {str(e)}")
        
        return img

    def _build_png_text_info(self, exif_text):
        """保存用のPNGテキストチャンク情報を生成"""
        try:
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            metadata = {
                'Comment': exif_text,
                'Creation Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Copyright': f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
            }
            for k, v in metadata.items():
                pnginfo.add_text(k, v)
            return pnginfo
        except Exception:
            return None
    
    def _add_webp_metadata(self, img, exif_text):
        """WebP용 EXIF 메타데이터를 추가 (piexif 사용)"""
        try:
            # piexif를 사용한 EXIF 데이터 구성
            exif_dict = {
                "0th": {
                    #piexif.ImageIFD.Software: "ComfyUI Local Save Node",
                    #piexif.ImageIFD.Artist: "ComfyUI Local Save Node",
                    piexif.ImageIFD.ImageDescription: exif_text,
                    piexif.ImageIFD.DateTime: datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                },
                "Exif": {
                    piexif.ExifIFD.UserComment: exif_text.encode('utf-8'),
                    piexif.ExifIFD.DateTimeOriginal: datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
                    piexif.ExifIFD.DateTimeDigitized: datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                },
                "GPS": {},
                "1st": {},
                "thumbnail": None
            }
            
            # EXIF 데이터를 바이트로 변환하여 이미지에 설정
            exif_bytes = piexif.dump(exif_dict)
            img.info['exif'] = exif_bytes
            
        except Exception as e:
            print(f"Warning: Could not add WebP EXIF metadata: {str(e)}")
        
        return img
    
    def _get_save_kwargs(self, file_format, 
                        png_compression, png_optimize,
                        jpeg_quality, jpeg_optimize, jpeg_progressive, jpeg_subsampling,
                        webp_quality, webp_lossless, webp_method):
        """ファイル形式に応じた保存オプションを取得"""
        if file_format == "PNG":
            return {
                "compress_level": png_compression,
                "optimize": png_optimize
            }
            
        elif file_format == "JPEG":
            # サブサンプリングの変換
            subsampling_map = {
                "4:4:4": 0,
                "4:2:2": 1, 
                "4:2:0": 2,
                "4:1:1": 3
            }
            
            kwargs = {
                "quality": jpeg_quality,
                "optimize": jpeg_optimize,
                "progressive": jpeg_progressive
            }
            
            if jpeg_subsampling in subsampling_map:
                kwargs["subsampling"] = subsampling_map[jpeg_subsampling]
                
            return kwargs
            
        elif file_format == "WEBP":
            if webp_lossless:
                return {
                    "lossless": True,
                    "method": webp_method
                }
            else:
                return {
                    "quality": webp_quality,
                    "method": webp_method
                }
        else:
            return {}