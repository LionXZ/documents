# -*- coding: utf-8 -*-
"""anim-10-partition.py —— 13180《操作系统》教学动图：动态分区分配与回收。

数据：教学示例数据（画面标注「教学示例数据」）。
- 内存用户区 100KB；进程依次申请：A 30KB、B 20KB、C 40KB

画面清单：
1.  初始：100KB 整块空闲
2~4. 首次适应依次分配 A(0~30K)、B(30~50K)、C(50~90K)，剩 90~100K
5.   释放 B → 外部碎片（分区之间的小空闲块，总和够用但不连续）
6.   回收合并一：释放 A，与下邻空洞合并为 0~50K
7.   回收合并二：释放 C，上邻+下邻都空闲 → 三块合并回 0~100K
8.   尾帧：回收四种情况（02326 2023.4 简答同源考点）+ 四种分配算法
"""

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "操作系统/images/os-anim-10-partition.gif")

# 内存条画布：x 30~58，y 5~55；100KB 线性映射到 50 个纵坐标单位
BAR_X0, BAR_X1, BAR_Y0, BAR_Y1 = 30, 58, 5, 55
KB2Y = (BAR_Y1 - BAR_Y0) / 100.0

# 分区外观：kind -> (填充色, 边框色)
LOOK = {
    "free": (style.C_LGREEN, style.C_GREEN),
    "A": ("#BFDBFE", style.C_BLUE),
    "B": ("#E9D8FD", style.C_PURPLE),
    "C": ("#FED7D7", style.C_RED),
    "hole": (style.C_YELLOW, style.C_ORANGE),
}


def kb_y(kb):
    """KB 地址 → 画布 y 坐标（0K 在下、100K 在上）"""
    return BAR_Y0 + kb * KB2Y


def draw_mem(ax, blocks, hi=None, hi_label=None):
    """画内存条。blocks: [(起KB, 止KB, 类型, 标签)]；hi: 高亮区(起, 止)"""
    ax.add_patch(Rectangle((BAR_X0, BAR_Y0), BAR_X1 - BAR_X0, BAR_Y1 - BAR_Y0,
                           fc="white", ec=style.C_GRAY, lw=1.4))
    for lo, hi_kb, kind, label in blocks:
        fc, ec = LOOK[kind]
        ax.add_patch(Rectangle((BAR_X0 + 0.7, kb_y(lo)), BAR_X1 - BAR_X0 - 1.4,
                               kb_y(hi_kb) - kb_y(lo), fc=fc, ec=ec, lw=1.5))
        ax.text((BAR_X0 + BAR_X1) / 2, kb_y((lo + hi_kb) / 2), label,
                fontsize=11.5, color=style.C_TEXT, ha="center", va="center",
                fontweight="bold")
    if hi is not None:
        ax.add_patch(Rectangle((BAR_X0 + 0.2, kb_y(hi[0])), BAR_X1 - BAR_X0 - 0.4,
                               kb_y(hi[1]) - kb_y(hi[0]), fc="none",
                               ec=style.C_ORANGE, lw=2.4, ls="--"))
        if hi_label:
            ax.text(BAR_X0 - 1.5, kb_y((hi[0] + hi[1]) / 2), hi_label,
                    fontsize=11.5, color=style.C_ORANGE, ha="right", va="center")
    # 右侧地址刻度
    for kb in (0, 30, 50, 90, 100):
        ax.text(BAR_X1 + 1.5, kb_y(kb), f"{kb}K", fontsize=10,
                color=style.C_GRAY, ha="left", va="center")


def panel(ax, lines, y0=48.5, dy=4.6):
    """右侧信息面板：lines 为 (文本, 颜色, 字号, 是否加粗)"""
    y = y0
    for txt, color, fs, bold in lines:
        ax.text(64.5, y, txt, fontsize=fs, color=color, va="center",
                fontweight="bold" if bold else "normal")
        y -= dy


def scene(title):
    """新建带标题与示例数据角标的画布"""
    fig, ax = style.new_fig(title=title)
    ax.text(97.5, 57.3, "教学示例数据", fontsize=10, color=style.C_GRAY,
            ha="right", va="center")
    return fig, ax


AB = "A 30KB、B 20KB、C 40KB"

# ============ 画面 1：初始整块空闲 ============
frames = []
fig, ax = scene("动态分区分配与回收：初始状态")
draw_mem(ax, [(0, 100, "free", "空闲 100KB")])
panel(ax, [
    ("内存用户区：100KB", style.C_TEXT, 13.5, True),
    ("初始为一整块空闲区", style.C_TEXT, 13, False),
    ("进程依次申请：", style.C_TEXT, 13, True),
    (AB, style.C_BLUE, 13, False),
    ("动态分区：用多少、分多少", style.C_GRAY, 12.5, False),
])
style.snapshot(fig, frames, "初始")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)

