# -*- coding: utf-8 -*-
"""群运算表验证（Z6 模 6 加法）动图脚本。
数据来源：自编教学数据，与文档例题同步（ANIM_SPEC 锚定）
    ⟨Z6, ⊕6⟩：Z6 = {0,1,2,3,4,5}，a⊕b = (a+b) mod 6
    动画：6×6 运算表逐行填充 → 封闭 → 幺元 0 → 对角线对称=交换律
          → 每行 0~5 各一次=每元有逆（0↔0、1↔5、2↔4、3↔3）
    结论：Z6 是交换群；|1|=6、|2|=3、|3|=2；结合律由「模 m 加法」定理保证
    关联真题：2026.4 单选「10 阶循环群 a⁴ 的阶 = 10/gcd(10,4) = 5」
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
set_style()
from matplotlib.patches import Rectangle

# ---------- 数据锚定（程序验算，与群论事实不符则拒绝运行） ----------
T = [[(i + j) % 6 for j in range(6)] for i in range(6)]
assert all(T[0][j] == j for j in range(6)), "幺元行验证失败"      # 0 行 = 表头
assert all(T[i][0] == i for i in range(6)), "幺元列验证失败"      # 0 列 = 表头
assert all(T[i][j] == T[j][i] for i in range(6) for j in range(6)), "交换律验证失败"
assert all(sorted(row) == list(range(6)) for row in T), "每行应含 0~5 各一次"
INV = {v: T[v].index(0) for v in range(6)}                       # 逆元 = 行内值为 0 的列
assert INV == {0: 0, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}, "逆元表验证失败"
ORD = {v: 1 + T[v].index(v) for v in range(6)}                   # 阶 = 首次回到 v 的步数
assert ORD[1] == 6 and ORD[2] == 3 and ORD[3] == 2, "元素阶验证失败"

OUT = "09-计算机基础/离散数学/images/02324-anim-grouptable.gif"

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

# ---------- 表格几何 ----------
CELL = 0.58                     # 数据格边长（数据单位）
X0, YTOP = 1.25, 4.72           # 数据区左上角（表头列在 X0 左侧 0.6）
HX, HY = X0 - 0.30, YTOP + 0.30 # 表头列/行的中心线偏移

def cell_xy(i, j):
    """第 i 行第 j 列格子的左下坐标（0 起，行向下增长）。"""
    return X0 + j * CELL, YTOP - (i + 1) * CELL

def draw_table(ax, upto=0, cur=None, marks=None, hi_rows=(), hi_cols=(),
               calc=None):
    """画 6×6 运算表。upto=已填满的行数；cur=(i,j) 正在填的格(红)；
    marks={(i,j):颜色} 额外高亮格；hi_rows/hi_cols=黄色高亮行/列；
    calc=(i,j) 显示计算式的格子。"""
    marks = marks or {}
    for j in range(6):          # 列表头
        x, _ = cell_xy(0, j)
        ax.text(x + CELL / 2, HY, str(j), ha="center", va="center",
                fontsize=14, color="#2d3748", fontweight="bold")
    for i in range(6):          # 行表头
        _, y = cell_xy(i, 0)
        ax.text(HX, y + CELL / 2, str(i), ha="center", va="center",
                fontsize=14, color="#2d3748", fontweight="bold")
    ax.text(HX, HY, "⊕₆", ha="center", va="center",
            fontsize=13, color=C_MAIN, fontweight="bold")
    for i in range(6):
        for j in range(6):
            x, y = cell_xy(i, j)
            face, tc, fw = "#ffffff", "#718096", "normal"
            if i < upto:                       # 已填行：蓝字
                face, tc, fw = "#ffffff", C_MAIN, "bold"
            if (i, j) in marks:                # 指定高亮格
                face, tc, fw = marks[(i, j)], "#2d3748", "bold"
            if hi_cols and i < upto and j in hi_cols:
                face = C_MARK
            if i in hi_rows:
                face = C_MARK
            if cur == (i, j):
                face, tc, fw = "#fee2e2", C_HIGH, "bold"
            ax.add_patch(Rectangle((x, y), CELL, CELL, facecolor=face,
                                   edgecolor=C_DIM, lw=1.2))
            ax.text(x + CELL / 2, y + CELL / 2, str(T[i][j]),
                    ha="center", va="center", fontsize=13, color=tc,
                    fontweight=fw)
            if calc == (i, j):                 # 该格旁标注计算式
                ax.text(x + CELL / 2, y - 0.42, f"({i}+{j}) mod 6 = {T[i][j]}",
                        ha="center", va="center", fontsize=12.5, color=C_HIGH)

PANEL_X = 7.75                 # 右侧说明面板中心 x

def panel(ax, title, lines, color="#2d3748"):
    """右侧说明面板：标题 + 若干行 (文字, 颜色, 是否加粗)。"""
    ax.text(PANEL_X, 4.8, title, ha="center", va="center",
            fontsize=15, color=color, fontweight="bold")
    y = 4.15
    for s, c, bold in lines:
        ax.text(PANEL_X, y, s, ha="center", va="center", fontsize=13.5,
                color=c, fontweight="bold" if bold else "normal")
        y -= 0.55

TITLE = "⟨Z6, ⊕6⟩ 模 6 加法运算表：一张表验证群的性质"
gb = GifBuilder(fps=2)

# ---- 帧 1：开场，介绍 Z6 与模 6 加法 ----
fig, ax = frame(TITLE)
draw_table(ax)
panel(ax, "运算对象", [("Z6 = {0, 1, 2, 3, 4, 5}", C_MAIN, True),
                       ("", "#2d3748", False),
                       ("运算规则：a ⊕ b = (a + b) mod 6", "#2d3748", False),
                       ("超过 5 就减去 6（模 6）", "#4a5568", False)])
add(gb, fig, "开场", n=6)

# ---- 帧 2：表头出现 ----
fig, ax = frame(TITLE)
draw_table(ax, upto=0)
panel(ax, "第一步：先标表头", [("行表头、列表头都是 0~5", "#2d3748", False),
                               ("表中第 i 行第 j 列 = i ⊕ j", C_MAIN, True)])
add(gb, fig, "表头", n=6)

# ---- 帧 3：逐行填表（第 0 行示范算法并解释，其余行快速填） ----
NOTE0 = [("示范：第 0 行 = 0 ⊕ j = j", C_HIGH, True),
         ("例：0 ⊕ 3 = (0+3) mod 6 = 3", "#2d3748", False),
         ("第 0 行恰与列表头一致", C_OK, True)]
NOTE1 = [("第 1 行：1 ⊕ 5 = (1+5) mod 6 = 0", "#2d3748", False),
         ("加到 6 就绕回 0（模 6 的意义）", "#4a5568", False)]
for i in range(6):
    fig, ax = frame(TITLE)                       # 行高亮帧
    draw_table(ax, upto=i, hi_rows=(i,))
    panel(ax, f"开始填第 {i} 行", [(f"行头 {i}：计算 {i} ⊕ 0 ~ {i} ⊕ 5",
                                    "#2d3748", False)])
    add(gb, fig, f"行{i}-开始", n=2)
    for j in range(6):                           # 逐格填
        fig, ax = frame(TITLE)
        draw_table(ax, upto=i, cur=(i, j))
        panel(ax, f"填第 {i} 行", [(f"{i} ⊕ {j} = ({i}+{j}) mod 6 = {T[i][j]}",
                                    C_HIGH, True)])
        add(gb, fig, f"格({i},{j})", n=1)
    fig, ax = frame(TITLE)                       # 行完成帧
    draw_table(ax, upto=i + 1)
    note = NOTE0 if i == 0 else (NOTE1 if i == 1 else
                                 [(f"第 {i} 行 = 表头行循环左移 {i} 位",
                                   "#2d3748", False)])
    panel(ax, f"第 {i} 行完成", note)
    add(gb, fig, f"行{i}-完成", n=6 if i <= 1 else 3)

# ---- 帧 4：封闭性验证 ----
fig, ax = frame(TITLE)
draw_table(ax, upto=6, marks={(i, j): "#e6ffed" for i in range(6) for j in range(6)})
panel(ax, "性质 1：封闭性", [("表内出现的数只有 0~5", C_OK, True),
                             ("没有跑出 Z6 的新元素", "#2d3748", False),
                             ("⇒ Z6 对 ⊕6 封闭", C_OK, True)])
add(gb, fig, "封闭", n=6)

# ---- 帧 5：幺元验证（0 行 0 列与表头一致） ----
marks0 = {(0, j): "#fefcbf" for j in range(6)}
marks0.update({(i, 0): "#fefcbf" for i in range(6)})
fig, ax = frame(TITLE)
draw_table(ax, upto=6, marks=marks0)
panel(ax, "性质 2：幺元", [("第 0 行、第 0 列与表头完全一致", "#2d3748", False),
                           ("即 0 ⊕ b = b ⊕ 0 = b 恒成立", "#2d3748", False),
                           ("⇒ 幺元 e = 0", C_OK, True)])
add(gb, fig, "幺元", n=6)

# ---- 帧 6：交换律验证（对角线对称） ----
marksx = {(1, 2): "#bee3f8", (2, 1): "#bee3f8",
          (1, 5): "#bee3f8", (5, 1): "#bee3f8",
          (2, 4): "#bee3f8", (4, 2): "#bee3f8"}
fig, ax = frame(TITLE)
draw_table(ax, upto=6, marks=marksx)
panel(ax, "性质 3：交换律", [("蓝色对称格：T[i][j] = T[j][i]", "#2d3748", False),
                             ("全表关于主对角线对称", C_OK, True),
                             ("⇒ a ⊕ b = b ⊕ a 恒成立", C_OK, True)])
add(gb, fig, "交换律", n=6)

# ---- 帧 7：逆元验证（每行 0~5 各一次） ----
marksz = {(i, T[i].index(0)): "#bee3f8" for i in range(6)}
fig, ax = frame(TITLE)
draw_table(ax, upto=6, marks=marksz)
panel(ax, "性质 4：逆元", [("每行 0~5 恰出现一次（含 0）", "#2d3748", False),
                           ("蓝色格 = 该行值为 0 的格", C_MAIN, True),
                           ("0↔0、1↔5、2↔4、3↔3 互为逆元", C_OK, True),
                           ("⇒ 每个元素都有逆元", C_OK, True)])
add(gb, fig, "逆元", n=6)
