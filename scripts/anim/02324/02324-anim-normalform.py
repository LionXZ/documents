# -*- coding: utf-8 -*-
"""(P∧Q)∨¬R 主析取范式展开 动图脚本。

数据来源：2024.10 简答题真题同款公式（ANIM_SPEC 第 2 条锚定，与真值表动图联动，数字不许改）。
成真赋值 5 个（000、010、100、110、111）→ 对应极小项
¬P∧¬Q∧¬R、¬P∧Q∧¬R、P∧¬Q∧¬R、P∧Q∧¬R、P∧Q∧R → 编码 m0∨m2∨m4∨m6∨m7。
节奏：等效驻留制——解释画面单帧 3000ms、动作子帧 1000~1500ms、尾帧 8000ms。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 苹方 .ttc 集合字体加载不稳，显式改用 Arial Unicode MS（∧∨¬ 等符号齐全）
plt.rcParams["font.family"] = ["Arial Unicode MS"]
set_style()

OUT = os.path.join("09-计算机基础", "离散数学", "images", "02324-anim-normalform.gif")

# ---------- 数据锚定与程序验算 ----------
ALL = [(p, q, r) for p in (0, 1) for q in (0, 1) for r in (0, 1)]   # 000→111
TRUE = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]      # 成真赋值

def minterm(p, q, r):
    """极小项：赋值 0 写 ¬，1 写原变量（程序生成，防手误）。"""
    return "∧".join([("¬P", "P")[p], ("¬Q", "Q")[q], ("¬R", "R")[r]])

def code(t):
    """极小项编码 m 下标 = 二进制赋值。"""
    return f"m{t[0]*4 + t[1]*2 + t[2]}"

assert [code(t) for t in TRUE] == ["m0", "m2", "m4", "m6", "m7"], "编码与 SPEC 不符"
assert [minterm(*t) for t in TRUE] == ["¬P∧¬Q∧¬R", "¬P∧Q∧¬R", "P∧¬Q∧¬R",
                                       "P∧Q∧¬R", "P∧Q∧R"], "极小项与 SPEC 不符"

# ---------- 布局 ----------
RY0, RDY = 4.85, 0.52            # 首行 y 与行距（8 行到 y=1.21）
XA, XARR, XM, XC = 1.15, 2.3, 4.75, 6.95   # 赋值 / 箭头 / 极小项 / 编码 的列位置

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

def note(ax, s, y=0.62, col="#4a5568", fs=13, bold=False):
    """底部说明行。"""
    ax.text(5.0, y, s, ha="center", va="center", fontsize=fs, color=col,
            fontweight="bold" if bold else "normal")

def draw_rows(ax, marked=False, m_done=0):
    """左侧 8 行赋值。marked=是否已标成真（绿）；m_done=已写出极小项的行数
    （按 TRUE 顺序计）。"""
    for i, t in enumerate(ALL):
        y = RY0 - i * RDY
        istrue = t in TRUE
        col = C_DIM if not marked else (C_OK if istrue else "#cbd5e0")
        ax.text(XA, y, f"{t[0]}{t[1]}{t[2]}", ha="center", va="center",
                fontsize=14, color=col,
                fontweight="bold" if marked and istrue else "normal")
        if istrue and TRUE.index(t) < m_done:      # 该成真行已写出极小项
            ax.text(XARR, y, "→", ha="center", va="center", fontsize=13,
                    color=C_HIGH)
            ax.text(XM, y, minterm(*t), ha="center", va="center",
                    fontsize=14, color="#1a202c")
            ax.text(XC, y, code(t), ha="center", va="center", fontsize=13,
                    color=C_HIGH, fontweight="bold")

def draw_rule(ax):
    """右侧规则面板。"""
    ax.text(8.55, 3.85, "极小项规则", ha="center", va="center", fontsize=13,
            color=C_MAIN, fontweight="bold")
    ax.text(8.55, 3.35, "赋值 0 → 写 ¬", ha="center", va="center",
            fontsize=12.5, color="#4a5568")
    ax.text(8.55, 2.9, "赋值 1 → 写原变量", ha="center", va="center",
            fontsize=12.5, color="#4a5568")

# ================= 帧序列 =================
TITLE = "主析取范式：由成真赋值写极小项（(P∧Q)∨¬R）"
gb = GifBuilder(fps=2)

# ---- ① 列出 8 个赋值（解释画面 3000ms） ----
fig, ax = frame(TITLE)
draw_rows(ax)
note(ax, "把每个成真赋值改写成一个极小项，再把它们全部 ∨ 起来")
add(gb, fig, "开场-8赋值", n=6)

# ---- ② 标出 5 个成真赋值（解释画面 3000ms） ----
fig, ax = frame(TITLE)
draw_rows(ax, marked=True)
draw_rule(ax)
note(ax, "5 个成真赋值（绿色）：000、010、100、110、111")
add(gb, fig, "标成真", n=6)

# ---- ③ 逐个写出极小项（每个出现后驻留 3000ms） ----
HINT = ["全 0 → 全写 ¬", "Q=1 写原变量，P、R 写 ¬", "P=1 写原变量",
        "P、Q 写原变量", "全 1 写原变量"]
for k, t in enumerate(TRUE):
    fig, ax = frame(TITLE)
    draw_rows(ax, marked=True, m_done=k + 1)
    draw_rule(ax)
    note(ax, f"{t[0]}{t[1]}{t[2]}：{HINT[k]} → {minterm(*t)}（{code(t)}）")
    add(gb, fig, f"极小项-{code(t)}", n=6)

# ---- ④ 用 ∨ 连接成主析取范式（动作子帧 1000ms） ----
EXPR_PARTS = [minterm(*t) for t in TRUE]
for j in range(len(EXPR_PARTS)):
    fig, ax = frame(TITLE)
    draw_rows(ax, marked=True, m_done=5)
    draw_rule(ax)
    note(ax, "用 ∨ 连接 5 个极小项（按编码从小到大）")
    expr = " ∨ ".join(EXPR_PARTS[:j + 1])
    ax.text(5.0, 0.18, expr, ha="center", va="center", fontsize=12.5,
            color=C_OK, fontweight="bold")
    add(gb, fig, f"连接-{j+1}", n=2)

# ---- 尾帧：完整主析取范式 + 编码（8000ms） ----
fig, ax = frame(TITLE)
draw_rows(ax, marked=True, m_done=5)
draw_rule(ax)
note(ax, "主析取范式编码：m0∨m2∨m4∨m6∨m7", y=0.62, col=C_OK, bold=True,
     fs=13.5)
ax.text(5.0, 0.18, " ∨ ".join(EXPR_PARTS), ha="center", va="center",
        fontsize=12.5, color=C_OK, fontweight="bold")
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
