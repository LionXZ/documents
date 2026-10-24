# -*- coding: utf-8 -*-
"""三集合文氏图区域染色 + 容斥原理 动图脚本。

数据来源：ANIM_SPEC 第 4 条与第 53 行锚定（自编教学数据，文档例题同步使用，数字不许改）：
某班 40 人；选 A 课 22、B 课 18、C 课 16；同时 A∧B 8、A∧C 9、B∧C 7；三门全选 4。
区域唯一口径（第 53 行验算）：仅A=9、仅B=7、仅C=4、恰AB=4、恰AC=5、恰BC=3、中心=4；
|A∪B∪C| = 22+18+16−8−9−7+4 = 36；三门都不选 = 40−36 = 4。
区域染色用 numpy 网格指示函数 + contourf 精确填充（venv 无 shapely）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import numpy as np

# 苹方 .ttc 集合字体加载不稳，显式改用 Arial Unicode MS（∧ 等符号齐全）
plt.rcParams["font.family"] = ["Arial Unicode MS"]
set_style()

OUT = os.path.join("09-计算机基础", "离散数学", "images", "02324-anim-venn.gif")

# ---------- 数据锚定与程序验算（与 SPEC 第 53 行逐项核对） ----------
NA, NB, NC = 22, 18, 16                 # 各单集人数
NAB, NAC, NBC, NABC = 8, 9, 7, 4        # 两两交集与三元交集
NTOTAL = 40
ONLY_A = NA - NAB - NAC + NABC          # 22−8−9+4
ONLY_B = NB - NAB - NBC + NABC          # 18−8−7+4
ONLY_C = NC - NAC - NBC + NABC          # 16−9−7+4
AB_ONLY, AC_ONLY, BC_ONLY = NAB - NABC, NAC - NABC, NBC - NABC
UNION = NA + NB + NC - NAB - NAC - NBC + NABC
NEITHER = NTOTAL - UNION
assert (ONLY_A, ONLY_B, ONLY_C) == (9, 7, 4), "单集区域与 SPEC 不符"
assert (AB_ONLY, AC_ONLY, BC_ONLY) == (4, 5, 3), "重叠区域与 SPEC 不符"
assert UNION == 36 and NEITHER == 4, "容斥结果与 SPEC 不符"

# ---------- 三圆几何与区域指示网格 ----------
CA, CB, CC = (2.95, 3.6), (4.25, 3.6), (3.6, 2.45)   # 三圆圆心
RAD = 1.45
_gx = np.linspace(0.0, 10.0, 500)
_gy = np.linspace(0.0, 5.68, 300)
X, Y = np.meshgrid(_gx, _gy)

def _inside(c):
    """网格点是否在圆 c 内。"""
    return (X - c[0]) ** 2 + (Y - c[1]) ** 2 <= RAD * RAD

_IA, _IB, _IC = _inside(CA), _inside(CB), _inside(CC)
MASK = {"onlyA": _IA & ~_IB & ~_IC, "onlyB": _IB & ~_IA & ~_IC,
        "onlyC": _IC & ~_IA & ~_IB, "ab": _IA & _IB & ~_IC,
        "ac": _IA & _IC & ~_IB, "bc": _IB & _IC & ~_IA,
        "ctr": _IA & _IB & _IC}
RCOL = {"onlyA": "#93c5fd", "onlyB": "#86efac", "onlyC": "#fcd34d",
        "ab": "#5eead4", "ac": "#c4b5fd", "bc": "#fda4af", "ctr": "#f87171"}
LPOS = {"onlyA": (2.05, 3.95), "onlyB": (5.15, 3.95), "onlyC": (3.6, 1.55),
        "ab": (3.6, 4.5), "ac": (2.8, 2.5), "bc": (4.4, 2.5),
        "ctr": (3.6, 3.12)}
VAL = {"onlyA": ONLY_A, "onlyB": ONLY_B, "onlyC": ONLY_C, "ab": AB_ONLY,
       "ac": AC_ONLY, "bc": BC_ONLY, "ctr": NABC}
# 染色顺序：先单集、减重叠、再加回中心（SPEC 指定）；算式与锚定一致
STEPS = [
    ("onlyA", f"仅选 A = {NA} − {NAB} − {NAC} + {NABC} = {ONLY_A}"
              "（先减各重叠，中心被减两次要加回）"),
    ("onlyB", f"仅选 B = {NB} − {NAB} − {NBC} + {NABC} = {ONLY_B}"),
    ("onlyC", f"仅选 C = {NC} − {NAC} − {NBC} + {NABC} = {ONLY_C}"),
    ("ab", f"恰 A∧B（不含 C）= {NAB} − {NABC} = {AB_ONLY}"),
    ("ac", f"恰 A∧C（不含 B）= {NAC} − {NABC} = {AC_ONLY}"),
    ("bc", f"恰 B∧C（不含 A）= {NBC} − {NABC} = {BC_ONLY}"),
    ("ctr", f"三门全选（中心）= {NABC}"),
]

# ---------- 绘制工具 ----------
def frame(title):
    """新画布。"""
    fig, ax = new_fig(title)
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.68)
    ax.axis("off")
    return fig, ax

def add(gb, fig, ctx, n=1):
    """QA 通过才入帧；有问题立即失败（必须修到 0 才能保存）。"""
    p = qa_figure(fig, ctx=ctx)
    assert p == 0, f"{ctx} QA 问题 {p} 个，禁止保存"
    gb.add(fig, n=n)

def draw_venn(ax, fills=(), nums=()):
    """三圆轮廓 + 已染色区域 + 区域数字。"""
    for k in fills:                     # 区域染色：网格指示函数精确填充
        ax.contourf(X, Y, MASK[k].astype(float), levels=[0.5, 1.5],
                    colors=[RCOL[k]], alpha=0.9, zorder=1)
    for c in (CA, CB, CC):              # 圆轮廓最后画，压在染色之上
        ax.add_patch(Circle(c, RAD, facecolor="none", edgecolor=C_MAIN,
                            lw=2.0, zorder=4))
    for x, y, s in [(2.0, 4.85, "A"), (5.2, 4.85, "B"), (3.6, 0.72, "C")]:
        ax.text(x, y, s, ha="center", va="center", fontsize=14,
                color=C_MAIN, fontweight="bold", zorder=5)
    for k in nums:                      # 区域数字（染过色的才标数）
        ax.text(LPOS[k][0], LPOS[k][1], str(VAL[k]), ha="center",
                va="center", fontsize=15, color="#1a202c",
                fontweight="bold", zorder=6)

def draw_panel(ax, neither=False):
    """右侧「已知」数据面板；neither=显示都不选结果。"""
    ax.add_patch(Rectangle((7.3, 0.95), 2.45, 4.35, facecolor="white",
                           edgecolor=C_DIM, lw=1.3, zorder=0))
    ax.text(8.52, 5.02, "已知", ha="center", va="center", fontsize=13.5,
            color="#2d3748", fontweight="bold", zorder=3)
    lines = [f"选 A 课 {NA} 人", f"选 B 课 {NB} 人", f"选 C 课 {NC} 人",
             f"A∧B {NAB} 人", f"A∧C {NAC} 人", f"B∧C {NBC} 人",
             f"三门全选 {NABC} 人", f"全班 {NTOTAL} 人"]
    for j, s in enumerate(lines):
        ax.text(8.52, 4.55 - j * 0.46, s, ha="center", va="center",
                fontsize=12, color="#4a5568", zorder=3)
    if neither:
        ax.text(8.52, 0.55, f"都不选 {NEITHER} 人", ha="center", va="center",
                fontsize=12.5, color=C_HIGH, fontweight="bold", zorder=3)

def note(ax, s, y=0.25, col="#4a5568", fs=13, bold=False):
    """底部说明行（文氏图下方居中）。"""
    ax.text(4.2, y, s, ha="center", va="center", fontsize=fs, color=col,
            fontweight="bold" if bold else "normal", zorder=6)

# ================= 帧序列 =================
TITLE = "三集合文氏图：区域染色 + 容斥原理"
gb = GifBuilder(fps=2)

# ---- ① 画三圆 + 已知条件（解释画面 3000ms） ----
fig, ax = frame(TITLE)
draw_venn(ax)
draw_panel(ax)
note(ax, "三个圆把平面分成 7 个互不重叠的区域，逐块染色标数")
add(gb, fig, "开场", n=6)

# ---- ② 逐区域染色并标数（染色 1500ms + 标数驻留 3000ms） ----
done_fill, done_num = [], []
for key, msg in STEPS:
    done_fill.append(key)
    fig, ax = frame(TITLE)
    draw_venn(ax, fills=done_fill)
    draw_panel(ax)
    note(ax, msg)
    add(gb, fig, f"染色-{key}", n=3)
    done_num.append(key)
    fig, ax = frame(TITLE)
    draw_venn(ax, fills=done_fill, nums=done_num)
    draw_panel(ax)
    note(ax, msg)
    add(gb, fig, f"标数-{key}", n=6)

# ---- ③ 容斥求和 |A∪B∪C|（解释画面 3000ms ×2） ----
fig, ax = frame(TITLE)
draw_venn(ax, fills=done_fill, nums=done_num)
draw_panel(ax)
note(ax, f"容斥：|A∪B∪C| = {NA}+{NB}+{NC} − {NAB}−{NAC}−{NBC} + {NABC}")
add(gb, fig, "容斥式", n=6)

fig, ax = frame(TITLE)
draw_venn(ax, fills=done_fill, nums=done_num)
draw_panel(ax)
note(ax, f"容斥：|A∪B∪C| = {NA}+{NB}+{NC} − {NAB}−{NAC}−{NBC} + {NABC}"
         f" = {UNION}", col=C_OK, bold=True)
add(gb, fig, "容斥结果", n=6)

# ---- ④ 三门都不选 = 40−36 = 4（解释画面 3000ms） ----
fig, ax = frame(TITLE)
draw_venn(ax, fills=done_fill, nums=done_num)
draw_panel(ax, neither=True)
note(ax, f"三门都不选 = {NTOTAL} − {UNION} = {NEITHER} 人",
     col=C_OK, bold=True)
add(gb, fig, "都不选", n=6)

# ---- 尾帧：全部数字 + 结论（8000ms） ----
fig, ax = frame(TITLE)
draw_venn(ax, fills=done_fill, nums=done_num)
draw_panel(ax, neither=True)
note(ax, f"至少选一门 {UNION} 人；三门都不选 = {NTOTAL} − {UNION} = "
         f"{NEITHER} 人", col=C_OK, bold=True)
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
