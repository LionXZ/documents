# -*- coding: utf-8 -*-
"""(P∧Q)∨¬R 真值表逐行生成 动图脚本。

数据来源：2024.10 简答题真题原公式 (P∧Q)∨¬R（ANIM_SPEC 第 1 条锚定，数字不许改）。
8 行赋值按 000→111 顺序逐行算出 P∧Q、¬R、最终值；
成真行（000、010、100、110、111）共 5 个，最后统一绿色高亮。
节奏：等效驻留制（与已完成动图一致）——解释画面 3000ms、动作子帧 1000~1500ms、尾帧 8000ms。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# 苹方 .ttc 集合字体加载不稳，显式改用单文件 ttf 的 Arial Unicode MS（∧∨¬ 等符号齐全）
plt.rcParams["font.family"] = ["Arial Unicode MS"]
set_style()

OUT = os.path.join("09-计算机基础", "离散数学", "images", "02324-anim-truthtable.gif")

# ---------- 数据锚定与程序验算 ----------
ROWS = [(p, q, r) for p in (0, 1) for q in (0, 1) for r in (0, 1)]   # 000→111

def calc(p, q, r):
    """按 (P∧Q)∨¬R 算一行：返回 (P∧Q, ¬R, 结果)。"""
    return p & q, 1 - r, (p & q) | (1 - r)

TRUE = [row for row in ROWS if calc(*row)[2] == 1]     # 成真赋值
assert TRUE == [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)], "成真行与 SPEC 不符"

def TF(v):
    """0/1 转成 F/T。"""
    return "T" if v else "F"

# ---------- 表格布局（数据坐标 x:0-10, y:0-5.68，与像素等比） ----------
COL = {"P": 1.5, "Q": 2.6, "R": 3.7, "AND": 5.0, "NOT": 6.2, "RES": 8.0}
HDR_Y, ROW0, DY = 5.05, 4.45, 0.52                     # 表头 y / 首行 y / 行距
TB = (0.95, 0.55, 9.05, 5.32)                          # 表格外框 (x0, y0, x1, y1)

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

def note(ax, s, y=0.30, col="#4a5568", fs=12.5, bold=False):
    """底部说明行。"""
    ax.text(5.0, y, s, ha="center", va="center", fontsize=fs, color=col,
            fontweight="bold" if bold else "normal")

def draw_table(ax, done_rows, cur=None, stage=0, hl=None, true_rows=()):
    """画真值表。done_rows=已完成行数；cur+stage=当前行填到第几步
    （1 赋值 / 2 加中间列 / 3 加结果）；hl=黄色高亮行；true_rows=成真行（绿底）。"""
    x0, y0, x1, y1 = TB
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor="white",
                           edgecolor=C_DIM, lw=1.4, zorder=0))
    ax.plot([x0, x1], [4.78, 4.78], color=C_DIM, lw=1.2, zorder=1)
    for x in (4.35, 5.6, 6.85):        # 三条列分隔浅线
        ax.plot([x, x], [y0, 4.78], color="#e2e8f0", lw=1.0, zorder=1)
    for key, s in [("P", "P"), ("Q", "Q"), ("R", "R"), ("AND", "P∧Q"),
                   ("NOT", "¬R"), ("RES", "(P∧Q)∨¬R")]:
        ax.text(COL[key], HDR_Y, s, ha="center", va="center", fontsize=14,
                color="#2d3748", fontweight="bold")
    for i in range(8):                 # 行标签：与 P 列数字水平间距 0.9（≥0.8）
        ax.text(0.6, ROW0 - i * DY, str(i + 1), ha="center", va="center",
                fontsize=12.5, color="#718096")
    # 逐行填值：complete 行整行显示；当前行按 stage 渐进显示
    for i, (p, q, r) in enumerate(ROWS):
        y = ROW0 - i * DY
        and_, notr, res = calc(p, q, r)
        complete = i < done_rows
        if true_rows and (p, q, r) in true_rows:   # 成真行绿底
            ax.add_patch(Rectangle((x0 + 0.03, y - 0.23), x1 - x0 - 0.06,
                                   0.46, facecolor="#dcfce7",
                                   edgecolor="none", zorder=1))
        if hl == i:                                # 当前行黄底
            ax.add_patch(Rectangle((x0 + 0.03, y - 0.23), x1 - x0 - 0.06,
                                   0.46, facecolor=C_MARK,
                                   edgecolor="none", zorder=1))
        show_asn = complete or (cur == i and stage >= 1)
        show_mid = complete or (cur == i and stage >= 2)
        show_res = complete or (cur == i and stage >= 3)
        vals = []
        if show_asn:
            vals += [("P", TF(p), "#2d3748"), ("Q", TF(q), "#2d3748"),
                     ("R", TF(r), "#2d3748")]
        if show_mid:
            vals += [("AND", TF(and_), "#2d3748"), ("NOT", TF(notr), "#2d3748")]
        if show_res:                               # 结果列：T 绿加粗，F 灰
            vals += [("RES", TF(res), C_OK if res else C_DIM)]
        for key, s, c in vals:
            ax.text(COL[key], y, s, ha="center", va="center", fontsize=14,
                    color=c, zorder=3,
                    fontweight="bold" if key == "RES" and res else "normal")

# ================= 帧序列 =================
TITLE = "真值表逐行生成：(P∧Q)∨¬R（2024.10 真题公式）"
gb = GifBuilder(fps=2)

# ---- 开场：空表 + 8 行说明（解释画面 3000ms） ----
fig, ax = frame(TITLE)
draw_table(ax, done_rows=0)
note(ax, "3 个变元 P、Q、R → 共 2³ = 8 行赋值，从上到下逐行算")
add(gb, fig, "开场", n=6)

# ---- 逐行填表：赋值 → 中间列 → 结果（动作子帧 1000~1500ms） ----
for i, (p, q, r) in enumerate(ROWS):
    and_, notr, res = calc(p, q, r)
    fig, ax = frame(TITLE)
    draw_table(ax, done_rows=i, cur=i, stage=1, hl=i)
    note(ax, f"第 {i+1} 行：P={p}，Q={q}，R={r}")
    add(gb, fig, f"行{i+1}-赋值", n=2)

    fig, ax = frame(TITLE)
    draw_table(ax, done_rows=i, cur=i, stage=2, hl=i)
    note(ax, f"P∧Q：有 F 则 F = {TF(and_)}；¬R：R={r} 取反 = {TF(notr)}")
    add(gb, fig, f"行{i+1}-中列", n=2)

    fig, ax = frame(TITLE)
    draw_table(ax, done_rows=i, cur=i, stage=3, hl=i)
    if res:
        note(ax, f"{TF(and_)}∨{TF(notr)}：有 T 则 T → 结果 T（成真）", col=C_OK)
    else:
        note(ax, "F∨F：全 F 则 F → 结果 F")
    add(gb, fig, f"行{i+1}-结果", n=3)

# ---- 成真行统一绿色高亮（解释画面 3000ms） ----
fig, ax = frame(TITLE)
draw_table(ax, done_rows=8, true_rows=TRUE)
note(ax, "成真赋值 5 个：000、010、100、110、111（绿色行）",
     y=0.30, col=C_OK, bold=True)
add(gb, fig, "成真行高亮", n=6)

# ---- 尾帧（8000ms） ----
fig, ax = frame(TITLE)
draw_table(ax, done_rows=8, true_rows=TRUE)
note(ax, "成真赋值 5 个：000、010、100、110、111（绿色行）",
     y=0.34, col=C_OK, bold=True)
note(ax, "规律：R=0 的 4 行全真；R=1 时需 P=Q=1 才成真", y=0.05)
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
