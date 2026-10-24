# -*- coding: utf-8 -*-
"""等价关系与划分 动图脚本。

数据来源：ANIM_SPEC 锚定（2026.04 证明题第 34 题真题思想的具化例）
    A = {1,2,3,4}，f: 1→x, 2→x, 3→y, 4→y；〈a,b〉∈R ⇔ f(a)=f(b)
    R = {〈1,1〉,〈2,2〉,〈3,3〉,〈4,4〉,〈1,2〉,〈2,1〉,〈3,4〉,〈4,3〉}（8 个序偶）
    等价类：[1]={1,2}，[3]={3,4}；结论：等价关系 ⇔ 划分
动画幕次：分团 → 补自反 → 补对称 → 传递自动成立 → 等价类与划分
注：苹方 .ttc 无法被 matplotlib 加载，显式改用 Arial Unicode MS；
    数学角括号用 U+3008/3009〈〉（苹方/Arial 均有字形）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse

# 字体：苹方 .ttc 加载失败会退化 DejaVu（中文豆腐块），改用 Arial Unicode MS
plt.rcParams["font.family"] = ["Arial Unicode MS"]
set_style()

# ---------- 数据锚定与程序验算（一个数字都不改） ----------
A = [1, 2, 3, 4]
FVAL = {1: "x", 2: "x", 3: "y", 4: "y"}
# R 按定义生成：〈a,b〉∈R 当且仅当 f(a)=f(b)
R_REL = {(a, b) for a in A for b in A if FVAL[a] == FVAL[b]}
assert R_REL == {(1, 1), (2, 2), (3, 3), (4, 4),
                 (1, 2), (2, 1), (3, 4), (4, 3)}, "R 与 SPEC 不符"
assert len(R_REL) == 8
CLS1 = {b for b in A if (1, b) in R_REL}
CLS3 = {b for b in A if (3, b) in R_REL}
assert CLS1 == {1, 2} and CLS3 == {3, 4}, "等价类与 SPEC 不符"
assert CLS1.isdisjoint(CLS3) and CLS1 | CLS3 == set(A), "应构成 A 的划分"

OUT = "09-计算机基础/离散数学/images/02324-anim-equivalence.gif"

# ---------- 布局：上团 x={1,2}，下团 y={3,4}（等比数据坐标） ----------
POS = {1: (6.3, 4.35), 2: (8.3, 4.35), 3: (6.3, 1.45), 4: (8.3, 1.45)}
PAIR_XY = {   # 左侧 R 序偶账本坐标（自环先行，再对称偶）
    (1, 1): (1.05, 3.55), (2, 2): (1.95, 3.55),
    (1, 2): (2.85, 3.55), (2, 1): (3.75, 3.55),
    (3, 3): (1.05, 3.10), (4, 4): (1.95, 3.10),
    (3, 4): (2.85, 3.10), (4, 3): (3.75, 3.10)}
CLS_FACE = {1: "#90cdf4", 2: "#90cdf4", 3: "#9ae6b4", 4: "#9ae6b4"}  # 点染色
CLS_BG = {1: "#bee3f8", 3: "#c6f6d5"}     # 团底色：[1] 淡蓝、[3] 淡绿

def frame(title):
    """新画布：x 0-10，y 0-5.68（与像素等比）。"""
    fig, ax = new_fig(title)
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.68)
    ax.axis("off")
    return fig, ax

def add(gb, fig, ctx, n=1):
    """QA 通过才入帧，有问题直接断言失败。"""
    p = qa_figure(fig, ctx=ctx)
    assert p == 0, f"{ctx} QA 问题 {p} 个，禁止保存"
    gb.add(fig, n=n)

def stage(ax, text, color="#4a5568"):
    """左下角步骤解说行。"""
    ax.text(2.4, 0.5, text, ha="center", va="center", fontsize=13, color=color)

def badge(ax, text, expl=None, color=C_HIGH):
    """中段幕标签 + 一句说明。"""
    ax.text(7.3, 3.0, text, ha="center", va="center", fontsize=16,
            fontweight="bold", color=color)
    if expl:
        ax.text(7.3, 2.55, expl, ha="center", va="center",
                fontsize=13, color="#4a5568")

def draw_panel(ax, nodes=(), lit=()):
    """左侧信息板：f 对应 + R 的 8 个序偶账本（lit 已亮，其余灰色待补）。"""
    for a in A:
        col = "#2d3748" if a in nodes else C_DIM
        ax.text(1.6 if a in (1, 3) else 3.1, 5.05 if a in (1, 2) else 4.62,
                f"f({a})={FVAL[a]}", ha="center", va="center",
                fontsize=14, color=col)
    ax.text(2.9, 4.08, "关系 R（共 8 个序偶）", ha="center", va="center",
            fontsize=14, color=C_MAIN)
    for pair, (x, y) in PAIR_XY.items():
        col = "#2d3748" if pair in lit else C_DIM
        ax.text(x, y, f"〈{pair[0]},{pair[1]}〉", ha="center", va="center",
                fontsize=14, color=col)

def draw_graph(ax, nodes=(), loops=(), edges=(), rings=(), fill=None,
               classes=(), cls_label=()):
    """右侧关系图。
    nodes 已出现点；loops 已补自环（上团画上方、下团画下方）；
    edges 已连的团内线（一条线代表对称的两个序偶）；rings 当前步高亮；
    fill 覆盖点填充色；classes 画哪些团的等价类底色；cls_label 标哪些类。"""
    ax.text(7.3, 5.18, "f 值 = x", ha="center", va="center",
            fontsize=13, color="#2c5282")
    ax.text(7.3, 0.52, "f 值 = y", ha="center", va="center",
            fontsize=13, color="#276749")
    for c in classes:
        yy = 4.35 if c == 1 else 1.45
        ax.add_patch(Ellipse((7.3, yy), 3.2, 1.16, facecolor=CLS_BG[c],
                             edgecolor="none", alpha=0.9, zorder=0))
    for (a, b) in edges:
        (x1, y1), (x2, y2) = POS[a], POS[b]
        ax.plot([x1 + 0.28, x2 - 0.28], [y1, y2], color=C_MAIN, lw=2.2,
                zorder=1)
    for v in POS:
        if v not in nodes:
            continue
        x, y = POS[v]
        face = (fill or {}).get(v, "#dbeafe")
        ax.add_patch(Circle((x, y), 0.26, facecolor=face,
                            edgecolor=C_MAIN, lw=1.6, zorder=3))
        ax.text(x, y, str(v), ha="center", va="center", fontsize=14,
                color="#1a365d", fontweight="bold", zorder=4)
        if v in loops:      # 自环小圆：贴在点外侧（上团在上、下团在下）
            sgn = 1 if y > 3 else -1
            ax.add_patch(Circle((x, y + sgn * 0.40), 0.14, facecolor="none",
                                edgecolor=C_HIGH, lw=2.0, zorder=2))
    for v in rings:         # 当前步高亮环
        x, y = POS[v]
        ax.add_patch(Circle((x, y), 0.40, facecolor="none",
                            edgecolor=C_HIGH, lw=2.6, zorder=2))
    for c in cls_label:     # 等价类标签
        if c == 1:
            ax.text(7.3, 3.88, "[1] = {1,2}", ha="center", va="center",
                    fontsize=14, fontweight="bold", color="#2c5282")
        else:
            ax.text(7.3, 1.95, "[3] = {3,4}", ha="center", va="center",
                    fontsize=14, fontweight="bold", color="#276749")

gb = GifBuilder(fps=2)
TITLE = "等价关系与划分  A={1,2,3,4}，〈a,b〉∈R ⇔ f(a)=f(b)"

# ---- 幕一：按 f 值把 4 个顶点分成两团 ----
fig, ax = frame(TITLE)
draw_panel(ax)
draw_graph(ax)
stage(ax, "定义：〈a,b〉∈R 当且仅当 f(a)=f(b)", color=C_MAIN)
add(gb, fig, "幕1-定义", n=6)

seen = []
for v, note in [(1, "1 的 f 值为 x → 放入上团"),
                (2, "2 的 f 值为 x → 放入上团"),
                (3, "3 的 f 值为 y → 放入下团"),
                (4, "4 的 f 值为 y → 放入下团")]:
    seen.append(v)
    fig, ax = frame(TITLE)
    draw_panel(ax, nodes=seen)
    draw_graph(ax, nodes=seen)
    stage(ax, note, color=C_HIGH)
    add(gb, fig, f"幕1-放点{v}", n=2)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A)
draw_graph(ax, nodes=A)
badge(ax, "按 f 值分团", "f 值相同的点聚成一团：{1,2}（x）与 {3,4}（y）",
      color=C_MAIN)
stage(ax, "R 现在还是空关系，下面逐条补序偶")
add(gb, fig, "幕1-分团完成", n=6)

# ---- 幕二：补自反环 〈1,1〉〈2,2〉〈3,3〉〈4,4〉 ----
done_loop = []
for v in A:
    done_loop.append(v)
    fig, ax = frame(TITLE)
    draw_panel(ax, nodes=A, lit={(a, a) for a in done_loop})
    draw_graph(ax, nodes=A, loops=done_loop, rings=[v])
    badge(ax, "① 自反", "自反：每个 a∈A 都有 〈a,a〉∈R → 逐点补自环")
    stage(ax, f"补自环 〈{v},{v}〉", color=C_HIGH)
    add(gb, fig, f"幕2-自环{v}", n=2)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit={(a, a) for a in A})
draw_graph(ax, nodes=A, loops=A)
badge(ax, "① 自反", "4 个自环补齐：〈1,1〉〈2,2〉〈3,3〉〈4,4〉")
stage(ax, "自反性成立：每个元素 a 都有 〈a,a〉∈R", color=C_OK)
add(gb, fig, "幕2-自反完成", n=6)

# ---- 幕三：补对称边 〈1,2〉〈2,1〉〈3,4〉〈4,3〉 ----
fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit={(a, a) for a in A} | {(1, 2), (2, 1)})
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2)])
badge(ax, "② 对称", "对称：〈a,b〉∈R 则 〈b,a〉∈R → 双向成对补边")
stage(ax, "f(1)=f(2)=x：〈1,2〉与〈2,1〉一并入 R", color=C_HIGH)
add(gb, fig, "幕3-边12", n=2)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)])
badge(ax, "② 对称", "同团点对双向连边，对称性成立")
stage(ax, "f(3)=f(4)=y：〈3,4〉与〈4,3〉一并入 R", color=C_HIGH)
add(gb, fig, "幕3-边34", n=2)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)])
badge(ax, "② 对称", "同团点对双向连边，对称性成立")
stage(ax, "R 补全：8 个序偶 = 4 个自环 + 4 个对称序偶", color=C_OK)
add(gb, fig, "幕3-对称完成", n=6)

# ---- 幕四：传递自动成立，无需补边 ----
fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)])
badge(ax, "③ 传递", "若 〈a,b〉、〈b,c〉∈R，则 f(a)=f(b)=f(c)")
stage(ax, "传递性还需要补边吗？")
add(gb, fig, "幕4-传递问", n=6)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)])
badge(ax, "③ 传递（自动成立）", "同团内 f 值全同，〈a,c〉本就在 R 中")
stage(ax, "同团任两点已互通 → 无需补任何新边", color=C_OK)
add(gb, fig, "幕4-传递结论", n=6)

# ---- 幕五：两团染色成等价类 [1]={1,2}、[3]={3,4} ----
fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)],
           fill={1: CLS_FACE[1], 2: CLS_FACE[2]}, classes=[1], cls_label=[1])
stage(ax, "[1] = {b | 〈1,b〉∈R} = {1,2}（1 所在的等价类）", color=C_HIGH)
add(gb, fig, "幕5-类1", n=3)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)],
           fill=CLS_FACE, classes=[1, 3], cls_label=[1, 3])
stage(ax, "[3] = {b | 〈3,b〉∈R} = {3,4}（3 所在的等价类）", color=C_HIGH)
add(gb, fig, "幕5-类3", n=3)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)],
           fill=CLS_FACE, classes=[1, 3], cls_label=[1, 3])
badge(ax, "等价类", "[1]={1,2}，[3]={3,4}", color=C_OK)
stage(ax, "[1]∩[3] = 空集 → 两团两两不交", color=C_OK)
add(gb, fig, "幕5-不交", n=6)

fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)],
           fill=CLS_FACE, classes=[1, 3], cls_label=[1, 3])
badge(ax, "等价类", "两两不交，并集 = A", color=C_OK)
stage(ax, "[1]∪[3] = {1,2,3,4} = A → 构成 A 的划分", color=C_OK)
add(gb, fig, "幕5-并集", n=6)

# ---- 尾帧：R 是 A 上的等价关系（自反+对称+传递），16 帧 = 8 秒 ----
fig, ax = frame(TITLE)
draw_panel(ax, nodes=A, lit=R_REL)
draw_graph(ax, nodes=A, loops=A, edges=[(1, 2), (3, 4)],
           fill=CLS_FACE, classes=[1, 3], cls_label=[1, 3])
badge(ax, "等价关系 ⇔ 划分", "{[1], [3]} 是 A 的一个划分", color=C_OK)
ax.text(2.5, 0.85, "R 是 A 上的等价关系（自反 + 对称 + 传递）",
        ha="center", va="center", fontsize=15, color=C_OK, fontweight="bold")
ax.text(2.5, 0.42, "2026.4 证明 2 评分结构：自反(1分)+对称(2分)+传递(3分)",
        ha="center", va="center", fontsize=12, color="#4a5568")
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
