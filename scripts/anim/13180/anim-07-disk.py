# -*- coding: utf-8 -*-
"""anim-07-disk.py —— 13180《操作系统》教学动图：磁盘调度算法 SSTF 与 SCAN。

数据来源：2026.4 真题综合题 38（画面标注「2026.4 真题数据」）。
- 磁道号范围 0~199；磁头当前停在 53 号道（刚完成 30 号道请求）
- 请求序列（到达次序）：98, 183, 35, 120, 10, 122, 64, 66

画面清单：
1. 题面（磁道号竖轴 + 磁头 53 + 8 个请求点）
2. FCFS 分三阶段连线：总计 45+85+148+85+110+112+58+2 = 645 道
3. SSTF 逐步推演 8 步：总计 11+2+31+25+88+22+2+61 = 242 道
4. SCAN（电梯）三阶段：上行到 199 端点才调头；146+189 = 335 道（LOOK 变体 303 道）
5. 尾帧：三算法寻道量对比条形图与点评
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "操作系统/images/os-anim-07-disk.gif")

REQ = [98, 183, 35, 120, 10, 122, 64, 66]            # 请求序列（到达次序）
FCFS = [53] + REQ                                    # FCFS 服务路径
SSTF = [53, 64, 66, 35, 10, 98, 120, 122, 183]       # SSTF 服务路径
SCAN = [53, 64, 66, 98, 120, 122, 183, 199, 35, 10]  # SCAN 服务路径
GRAY = "#A7B0BC"  # 未服务请求点的浅灰

# SSTF 每步数据：(当前磁头, 入选请求, 距离, 落选请求, 落选距离)
STEPS = [
    (53, 64, 11, 66, 13),
    (64, 66, 2, None, None),
    (66, 35, 31, 98, 32),
    (35, 10, 25, None, None),
    (10, 98, 88, None, None),
    (98, 120, 22, None, None),
    (120, 122, 2, None, None),
    (122, 183, 61, None, None),
]


def ty(t):
    """磁道号 → 画布 y 坐标（0~199 线性映射到 6~50）"""
    return 6.0 + 44.0 * t / 199.0


def xs_of(n):
    """服务次序 → 画布 x 坐标（图表区 11~57 等距）"""
    return [11.0 + k * 46.0 / (n - 1) for k in range(n)]


def scene(title):
    """新建带标题与真题角标的画布"""
    fig, ax = style.new_fig(title=title)
    ax.text(97.5, 57.3, "2026.4 真题数据", fontsize=10, color=style.C_GRAY,
            ha="right", va="center")
    return fig, ax


def draw_axes(ax):
    """画磁道号竖轴与服务次序横轴"""
    ax.plot([6, 6], [4.5, 50.5], color=style.C_GRAY, lw=1.2)
    ax.plot([6, 58], [4.5, 4.5], color=style.C_GRAY, lw=1.2)
    ax.annotate("", xy=(59.5, 4.5), xytext=(56.5, 4.5),
                arrowprops=dict(arrowstyle="->", color=style.C_GRAY, lw=1.2))
    ax.text(3.4, 17, "磁道号", fontsize=11, color=style.C_GRAY,
            rotation=90, va="center", ha="center")
    ax.text(32, 1.4, "服务次序（时间从左到右）", fontsize=11,
            color=style.C_GRAY, ha="center")
    for t in (0, 100, 199):
        ax.text(5.2, ty(t), str(t), fontsize=10.5, color=style.C_GRAY,
                ha="right", va="center")


def seg_mark(ax, xs, tracks, k, color, fs, bold, shift=(0.0, 0.0)):
    """在第 k 段中点标注移动道数（上行标上方、下行标下方）；shift 可微调避让"""
    xm = (xs[k] + xs[k + 1]) / 2 + shift[0]
    ym = (ty(tracks[k]) + ty(tracks[k + 1])) / 2 + shift[1]
    d = abs(tracks[k + 1] - tracks[k])
    yy = ym + (1.7 if tracks[k + 1] >= tracks[k] else -2.3)
    ax.text(xm, yy, str(d), fontsize=fs, ha="center", va="center", color=color,
            fontweight="bold" if bold else "normal")


def draw_chart(ax, tracks, seg_upto, chosen_seg=None, loser_pair=None,
               seg_labels=True, label_shifts=None):
    """画调度轨迹图。

    tracks：服务路径；seg_upto：已确定的线段数；
    chosen_seg：当前步入选线段（橙粗）；loser_pair：落选线段的点下标对（灰虚线）；
    label_shifts：{线段下标: (dx, dy)} 个别段标注的避让位移。
    """
    label_shifts = label_shifts or {}
    n = len(tracks)
    xs = xs_of(n)
    draw_axes(ax)
    for k in range(seg_upto):  # 已走过的线段
        if k == chosen_seg:
            continue
        ax.plot([xs[k], xs[k + 1]], [ty(tracks[k]), ty(tracks[k + 1])],
                color=style.C_BLUE, lw=2.0, zorder=2, solid_capstyle="round")
    if loser_pair is not None:  # 落选候选（灰虚线）
        k1, k2 = loser_pair
        ax.plot([xs[k1], xs[k2]], [ty(tracks[k1]), ty(tracks[k2])],
                color=GRAY, lw=1.6, ls=(0, (4, 3)), zorder=2)
    if chosen_seg is not None:  # 当前入选线段（橙粗）
        k = chosen_seg
        ax.plot([xs[k], xs[k + 1]], [ty(tracks[k]), ty(tracks[k + 1])],
                color=style.C_ORANGE, lw=3.2, zorder=4, solid_capstyle="round")
    # 线段距离标注
    if seg_labels:
        for k in range(seg_upto):
            color = style.C_ORANGE if k == chosen_seg else style.C_BLUE
            seg_mark(ax, xs, tracks, k, color,
                     11.5 if k == chosen_seg else 10.5,
                     k == chosen_seg, shift=label_shifts.get(k, (0.0, 0.0)))
    # 服务点与标签（标签放在来线方向的反侧，避免被折线穿过）
    for k, t in enumerate(tracks):
        if k == 0:
            c, ms = style.C_TEXT, 10
        elif chosen_seg is not None and k == chosen_seg + 1:
            c, ms = style.C_ORANGE, 8.5          # 刚被服务的点
        elif k <= seg_upto:
            c, ms = style.C_BLUE, 7
        else:
            c, ms = GRAY, 7
        ax.plot([xs[k]], [ty(t)], "o", ms=ms, color=c, zorder=5)
        above = False if k == 0 else ty(tracks[k]) >= ty(tracks[k - 1])
        yy = ty(t) + 2.2 if above else ty(t) - 2.6
        prefix = "磁头 " if k == 0 else ""
        ax.text(xs[k], yy, prefix + str(t), fontsize=11, ha="center",
                color=c, fontweight="bold")
    return xs


def panel(ax, lines, y0=48.5, dy=4.6):
    """右侧信息面板：lines 为 (文本, 颜色, 字号, 是否加粗)"""
    y = y0
    for txt, color, fs, bold in lines:
        ax.text(61.5, y, txt, fontsize=fs, color=color, va="center",
                fontweight="bold" if bold else "normal")
        y -= dy


# ============ 画面 1：题面 ============
frames = []
fig, ax = scene("磁盘调度算法：FCFS · SSTF · SCAN")
draw_chart(ax, FCFS, seg_upto=0, seg_labels=False)
panel(ax, [
    ("磁道号范围：0 ~ 199", style.C_TEXT, 13, False),
    ("磁头当前位置：53 号道（图中●）", style.C_TEXT, 13, False),
    ("刚完成 30 号道的请求", style.C_GRAY, 12, False),
    ("请求序列（到达次序）：", style.C_TEXT, 13, True),
    ("98、183、35、120、10、122、64、66", style.C_BLUE, 13, False),
    ("目标：依次服务完全部请求，", style.C_TEXT, 13, False),
    ("使磁头移动的总道数尽量少", style.C_TEXT, 13, False),
])
style.snapshot(fig, frames, "题面")
style.hold(fig, frames, style.HOLD_MIN)
plt.close(fig)

# ============ 画面 2~4：FCFS 三阶段 ============
fcfs_stages = [
    (2, [
        ("FCFS：按到达次序依次服务", style.C_TEXT, 13.5, True),
        ("路径：53 → 98 → 183", style.C_BLUE, 12.5, False),
        ("各段移动：45、85", style.C_BLUE, 12.5, False),
        ("累计移动：45 + 85 = 130 道", style.C_TEXT, 13, True),
    ]),
    (5, [
        ("FCFS：按到达次序依次服务", style.C_TEXT, 13.5, True),
        ("路径：53→98→183→35→120→10", style.C_BLUE, 12.5, False),
        ("各段移动：45、85、148、85、110", style.C_BLUE, 12.5, False),
        ("累计移动：130+148+85+110 = 473 道", style.C_TEXT, 13, True),
    ]),
    (8, [
        ("FCFS：按到达次序依次服务", style.C_TEXT, 13.5, True),
        ("路径：53→98→183→35→120→10→122→64→66",
         style.C_BLUE, 11.5, False),
        ("各段移动：45、85、148、85、110、112、58、2", style.C_BLUE, 11.5, False),
        ("45+85+148+85+110+112+58+2 = 645 道", style.C_ORANGE, 12.5, True),
        ("按到达顺序机械执行，路径交叉往返，寻道量大", style.C_RED, 12, True),
    ]),
]
for upto, lines in fcfs_stages:
    fig, ax = scene("FCFS 先来先服务：按到达次序连线")
    draw_chart(ax, FCFS, seg_upto=upto, chosen_seg=upto - 1)
    panel(ax, lines)
    style.snapshot(fig, frames, f"FCFS {upto}/8")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 5~12：SSTF 逐步推演（8 步） ============
cum = 0
path = [53]
for i, (cur, nxt, d, lk, ld) in enumerate(STEPS, 1):
    cum += d
    path.append(nxt)
    lines = [
        (f"SSTF 最短寻道时间优先（第 {i}/8 步）", style.C_TEXT, 13.5, True),
        (f"当前磁头：{cur} 号道", style.C_TEXT, 13, False),
        (f"选最近请求：{nxt} 号道（距 {d} 道）", style.C_ORANGE, 13, True),
    ]
    if lk is not None:
        lines.append((f"对比：比 {lk} 号道（距 {ld} 道）更近", style.C_GRAY, 12, False))
    lines.append(("已走：" + "→".join(str(p) for p in path),
                  style.C_BLUE, 10.5, False))
    lines.append((f"累计寻道：{cum} 道", style.C_TEXT, 13, True))
    if i == len(STEPS):
        lines.append(("总计 11+2+31+25+88+22+2+61 = 242 道", style.C_GREEN, 12.5, True))
    fig, ax = scene(f"SSTF：每次选距当前磁头最近的请求（第 {i}/8 步）")
    loser_pair = (i - 1, SSTF.index(lk)) if lk is not None else None
    draw_chart(ax, SSTF, seg_upto=i - 1, chosen_seg=i - 1, loser_pair=loser_pair)
    panel(ax, lines)
    style.snapshot(fig, frames, f"SSTF 第{i}步")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 13~15：SCAN（电梯算法）三阶段 ============
scan_stages = [
    (6, [
        ("SCAN（电梯算法）：沿一个方向扫描", style.C_TEXT, 13.5, True),
        ("方向：磁道号增大，沿途依次服务", style.C_TEXT, 13, False),
        ("64、66、98、120、122、183", style.C_BLUE, 12.5, False),
        ("当前移到 183 号道", style.C_TEXT, 13, False),
    ]),
    (7, [
        ("183 之后上行再无请求，但 SCAN 规定：", style.C_TEXT, 13, False),
        ("一直移到最外端 199 才调头", style.C_ORANGE, 13.5, True),
        ("（教材口径：到最外/最内侧才折返）", style.C_GRAY, 11.5, False),
    ]),
    (9, [
        ("调头后向磁道号减小方向：服务 35、10", style.C_TEXT, 12.5, False),
        ("上行：(199 - 53) = 146 道", style.C_TEXT, 12.5, False),
        ("下行：(199 - 10) = 189 道", style.C_TEXT, 12.5, False),
        ("总计：146 + 189 = 335 道", style.C_ORANGE, 13, True),
        ("LOOK 变体：到 183 后无请求即调头：", style.C_ORANGE, 11.5, False),
        ("(183-53)+(183-10) = 130+173 = 303 道", style.C_ORANGE, 11.5, False),
    ]),
]
for upto, lines in scan_stages:
    fig, ax = scene("SCAN 扫描（电梯）算法：扫到端点再回头")
    # 183→199 段较短，其标注右下微移避让点标「183」
    draw_chart(ax, SCAN, seg_upto=upto, chosen_seg=upto - 1,
               label_shifts={6: (1.6, -0.7)})
    panel(ax, lines)
    style.snapshot(fig, frames, f"SCAN {upto}/9")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

# ============ 画面 16：尾帧结论对比 ============
fig, ax = style.new_fig(title="结论对比：三种磁盘调度算法的总寻道量")
bars = [
    ("FCFS（按到达次序）", 645, "#8A94A6"),
    ("SSTF（每次选最近）", 242, style.C_GREEN),
    ("SCAN（扫到端点回头）", 335, style.C_BLUE),
]
for i, (name, val, color) in enumerate(bars):
    yc = 42 - i * 9.5
    ax.text(27.5, yc, name, fontsize=13, color=style.C_TEXT, ha="right", va="center")
    w = val / 645.0 * 45.0
    ax.barh([yc], [w], height=4.4, color=color, left=29, zorder=3)
    ax.text(29 + w + 1.8, yc, f"{val} 道", fontsize=14, color=color,
            fontweight="bold", va="center")
ax.text(29, 8.5, "SSTF 寻道量小但可能饥饿（远端请求）；", fontsize=13,
        color=style.C_GREEN, va="center")
ax.text(29, 4.5, "SCAN 无饥饿、各磁道机会更公平", fontsize=13,
        color=style.C_GREEN, va="center")
style.snapshot(fig, frames, "尾帧结论")
style.hold(fig, frames, style.TAIL_HOLD)
plt.close(fig)

style.save_gif(frames, OUT)
print(f"[done] anim-07 总帧数={len(frames)}")
