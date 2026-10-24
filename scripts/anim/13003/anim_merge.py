# -*- coding: utf-8 -*-
"""动图 03：归并排序逐层合并（二路归并，自底向上）。

数据与文档【例 8-4】一致：49 38 65 97 76 13 27 49'。
文档对应：第 8 章 排序 - 8.4 归并排序。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

BASE = ["49", "38", "65", "97", "76", "13", "27", "49'"]
rec = Recorder()
qa = []

def seg_colors(groups, hi_group=None):
    """按组给 8 个元素着色；hi_group 指定的组高亮。"""
    colors = {}
    palette = [C_NODE, "#DCEDC8", "#B3E5FC", "#FFE0B2"]
    for gi, idxs in enumerate(groups):
        c = C_HL if gi == hi_group else palette[gi % len(palette)]
        for k in idxs:
            colors[k] = c
    return colors

def draw(groups, title, note, hi_group=None, hold=SUB, y=32, extra=None):
    fig, ax = new_fig(title, note)
    labels = sorted(BASE, key=lambda t: BASE.index(t))  # 保持原顺序
    boxes_row(ax, BASE, y, x0=11, w=7.6, gap=1.3, h=7.5,
              colors=seg_colors(groups, hi_group), fontsize=14, show_index=True)
    if extra:
        ax.text(45, 13, extra, ha="center", fontsize=12.5, color=C_TEXT, fontweight="bold")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

G0 = [[0], [1], [2], [3], [4], [5], [6], [7]]
G1 = [[0, 1], [2, 3], [4, 5], [6, 7]]
G2 = [[0, 1, 2, 3], [4, 5, 6, 7]]
G3 = [list(range(8))]

# 幕 0：初始
draw(G0, "归并排序 · 二路归并（自底向上）",
     "思想：初始每个元素自成长度 1 的有序段，两两归并 → 段长逐层加倍，直到整表有序", hold=HOLD)

# 第 1 层
draw(G1, "归并排序 · 第 1 层合并（段长 1 → 2）",
     "相邻两两归并：49/38 → 38 49；65/97 → 65 97；76/13 → 13 76；27/49' → 27 49'",
     hi_group=0, hold=HOLD)
draw(G1, "归并排序 · 第 1 层合并（段长 1 → 2）",
     "相邻两两归并：49/38 → 38 49；65/97 → 65 97；76/13 → 13 76；27/49' → 27 49'",
     hi_group=3, hold=HOLD)
draw(G1, "归并排序 · 第 1 层完成", "得到 4 个长度为 2 的有序段：38 49 / 65 97 / 13 76 / 27 49'", hold=HOLD)

# 第 2 层
draw(G2, "归并排序 · 第 2 层合并（段长 2 → 4）",
     "归并 [38 49] 与 [65 97]：互相比较取小者 → 38, 49, 65, 97（蓝段）",
     hi_group=0, hold=HOLD)
draw(G2, "归并排序 · 第 2 层合并（段长 2 → 4）",
     "归并 [13 76] 与 [27 49']：比较取小 → 13, 27, 49', 76（橙段）",
     hi_group=1, hold=HOLD)
draw(G2, "归并排序 · 第 2 层完成", "得到 2 个长度为 4 的有序段：38 49 65 97 / 13 27 49' 76", hold=HOLD)

# 第 3 层
draw(G3, "归并排序 · 第 3 层合并（段长 4 → 8）",
     "两段逐指针比较：38↔13 → 13；38↔27 → 27；38↔49' → 38；49↔49' → 49（相等取左段，稳定）",
     hold=HOLD)
draw(G3, "归并排序 · 第 3 层合并（段长 4 → 8）",
     "继续：65↔49' → 49'；65↔76 → 65；76↔76 → 76；收尾接 97 → 全表有序",
     hold=HOLD)

# 结论幕
fig, ax = new_fig("归并排序 · 结论", "三个有序段逐层向上归并，直到整表有序")
ys_rows = [
    ("初始", G0, None),
    ("第 1 层", G1, None),
    ("第 2 层", G2, None),
    ("第 3 层", G3, C_DONE),
]
for i, (name, groups, force) in enumerate(ys_rows):
    y = 42 - i * 8.2
    ax.text(5.5, y, name, ha="left", va="center", fontsize=12, color="#455A64", fontweight="bold")
    colors = seg_colors(groups)
    if force:
        colors = {k: C_DONE for k in range(8)}
    boxes_row(ax, BASE, y, x0=13, w=7.6, gap=1.3, h=6.4, colors=colors,
              fontsize=13, show_index=False)
ax.text(45, 9.5, "要点：① 时间复杂度恒为 O(n log₂n)（最好/最坏/平均都一样）", ha="center", fontsize=13, color=C_TEXT)
ax.text(45, 4.5, "② 额外空间 O(n)（辅助数组）；③ 稳定排序——两个 49 的先后保持不变", ha="center", fontsize=13, color="#1B5E20")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-merge.gif")
check_and_save(rec, out)
