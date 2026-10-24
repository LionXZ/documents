# -*- coding: utf-8 -*-
"""anim-11-io.py —— 13180《操作系统》教学动图：I/O 控制方式演进。

机制对比图：CPU 时间轴 + 设备时间轴（无具体数字数据）。

画面清单：
1. 程序查询（轮询）：CPU 全程忙等，与设备串行
2. 中断控制：CPU 启动后去干别的，设备就绪发中断才介入（每传一个数据单位中断一次）
3. DMA：DMA 控制器接管，设备与内存间直传整块数据，CPU 只做预处理/后处理
4. 通道：通道执行自己的通道程序、管理多台设备，CPU 只需启动通道
5. 尾帧：四方式对比表 + 演进主线
"""

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "操作系统/images/os-anim-11-io.gif")

C_WORK = "#F6AD55"    # 设备工作段
C_DONE = "#9AE6B4"    # 完成
C_BUSY = "#CBD5E1"    # CPU 忙等
C_IDLE = "#E2E8F0"    # CPU 做其他工作
C_SEGB = "#90CDF4"    # CPU 介入段


def band(ax, y0, y1, label, x0=12, x1=92):
    """画一条时间带（CPU / 设备）及左侧标签"""
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#F7FAFC",
                           ec=style.C_GRAY, lw=1.3))
    ax.text(x0 - 2, (y0 + y1) / 2, label, fontsize=13, color=style.C_TEXT,
            ha="right", va="center", fontweight="bold")


def seg(ax, x0, x1, y0, y1, color, text, fs=11.5, tc=None):
    """时间带上的工作段 + 段内文字"""
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=color, ec="none"))
    ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, fontsize=fs, ha="center",
            va="center", color=tc or style.C_TEXT, fontweight="bold")


def time_arrow(ax, y):
    """底部时间方向箭头"""
    ax.annotate("", xy=(93, y), xytext=(84, y),
                arrowprops=dict(arrowstyle="->", color=style.C_GRAY, lw=1.6))
    ax.text(96.5, y, "时间", fontsize=11, color=style.C_GRAY,
            ha="center", va="center")


def note(ax, text, y=5.5, color=style.C_RED, fs=13.5):
    """底部结论/说明行"""
    ax.text(52, y, text, fontsize=fs, color=color, ha="center", va="center",
            fontweight="bold")


def fbox(ax, x, y, w, h, text, fc, ec, fs=13):
    """流程框"""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.4,rounding_size=0.8",
                                fc=fc, ec=ec, lw=1.8))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            color=style.C_TEXT, fontweight="bold")


