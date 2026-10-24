# -*- coding: utf-8 -*-
"""动图 11：出入栈序列合法性判断（栈混洗）。

数据与文档【例 3-1】一致：进栈序列 1, 2, 3, 4。
① 合法出栈序列 3, 2, 4, 1 的完整模拟；② 非法序列 4, 3, 1, 2 卡死演示。
结论：n 个不同元素进栈，出栈序列数 = 卡特兰数 C(2n,n)/(n+1)（n=4 时 14 种）。
文档对应：第 3 章 栈与队列 - 3.1 栈。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

INSEQ = ["1", "2", "3", "4"]
rec = Recorder()
qa = []

def draw(stack, popped, next_in, title, note, ok=True, hold=SUB, inptr=0, verdict=None):
    fig, ax = new_fig(title, note)
    # 左：进栈序列
    ax.text(14, 46, "进栈序列", ha="center", fontsize=12, color="#455A64", fontweight="bold")
    for k, v in enumerate(INSEQ):
        fc = C_DONE if k < inptr else (C_HL if k == inptr else C_NODE)
        ax.add_patch(plt.Rectangle((6 + k * 8.4, 36), 7.4, 6.4, fc=fc, ec=C_EDGE, lw=1.6, zorder=3))
        ax.text(9.7 + k * 8.4, 39.2, v, ha="center", va="center", fontsize=13, fontweight="bold", zorder=4)
    # 中：栈（竖直）
    ax.text(45, 46, "栈（后进先出）", ha="center", fontsize=12, color="#6A1B9A", fontweight="bold")
    ax.add_patch(plt.Rectangle((40, 14), 10, 28, fc="none", ec=C_EDGE, lw=2.2, zorder=2))
    for k, v in enumerate(stack):
        y = 17 + k * 6.4
        ax.add_patch(plt.Rectangle((41.4, y), 7.2, 5.6, fc=C_QUEUE, ec=C_EDGE, lw=1.5, zorder=3))
        ax.text(45, y + 2.8, v, ha="center", va="center", fontsize=13, fontweight="bold", zorder=4)
    if stack:
        ax.annotate("栈顶", xy=(50.4, 17 + (len(stack) - 1) * 6.4 + 2.8), xytext=(58, 43),
                    fontsize=11, color="#6A1B9A", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#6A1B9A"))
    # 右：出栈序列（目标）
    ax.text(74, 46, "出栈序列（目标）", ha="center", fontsize=12, color="#455A64", fontweight="bold")
    for k, v in enumerate(popped):
        ax.add_patch(plt.Rectangle((65 + k * 8.4, 36), 7.4, 6.4, fc=C_DONE, ec=C_EDGE, lw=1.6, zorder=3))
        ax.text(68.7 + k * 8.4, 39.2, v, ha="center", va="center", fontsize=13, fontweight="bold", zorder=4)
    if verdict:
        ax.text(45, 9, verdict, ha="center", fontsize=14, fontweight="bold",
                color="#1B5E20" if ok else "#B71C1C")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# ===== 幕 0 =====
draw([], [], 0, "出入栈序列 · 判断规则", "任何时刻：要么下一个元素进栈，要么栈顶出栈；栈顶不等于目标序列下一项且无可进栈 → 序列非法",
     hold=HOLD)

# ===== 幕 A：合法序列 3,2,4,1 =====
target = ["3", "2", "4", "1"]
stack, popped, ip = [], [], 0
draw(stack, popped, ip, "判断 3, 2, 4, 1 是否合法", "目标第 1 个出栈的是 3：1、2、3 依次进栈，3 在栈顶", hold=HOLD)
for v in ["1", "2", "3"]:
    stack.append(v); ip += 1
    draw(stack, popped, ip, "判断 3, 2, 4, 1 是否合法", f"{v} 进栈", hold=SUB, inptr=ip)
    if v == "3":
        break
for step, note in [
    ("3", "栈顶 3 = 目标 3 → 出栈"),
    ("2", "栈顶 2 = 目标 2 → 出栈"),
]:
    stack.pop(); popped.append(step)
    draw(stack, popped, ip, "判断 3, 2, 4, 1 是否合法", note, inptr=ip, hold=SUB)
stack.append("4"); ip += 1
draw(stack, popped, ip, "判断 3, 2, 4, 1 是否合法", "目标第 3 个是 4：4 进栈后在栈顶", inptr=ip, hold=SUB)
stack.pop(); popped.append("4")
draw(stack, popped, ip, "判断 3, 2, 4, 1 是否合法", "4 出栈", inptr=ip, hold=SUB)
stack.pop(); popped.append("1")
draw(stack, popped, ip, "判断 3, 2, 4, 1 是否合法", "最后栈顶 1 出栈 → 序列合法", inptr=ip,
     verdict="3, 2, 4, 1 是合法出栈序列", ok=True, hold=HOLD)

# ===== 幕 B：非法序列 4,3,1,2 =====
target = ["4", "3", "1", "2"]
stack, popped, ip = [], [], 0
draw(stack, popped, ip, "判断 4, 3, 1, 2 是否合法", "目标第 1 个出栈的是 4 → 必须把 1、2、3、4 全部进栈", hold=HOLD)
for v in INSEQ:
    stack.append(v); ip += 1
    draw(stack, popped, ip, "判断 4, 3, 1, 2 是否合法", f"{v} 进栈（为让 4 先出，只能全部先进栈）", inptr=ip, hold=SUB)
stack.pop(); popped.append("4")
draw(stack, popped, ip, "判断 4, 3, 1, 2 是否合法", "4 出栈（第一个目标满足）", inptr=ip, hold=SUB)
stack.pop(); popped.append("3")
draw(stack, popped, ip, "判断 4, 3, 1, 2 是否合法", "3 出栈（第二个目标满足）", inptr=ip, hold=SUB)
draw(stack, popped, ip, "判断 4, 3, 1, 2 是否合法",
     "下一个目标是 1，但栈顶是 2（1 压在 2 下面）；且 4 个元素已全部进栈，无法再进 → 卡死",
     inptr=ip, verdict="4, 3, 1, 2 是非法出栈序列（1 不可能先于 2 出栈）", ok=False, hold=HOLD)

# 结论幕
fig, ax = new_fig("出入栈序列 · 结论", "")
ax.text(45, 38, "① 判定法：按目标序列模拟——能进则进、栈顶即出；卡死即非法", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 31.5, "② 必非法特征：对任意 i<j<k，若 k 先出、j 后出，则 i 不能插在 j 前出栈", ha="center", fontsize=13, color="#B26A00")
ax.text(45, 25, "   （如 4,3,1,2：1 想先出，但它比 2 先进栈）", ha="center", fontsize=12.5, color="#B26A00")
ax.text(45, 18.5, "③ n 个不同元素依次进栈，出栈序列共有卡特兰数种：n=3 → 5 种，n=4 → 14 种", ha="center",
        fontsize=13.5, color=C_TEXT)
ax.text(45, 12, "记忆锚点：栈 = 后进先出 LIFO；进栈 push / 出栈 pop；栈空判 top<0（顺序栈）",
        ha="center", fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-stackseq.gif")
check_and_save(rec, out)
