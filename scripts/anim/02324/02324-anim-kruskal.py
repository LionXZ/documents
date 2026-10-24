# -*- coding: utf-8 -*-
"""Kruskal 最小生成树 动图脚本。
数据来源：自编教学数据，与文档例题同步（ANIM_SPEC 锚定，一个数字不许改）
    V={A,B,C,D,E}，无向带权边：AB=1、AC=2、BC=3、CD=4、BD=5、CE=6、DE=7
    选边顺序：AB1 选入、AC2 选入、BC3 成环弃、CD4 选入、BD5 成环弃、CE6 选入
    MST = {AB, AC, CD, CE}，W = 1+2+4+6 = 13
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
set_style()
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D

# ---------- 数据锚定（并查集程序验算，与 SPEC 不符则拒绝运行） ----------
EDGES = [("AB", 1), ("AC", 2), ("BC", 3), ("CD", 4), ("BD", 5), ("CE", 6), ("DE", 7)]
POS = {"A": (1.0, 4.3), "B": (4.2, 4.3), "C": (1.9, 2.9),
       "D": (3.9, 1.2), "E": (1.0, 1.2)}
SPEC_MST = ["AB", "AC", "CD", "CE"]

fa = {v: v for v in POS}                       # 并查集模拟 Kruskal 选边
def find(x):
    while fa[x] != x:
        x = fa[x]
    return x
mst = []
for name, w in EDGES:                          # 按权升序逐边考察
    u, v = name[0], name[1]
    if find(u) != find(v):                     # 不连通则选入并合并
        fa[find(u)] = find(v)
        mst.append(name)
    if len(mst) == 4:                          # 选满 |V|-1 条即终止
        break
assert mst == SPEC_MST and sum(w for n, w in EDGES if n in mst) == 13, "数据与 SPEC 不符"

OUT = "09-计算机基础/离散数学/images/02324-anim-kruskal.gif"

# ---------- 帧工具 ----------
def frame(title):
    """新画布：数据坐标 x:0-10，y:0-5.68（与像素等比）。"""
    fig, ax = new_fig(title)
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.68)
    ax.axis("off")
    return fig, ax

def add(gb, fig, ctx, n=1):
    """QA 通过才允许入帧；有问题抛出（须修到 0）。"""
    p = qa_figure(fig, ctx=ctx)
    assert p == 0, f"{ctx} QA 问题 {p} 个，禁止保存"
    gb.add(fig, n=n)

# ---------- 绘制 ----------
VTX_LBL = {"A": (1.0, 4.75), "B": (4.2, 4.75), "C": (1.42, 3.0),
           "D": (4.05, 0.78), "E": (1.0, 0.75)}          # 顶点标签偏移位
W_LBL = {"AB": (2.6, 4.62), "AC": (1.05, 3.86), "BC": (3.38, 3.35),
         "CD": (3.22, 2.38), "BD": (4.55, 2.8), "CE": (1.0, 2.22),
         "DE": (2.45, 0.8)}                                # 边权标签位
R = 0.26                                                   # 顶点圆半径

def draw_graph(ax, chosen=(), cur=None, dropped=(), show_w=True):
    """画左图。chosen=已选入边(绿粗)，cur=当前考察边(红粗)，
    dropped=已弃边(灰虚线)，其余原图边为淡灰细线。"""
    for name, w in EDGES:
        p1, p2 = POS[name[0]], POS[name[1]]
        if name in chosen:
            c, lw, ls, z = C_OK, 3.6, "-", 3
        elif name == cur:
            c, lw, ls, z = C_HIGH, 3.6, "-", 3
        elif name in dropped:
            c, lw, ls, z = C_DIM, 1.6, (0, (4, 3)), 2
        else:
            c, lw, ls, z = C_DIM, 1.6, "-", 1
        ax.add_line(Line2D([p1[0], p2[0]], [p1[1], p2[1]],
                           color=c, lw=lw, linestyle=ls, zorder=z))
        if show_w:
            ax.text(*W_LBL[name], str(w), ha="center", va="center",
                    fontsize=13, color=c if c != C_DIM else "#718096",
                    fontweight="bold", zorder=4)
    for v, (x, y) in POS.items():
        ax.add_patch(Circle((x, y), R, facecolor="#dbeafe",
                            edgecolor=C_MAIN, lw=1.6, zorder=5))
        ax.text(*VTX_LBL[v], v, ha="center", va="center",
                fontsize=15, color="#2d3748", fontweight="bold", zorder=6)

ROW_Y = [4.45, 4.02, 3.59, 3.16, 2.73, 2.30, 1.87]   # 右侧 7 行列表的纵坐标

def draw_panel(ax, hi=None, state=None):
    """右侧排序面板。hi=高亮行下标，state={边名: (文字, 颜色)}。"""
    ax.text(6.35, 4.92, "边按权从小到大排序", ha="center", va="center",
            fontsize=14, color="#2d3748", fontweight="bold")
    state = state or {}
    for i, (name, w) in enumerate(EDGES):
        if i == hi:
            ax.add_patch(Rectangle((5.75, ROW_Y[i] - 0.19), 3.95, 0.38,
                                   facecolor=C_MARK, edgecolor="none", zorder=1))
        col = "#4a5568" if i != hi else "#2d3748"
        ax.text(5.95, ROW_Y[i], f"{i + 1}. {name}  权 {w}",
                ha="left", va="center", fontsize=13.5, color=col, zorder=2)
        if name in state:
            s, c = state[name]
            ax.text(9.45, ROW_Y[i], s, ha="right", va="center",
                    fontsize=13.5, color=c, fontweight="bold", zorder=2)

TITLE = "Kruskal 最小生成树：每次选「权最小且不成环」的边"
gb = GifBuilder(fps=2)

# ---- 帧 1：开场，展示原图 ----
fig, ax = frame(TITLE)
draw_graph(ax)
ax.text(7.7, 1.05, "5 个顶点 7 条带权边\n目标：连接所有顶点\n且总权最小",
        ha="center", va="center", fontsize=13.5, color="#4a5568")
add(gb, fig, "开场", n=6)

# ---- 帧 2：边按权排序 ----
fig, ax = frame(TITLE)
draw_graph(ax)
draw_panel(ax)
ax.text(7.7, 1.05, "从权最小的边开始逐条考察", ha="center", va="center",
        fontsize=13.5, color=C_HIGH)
add(gb, fig, "排序", n=6)

# ---- 帧 3：逐边考察（选满 4 条即终止，DE=7 不再考察） ----
REASON = {"AB": "A、B 尚不连通 ⇒ 选入，权 1",
          "AC": "A、C 尚不连通 ⇒ 选入，权 2",
          "BC": "B、C 已连通（B-A-C），选入会成环 ⇒ 弃",
          "CD": "C、D 尚不连通 ⇒ 选入，权 4",
          "BD": "B、D 已连通（B-A-C-D），成环 ⇒ 弃",
          "CE": "C、E 尚不连通 ⇒ 选入，权 6"}
chosen, dropped, state = [], [], {}
for i, (name, w) in enumerate(EDGES[:6]):
    u, v = name[0], name[1]
    fig, ax = frame(TITLE)
    draw_graph(ax, chosen=chosen, cur=name, dropped=dropped)
    draw_panel(ax, hi=i, state=state)
    ax.text(7.7, 0.85, f"考察 {name}（权 {w}）……", ha="center", va="center",
            fontsize=13.5, color=C_HIGH, fontweight="bold")
    add(gb, fig, f"{name}-考察", n=2)
    if u + v in ("AB", "AC", "CD", "CE"):
        chosen.append(name)
        state[name] = ("选入", C_OK)
    else:
        dropped.append(name)
        state[name] = ("弃", C_HIGH)
    fig, ax = frame(TITLE)
    draw_graph(ax, chosen=chosen, dropped=dropped)
    draw_panel(ax, state=state)
    ax.text(7.7, 0.85, REASON[name], ha="center", va="center",
            fontsize=13.5, color=state[name][1])
    add(gb, fig, f"{name}-结果", n=6)

# ---- 帧 4：算法终止 ----
fig, ax = frame(TITLE)
draw_graph(ax, chosen=chosen, dropped=dropped)
draw_panel(ax, state=state)
ax.text(7.7, 0.9, "已选 4 = 5−1 条边 ⇒ 生成树完成\nDE（权 7）无需再考察",
        ha="center", va="center", fontsize=13, color="#2d3748")
add(gb, fig, "终止", n=6)

# ---- 尾帧：MST 结果与总权 ----
fig, ax = frame("Kruskal 最小生成树：结果（总权 13）")
draw_graph(ax, chosen=chosen, dropped=dropped)
draw_panel(ax, state=state)
ax.text(7.7, 0.95, "MST = {AB, AC, CD, CE}", ha="center", va="center",
        fontsize=15, color=C_OK, fontweight="bold")
ax.text(7.7, 0.42, "W = 1 + 2 + 4 + 6 = 13", ha="center", va="center",
        fontsize=15, color=C_OK, fontweight="bold")
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
assert ok, "GIF 超过 2MB"
