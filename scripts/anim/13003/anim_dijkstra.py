# -*- coding: utf-8 -*-
"""动图 07：Dijkstra 最短路径（按路径长度递增次序）。

图与文档【例 6-3】一致：有向边 A→B=1, A→C=4, B→C=2, B→D=6, C→D=3。
从 A 出发到各顶点：A=0, B=1, C=3(经 B), D=6(经 C)。
文档对应：第 6 章 图 - 6.5 最短路径。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

POS = {"A": (14, 30), "B": (33, 38), "C": (33, 16), "D": (56, 27)}
DIRECTED = [("A", "B", 1), ("A", "C", 4), ("B", "C", 2), ("B", "D", 6), ("C", "D", 3)]
rec = Recorder()
qa = []

def midpoint(p1, p2, off=2.6):
    """取线段中点并向外偏移，放权值标签。"""
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    norm = max(1e-9, (dx * dx + dy * dy) ** 0.5)
    # 左法线方向偏移
    return mx - dy / norm * off, my + dx / norm * off

def draw(title, note, dist, settled, cur=None, relax_edge=None, hold=SUB, path_edge=None):
    fig, ax = new_fig(title, note)
    # 边
    for a, b, w in DIRECTED:
        hot = relax_edge and (a, b) == relax_edge
        onpath = path_edge and (a, b) in path_edge
        x1, y1 = POS[a]; x2, y2 = POS[b]
        arrow(ax, x1, y1, x2, y2,
              color="#E65100" if hot else ("#1565C0" if onpath else C_EDGE),
              lw=3.4 if (hot or onpath) else 1.8, zorder=1)
        lx, ly = midpoint(POS[a], POS[b], 3.0)
        ax.text(lx, ly, str(w), ha="center", va="center", fontsize=12, fontweight="bold",
                color="#37474F",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", zorder=2))
    # 顶点（上标 dist）
    for name, (x, y) in POS.items():
        fc = C_DONE if name in settled else C_NODE
        if name == cur:
            fc = C_HL
        ax.add_patch(plt.Circle((x, y), 3.6, fc=fc, ec=C_EDGE, lw=1.8, zorder=3))
        ax.text(x, y, name, ha="center", va="center", fontsize=13.5, fontweight="bold", zorder=4)
        d = dist[name]
        ax.text(x, y + 5.4, "∞" if d is None else str(d), ha="center", fontsize=12,
                fontweight="bold", color="#0D47A1" if d is not None else "#90A4AE", zorder=4)
    # 右栏：状态表
    ax.text(74, 44, "dist / 是否已确定", ha="center", fontsize=12.5, color="#455A64", fontweight="bold")
    for k, name in enumerate("ABCD"):
        y = 38 - k * 6.4
        d = dist[name]
        mark = "已确定" if name in settled else ("候选" if d is not None else "未知")
        ax.text(66, y, f"{name} : " + ("∞" if d is None else str(d)), ha="left", va="center",
                fontsize=13, fontweight="bold", color="#0D47A1" if d is not None else "#90A4AE")
        ax.text(84, y, mark, ha="center", va="center", fontsize=10.5,
                color="#1B5E20" if name in settled else "#616161")
    ax.text(74, 11, "绿=已确定最短路；蓝=当前 dist", ha="center", fontsize=10.5, color="#616161")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 初始
dist = {"A": 0, "B": None, "C": None, "D": None}
draw("Dijkstra · 初始化", "源点 A 的 dist=0，其余为 ∞；每轮从未确定者中选 dist 最小的顶点",
     dist, set(), hold=HOLD)

# 轮 1：选 A
draw("Dijkstra · 第 1 轮", "选 dist 最小的 A(0) → A 已确定",
     dist, {"A"}, cur="A", hold=SUB)
dist = {"A": 0, "B": 1, "C": 4, "D": None}
draw("Dijkstra · 第 1 轮", "松弛 A 的出边：B = 0+1 = 1；C = 0+4 = 4",
     dist, {"A"}, relax_edge=("A", "B"), hold=SUB)
draw("Dijkstra · 第 1 轮", "松弛 A 的出边：B = 0+1 = 1；C = 0+4 = 4",
     dist, {"A"}, relax_edge=("A", "C"), hold=SUB)

# 轮 2：选 B
draw("Dijkstra · 第 2 轮", "候选 B(1)、C(4) 中选最小 → B(1) 已确定",
     dist, {"A", "B"}, cur="B", hold=SUB)
dist = {"A": 0, "B": 1, "C": 3, "D": 7}
draw("Dijkstra · 第 2 轮", "松弛 B 的出边：C = 1+2 = 3 < 4 更新；D = 1+6 = 7",
     dist, {"A", "B"}, relax_edge=("B", "C"), hold=SUB)
draw("Dijkstra · 第 2 轮", "松弛 B 的出边：C = 3；D = 7",
     dist, {"A", "B"}, relax_edge=("B", "D"), hold=SUB)

# 轮 3：选 C
draw("Dijkstra · 第 3 轮", "候选 C(3)、D(7) 中选最小 → C(3) 已确定",
     dist, {"A", "B", "C"}, cur="C", hold=SUB)
dist = {"A": 0, "B": 1, "C": 3, "D": 6}
draw("Dijkstra · 第 3 轮", "松弛 C 的出边：D = 3+3 = 6 < 7 更新",
     dist, {"A", "B", "C"}, relax_edge=("C", "D"), hold=SUB)

# 轮 4：选 D
draw("Dijkstra · 第 4 轮", "只剩 D(6) → D 已确定；全部顶点完成",
     dist, {"A", "B", "C", "D"}, cur="D", hold=HOLD)

# 结论幕：最短路径树
fig, ax = new_fig("Dijkstra · 结果与结论", "A 到各顶点最短路径与长度")
POS2 = {"A": (22, 36), "B": (40, 43), "C": (40, 22), "D": (60, 33)}
for a, b in [("A", "B"), ("B", "C"), ("C", "D")]:
    x1, y1 = POS2[a]; x2, y2 = POS2[b]
    arrow(ax, x1, y1, x2, y2, color="#1565C0", lw=3.4, zorder=1)
for name, (x, y) in POS2.items():
    ax.add_patch(plt.Circle((x, y), 3.6, fc=C_DONE, ec=C_EDGE, lw=1.8, zorder=3))
    ax.text(x, y, name, ha="center", va="center", fontsize=13.5, fontweight="bold", zorder=4)
ax.text(80, 40, "A→B：1（直达）", ha="center", fontsize=13, color=C_TEXT, fontweight="bold")
ax.text(80, 33, "A→C：3（A-B-C）", ha="center", fontsize=13, color=C_TEXT, fontweight="bold")
ax.text(80, 26, "A→D：6（A-B-C-D）", ha="center", fontsize=13, color=C_TEXT, fontweight="bold")
ax.text(80, 19, "（绕行比直达短：4→3、7→6）", ha="center", fontsize=11, color="#455A64")
ax.text(45, 9, "要点：按路径长度递增次序逐个确定；「贪心」——每轮选当前 dist 最小者；时间复杂度 O(n²)",
        ha="center", fontsize=13, color="#1B5E20", fontweight="bold")
ax.text(45, 4, "注意：dist 一旦标记「已确定」不再改变；负权边不适用", ha="center", fontsize=12, color="#B26A00")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-dijkstra.gif")
check_and_save(rec, out)
