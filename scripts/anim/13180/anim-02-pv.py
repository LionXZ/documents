# -*- coding: utf-8 -*-
"""13180《操作系统》动图 02：PV 信号量与生产者-消费者问题。

数据：缓冲区 5 格；mutex=1（互斥）、empty=5（空缓冲数）、full=0（满缓冲数）。
分镜：布局与初值 → 生产者五步（P(empty)→P(mutex)→放入→V(mutex)→V(full)）
      → 生产至全满 → 再生产被阻塞（empty=-1）→ 消费者取货并 V(empty) 唤醒
      → 尾帧小结（P/V 定义、互斥与同步用法、错误顺序导致死锁）。
QA 由 style.snapshot 内置检测。
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images/os-anim-02-pv.gif"

PROD = ["P(empty)", "P(mutex)", "放入产品", "V(mutex)", "V(full)"]
CONS = ["P(full)", "P(mutex)", "取走产品", "V(mutex)", "V(empty)"]

BASE = dict(buf=[None] * 5, mutex=1, empty=5, full=0,
            pline=-1, cline=-1, pblocked=False, wake=False,
            note1=None, note2=None)


def draw(s):
    """按状态 dict s 画一帧，返回 (fig, ax)。"""
    fig, ax = style.new_fig(title="PV 信号量与生产者-消费者（缓冲区 5 格）")

    # ---- 生产者框（阻塞时变红）----
    pc = style.C_LRED if s["pblocked"] else style.C_LIGHT
    pec = style.C_RED if s["pblocked"] else style.C_BLUE
    ax.add_patch(plt.Rectangle((2, 26), 24, 23, fc=pc, ec=pec, lw=2))
    head = "生产者（阻塞）" if s["pblocked"] else "生产者"
    ax.text(14, 46.3, head, ha="center", fontsize=11.5, fontweight="bold", color=pec)
    for i, code in enumerate(PROD):
        y = 42.4 - i * 3.5
        hl = (i == s["pline"])
        if hl:
            ax.add_patch(plt.Rectangle((3.4, y - 1.5), 21.2, 3.0,
                                       fc="#FDE68A", ec="none", zorder=1))
        ax.text(14, y, code, ha="center", va="center", fontsize=11.5, zorder=2,
                color=style.C_TEXT if hl else style.C_GRAY,
                fontweight="bold" if hl else "normal")

    # ---- 消费者框 ----
    ax.add_patch(plt.Rectangle((74, 26), 24, 23, fc=style.C_LIGHT, ec=style.C_BLUE, lw=2))
    ax.text(86, 46.3, "消费者", ha="center", fontsize=12.5, fontweight="bold", color=style.C_BLUE)
    for i, code in enumerate(CONS):
        y = 42.4 - i * 3.5
        hl = (i == s["cline"])
        if hl:
            ax.add_patch(plt.Rectangle((75.4, y - 1.5), 21.2, 3.0,
                                       fc="#FDE68A", ec="none", zorder=1))
        ax.text(86, y, code, ha="center", va="center", fontsize=11.5, zorder=2,
                color=style.C_TEXT if hl else style.C_GRAY,
                fontweight="bold" if hl else "normal")

    # ---- 缓冲区 5 格 ----
    ax.text(51, 45.6, "缓冲区（5 格）", ha="center", fontsize=12,
            fontweight="bold", color=style.C_TEXT)
    for i in range(5):
        x0 = 31.8 + i * 7.7
        has = s["buf"][i]
        ax.add_patch(plt.Rectangle((x0, 33), 7.7, 8,
                                   fc=style.C_LIGHT if has else "#FFFFFF",
                                   ec=style.C_GRAY, lw=1.5))
        if has:
            ax.text(x0 + 3.85, 37, has, ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color=style.C_BLUE)

    # ---- 唤醒箭头 ----
    if s["wake"]:
        ax.annotate("", xy=(27, 23.5), xytext=(73, 23.5),
                    arrowprops=dict(arrowstyle="-|>", color=style.C_GREEN,
                                    lw=2.5, connectionstyle="arc3,rad=0.25"))
        ax.text(50, 19.5, "V(empty) 唤醒阻塞的生产者", ha="center",
                fontsize=12, fontweight="bold", color=style.C_GREEN)

    # ---- 信号量卡片 ----
    cards = [("mutex", s["mutex"], "互斥信号量"),
             ("empty", s["empty"], "空缓冲数"),
             ("full", s["full"], "满缓冲数")]
    for i, (name, val, desc) in enumerate(cards):
        x0 = 8 + i * 30
        ax.add_patch(plt.Rectangle((x0, 3), 24, 10, fc="#F7FAFC",
                                   ec=style.C_BLUE, lw=1.5))
        ax.text(x0 + 12, 9.6, f"{name} = {val}", ha="center", va="center",
                fontsize=14, fontweight="bold", color=style.C_RED)
        ax.text(x0 + 12, 5.4, desc, ha="center", va="center",
                fontsize=10.5, color=style.C_GRAY)

    # ---- 顶部旁注 ----
    if s["note1"]:
        ax.text(50, 54.2, s["note1"], ha="center", fontsize=13.5,
                fontweight="bold", color=style.C_TEXT)
    if s["note2"]:
        ax.text(50, 50.6, s["note2"], ha="center", fontsize=11.5, color=style.C_GRAY)
    return fig, ax


def summary_frame(frames):
    """尾帧：P/V 小结（独立干净布局，驻留 16 帧）。"""
    fig, ax = style.new_fig(title="PV 操作小结")
    lines = [
        (54.0, "P ＝ 申请：信号量减 1；减 1 后 < 0，则阻塞自己", style.C_TEXT, 13.5, True),
        (48.8, "V ＝ 释放：信号量加 1；加 1 后 ≤ 0，则唤醒一个等待者", style.C_TEXT, 13.5, True),
        (42.6, "实现互斥：同一个 mutex，先 P 后 V 夹住临界区", style.C_BLUE, 13, True),
        (37.4, "实现同步：用资源信号量 empty / full 控制生产与消费的次序", style.C_BLUE, 13, True),
        (30.6, "注意：若先 P(mutex) 后 P(empty) —— 缓冲区满时，生产者", style.C_RED, 12.5, False),
        (26.2, "持有锁等待空缓冲，消费者进不了临界区 → 死锁", style.C_RED, 12.5, False),
    ]
    for y, t, c, fs, bold in lines:
        ax.text(50, y, t, ha="center", fontsize=fs, color=c,
                fontweight="bold" if bold else "normal")
    style.snapshot(fig, frames, "P13-尾帧小结")
    style.hold(fig, frames, style.TAIL_HOLD)
    plt.close(fig)


def main():
    frames = []
    steps = [
        ("P1-布局与初值", {},
         dict(note1="三个信号量：mutex 管互斥，empty / full 管同步",
              note2="先看生产者放入一个产品的完整过程")),
        ("P2-P(empty)", dict(pline=0, empty=4),
         dict(note1="P(empty)：申请一个空缓冲  5 → 4",
              note2="P 操作：信号量减 1；若减 1 后 < 0，则自己阻塞进入等待队列")),
        ("P3-P(mutex)", dict(pline=1, mutex=0),
         dict(note1="P(mutex)：进入临界区前先加锁  1 → 0",
              note2="mutex 初值 1，保证同一时刻只有一个进程访问缓冲区")),
        ("P4-放入产品", dict(pline=2, buf=["产品1", None, None, None, None]),
         dict(note1="把产品放入第 1 格",
              note2="此时生产者仍在临界区内（mutex = 0）")),
        ("P5-V(mutex)", dict(pline=3, mutex=1),
         dict(note1="V(mutex)：退出临界区解锁  0 → 1",
              note2="V 操作：信号量加 1；若加 1 后 ≤ 0，则唤醒一个等待者")),
        ("P6-V(full)", dict(pline=4, full=1),
         dict(note1="V(full)：满缓冲数加 1  0 → 1",
              note2="full 表示已有产品的格数，消费者凭它判断能否取货")),
        ("P7-生产至全满", dict(pline=-1, buf=["产品1", "产品2", "产品3", "产品4", "产品5"],
                          full=5, empty=0),
         dict(note1="连续生产：缓冲区全满（5 格均有产品）",
              note2="empty = 0：空缓冲用完；full = 5：满缓冲 5 个")),
        ("P8-生产者阻塞", dict(pline=0, pblocked=True, empty=-1,
                          buf=["产品1", "产品2", "产品3", "产品4", "产品5"], full=5),
         dict(note1="生产者再想放入：P(empty) 使 empty = -1 < 0",
              note2="减 1 后小于 0 → 生产者阻塞，代码停在 P(empty) 处")),
        ("P9-消费P(full)", dict(cline=0, full=4,
                           buf=["产品1", "产品2", "产品3", "产品4", "产品5"], empty=-1),
         dict(note1="消费者取货：P(full)  5 → 4",
              note2="申请一个满缓冲，允许取货")),
        ("P10-消费P(mutex)", dict(cline=1, mutex=0,
                             buf=["产品1", "产品2", "产品3", "产品4", "产品5"], empty=-1, full=4),
         dict(note1="消费者：P(mutex)  1 → 0",
              note2="进入临界区取产品")),
        ("P11-取走产品", dict(cline=2, buf=[None, "产品2", "产品3", "产品4", "产品5"],
                         mutex=0, empty=-1, full=4),
         dict(note1="取走第 1 格的产品，该格变空",
              note2="消费者仍在临界区内（mutex = 0）")),
        ("P12-唤醒生产者", dict(cline=4, mutex=1, empty=0, wake=True, pblocked=False,
                          buf=[None, "产品2", "产品3", "产品4", "产品5"], full=4),
         dict(note1="V(mutex) 解锁 0 → 1；V(empty) 使 empty 由 -1 → 0",
              note2="加 1 后 ≤ 0 说明有等待者 → V(empty) 唤醒阻塞的生产者")),
    ]
    for tag, upd, note in steps:
        s = {**BASE, **upd, **note}
        fig, ax = draw(s)
        style.snapshot(fig, frames, tag)
        style.hold(fig, frames, style.HOLD_MIN)
        plt.close(fig)

    summary_frame(frames)
    style.save_gif(frames, OUT)


if __name__ == "__main__":
    main()
