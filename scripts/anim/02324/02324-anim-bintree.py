# -*- coding: utf-8 -*-
"""二叉树三种遍历（先序 / 中序 / 后序）三幕动画脚本。
数据来源：自编教学数据，与文档例题同步（ANIM_SPEC 第 11 条锚定，不许改）。
树：根 A，左 B 右 C；B 左 D 右 E；C 左 F（F 为叶）。
先序（根左右）= A B D E C F；中序（左根右）= D B E A F C；后序（左右根）= D E B F C A。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import (set_style, new_fig, GifBuilder, qa_figure,
                          C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK)
from matplotlib.patches import Circle, Rectangle

OUT = os.path.join("09-计算机基础", "离散数学", "images", "02324-anim-bintree.gif")
set_style()

# ---------- 树的数据（锚定）----------
TPOS = {"A": (5.0, 4.9), "B": (3.2, 3.9), "C": (6.8, 3.9),
        "D": (2.2, 2.9), "E": (4.2, 2.9), "F": (5.8, 2.9)}
TEDGES = [("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "F")]
R = 0.27                       # 顶点半径
# 三种遍历（锚定）：幕名 -> (访问序列, 口诀, 备注)
TRAVERSALS = {
    "先序": ("ABDECF", "根 -> 左 -> 右", "根最先被记录（序列开头是 A）"),
    "中序": ("DBEAFC", "左 -> 根 -> 右", "根夹在左右子树之间（第 4 位）"),
    "后序": ("DEBFCA", "左 -> 右 -> 根", "根最后被记录（序列末尾是 A）"),
}
# 序列格子：6 格，格宽 0.75、格高 0.6，中心 y=1.2
CELL_W, CELL_H, CELL_Y = 0.75, 0.6, 1.2
CELL_X0 = 3.25                 # 第 1 格中心 x，向右步进 CELL_W


def make_frame(order, k, note=False, dim=False):
    """绘制一帧。order=遍历名；k=已访问点数(0~6)；note=是否显示备注行；
    dim=True 时树整体画成灰色（用于总结帧背景）。"""
    name, seq, motto, tips = order_name(order)
    fig, ax = new_fig("二叉树三种遍历：先序 · 中序 · 后序")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    visited = list(seq[:k])
    cur = visited[-1] if visited else None
    tree_col = C_DIM if dim else "#1a202c"
    # ---- 树：边 ----
    for a, b in TEDGES:
        (x0, y0), (x1, y1) = TPOS[a], TPOS[b]
        ax.plot([x0, x1], [y0, y1], color=tree_col, lw=2, zorder=2)
    # ---- 树：顶点（已访绿 / 当前红大 / 未访蓝；dim 时全灰）----
    for kk, (x, y) in TPOS.items():
        if dim:
            fc = C_DIM
        elif kk == cur:
            fc = C_HIGH
        elif kk in visited:
            fc = C_OK
        else:
            fc = C_MAIN
        rr = R + (0.07 if kk == cur and not dim else 0)
        ax.add_patch(Circle((x, y), rr, fc=fc, ec="white", lw=1.5, zorder=5))
        ax.text(x, y, kk, fontsize=14, color="white", ha="center",
                va="center", fontweight="bold", zorder=6)
    return fig, ax


def order_name(order):
    """取幕的数据：名称 / 访问序列 / 口诀 / 备注。"""
    seq, motto, tips = TRAVERSALS[order]
    return order, seq, motto, tips


def draw_cells(ax, order, k, note=False):
    """幕名 + 口诀行 + 序列格子（前 k 格已填，最新一格黄色高亮）。"""
    name, seq, motto, tips = order_name(order)
    ax.text(5.0, 2.05, f"{name}遍历（{motto}）", fontsize=14,
            fontweight="bold", color=C_MAIN, ha="center")
    for j in range(6):
        cx = CELL_X0 + j * CELL_W
        filled = j < k
        fc = C_MARK if j == k - 1 else ("white" if filled else "#f1f1f1")
        ax.add_patch(Rectangle((cx - CELL_W / 2, CELL_Y - CELL_H / 2),
                               CELL_W, CELL_H, fc=fc, ec="#8a94a0", lw=1.2, zorder=3))
        if filled:
            ax.text(cx, CELL_Y, seq[j], fontsize=15, ha="center", va="center",
                    fontweight="bold", color="#1a202c", zorder=4)
    if note:
        ax.text(5.0, 0.45, tips, fontsize=12.5, color="#555555", ha="center")


# ================= 主流程：三幕 + 总结 =================
gb = GifBuilder(fps=2)
qa_total = 0


def emit(fig, ax, n, ctx, order=None, k=0, note=False):
    """先画序列区再 QA 加帧；问题数累计。"""
    global qa_total
    if order is not None:
        draw_cells(ax, order, k, note)
    qa_total += qa_figure(fig, ctx)
    gb.add(fig, n=n)

# 三幕循环：幕头 6 帧 -> 逐点访问各 2 帧 -> 幕尾备注 8 帧
for order in ["先序", "中序", "后序"]:
    fig, ax = make_frame(order, 0)
    emit(fig, ax, 6, f"{order}幕头", order=order, k=0)
    seq = TRAVERSALS[order][0]
    for k in range(1, 7):
        fig, ax = make_frame(order, k)
        emit(fig, ax, 2, f"{order}访问{seq[k-1]}", order=order, k=k)
    fig, ax = make_frame(order, 6)
    emit(fig, ax, 8, f"{order}幕尾", order=order, k=6, note=True)

# 总结尾帧：灰树背景 + 三序列对照 + 记忆锚点（驻留 16 帧 = 8 秒）
fig, ax = make_frame("先序", 0, dim=True)
ax.text(5.0, 2.05, "先序（根 -> 左 -> 右）：A B D E C F", fontsize=13.5,
        color="#1a202c", ha="center")
ax.text(5.0, 1.50, "中序（左 -> 根 -> 右）：D B E A F C", fontsize=13.5,
        color="#1a202c", ha="center")
ax.text(5.0, 0.95, "后序（左 -> 右 -> 根）：D E B F C A", fontsize=13.5,
        color="#1a202c", ha="center")
ax.text(5.0, 0.35, "记忆锚点：先序根在前 · 中序根在中 · 后序根在后",
        fontsize=14, color=C_OK, fontweight="bold", ha="center")
qa_total += qa_figure(fig, "总结")
gb.add(fig, n=16)

gb.save(OUT)
print(f"[QA] bintree 问题总数 = {qa_total}")
sys.exit(1 if qa_total > 0 else 0)