# ============ 画面 2~4：首次适应依次分配 A、B、C ============
alloc_scenes = [
    ([(0, 30, "A", "A 30KB"), (30, 100, "free", "空闲 70KB")],
     [("申请 A：30KB", style.C_TEXT, 13.5, True),
      ("首次适应：从低地址开始找", style.C_TEXT, 13, False),
      ("第一个够大的空闲区装入", style.C_TEXT, 13, False),
      ("→ A 装入 0~30K", style.C_BLUE, 13.5, True),
      ("剩余空闲：30~100K", style.C_TEXT, 13, False)]),
    ([(0, 30, "A", "A 30KB"), (30, 50, "B", "B 20KB"),
      (50, 100, "free", "空闲 50KB")],
     [("申请 B：20KB", style.C_TEXT, 13.5, True),
      ("紧接 A 之后装入 30~50K", style.C_TEXT, 13, False),
      ("→ B 装入 30~50K", style.C_PURPLE, 13.5, True),
      ("剩余空闲：50~100K（50KB）", style.C_TEXT, 13, False)]),
    ([(0, 30, "A", "A 30KB"), (30, 50, "B", "B 20KB"),
      (50, 90, "C", "C 40KB"), (90, 100, "free", "空闲 10KB")],
     [("申请 C：40KB", style.C_TEXT, 13.5, True),
      ("→ C 装入 50~90K", style.C_RED, 13.5, True),
      ("剩余空闲：90~100K（仅 10KB）", style.C_ORANGE, 13, True),
      ("动态分区：按需划分，剩多少用多少", style.C_GRAY, 12.5, False)]),
]
for blocks, lines in alloc_scenes:
    fig, ax = scene("首次适应分配：按申请顺序从低址划分")
    draw_mem(ax, blocks)
    panel(ax, lines)
    style.snapshot(fig, frames, "分配")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 5：释放 B → 外部碎片 ============
fig, ax = scene("释放 B：产生外部碎片")
draw_mem(ax, [(0, 30, "A", "A 30KB"), (30, 50, "hole", "空洞 20KB"),
              (50, 90, "C", "C 40KB"), (90, 100, "free", "空闲 10KB")])
panel(ax, [
    ("B 结束，释放 20KB", style.C_TEXT, 13.5, True),
    ("30~50K 变成空洞（黄色）", style.C_TEXT, 13, False),
    ("外部碎片：分区之间的小空闲块，", style.C_RED, 12.5, True),
    ("总和够用但不连续", style.C_RED, 12.5, True),
])
style.snapshot(fig, frames, "外部碎片")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)

# ============ 画面 6：回收合并一（与下邻合并） ============
fig, ax = scene("回收合并一：A 释放后与下邻空闲区合并")
draw_mem(ax, [(0, 50, "free", "空闲 50KB"), (50, 90, "C", "C 40KB"),
              (90, 100, "free", "空闲 10KB")],
         hi=(0, 50), hi_label="合并为 0~50K")
panel(ax, [
    ("A 也结束，释放 30KB", style.C_TEXT, 13.5, True),
    ("A 的空洞（0~30K）与其下邻", style.C_TEXT, 13, False),
    ("空洞（30~50K）紧邻", style.C_TEXT, 13, False),
    ("→ 与下邻空闲区合并", style.C_GREEN, 13.5, True),
    ("0~30K + 30~50K = 0~50K", style.C_BLUE, 13, False),
])
style.snapshot(fig, frames, "下邻合并")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)

# ============ 画面 7：回收合并二（上邻+下邻都空闲） ============
fig, ax = scene("回收合并二：上邻、下邻都空闲 → 三块合并")
draw_mem(ax, [(0, 100, "free", "空闲 100KB")],
         hi=(0, 100), hi_label="三块合并为一块")
panel(ax, [
    ("C 也结束，释放 40KB", style.C_TEXT, 13.5, True),
    ("其上邻（0~50K）与下邻", style.C_TEXT, 13, False),
    ("（90~100K）都是空闲区", style.C_TEXT, 13, False),
    ("→ 三块合并为一块", style.C_GREEN, 13.5, True),
    ("内存恢复为 0~100K 完整空闲区", style.C_TEXT, 13, False),
])
style.snapshot(fig, frames, "三块合并")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)

# ============ 画面 8：尾帧——回收四种情况（同源真题考点） ============
fig, ax = style.new_fig(title="内存回收的四种情况（02326 · 2023.4 简答同源考点）")
ax.text(97.5, 57.3, "同源真题考点", fontsize=10, color=style.C_GRAY,
        ha="right", va="center")
cases = [
    ("① 上邻空闲 → 与上邻合并", 45),
    ("② 下邻空闲 → 与下邻合并", 38),
    ("③ 上下邻都空闲 → 三块合并为一块", 31),
    ("④ 上下邻都不空闲 → 单独作为新空闲分区登记", 24),
]
for txt, yc in cases:
    ax.text(10, yc, txt, fontsize=14, color=style.C_TEXT, va="center")
ax.plot([10, 90], [18.5, 18.5], color=style.C_GRAY, lw=1.0)
ax.text(10, 13, "分配算法：首次适应 / 最佳适应 / 最坏适应 / 邻近适应",
        fontsize=14.5, color=style.C_ORANGE, va="center", fontweight="bold")
ax.text(10, 7.5, "回收时按「上邻？下邻？」两个判断依次检查", fontsize=12,
        color=style.C_GRAY, va="center")
style.snapshot(fig, frames, "尾帧回收四情况")
style.hold(fig, frames, style.TAIL_HOLD)
plt.close(fig)

style.save_gif(frames, OUT)
print(f"[done] anim-10 总帧数={len(frames)}")
