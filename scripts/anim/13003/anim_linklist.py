# -*- coding: utf-8 -*-
"""动图 10：单链表插入与删除（指针变化）。

数据与文档【例 2-2】一致：链表 a1→a2→a3→a4，
① 在 a2 后插入 x：s->next = p->next; p->next = s（先接后断，顺序不能反）；
② 删除 a3：p->next = p->next->next。
文档对应：第 2 章 线性表 - 2.2 单链表。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

rec = Recorder()
qa = []

def draw(nodes, title, note, hi=(), ghost=None, dropped=(), arrows_over=(), hold=SUB,
         labels_extra=None):
    """nodes: [(标签,x)]；arrows_over: {(起点标签): (终点标签, 颜色, 弧度高)} 额外跨接箭头。"""
    fig, ax = new_fig(title, note)
    posmap = {}
    for k, (lab, x) in enumerate(nodes):
        if lab in dropped:
            continue
        fc = C_HL if lab in hi else C_NODE
        ax.add_patch(plt.Rectangle((x - 4.2, 26), 8.4, 8, fc=fc, ec=C_EDGE, lw=1.8, zorder=3))
        ax.text(x, 30, lab, ha="center", va="center", fontsize=13.5, fontweight="bold", zorder=4)
        posmap[lab] = x
        if dropped and lab == nodes[len(nodes) - 1][0]:
            pass
    # 链箭头（相邻）
    keys = [lab for lab, _ in nodes if lab not in dropped]
    for a, b in zip(keys, keys[1:]):
        arrow(ax, posmap[a] + 4.2, 30, posmap[b] - 4.2, 30, color=C_EDGE, lw=2.2)
    # 跨接箭头
    for a, (b, color, arc) in (arrows_over or {}).items():
        if a not in posmap or b not in posmap:
            continue
        arrow(ax, posmap[a] + 4.2, 30, posmap[b] - 4.2, 30, color=color, lw=2.8,
              connectionstyle=f"arc3,rad={arc}")
    # head 指针
    if keys:
        x0 = posmap[keys[0]]
        ax.text(x0 - 11.5, 30, "head", ha="center", va="center", fontsize=12.5,
                fontweight="bold", color="#6A1B9A")
        arrow(ax, x0 - 8.2, 30, x0 - 4.4, 30, color="#6A1B9A", lw=2.4)
    if dropped:
        for lab, x in nodes:
            if lab in dropped:
                ax.add_patch(plt.Rectangle((x - 4.2, 26), 8.4, 8, fc="#ECEFF1", ec=C_DIM,
                                           lw=1.4, zorder=2, linestyle="--"))
                ax.text(x, 30, lab, ha="center", va="center", fontsize=13.5,
                        color=C_DIM, zorder=2)
                ax.annotate("已脱离链", xy=(x, 34.2), xytext=(x, 40), ha="center",
                            fontsize=10.5, color="#B71C1C",
                            arrowprops=dict(arrowstyle="->", color="#B71C1C"))
    ax.text(45, 16, "单链表插删只改指针、不移动元素 → 时间 O(1)（找到位置后）", ha="center",
            fontsize=11.5, color="#455A64")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

X = 12
base = [("a1", X), ("a2", X + 16), ("a3", X + 32), ("a4", X + 48)]

# ============ 幕 A：插入 x ============
draw(base, "单链表 · 在 a2 后插入 x", "先定位：p 指向 a2，新结点 s（值 x）待插入", hold=HOLD)
draw(base + [("x", X + 24)], "单链表 · 第 ① 步：s->next = p->next",
     "新结点 s 的后继先接 a3（先接后断——若先改 p->next 会丢掉 a3 起的整条链）",
     hi=("x", "a3"), arrows_over={"x": ("a3", "#E65100", -0.35)}, hold=HOLD)
draw(base + [("x", X + 24)], "单链表 · 第 ② 步：p->next = s",
     "再把 a2 的后继改指向 x —— 插入完成，只动了两根指针",
     hi=("a2", "x"), arrows_over={"a2": ("x", "#1565C0", -0.3), "x": ("a3", "#E65100", -0.35)}, hold=HOLD)

# ============ 幕 B：删除 a3 ============
draw(base + [("x", X + 24)], "单链表 · 删除 a3", "定位 p 指向 a2（被删结点的前驱）", hi=("a2", "a3"), hold=HOLD)
draw(base + [("x", X + 24)], "单链表 · 删除 a3：p->next = p->next->next",
     "a2 的后继直接改指 a3 的后继 a4；a3 脱离链表",
     hi=("a2", "a4"), dropped=("a3",), arrows_over={"a2": ("a4", "#1565C0", -0.4)}, hold=HOLD)
draw([("a1", X), ("a2", X + 16), ("a4", X + 48)], "单链表 · 删除完成",
     "被删结点释放（free）；链长 4 → 3", hold=HOLD)

# 结论幕
fig, ax = new_fig("单链表插删 · 结论", "")
ax.text(45, 40, "① 插入口诀：先接后断——s->next = p->next; p->next = s（次序反了丢链）", ha="center",
        fontsize=13.5, color=C_TEXT)
ax.text(45, 33.5, "② 删除（带前驱）：p->next = p->next->next；释放被删结点", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 27, "③ 改指针 O(1)；但查找定位须从头扫 → 按位序插删整体 O(n)", ha="center", fontsize=13.5, color="#B26A00")
ax.text(45, 20.5, "④ 与顺序表对照：链表插删不搬元素、顺序表可随机存取——按场景选型", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 13, "记忆锚点：单链表每个结点 = 数据域 + 指针域；尾结点指针域为空（∧）", ha="center",
        fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-linklist.gif")
check_and_save(rec, out)
