# -*- coding: utf-8 -*-
"""关系矩阵复合与传递闭包 + Warshall 算法 动图脚本。

数据来源：2025.10 简答题真题原题
    A={1,2,3}，R={〈1,1〉,〈1,3〉,〈2,2〉,〈3,2〉}
幕一：M(R) -> 布尔乘得 M(R²) -> M(R³) -> 三者取并得 t(R)
幕二：Warshall 算法逐个插入中间点 k=1,2,3，结果与幕一一致
数据锚定（ANIM_SPEC）：R² = R³ = t(R) = {〈1,1〉,〈1,2〉,〈1,3〉,〈2,2〉,〈3,2〉}
注：苹方缺 〈 用 U+3008/3009 替代数学角括号，字形视觉一致。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib.pyplot as plt
# 苹方 .ttc 集合字体 matplotlib 加载失败会退化到 DejaVu（中文豆腐块），
# 故显式改用单文件 ttf 的 Arial Unicode MS（中文、〈〉、数学符号齐全）
plt.rcParams["font.family"] = ["Arial Unicode MS"]

# ---------- 数据锚定与程序验算（与 SPEC 不符则拒绝运行） ----------
R = {(1, 1), (1, 3), (2, 2), (3, 2)}          # 2025.10 真题关系
N = [1, 2, 3]                                  # 元素全集

def comp(p, q):
    """关系布尔复合。"""
    return {(a, d) for (a, b) in p for (c, d) in q if b == c}

R2 = comp(R, R)
R3 = comp(R2, R)
TR = R | R2 | R3
SPEC = {(1, 1), (1, 2), (1, 3), (2, 2), (3, 2)}
assert R2 == SPEC and R3 == SPEC and TR == SPEC, "数据与 SPEC 不符"

def mat(rel):
    """关系 -> 3x3 0-1 矩阵（行=第一元素，列=第二元素）。"""
    return [[1 if (i, j) in rel else 0 for j in N] for i in N]

MR, M2, M3 = mat(R), mat(R2), mat(R3)

# Warshall 迭代序列：Wk[k] 为插入中间点 1..k 后的矩阵（列表按幕二使用）
def warshall_steps():
    steps = [mat(R)]
    for k in (1, 2, 3):
        w = {(i, j) for i in N for j in N if steps[-1][i - 1][j - 1] == 1}
        w |= {(i, j) for (i, a) in w for (b, j) in w if a == k and b == k}
        steps.append(mat(w))
    return steps

WS = warshall_steps()
assert WS[3] == mat(SPEC), "Warshall 结果与 SPEC 不符"

# 相对路径定位：工作目录必须为仓库根
OUT = "09-计算机基础/离散数学/images/02324-anim-relcomp.gif"

# ---------- 矩阵绘制 ----------
CELL = 0.8          # 格子边长（数据单位）

def draw_matrix(ax, x0, y0, m, title, hl_row=None, hl_col=None,
                new_cells=None, done_cells=None):
    """画一个 3x3 关系矩阵。x0,y0 = 左下角格子的左下坐标。
    hl_row/hl_col：黄色高亮的行/列（0 起）；new_cells：红色新填格；
    done_cells：绿色已确认格。返回无。"""
    new_cells = new_cells or set()
    done_cells = done_cells or set()
    # 浅色背板：圈住行标签 + 矩阵本体，标明归属
    ax.add_patch(Rectangle((x0 - 0.62, y0 - 0.15), CELL * 3 + 0.74,
                           CELL * 3 + 0.30, facecolor="#f5efe0",
                           edgecolor="none", zorder=0))
    for i in range(3):
        for j in range(3):
            cx, cy = x0 + j * CELL, y0 + (2 - i) * CELL   # i 行在上
            face, edge, tc = "#ffffff", C_DIM, C_DIM
            if m[i][j] == 1:
                face, tc = "#dbeafe", C_MAIN
            if (i, j) in done_cells:
                face, edge, tc = "#dcfce7", C_OK, C_OK
            if (i, j) in new_cells:
                face, edge, tc = "#fee2e2", C_HIGH, C_HIGH
            if hl_row == i:
                face = C_MARK if m[i][j] == 0 else "#fde68a"
            if hl_col == j:
                face = C_MARK if m[i][j] == 0 else "#fde68a"
            ax.add_patch(Rectangle((cx, cy), CELL, CELL,
                                   facecolor=face, edgecolor=edge, lw=1.4))
            ax.text(cx + CELL / 2, cy + CELL / 2, str(m[i][j]),
                    ha="center", va="center", fontsize=15,
                    color=tc, fontweight="bold")
    # 行标签：与第一位数字（第一列格心）水平间距 0.8 数据单位
    for i in range(3):
        ax.text(x0 + CELL / 2 - 0.8, y0 + (2 - i) * CELL + CELL / 2,
                str(N[i]), ha="center", va="center",
                fontsize=14, color="#4a5568")
    # 列标签：与第一行数字格心垂直间距 0.8 数据单位
    for j in range(3):
        ax.text(x0 + j * CELL + CELL / 2, y0 + 2 * CELL + CELL / 2 + 0.8,
                str(N[j]), ha="center", va="center",
                fontsize=14, color="#4a5568")
    # 矩阵标题（M(R) 等），再往上一层
    ax.text(x0 + 1.5 * CELL, y0 + 2 * CELL + CELL / 2 + 1.45,
            title, ha="center", va="center",
            fontsize=15, color="#2d3748", fontweight="bold")


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

# 三矩阵横向布局（左下角 x）：0.60 / 3.75 / 6.90，间距含行标签
X1, X2, X3, Y0 = 0.55, 3.95, 7.35, 0.95

gb = GifBuilder(fps=2)

# ---- 幕一 开场：介绍 R 与其关系矩阵 ----
fig, ax = frame("幕一  传递闭包 t(R) = R ∪ R² ∪ R³（2025.10 真题）")
draw_matrix(ax, X1, Y0, MR, "M(R)")
ax.text(7.4, 3.9, "A = {1, 2, 3}", ha="center", va="center", fontsize=14)
ax.text(7.4, 3.2, "R = {〈1,1〉, 〈1,3〉,\n 〈2,2〉, 〈3,2〉}",
        ha="center", va="center", fontsize=14, color=C_MAIN)
ax.text(7.4, 1.9, "行 = 第一元素\n列 = 第二元素", ha="center",
        va="center", fontsize=13, color="#4a5568")
add(gb, fig, "幕1-开场", n=6)

# ---- 幕一 说明：先布尔乘求 R² ----
fig, ax = frame("幕一  传递闭包 t(R) = R ∪ R² ∪ R³（2025.10 真题）")
draw_matrix(ax, X1, Y0, MR, "M(R)")
ax.text(5.9, 3.4, "布尔乘：M(R²) = M(R) ⊙ M(R)", ha="center",
        va="center", fontsize=15, color=C_HIGH)
ax.text(5.9, 2.5, "规则：M²[i,j] = 任取中转 k，\nM[i,k]=1 且 M[k,j]=1 则记 1",
        ha="center", va="center", fontsize=13, color="#4a5568")
add(gb, fig, "幕1-说明布尔乘", n=6)

# ---- 幕一 逐行布尔乘填出 M(R²) ----
# 每行：高亮 M(R) 该行(2帧) -> 逐格填 R²(每格2帧) -> 行解释文字(6帧)
ROW_NOTE = {0: "行 1：1→1 走到 {1,3}，1→3 走到 {2} ⇒ 到达 {1,2,3}",
            1: "行 2：2→2 走到 {2} ⇒ 到达 {2}",
            2: "行 3：3→2 走到 {2} ⇒ 到达 {2}"}
for i in range(3):
    fig, ax = frame("幕一  逐行布尔乘求 M(R²)")
    draw_matrix(ax, X1, Y0, MR, "M(R)", hl_row=i)
    draw_matrix(ax, X2, Y0, M2, "M(R²)")
    ax.text(3.5, 3.6, "⊙", ha="center", va="center", fontsize=22, color=C_HIGH)
    add(gb, fig, f"R2-行{i+1}-高亮", n=2)
    filled = set()
    for j in range(3):
        filled.add((i, j))
        fig, ax = frame("幕一  逐行布尔乘求 M(R²)")
        draw_matrix(ax, X1, Y0, MR, "M(R)", hl_row=i)
        draw_matrix(ax, X2, Y0, M2, "M(R²)", new_cells=filled)
        ax.text(3.5, 3.6, "⊙", ha="center", va="center",
                fontsize=22, color=C_HIGH)
        add(gb, fig, f"R2-行{i+1}-填({i+1},{j+1})", n=2)
    fig, ax = frame("幕一  逐行布尔乘求 M(R²)")
    draw_matrix(ax, X1, Y0, MR, "M(R)")
    draw_matrix(ax, X2, Y0, M2, "M(R²)", done_cells={(a, b) for a in (0, 1, 2) for b in (0, 1, 2) if M2[a][b] == 1})
    ax.text(5.5, 0.45, ROW_NOTE[i], ha="center", va="center",
            fontsize=13, color=C_OK)
    add(gb, fig, f"R2-行{i+1}-解释", n=6)

# ---- 幕一 R² 小结，再乘一次得 R³ ----
fig, ax = frame("幕一  M(R²) 完成")
draw_matrix(ax, X1, Y0, MR, "M(R)")
draw_matrix(ax, X2, Y0, M2, "M(R²)", done_cells={(a, b) for a in (0, 1, 2) for b in (0, 1, 2) if M2[a][b] == 1})
ax.text(5.5, 0.45, "R² = {〈1,1〉, 〈1,2〉, 〈1,3〉, 〈2,2〉, 〈3,2〉}",
        ha="center", va="center", fontsize=14, color=C_OK)
add(gb, fig, "R2-小结", n=6)

# R³ = M(R²) ⊙ M(R)：三行高亮扫过（各 2 帧），矩阵内容与 R² 相同
for i in range(3):
    fig, ax = frame("幕一  再布尔乘一次求 M(R³)")
    draw_matrix(ax, X2, Y0, M2, "M(R²)", hl_row=i)
    draw_matrix(ax, X3, Y0, M3, "M(R³)")
    ax.text(6.65, 3.6, "⊙", ha="center", va="center", fontsize=22, color=C_HIGH)
    add(gb, fig, f"R3-行{i+1}", n=2)

fig, ax = frame("幕一  R³ 已稳定")
draw_matrix(ax, X1, Y0, MR, "M(R)")
draw_matrix(ax, X2, Y0, M2, "M(R²)")
draw_matrix(ax, X3, Y0, M3, "M(R³)")
ax.text(5.5, 0.45, "M(R³) = M(R²)：矩阵不再变化，闭包已稳定",
        ha="center", va="center", fontsize=14, color=C_HIGH)
add(gb, fig, "R3-结论", n=6)

# ---- 幕一 尾帧：三矩阵取并 = t(R) ----
for r in range(3):    # 逐行扫高亮：三矩阵同行合并（每行 2 帧）
    fig, ax = frame("幕一  三矩阵取并得传递闭包")
    draw_matrix(ax, X1, Y0, MR, "M(R)", hl_row=r)
    draw_matrix(ax, X2, Y0, M2, "M(R²)", hl_row=r)
    draw_matrix(ax, X3, Y0, M3, "M(R³)", hl_row=r)
    ax.text(6.65, 3.6, "∪", ha="center", va="center", fontsize=22, color=C_OK)
    add(gb, fig, f"tR-并-行{r+1}", n=2)

fig, ax = frame("幕一  传递闭包结果（结论）")
draw_matrix(ax, X1, Y0, MR, "M(R)")
draw_matrix(ax, X2, Y0, M2, "M(R²)")
draw_matrix(ax, X3, Y0, M3, "M(R³)")
ax.text(6.65, 3.6, "∪", ha="center", va="center", fontsize=22, color=C_OK)
ax.text(5.5, 0.42, "t(R) = R ∪ R² ∪ R³", ha="center", va="center",
        fontsize=15, color=C_OK, fontweight="bold")
ax.text(5.5, 0.02, "t(R) = {〈1,1〉, 〈1,2〉, 〈1,3〉, 〈2,2〉, 〈3,2〉}",
        ha="center", va="center", fontsize=14, color=C_OK)
add(gb, fig, "幕1-尾帧", n=16)

# ================= 幕二：Warshall 算法 =================
WX, WY = 4.0, 0.95          # 幕二矩阵左下角（居中）

# ---- 幕二 开场 ----
fig, ax = frame("幕二  Warshall 算法：插入中间点求闭包")
draw_matrix(ax, WX, WY, WS[0], "M(W)")
ax.text(7.9, 3.6, "初始 M(W) = M(R)", ha="center", va="center", fontsize=14)
ax.text(7.9, 2.7, "依次允许经过中转点\nk = 1, 2, 3", ha="center",
        va="center", fontsize=14, color=C_HIGH)
ax.text(7.9, 1.5, "若 W[i,k]=1 且 W[k,j]=1\n则 W[i,j] 记 1",
        ha="center", va="center", fontsize=13, color="#4a5568")
add(gb, fig, "幕2-开场", n=6)

# ---- k=1、k=2：均无新增路径 ----
K_NOTE = {1: "k=1：中转 1 的组合 i→1→j 已都有路径 → 矩阵不变",
          2: "k=2：中转 2 无新组合 → 矩阵不变"}
for k in (1, 2):
    fig, ax = frame(f"幕二  插入中转点 k = {k}")
    draw_matrix(ax, WX, WY, WS[k - 1], "M(W)", hl_row=k - 1, hl_col=k - 1)
    ax.text(2.0, 3.6, f"k = {k}", ha="center", va="center",
            fontsize=20, color=C_HIGH, fontweight="bold")
    ax.text(2.0, 2.6, f"检查第 {k} 行\n与第 {k} 列", ha="center",
            va="center", fontsize=13, color="#4a5568")
    add(gb, fig, f"幕2-k{k}-高亮", n=3)
    fig, ax = frame(f"幕二  插入中转点 k = {k}")
    draw_matrix(ax, WX, WY, WS[k], "M(W)")
    ax.text(2.0, 3.6, f"k = {k}", ha="center", va="center",
            fontsize=20, color=C_HIGH, fontweight="bold")
    ax.text(5.0, 0.45, K_NOTE[k], ha="center", va="center",
            fontsize=12, color=C_OK)
    add(gb, fig, f"幕2-k{k}-不变", n=6)

# ---- k=3：发现新路径 1→3→2，新增 W[1,2] ----
fig, ax = frame("幕二  插入中转点 k = 3")
draw_matrix(ax, WX, WY, WS[2], "M(W)", hl_row=2, hl_col=2)
ax.text(2.0, 3.6, "k = 3", ha="center", va="center",
        fontsize=20, color=C_HIGH, fontweight="bold")
ax.text(2.0, 2.6, "检查第 3 行\n与第 3 列", ha="center", va="center",
        fontsize=13, color="#4a5568")
add(gb, fig, "幕2-k3-高亮", n=3)

# 考察 W[1,3] 与 W[3,2]（红框标出）
fig, ax = frame("幕二  k=3：发现新路径")
draw_matrix(ax, WX, WY, WS[2], "M(W)",
            new_cells={(0, 2), (2, 1)})
ax.text(2.0, 3.6, "k = 3", ha="center", va="center",
        fontsize=20, color=C_HIGH, fontweight="bold")
ax.text(2.0, 2.6, "W[1,3]=1 且 W[3,2]=1\n⇒ 1→3→2 可达", ha="center",
        va="center", fontsize=13, color=C_HIGH)
add(gb, fig, "幕2-k3-考察", n=3)

# 新增 W[1,2]=1（绿格）
fig, ax = frame("幕二  k=3：填入新路径")
draw_matrix(ax, WX, WY, WS[3], "M(W)", done_cells={(0, 1)})
ax.text(2.0, 3.6, "k = 3", ha="center", va="center",
        fontsize=20, color=C_HIGH, fontweight="bold")
ax.text(2.0, 2.6, "新增 〈1,2〉\nW[1,2] = 1", ha="center", va="center",
        fontsize=13, color=C_OK)
add(gb, fig, "幕2-k3-新增", n=3)

# ---- 幕二 尾帧：与幕一结果一致 ----
fig, ax = frame("幕二  Warshall 结果（结论）")
draw_matrix(ax, WX, WY, WS[3], "M(W)", done_cells={(a, b) for a in (0, 1, 2) for b in (0, 1, 2) if WS[3][a][b] == 1})
ax.text(5.0, 0.45, "Warshall 最终矩阵 = t(R) = {〈1,1〉, 〈1,2〉, 〈1,3〉, 〈2,2〉, 〈3,2〉}",
        ha="center", va="center", fontsize=14, color=C_OK)
ax.text(5.0, 0.05, "与幕一「取并法」结果完全一致", ha="center", va="center",
        fontsize=13, color=C_OK)
add(gb, fig, "幕2-尾帧", n=16)

# ---------- 保存 ----------
ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
