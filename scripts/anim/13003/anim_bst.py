# -*- coding: utf-8 -*-
"""动图 05：二叉排序树（BST）插入过程。

序列与文档【例 7-2】一致：45, 24, 53, 12, 28, 90（逐个插入）。
文档对应：第 7 章 查找 - 7.3 二叉排序树。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

SEQ = [45, 24, 53, 12, 28, 90]
rec = Recorder()
qa = []

# 树状态：node: dict 值 -> (x, y)
pos = {}
children = {}   # 值 -> (左值/None, 右值/None)

def layout(root_val, depth=0, x=45, span=26):
    """简单等距布局：每层 y 降 9，左右各分一半 span。"""
    if root_val is None:
        return
    pos[root_val] = (x, 46 - depth * 9.5)
    l, r = children[root_val]
    layout(l, depth + 1, x - span / 2, span / 2)
    layout(r, depth + 1, x + span / 2, span / 2)

def draw(title, note, path=(), cur=None, hold=SUB, inorder=None):
    fig, ax = new_fig(title, note)
    pos.clear()
    root = list(children)[0] if children else None
    layout(root)
    # 边
    for pv, (l, r) in children.items():
        for cv in (l, r):
            if cv is not None:
                x1, y1 = pos[pv]; x2, y2 = pos[cv]
                on = pv in path and cv in path
                arrow(ax, x1, y1, x2, y2, color="#E65100" if on else C_EDGE,
                      lw=3 if on else 1.8, style="-", zorder=1)
    # 结点
    for v, (x, y) in pos.items():
        if v == cur:
            fc = C_HL
        elif v in path:
            fc = C_VIS
        else:
            fc = C_NODE
        ax.add_patch(plt.Circle((x, y), 3.4, fc=fc, ec=C_EDGE, lw=1.8, zorder=3))
        ax.text(x, y, str(v), ha="center", va="center", fontsize=13.5,
                fontweight="bold", color=C_TEXT, zorder=4)
    # 比较说明
    if path:
        ax.text(45, 7, "比较规则：小往左、大往右、相等不插入（本例无相等）", ha="center",
                fontsize=11.5, color="#455A64")
    if inorder:
        ax.text(45, 11.5, "中序遍历：" + "  ".join(str(t) for t in inorder),
                ha="center", fontsize=13.5, color="#1B5E20", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", fc=C_DONE, ec=C_EDGE))
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 幕 0：BST 定义
draw("二叉排序树（BST）· 定义", "左子树所有结点 < 根 < 右子树所有结点；左右子树也各是 BST",
     hold=HOLD)

# 逐个插入
root = None
for i, v in enumerate(SEQ):
    if root is None:
        children[v] = (None, None)
        root = v
        draw(f"插入 {v}（第 {i+1} 个）", "树空 → 直接作根", path=(v,), cur=v, hold=HOLD)
        continue
    # 沿查找路径
    path = [root]
    cur = root
    while True:
        nxt = children[cur]
        go_left = v < cur
        draw(f"插入 {v}（第 {i+1} 个）", f"{v} 与 {cur} 比较：{'小于' if go_left else '大于'} → 走{'左' if go_left else '右'}子树",
             path=tuple(path), cur=cur, hold=SUB)
        child = nxt[0] if go_left else nxt[1]
        if child is None:
            if go_left:
                children[cur] = (v, nxt[1])
            else:
                children[cur] = (nxt[0], v)
            children[v] = (None, None)
            path.append(v)
            draw(f"插入 {v}（第 {i+1} 个）", f"空位 → {v} 作为 {cur} 的{'左' if go_left else '右'}孩子",
                 path=tuple(path), cur=v, hold=HOLD)
            break
        path.append(child)
        cur = child

# 结论幕
inorder = sorted(SEQ)
fig, ax = new_fig("BST 插入 · 结论", "中序遍历 BST 恰好得到升序序列（BST 的核心性质）")
layout(root)
for pv, (l, r) in children.items():
    for cv in (l, r):
        if cv is not None:
            arrow(ax, pos[pv][0], pos[pv][1], pos[cv][0], pos[cv][1], color=C_EDGE, lw=1.8, style="-")
for v, (x, y) in pos.items():
    ax.add_patch(plt.Circle((x, y), 3.4, fc=C_DONE, ec=C_EDGE, lw=1.8, zorder=3))
    ax.text(x, y, str(v), ha="center", va="center", fontsize=13.5, fontweight="bold", zorder=4)
ax.text(45, 9, "中序遍历 = 12  24  28  45  53  90（升序）；查找/插入最坏 O(n)（斜树）、平均 O(log₂n)",
        ha="center", fontsize=13, color=C_TEXT, fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-bst.gif")
check_and_save(rec, out)
