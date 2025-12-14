"""
AFOLIE 图像文件夹节点 - 保存图像到自定义文件夹
"""

import os
import torch
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import json
import folder_paths
from datetime import datetime


def tensor2pil(image):
    """Convert tensor to PIL Image"""
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


class AFOLIE图像文件夹:
    """
    图像文件夹节点
    将图像保存到指定的自定义文件夹路径，而不是默认的output文件夹
    """
    
    def __init__(self):
        self.output_dir = None
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
        self.counter = 0  # 添加计数器
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "文件夹路径": ("STRING", {
                    "default": "E:/AI/ComfyUI_works/output_custom",
                    "multiline": False
                }),
                "文件名前缀": ("STRING", {
                    "default": "AFOLIE",
                    "multiline": False
                }),
                "文件格式": (["png", "jpg", "jpeg", "webp"],),
            },
            "optional": {
                "保存元数据": ("BOOLEAN", {
                    "default": True
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "保存路径")
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "AFOLIE/输出"

    def save_images(self, 图像, 文件夹路径, 文件名前缀="AFOLIE", 文件格式="png", 保存元数据=True):
        """
        保存图像到指定文件夹（最高质量）
        
        Args:
            图像: 输入图像张量
            文件夹路径: 目标文件夹路径
            文件名前缀: 文件名前缀
            文件格式: 保存格式 (png/jpg/jpeg/webp)
            保存元数据: 是否保存元数据
        
        Returns:
            图像: 原始图像（用于链接其他节点）
            保存路径: 保存的文件路径列表
        """
        # 确保文件夹路径存在
        folder_path = 文件夹路径.strip()
        if not folder_path:
            folder_path = "E:/AI/ComfyUI_works/output_custom"
        
        # 创建文件夹（如果不存在）
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"创建文件夹失败: {folder_path}, 错误: {str(e)}")
            # 使用默认路径
            folder_path = os.path.join(os.path.dirname(__file__), "..", "saved_images")
            os.makedirs(folder_path, exist_ok=True)
        
        # 处理文件格式
        if 文件格式 == "jpg":
            文件格式 = "jpeg"
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存的文件路径列表
        saved_paths = []
        
        # 处理批次中的每个图像
        batch_size = 图像.shape[0]
        
        for i in range(batch_size):
            img_tensor = 图像[i]
            
            # 转换为PIL图像
            pil_img = tensor2pil(img_tensor)
            
            # 生成唯一文件名（使用计数器确保不重复）
            filename = f"{文件名前缀}_{timestamp}_{self.counter:04d}.{文件格式}"
            self.counter += 1
            
            # 完整文件路径
            file_path = os.path.join(folder_path, filename)
            
            # 准备保存参数
            save_kwargs = {}
            
            if 文件格式 == "png":
                # 使用最低压缩级别以获得最佳质量（0=无压缩，但文件较大）
                save_kwargs["compress_level"] = 0
                
                # 添加元数据
                if 保存元数据:
                    metadata = PngInfo()
                    metadata.add_text("Software", "ComfyUI - AFOLIE")
                    metadata.add_text("Timestamp", timestamp)
                    metadata.add_text("Prefix", 文件名前缀)
                    save_kwargs["pnginfo"] = metadata
                    
            elif 文件格式 in ["jpeg", "jpg"]:
                # 使用最高质量保存JPEG
                save_kwargs["quality"] = 100
                save_kwargs["optimize"] = True
                # JPEG不支持透明度，需要转换
                if pil_img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', pil_img.size, (255, 255, 255))
                    if pil_img.mode == 'P':
                        pil_img = pil_img.convert('RGBA')
                    background.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode == 'RGBA' else None)
                    pil_img = background
                    
            elif 文件格式 == "webp":
                # 使用最高质量保存WebP
                save_kwargs["quality"] = 100
                save_kwargs["method"] = 6
            
            # 保存图像
            try:
                pil_img.save(file_path, format=文件格式.upper(), **save_kwargs)
                saved_paths.append(file_path)
                print(f"图像已保存: {file_path}")
            except Exception as e:
                print(f"保存图像失败: {file_path}, 错误: {str(e)}")
                saved_paths.append(f"保存失败: {str(e)}")
        
        # 返回原始图像和保存路径
        saved_paths_str = "\n".join(saved_paths)
        
        return {
            "ui": {
                "images": [{"filename": os.path.basename(p), "subfolder": "", "type": "output"} for p in saved_paths if os.path.exists(p)]
            },
            "result": (图像, saved_paths_str)
        }


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIE图像文件夹": AFOLIE图像文件夹
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIE图像文件夹": "图像文件夹 💾"
}
