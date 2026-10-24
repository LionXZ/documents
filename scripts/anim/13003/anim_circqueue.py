# -*- coding: utf-8 -*-
"""动图 12：循环队列出入队与队满判定。

数据与文档【例 3-2】一致：容量 M=6（牺牲一格判满），
入队 A,B,C → 出队 2 次 → 再入队 D,E,F,G 触发「假溢出/绕回」，(rear+1)%M==front 判满。
文档对应：第 3 章 栈与队列 - 3.2 队列。
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

M = 6
rec = Recorder()
qa = []

CX, CY, R = 30, 27, 13.5

def slot_xy(i):
    ang = -90 + i * 60   # 顶部顺时针
    rad = math.radians(ang)
    return CX + R * math.cos(rad), CY + R * math.sin(rad)

def draw(queue, front, rear, title, note, hi=(), hold=SUB, verdict=None):
    """queue: 长度 M 列表（None 为空）；front/rear 为逻辑下标。
    front/rear 用槽圆描边色标识（蓝=front、红=rear），文字图例固定在底部，避免动态标注重叠。"""
    fig, ax = new_fig(title, note)
    for i in range(M):
        x, y = slot_xy(i)
        v = queue[i]
        occupied = v is not None
        fc = C_HL if i in hi else (C_QUEUE if occupied else C_NODE)
        ec, lw = C_EDGE, 2.0
        if i == front and i == rear:
            ec, lw = "#6A1B9A", 3.6          # front=rear（队空起点）紫色
        elif i == front:
            ec, lw = "#1565C0", 3.6          # front 蓝描边
        elif i == rear:
            ec, lw = "#C62828", 3.6          # rear 红描边
        ax.add_patch(plt.Circle((x, y), 4.0, fc=fc, ec=ec, lw=lw, zorder=3))
        ax.text(x, y, v if v else "·", ha="center", va="center", fontsize=14,
                fontweight="bold", color=C_TEXT if v else C_DIM, zorder=4)
        ax.text(x * 0.59 + CX * 0.41, y * 0.59 + CY * 0.41, f"[{i}]", ha="center", va="center",
                fontsize=9.5, color=C_DIM, zorder=2)
    # 状态行
    cnt = len([v for v in queue if v is not None])
    ax.text(72, 40, f"front = {front}，rear = {rear}", ha="center", fontsize=13, color="#1565C0", fontweight="bold")
    ax.text(72, 33.5, f"元素个数 = {cnt}", ha="center", fontsize=13, color=C_TEXT)
    ax.text(72, 26, "入队：rear = (rear+1) mod M", ha="center", fontsize=11.5, color="#C62828")
    ax.text(72, 20.5, "出队：front = (front+1) mod M", ha="center", fontsize=11.5, color="#1565C0")
    ax.text(72, 14, "队满：(rear+1) mod M == front", ha="center", fontsize=11.5, color="#B26A00")
    ax.text(72, 8.5, "队空：front == rear", ha="center", fontsize=11.5, color="#455A64")
    # 底部图例（固定位置）
    ax.text(10, 5.5, "●蓝描边 = front 指向槽", ha="left", va="center", fontsize=11, color="#1565C0", fontweight="bold")
    ax.text(33, 5.5, "●红描边 = rear 指向槽", ha="left", va="center", fontsize=11, color="#C62828", fontweight="bold")
    ax.text(56, 5.5, "●紫 = front=rear（队空起点）", ha="left", va="center", fontsize=11, color="#6A1B9A", fontweight="bold")
    if verdict:
        ax.text(45, 1.5, verdict, ha="center", fontsize=13, fontweight="bold", color="#B71C1C")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 状态模拟
queue = [None] * M
front = rear = 0
draw(queue, front, rear, "循环队列 · 初始", "front 与 rear 都指向 0 → 队空（约定 rear 指向「下一个入队位置」）", hold=HOLD)

for name in ["A", "B", "C"]:
    queue[rear] = name
    rear = (rear + 1) % M
    draw(queue, front, rear, "循环队列 · 入队 A、B、C", f"{name} 入队 → rear 后移（mod M 绕圈）", hold=SUB)
draw(queue, front, rear, "循环队列 · 入队 A、B、C", "3 个元素入队：front=0，rear=3，个数 3", hold=HOLD)

for _ in range(2):
    queue[front] = None
    front = (front + 1) % M
draw(queue, front, rear, "循环队列 · 出队 2 次", "A、B 出队 → front 后移到 2；前面的格子「空出来」", hold=HOLD)

for name in ["D", "E", "F", "G"]:
    queue[rear] = name
    rear = (rear + 1) % M
    draw(queue, front, rear, "循环队列 · 再入队 D、E、F、G", f"{name} 入队 → rear 绕回头部继续走（循环的意义：复用空格）", hold=SUB)

draw(queue, front, rear, "循环队列 · 队满判定",
     "此时 (rear+1) mod 6 = 2 == front → 队满（牺牲一格区分空/满）",
     verdict="(rear+1) mod M == front → 队满，还剩 1 格也不能再入队", hold=HOLD)

# 结论幕
fig, ax = new_fig("循环队列 · 结论", "")
ax.text(45, 38, "① 顺序队列「假溢出」：出队后前部空格无法复用 → 取模循环解决", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 31.5, "② 入队 rear=(rear+1) mod M；出队 front=(front+1) mod M", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 25, "③ 牺牲一格判满：(rear+1) mod M == front（队空 = front == rear）", ha="center", fontsize=13.5, color="#B26A00")
ax.text(45, 18.5, "④ 实际容量 M-1；元素个数 = (rear-front+M) mod M", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 11, "记忆锚点：队列 = 先进先出 FIFO；循环队列把数组首尾逻辑相连", ha="center",
        fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-circqueue.gif")
check_and_save(rec, out)
