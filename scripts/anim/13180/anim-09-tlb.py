# -*- coding: utf-8 -*-
"""anim-09-tlb.py —— 13180《操作系统》教学动图：快表 TLB 与缺页的时间开销。

数据来源：2026.4 真题综合题 37(3)(4) 同场景（画面标注「2026.4 真题数据」）。
- 查 TLB 10ns；查页表 150ns；处理一次缺页 100ms
- 进程共 2 个页面：页 2 有效（帧 256H）、页 1 初始无效
- TLB 初始为空、容量可容纳全部 2 页

画面清单：
1. 数量级对比：10ns / 160ns / 100ms 的悬殊差距
2. 访问 2025H（页 2）：TLB 未命中 → 查页表有效 → 160ns；转换后登记 TLB
3. 访问 1505H（页 1）：未命中 → 有效位 0 → 缺页中断 → 处理 100ms → 重执行
   合计 10+150+100000000+10+150 = 100000320 ns
4. 访问 25E5H（页 2）：TLB 命中 → 直接得帧号 256H，仅 10ns
5. 尾帧：TLB 本质与三级时间对比
"""

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "操作系统/images/os-anim-09-tlb.gif")


def fbox(ax, x, y, w, h, text, fc, ec, fs=13, tc=None, bold=True, lw=1.8):
    """流程框：框 + 居中文本"""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.4,rounding_size=0.8",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            color=tc or style.C_TEXT,
            fontweight="bold" if bold else "normal")


def arrow(ax, xy_from, xy_to, color=style.C_GRAY, lw=2.0):
    """带箭头连线"""
    ax.annotate("", xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))


def data_scene(title):
    """新建带真题角标的画布"""
    fig, ax = style.new_fig(title=title)
    ax.text(97.5, 57.3, "2026.4 真题数据", fontsize=10, color=style.C_GRAY,
            ha="right", va="center")
    return fig, ax


# ============ 画面 1：数量级对比 ============
frames = []
fig, ax = data_scene("缺页的时间开销：先看数量级")
ax.text(25, 43, "查一次 TLB", fontsize=13, color=style.C_TEXT, ha="right", va="center")
ax.plot([26], [43], "o", ms=4.5, color=style.C_BLUE)
ax.text(28.5, 43, "10ns", fontsize=13.5, color=style.C_BLUE, va="center", fontweight="bold")
ax.text(36, 43, "（在本图比例下小到画不出来）", fontsize=11, color=style.C_GRAY, va="center")
ax.text(25, 34, "TLB 未命中一次", fontsize=13, color=style.C_TEXT, ha="right", va="center")
ax.add_patch(FancyBboxPatch((26, 32.4), 1.0, 3.2,
                            boxstyle="round,pad=0.1", fc=style.C_ORANGE,
                            ec=style.C_ORANGE))
ax.text(29.5, 34, "160ns", fontsize=13.5, color=style.C_ORANGE, va="center", fontweight="bold")
ax.text(25, 24, "处理一次缺页", fontsize=13, color=style.C_TEXT, ha="right", va="center")
ax.add_patch(FancyBboxPatch((26, 21.7), 64, 4.6,
                            boxstyle="round,pad=0.1", fc=style.C_RED, ec=style.C_RED))
ax.text(58, 24, "100ms = 100000000 ns", fontsize=13, color="white",
        ha="center", va="center", fontweight="bold")
ax.text(50, 14, "100ms ≈ 160ns 的 60 多万倍 ——", fontsize=14, color=style.C_RED,
        ha="center", va="center", fontweight="bold")
ax.text(50, 9, "缺页一次的代价抵得上几十万次查表", fontsize=14, color=style.C_RED,
        ha="center", va="center", fontweight="bold")
ax.text(50, 4, "（三种条形按同一时间比例画，长度悬殊即数量级差距）", fontsize=10.5,
        color=style.C_GRAY, ha="center", va="center")
style.snapshot(fig, frames, "数量级对比")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)


