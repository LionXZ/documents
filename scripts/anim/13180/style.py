# -*- coding: utf-8 -*-
"""13180《操作系统》教学动图共享样式与 QA 模块。

规范口径（来自项目 CLAUDE.md 知识整理规范）：
- fps=2（每帧 500ms）；每个解释性画面驻留 >=6 帧（3 秒）；结论/尾帧 >=16 帧（8 秒）
- 中间动作拆 3~4 个子帧：高亮 → 变化 → 标记 → 停留
- 字体：Hiragino Sans GB（matplotlib 环境下最接近苹方的可用中文字体）
- 图内禁止使用 ✓/✔/⋮ 等苹方缺失字形（用「是/否/成立/满足」等文字或简单符号）
- 行标签与第一位数字间距 >=0.8 数据单位；文字不得越界、不得互相压盖
- QA：逐帧检测文字越界与两两重叠，必须清零
- 单张 GIF <= 2MB

用法：
    frames = []
    fig, ax = style.new_fig(title="...")
    ... 画图 ...
    style.snapshot(fig, frames, "画面1")   # QA + 快照（不关闭）
    style.hold(fig, frames, 6)             # 驻留到 >=6 帧
    plt.close(fig)
    ... 下一画面 ...
    style.save_gif(frames, out_path)       # 合成 + 大小把关
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.text as mtext
import numpy as np
from PIL import Image

# 统一字体（苹方在 matplotlib 不可注册，用 Hiragino Sans GB 替代）
plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

FPS = 2                      # 帧率：每秒 2 帧
HOLD_MIN = 6                 # 每个解释性画面最少驻留帧数（=3 秒）
TAIL_HOLD = 16               # 结论/尾帧最少驻留帧数（=8 秒）
MAX_BYTES = 2 * 1024 * 1024  # 单张 GIF 上限

# 统一调色板
C_BG = "#FFFFFF"
C_TEXT = "#1F2933"
C_BLUE = "#2B6CB0"
C_RED = "#C53030"
C_GREEN = "#2F855A"
C_ORANGE = "#DD6B20"
C_PURPLE = "#6B46C1"
C_GRAY = "#718096"
C_LIGHT = "#EBF4FF"
C_YELLOW = "#FEF3C7"
C_PINK = "#FED7D7"
C_LGREEN = "#F0FFF4"
C_LRED = "#FFF5F5"


def new_fig(w=10.0, h=6.0, title=None):
    """新建统一风格的画布，返回 (fig, ax)。坐标系统一 0~100（x）、0~60（y）便于布局。"""
    fig, ax = plt.subplots(figsize=(w, h), dpi=100)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")
    ax.set_xticks([])  # 连刻度 Text 对象一并清除，避免 QA 误报（axis off 下刻度本就不渲染）
    ax.set_yticks([])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    if title:
        ax.set_title(title, fontsize=17, color=C_TEXT, pad=14, fontweight="bold")
    return fig, ax


def qa_frame(fig, tag):
    """逐帧 QA：检测文字越界与两两重叠（过滤不可见/空文本）。发现问题直接抛异常。"""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    texts = []
    for t in fig.findobj(mtext.Text):
        s = t.get_text()
        if not s.strip() or not t.get_visible():
            continue
        bb = t.get_window_extent(renderer)
        if bb.width <= 0 or bb.height <= 0:
            continue
        texts.append((s, bb))
    problems = []
    for s, bb in texts:
        if bb.x0 < -1.5 or bb.y0 < -1.5 or bb.x1 > W + 1.5 or bb.y1 > H + 1.5:
            problems.append(f"  [越界] '{s[:24]}' extent=({bb.x0:.0f},{bb.y0:.0f})-({bb.x1:.0f},{bb.y1:.0f}) 画布 {W}x{H}")
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            s1, b1 = texts[i]
            s2, b2 = texts[j]
            if b1.overlaps(b2):
                ix = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
                iy = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
                if ix > 2 and iy > 2:
                    problems.append(f"  [重叠] '{s1[:20]}' × '{s2[:20]}' 交叠 {ix:.0f}x{iy:.0f}px")
    if problems:
        raise AssertionError(f"QA 未通过（{tag}）：\n" + "\n".join(problems))


def _snap(fig):
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    arr = np.asarray(buf)[:, :, :4].copy()
    return Image.fromarray(arr, "RGBA").convert("RGB")


def snapshot(fig, frames, tag, qa=True):
    """QA（可关）+ 把当前画布快照为一帧。不关闭 fig，由调用方负责。"""
    if qa:
        qa_frame(fig, tag)
    frames.append(_snap(fig))


def hold(fig, frames, n=HOLD_MIN):
    """把当前画面驻留到共 n 帧（若已快照过 1 帧，则补 n-1 帧）。"""
    for _ in range(n - 1):
        frames.append(_snap(fig))


def _keep_unique(quanted):
    """Pillow 11+ 保存 GIF 时会合并「连续完全相同的帧」并累加 duration，
    导致 fps=2 口径（每画面 6 个独立帧、duration 恒 500ms）失效。
    对与前一帧相同的帧做右下角单像素调色板索引微扰，保证逐帧独立存储。"""
    for i in range(1, len(quanted)):
        if quanted[i].tobytes() == quanted[i - 1].tobytes():
            im = quanted[i].copy()
            px = im.load()
            w, h = im.size
            cur = px[w - 1, h - 1]
            for idx in range(256):  # 取一个与当前像素不同的索引（1px 肉眼不可见）
                if idx != cur:
                    px[w - 1, h - 1] = idx
                    break
            quanted[i] = im
    return quanted


def save_gif(frames, out_path, fps=FPS):
    """合成 GIF（自适应调色板降色直到 <=2MB），打印帧数/时长/大小。"""
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    n = len(frames)
    ok = False
    for colors in (128, 96, 64, 48, 32):
        quanted = [f.convert("P", palette=Image.ADAPTIVE, colors=colors) for f in frames]
        quanted = _keep_unique(quanted)
        quanted[0].save(
            out_path, save_all=True, append_images=quanted[1:],
            duration=int(1000 / fps), loop=0, optimize=True,
        )
        size = os.path.getsize(out_path)
        print(f"[save] {out_path} 帧数={n} 时长={n / fps:.1f}s 颜色={colors} 大小={size / 1024:.0f}KB")
        if size <= MAX_BYTES:
            ok = True
            break
    if not ok:
        raise AssertionError(f"GIF 超 2MB：{out_path}")
    return out_path
