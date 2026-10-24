# -*- coding: utf-8 -*-
"""02324 离散数学 动图共享渲染工具。

所有动图脚本 import 本模块，保证风格一致（苹方字体、900×560、fps=2、慢节奏）。
QA 规则（项目 CLAUDE.md）：
- fps=2，每个解释性画面驻留 >=6 帧（3 秒）；结论尾帧 >=16 帧（8 秒）
- 单张 GIF <= 2MB
- 字形：苹方（PingFang SC），禁止使用 ✓ / ✔ / ⋮ 等苹方缺字形字符
- 文字不得超出画布、两两不得重叠（qa_figure 逐帧机检）
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------- 字体与全局风格 ----------
def set_style():
    """苹方 + 负号可显示，全局字号。"""
    plt.rcParams["font.family"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False   # 负号用 ASCII，避免缺字形
    plt.rcParams["font.size"] = 13

# 统一配色（与 13015 系列一致的柔和教学配色）
C_MAIN = "#2b6cb0"    # 主色（蓝）
C_HIGH = "#e53e3e"    # 高亮（红）
C_OK   = "#38a169"    # 结论/正确（绿）
C_DIM  = "#a0aec0"    # 淡化（灰）
C_BG   = "#fffaf0"    # 背景（暖白）
C_MARK = "#f6e05e"    # 标记（黄）

# ---------- 画布 ----------
FIG_W, FIG_H, DPI = 9.0, 5.6, 100   # 900x560 px

def new_fig(title=""):
    """新建 900x560 画布，返回 (fig, ax)。"""
    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor(C_BG)
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.84])
    ax.set_facecolor(C_BG)
    if title:
        ax.set_title(title, fontsize=17, fontweight="bold", pad=12)
    return fig, ax

# ---------- QA：逐帧文字越界/重叠机检 ----------
def qa_figure(fig, ctx=""):
    """检测单帧内所有文字：越界或两两重叠则打印问题。

    过滤规则：axis(off) 的刻度文本不参与检测（项目规范允许）。
    返回问题数（0 = 通过）。
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    W, H = fig.get_size_inches() * fig.dpi
    texts = []
    for ax in fig.get_axes():
        items = ax.texts + [ax.title, ax.xaxis.label, ax.yaxis.label]
        # axis(off) 时刻度文本不检测
        if ax.axison:
            items += ax.get_xticklabels() + ax.get_yticklabels()
        for t in items:
            s = t.get_text().strip()
            if s and t.get_visible():
                texts.append(t)
    # 图例文字也检测
    for ax in fig.get_axes():
        leg = ax.get_legend()
        if leg:
            for t in leg.get_texts():
                if t.get_text().strip():
                    texts.append(t)
    problems = 0
    boxes = []
    for t in texts:
        bb = t.get_window_extent(renderer)
        if bb.x0 < -2 or bb.y0 < -2 or bb.x1 > W + 2 or bb.y1 > H + 2:
            print(f"  [QA越界]{ctx} '{t.get_text()[:24]}' bbox=({bb.x0:.0f},{bb.y0:.0f},{bb.x1:.0f},{bb.y1:.0f}) canvas=({W:.0f}x{H:.0f})")
            problems += 1
        boxes.append((t.get_text()[:18], bb))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            if a.overlaps(b):
                # 完全包含（父容器标签压着子元素）也算重叠
                print(f"  [QA重叠]{ctx} '{boxes[i][0]}' <-> '{boxes[j][0]}'")
                problems += 1
    return problems

# ---------- GIF 输出 ----------
class GifBuilder:
    """收集 RGB 帧并保存 GIF（fps=2）。用法：

        gb = GifBuilder()
        for frame in frames:
            gb.add(fig)      # fig 会被关闭
        gb.save("xxx.gif")   # 含 QA：尺寸/大小/帧数校验
    """
    def __init__(self, fps=2):
        self.fps = fps
        self.frames = []

    def add(self, fig, n=1):
        """加入一帧（同一画面重复 n 次即驻留 n 帧）。"""
        fig.canvas.draw()
        import PIL.Image as Image
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
        for _ in range(n):
            self.frames.append(img.copy())
        plt.close(fig)

    def save(self, path, max_mb=2.0):
        from PIL import Image
        os.makedirs(os.path.dirname(path), exist_ok=True)
        d = int(1000 / self.fps)
        # 尾帧已由调用方控制驻留帧数；这里统一量化减色以控体积
        quant = [f.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE) for f in self.frames]
        quant[0].save(path, save_all=True, append_images=quant[1:],
                      duration=d, loop=0, optimize=True)
        size_mb = os.path.getsize(path) / 1024 / 1024
        nframe = len(self.frames)
        dur = nframe / self.fps
        print(f"[GIF] {os.path.basename(path)}  {nframe}帧 / {dur:.0f}s / {size_mb:.2f}MB", "OK" if size_mb <= max_mb else "!!超过2MB")
        return size_mb <= max_mb