# ============ 画面 2：访问 2025H（两个子画面） ============
def draw_2025(ax, stage):
    """访问 2025H：stage 1 查 TLB 未命中；stage 2 查页表有效 + 登记 TLB"""
    fbox(ax, 21, 37, 20, 8, "查 TLB", style.C_LIGHT,
         style.C_GREEN if stage >= 2 else style.C_ORANGE,
         lw=2.4 if stage == 1 else 1.8)
    ax.text(21, 31.5, "10ns · 未命中（TLB 为空）", fontsize=11.5,
            color=style.C_RED if stage == 1 else style.C_GRAY,
            ha="center", va="center")
    fbox(ax, 50, 37, 20, 8, "查页表", style.C_LIGHT,
         style.C_BLUE if stage >= 2 else style.C_GRAY,
         lw=2.4 if stage >= 2 else 1.8)
    ax.text(50, 31.5, "150ns · 页 2 有效", fontsize=11.5, color=style.C_BLUE,
            ha="center", va="center")
    fbox(ax, 79, 37, 22, 8, "得物理地址", style.C_LIGHT,
         style.C_BLUE if stage >= 2 else "#D5DBE3", fs=13.5)
    ax.text(79, 31.5, "帧号 256H", fontsize=11.5, color=style.C_GRAY,
            ha="center", va="center")
    arrow(ax, (31.5, 37), (39.5, 37))
    arrow(ax, (60.5, 37), (67.5, 37))
    if stage >= 2:
        ax.text(50, 21, "合计：10 + 150 = 160 ns", fontsize=15,
                color=style.C_TEXT, ha="center", va="center", fontweight="bold")
        ax.text(50, 14, "转换完成后：把「页 2 → 帧 256H」登记进 TLB",
                fontsize=13, color=style.C_GREEN, ha="center", va="center")


