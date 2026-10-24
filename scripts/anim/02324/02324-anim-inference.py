# -*- coding: utf-8 -*-
"""推理规则两幕动图：假言推理 + 拒取式。

数据来源：ANIM_SPEC 第 3 条锚定（教材标准规则形式）。
幕一「假言推理」：前提 P→Q，P ⇒ 结论 Q（肯定前件则肯定后件）
幕二「拒取式」：前提 P→Q，¬Q ⇒ 结论 ¬P（否定后件则否定前件）
关联真题：2024.10 证明题（S→¬Q，S∨R，¬R↔Q ⊢ R），尾帧提示考题用法。
节奏：等效驻留制——解释画面单帧 3000ms、动作子帧 1500ms、尾帧 8000ms。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import set_style, new_fig, GifBuilder, qa_figure
from render_utils import C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# 苹方 .ttc 集合字体加载不稳，显式改用 Arial Unicode MS（⇒ ⊢ ↔ 等齐全）
plt.rcParams["font.family"] = ["Arial Unicode MS"]
set_style()

OUT = os.path.join("09-计算机基础", "离散数学", "images", "02324-anim-inference.gif")

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

def note(ax, s, y=1.5, col="#4a5568", fs=13, bold=False):
    """底部说明行。"""
    ax.text(5.0, y, s, ha="center", va="center", fontsize=fs, color=col,
            fontweight="bold" if bold else "normal")

def box(ax, cx, cy, w, h, s, fc="white", ec=C_MAIN, lw=2.0):
    """圆角矩形前提/结论框 + 居中加粗文字。"""
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.06,rounding_size=0.12",
                 facecolor=fc, edgecolor=ec, lw=lw, zorder=2))
    ax.text(cx, cy, s, ha="center", va="center", fontsize=15,
            color="#1a202c", fontweight="bold", zorder=3)

def arrows(ax):
    """两条前提框汇聚到结论框的箭头（弧线避开中间的 ⇒ 号）。"""
    for xa, ya, xb, yb, rad in [(4.28, 3.98, 6.02, 3.58, -0.25),
                                (4.28, 2.68, 6.02, 3.08, 0.25)]:
        ax.add_patch(FancyArrowPatch((xa, ya), (xb, yb),
                     connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                     mutation_scale=16, color=C_HIGH, lw=2.2, zorder=1))

def act_frame(act2=False, hl=False, show_arrows=False, done=False):
    """画一幕底图。act2=拒取式（前提 ¬Q / 结论 ¬P）；hl=高亮前提 2；
    show_arrows=画推理箭头；done=结论框染绿。"""
    title = ("推理规则二：拒取式   P→Q，¬Q ⇒ ¬P" if act2
             else "推理规则一：假言推理   P→Q，P ⇒ Q")
    fig, ax = frame(title)
    box(ax, 2.55, 3.98, 3.3, 0.85, "前提 1：P → Q")
    box(ax, 2.55, 2.68, 3.3, 0.85, "前提 2：¬Q" if act2 else "前提 2：P",
        fc="#fee2e2" if hl else "white", ec=C_HIGH if hl else C_MAIN,
        lw=3.0 if hl else 2.0)
    box(ax, 7.55, 3.33, 2.9, 0.85, "结论：¬P" if act2 else "结论：Q",
        fc="#dcfce7" if done else "white", ec=C_OK if done else C_MAIN,
        lw=2.4 if done else 2.0)
    ax.text(5.15, 3.33, "⇒", ha="center", va="center", fontsize=28,
            color=C_HIGH, fontweight="bold")
    if show_arrows or done:
        arrows(ax)
    return fig, ax

# ================= 帧序列 =================
gb = GifBuilder(fps=2)

# ---- 幕一 假言推理：P→Q，P ⇒ Q ----
fig, ax = act_frame()
note(ax, "两条前提合起来，推出一个结论")
add(gb, fig, "幕1-开场", n=6)

fig, ax = act_frame(hl=True)
note(ax, "前提 P 真：肯定前件")
add(gb, fig, "幕1-肯定前件", n=3)

fig, ax = act_frame(hl=True, show_arrows=True)
note(ax, "P→Q 说的是：有 P 就必有 Q")
add(gb, fig, "幕1-箭头", n=3)

fig, ax = act_frame(show_arrows=True, done=True)
note(ax, "于是 Q 必真：肯定后件", col=C_OK)
add(gb, fig, "幕1-结论", n=3)

fig, ax = act_frame(done=True)
note(ax, "为什么成立：肯定前件，则肯定后件", col=C_OK, bold=True)
add(gb, fig, "幕1-为什么", n=6)

fig, ax = act_frame(done=True)
note(ax, "为什么成立：肯定前件，则肯定后件", col=C_OK, bold=True)
note(ax, "例：P=「下雨」，Q=「地湿」：下雨 + 下雨则地湿 ⇒ 地湿", y=0.7)
add(gb, fig, "幕1-例子", n=6)

# ---- 幕二 拒取式：P→Q，¬Q ⇒ ¬P ----
fig, ax = act_frame(act2=True)
note(ax, "前提换成 ¬Q：从「否定后件」往回推")
add(gb, fig, "幕2-开场", n=6)

fig, ax = act_frame(act2=True, hl=True)
note(ax, "Q 假：否定后件")
add(gb, fig, "幕2-否定后件", n=3)

fig, ax = act_frame(act2=True, hl=True, show_arrows=True)
note(ax, "P→Q 的逆否等价：Q 假则 P 必假")
add(gb, fig, "幕2-箭头", n=3)

fig, ax = act_frame(act2=True, show_arrows=True, done=True)
note(ax, "于是 P 必假：否定前件", col=C_OK)
add(gb, fig, "幕2-结论", n=3)

fig, ax = act_frame(act2=True, done=True)
note(ax, "为什么成立：否定后件，则否定前件", col=C_OK, bold=True)
add(gb, fig, "幕2-为什么", n=6)

fig, ax = act_frame(act2=True, done=True)
note(ax, "为什么成立：否定后件，则否定前件", col=C_OK, bold=True)
note(ax, "例：地不湿 + 下雨则地湿 ⇒ 没下雨（Q 假推 P 假）", y=0.7)
add(gb, fig, "幕2-例子", n=6)

# ---- 尾帧：两规则口诀 + 考题用法（8000ms） ----
fig, ax = act_frame(act2=True, done=True)
note(ax, "假言推理：肯定前件 ⇒ 肯定后件 ｜ 拒取式：否定后件 ⇒ 否定前件",
     y=1.5, col=C_OK, bold=True, fs=13.5)
note(ax, "考题用法：证明题（2024.10：S→¬Q，S∨R，¬R↔Q ⊢ R）每步写明规则名",
     y=0.7, fs=12.5)
add(gb, fig, "尾帧", n=16)

ok = gb.save(OUT)
print("保存", "成功" if ok else "失败（超过 2MB）")
