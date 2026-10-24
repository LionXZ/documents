# -*- coding: utf-8 -*-
"""13180《操作系统》动图 04：进程调度算法对比 FCFS vs SRTF。

数据（2026.4 真题综合题 36）：单 CPU，四进程 A(到达 0, 运行 12)、B(1,5)、C(2,3)、D(3,8)。
分镜：数据表 → FCFS 甘特图逐块 → FCFS 周转逐个 + 平均 17.75
      → SRTF 逐时刻推演（到达/抢占/完成）→ SRTF 周转与带权周转
      → 结论对比（13.5 更短但长作业可能饥饿）。
QA 由 style.snapshot 内置检测。
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images/os-anim-04-sched.gif"

TITLE = "进程调度算法对比：FCFS vs SRTF（2026.4 真题数据）"
PROCS = [("A", 0, 12), ("B", 1, 5), ("C", 2, 3), ("D", 3, 8)]
X0, X1 = 8, 92
FCFS_S = (X1 - X0) / 28.0     # FCFS 时间轴：0~28
SRTF_S = (X1 - X0) / 29.0     # SRTF 时间轴：0~29
FCFS_BLOCKS = [(0, 12, "A"), (12, 17, "B"), (17, 20, "C"), (20, 28, "D")]
SRTF_SEGS = [(0, 1, "A"), (1, 2, "B"), (2, 5, "C"), (5, 9, "B"), (9, 17, "D"), (17, 29, "A")]
PROC_FILL = {"A": style.C_LIGHT, "B": style.C_LGREEN, "C": "#FEF3C7", "D": "#F3EEFB"}
PROC_EDGE = {"A": style.C_BLUE, "B": style.C_GREEN, "C": style.C_ORANGE, "D": style.C_PURPLE}


def xx(s, scale):
    return X0 + s * scale


def block(ax, s0, s1, scale, y0, h, name, mode):
    """mode: done 完成 / cur 当前 / future 未运行"""
    x = xx(s0, scale)
    w = (s1 - s0) * scale
    if mode == "future":
        ax.add_patch(plt.Rectangle((x, y0), w, h, fc="#FFFFFF",
                                   ec=style.C_GRAY, lw=1.2, linestyle=(0, (3, 2))))
        tc = style.C_GRAY
    elif mode == "cur":
        ax.add_patch(plt.Rectangle((x, y0), w, h, fc="#FDE68A",
                                   ec=style.C_RED, lw=2))
        tc = style.C_TEXT
    else:
        ax.add_patch(plt.Rectangle((x, y0), w, h, fc=PROC_FILL[name],
                                   ec=PROC_EDGE[name], lw=1.6))
        tc = style.C_TEXT
    fs = 13 if w > 6 else 10.5
    ax.text(x + w / 2, y0 + h / 2, name, ha="center", va="center",
            fontsize=fs, fontweight="bold" if mode != "future" else "normal",
            color=tc)


def ticks(ax, ts, scale, y):
    for t in ts:
        ax.text(xx(t, scale), y, str(t), ha="center", va="top",
                fontsize=10, color=style.C_GRAY)


def notes(ax, n1, n2):
    if n1:
        ax.text(50, 54.2, n1, ha="center", fontsize=13.5, fontweight="bold",
                color=style.C_TEXT)
    if n2:
        ax.text(50, 50.6, n2, ha="center", fontsize=11.5, color=style.C_GRAY)


def table_frame(frames, tag):
    """P1：题面数据表。"""
    fig, ax = style.new_fig(title=TITLE)
    cols = [(30, 46), (46, 60), (60, 74)]
    heads = ["进程", "到达时间", "运行时间"]
    ax.add_patch(plt.Rectangle((30, 42.4), 44, 5.2, fc=style.C_LIGHT, ec=style.C_BLUE, lw=1.5))
    for (x0, x1), h in zip(cols, heads):
        ax.text((x0 + x1) / 2, 45.0, h, ha="center", va="center",
                fontsize=12, fontweight="bold", color=style.C_BLUE)
    for i, (name, arr, run) in enumerate(PROCS):
        y = 39 - i * 5.5
        ax.add_patch(plt.Rectangle((30, y - 2.4), 44, 4.8, fc="#FFFFFF",
                                   ec=style.C_GRAY, lw=1.2))
        for (x0, x1), v in zip(cols, (name, str(arr), str(run))):
            ax.text((x0 + x1) / 2, y, v, ha="center", va="center",
                    fontsize=12.5, color=style.C_TEXT)
    notes(ax, "单 CPU，四个进程同时竞争一个处理器",
          "分别用 FCFS（先来先服务）与 SRTF（最短剩余时间优先）调度并对比周转时间")
    style.snapshot(fig, frames, tag)
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)


def fcfs_frame(frames, tag, done_n, cur, n1, n2, formulas=None, avg=None, hold=style.HOLD_MIN):
    """FCFS 甘特图画面（含周转公式可选）。"""
    fig, ax = style.new_fig(title=TITLE)
    ax.text(50, 43, "FCFS（先来先服务）甘特图", ha="center", fontsize=12.5,
            fontweight="bold", color=style.C_TEXT)
    for i, (s0, s1, name) in enumerate(FCFS_BLOCKS):
        mode = "done" if i < done_n else ("cur" if i == cur else "future")
        block(ax, s0, s1, FCFS_S, 30, 8, name, mode)
    ticks(ax, [0, 12, 17, 20, 28], FCFS_S, 29.5)
    if formulas:
        for y, t in formulas:
            ax.text(50, y, t, ha="center", fontsize=13, color=style.C_TEXT)
    if avg:
        ax.text(50, avg[0], avg[1], ha="center", fontsize=14.5,
                fontweight="bold", color=style.C_BLUE)
    notes(ax, n1, n2)
    style.snapshot(fig, frames, tag)
    style.hold(fig, frames, hold)
    plt.close(fig)


def srtf_frame(frames, tag, rows, segs_done, segs_cur, n1, n2, bottom=None, hold=style.HOLD_MIN):
    """SRTF 推演画面：上半剩余时间状态表 + 下半甘特生长。

    rows: (name, desc, state)，state ∈ run / wait / new / notarrived / done
    """
    fig, ax = style.new_fig(title=TITLE)
    fill = {"run": "#FDE68A", "wait": "#FFFFFF", "new": style.C_LIGHT,
            "notarrived": None, "done": style.C_LGREEN}
    for i, (name, desc, st) in enumerate(rows):
        y = 47 - i * 5.5
        if fill[st]:
            ax.add_patch(plt.Rectangle((24, y - 2.1), 54, 4.2, fc=fill[st],
                                       ec=style.C_GRAY, lw=1.0))
        tc = style.C_GRAY if st == "notarrived" else style.C_TEXT
        ax.text(27, y, f"{name}：{desc}", ha="left", va="center",
                fontsize=12, fontweight="bold" if st == "run" else "normal",
                color=tc)
    for j, (s0, s1, name) in enumerate(segs_done):
        block(ax, s0, s1, SRTF_S, 14, 6, name, "done")
    if segs_cur:
        block(ax, segs_cur[0], segs_cur[1], SRTF_S, 14, 6, segs_cur[2], "cur")
    ends = {0} | {s0 for s0, _, _ in segs_done}
    if segs_done:
        ends.add(segs_done[-1][1])
    if segs_cur:
        ends.add(segs_cur[0])
    ticks(ax, sorted(ends), SRTF_S, 13.5)
    if bottom:
        for y, t, c, fs, bold in bottom:
            ax.text(50, y, t, ha="center", fontsize=fs, color=c,
                    fontweight="bold" if bold else "normal")
    notes(ax, n1, n2)
    style.snapshot(fig, frames, tag)
    style.hold(fig, frames, hold)
    plt.close(fig)


def main():
    frames = []
    table_frame(frames, "P1-数据表")

    # ---- FCFS：甘特图逐块 + 周转逐个 ----
    fcfs_steps = [
        ("P2a-FCFS-A", 0, 0, "FCFS：按到达顺序依次运行，A 最先到达先运行",
         "A：0 → 12（运行 12）"),
        ("P2b-FCFS-B", 1, 1, "A 完成后轮到 B", "B：12 → 17（运行 5）"),
        ("P2c-FCFS-C", 2, 2, "接着 C", "C：17 → 20（运行 3）"),
        ("P2d-FCFS-D", 3, 3, "最后 D", "D：20 → 28（运行 8）"),
    ]
    for tag, dn, cur, n1, n2 in fcfs_steps:
        fcfs_frame(frames, tag, dn, cur, n1, n2)

    fcfs_frame(frames, "P3a-FCFS周转AB", 4, -1,
               "周转时间 = 完成时刻 - 到达时刻",
               "按公式逐个计算：",
               formulas=[(16.5, "A：周转 = 12 - 0 = 12"),
                         (11.0, "B：周转 = 17 - 1 = 16")])
    fcfs_frame(frames, "P3b-FCFS周转CD", 4, -1,
               "周转时间 = 完成时刻 - 到达时刻",
               "继续计算：",
               formulas=[(16.5, "C：周转 = 20 - 2 = 18"),
                         (11.0, "D：周转 = 28 - 3 = 25")])
    fcfs_frame(frames, "P3c-FCFS平均", 4, -1,
               "FCFS 平均周转时间",
               "四个进程周转时间取平均：",
               avg=(14.0, "平均周转 = (12 + 16 + 18 + 25) ÷ 4 = 71 ÷ 4 = 17.75"))

    # ---- SRTF：逐时刻推演 ----
    srtf_frame(frames, "P4a-t0", [
        ("A", "到达 0 · 运行 12 · 剩余 12 ← 当前运行", "run"),
        ("B", "到达 1 · 运行 5 · 未到达", "notarrived"),
        ("C", "到达 2 · 运行 3 · 未到达", "notarrived"),
        ("D", "到达 3 · 运行 8 · 未到达", "notarrived"),
    ], [], (0, 0, "A"),
        "t=0：只有 A 到达 → A 运行", "无竞争，A 直接上 CPU")
    srtf_frame(frames, "P4b-t1", [
        ("A", "到达 0 · 运行 12 · 剩余 11（已运行 1）", "wait"),
        ("B", "到达 1 · 运行 5 · 剩余 5 ← 抢占 CPU", "run"),
        ("C", "到达 2 · 运行 3 · 未到达", "notarrived"),
        ("D", "到达 3 · 运行 8 · 未到达", "notarrived"),
    ], [(0, 1, "A")], (1, 1, "B"),
        "t=1：B 到达，B(5) < A 剩余(11) → B 抢占", "SRTF 总是让剩余运行时间最短的进程先执行")
    srtf_frame(frames, "P4c-t2", [
        ("A", "到达 0 · 运行 12 · 剩余 11", "wait"),
        ("B", "到达 1 · 运行 5 · 剩余 4（已运行 1）", "wait"),
        ("C", "到达 2 · 运行 3 · 剩余 3 ← 抢占 CPU", "run"),
        ("D", "到达 3 · 运行 8 · 未到达", "notarrived"),
    ], [(0, 1, "A"), (1, 2, "B")], (2, 2, "C"),
        "t=2：C 到达，C(3) < B 剩余(4) → C 抢占", "新到达进程的剩余时间更短，立即换它上 CPU")
    srtf_frame(frames, "P4d-t3", [
        ("A", "到达 0 · 运行 12 · 剩余 11", "wait"),
        ("B", "到达 1 · 运行 5 · 剩余 4", "wait"),
        ("C", "到达 2 · 运行 3 · 剩余 2 ← 继续运行", "run"),
        ("D", "到达 3 · 运行 8 · 剩余 8", "wait"),
    ], [(0, 1, "A"), (1, 2, "B"), (2, 3, "C")], (3, 3, "C"),
        "t=3：D 到达，D(8) > C 剩余(2) → C 继续", "D 的剩余时间更长，不能抢占，只能等待")
    srtf_frame(frames, "P4e-SRTF完成", [
        ("A", "17 → 29 完成 · 周转 29 - 0 = 29", "done"),
        ("B", "5 → 9 完成 · 周转 9 - 1 = 8", "done"),
        ("C", "2 → 5 完成 · 周转 5 - 2 = 3", "done"),
        ("D", "9 → 17 完成 · 周转 17 - 3 = 14", "done"),
    ], SRTF_SEGS, None,
        "SRTF 推演完成：C、B、D、A 依次完成", None,
        bottom=[(8.6, "t=5 C 完成（周转 3）；t=9 B 完成（周转 8）", style.C_TEXT, 12, False),
                (4.0, "t=17 D 完成（周转 14）；t=29 A 完成（周转 29）", style.C_TEXT, 12, False)])

    # ---- P5：SRTF 周转 + 带权周转 ----
    fig, ax = style.new_fig(title=TITLE)
    ax.text(28, 46, "周转时间", ha="center", fontsize=13, fontweight="bold", color=style.C_BLUE)
    for y, t in [(40, "A = 29 - 0 = 29"), (34.5, "B = 9 - 1 = 8"),
                 (29, "C = 5 - 2 = 3"), (23.5, "D = 17 - 3 = 14")]:
        ax.text(28, y, t, ha="center", fontsize=13.5, color=style.C_TEXT)
    ax.text(74, 46, "带权周转 = 周转 ÷ 运行时间", ha="center", fontsize=13,
            fontweight="bold", color=style.C_BLUE)
    for y, t in [(40, "A = 29/12 ≈ 2.42"), (34.5, "B = 8/5 = 1.6"),
                 (29, "C = 3/3 = 1.0"), (23.5, "D = 14/8 = 1.75")]:
        ax.text(74, y, t, ha="center", fontsize=13.5, color=style.C_TEXT)
    ax.text(50, 13, "平均周转 = (29 + 8 + 3 + 14) ÷ 4 = 54 ÷ 4 = 13.5",
            ha="center", fontsize=14.5, fontweight="bold", color=style.C_BLUE)
    style.snapshot(fig, frames, "P5-SRTF周转与带权")
    style.hold(fig, frames, style.HOLD_MIN)
    plt.close(fig)

    # ---- P6：结论对比（双甘特并排）----
    fig, ax = style.new_fig(title=TITLE)
    ax.text(50, 51.5, "FCFS 甘特图（平均周转 17.75）", ha="center", fontsize=12.5,
            fontweight="bold", color=style.C_TEXT)
    for s0, s1, name in FCFS_BLOCKS:
        block(ax, s0, s1, FCFS_S, 42, 6, name, "done")
    ticks(ax, [0, 12, 17, 20, 28], FCFS_S, 41.5)
    ax.text(50, 35.5, "SRTF 甘特图（平均周转 13.5）", ha="center", fontsize=12.5,
            fontweight="bold", color=style.C_TEXT)
    for s0, s1, name in SRTF_SEGS:
        block(ax, s0, s1, SRTF_S, 26, 6, name, "done")
    ticks(ax, [0, 1, 2, 5, 9, 17, 29], SRTF_S, 25.5)
    ax.text(50, 17, "SRTF 平均周转更短（13.5 < 17.75）", ha="center",
            fontsize=13.5, fontweight="bold", color=style.C_GREEN)
    ax.text(50, 12, "但 SRTF 中长作业可能长期得不到调度（饥饿）：短作业不断到达时，"
                    "长作业被一再推迟", ha="center", fontsize=11.5, color=style.C_GRAY)
    style.snapshot(fig, frames, "P6-结论对比")
    style.hold(fig, frames, style.TAIL_HOLD)
    plt.close(fig)

    style.save_gif(frames, OUT)


if __name__ == "__main__":
    main()
