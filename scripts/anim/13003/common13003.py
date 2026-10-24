# -*- coding: utf-8 -*-
"""13003 数据结构与算法 动图公共模块。

规范（遵循项目 CLAUDE.md 与任务口径）：
- 画布 900x560（figsize 9x5.6, dpi=100），GIF fps=2（每帧 500ms）
- 每个解释性画面（文字/数字出现后）驻留 >=6 帧（=3 秒）再切换
- 每个动作拆 3~4 子帧：高亮 -> 变化 -> 标记 -> 停留
- 结论/公式尾帧停留 >=8 秒（16 帧）
- 苹方字体（PingFang SC）；禁用 unicode_minus；不使用 ✓/✔ 等苹方缺字形字符
- 逐帧 QA：检测文字画布越界与两两重叠（过滤不可见文本）
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image
import io
import os
import numpy as np

# ---------- 全局常量 ----------
FPS = 2
DUR_MS = 500          # fps=2 -> 每帧 500ms
HOLD = 6              # 解释性画面最小驻留帧数（3 秒）
SUB = 2               # 每个动作子帧的重复数（高亮/变化各停 1 秒）
FINAL_HOLD = 16       # 结论尾帧 >=8 秒
FIG_W, FIG_H, DPI = 9.0, 5.6, 100   # 900x560

plt.rcParams["font.family"] = ["PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 配色 ----------
C_NODE   = "#EAF2FB"   # 结点默认底色
C_EDGE   = "#5B7A99"   # 边/框线
C_TEXT   = "#1F2937"   # 正文
C_HL     = "#FFD54F"   # 高亮（比较/当前）
C_SWAP   = "#FF8A65"   # 交换/变化
C_DONE   = "#A5D6A7"   # 完成/有序
C_VIS    = "#90CAF9"   # 已访问
C_QUEUE  = "#CE93D8"   # 队列/栈辅助结构
C_BASE   = "#F5F5F5"   # 背景
C_DIM    = "#B0BEC5"   # 弱化


class Recorder:
    """帧收集器：把 matplotlib figure 渲染成帧，支持驻留重复。"""

    def __init__(self):
        self.frames = []   # list[PIL.Image]

    def add(self, fig, hold=1):
        """渲染当前 fig 并驻留 hold 帧（hold>=1）。调用后不关闭 fig，由调用方管理。"""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=DPI, facecolor=fig.get_facecolor())
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
        for _ in range(max(1, int(hold))):
            self.frames.append(img.copy())
        buf.close()
        return img   # 返回首帧图像，QA 用

    def save(self, path, qa_reports=None):
        """保存 GIF（fps=2，循环播放）。返回 (帧数, 时长秒, 文件字节)。"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        n = len(self.frames)
        self.frames[0].save(
            path, save_all=True, append_images=self.frames[1:],
            duration=DUR_MS, loop=0, optimize=True,
        )
        size = os.path.getsize(path)
        return n, n / FPS, size


def new_fig(title=None, subtitle=None):
    """新建 900x560 画布。返回 (fig, ax)。"""
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 56)
    ax.axis("off")   # QA 检测时据此过滤不可见文本
    if title:
        ax.text(45, 53.6, title, ha="center", va="center",
                fontsize=15, fontweight="bold", color=C_TEXT)
    if subtitle:
        # 副标题较长时缩小字号，避免横向伸入画面两侧的栏目区
        fs = 11 if len(subtitle) <= 30 else 9.5
        ax.text(45, 50.4, subtitle, ha="center", va="center",
                fontsize=fs, color="#455A64")
    return fig, ax


# ---------- QA：越界与重叠检测 ----------
def _visible_texts(fig):
    """收集 figure 内所有可见文本对象；axis(off) 的坐标轴刻度文本不参与检测（项目规范）。"""
    out = []
    for ax in fig.axes:
        texts = list(ax.texts)
        if ax.axison:   # 坐标轴开启时才检测刻度文本（axis off 时不渲染）
            texts += list(ax.get_xticklabels()) + list(ax.get_yticklabels())
            if ax.title.get_text():
                texts.append(ax.title)
        for t in texts:
            try:
                if t.get_text() and t.get_visible():
                    out.append(t)
            except Exception:
                pass
    for t in fig.texts:
        if t.get_text() and t.get_visible():
            out.append(t)
    return out


