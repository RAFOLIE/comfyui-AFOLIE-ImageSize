"""
AFOLIE Image Size Nodes - 图像缩放节点
提供像素和倍数两种缩放方式，以及像素对齐功能
"""

import os
import subprocess
import tempfile
import torch
import numpy as np
from PIL import Image, ImageDraw


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


class AFOLIE图像网格裁剪:
    """
    图像网格裁剪节点
    根据横向和纵向数量将图像均匀裁剪成多个子图像
    同时输出带网格线的预览图像
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "横向数量": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 20,
                    "step": 1,
                    "tooltip": "水平方向分割数量，0表示不横向裁剪"
                }),
                "纵向数量": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 20,
                    "step": 1,
                    "tooltip": "垂直方向分割数量，0表示不纵向裁剪"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("裁剪图像", "预览图像")
    FUNCTION = "crop_image"
    CATEGORY = "AFOLIE/图像"

    def crop_image(self, 图像, 横向数量, 纵向数量):
        """
        将图像按网格裁剪成多个子图像，同时生成预览图像
        
        Args:
            图像: 输入图像张量
            横向数量: 水平方向分割的块数（列数），0表示不横向裁剪
            纵向数量: 垂直方向分割的块数（行数），0表示不纵向裁剪
        
        Returns:
            裁剪图像: 裁剪后的所有子图像（按从左到右、从上到下的顺序）
            预览图像: 原始图像（用于预览）
        """
        batch_size, orig_height, orig_width, channels = 图像.shape
        
        # 处理 0 的情况：0 表示不裁剪该方向，视为 1
        actual_横向数量 = max(1, 横向数量)
        actual_纵向数量 = max(1, 纵向数量)
        
        # 计算每个子图块的标准尺寸（向上取整，确保覆盖所有像素）
        block_width = (orig_width + actual_横向数量 - 1) // actual_横向数量
        block_height = (orig_height + actual_纵向数量 - 1) // actual_纵向数量
        
        # 存储所有裁剪后的图像和预览图像
        all_cropped_images = []
        preview_images = []
        
        # 处理批次中的每个图像
        for b in range(batch_size):
            img = 图像[b]
            
            # 转换为PIL图像
            pil_img = tensor2pil(img)
            
            # === 生成预览图像（直接使用原图）===
            preview_tensor = pil2tensor(pil_img)
            preview_images.append(preview_tensor)
            
            # === 裁剪图像 ===
            # 按网格裁剪：从上到下，从左到右
            for row in range(actual_纵向数量):
                for col in range(actual_横向数量):
                    # 计算裁剪区域的坐标
                    left = col * block_width
                    upper = row * block_height
                    right = min(left + block_width, orig_width)
                    lower = min(upper + block_height, orig_height)
                    
                    # 裁剪图像
                    cropped_pil = pil_img.crop((left, upper, right, lower))
                    
                    # 如果裁剪后的尺寸小于标准尺寸，调整到标准尺寸
                    # 这确保所有子图像尺寸一致，便于后续批量处理
                    actual_width = right - left
                    actual_height = lower - upper
                    
                    if actual_width != block_width or actual_height != block_height:
                        # 创建标准尺寸的画布，将裁剪的图像放在左上角
                        # 使用最近邻插值调整尺寸，保持像素艺术的锐利边缘
                        cropped_pil = cropped_pil.resize(
                            (block_width, block_height), 
                            Image.NEAREST
                        )
                    
                    # 转换回张量
                    cropped_tensor = pil2tensor(cropped_pil)
                    
                    all_cropped_images.append(cropped_tensor)
        
        # 将所有裁剪后的图像堆叠成批次
        cropped_result = torch.cat(all_cropped_images, dim=0)
        
        # 将所有预览图像堆叠成批次
        preview_result = torch.cat(preview_images, dim=0)
        
        return (cropped_result, preview_result)


class AFOLIE像素对齐:
    """
    像素对齐节点 - 将像素对齐到完美网格
    修复 AI 生成的像素艺术中的不一致问题
    """
    
    def __init__(self):
        # 获取可执行文件路径（在 bin 目录下）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.exe_path = os.path.join(current_dir, "bin", "spritefusion-pixel-snapper.exe")
        
        if not os.path.exists(self.exe_path):
            raise FileNotFoundError(f"找不到可执行文件: {self.exe_path}")
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "图像": ("IMAGE",),
                "颜色数量": ("INT", {
                    "default": 16,
                    "min": 2,
                    "max": 256,
                    "step": 1,
                    "tooltip": "图像将被量化到这个数量的颜色"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("对齐后的图像",)
    FUNCTION = "process"
    CATEGORY = "AFOLIE/图像"
    DESCRIPTION = """
    将像素对齐到完美网格
    
    功能：
    • 将像素对齐到完美网格
    • 修复 AI 生成像素艺术的不一致
    • 量化颜色到严格的调色板
    • 保持尽可能多的细节（如抖动）
    
    适用于：
    • AI 生成的像素艺术
    • 不适合网格的程序化 2D 艺术
    • 需要完美缩放的 2D 游戏资源和 3D 纹理
    """
    
    def tensor_to_pil(self, tensor):
        """将单个 ComfyUI 张量转换为 PIL 图像"""
        # tensor shape: [H, W, C]
        np_image = tensor.cpu().numpy()
        np_image = (np_image * 255).astype(np.uint8)
        pil_image = Image.fromarray(np_image)
        return pil_image
    
    def pil_to_tensor(self, pil_image):
        """将 PIL 图像转换为 ComfyUI 张量（添加批次维度）"""
        np_image = np.array(pil_image).astype(np.float32)
        np_image = np_image / 255.0
        tensor = torch.from_numpy(np_image).unsqueeze(0)
        return tensor
    
    def process_single_image(self, pil_image, k_colors):
        """处理单张图像"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as input_file:
            input_path = input_file.name
            pil_image.save(input_path, 'PNG')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # 构建命令
            cmd = [self.exe_path, input_path, output_path, str(k_colors)]
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "未知错误"
                raise RuntimeError(f"像素对齐处理失败: {error_msg}")
            
            # 读取输出图像
            output_image = Image.open(output_path)
            
            # 确保输出图像是 RGB
            if output_image.mode not in ['RGB', 'RGBA']:
                output_image = output_image.convert('RGB')
            
            # 如果是 RGBA，转换为 RGB
            if output_image.mode == 'RGBA':
                background = Image.new('RGB', output_image.size, (255, 255, 255))
                background.paste(output_image, mask=output_image.split()[3])
                output_image = background
            
            return output_image
            
        finally:
            # 清理临时文件
            try:
                os.unlink(input_path)
            except:
                pass
            try:
                os.unlink(output_path)
            except:
                pass
    
    def process(self, 图像, 颜色数量):
        """处理图像（支持批量处理）"""
        try:
            batch_size = 图像.shape[0]
            output_tensors = []
            
            for i in range(batch_size):
                single_image = 图像[i]
                original_height = single_image.shape[0]
                original_width = single_image.shape[1]
                
                pil_image = self.tensor_to_pil(single_image)
                output_image = self.process_single_image(pil_image, 颜色数量)
                
                # 如果输出尺寸与原始尺寸不同，调整回原始尺寸
                if output_image.size != (original_width, original_height):
                    output_image = output_image.resize(
                        (original_width, original_height), 
                        Image.NEAREST
                    )
                
                output_tensor = self.pil_to_tensor(output_image)
                output_tensors.append(output_tensor)
            
            result = torch.cat(output_tensors, dim=0)
            return (result,)
                    
        except Exception as e:
            raise RuntimeError(f"像素对齐节点错误: {str(e)}")


# Node registration
NODE_CLASS_MAPPINGS = {
    "AFOLIE图像像素缩放": AFOLIE图像像素缩放,
    "AFOLIE图像倍数缩放": AFOLIE图像倍数缩放,
    "AFOLIE图像网格裁剪": AFOLIE图像网格裁剪,
    "AFOLIE像素对齐": AFOLIE像素对齐
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AFOLIE图像像素缩放": "图像像素缩放 📐",
    "AFOLIE图像倍数缩放": "图像倍数缩放 🔢",
    "AFOLIE图像网格裁剪": "图像网格裁剪 ✂️",
    "AFOLIE像素对齐": "像素对齐 🎯"
}
