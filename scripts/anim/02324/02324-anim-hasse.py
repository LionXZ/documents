# -*- coding: utf-8 -*-
"""哈斯图逐层绘制 动图脚本。

数据来源：ANIM_SPEC 锚定（自编教学数据，文档例题同步使用）
    A={1,2,3,6,12}，「|」整除关系
覆盖关系（程序验算）：1≺2、1≺3、2≺6、3≺6、6≺12
不画的边（自环/传递边）：2|12、3|12、1|6、1|12
结论：极大元=12、极小元=1、最大元=12、最小元=1
尾帧：B={1,2,3,6} 的上界 6、12；上确界 6
注：苹方 .ttc 无法被 matplotlib 加载，显式改用 Arial Unicode MS。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

# 字体：苹方 .ttc 加载失败会退化 DejaVu（中文豆腐块），改用 Arial Unicode MS
plt.rcParams["font.family"] = ["Arial Unicode MS"]

# ---------- 数据锚定与程序验算 ----------
A = [1, 2, 3, 6, 12]
REL = {(a, b) for a in A for b in A if a != b and b % a == 0}   # 真整除对
COVER = {(a, b) for (a, b) in REL
         if not any(a != c != b and b % c == 0 and c % a == 0 for c in A)}
assert COVER == {(1, 2), (1, 3), (2, 6), (3, 6), (6, 12)}, "覆盖关系与 SPEC 不符"

# 哈斯图坐标：分层（等比数据坐标）
POS = {1: (7.2, 1.0), 2: (6.2, 2.2), 3: (8.2, 2.2),
       6: (7.2, 3.4), 12: (7.2, 4.6)}
OUT = "09-计算机基础/离散数学/images/02324-anim-hasse.gif"

def frame(title):
    """新画布：x 0-10，y 0-5.68（与像素等比）。"""
    fig, ax = new_fig(title)
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.68)
    ax.axis("off")
    return fig, ax

def add(gb, fig, ctx, n=1):
    """QA 通过才入帧。"""
    p = qa_figure(fig, ctx=ctx)
    assert p == 0, f"{ctx} QA 问题 {p} 个，禁止保存"
    gb.add(fig, n=n)

def draw_hasse(ax, nodes=(), edges=(), ring=(), fill=None, subset=()):
    """画哈斯图。nodes/edges 已出现的点与边；ring 加色环的点；
    fill dict{点:颜色}；subset 染黄子集 B 的点。"""
    fill = fill or {}
    for (a, b) in edges:
        (x1, y1), (x2, y2) = POS[a], POS[b]
        ax.plot([x1, x2], [y1 + 0.26, y2 - 0.26], color=C_MAIN, lw=2.2,
                zorder=1)
    for v in POS:
        if v not in nodes:
            continue
        x, y = POS[v]
        face = fill.get(v, "#dbeafe" if v not in subset else C_MARK)
        ax.add_patch(Circle((x, y), 0.26, facecolor=face,
                            edgecolor=C_MAIN, lw=1.6, zorder=3))
        ax.text(x, y, str(v), ha="center", va="center", fontsize=14,
                color="#1a365d", fontweight="bold", zorder=4)
    for v in ring:
        x, y = POS[v]
        ax.add_patch(Circle((x, y), 0.40, facecolor="none",
                            edgecolor=C_HIGH, lw=2.6, zorder=2))

# ---------- 左侧可比对列表 ----------
# 两列排布：(元素, y 行号)；划掉的传递边加红色删除线
PAIRS = [(1, 2, 0, 0), (1, 3, 0, 1), (1, 6, 0, 2), (1, 12, 0, 3),
         (2, 6, 0, 4), (2, 12, 1, 0), (3, 6, 1, 1), (3, 12, 1, 2),
         (6, 12, 1, 3)]
COL_X = [1.6, 3.5]          # 两列 x 中心
ROW_Y0, ROW_DY = 3.9, -0.45 # 首行 y 与行距

def draw_list(ax, cut=(), good=(), note=""):
    """画 9 对可比对；cut 中画删除线，good 中染绿。"""
    for (a, b, c, r) in PAIRS:
        x, y = COL_X[c], ROW_Y0 + r * ROW_DY
        s = f"{a}|{b}"
        if (a, b) in good:
            col = C_OK
        elif (a, b) in cut:
            col = C_DIM
        else:
            col = "#2d3748"
        t = ax.text(x, y, s, ha="center", va="center", fontsize=15, color=col)
        if (a, b) in cut:   # 删除线
            ax.plot([x - 0.32, x + 0.45], [y, y], color=C_HIGH, lw=2.0)
    if note:
        ax.text(2.5, 0.55, note, ha="center", va="center",
                fontsize=13, color="#4a5568")

gb = GifBuilder(fps=2)
TITLE = "哈斯图  A = {1,2,3,6,12}，整除关系 x | y"

# ---- 幕一 开场：列出全部可比对 ----
fig, ax = frame(TITLE)
draw_list(ax, note="可比对：y 是 x 的倍数且 x ≠ y")
ax.text(7.2, 5.0, "x|y 即 y 是 x 的倍数", ha="center", va="center",
        fontsize=14, color=C_MAIN)
add(gb, fig, "幕1-开场-9对", n=6)

fig, ax = frame(TITLE)
draw_list(ax, note="覆盖：x|y 且没有中间元 z（x|z 且 z|y）→ 哈斯图只画覆盖")
ax.text(7.2, 5.0, "哈斯图只画「覆盖」边", ha="center", va="center",
        fontsize=15, color=C_HIGH)
add(gb, fig, "幕1-覆盖定义", n=6)

# ---- 幕一 逐条划掉传递边（有中间元的可比对） ----
CUT_SEQ = [((1, 6), "1|6：有中间元 2（1|2 且 2|6）→ 传递边，不画"),
           ((2, 12), "2|12：有中间元 6（2|6 且 6|12）→ 传递边，不画"),
           ((1, 12), "1|12：有中间元 2、3、6 → 传递边，不画"),
           ((3, 12), "3|12：有中间元 6（3|6 且 6|12）→ 传递边，不画")]
done_cut = set()
for pair, note in CUT_SEQ:
    done_cut.add(pair)
    fig, ax = frame(TITLE)
    draw_list(ax, cut=done_cut, note=note)
    add(gb, fig, f"幕1-划掉{pair[0]}|{pair[1]}", n=2)

# ---- 幕一 结论：剩 5 条覆盖关系 ----
fig, ax = frame(TITLE)
draw_list(ax, cut=done_cut, good=COVER,
          note="覆盖关系 5 条：1≺2、1≺3、2≺6、3≺6、6≺12")
ax.text(7.2, 5.0, "得到覆盖关系", ha="center", va="center",
        fontsize=15, color=C_OK)
add(gb, fig, "幕1-覆盖结论", n=6)

# ---- 幕二 逐层画点：1 -> 2,3 -> 6 -> 12 ----
LAYERS = [([1], "底层：最小元 1"),
          ([1, 2, 3], "第二层：2、3（都只被 1 直接整除）"),
          ([1, 2, 3, 6], "第三层：6"),
          ([1, 2, 3, 6, 12], "顶层：12")]
for nodes, note in LAYERS:
    fig, ax = frame(TITLE)
    draw_list(ax, cut=done_cut, good=COVER)
    draw_hasse(ax, nodes=nodes)
    ax.text(7.2, 0.55, note, ha="center", va="center",
            fontsize=13, color=C_HIGH)
    add(gb, fig, f"幕2-画点{len(nodes)}", n=4)

fig, ax = frame(TITLE)
draw_list(ax, cut=done_cut, good=COVER)
draw_hasse(ax, nodes=A)
ax.text(7.2, 0.55, "按「高度」分层摆好 5 个点", ha="center", va="center",
        fontsize=13, color="#4a5568")
add(gb, fig, "幕2-五点完成", n=6)

# ---- 幕三 逐条连覆盖边 ----
COVER_SEQ = [(1, 2), (1, 3), (2, 6), (3, 6), (6, 12)]
edges = []
for e in COVER_SEQ:
    edges.append(e)
    fig, ax = frame(TITLE)
    draw_list(ax, cut=done_cut, good=COVER)
    draw_hasse(ax, nodes=A, edges=edges)
    ax.text(7.2, 0.55, f"连边 {e[0]} ≺ {e[1]}", ha="center", va="center",
            fontsize=13, color=C_MAIN)
    add(gb, fig, f"幕3-连边{e[0]}{e[1]}", n=2)

fig, ax = frame(TITLE)
draw_list(ax, cut=done_cut, good=COVER)
draw_hasse(ax, nodes=A, edges=COVER)
ax.text(7.2, 0.55, "自环与传递边（2|12、3|12、1|6、1|12）都不画",
        ha="center", va="center", fontsize=13, color="#4a5568")
add(gb, fig, "幕3-连边完成", n=6)

# ---- 幕四 标注极大/极小/最大/最小 ----
fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, ring=[12])
ax.text(7.2, 0.55, "极大元 = 12（没有更上方的元素）", ha="center",
        va="center", fontsize=13, color=C_HIGH)
add(gb, fig, "幕4-极大元", n=3)

fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, ring=[12, 1])
ax.text(7.2, 0.55, "极小元 = 1（没有更下方的元素）", ha="center",
        va="center", fontsize=13, color=C_HIGH)
add(gb, fig, "幕4-极小元", n=3)

fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, ring=[12, 1],
           fill={12: "#fde68a", 1: "#fde68a"})
ax.text(7.2, 0.55, "最大元 = 12（被所有元素整除）；最小元 = 1（整除所有元素）",
        ha="center", va="center", fontsize=13, color=C_OK)
add(gb, fig, "幕4-最大最小", n=6)

# ---- 幕五 子集 B={1,2,3,6} 的上界与上确界 ----
B = [1, 2, 3, 6]
fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, subset=B)
ax.text(7.2, 0.55, "取子集 B = {1,2,3,6}（黄色点）", ha="center",
        va="center", fontsize=13, color="#975a16")
add(gb, fig, "幕5-B染色", n=3)

fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, subset=B, ring=[6, 12])
ax.text(7.2, 0.55, "上界：6、12（B 中所有元素都整除它）", ha="center",
        va="center", fontsize=13, color=C_HIGH)
add(gb, fig, "幕5-上界", n=3)

fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, subset=B, ring=[12],
           fill={6: "#c6f6d5"})
ax.add_patch(Circle(POS[6], 0.40, facecolor="none", edgecolor=C_OK,
                    lw=3.0, zorder=2))
ax.text(7.2, 0.55, "上界中最小的 → 上确界 = 6（最小上界）", ha="center",
        va="center", fontsize=13, color=C_OK)
add(gb, fig, "幕5-上确界", n=6)

# ---- 尾帧：完整哈斯图总复习（16 帧 = 8 秒） ----
fig, ax = frame(TITLE)
draw_hasse(ax, nodes=A, edges=COVER, fill={12: "#fde68a", 1: "#fde68a"})
ax.text(7.2, 0.66, "覆盖边 5 条：1≺2、1≺3、2≺6、3≺6、6≺12",
        ha="center", va="center", fontsize=13, color=C_OK)
ax.text(7.2, 0.22, "极大元 = 最大元 = 12；极小元 = 最小元 = 1",
        ha="center", va="center", fontsize=13, color=C_OK)
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
