# -*- coding: utf-8 -*-
"""动图 02：快速排序一趟 partition（填坑法）+ 分治递归结构。

数据与文档【例 8-3】一致：49 38 65 97 76 13 27 49'，枢轴取首元素 49。
文档对应：第 8 章 排序 - 8.2 交换排序。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

LABEL = ["49", "38", "65", "97", "76", "13", "27", "49'"]
arr = [49, 38, 65, 97, 76, 13, 27, 49]

rec = Recorder()
qa = []

def draw(a, pivot_idx=None, hole=None, low=None, high=None, filled=None,
         title="", note="", hold=SUB):
    fig, ax = new_fig(title or "快速排序 · 一趟划分（枢轴 = 首元素 49）", note)
    colors, tcolors = {}, {}
    if filled:
        for k in filled:
            colors[k] = C_DONE
    xs = boxes_row(ax, LABEL, 30, x0=7, w=8.2, gap=1.5, h=8, colors=colors, fontsize=14)
    # 枢轴标记（坑/已就位）
    if pivot_idx is not None:
        px = xs[pivot_idx]
        ax.annotate("枢轴", xy=(px, 41), ha="center", fontsize=11, color="#B26A00", fontweight="bold")
    if hole is not None:
        colors[hole] = C_HL
        ax.patches[-1].set_fc(C_HL) if False else None
    # low / high 指针箭头
    if low is not None:
        arrow(ax, xs[low], 19, xs[low], 25.2, color="#1565C0", lw=2.6)
        ax.text(xs[low], 16.4, "low", ha="center", fontsize=12, color="#1565C0", fontweight="bold")
    if high is not None:
        arrow(ax, xs[high], 41.5, xs[high], 35.2, color="#C62828", lw=2.6)
        ax.text(xs[high], 44.2, "high", ha="center", fontsize=12, color="#C62828", fontweight="bold")
    # 重新画高亮覆盖（在数组之上）
    for k, c in ((hole, C_HL),):
        if k is not None:
            ax.add_patch(plt.Rectangle((xs[k] - 4.1, 26), 8.2, 8, fc=c, ec=C_EDGE, lw=1.6, zorder=5, alpha=0.55))
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 幕 0：初始（枢轴 49 存入临时变量，位置 0 成坑）
draw(arr, pivot_idx=0, hole=0, low=0, high=7, title="快速排序 · 一趟划分（填坑法）",
     note="第 1 步：枢轴 = 首元素 49 暂存，位置 0 变成「坑」；目标：比 49 小的甩左边、大的甩右边",
     hold=HOLD)

# 填坑法逐步（手工推导，与文档例 8-2 每步一致）
steps = [
    # (说明, 操作后数组, low, high, hole, 被移动值来源)
    ("high 从右向左找比 49 小的数：49' 不小于 49，越过；找到 27 → 填入左端坑，右侧位置 6 成为新坑",
     [27, 38, 65, 97, 76, 13, 27, 49], 0, 5, 6),
    ("low 从左向右找比 49 大的数：38 不是；65 满足 → 填入右侧坑，位置 2 成为新坑",
     [27, 38, 13, 97, 76, 13, 65, 49], 2, 6, 2),
    ("high 继续向左找比 49 小的：13 满足 → 填入左侧坑，位置 5 成为新坑",
     [27, 38, 13, 97, 76, 13, 65, 49], 2, 4, 5),
    ("low 继续向右找比 49 大的：97 满足 → 填入右侧坑，位置 3 成为新坑",
     [27, 38, 13, 97, 76, 97, 65, 49], 3, 5, 3),
    ("high 向左扫：76 不小于 49；high 与 low 相遇于位置 3 → 枢轴 49 落坑，划分完成",
     [27, 38, 13, 97, 76, 97, 65, 49], 3, 4, 3),
]
i = 0
low, high, hole = 0, 7, 0
for note, a2, low2, high2, hole2 in steps:
    i += 1
    last = (i == len(steps))
    if i in (1, 3):
        draw(a2, pivot_idx=None, hole=hole2, low=low2, high=high2,
             title=f"快速排序 · 一趟划分（第 {i+1} 步）", note=note, hold=SUB)
        # 修正数据（把被移动值真正写入演示数组）
        arr2 = list(a2)
        draw(arr2, pivot_idx=None, hole=hole2, low=low2, high=high2,
             title=f"快速排序 · 一趟划分（第 {i+1} 步）", note=note.split("→")[-1].strip(),
             hold=SUB)
    else:
        draw(a2, pivot_idx=None, hole=hole2, low=low2, high=high2,
             title=f"快速排序 · 一趟划分（第 {i+1} 步）", note=note, hold=SUB)
    low, high, hole = low2, high2, hole2

# 幕：枢轴落位结果
final = [27, 38, 13, 49, 76, 97, 65, 49]
draw(final, pivot_idx=3, filled=[3], title="快速排序 · 一趟划分完成",
     note="枢轴 49 就位于第 4 位：左侧 {27,38,13} 全小、右侧 {76,97,65,49'} 全大", hold=HOLD)

# 幕：分治递归结构
fig, ax = new_fig("快速排序 · 分治递归", "对枢轴左右两个子表递归做同样划分，直到子表长度 ≤ 1")
rows = [
    ("[49  38  65  97  76  13  27  49']", 45, 40, C_NODE),
    ("[27  38  13]   49   [76  97  65  49']", 45, 32, C_VIS),
    ("[13]  [27]  [38]        [49'  65]  [76]  [97]", 45, 24, C_DONE),
    ("最终有序：13  27  38  49  49'  65  76  97", 45, 15, C_DONE),
]
for txt, x, y, c in rows:
    ax.text(x, y, txt, ha="center", va="center", fontsize=13.5,
            color=C_TEXT, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", fc=c, ec=C_EDGE))
arrow(ax, 33, 38.6, 26, 34.4, color=C_EDGE)
arrow(ax, 57, 38.6, 64, 34.4, color=C_EDGE)
img = rec.add(fig, hold=HOLD)
qa.extend("递归幕: " + p for p in check_frame(fig))
plt.close(fig)

# 结论幕
fig, ax = new_fig("快速排序 · 结论", "")
ax.text(45, 40, "① 每趟选定枢轴：小的甩左、大的甩右，枢轴落定最终位置", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 33, "② 平均 / 最好 O(n log₂n)；最坏（基本有序时）O(n²)", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 26, "③ 额外空间 O(log₂n)（递归栈）；本例 8 元素一趟比较约 7 次", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 19, "④ 不稳定排序：相等元素相对次序可能改变", ha="center", fontsize=13.5, color="#B71C1C")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-quick.gif")
check_and_save(rec, out)
