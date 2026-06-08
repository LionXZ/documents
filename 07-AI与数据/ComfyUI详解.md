# ComfyUI 完全上手指南

> 从安装环境到生成第一张图，每个节点是什么意思、每根线怎么连、参数怎么调——手把手带你入门。

---

## 目录

- [一、ComfyUI 是什么](#一comfyui-是什么)
- [二、为什么用 ComfyUI 而不是 WebUI](#二为什么用-comfyui-而不是-webui)
- [三、环境准备与安装](#三环境准备与安装)
- [四、界面速览](#四界面速览)
- [五、第一个工作流：文字生图](#五第一个工作流文字生图)
- [六、核心节点详解](#六核心节点详解)
- [七、工作流 2：图生图（img2img）](#七工作流-2图生图img2img)
- [八、工作流 3：使用 LoRA](#八工作流-3使用-lora)
- [九、工作流 4：ControlNet 精准控图](#九工作流-4controlnet-精准控图)
- [十、工作流 5：IP-Adapter 角色一致性](#十工作流-5ip-adapter-角色一致性)
- [十一、工作流 6：放大与修复](#十一工作流-6放大与修复)
- [十二、模型管理](#十二模型管理)
- [十三、快捷键与效率技巧](#十三快捷键与效率技巧)
- [十四、Python API 接入](#十四python-api-接入)
- [十五、常见问题排查](#十五常见问题排查)

---

## 一、ComfyUI 是什么

ComfyUI 是一个**节点式 Stable Diffusion 工作流编辑器**。它把 AI 生图拆成一个个小方块（节点），你用线把它们连起来，形成一个完整的生成流程。

```
Prompt（提示词） ──┐
                  ├──→ KSampler（采样器）──→ VAE Decode（解码）──→ 图片输出
Checkpoint（模型）─┘
```

和传统界面（点击按钮 → 出图）不同，ComfyUI 让你**看得见每一步在做什么**。你可以中途插入 ControlNet、换模型、加 LoRA、调整降噪强度——这些在传统界面里是黑盒，在 ComfyUI 里是可见的节点和线。

---

## 二、为什么用 ComfyUI 而不是 WebUI

| | ComfyUI | Stable Diffusion WebUI (A1111) |
|------|------|------|
| **操作方式** | 节点连线 | 点击按钮、滑条 |
| **灵活性** | 极高，自由组合节点 | 固定流程 |
| **显存占用** | 低 30-50% | 较高 |
| **批量生成** | 天然支持 | 需要脚本 |
| **工作流复用** | 拖入 JSON/图片即可 | 保存配置 |
| **学习曲线** | 偏高（需要理解流程） | 低（像用手机 App） |
| **适合** | 专业创作者、自动化、API 集成 | 快速出图、新手 |

一句话总结：WebUI 像傻瓜相机，ComfyUI 像单反——拍得快用傻瓜，专业出图画质用单反。

---

## 三、环境准备与安装

### 3.1 硬件要求

| 项目 | 最低 | 推荐 |
|------|------|------|
| GPU | 8GB 显存 (SD 1.5) | 16GB+ (SDXL/Flux) |
| 内存 | 16GB | 32GB |
| 硬盘 | 50GB | 200GB+ (模型很大) |

**macOS 用户注意：** Apple Silicon (M1/M2/M3) 可以跑但比 NVIDIA 慢很多，入门够用，量产建议用 NVIDIA GPU。

### 3.2 安装方式

#### 方式 1：一键整合包（推荐新手）

```bash
# Windows: 下载 ComfyUI_windows_portable 解压即用
# 地址: https://github.com/comfyanonymous/ComfyUI/releases

# macOS / Linux: Git 克隆
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

#### 方式 2：Docker（适合服务器）

```bash
docker run --gpus all -p 8188:8188 \
  -v ./models:/ComfyUI/models \
  -v ./output:/ComfyUI/output \
  yanwk/comfyui-boot:latest
```

### 3.3 首次启动

```bash
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

打开 `http://localhost:8188`，你会看到一个默认的文字生图工作流。

### 3.4 下载第一个模型

此时还出不了图——没有模型文件。把模型放到指定目录：

```bash
# 模型存放位置
ComfyUI/
├── models/
│   ├── checkpoints/        # ← 大模型文件（.safetensors / .ckpt）
│   ├── vae/                # ← VAE 模型
│   ├── loras/              # ← LoRA 模型
│   ├── controlnet/         # ← ControlNet 模型
│   ├── clip/               # ← CLIP 文本编码器
│   └── upscale_models/     # ← 放大模型
```

**新手推荐第一个模型：** DreamShaper 或 Anything V5——社区口碑好，出图稳定。

> 去哪里下载？国内用 `hf-mirror.com`（HuggingFace 镜像），搜索模型名下载 `.safetensors` 文件，放到 `models/checkpoints/` 目录。

---

## 四、界面速览

打开 ComfyUI 后你会看到：

```
┌─────────────────────────────────────────────────────┐
│ 菜单栏: Queue | View | Workflow                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│   Load Checkpoint    CLIP Text Encode (正面)        │
│   dreamshaper_8.safetensors                         │
│         │                   │                       │
│         │    ┌──────────────┘                       │
│         │    │                                      │
│         ├────┤                                      │
│         │    │           Empty Latent Image         │
│         │    │           512×512                    │
│         │    │               │                      │
│         ├────┤               │                      │
│         │    │    ┌──────────┘                      │
│         │    │    │                                 │
│         ▼    ▼    ▼                                 │
│         KSampler                                    │
│              │                                      │
│              ▼                                      │
│         VAE Decode                                  │
│              │                                      │
│              ▼                                      │
│         Save Image                                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

四个关键操作：

| 操作 | 怎么做 |
|------|------|
| **添加节点** | 双击空白区域 → 搜索 → 回车 |
| **连线** | 从一个节点的输出圆点拖到另一个节点的输入圆点 |
| **断开连接** | 按住 Ctrl + 拖动连接线 |
| **删除节点** | 选中 → Backspace |
| **排列节点** | 右键空白 → `Arrange All Nodes` |

---

## 五、第一个工作流：文字生图

现在从头搭建一个文字生图流程。你要理解这张图的含义：

```
提示词 ──→ CLIP 编码 ──→ ┐
                          ├──→ KSampler ──→ VAE 解码 ──→ 保存图片
模型文件 ──→ 加载模型 ──→ ┘
                         │
            空画布 ──────┘
```

### 5.1 搭建步骤

#### 步骤 1：添加加载模型的节点

双击空白 → 搜索 `Load Checkpoint` → 点击添加。

这个节点加载 `.safetensors` 大模型文件。在节点里选择你下载的模型名。

#### 步骤 2：添加提示词节点

双击空白 → 搜索 `CLIP Text Encode` → 添加两个（一个写正面提示词，一个写负面提示词）。

```
CLIP Text Encode (正面):  1girl, sitting by window, afternoon light, warm atmosphere, masterpiece, best quality
CLIP Text Encode (负面):   lowres, bad anatomy, blurry, worst quality, watermark
```

把 `Load Checkpoint` 的 `CLIP` 输出连到两个 `CLIP Text Encode` 的 `clip` 输入。

#### 步骤 3：添加空画布节点

双击 → 搜索 `Empty Latent Image` → 添加。

| 参数 | 推荐值 | 说明 |
|------|------|------|
| width | 512 | 宽度（SD 1.5 最佳） |
| height | 768 | 高度（竖构图） |
| batch_size | 1 | 一次生成几张 |

> **为什么是 512x768 而不是更大的？** SD 1.5 模型训练时用的就是这个尺寸，超了容易出畸形图。SDXL 模型用 1024x1024。

#### 步骤 4：连接 KSampler

双击 → 搜索 `KSampler` → 添加。这是**整个流程的核心**，负责从噪声中逐步还原图像。

关键连接：

```
Load Checkpoint → MODEL     → KSampler 的 model 输入
正面 CLIP Encode → CONDITIONING → KSampler 的 positive 输入
负面 CLIP Encode → CONDITIONING → KSampler 的 negative 输入
Empty Latent Image → LATENT  → KSampler 的 latent_image 输入
```

KSampler 参数设置：

| 参数 | 推荐值 | 说明 |
|------|------|------|
| seed | 随机 | 固定种子可复现画面 |
| control_after_generate | randomize | 每次自动换种子 |
| steps | 20 | 采样步数：太少噪点多，太多无明显提升 |
| cfg | 7 | 提示词权重：越高越贴合但可能过饱和 |
| sampler_name | euler_ancestral | 采样器名 |
| scheduler | normal | 调度器 |

#### 步骤 5：VAE 解码

双击 → 搜索 `VAE Decode` → 添加。

KSampler 输出的是"潜空间"图像（一堆数字），VAE Decode 把它转成肉眼可见的图片。

```
KSampler → LATENT → VAE Decode → IMAGE
Load Checkpoint → VAE → VAE Decode 的 vae 输入
```

#### 步骤 6：保存图片

双击 → 搜索 `Save Image`（或 `Preview Image`）→ 添加。

```
VAE Decode → IMAGE → Save Image
```

### 5.2 完整节点清单

| 节点名 | 数量 | 作用 |
|------|------|------|
| Load Checkpoint | 1 | 加载大模型 |
| CLIP Text Encode | 2 | 正面 + 负面提示词 |
| Empty Latent Image | 1 | 创建空白画布 |
| KSampler | 1 | 采样生成 |
| VAE Decode | 1 | 解码为图片 |
| Save Image | 1 | 保存到本地 |

### 5.3 点击生成

点击右上角 `Queue Prompt`（或 Ctrl + Enter），右下角会显示进度，完成后图片出现在 `Save Image` 节点旁边。

图片默认保存在 `ComfyUI/output/` 目录。

---

## 六、核心节点详解

### 6.1 Load Checkpoint（加载模型）

这个节点加载的是"大模型"（Base Model），决定了画面的整体风格和质量。

常见的输出：

| 输出 | 说明 |
|------|------|
| MODEL | 扩散模型本体，连 KSampler |
| CLIP | 文本编码器，连 Text Encode |
| VAE | 图像解码器，连 VAE Decode |

> **模型放哪里？** `models/checkpoints/` 目录下的 `.safetensors` 或 `.ckpt` 文件。

### 6.2 CLIP Text Encode（文本编码）

把你写的自然语言（"一个女孩在窗边"）转成 AI 能理解的向量。

```python
正面提示词（positive）: 告诉 AI 你要什么
负面提示词（negative）: 告诉 AI 不要什么
```

**好用的负面提示词模板：**

```
lowres, bad anatomy, bad hands, text, error, missing fingers,
extra digit, fewer digits, cropped, worst quality, low quality,
normal quality, jpeg artifacts, signature, watermark, username,
blurry, ugly, old, wide hips, fused fingers, poorly drawn
```

### 6.3 KSampler（采样器）

这是 ComfyUI 最核心的节点——**从纯噪声中逐步还原出图像**。可以理解为 AI 画画的"笔触控制器"。

| 参数 | 推荐值 | 说明 |
|------|------|------|
| seed | 随机/固定 | 固定 = 相同参数得出相同图片 |
| steps | 20-30 | 20 够用，30 更精细（但更慢） |
| cfg | 5-8 | 提示词贴合度，太高会过饱和 |
| sampler_name | euler_ancestral | 推荐：`dpmpp_2m` 细节好，`euler_a` 创意好 |
| scheduler | normal | `karras` 细节更丰富 |
| denoise | 1.0 | 1.0=从头画，0.5=图生图时保留原图 |

---

## 七、工作流 2：图生图（img2img）

**需求**：给一张照片，AI 参考这张图的构图和配色，重新生成一张风格化的图。

### 7.1 核心思路

和文字生图唯一区别：不再是"空画布"，而是**上传一张图片作为起点**。KSampler 的 `denoise` 设为 0.5-0.7 表示保留原图 50%-30% 的信息。

### 7.2 节点变化

把 `Empty Latent Image` 替换为：

```
Load Image → VAE Encode → KSampler
```

具体节点：

```
Load Image (选择图片) → IMAGE → VAE Encode → LATENT → KSampler
```

`VAE Encode` 的 `vae` 输入从 `Load Checkpoint` 的 VAE 输出连接。

### 7.3 参数关键

| KSampler 参数 | 图生图推荐值 | 说明 |
|------|------|------|
| denoise | 0.6 | 越低越接近原图，越高越自由 |
| steps | 25 | 比文字生图多几步 |
| cfg | 7.5 | 正常值 |

- `denoise = 0.3`：微调（换风格但构图不变）
- `denoise = 0.6`：重绘（保留构图，改变细节）
- `denoise = 0.9`：接近重画（只保留大概轮廓）

---

## 八、工作流 3：使用 LoRA

**需求**：让生成的人物固定某种画风、长相、服装，而不换整个大模型。

### 8.1 LoRA 是什么

LoRA（Low-Rank Adaptation）是一种**轻量级微调**。大模型是"通才"（什么都能画），LoRA 是"偏科生"（只会画一种风格/角色）。把 LoRA 加载到大模型上，大模型就学会了这个特定风格。

```python
大模型 (checkpoint, 2-7GB) + LoRA (几十 MB) = 特定风格的大模型
```

### 8.2 节点

双击 → 搜索 `Load LoRA` → 添加。

连接方式：

```
Load Checkpoint → MODEL → Load LoRA → MODEL → KSampler
Load Checkpoint → CLIP  → Load LoRA → CLIP  → CLIP Text Encode
```

| LoRA 参数 | 推荐值 | 说明 |
|------|------|------|
| model_weight | 0.8 | 对画面的影响力，1.0=最强 |
| clip_weight | 0.8 | 对提示词理解的影响 |

> **LoRA 放哪里？** `models/loras/` 目录。

### 8.3 堆叠多个 LoRA

可以串联多个 `Load LoRA`：

```
Load Checkpoint → Load LoRA (脸型) → Load LoRA (服装) → Load LoRA (画风) → KSampler
```

---

## 九、工作流 4：ControlNet 精准控图

**需求**：不止是"风格参考"，而是**精确控制构图**——人物摆什么姿势、手放哪里、画面怎么布局。

### 9.1 ControlNet 是什么

ControlNet 是"控制器"。你给一张参考图（姿势、线稿、深度图），AI 严格按这个参考图来重新画。

### 9.2 控制类型

| ControlNet 类型 | 参考图 | 应用 |
|------|------|------|
| OpenPose | 姿势骨架 | 人物动作 |
| Canny | 边缘检测 | 保持轮廓 |
| Depth | 深度图 | 保持空间关系 |
| Scribble | 涂鸦 | 草稿转成品 |
| Tile | 细节保持 | 放大修复 |

### 9.3 节点连接

```
Load Image (参考图) → ControlNet Preprocessor → ControlNet Apply → KSampler
```

具体：

```
1. 加载参考图: Load Image
2. 预处理: ControlNet Preprocessor（如 OpenPose Preprocessor 提取骨架）
3. 应用控制: ControlNet Apply，连接 KSampler
4. KSampler 的 positive/negative 照常
```

`ControlNet Apply` 的关键连接：

```
Load Checkpoint → MODEL     → ControlNet Apply
ControlNet Loader → CONTROL_NET → ControlNet Apply
Preprocessor → IMAGE → ControlNet Apply
ControlNet Apply → MODEL → KSampler
```

| 参数 | 推荐值 | 说明 |
|------|------|------|
| strength | 1.0 | 控制强度，1.0=完全遵守 |

### 9.4 多个 ControlNet

可以同时用多个 ControlNet（如 OpenPose + Canny）：

```python
第 1 个 ControlNet（OpenPose，strength=1.0）→ 第 2 个 ControlNet（Canny，strength=0.5）→ KSampler
```

---

## 十、工作流 5：IP-Adapter 角色一致性

**需求**：让同一个角色在多个画面中保持一致的长相。这是小说转漫剧、系列插画的核心需求。

### 10.1 IP-Adapter 是什么

不是参考姿势/线条，而是**参考"人物长相"**。你给一张角色的照片，AI 在画每一张图时都记住这个脸。

### 10.2 节点连接

```
Load Image (角色参考照) → IP-Adapter → KSampler
```

```
1. Load Image（角色参考照）→ CLIP Vision Encode → IP-Adapter Apply
2. IP-Adapter Model Loader → IP-Adapter Apply
3. IP-Adapter Apply → MODEL → KSampler
```

| 参数 | 推荐值 | 说明 |
|------|------|------|
| weight | 0.8 | 角色相似度，太高可能僵硬 |

### 10.3 IP-Adapter + LoRA 组合（最强一致性）

```
Load Checkpoint
    ↓
Load LoRA (角色) → IP-Adapter (长相) → ControlNet (姿势) → KSampler
```

这是目前保证角色一致性最强的组合：LoRA 学风格，IP-Adapter 保脸，ControlNet 控姿势。

---

## 十一、工作流 6：放大与修复

**需求**：生成的图只有 512x768，放大到 2048x3072 不模糊。

### 11.1 Hires Fix（高清修复）

直接在高分辨率下重新采样一次：

```
KSampler (低分, denoise=1.0) → Upscale Latent (2x) → KSampler (高分, denoise=0.5) → VAE Decode
```

添加节点：
- `Latent Upscale` — 在潜空间中放大（比图片放大质量好）
- 第 2 个 KSampler — 在放大后的潜空间重新降噪

### 11.2 Ultimate SD Upscale（终极放大）

把图切成小块分别放大再拼回去，适合超大图（4K+）：

```
VAE Decode → Ultimate SD Upscale → Save Image
```

---

## 十二、模型管理

### 12.1 模型类型速查

| 文件后缀 | 类型 | 存放位置 | 作用 |
|------|------|------|------|
| `.safetensors` / `.ckpt` | Checkpoint | `models/checkpoints/` | 大模型，决定整体风格 |
| `.safetensors` | LoRA | `models/loras/` | 轻量微调，画风/角色 |
| `.safetensors` | VAE | `models/vae/` | 图像编解码 |
| `.safetensors` | ControlNet | `models/controlnet/` | 控制构图 |
| `.safetensors` | IP-Adapter | `models/ipadapter/` | 角色一致性 |
| `.safetensors` | Upscale | `models/upscale_models/` | 图像放大 |
| `.safetensors` | CLIP | `models/clip/` | 文本编码器 |

### 12.2 推荐入门模型

| 用途 | 推荐模型 | 大小 |
|------|------|------|
| 通用写实（SD 1.5） | DreamShaper | 2GB |
| 二次元（SD 1.5） | Anything V5 | 2GB |
| 通用写实（SDXL） | Juggernaut XL | 7GB |
| 二次元（SDXL） | Animagine XL | 7GB |
| 真实照片（Flux） | Flux.1-dev | 12GB+ |

> **SD 1.5 vs SDXL vs Flux？** SD 1.5 快、生态最丰富、8GB 显存可跑；SDXL 画质更好、1024x1024 原生；Flux 画质最强但至少 16GB 显存。

---

## 十三、快捷键与效率技巧

| 快捷键 | 功能 |
|------|------|
| `Ctrl + Enter` | 提交生成队列 |
| `Ctrl + S` | 保存工作流 |
| `Ctrl + O` | 加载工作流 |
| `Ctrl + Z` | 撤销 |
| `Ctrl + A` | 全选节点 |
| `Delete` | 删除选中节点 |
| `双击空白` | 搜索节点 |
| `右键空白` | 排列节点 / 锁定画布 |
| `Ctrl + 鼠标滚轮` | 缩放 |
| `Alt + 拖拽空白` | 平移画布 |
| `Ctrl + M` | 开关节点静音模式 |
| `Ctrl + B` | 开关节点旁路模式 |

---

## 十四、Python API 接入

ComfyUI 有 HTTP API，可以通过 Python 脚本自动提交任务、获取结果。

### 14.1 启动 API 模式

```bash
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```

### 14.2 Python 调用示例

```python
import json
import urllib.request
import urllib.parse
import random


def queue_prompt(prompt_workflow):
    """提交工作流到 ComfyUI"""
    data = json.dumps({"prompt": prompt_workflow}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_image(filename, output_dir="output"):
    """下载生成的图片"""
    url = f"http://127.0.0.1:8188/view?filename={filename}"
    urllib.request.urlretrieve(url, f"{output_dir}/{filename}")


# 加载你保存的工作流 JSON
with open("workflow.json", "r") as f:
    workflow = json.load(f)

# 修改提示词
for node_id, node in workflow.items():
    if node["class_type"] == "CLIPTextEncode":
        if "正面" in str(node.get("_meta", {}).get("title", "")):
            node["inputs"]["text"] = "a beautiful sunset over mountains, masterpiece"

# 提交
result = queue_prompt(workflow)
print(f"任务ID: {result['prompt_id']}")
```

### 14.3 常用 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/prompt` | POST | 提交工作流 |
| `/history/{prompt_id}` | GET | 查询任务状态 |
| `/view?filename=xxx` | GET | 下载图片 |
| `/queue` | GET | 查看队列 |
| `/interrupt` | POST | 中断当前任务 |

---

## 十五、常见问题排查

### 15.1 出图全黑或全噪点

- **原因**：模型文件和 VAE 不匹配
- **解决**：清空 VAE 输入（不连线用内置 VAE）试试看，如果能正常出图就是 VAE 文件问题

### 15.2 显存不足（Out of Memory）

```bash
# 在启动命令里加低显存参数
python main.py --lowvram
# 或者极限节省:
python main.py --novram
```

### 15.3 出图太慢

```python
# KSampler 调低 steps: 30 → 20
# 降低分辨率: 1024×1024 → 512×768
# 换更快的采样器: dpmpp_2m → euler_ancestral
# 使用 fp16 模型（.safetensors 通常自带）
```

### 15.4 角色不一致（脸变了）

- 加 IP-Adapter（保脸）
- 加角色 LoRA（保画风）
- 固定 seed 值
- 使用 ControlNet OpenPose（保姿势）

### 15.5 手部畸形

```
负面提示词加: bad hands, missing fingers, extra fingers, fused fingers
正面提示词加: perfect hands, detailed fingers
```

或使用专门的"修复手部"LoRA。

---

> **进阶学习路径：**
> 1. 熟练文字生图 → 掌握 KSampler 参数
> 2. 熟练 img2img → 理解 denoise
> 3. 学会 LoRA → 固定风格
> 4. 学会 ControlNet → 精准控图
> 5. 学会 IP-Adapter → 角色一致性
> 6. 搭建自己的自动生成流水线（Python API + 工作流复用）
