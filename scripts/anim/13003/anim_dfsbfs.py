# -*- coding: utf-8 -*-
"""动图 06：图的 BFS（队列）与 DFS（栈）演变。

图与文档【例 6-1】一致（严蔚敏 G4）：
边：v1-v2, v1-v3, v2-v4, v3-v5, v4-v6, v5-v6
BFS 序列 v1 v2 v3 v4 v5 v6；DFS 序列 v1 v2 v4 v6 v5 v3（邻接点按编号小者优先）。
文档对应：第 6 章 图 - 6.3 遍历。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

POS = {"v1": (18, 38), "v2": (10, 25), "v3": (30, 30),
       "v4": (14, 12), "v5": (36, 16), "v6": (27, 5)}
EDGES = [("v1", "v2"), ("v1", "v3"), ("v2", "v4"), ("v3", "v5"), ("v4", "v6"), ("v5", "v6")]
rec = Recorder()
qa = []

def draw(title, note, visited=(), cur=None, aux=(), aux_kind="queue", seq=(),
         active_edge=None, hold=SUB, aux_note=""):
    fig, ax = new_fig(title, note)
    # 图区（左半）
    for a, b in EDGES:
        on = active_edge and {a, b} == set(active_edge)
        x1, y1 = POS[a]; x2, y2 = POS[b]
        arrow(ax, x1, y1, x2, y2, color="#E65100" if on else C_EDGE,
              lw=3.2 if on else 1.8, style="-", zorder=1)
    for name, (x, y) in POS.items():
        fc = C_DONE if name in visited else C_NODE
        if name == cur:
            fc = C_HL
        ax.add_patch(plt.Circle((x, y), 3.3, fc=fc, ec=C_EDGE, lw=1.8, zorder=3))
        ax.text(x, y, name, ha="center", va="center", fontsize=12.5,
                fontweight="bold", color=C_TEXT, zorder=4)
    # 右栏：辅助结构（队列/栈）
    ax.text(70, 45, ("队  列" if aux_kind == "queue" else "栈") + "（辅存待访问）",
            ha="center", fontsize=12.5, color="#455A64", fontweight="bold")
    n = len(aux)
    for k, name in enumerate(aux):
        if aux_kind == "queue":
            x = 56 + k * 11
            label = name
        else:
            x = 70
            y_ = 39 - k * 6.4
            ax.add_patch(plt.Rectangle((x - 5, y_ - 2.6), 10, 5.2, fc=C_QUEUE, ec=C_EDGE, lw=1.5, zorder=3))
            ax.text(x, y_, name, ha="center", va="center", fontsize=12.5, fontweight="bold", zorder=4)
            continue
        y_ = 39
        ax.add_patch(plt.Rectangle((x - 5, y_ - 2.6), 10, 5.2, fc=C_QUEUE, ec=C_EDGE, lw=1.5, zorder=3))
        ax.text(x, y_, label, ha="center", va="center", fontsize=12.5, fontweight="bold", zorder=4)
    if aux_kind == "queue" and aux:
        ax.text(52.5, 39, "队头→", ha="right", va="center", fontsize=10.5, color="#6A1B9A", fontweight="bold")
    if aux_kind == "stack" and aux:
        ax.annotate("栈顶", xy=(76.5, 39 - 0 * 6.4), xytext=(82, 42),
                    fontsize=10.5, color="#6A1B9A", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#6A1B9A"))
    if aux_note:
        ax.text(70, 8, aux_note, ha="center", fontsize=11.5, color="#6A1B9A", fontweight="bold")
    # 访问序列
    for k, s in enumerate(seq):
        ax.text(58 + k * 5.6, 16, s, ha="center", va="center", fontsize=12,
                fontweight="bold", color="#1565C0")
    ax.text(70, 21, "访问序列", ha="center", fontsize=11, color="#455A64")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# ---------- BFS ----------
bfs_steps = [
    # (cur, visited, aux, seq, active_edge, note)
    ("v1", ["v1"], ["v2", "v3"], ["v1"], None, "访问 v1，把邻接点 v2、v3 依次入队", HOLD),
    ("v1", ["v1"], ["v2", "v3"], ["v1"], ("v1", "v2"), "v1 出队后处理其邻接点：v2 入队", SUB),
    ("v1", ["v1"], ["v2", "v3"], ["v1"], ("v1", "v3"), "接着 v3 入队", SUB),
    ("v2", ["v1", "v2"], ["v3", "v4"], ["v1", "v2"], ("v2", "v4"), "队头 v2 出队并访问；其未访问邻接点 v4 入队", HOLD),
    ("v3", ["v1", "v2", "v3"], ["v4", "v5"], ["v1", "v2", "v3"], ("v3", "v5"), "v3 出队并访问；v5 入队", HOLD),
    ("v4", ["v1", "v2", "v3", "v4"], ["v5", "v6"], ["v1", "v2", "v3", "v4"], ("v4", "v6"), "v4 出队并访问；v6 入队", HOLD),
    ("v5", ["v1", "v2", "v3", "v4", "v5"], ["v6"], ["v1", "v2", "v3", "v4", "v5"], None, "v5 出队并访问；邻接点均已访问，无新入队", HOLD),
    ("v6", ["v1", "v2", "v3", "v4", "v5", "v6"], [], ["v1", "v2", "v3", "v4", "v5", "v6"], None, "v6 出队并访问；队列空 → BFS 结束", HOLD),
]
for cur, vis, aux, seq, edge, note, hold in bfs_steps:
    draw(f"广度优先 BFS · 借助队列", note, visited=vis, cur=cur, aux=aux,
         aux_kind="queue", seq=seq, active_edge=edge, hold=hold)

# ---------- DFS ----------
dfs_steps = [
    ("v1", ["v1"], ["v1"], ["v1"], None, "访问 v1，v1 进栈", HOLD),
    ("v2", ["v1", "v2"], ["v1", "v2"], ["v1", "v2"], ("v1", "v2"), "v1 的邻接点 v2 未访问 → 访问 v2 并进栈", HOLD),
    ("v4", ["v1", "v2", "v4"], ["v1", "v2", "v4"], ["v1", "v2", "v4"], ("v2", "v4"), "v2 的邻接点 v1 已访问、v4 未访问 → 访问 v4 进栈", HOLD),
    ("v6", ["v1", "v2", "v4", "v6"], ["v1", "v2", "v4", "v6"], ["v1", "v2", "v4", "v6"], ("v4", "v6"), "v4 的邻接点 v6 未访问 → 访问 v6 进栈", HOLD),
    ("v5", ["v1", "v2", "v4", "v6", "v5"], ["v1", "v2", "v4", "v6", "v5"], ["v1", "v2", "v4", "v6", "v5"], ("v6", "v5"), "v6 的邻接点 v5 未访问 → 访问 v5 进栈", HOLD),
    ("v3", ["v1", "v2", "v4", "v6", "v5", "v3"], ["v1", "v2", "v4", "v6", "v5", "v3"], ["v1", "v2", "v4", "v6", "v5", "v3"], ("v5", "v3"), "v5 的邻接点 v3 未访问 → 访问 v3 进栈", HOLD),
    ("v3", ["v1", "v2", "v4", "v6", "v5", "v3"], [], ["v1", "v2", "v4", "v6", "v5", "v3"], None,
     "v3 无未访问邻接点 → 依次退栈回溯，栈空 → DFS 结束", HOLD),
]
for cur, vis, aux, seq, edge, note, hold in dfs_steps:
    draw("深度优先 DFS · 借助栈", note, visited=vis, cur=cur, aux=aux,
         aux_kind="stack", seq=seq, active_edge=edge, hold=hold)

# 结论幕
fig, ax = new_fig("BFS 与 DFS · 结论", "")
ax.text(24, 38, "BFS", ha="center", fontsize=15, fontweight="bold", color="#6A1B9A")
ax.text(24, 32.5, "辅助结构：队列（先进先出）", ha="center", fontsize=12.5, color=C_TEXT)
ax.text(24, 27.5, "序列：v1 v2 v3 v4 v5 v6", ha="center", fontsize=12.5, color=C_TEXT, fontweight="bold")
ax.text(24, 22.5, "按「层次」扩散，先访问的邻接点先扩展", ha="center", fontsize=12, color="#455A64")
ax.text(66, 38, "DFS", ha="center", fontsize=15, fontweight="bold", color="#6A1B9A")
ax.text(66, 32.5, "辅助结构：栈（后进先出）", ha="center", fontsize=12.5, color=C_TEXT)
ax.text(66, 27.5, "序列：v1 v2 v4 v6 v5 v3", ha="center", fontsize=12.5, color=C_TEXT, fontweight="bold")
ax.text(66, 22.5, "一条路走到底，走不通再回溯", ha="center", fontsize=12, color="#455A64")
ax.text(45, 13, "共同点：每个顶点恰访问一次；邻接矩阵存贮时总时间 O(n²)，邻接表 O(n+e)", ha="center",
        fontsize=13, color="#1B5E20", fontweight="bold")
ax.text(45, 8, "注意：遍历序列不唯一——取决于邻接点的排列次序（本例按编号从小到大）", ha="center", fontsize=12, color="#B26A00")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-dfsbfs.gif")
check_and_save(rec, out)
