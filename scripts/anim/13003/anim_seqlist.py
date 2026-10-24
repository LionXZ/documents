# -*- coding: utf-8 -*-
"""动图 09：顺序表插入与删除（元素移动过程）。

数据与文档【例 2-1】一致：
表 (3, 6, 11, 17, 25)：① 在第 3 个位置插入 15 → 17、25 依次后移；② 删除第 2 个元素 6 → 后面依次前移。
文档对应：第 2 章 线性表 - 2.1 顺序表。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

rec = Recorder()
qa = []

def draw(vals, hi=(), moved=(), title="", note="", hold=SUB, ghost=None):
    """vals 展示数组；hi 黄=关注位；moved 红=刚移动；ghost=(idx,label) 幽灵占位。"""
    fig, ax = new_fig(title, note)
    labels = [str(v) for v in vals]
    if ghost:
        idx, label = ghost
        labels = labels[:idx] + [label] + labels[idx:]
    colors = {}
    for k in hi:
        colors[k] = C_HL
    for k in moved:
        colors[k] = C_SWAP
    boxes_row(ax, labels, 30, x0=10, w=8.6, gap=1.6, h=8, colors=colors, fontsize=14.5)
    ax.text(45, 16, "位序（从 1 起）：插入/删除都要移动元素，等概率平均移动 n/2 个",
            ha="center", fontsize=11.5, color="#455A64")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# ============ 幕 A：插入 ============
arr = [3, 6, 11, 17, 25]
draw(arr, title="顺序表 · 在第 3 位插入 15", note="顺序表按位序存储：插入前先空出第 3 位 → 第 5、4 位元素依次后移",
     hold=HOLD)
# 后移：从最后一个开始（25 → 17）
draw(arr, hi=(4,), title="顺序表 · 插入 15：元素后移", note="第 5 位 25 后移（从表尾往前挪，防止覆盖）", hold=SUB)
draw(arr, hi=(4,), moved=(5,), ghost=(5, ""), title="顺序表 · 插入 15：元素后移",
     note="25 后移到第 6 位（扩容后新格）", hold=SUB)
arr2 = [3, 6, 11, 17, 25]
draw(arr2, hi=(3,), moved=(4,), ghost=(5, ""), title="顺序表 · 插入 15：元素后移",
     note="接着 17 后移到第 5 位", hold=SUB)
draw([3, 6, 11, 17, 25, ""], hi=(2,), moved=(), ghost=None, title="顺序表 · 插入 15：元素后移",
     note="第 3 位已空出", hold=SUB)
draw([3, 6, 11, 15, 17, 25], hi=(3,), title="顺序表 · 插入完成", note="15 写入第 3 位；表长 5 → 6",
     hold=HOLD)

# ============ 幕 B：删除 ============
arr = [3, 6, 11, 17, 25]
draw(arr, hi=(1,), title="顺序表 · 删除第 2 个元素 6", note="删除后须把后面元素依次前移补位（从被删位后一个开始）",
     hold=HOLD)
draw([3, "", 11, 17, 25], hi=(1,), title="顺序表 · 删除 6", note="6 被删除，位置 2 空出", hold=SUB)
draw([3, 11, 11, 17, 25], hi=(2,), moved=(1,), title="顺序表 · 删除 6：前移补位",
     note="11 前移到第 2 位", hold=SUB)
draw([3, 11, 17, 17, 25], hi=(3,), moved=(2,), title="顺序表 · 删除 6：前移补位",
     note="17 前移到第 3 位", hold=SUB)
draw([3, 11, 17, 25, 25], hi=(4,), moved=(3,), title="顺序表 · 删除 6：前移补位",
     note="25 前移到第 4 位", hold=SUB)
draw([3, 11, 17, 25], title="顺序表 · 删除完成", note="表长 5 → 4；逻辑上第 5 位作废", hold=HOLD)

# 结论幕
fig, ax = new_fig("顺序表插删 · 结论", "")
ax.text(45, 38, "① 按位序 i 插入：第 n…i 位依次后移，平均移动 n/2 → 时间 O(n)", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 31.5, "② 按位序 i 删除：第 i+1…n 位依次前移，平均移动 (n-1)/2 → 时间 O(n)", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 25, "③ 后移从表尾往前、前移从被删位往后——顺序不能反，否则覆盖丢数据", ha="center", fontsize=13.5, color="#B26A00")
ax.text(45, 18.5, "④ 优点：随机存取 O(1)；缺点：插删须移动大量元素（与链表对照）", ha="center", fontsize=13.5, color=C_TEXT)
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-seqlist.gif")
check_and_save(rec, out)
