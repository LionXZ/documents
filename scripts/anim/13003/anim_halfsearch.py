# -*- coding: utf-8 -*-
"""动图 13：折半查找（二分查找）逐步定位。

数据与文档【例 7-1】一致：有序表 5 13 19 21 37 56 64 75 80 88 92（11 个），查 21。
比较 3 次：56 → 19 → 21 命中。
文档对应：第 7 章 查找 - 7.2 折半查找。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

A = [5, 13, 19, 21, 37, 56, 64, 75, 80, 88, 92]
KEY = 21
rec = Recorder()
qa = []

def draw(low, high, mid, title, note, cmp_text="", hold=SUB, found=False, done_idx=()):
    fig, ax = new_fig(title, note)
    colors, tcolors = {}, {}
    for k in range(low, high + 1):
        colors[k] = C_VIS
    colors[mid] = C_DONE if found else C_HL
    labels = [str(v) for v in A]
    xs = boxes_row(ax, labels, 30, x0=7, w=6.6, gap=1.3, h=8, colors=colors, fontsize=13)
    # 指针（mid 与 low/high 同位时横向偏移文字，避免重叠）
    mid_off = 0
    if mid == low:
        mid_off = 4
    elif mid == high:
        mid_off = -4
    for val, idx, color, yoff in (("low", low, "#1565C0", -11), ("high", high, "#C62828", 11), ("mid", mid, "#E65100", -11)):
        arrow(ax, xs[idx], 30 + yoff, xs[idx], 30 + (4.6 if yoff < 0 else -4.6), color=color, lw=2.6)
        tx = xs[idx] + (mid_off if val == "mid" else 0)
        ax.text(tx, 30 + yoff - (2.6 if yoff < 0 else -2.6), val, ha="center",
                fontsize=11.5, color=color, fontweight="bold")
    ax.text(45, 8.5, cmp_text, ha="center", fontsize=13, color=C_TEXT, fontweight="bold")
    if found:
        ax.text(45, 3, f"查找成功：{KEY} 在表中第 4 位，共比较 3 次", ha="center",
                fontsize=13.5, color="#1B5E20", fontweight="bold")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 幕 0
draw(0, 10, 5, "折半查找 · 前提与初值", "前提：顺序存储 + 有序（关键前提，常考判断题）；low=0，high=10，mid=(low+high)//2", hold=HOLD)

# 第 1 次：mid=5 (56)
draw(0, 10, 5, "折半查找 · 第 1 次比较", "mid = (0+10)//2 = 5 → A[5] = 56", cmp_text=f"56 > {KEY} → 目标在左半区间，high = mid - 1 = 4")
# 第 2 次：mid=2 (19)
draw(0, 4, 2, "折半查找 · 第 2 次比较", "mid = (0+4)//2 = 2 → A[2] = 19", cmp_text=f"19 < {KEY} → 目标在右半区间，low = mid + 1 = 3")
# 第 3 次：mid=3 (21)
draw(3, 4, 3, "折半查找 · 第 3 次比较", "mid = (3+4)//2 = 3 → A[3] = 21", cmp_text=f"A[mid] = {KEY} → 命中！", found=True)

# 查找 62 失败演示（区间收敛到空）
draw(0, 10, 5, "对照：查找 62（失败）", "第 1 次 mid=5：56 < 62 → low = 6", cmp_text="56 < 62 → low = mid + 1 = 6")
draw(6, 10, 8, "对照：查找 62（失败）", "第 2 次 mid=8：80 > 62 → high = 7", cmp_text="80 > 62 → high = mid - 1 = 7")
draw(6, 7, 6, "对照：查找 62（失败）", "第 3 次 mid=6：64 > 62 → high = 5", cmp_text="64 > 62 → high = mid - 1 = 5")
draw(7, 5, 6, "对照：查找 62（失败）", "low=7 > high=5 → 区间为空，查找失败", cmp_text="low > high → 查找失败（62 不在表中）",
     hold=HOLD, found=False)

# 结论幕
fig, ax = new_fig("折半查找 · 结论", "")
ax.text(45, 38, "① mid = (low + high) // 2；与 A[mid] 比三分：相等命中 / 小则 high=mid-1 / 大则 low=mid+1", ha="center",
        fontsize=12.8, color=C_TEXT)
ax.text(45, 31.5, "② 最多比较 ⌈log₂(n+1)⌉ 次（n=11 → 4 次内）；时间复杂度 O(log₂n)", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 25, "③ 前提铁律：顺序存储（随机存取）+ 关键字有序——链表不能折半", ha="center", fontsize=13.5, color="#B71C1C", fontweight="bold")
ax.text(45, 18.5, "④ 判定树：中间结点为根，左右子树各半——n 个元素的判定树是平衡的", ha="center", fontsize=13, color=C_TEXT)
ax.text(45, 11, "记忆锚点：折半 = 每次砍一半；失败出口 = low > high", ha="center", fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-halfsearch.gif")
check_and_save(rec, out)
