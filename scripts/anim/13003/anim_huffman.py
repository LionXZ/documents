# -*- coding: utf-8 -*-
"""动图 14：哈夫曼树构造与 WPL 计算。

数据与文档【例 5-4】一致：权值 {7, 5, 2, 4}。
构造：2+4=6 → 5+6=11 → 7+11=18；WPL = 7×1 + 5×2 + 2×3 + 4×3 = 35。
文档对应：第 5 章 树与二叉树 - 5.5 哈夫曼树。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

rec = Recorder()
qa = []

# 结点集：(名字, 权, x, y)（动态布局手工给定）
def draw_frame(title, note, nodes, links, sel=(), new_root=None, hold=SUB, wpl_lines=None):
    """nodes: [(label, w, x, y, is_leaf)]；links: [(父,子)]；sel: 参与合并的两个结点 label。"""
    fig, ax = new_fig(title, note)
    childmap = {}
    for p, c in links:
        childmap.setdefault(p, []).append(c)
    pos = {n[0]: (n[2], n[3]) for n in nodes}
    for p, c in links:
        hot = p == new_root
        arrow(ax, pos[p][0], pos[p][1], pos[c][0], pos[c][1],
              color="#E65100" if hot else C_EDGE, lw=3 if hot else 1.8, style="-", zorder=1)
    for label, w, x, y, is_leaf in nodes:
        if label in sel:
            fc = C_HL
        elif label == new_root:
            fc = C_VIS
        else:
            fc = C_NODE if is_leaf else C_QUEUE
        ax.add_patch(plt.Circle((x, y), 3.5, fc=fc, ec=C_EDGE, lw=1.8, zorder=3))
        ax.text(x, y, label, ha="center", va="center", fontsize=12.5, fontweight="bold", zorder=4)
        ax.text(x, y - 5.2, str(w), ha="center", fontsize=11.5, color="#0D47A1", zorder=4, fontweight="bold")
    if wpl_lines:
        for txt, y, color in wpl_lines:
            ax.text(74, y, txt, ha="center", fontsize=13, color=color, fontweight="bold")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 幕 0：初始森林
draw_frame("哈夫曼树 · 初始（每权一棵单结点树）", "规则：每次取权最小的两棵树合并，新根权 = 之和；重复至只剩一棵",
           [("7", 7, 12, 30, True), ("5", 5, 26, 30, True), ("2", 2, 40, 30, True), ("4", 4, 54, 30, True)],
           [], hold=HOLD)

# 步 1：选 2、4 合并成 6
draw_frame("哈夫曼树 · 第 1 步：选最小的 2 和 4", "森林中最小的两个权：2 与 4 → 合并，新根权 6",
           [("7", 7, 12, 30, True), ("5", 5, 26, 30, True), ("2", 2, 44, 20, True), ("4", 4, 58, 20, True),
            ("6", 6, 51, 34, False)],
           [("6", "2"), ("6", "4")], sel=("2", "4"), hold=SUB)
draw_frame("哈夫曼树 · 第 1 步完成：新树权 6", "森林变为 {7, 5, 6}",
           [("7", 7, 12, 30, True), ("5", 5, 26, 30, True), ("2", 2, 44, 20, True), ("4", 4, 58, 20, True),
            ("6", 6, 51, 34, False)],
           [("6", "2"), ("6", "4")], new_root="6", hold=HOLD)

# 步 2：选 5、6 合并成 11
draw_frame("哈夫曼树 · 第 2 步：选最小的 5 和 6", "森林 {7, 5, 6} 中最小两个：5 与 6 → 合并，新根权 11",
           [("7", 7, 12, 30, True), ("5", 5, 44, 18, True), ("2", 2, 56, 8, True), ("4", 4, 70, 8, True),
            ("6", 6, 63, 18, False), ("11", 11, 53, 32, False)],
           [("6", "2"), ("6", "4"), ("11", "5"), ("11", "6")], sel=("5", "6"), hold=SUB)
draw_frame("哈夫曼树 · 第 2 步完成：新树权 11", "森林变为 {7, 11}",
           [("7", 7, 12, 30, True), ("5", 5, 44, 18, True), ("2", 2, 56, 8, True), ("4", 4, 70, 8, True),
            ("6", 6, 63, 18, False), ("11", 11, 53, 32, False)],
           [("6", "2"), ("6", "4"), ("11", "5"), ("11", "6")], new_root="11", hold=HOLD)

# 步 3：选 7、11 合并成 18（最终树）
final_nodes = [("7", 7, 30, 34, True), ("11", 11, 52, 34, False),
               ("5", 5, 44, 20, True), ("6", 6, 60, 20, False),
               ("2", 2, 53, 9, True), ("4", 4, 67, 9, True), ("18", 18, 41, 46, False)]
final_links = [("18", "7"), ("18", "11"), ("11", "5"), ("11", "6"), ("6", "2"), ("6", "4")]
draw_frame("哈夫曼树 · 第 3 步：选 7 和 11 → 根 18", "只剩一棵树，构造完成",
           final_nodes, final_links, sel=("7", "11"), hold=SUB)

# 结论幕：WPL
draw_frame("哈夫曼树 · WPL（带权路径长度）", "WPL = 各叶结点 权 × 路径长度（到根的边数）之和",
           final_nodes, final_links, new_root="18",
           wpl_lines=[("7×1 = 7", 40, C_TEXT), ("5×2 = 10", 34, C_TEXT),
                      ("2×3 = 6", 28, C_TEXT), ("4×3 = 12", 22, C_TEXT),
                      ("WPL = 35", 15, "#1B5E20")],
           hold=HOLD)

fig, ax = new_fig("哈夫曼树 · 结论", "")
ax.text(45, 38, "① 构造口诀：每次取权值最小的两棵合并（可用小根堆/反复选最小）", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 31.5, "② n 个叶的哈夫曼树共 2n-1 个结点、无度为 1 的结点（本例 4 叶 → 7 结点）", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 25, "③ 权越大的叶离根越近 → WPL 最小；WPL = Σ 权ᵢ×路径长ᵢ（本例 35）", ha="center", fontsize=13.5, color="#0D47A1")
ax.text(45, 18.5, "④ 哈夫曼树不唯一（左右子树可交换），但 WPL 唯一且最小", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 11, "记忆锚点：哈夫曼 = 最优二叉树 = WPL 最小；前缀码：任一编码都不是另一编码的前缀", ha="center",
        fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-huffman.gif")
check_and_save(rec, out)
