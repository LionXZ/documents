# -*- coding: utf-8 -*-
"""动图 01：冒泡排序逐趟过程（数据：严蔚敏经典例 49 38 65 97 76 13 27 49'，升序）。

文档对应：第 8 章 排序 - 8.2 交换排序 -【例 8-2】。
运行：.venv-13003/bin/python scripts/anim/13003/anim_bubble.py
输出：09-计算机基础/数据结构与算法/images/13003-anim-bubble.gif
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

A = [49, 38, 65, 97, 76, 13, 27, 49]
LABEL = ["49", "38", "65", "97", "76", "13", "27", "49'"]   # 49' 用于稳定性演示

rec = Recorder()
qa_problems = []

def draw(vals, labels, hi=(), swapped=(), done_idx=(), title="", note="", hold=SUB, y=28, checkpoint=True):
    """画一帧：vals 当前数组；hi 橙色高亮（正在比较）；swapped 红色（刚交换）；done_idx 绿色（已归位）。"""
    fig, ax = new_fig(title or "冒泡排序（升序）：相邻比较，逆序交换", note)
    colors, tcolors = {}, {}
    for k in hi:
        colors[k] = C_HL
    for k in swapped:
        colors[k] = C_SWAP
    for k in done_idx:
        colors[k] = C_DONE
    xs = boxes_row(ax, labels, y, x0=7, w=8.2, gap=1.5, h=8,
                   colors=colors, fontsize=15)
    if hi and len(hi) == 2:
        ax.annotate("比较", xy=(sum(xs[k] for k in hi) / 2, y + 5.4),
                    ha="center", fontsize=12, color="#B26A00", fontweight="bold")
    img = rec.add(fig, hold=hold)
    if checkpoint:
        problems = check_frame(fig)
        qa_problems.extend(f"帧{len(rec.frames)}: " + p for p in problems)
    plt.close(fig)
    return img

# ---------- 模拟冒泡，记录每趟事件 ----------
n = len(A)
arr = A[:]
done = []   # 已归位下标

# 幕 0：初始序列（解释画面驻留 6 帧）
draw(arr, LABEL, title="冒泡排序（升序）：相邻比较，逆序交换",
     note="规则：从前往后两两比较，前大后小则交换 → 每趟把当前最大值「冒」到末尾",
     hold=HOLD)

for t in range(1, n):
    swapped_any = False
    # 第 t 趟：逐对演示
    for k in range(0, n - t):
        hi = (k, k + 1)
        need = arr[k] > arr[k + 1]
        note = f"第 {t} 趟 · 比较 {arr[k]} 与 {arr[k+1]}：" + ("前大后小 → 交换" if need else "顺序正常 → 不动")
        draw(arr, LABEL, hi=hi, done_idx=done, title=f"冒泡排序 · 第 {t} 趟", note=note, hold=SUB)
        if need:
            arr[k], arr[k + 1] = arr[k + 1], arr[k]
            swapped_any = True
            draw(arr, LABEL, swapped=(k + 1,), done_idx=done,
                 title=f"冒泡排序 · 第 {t} 趟", note=f"{arr[k+1]} > {arr[k]}，交换后", hold=SUB)
    done = list(range(n - t, n))
    note = f"第 {t} 趟结束：最大值 {arr[n-t]} 沉底归位（绿色区）" + ("，本轮无交换 → 排序可以提前结束" if not swapped_any else "")
    draw(arr, LABEL, done_idx=done, title=f"冒泡排序 · 第 {t} 趟 完成", note=note, hold=HOLD)
    if not swapped_any:
        break

# ---------- 结论幕（尾帧 >=8 秒） ----------
fig, ax = new_fig("冒泡排序 · 结论",
                  "n 个元素最多 n-1 趟；本例第 6 趟无交换，提前结束")
xs = boxes_row(ax, LABEL, 30, x0=7, w=8.2, gap=1.5, h=8,
               colors={k: C_DONE for k in range(n)}, fontsize=15)
ax.text(45, 18.5, "要点：① 每趟把当前最大值归位；② 无交换即整体有序，可提前结束", ha="center", fontsize=12.5, color=C_TEXT)
ax.text(45, 13.5, "③ 比较次数最多 n(n-1)/2；时间复杂度 O(n²)，额外空间 O(1)", ha="center", fontsize=12.5, color=C_TEXT)
ax.text(45, 8.5, "④ 稳定排序：相等元素不交换，两个 49 的先后保持不变", ha="center", fontsize=12.5, color="#1B5E20")
img = rec.add(fig, hold=FINAL_HOLD)
qa_problems.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa_problems
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-bubble.gif")
check_and_save(rec, out)
