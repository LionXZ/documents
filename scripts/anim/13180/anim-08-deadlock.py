# -*- coding: utf-8 -*-
"""anim-08-deadlock.py —— 13180《操作系统》教学动图：死锁四条件与循环等待。

场景数据：2026.4 真题综合题 39 示意（画面标注「2026.4 真题场景」）。
- 某类资源 R 共 2 个（不可剥夺）
- P1 持有 1 个、又申请 1 个被阻塞；P2 持有 1 个、也申请 1 个被阻塞

画面清单：
1~4. 四个必要条件逐个出现的卡片：互斥 / 不可剥夺 / 请求并保持 / 循环等待
5.   场景图：已分配（绿实线）+ 申请等待（红虚线）→ 形成等待环 → 死锁
6.   四条件关系：缺一不可，破坏任一条件即可预防（互斥通常不可破坏）
7.   尾帧：预防 / 避免 / 解除 三大处理策略
"""

import os
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "操作系统/images/os-anim-08-deadlock.gif")

# 四个必要条件：(名称, 卡片一句话（已按行拆好）, 主题色)
CONDS = [
    ("互斥", ["资源一次只能被一个进程使用"], style.C_BLUE),
    ("不可剥夺", ["资源只能由持有者自愿释放，", "不能被强行夺走"], style.C_PURPLE),
    ("请求并保持", ["持有资源的同时又申请新资源，", "被阻塞时不释放已有资源"], style.C_ORANGE),
    ("循环等待", ["存在 进程→资源→进程 的", "环形等待链"], style.C_GREEN),
]


def card(ax, x, y, w, h, fc, ec, lw=1.8):
    """圆角卡片"""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.5,rounding_size=1.2",
                                fc=fc, ec=ec, lw=lw))


def fbox(ax, x, y, w, h, text, fc, ec, fs, tc=None, bold=True, lw=1.8):
    """流程框：框 + 居中文本"""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.4,rounding_size=0.8",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            color=tc or style.C_TEXT,
            fontweight="bold" if bold else "normal")


def arrow(ax, xy_from, xy_to, color, lw=2.0, ls="-"):
    """带箭头连线"""
    ax.annotate("", xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls))