for stage in (1, 2):
    fig, ax = data_scene("访问 2025H → 页 2（TLB 初始为空）")
    draw_2025(ax, stage)
    style.snapshot(fig, frames, f"2025H stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)


# ============ 画面 3：访问 1505H，发生缺页（四个子画面） ============
def draw_1505(ax, stage):
    """访问 1505H：stage 1 查到缺页 → 2 处理缺页 → 3 重新执行 → 4 合计"""
    # 第一行：第一次转换
    fbox(ax, 14.5, 45, 18.5, 6.5, "查 TLB", style.C_LIGHT, style.C_GRAY)
    ax.text(14.5, 38.8, "10ns · 未命中", fontsize=10.5, color=style.C_GRAY,
            ha="center", va="center")
    fbox(ax, 38, 45, 18.5, 6.5, "查页表", style.C_LIGHT, style.C_GRAY)
    ax.text(38, 38.8, "150ns", fontsize=10.5, color=style.C_GRAY,
            ha="center", va="center")
    fbox(ax, 61.5, 45, 20, 6.5, "页 1 有效位 = 0", style.C_PINK, style.C_RED,
         fs=12.5, tc=style.C_RED)
    ax.text(61.5, 38.8, "初始无效", fontsize=10.5, color=style.C_GRAY,
            ha="center", va="center")
    fbox(ax, 85.5, 45, 18, 6.5, "缺页中断", style.C_RED, style.C_RED,
         fs=13.5, tc="white")
    ax.text(85.5, 38.8, "转缺页处理程序", fontsize=10.5, color=style.C_RED,
            ha="center", va="center")
    arrow(ax, (24, 45), (28.5, 45))
    arrow(ax, (47.5, 45), (51, 45))
    arrow(ax, (71.9, 45), (76, 45))
    if stage >= 2:  # 处理缺页
        arrow(ax, (80, 41.5), (30, 32.1), color=style.C_ORANGE, lw=2.2)
        fbox(ax, 22, 28, 25, 7.5, "处理缺页 100ms\n（调入页面、更新页表）",
             style.C_YELLOW, style.C_ORANGE, fs=11.5)
    if stage >= 3:  # 重新执行地址转换
        fbox(ax, 52, 28, 19, 6.5, "查 TLB", style.C_LIGHT, style.C_GRAY)
        ax.text(52, 22.0, "10ns · 未命中", fontsize=10.5, color=style.C_GRAY,
                ha="center", va="center")
        fbox(ax, 81, 28, 21, 6.5, "查页表", style.C_LIGHT, style.C_BLUE)
        ax.text(81, 22.0, "150ns · 页 1 此时有效", fontsize=10.5,
                color=style.C_BLUE, ha="center", va="center")
        arrow(ax, (35, 28), (42, 28))
        arrow(ax, (61.9, 28), (70, 28))
    if stage >= 4:  # 合计与结论
        ax.text(50, 14.5, "合计：10 + 150 + 100000000 + 10 + 150 = 100000320 ns",
                fontsize=13, color=style.C_TEXT, ha="center", va="center",
                fontweight="bold")
        ax.text(50, 9.5, "缺页让本次访问慢了 60 多万倍", fontsize=13.5,
                color=style.C_RED, ha="center", va="center", fontweight="bold")
        ax.text(50, 5, "处理后：页 1 也登记进 TLB", fontsize=12,
                color=style.C_ORANGE, ha="center", va="center")


for stage in (1, 2, 3, 4):
    fig, ax = data_scene("访问 1505H → 页 1（页 1 初始无效）")
    draw_1505(ax, stage)
    style.snapshot(fig, frames, f"1505H stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)


# ============ 画面 4：访问 25E5H，TLB 命中（两个子画面） ============
def draw_25e5(ax, stage):
    """访问 25E5H：stage 1 TLB 命中；stage 2 直接得帧号仅 10ns"""
    fbox(ax, 28, 38, 26, 8, "查 TLB：命中！", style.C_LGREEN, style.C_GREEN, lw=2.4)
    ax.text(28, 32, "页 2 已在 TLB 中", fontsize=12, color=style.C_GREEN,
            ha="center", va="center")
    if stage >= 2:
        fbox(ax, 72, 38, 22, 8, "直接得帧号 256H", style.C_LGREEN, style.C_GREEN,
             fs=13)
        arrow(ax, (41.5, 38), (60.5, 38), color=style.C_GREEN)
        ax.text(50, 22, "仅 10ns", fontsize=21, color=style.C_GREEN,
                ha="center", va="center", fontweight="bold")
        ax.text(50, 13.5, "命中 TLB，免去查页表的 150ns", fontsize=13,
                color=style.C_GREEN, ha="center", va="center")


for stage in (1, 2):
    fig, ax = data_scene("访问 25E5H → 页 2（TLB 命中）")
    draw_25e5(ax, stage)
    style.snapshot(fig, frames, f"25E5H stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 5：尾帧小结 ============
fig, ax = style.new_fig(title="小结：快表 TLB 与三级时间")
ax.text(50, 45, "TLB = 页表的缓存（相联存储）", fontsize=15.5,
        color=style.C_TEXT, ha="center", va="center", fontweight="bold")
ax.text(50, 38.5, "命中率取决于程序的局部性", fontsize=14,
        color=style.C_TEXT, ha="center", va="center")
chips = [(20, "TLB 命中 10ns", style.C_BLUE, style.C_LIGHT),
         (50, "未命中 160ns", style.C_ORANGE, style.C_YELLOW),
         (80, "缺页 100ms", style.C_RED, style.C_PINK)]
for cx, txt, ec, fc in chips:
    fbox(ax, cx, 27, 22, 7, txt, fc, ec, fs=13.5, tc=ec)
# ≪ 字形在苹方系字体缺失，用文字「远小于」表达数量级关系
ax.text(35, 27, "远小于", fontsize=12.5, color=style.C_GRAY, ha="center", va="center")
ax.text(65, 27, "远小于", fontsize=12.5, color=style.C_GRAY, ha="center", va="center")
ax.text(50, 12, "回看：2025H 共 160ns；1505H 共 100000320 ns；25E5H 仅 10ns",
        fontsize=12.5, color=style.C_GRAY, ha="center", va="center")
style.snapshot(fig, frames, "尾帧小结")
style.hold(fig, frames, style.TAIL_HOLD)
plt.close(fig)

style.save_gif(frames, OUT)
print(f"[done] anim-09 总帧数={len(frames)}")
