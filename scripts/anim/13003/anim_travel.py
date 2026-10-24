# -*- coding: utf-8 -*-
"""动图 04：二叉树前序 / 中序 / 后序遍历走树（三幕）。

树与文档【例 5-2】一致（8 结点）：
        A
       / \
      B   C
     / \    \
    D   E    F
       / \   /
      G   H I
前序 A B D E G H C F I；中序 D B G E H A C I F；后序 D G H E B I F C A。
文档对应：第 5 章 树与二叉树 - 5.3 遍历。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

POS = {"A": (30, 44), "B": (18, 35), "C": (44, 35),
       "D": (12, 26), "E": (25, 26), "F": (51, 26),
       "G": (19, 17), "H": (31, 17), "I": (51, 17)}
EDGES = [("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"),
         ("C", "F"), ("E", "G"), ("E", "H"), ("F", "I")]
ORDERS = {
    "前序（根 → 左 → 右）": ["A", "B", "D", "E", "G", "H", "C", "F", "I"],
    "中序（左 → 根 → 右）": ["D", "B", "G", "E", "H", "A", "C", "I", "F"],
    "后序（左 → 右 → 根）": ["D", "G", "H", "E", "B", "I", "F", "C", "A"],
}

rec = Recorder()
qa = []

def draw_tree(title, note, visited, cur=None, seq=(), hold=SUB):
    fig, ax = new_fig(title, note)
    # 树区左移，右栏留序列
    for a, b in EDGES:
        x1, y1 = POS[a]; x2, y2 = POS[b]
        arrow(ax, x1, y1, x2, y2, color=C_EDGE, lw=1.8, style="-", zorder=1)
    for name, (x, y) in POS.items():
        fc = C_DONE if name in visited else C_NODE
        if name == cur:
            fc = C_HL
        ax.add_patch(plt.Circle((x, y), 3.4, fc=fc, ec=C_EDGE, lw=1.8, zorder=3))
        ax.text(x, y, name, ha="center", va="center", fontsize=14,
                fontweight="bold", color=C_TEXT, zorder=4)
    # 右栏：访问序列
    ax.text(72, 44, "访问序列", ha="center", fontsize=12.5, color="#455A64", fontweight="bold")
    cols = 2
    for k, s in enumerate(seq):
        r, c = divmod(k, cols)
        ax.text(66 + c * 12, 38.5 - r * 5.6, s, ha="center", va="center",
                fontsize=14, fontweight="bold", color="#1565C0",
                bbox=dict(boxstyle="circle,pad=0.32", fc=C_NODE, ec=C_EDGE, lw=1.2))
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

for order_name, order in ORDERS.items():
    visited, seq = set(), []
    draw_tree(f"二叉树 {order_name.split('（')[0]}遍历 · {order_name.split('（')[1][:-1]}",
              "空树返回；否则按规则访问——先记住口诀再看指针怎么走",
              visited, None, [], hold=HOLD)
    for i, name in enumerate(order):
        visited.add(name)
        seq.append(name)
        draw_tree(f"二叉树遍历 · {order_name}", f"第 {i+1} 步：访问 {name}", visited, cur=name, seq=seq, hold=SUB)
    draw_tree(f"二叉树遍历 · {order_name} 完成", f"{order_name}：{'  '.join(order)}",
              visited, None, seq=order, hold=HOLD)

# 结论幕
fig, ax = new_fig("三种遍历 · 结论", "同一棵树，三种访问次序（先/中/后 = 根的位置）")
rows = [("前序", "根→左→右", "A B D E G H C F I", 37),
        ("中序", "左→根→右", "D B G E H A C I F", 27),
        ("后序", "左→右→根", "D G H E B I F C A", 17)]
for name, rule, seq_txt, y in rows:
    ax.text(10, y, name, ha="center", fontsize=14, fontweight="bold", color="#1565C0")
    ax.text(24, y, rule, ha="center", fontsize=13, color=C_TEXT)
    ax.text(55, y, seq_txt, ha="center", fontsize=14, fontweight="bold", color=C_TEXT,
            bbox=dict(boxstyle="round,pad=0.4", fc=C_NODE, ec=C_EDGE))
ax.text(45, 8, "记忆锚点：名字里的第几个字，根就在第几位；中序 + 前序/后序任一可唯一还原二叉树", ha="center",
        fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-travel.gif")
check_and_save(rec, out)
