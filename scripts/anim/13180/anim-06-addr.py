# -*- coding: utf-8 -*-
"""13180《操作系统》动图 06：页式虚拟地址转换。

数据（2026.4 真题综合题 37）：逻辑空间 64KB，页大小 4KB（2¹²），按字节编址
→ 页号 4 位、页内地址 12 位。页表：页 0→0A2H（有效）、页 1→080H（有效位 0，缺页）、
页 2→256H（有效）。转换逻辑地址 2025H = 0010 0000 0010 0101B → 物理地址 256025H；
缺页分支演示 1505H（页 1，有效位 0 → 缺页中断）。
分镜：题面 → 拆页号 → 拆偏移 → 查页表 → 拼接原理 → 计算结果 → 缺页分支 → 三步法尾帧。
QA 由 style.snapshot 内置检测。
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images/os-anim-06-addr.gif"

TITLE = "页式虚拟地址转换（2026.4 真题数据）"
PT_ROWS = [("页 0", "0A2H", "1"), ("页 1", "080H", "0"), ("页 2", "256H", "1")]
PT_Y = [40.0, 34.0, 28.0]          # 页表三行的中心 y


def draw_pagetable(ax, hl=None, hl_red=None):
    """右侧页表：hl 黄色高亮行，hl_red 红色高亮行。"""
    ax.add_patch(plt.Rectangle((62, 43.6), 34, 4.8, fc=style.C_LIGHT, ec=style.C_BLUE, lw=1.5))
    for cx, h in [(70, "页号"), (81, "帧号"), (92, "有效位")]:
        ax.text(cx, 46.0, h, ha="center", va="center", fontsize=11.5,
                fontweight="bold", color=style.C_BLUE)
    for i, (pg, fr, v) in enumerate(PT_ROWS):
        y = PT_Y[i]
        if i == hl:
            fc, ec, tc = "#FDE68A", style.C_ORANGE, style.C_TEXT
        elif i == hl_red:
            fc, ec, tc = style.C_LRED, style.C_RED, style.C_RED
        else:
            fc, ec, tc = "#FFFFFF", style.C_GRAY, style.C_TEXT
        ax.add_patch(plt.Rectangle((62, y - 2.4), 34, 4.8, fc=fc, ec=ec, lw=1.6))
        for cx, v2 in [(70, pg), (81, fr), (92, v)]:
            ax.text(cx, y, v2, ha="center", va="center", fontsize=12,
                    fontweight="bold" if (i == hl or i == hl_red) else "normal",
                    color=tc)


def draw_binary(ax, lo_bin, hi_bin, addr, hl_page=False, hl_off=False):
    """左上：逻辑地址与 16 位二进制（高 4 位 / 低 12 位分段显示）。"""
    ax.text(25.5, 50, f"逻辑地址 {addr}", ha="center", fontsize=15,
            fontweight="bold", color=style.C_TEXT)
    ax.text(23.5, 42, hi_bin, ha="center", va="center", fontsize=15,
            family="monospace", color=style.C_BLUE if hl_page else style.C_TEXT,
            fontweight="bold" if hl_page else "normal")
    ax.text(40.5, 42, lo_bin, ha="center", va="center", fontsize=15,
            family="monospace", color=style.C_GREEN if hl_off else style.C_TEXT,
            fontweight="bold" if hl_off else "normal")
    if hl_page:
        ax.add_patch(plt.Rectangle((21.2, 39.4), 4.6, 5.2, fc="none",
                                   ec=style.C_ORANGE, lw=2.4))
    if hl_off:
        ax.add_patch(plt.Rectangle((33.7, 39.4), 13.6, 5.2, fc="none",
                                   ec=style.C_GREEN, lw=2.4))


def notes(ax, lines):
    for y, t, c, fs, bold in lines:
        ax.text(30, y, t, ha="center", fontsize=fs, color=c,
                fontweight="bold" if bold else "normal")


def main():
    frames = []

    # ---- P1：题面 ----
    fig, ax = style.new_fig(title=TITLE)
    draw_binary(ax, "0000 0010 0101", "0010", "2025H")
    ax.add_patch(plt.Rectangle((62, 36), 34, 16, fc="#F7FAFC", ec=style.C_BLUE, lw=1.5))
    for y, t in [(48.6, "逻辑地址空间 64KB"),
                 (43.6, "页面大小 4KB（4096 字节）"),
                 (38.6, "按字节编址")]:
        ax.text(79, y, t, ha="center", fontsize=11.5, color=style.C_TEXT)
    notes(ax, [(22, "16 位逻辑地址：高 4 位是页号，低 12 位是页内地址",
                style.C_GRAY, 12, False),
               (17, "先按 4KB 页大小把 2025H 拆成两部分", style.C_GRAY, 12, False)])
    style.snapshot(fig, frames, "P1-题面")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P2a：高 4 位 = 页号 ----
    fig, ax = style.new_fig(title=TITLE)
    draw_binary(ax, "0000 0010 0101", "0010", "2025H", hl_page=True)
    draw_pagetable(ax)
    notes(ax, [(33, "高 4 位 = 页号：0010B = 2H", style.C_ORANGE, 13, True),
               (27.5, "为什么按 12 位切：4KB = 4096 字节 = 2 的 12 次方，页内地址恰占 12 位",
                style.C_TEXT, 12, False),
               (22.5, "页号 = 逻辑地址 ÷ 页大小（取整）= 2025H ÷ 1000H = 2",
                style.C_GRAY, 11.5, False)])
    style.snapshot(fig, frames, "P2a-拆页号")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P2b：低 12 位 = 页内偏移 ----
    fig, ax = style.new_fig(title=TITLE)
    draw_binary(ax, "0000 0010 0101", "0010", "2025H", hl_off=True)
    draw_pagetable(ax)
    notes(ax, [(33, "低 12 位 = 页内偏移：0000 0010 0101B = 025H",
                style.C_GREEN, 13, True),
               (27.5, "偏移 = 逻辑地址 mod 页大小 = 2025H mod 1000H = 025H",
                style.C_TEXT, 12, False),
               (22.5, "页内偏移在转换中保持不变，原样进入物理地址低位",
                style.C_GRAY, 11.5, False)])
    style.snapshot(fig, frames, "P2b-拆偏移")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P3：查页表 ----
    fig, ax = style.new_fig(title=TITLE)
    draw_binary(ax, "0000 0010 0101", "0010", "2025H", hl_page=True)
    draw_pagetable(ax, hl=2)
    ax.annotate("", xy=(61, 27.5), xytext=(25, 39),
                arrowprops=dict(arrowstyle="-|>", color=style.C_BLUE, lw=2.5,
                                connectionstyle="arc3,rad=0.25"))
    notes(ax, [(20, "页号 2 查页表 → 帧号 256H，有效位 = 1（该页在内存）",
                style.C_BLUE, 13, True),
               (15, "页 1 的有效位 = 0：该页当前不在内存（后面演示缺页）",
                style.C_GRAY, 11.5, False)])
    style.snapshot(fig, frames, "P3-查页表")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P4a：拼接原理（帧号在高位 + 偏移在低位）----
    fig, ax = style.new_fig(title=TITLE)
    draw_binary(ax, "0000 0010 0101", "0010", "2025H")
    draw_pagetable(ax, hl=2)
    for k, (ch, col) in enumerate([("2", style.C_BLUE), ("5", style.C_BLUE),
                                   ("6", style.C_BLUE), ("0", style.C_GREEN),
                                   ("2", style.C_GREEN), ("5", style.C_GREEN)]):
        x0 = 24 + k * 6
        ax.add_patch(plt.Rectangle((x0, 30), 6, 8,
                                   fc=style.C_LIGHT if col == style.C_BLUE else "#F0FFF4",
                                   ec=col, lw=1.8))
        ax.text(x0 + 3, 34, ch, ha="center", va="center", fontsize=16,
                fontweight="bold", color=col)
    ax.text(34, 27.2, "帧号 256H（来自页表）", ha="center", va="top", fontsize=11.5,
            fontweight="bold", color=style.C_BLUE)
    ax.text(53, 27.2, "偏移 025H", ha="center", va="top", fontsize=11.5,
            fontweight="bold", color=style.C_GREEN)
    notes(ax, [(22, "帧号相当于高位：×1000H 即左移 3 个十六进制位",
                style.C_TEXT, 12, False),
               (17, "页内偏移原样照抄到低位，不必换算", style.C_TEXT, 12, False)])
    style.snapshot(fig, frames, "P4a-拼接原理")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P4b：计算结果 ----
    fig, ax = style.new_fig(title=TITLE)
    draw_pagetable(ax, hl=2)
    notes(ax, [(44, "物理地址 = 帧号 × 1000H + 页内偏移", style.C_TEXT, 13.5, True),
               (36.5, "256H × 1000H + 025H", style.C_TEXT, 14, False),
               (29, "= 256000H + 025H", style.C_TEXT, 14, False),
               (20.5, "= 256025H", style.C_GREEN, 18, True)])
    style.snapshot(fig, frames, "P4b-计算结果")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P5：缺页分支（1505H → 页 1，有效位 0）----
    fig, ax = style.new_fig(title=TITLE)
    draw_binary(ax, "0101 0000 0101", "0001", "1505H", hl_page=True)
    draw_pagetable(ax, hl_red=1)
    notes(ax, [(33, "页号 = 0001B = 1 → 查页表：帧号 080H，有效位 = 0",
                style.C_ORANGE, 12.5, True),
               (25.5, "有效位 = 0 → 产生缺页中断：请求 OS 把该页调入内存",
                style.C_RED, 13, True),
               (20, "缺页调入完成后，重新执行被中断的那条指令", style.C_GRAY, 12, False)])
    style.snapshot(fig, frames, "P5-缺页分支")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P6：尾帧三步法 ----
    fig, ax = style.new_fig(title="页式地址转换三步法")
    lines = [
        (48, "① 按页大小切分逻辑地址：页号 = 高位，页内偏移 = 低位", style.C_TEXT, 13.5, True),
        (41, "② 页号查页表得帧号，同时检查有效位（0 → 缺页中断）", style.C_TEXT, 13.5, True),
        (34, "③ 物理地址 = 帧号（高位）拼接偏移（低位原样照抄）", style.C_TEXT, 13.5, True),
        (25, "本题：2025H → 页 2 → 帧 256H → 物理地址 256025H", style.C_GREEN, 13.5, True),
        (19, "反例：1505H → 页 1 有效位 0 → 缺页中断", style.C_RED, 12.5, False),
    ]
    for y, t, c, fs, bold in lines:
        ax.text(50, y, t, ha="center", fontsize=fs, color=c,
                fontweight="bold" if bold else "normal")
    style.snapshot(fig, frames, "P6-尾帧三步法")
    style.hold(fig, frames, style.TAIL_HOLD)
    plt.close(fig)

    style.save_gif(frames, OUT)


if __name__ == "__main__":
    main()
