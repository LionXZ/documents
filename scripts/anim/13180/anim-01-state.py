# -*- coding: utf-8 -*-
"""13180《操作系统》动图 01：进程五状态转换图。

分镜：
 1. 三主状态框（就绪/运行/阻塞）淡色占位 + 旁注
 2. 加入 新建/终止 两侧框与两条箭头，凑齐五状态
 3~8. 逐条绘制转换箭头并旁注原因（每条一个画面，箭头红色高亮）
 9. 特别标注：阻塞 → 运行 不存在（必须先经就绪）
 10. 尾帧：完整五状态图 + 口诀
QA 由 style.snapshot 内置（文字越界/两两重叠检测）。
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images/os-anim-01-state.gif"

# 状态框：(中心x, 中心y, 宽, 高, 填充色, 边框色, 中文名, 英文名)
BOXES = [
    (12, 47, 17, 7, "#F3EEFB", style.C_PURPLE, "新建", "(New)"),
    (88, 47, 19, 7, "#F5F5F5", style.C_GRAY, "终止", "(Terminated)"),
    (32, 33, 18, 7.5, style.C_LIGHT, style.C_BLUE, "就绪", "(Ready)"),
    (68, 33, 18, 7.5, style.C_LGREEN, style.C_GREEN, "运行", "(Running)"),
    (50, 8.5, 20, 7.5, style.C_YELLOW, style.C_ORANGE, "阻塞/等待", "(Blocked)"),
]

# 转换箭头：(起点, 终点, 弧度)，前 4 条为三状态间转换，后 2 条为外侧转换
ARROWS = [
    ((42.5, 35.2), (57.5, 35.2), 0.28),    # 就绪→运行（上拱）
    ((57.5, 30.8), (42.5, 30.8), -0.28),   # 运行→就绪（下拱，与上拱弧对称分开）
    ((61.5, 29.0), (53.5, 12.8), 0.0),     # 运行→阻塞
    ((46.5, 12.8), (37.0, 29.0), 0.0),     # 阻塞→就绪
    ((17.0, 43.4), (24.5, 36.9), 0.0),     # 创建→就绪
    ((74.0, 36.9), (82.5, 43.4), 0.0),     # 运行→终止
]

# 每条转换的旁注（与 ARROWS 下标一一对应，数字与口径按分镜）
NOTES = [
    ("就绪 → 运行", "进程调度：被调度程序选中，获得 CPU"),
    ("运行 → 就绪", "时间片用完 / 被更高优先级抢占"),
    ("运行 → 阻塞", "请求资源或等待事件（如 I/O）"),
    ("阻塞 → 就绪", "等待的事件发生（如 I/O 完成）"),
    ("创建 → 就绪", "进程创建完成，进入就绪队列"),
    ("运行 → 终止", "进程完成，或异常终止"),
]


def draw_scene(show_arrows=True, show_outer=True, highlight=-1,
               note1=None, note2=None, note_color=None):
    """画一幅完整场景并返回 (fig, ax)。highlight=-1 表示不高亮任何箭头。"""
    fig, ax = style.new_fig(title="进程五状态转换图")
    for i, (p0, p1, rad) in enumerate(ARROWS):
        outer = i >= 4
        if not show_arrows or (not show_outer and outer):
            continue
        is_hl = (i == highlight)
        ax.annotate("", xy=p1, xytext=p0,
                    arrowprops=dict(
                        arrowstyle="-|>", mutation_scale=22,
                        color=style.C_RED if is_hl else style.C_GRAY,
                        lw=4.0 if is_hl else 2.0,
                        connectionstyle=f"arc3,rad={rad}"))
    for cx, cy, w, h, fc, ec, zh, en in BOXES:
        ax.add_patch(plt.Rectangle((cx - w / 2, cy - h / 2), w, h,
                                   fc=fc, ec=ec, lw=2, zorder=3))
        ax.text(cx, cy + 1.7, zh, ha="center", va="center", fontsize=14.5,
                fontweight="bold", color=style.C_TEXT, zorder=4)
        ax.text(cx, cy - 2.0, en, ha="center", va="center", fontsize=9.5,
                color=style.C_GRAY, zorder=4)
    if note1:
        ax.text(50, 52.5, note1, ha="center", fontsize=15, fontweight="bold",
                color=note_color or style.C_TEXT)
    if note2:
        ax.text(50, 46.2, note2, ha="center", fontsize=12,
                color=note_color or style.C_TEXT)
    return fig, ax


def scene(frames, tag, hold, extra=None, **kw):
    """统一流程：画场景 → 可选附加绘制 → QA 快照 → 驻留 → 关闭。"""
    fig, ax = draw_scene(**kw)
    if extra:
        extra(ax)
    style.snapshot(fig, frames, tag)
    style.hold(fig, frames, hold)
    plt.close(fig)


def main():
    frames = []
    # 画面 1：三个基本状态
    scene(frames, "P1-三主状态", style.HOLD_MIN,
          show_arrows=False,
          note1="进程的三个基本状态",
          note2="就绪 · 运行 · 阻塞 —— 转换箭头接下来逐条加入")
    # 画面 2：加入新建/终止
    scene(frames, "P2-五状态", style.HOLD_MIN,
          note1="加入「新建」与「终止」",
          note2="五种状态齐了：创建后进入系统，终止后退出系统")
    # 画面 3~8：逐条转换 + 原因
    for i, (t1, t2) in enumerate(NOTES):
        scene(frames, f"P{3 + i}-{t1}", style.HOLD_MIN,
              highlight=i, note1=t1, note2=t2)

    # 画面 9：阻塞不能直达运行（补一条红色虚线示意此路不通）
    def extra9(ax):
        ax.annotate("", xy=(64, 29.2), xytext=(56.5, 12.8),
                    arrowprops=dict(arrowstyle="-|>", color=style.C_RED,
                                    lw=2.2, linestyle=(0, (4, 3)), alpha=0.9))
        ax.text(67.5, 20.0, "此路不通", fontsize=11.5, color=style.C_RED)

    scene(frames, "P9-阻塞不能直达运行", style.HOLD_MIN,
          note1="阻塞 → 运行 不存在",
          note2="阻塞必须先回到就绪，再经进程调度才能获得 CPU",
          note_color=style.C_RED, extra=extra9)

    # 画面 10：尾帧口诀
    scene(frames, "P10-尾帧口诀", style.TAIL_HOLD,
          note1="就绪等待 CPU · 运行正在执行 · 阻塞等待事件",
          note2="单向箭头共 6 条，阻塞不能直达运行",
          note_color=style.C_BLUE)

    style.save_gif(frames, OUT)


if __name__ == "__main__":
    main()