# ============ 画面 1~4：四个必要条件逐个出现 ============
frames = []
for i, (name, sent, color) in enumerate(CONDS, 1):
    fig, ax = style.new_fig(title=f"死锁的四个必要条件（{i}/4）：{name}")
    # 左侧大卡片
    card(ax, 32, 31, 48, 32, style.C_LIGHT, color, lw=2.2)
    ax.text(32, 37, name, fontsize=21, color=color, ha="center",
            va="center", fontweight="bold")
    if len(sent) == 1:
        ax.text(32, 26, sent[0], fontsize=14, color=style.C_TEXT,
                ha="center", va="center")
    else:
        ax.text(32, 28, sent[0], fontsize=14, color=style.C_TEXT,
                ha="center", va="center")
        ax.text(32, 22.5, sent[1], fontsize=14, color=style.C_TEXT,
                ha="center", va="center")
    # 右侧进度清单
    ax.text(79, 45, "四个必要条件", fontsize=14, color=style.C_TEXT,
            ha="center", fontweight="bold")
    for j, (cname, _, ccolor) in enumerate(CONDS):
        ry = 38.5 - j * 6.5
        if j < i - 1:            # 已讲过
            ax.text(68, ry, "●", fontsize=11, color=ccolor, ha="center", va="center")
            ax.text(71.5, ry, cname, fontsize=13.5, color=style.C_TEXT, va="center")
        elif j == i - 1:         # 当前讲到
            ax.text(68, ry, "▲", fontsize=12, color=style.C_ORANGE, ha="center", va="center")
            ax.text(71.5, ry, cname, fontsize=14.5, color=style.C_ORANGE,
                    va="center", fontweight="bold")
        else:                    # 还没讲
            ax.text(68, ry, "○", fontsize=11, color=style.C_GRAY, ha="center", va="center")
            ax.text(71.5, ry, cname, fontsize=13, color=style.C_GRAY, va="center")
    style.snapshot(fig, frames, f"条件{i}：{name}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)


# ============ 画面 5：真题场景图（三个子画面递进） ============
def draw_scenario(ax, stage):
    """死锁场景图：stage 1 已分配 → 2 申请等待 → 3 形成环死锁"""
    ax.text(50, 55.5, "绿实线：已分配　　红虚线：申请等待",
            fontsize=12, color=style.C_GRAY, ha="center", va="center")
    ax.text(66, 52.5, "资源 R（共 2 个，不可剥夺）", fontsize=12.5,
            color=style.C_TEXT, ha="center", va="center")
    # 进程框
    fbox(ax, 17, 45, 13, 8, "P1", style.C_LIGHT, style.C_BLUE, 17)
    ax.text(17, 38.2, "持有 1 个，又申请 1 个", fontsize=11.5,
            color=style.C_TEXT, ha="center", va="center")
    ax.text(17, 35.6, "→ 被阻塞", fontsize=11.5, color=style.C_RED,
            ha="center", va="center")
    fbox(ax, 17, 15, 13, 8, "P2", style.C_LIGHT, style.C_BLUE, 17)
    ax.text(17, 8.2, "持有 1 个，也申请 1 个", fontsize=11.5,
            color=style.C_TEXT, ha="center", va="center")
    ax.text(17, 5.6, "→ 被阻塞", fontsize=11.5, color=style.C_RED,
            ha="center", va="center")
    # 资源方块（2 个实例）
    for rx, ry, tag in ((66, 45, "实例 1"), (66, 15, "实例 2")):
        ax.add_patch(Rectangle((rx - 4.5, ry - 4), 9, 8, fc=style.C_YELLOW,
                               ec=style.C_ORANGE, lw=1.8))
        ax.text(rx, ry + 1.4, "R", fontsize=15, color=style.C_TEXT,
                ha="center", va="center", fontweight="bold")
        ax.text(rx, ry - 1.8, tag, fontsize=10, color=style.C_GRAY,
                ha="center", va="center")
    # 已分配（绿实线：资源 → 占有它的进程）
    arrow(ax, (61.2, 45), (24, 45), style.C_GREEN, lw=2.6)
    ax.text(43, 47.1, "已分配", fontsize=12, color=style.C_GREEN, ha="center")
    arrow(ax, (61.2, 15), (24, 15), style.C_GREEN, lw=2.6)
    ax.text(43, 17.1, "已分配", fontsize=12, color=style.C_GREEN, ha="center")
    if stage >= 2:  # 申请等待（红虚线：进程 → 它等待的资源）
        arrow(ax, (23.5, 41.5), (62.5, 18.8), style.C_RED, lw=2.2, ls="--")
        ax.text(37.5, 32.2, "申请等待", fontsize=12, color=style.C_RED, ha="center")
        arrow(ax, (23.5, 18.5), (62.5, 41.2), style.C_RED, lw=2.2, ls="--")
        ax.text(49.5, 36.4, "申请等待", fontsize=12, color=style.C_RED, ha="center")
    if stage >= 3:  # 结论
        ax.text(50, 2.6, "两个进程互相等待对方占有的资源，谁也不释放 → 死锁",
                fontsize=13.5, color=style.C_RED, ha="center", va="center",
                fontweight="bold")


for stage in (1, 2, 3):
    fig, ax = style.new_fig(title="死锁场景：互相等待，谁也不释放")
    ax.text(97.5, 57.3, "2026.4 真题场景", fontsize=10, color=style.C_GRAY,
            ha="right", va="center")
    draw_scenario(ax, stage)
    style.snapshot(fig, frames, f"场景 stage{stage}")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 6：四条件的关系 ============
fig, ax = style.new_fig(title="四个条件的关系：缺一不可")
card_pos = [(27.5, 41), (72.5, 41), (27.5, 23), (72.5, 23)]
for (cx, cy), (idx, (name, _, color)) in zip(card_pos, enumerate(CONDS, 1)):
    card(ax, cx, cy, 38, 12, style.C_LIGHT, color, lw=2.0)
    ax.text(cx, cy, f"{'①②③④'[idx - 1]} {name}", fontsize=15.5, color=color,
            ha="center", va="center", fontweight="bold")
ax.text(50, 12, "四个条件缺一不可 —— 全部同时成立才可能死锁",
        fontsize=14.5, color=style.C_TEXT, ha="center", va="center",
        fontweight="bold")
ax.text(50, 6.5, "破坏任意一个条件即可预防死锁（互斥条件通常不可破坏）",
        fontsize=13, color=style.C_ORANGE, ha="center", va="center")
style.snapshot(fig, frames, "四条件关系")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)

# ============ 画面 7：尾帧三大处理策略 ============
fig, ax = style.new_fig(title="尾帧总结：死锁的处理策略")
strategies = [
    ("死锁预防", "破坏四个必要条件之一（如：资源有序分配法破坏「循环等待」）",
     style.C_BLUE, 44),
    ("死锁避免", "银行家算法：每次分配前判断，始终保持在安全状态",
     style.C_GREEN, 28.5),
    ("死锁解除", "资源剥夺 / 撤销进程 / 进程回退",
     style.C_ORANGE, 13),
]
for name, desc, color, yc in strategies:
    card(ax, 50, yc, 84, 11, style.C_LIGHT, color, lw=2.0)
    ax.text(13, yc, name, fontsize=16, color=color, va="center", fontweight="bold")
    ax.text(32, yc, desc, fontsize=12.5, color=style.C_TEXT, va="center")
style.snapshot(fig, frames, "尾帧策略")
style.hold(fig, frames, style.TAIL_HOLD)
plt.close(fig)

style.save_gif(frames, OUT)
print(f"[done] anim-08 总帧数={len(frames)}")