# ============ 画面 1：程序查询（轮询），两个子画面 ============
frames = []
for stage in (1, 2):
    fig, ax = style.new_fig(title="I/O 控制方式演进 ①：程序查询（轮询）")
    band(ax, 38, 44, "CPU")
    seg(ax, 12, 92, 38, 44, C_BUSY, "忙等查询：反复读取设备状态（独占 CPU）", 12.5)
    band(ax, 16, 22, "设备")
    seg(ax, 12, 70, 16, 22, C_WORK, "设备准备数据（忙）")
    seg(ax, 70, 92, 16, 22, C_DONE, "完成")
    for px in (30, 52, 74):  # 反复轮询
        ax.annotate("", xy=(px, 22.6), xytext=(px, 37.4),
                    arrowprops=dict(arrowstyle="->", color=style.C_GRAY,
                                    lw=1.4, ls="--"))
    ax.text(41, 30, "反复查询状态", fontsize=11.5, color=style.C_GRAY,
            ha="center", va="center")
    time_arrow(ax, 10.5)
    if stage >= 2:
        note(ax, "CPU 全程被独占，与设备串行，效率最低")
    style.snapshot(fig, frames, f"程序查询 stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 2：中断控制方式，两个子画面 ============
for stage in (1, 2):
    fig, ax = style.new_fig(title="I/O 控制方式演进 ②：中断控制")
    band(ax, 38, 44, "CPU")
    seg(ax, 12, 28, 38, 44, C_SEGB, "发出启动命令", 11)
    seg(ax, 28, 74, 38, 44, C_IDLE, "执行其他计算（与设备并行）", 12)
    if stage >= 2:
        seg(ax, 74, 92, 38, 44, C_SEGB, "响应并处理中断", 11)
    band(ax, 16, 22, "设备")
    seg(ax, 12, 70, 16, 22, C_WORK, "设备工作（准备数据）")
    seg(ax, 70, 92, 16, 22, C_DONE, "完成")
    if stage >= 2:  # 设备就绪 → 中断信号
        ax.annotate("", xy=(80, 37.4), xytext=(71, 22.6),
                    arrowprops=dict(arrowstyle="->", color=style.C_RED, lw=2.2))
        ax.text(84.5, 30, "中断信号", fontsize=12, color=style.C_RED,
                ha="left", va="center")
        note(ax, "CPU 与设备并行；每传送一个数据单位（字节/字）中断一次",
             color=style.C_TEXT, fs=12.5)
    time_arrow(ax, 10.5)
    style.snapshot(fig, frames, f"中断控制 stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 3：DMA 方式，两个子画面 ============
for stage in (1, 2):
    fig, ax = style.new_fig(title="I/O 控制方式演进 ③：DMA（直接存储器存取）")
    band(ax, 40, 46, "CPU")
    seg(ax, 12, 30, 40, 46, C_SEGB, "预处理", 11.5)
    seg(ax, 30, 76, 40, 46, C_IDLE, "CPU 与 I/O 并行", 12)
    if stage >= 2:
        seg(ax, 76, 92, 40, 46, C_SEGB, "后处理", 11.5)
    fbox(ax, 58, 30, 26, 6.5, "DMA 控制器", style.C_LIGHT, style.C_BLUE)
    fbox(ax, 20, 30, 16, 6.5, "内存", style.C_YELLOW, style.C_ORANGE)
    ax.text(37, 34.6, "整块数据直达内存", fontsize=11, color=style.C_GRAY,
            ha="center", va="center")
    band(ax, 14, 20, "设备")
    seg(ax, 12, 70, 14, 20, C_WORK, "设备传送（整块数据）", 11.5)
    seg(ax, 70, 92, 14, 20, C_DONE, "完成")
    ax.annotate("", xy=(60, 26.6), xytext=(64, 20.6),
                arrowprops=dict(arrowstyle="->", color=style.C_GRAY, lw=2.2))
    ax.annotate("", xy=(28.4, 30), xytext=(45, 30),
                arrowprops=dict(arrowstyle="->", color=style.C_BLUE, lw=2.4))
    time_arrow(ax, 9)
    if stage >= 2:
        note(ax, "数据传送不再经过 CPU，以数据块为单位", y=4, color=style.C_BLUE)
    style.snapshot(fig, frames, f"DMA stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 4：通道方式，两个子画面 ============
for stage in (1, 2):
    fig, ax = style.new_fig(title="I/O 控制方式演进 ④：通道方式")
    band(ax, 46, 52, "CPU")
    seg(ax, 12, 28, 46, 52, C_SEGB, "启动通道", 11)
    seg(ax, 28, 92, 46, 52, C_IDLE, "CPU 几乎完全解放，执行其他程序", 12)
    fbox(ax, 56, 37.5, 30, 6.5, "通道（专用 I/O 处理器）", style.C_LGREEN,
         style.C_GREEN)
    ax.annotate("", xy=(62, 41), xytext=(62, 45.4),
                arrowprops=dict(arrowstyle="->", color=style.C_BLUE, lw=2.2))
    band(ax, 24, 29.5, "设备 1", x0=30, x1=92)
    seg(ax, 30, 92, 24, 29.5, C_WORK, "按通道程序传送数据", 11)
    if stage >= 2:
        band(ax, 14.5, 20, "设备 2", x0=30, x1=92)
        seg(ax, 30, 92, 14.5, 20, C_WORK, "按通道程序传送数据", 11)
        ax.annotate("", xy=(48, 20.6), xytext=(52, 34.2),
                    arrowprops=dict(arrowstyle="->", color=style.C_GRAY, lw=2.0))
        note(ax, "通道有自己的指令和程序（通道程序），可管理多台设备；CPU 只需启动通道",
             y=6.5, color=style.C_TEXT, fs=12)
    ax.annotate("", xy=(60, 30), xytext=(58, 34.2),
                arrowprops=dict(arrowstyle="->", color=style.C_GRAY, lw=2.0))
    time_arrow(ax, 10.5)
    style.snapshot(fig, frames, f"通道 stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 5：尾帧对比表 ============
fig, ax = style.new_fig(title="小结：四种 I/O 控制方式对比")
headers = [(13, "方式"), (43, "CPU 干预程度"), (72, "传送单位")]
for hx, ht in headers:
    ax.text(hx, 47, ht, fontsize=13.5, color=style.C_GRAY, ha="left",
            va="center", fontweight="bold")
rows = [
    ("程序查询（轮询）", "全程忙等，独占 CPU", "字 / 字节"),
    ("中断控制", "每传一个数据单位中断一次", "字 / 字节"),
    ("DMA", "仅预处理 + 后处理", "数据块"),
    ("通道", "几乎不参与", "一组数据块"),
]
for i, (m, cpu, unit) in enumerate(rows):
    ry = 36.5 - i * 7
    if i % 2 == 0:
        ax.add_patch(Rectangle((8, ry - 3.1), 86, 6.2, fc="#F1F5F9", ec="none"))
    ax.text(13, ry, m, fontsize=13.5, color=style.C_TEXT, va="center",
            fontweight="bold")
    ax.text(43, ry, cpu, fontsize=13.5, color=style.C_TEXT, va="center")
    ax.text(72, ry, unit, fontsize=13.5, color=style.C_TEXT, va="center")
ax.text(50, 7.5, "演进主线：把 CPU 从 I/O 中一步步解放出来", fontsize=15,
        color=style.C_GREEN, ha="center", va="center", fontweight="bold")
style.snapshot(fig, frames, "尾帧对比表")
style.hold(fig, frames, style.TAIL_HOLD)
plt.close(fig)

style.save_gif(frames, OUT)
print(f"[done] anim-11 总帧数={len(frames)}")
