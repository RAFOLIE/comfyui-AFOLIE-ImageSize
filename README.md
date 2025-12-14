# AFOLIE ImageSize - ComfyUI Custom Nodes

[English](#english) | [中文](#中文)

---

## English

A comprehensive ComfyUI custom node collection for image processing, providing Photoshop-like image resizing, batch image loading, and custom folder saving functionality.

### 📦 Features Overview

This plugin provides **7 powerful nodes** organized into three categories:

#### 🖼️ Image Processing (AFOLIE/图像)
- **Image Size (图像像素缩放)** - Pixel-based image resizing
- **Image Scale (图像倍数缩放)** - Scale-based image resizing

#### 📥 Input Nodes (AFOLIE/输入)
- **Input Batch Images (Input批次图像)** - Load batch images with original sizes
- **Input Batch Images Pixels (Input批次图像像素)** - Load and resize to uniform pixel dimensions
- **Input Batch Images Scale (Input批次图像倍数)** - Load and scale by multiplier

#### 💾 Output Nodes (AFOLIE/输出)
- **Image Folder (图像文件夹)** - Save images to custom folder paths

---

### 🎯 Node Details

#### 1. Image Size (图像像素缩放) 📏

Photoshop-like image resizing with pixel-based dimensions.

**Features:**
- Direct pixel dimension control (64-8192px)
- Aspect ratio lock/unlock
- 7 resampling methods
- Batch processing support

**Parameters:**
| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| image | IMAGE | - | - | Input image |
| resize_mode | Choice | pixels/scale | pixels | Resize mode |
| width | INT | 64-8192 | 512 | Target width (pixels mode) |
| height | INT | 64-8192 | 512 | Target height (pixels mode) |
| scale_factor | FLOAT | 0.01-12.0 | 1.0 | Scale multiplier (scale mode) |
| maintain_aspect_ratio | BOOLEAN | true/false | true | Lock aspect ratio |
| resample | BOOLEAN | true/false | true | Enable resampling |
| resampling_method | Choice | 7 methods | bicubic_smooth | Sampling method |

**Resampling Methods:**
- `bicubic_smooth` - Smooth bicubic interpolation (default)
- `preserve_details_enlarge` - Lanczos, best for enlarging
- `preserve_details_2` - High-quality Lanczos
- `bicubic_smoother_enlarge` - Smoother bicubic for enlarging
- `bicubic_sharper_reduce` - Sharper bicubic for reducing
- `nearest_hard_edges` - Nearest neighbor for pixel art
- `bilinear` - Bilinear interpolation for fast processing

**Use Cases:**
```
Enlarge with detail preservation:
- resize_mode: pixels
- width: 2048, height: 2048
- resampling_method: preserve_details_enlarge

Reduce image size:
- resize_mode: scale
- scale_factor: 0.5
- resampling_method: bicubic_sharper_reduce

Pixel art scaling:
- resize_mode: scale
- scale_factor: 4.0
- resampling_method: nearest_hard_edges
```

---

#### 2. Image Scale (图像倍数缩放) 🔢

Scale-based image resizing with multiplier control.

**Features:**
- Scale multiplier: 0.01x - 12x
- Same resampling methods as Image Size
- Aspect ratio preservation
- Batch processing support

**Parameters:**
Same as Image Size node, optimized for scale-based workflow.

---

#### 3. Input Batch Images (Input批次图像) 📁

Load multiple images from a folder while preserving original dimensions.

**Features:**
- Load all images from specified folder
- Preserve original image sizes
- Support PNG (with transparency) and JPG formats
- Automatic batch processing via list output
- Sorted file loading

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| 路径 (Path) | STRING | E:/AI/ComfyUI_works/input_images | Folder path |
| 文件格式 (Format) | Choice | all | File format filter (all/png/jpg) |

**Output:**
- IMAGE (List) - Each image output individually for batch processing

**Workflow:**
```
Input Batch Images → Process → Save
                  ↓
            (14 images loaded)
                  ↓
         (14 iterations automatically)
                  ↓
            (14 images saved)
```

---

#### 4. Input Batch Images Pixels (Input批次图像像素) 📐

Load batch images and resize all to uniform pixel dimensions.

**Features:**
- Unified pixel dimensions for all images
- 4 resampling methods
- Automatic format conversion
- Batch processing support

**Parameters:**
| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| 路径 (Path) | STRING | - | E:/AI/ComfyUI_works/input_images | Folder path |
| 文件格式 (Format) | Choice | all/png/jpg | all | File format |
| 统一宽度 (Width) | INT | 64-8192 | 512 | Unified width |
| 统一高度 (Height) | INT | 64-8192 | 512 | Unified height |
| 采样方法 (Method) | Choice | 4 methods | Lanczos | Resampling method |

**Resampling Methods:**
- `保留细节(Lanczos)` - Preserve details (best quality)
- `两次立方(Bicubic)` - Bicubic interpolation
- `两次线性(Bilinear)` - Bilinear interpolation
- `邻近(Nearest)` - Nearest neighbor (pixel art)

---

#### 5. Input Batch Images Scale (Input批次图像倍数) 🔢

Load batch images and scale all by a uniform multiplier.

**Features:**
- Scale all images by same multiplier
- Base size from first image
- 4 resampling methods
- Batch processing support

**Parameters:**
| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| 路径 (Path) | STRING | - | E:/AI/ComfyUI_works/input_images | Folder path |
| 文件格式 (Format) | Choice | all/png/jpg | all | File format |
| 倍数 (Scale) | FLOAT | 0.01-12.0 | 1.0 | Scale multiplier |
| 采样方法 (Method) | Choice | 4 methods | Lanczos | Resampling method |

**Example:**
```
First image: 1024x768
Scale: 2.0
Result: All images scaled to 2048x1536
```

---

#### 6. Image Folder (图像文件夹) 💾

Save images to custom folder paths instead of default output folder.

**Features:**
- Custom folder path support
- Multiple format support (PNG/JPG/JPEG/WebP)
- Highest quality saving
- Unique filename with counter
- Metadata support (PNG)
- Automatic folder creation

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| 图像 (Image) | IMAGE | - | Input image |
| 文件夹路径 (Path) | STRING | E:/AI/ComfyUI_works/output_custom | Save folder path |
| 文件名前缀 (Prefix) | STRING | AFOLIE | Filename prefix |
| 文件格式 (Format) | Choice | png | File format (png/jpg/jpeg/webp) |
| 保存元数据 (Metadata) | BOOLEAN | true | Save metadata (PNG only) |

**Filename Format:**
```
Prefix_Timestamp_Counter.Format
Example: AFOLIE_20251213_173141_0000.png
         AFOLIE_20251213_173141_0001.png
         AFOLIE_20251213_173141_0002.png
```

**Quality Settings:**
- PNG: compress_level=0 (no compression, best quality)
- JPG: quality=100, optimize=True
- WebP: quality=100, method=6

**Output:**
- IMAGE - Pass-through for chaining
- STRING - Saved file paths

---

### 📥 Installation

#### Method 1: Git Clone
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/comfyui-AFOLIE-ImageSize.git
```

#### Method 2: Manual Installation
1. Download and extract the plugin
2. Copy the `comfyui-AFOLIE-ImageSize` folder to `ComfyUI/custom_nodes/`
3. Restart ComfyUI

#### Method 3: ComfyUI Manager
Search for "AFOLIE ImageSize" in ComfyUI Manager and install.

---

### 🚀 Usage Examples

#### Example 1: Batch Image Processing with Uniform Size
```
Input Batch Images Pixels (512x512)
    ↓
[Your Processing Nodes]
    ↓
Image Folder (Save to custom path)
```

#### Example 2: Scale Multiple Images
```
Input Batch Images Scale (2x)
    ↓
[Your Processing Nodes]
    ↓
Image Folder (Save as PNG)
```

#### Example 3: Mixed Size Batch Processing
```
Input Batch Images (Original sizes)
    ↓
Image Size (Resize individually)
    ↓
Image Folder (Save to custom path)
```

#### Example 4: High-Quality Upscaling
```
Load Image
    ↓
Image Size (4096x4096, preserve_details_enlarge)
    ↓
Image Folder (Save as PNG, highest quality)
```

---

### 🔧 Technical Details

**Dependencies:**
- torch
- numpy
- PIL (Pillow)
- folder_paths (ComfyUI)

**Image Processing:**
- Tensor-based processing
- Automatic format conversion
- Batch processing support
- Color precision preservation

**File Handling:**
- Automatic directory creation
- Unique filename generation
- Format-specific optimization
- Metadata preservation (PNG)

---

### 📋 Version History

#### v1.0.0 (2025-12-13)
- ✅ Initial release
- ✅ Image Size node with 7 resampling methods
- ✅ Image Scale node
- ✅ Three Input batch nodes
- ✅ Image Folder save node
- ✅ Batch processing support
- ✅ Counter-based unique filenames

---

### 📝 License

MIT License

### 👤 Author

AFOLIE

### 🐛 Issues & Support

For issues, suggestions, or feature requests, please submit an issue on GitHub.

---

## 中文

ComfyUI自定义节点集合，提供类似Photoshop的图像大小调整、批量图像加载和自定义文件夹保存功能。

### 📦 功能概览

本插件提供 **7个强大的节点**，分为三个类别：

#### 🖼️ 图像处理 (AFOLIE/图像)
- **图像像素缩放** - 基于像素的图像大小调整
- **图像倍数缩放** - 基于倍数的图像缩放

#### 📥 输入节点 (AFOLIE/输入)
- **Input批次图像 📁** - 加载批次图像（保持原始尺寸）
- **Input批次图像像素 📐** - 加载并调整到统一像素尺寸
- **Input批次图像倍数 🔢** - 加载并按倍数统一缩放

#### 💾 输出节点 (AFOLIE/输出)
- **图像文件夹 💾** - 保存图像到自定义文件夹路径

---

### 🎯 节点详情

#### 1. 图像像素缩放 📏

类似Photoshop的图像大小调整功能，基于像素尺寸。

**功能特性：**
- 直接像素尺寸控制（64-8192像素）
- 宽高比锁定/解锁
- 7种重新采样方法
- 支持批处理

**参数说明：**
| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| image | IMAGE | - | - | 输入图像 |
| resize_mode | 选择 | pixels/scale | pixels | 调整模式 |
| width | 整数 | 64-8192 | 512 | 目标宽度（像素模式） |
| height | 整数 | 64-8192 | 512 | 目标高度（像素模式） |
| scale_factor | 浮点 | 0.01-12.0 | 1.0 | 缩放倍数（倍数模式） |
| maintain_aspect_ratio | 布尔 | true/false | true | 锁定宽高比 |
| resample | 布尔 | true/false | true | 启用重新采样 |
| resampling_method | 选择 | 7种方法 | bicubic_smooth | 采样方法 |

**重新采样方法：**
- `两次立方(平滑渐变)` - 平滑的双三次插值（默认）
- `保留细节(扩大)` - Lanczos算法，最适合放大
- `保留细节 2.0` - 高质量Lanczos
- `两次立方(较平滑)(扩大)` - 平滑的双三次放大
- `两次立方(较锐利)(缩减)` - 锐利的双三次缩小
- `邻近(硬边缘)` - 最近邻插值，适合像素艺术
- `两次线性` - 双线性插值，快速处理

**使用场景：**
```
放大并保留细节：
- resize_mode: pixels
- width: 2048, height: 2048
- resampling_method: preserve_details_enlarge

缩小图像：
- resize_mode: scale
- scale_factor: 0.5
- resampling_method: bicubic_sharper_reduce

像素艺术缩放：
- resize_mode: scale
- scale_factor: 4.0
- resampling_method: nearest_hard_edges
```

---

#### 2. 图像倍数缩放 🔢

基于倍数的图像缩放控制。

**功能特性：**
- 缩放倍数：0.01x - 12x
- 与图像像素缩放相同的采样方法
- 保持宽高比
- 支持批处理

**参数说明：**
与图像像素缩放节点相同，针对倍数工作流优化。

---

#### 3. Input批次图像 📁

从文件夹加载多张图像，保持原始尺寸。

**功能特性：**
- 从指定文件夹加载所有图像
- 保持原始图像尺寸
- 支持PNG（保留透明度）和JPG格式
- 通过列表输出自动批处理
- 按文件名排序加载

**参数说明：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|---------|------|
| 路径 | STRING | E:/AI/ComfyUI_works/input_images | 文件夹路径 |
| 文件格式 | 选择 | all | 文件格式筛选（all/png/jpg） |

**输出：**
- IMAGE（列表） - 每张图像单独输出用于批处理

**工作流程：**
```
Input批次图像 → 处理 → 保存
            ↓
      (加载14张图像)
            ↓
      (自动迭代14次)
            ↓
      (保存14张图像)
```

---

#### 4. Input批次图像像素 📐

加载批次图像并调整所有图像到统一像素尺寸。

**功能特性：**
- 所有图像统一到指定像素尺寸
- 4种重新采样方法
- 自动格式转换
- 支持批处理

**参数说明：**
| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| 路径 | STRING | - | E:/AI/ComfyUI_works/input_images | 文件夹路径 |
| 文件格式 | 选择 | all/png/jpg | all | 文件格式 |
| 统一宽度 | 整数 | 64-8192 | 512 | 统一宽度 |
| 统一高度 | 整数 | 64-8192 | 512 | 统一高度 |
| 采样方法 | 选择 | 4种方法 | Lanczos | 重新采样方法 |

**采样方法：**
- `保留细节(Lanczos)` - 保留细节（最佳质量）
- `两次立方(Bicubic)` - 双三次插值
- `两次线性(Bilinear)` - 双线性插值
- `邻近(Nearest)` - 最近邻（像素艺术）

---

#### 5. Input批次图像倍数 🔢

加载批次图像并按统一倍数缩放所有图像。

**功能特性：**
- 所有图像按相同倍数缩放
- 基准尺寸来自第一张图像
- 4种重新采样方法
- 支持批处理

**参数说明：**
| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| 路径 | STRING | - | E:/AI/ComfyUI_works/input_images | 文件夹路径 |
| 文件格式 | 选择 | all/png/jpg | all | 文件格式 |
| 倍数 | 浮点 | 0.01-12.0 | 1.0 | 缩放倍数 |
| 采样方法 | 选择 | 4种方法 | Lanczos | 重新采样方法 |

**示例：**
```
第一张图像：1024x768
倍数：2.0
结果：所有图像缩放到 2048x1536
```

---

#### 6. 图像文件夹 💾

将图像保存到自定义文件夹路径，而不是默认的output文件夹。

**功能特性：**
- 支持自定义文件夹路径
- 支持多种格式（PNG/JPG/JPEG/WebP）
- 最高质量保存
- 使用计数器确保文件名唯一
- 支持元数据（PNG）
- 自动创建文件夹

**参数说明：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|---------|------|
| 图像 | IMAGE | - | 输入图像 |
| 文件夹路径 | STRING | E:/AI/ComfyUI_works/output_custom | 保存文件夹路径 |
| 文件名前缀 | STRING | AFOLIE | 文件名前缀 |
| 文件格式 | 选择 | png | 文件格式（png/jpg/jpeg/webp） |
| 保存元数据 | 布尔 | true | 保存元数据（仅PNG） |

**文件命名格式：**
```
前缀_时间戳_计数器.格式
示例：AFOLIE_20251213_173141_0000.png
     AFOLIE_20251213_173141_0001.png
     AFOLIE_20251213_173141_0002.png
```

**质量设置：**
- PNG：compress_level=0（无压缩，最佳质量）
- JPG：quality=100, optimize=True
- WebP：quality=100, method=6

**输出：**
- IMAGE - 传递用于链接
- STRING - 保存的文件路径

---

### 📥 安装方法

#### 方法1：Git克隆
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/comfyui-AFOLIE-ImageSize.git
```

#### 方法2：手动安装
1. 下载并解压插件
2. 将 `comfyui-AFOLIE-ImageSize` 文件夹复制到 `ComfyUI/custom_nodes/`
3. 重启ComfyUI

#### 方法3：ComfyUI Manager
在ComfyUI Manager中搜索"AFOLIE ImageSize"并安装。

---

### 🚀 使用示例

#### 示例1：批量图像处理并统一尺寸
```
Input批次图像像素 (512x512)
    ↓
[您的处理节点]
    ↓
图像文件夹 (保存到自定义路径)
```

#### 示例2：批量缩放图像
```
Input批次图像倍数 (2倍)
    ↓
[您的处理节点]
    ↓
图像文件夹 (保存为PNG)
```

#### 示例3：混合尺寸批处理
```
Input批次图像 (保持原始尺寸)
    ↓
图像像素缩放 (单独调整)
    ↓
图像文件夹 (保存到自定义路径)
```

#### 示例4：高质量放大
```
加载图像
    ↓
图像像素缩放 (4096x4096, preserve_details_enlarge)
    ↓
图像文件夹 (保存为PNG，最高质量)
```

---

### 🔧 技术细节

**依赖项：**
- torch
- numpy
- PIL (Pillow)
- folder_paths (ComfyUI)

**图像处理：**
- 基于张量的处理
- 自动格式转换
- 支持批处理
- 保持颜色精度

**文件处理：**
- 自动创建目录
- 唯一文件名生成
- 格式特定优化
- 元数据保留（PNG）

---

### 📋 版本历史

#### v1.0.0 (2025-12-13)
- ✅ 初始版本发布
- ✅ 图像像素缩放节点，支持7种采样方法
- ✅ 图像倍数缩放节点
- ✅ 三个Input批次节点
- ✅ 图像文件夹保存节点
- ✅ 批处理支持
- ✅ 基于计数器的唯一文件名

---

### 📝 许可证

GPL-3.0 license

### 👤 作者

AFOLIE

### 🐛 问题与支持

如有问题、建议或功能请求，请在GitHub上提交issue。

---

**注意 / Note**: 
- 此插件需要ComfyUI环境
- 所有依赖项通常已包含在ComfyUI中
- 重启ComfyUI后节点才会生效

**This plugin requires ComfyUI environment**
- All dependencies are typically included in ComfyUI
- Restart ComfyUI for nodes to take effect