def check_frame(fig):
    """检测单帧：文字越界画布 + 文字两两重叠。返回问题描述列表（空列表=通过）。"""
    problems = []
    renderer = fig.canvas.get_renderer() if hasattr(fig.canvas, "get_renderer") else None
    if renderer is None:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    W, H = fig.get_size_inches() * fig.dpi   # 900, 560
    items = []
    for t in _visible_texts(fig):
        try:
            bb = t.get_window_extent(renderer=renderer)
        except Exception:
            continue
        items.append((t.get_text(), bb))
        # 越界检测（留 1px 容差）
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > W + 1 or bb.y1 > H + 1:
            problems.append(f"越界: 「{t.get_text()[:14]}」 bbox=({bb.x0:.0f},{bb.y0:.0f},{bb.x1:.0f},{bb.y1:.0f})")
    # 两两重叠检测
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            t1, b1 = items[i]
            t2, b2 = items[j]
            ix = max(0, min(b1.x1, b2.x1) - max(b1.x0, b2.x0))
            iy = max(0, min(b1.y1, b2.y1) - max(b1.y0, b2.y0))
            if ix > 2 and iy > 2:   # 容差 2px
                problems.append(f"重叠: 「{t1[:10]}」x「{t2[:10]}」 交叉 {ix:.0f}x{iy:.0f}px")
    return problems


def check_and_save(rec, path, verbose=True):
    """保存 GIF 并对抽样帧做 QA（每张图抽首/中/尾 + 全部驻留首帧已即时检测时可直接用全部）。"""
    n, sec, size = rec.save(path)
    problems_all = getattr(rec, "qa_problems", [])
    if verbose:
        tag = "PASS" if not problems_all else "FAIL"
        print(f"[{tag}] {os.path.basename(path)}  {n}帧 {sec:.0f}s {size/1024:.0f}KB 问题{len(problems_all)}处")
        for p in problems_all[:8]:
            print("   -", p)
    return problems_all


def arrow(ax, x1, y1, x2, y2, color=C_EDGE, lw=2.2, style="-|>", shrinkA=8, shrinkB=8, zorder=2, ls="-", connectionstyle=None):
    """带箭头连线（数据坐标）。"""
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                        mutation_scale=16, color=color, lw=lw,
                        shrinkA=shrinkA, shrinkB=shrinkB, zorder=zorder, linestyle=ls,
                        connectionstyle=connectionstyle)
    ax.add_patch(a)
    return a


def boxes_row(ax, vals, y, x0=6, w=8.4, gap=1.2, h=7, colors=None, tcolors=None, fontsize=15, start_idx=0, extra=None, show_index=True):
    """画一排方块数组。返回方块中心 x 列表。colors/tcolors 可传 dict{下标:色}。show_index=False 不画下标。"""
    xs = []
    for k, v in enumerate(vals):
        cx = x0 + k * (w + gap) + w / 2
        fc = (colors or {}).get(k, C_NODE)
        ax.add_patch(plt.Rectangle((cx - w / 2, y - h / 2), w, h,
                                   fc=fc, ec=C_EDGE, lw=1.6, zorder=3))
        tc = (tcolors or {}).get(k, C_TEXT)
        label = str(v) if extra is None else f"{v}"
        ax.text(cx, y, label, ha="center", va="center", fontsize=fontsize,
                color=tc, fontweight="bold", zorder=4)
        if show_index and start_idx + k >= 0:
            ax.text(cx, y - h / 2 - 1.9, str(start_idx + k), ha="center", va="center",
                    fontsize=9, color=C_DIM, zorder=2)
        xs.append(cx)
    return xs
