"""
AFOLIE Image Size Nodes - 图像缩放节点
提供像素和倍数两种缩放方式
"""

import torch
import numpy as np
from PIL import Image


def tensor2pil(image):
    """Convert tensor to PIL Image"""
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


def pil2tensor(image):
    """Convert PIL Image to tensor"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


# 采样方法列表（两个节点共用）
SAMPLING_METHODS = [
    "两次立方(平滑渐变)",
    "保留细节(扩大)",
    "保留细节2.0",
    "两次立方(较平滑)(扩大)",
    "两次立方(较锐利)(缩减)",
    "邻近(硬边缘)",
    "两次线性"
]


class AFOLIE图像像素缩放:
    """
    图像像素缩放节点
    通过指定宽度和高度来调整图像大小
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "宽度": ("INT", {
                    "default": 512,
                    "min": 2,
                    "max": 2048,
                    "step": 1
                }),
                "高度": ("INT", {
                    "default": 512,
                    "min": 2,
                    "max": 2048,
                    "step": 1
                }),
                "采样方法": (SAMPLING_METHODS,),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "resize_image"
    CATEGORY = "AFOLIE/图像"

    def resize_image(self, 图像, 宽度, 高度, 采样方法):
        """
        使用像素值调整图像大小
        
        Args:
            图像: 输入图像张量
            宽度: 目标宽度（像素）
            高度: 目标高度（像素）
            采样方法: 重新采样算法
        """
        batch_size = 图像.shape[0]
        target_width = 宽度
        target_height = 高度
        
        # 处理批次中的每个图像
        resized_images = []
        
        for i in range(batch_size):
            img = 图像[i]
            
            # 转换为PIL进行高质量重采样
            pil_img = tensor2pil(img)
            
            # 将重采样方法映射到PIL滤镜
            resample_map = {
                "两次立方(平滑渐变)": Image.BICUBIC,
                "保留细节(扩大)": Image.LANCZOS,
                "保留细节2.0": Image.LANCZOS,
                "两次立方(较平滑)(扩大)": Image.BICUBIC,
                "两次立方(较锐利)(缩减)": Image.BICUBIC,
                "邻近(硬边缘)": Image.NEAREST,
                "两次线性": Image.BILINEAR
            }
            
            pil_filter = resample_map.get(采样方法, Image.BICUBIC)
            
            # 使用PIL调整大小
            resized_pil = pil_img.resize((target_width, target_height), pil_filter)
            
            # 转换回张量
            resized_tensor = pil2tensor(resized_pil)
            
            resized_images.append(resized_tensor)
        
        # 将所有图像堆叠回批次
        result = torch.cat(resized_images, dim=0)
        
        return (result,)


class AFOLIE图像倍数缩放:
    """
    图像倍数缩放节点
    通过倍数来调整图像大小
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "倍数": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 12.0,
                    "step": 0.01
                }),
                "采样方法": (SAMPLING_METHODS,),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "resize_image"
    CATEGORY = "AFOLIE/图像"

    def resize_image(self, 图像, 倍数, 采样方法):
        """
        使用倍数调整图像大小
        
        Args:
            图像: 输入图像张量
            倍数: 缩放倍数
            采样方法: 重新采样算法
        """
        batch_size, orig_height, orig_width, channels = 图像.shape
        
        # 根据倍数计算目标尺寸
        target_width = int(orig_width * 倍数)
        target_height = int(orig_height * 倍数)
        
        # 确保尺寸至少为1
        target_width = max(1, target_width)
        target_height = max(1, target_height)
        
        # 处理批次中的每个图像
        resized_images = []
        
        for i in range(batch_size):
            img = 图像[i]
            
            # 转换为PIL进行高质量重采样
            pil_img = tensor2pil(img)
            
            # 将重采样方法映射到PIL滤镜
            resample_map = {
                "两次立方(平滑渐变)": Image.BICUBIC,
                "保留细节(扩大)": Image.LANCZOS,
                "保留细节2.0": Image.LANCZOS,
                "两次立方(较平滑)(扩大)": Image.BICUBIC,
                "两次立方(较锐利)(缩减)": Image.BICUBIC,
                "邻近(硬边缘)": Image.NEAREST,
                "两次线性": Image.BILINEAR
            }
            
            pil_filter = resample_map.get(采样方法, Image.BICUBIC)
            
            # 使用PIL调整大小
            resized_pil = pil_img.resize((target_width, target_height), pil_filter)
            
            # 转换回张量
            resized_tensor = pil2tensor(resized_pil)
            
            resized_images.append(resized_tensor)
        
        # 将所有图像堆叠回批次
        result = torch.cat(resized_images, dim=0)
        
        return (result,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIE图像像素缩放": AFOLIE图像像素缩放,
    "AFOLIE图像倍数缩放": AFOLIE图像倍数缩放
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIE图像像素缩放": "图像像素缩放 📐",
    "AFOLIE图像倍数缩放": "图像倍数缩放 🔢"
}
