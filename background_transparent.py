"""
AFOLIE 背景透明化节点
将指定颜色的背景转换为透明
"""

import torch
import numpy as np
from PIL import Image
from scipy import ndimage


def tensor2pil(image):
    """Convert tensor to PIL Image (RGB) - handles single image tensor (H, W, C)"""
    img_np = image.cpu().numpy()
    # 确保是 3D 数组 (H, W, C)
    if img_np.ndim == 4:
        img_np = img_np.squeeze(0)
    img_np = np.clip(255. * img_np, 0, 255).astype(np.uint8)
    
    # 根据通道数返回不同模式
    if img_np.shape[2] == 4:
        return Image.fromarray(img_np, mode='RGBA')
    elif img_np.shape[2] == 3:
        return Image.fromarray(img_np, mode='RGB')
    else:
        return Image.fromarray(img_np)


def pil2tensor(image):
    """Convert PIL Image to tensor (supports RGBA) - returns (1, H, W, C)"""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def hex_to_rgb(hex_color):
    """
    将十六进制颜色转换为 RGB 元组
    
    Args:
        hex_color: 十六进制颜色字符串，如 '#ffffff' 或 'ffffff'
    
    Returns:
        (r, g, b) 元组，值范围 0-255
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"无效的十六进制颜色: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(img_array, target_rgb):
    """
    计算图像中每个像素与目标颜色的欧几里得距离
    
    Args:
        img_array: numpy 数组，形状为 (H, W, 3)，值范围 0-255
        target_rgb: 目标颜色 (r, g, b)，值范围 0-255
    
    Returns:
        距离数组，形状为 (H, W)，值范围 0-441.67（sqrt(255^2 * 3)）
    """
    target = np.array(target_rgb, dtype=np.float32)
    diff = img_array.astype(np.float32) - target
    distance = np.sqrt(np.sum(diff ** 2, axis=2))
    return distance


def find_edge_connected_regions(mask):
    """
    找到与图像边缘连通的区域
    
    Args:
        mask: 布尔数组，True 表示匹配目标颜色的像素
    
    Returns:
        布尔数组，True 表示与边缘连通的匹配像素
    """
    h, w = mask.shape
    
    # 创建一个边缘种子掩码
    edge_seed = np.zeros_like(mask, dtype=bool)
    edge_seed[0, :] = mask[0, :]      # 上边缘
    edge_seed[-1, :] = mask[-1, :]    # 下边缘
    edge_seed[:, 0] = mask[:, 0]      # 左边缘
    edge_seed[:, -1] = mask[:, -1]    # 右边缘
    
    # 使用标签连通区域
    labeled_array, num_features = ndimage.label(mask)
    
    # 找到与边缘连通的标签
    edge_labels = set(labeled_array[edge_seed])
    edge_labels.discard(0)  # 移除背景标签
    
    # 创建结果掩码
    edge_connected = np.zeros_like(mask, dtype=bool)
    for label in edge_labels:
        edge_connected |= (labeled_array == label)
    
    return edge_connected


class AFOLIE背景透明化:
    """
    背景透明化节点
    将指定颜色的背景转换为透明
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "透明色值": ("STRING", {
                    "default": "#ffffff",
                    "multiline": False
                }),
                "颜色容差": ("FLOAT", {
                    "default": 10.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.5,
                    "display": "slider"
                }),
                "保护主体内部颜色": ("BOOLEAN", {
                    "default": True
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("图像", "遮罩")
    FUNCTION = "make_transparent"
    CATEGORY = "AFOLIE/图像"

    def make_transparent(self, 图像, 透明色值, 颜色容差, 保护主体内部颜色):
        """
        将指定颜色的背景转换为透明
        
        Args:
            图像: 输入图像张量 (B, H, W, C)
            透明色值: 十六进制颜色字符串，如 '#ffffff'
            颜色容差: 颜色匹配容差百分比 (0-100)
            保护主体内部颜色: 是否保护主体内部的相似颜色
        
        Returns:
            (透明图像 RGBA, 遮罩)
        """
        # 解析目标颜色
        try:
            target_rgb = hex_to_rgb(透明色值)
        except ValueError:
            # 如果颜色无效，默认使用白色
            target_rgb = (255, 255, 255)
        
        batch_size = 图像.shape[0]
        
        # 计算颜色距离阈值
        # 最大距离约为 441.67 (sqrt(255^2 * 3))
        max_distance = np.sqrt(255**2 * 3)
        threshold = (颜色容差 / 100.0) * max_distance
        
        result_images = []
        result_masks = []
        
        for i in range(batch_size):
            img = 图像[i]
            
            # 转换为 PIL 图像
            pil_img = tensor2pil(img)
            
            # 转换为 numpy 数组，值范围 0-255
            img_array = np.array(pil_img)
            
            # 确保只使用 RGB 通道进行颜色距离计算
            if img_array.ndim == 3 and img_array.shape[2] == 4:
                # RGBA 图像，只取 RGB 通道
                rgb_array = img_array[:, :, :3]
            else:
                rgb_array = img_array
            
            # 计算每个像素与目标颜色的距离
            distance = color_distance(rgb_array, target_rgb)
            
            # 创建匹配掩码 (True = 匹配目标颜色，需要透明化)
            match_mask = distance <= threshold
            
            # 如果启用保护主体内部颜色
            if 保护主体内部颜色:
                # 只透明化与边缘连通的区域
                transparent_mask = find_edge_connected_regions(match_mask)
            else:
                transparent_mask = match_mask
            
            # 创建 RGBA 图像
            rgba_array = np.zeros((rgb_array.shape[0], rgb_array.shape[1], 4), dtype=np.uint8)
            rgba_array[:, :, :3] = rgb_array  # RGB 通道（确保是3通道）
            rgba_array[:, :, 3] = 255  # Alpha 通道默认不透明
            rgba_array[transparent_mask, 3] = 0  # 设置透明区域的 alpha 为 0
            
            # 转换为 PIL RGBA 图像，然后转为张量
            rgba_pil = Image.fromarray(rgba_array, mode='RGBA')
            rgba_tensor = pil2tensor(rgba_pil)  # (1, H, W, 4)
            result_images.append(rgba_tensor)
            
            # 创建遮罩 - 从 alpha 通道提取
            # alpha=255 -> 1.0 (前景/主体), alpha=0 -> 0.0 (背景/透明)
            mask_array = (~transparent_mask).astype(np.float32)
            mask_tensor = torch.from_numpy(mask_array).unsqueeze(0)
            result_masks.append(mask_tensor)
        
        # 合并批次
        final_image = torch.cat(result_images, dim=0)  # (B, H, W, 4)
        final_mask = torch.cat(result_masks, dim=0)    # (B, H, W)
        
        return (final_image, final_mask)


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIE背景透明化": AFOLIE背景透明化
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIE背景透明化": "背景透明化 🎨"
}
