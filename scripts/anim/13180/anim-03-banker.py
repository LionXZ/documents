# -*- coding: utf-8 -*-
"""13180《操作系统》动图 03：银行家算法安全性检测（教学示例数据）。

数据：3 类资源总量 (3, 2)；Available=(1,1)。
  P1：Alloc(1,0)  Need(1,1)；P2：Alloc(1,1)  Need(1,1)；P3：Alloc(0,1)  Need(3,1)
分镜：表格 → 逐进程「判定成立 → 回收资源」（每进程两个画面）
      → 安全序列 P1→P2→P3（Available 演变标注）→ 反例：Available=(0,1) 时全部不成立。
QA 由 style.snapshot 内置检测。
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images/os-anim-03-banker.gif"

ROWS = [("P1", "(1, 0)", "(1, 1)"),
        ("P2", "(1, 1)", "(1, 1)"),
        ("P3", "(0, 1)", "(3, 1)")]
COLS = [(4, 14), (14, 36), (36, 58)]      # 进程 / Alloc / Need 的 x 区间
HEADS = ["进程", "已分配 Alloc (A,B)", "尚需 Need (A,B)"]
ROW_Y = [40.5, 35.0, 29.5]                 # 三行的中心 y

BASE = dict(rows=["#FFFFFF"] * 3, row_tc=[style.C_TEXT] * 3,
            avail=(1, 1), acolor=style.C_TEXT,
            judge1=None, judge2=None, jcolor=style.C_TEXT,
            recycle=None, recycle_label=None, seq=False,
            contra=False)


def draw(s):
    fig, ax = style.new_fig(title="银行家算法安全性检测（教学示例数据）")

    # ---- 左侧：进程表格 ----
    ax.add_patch(plt.Rectangle((4, 43.4), 54, 5.2, fc=style.C_LIGHT, ec=style.C_BLUE, lw=1.5))
    for (x0, x1), h in zip(COLS, HEADS):
        ax.text((x0 + x1) / 2, 46.0, h, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color=style.C_BLUE)
    for i, (name, alloc, need) in enumerate(ROWS):
        y = ROW_Y[i]
        ax.add_patch(plt.Rectangle((4, y - 2.6), 54, 5.2,
                                   fc=s["rows"][i], ec=style.C_GRAY, lw=1.2))
        for (x0, x1), v in zip(COLS, (name, alloc, need)):
            ax.text((x0 + x1) / 2, y, v, ha="center", va="center", fontsize=12,
                    fontweight="bold" if s["rows"][i] != "#FFFFFF" else "normal",
                    color=s["row_tc"][i])
    ax.text(4, 25.2, "资源总量 Total = (3, 2)", ha="left", fontsize=11,
            color=style.C_GRAY)

    # ---- 右上：Available 卡片 ----
    ax.add_patch(plt.Rectangle((78, 40), 20, 12, fc="#F7FAFC",
                               ec=s["acolor"], lw=2))
    ax.text(88, 48.5, "Available", ha="center", va="center", fontsize=12,
            fontweight="bold", color=style.C_TEXT)
    ax.text(88, 43.6, f"({s['avail'][0]}, {s['avail'][1]})", ha="center",
            va="center", fontsize=17, fontweight="bold", color=s["acolor"])
    ax.text(88, 36.9, "当前可用资源", ha="center", va="center",
            fontsize=10, color=style.C_GRAY)

    # ---- 回收箭头 ----
    if s["recycle"] is not None:
        y = ROW_Y[s["recycle"]]
        ax.annotate("", xy=(77.5, 42.6), xytext=(58.5, y + 1.2),
                    arrowprops=dict(arrowstyle="-|>", color=style.C_GREEN,
                                    lw=2.5, connectionstyle="arc3,rad=-0.3"))
        ax.text(68, 37.6, s["recycle_label"], ha="center", va="center",
                fontsize=10, fontweight="bold", color=style.C_GREEN)

    # ---- 底部：判定文字 / 安全序列 / 反例 ----
    if s["seq"]:
        seq_x = [16, 40, 64]
        for cx in seq_x:
            ax.add_patch(plt.Rectangle((cx - 6, 9.5), 12, 6.5, fc=style.C_LGREEN,
                                       ec=style.C_GREEN, lw=2))
            ax.text(cx, 12.7, f"P{seq_x.index(cx) + 1}", ha="center", va="center",
                    fontsize=14, fontweight="bold", color=style.C_GREEN)
        for x0, x1 in [(22.5, 33.5), (46.5, 57.5), (70.5, 77.5)]:
            ax.annotate("", xy=(x1, 12.7), xytext=(x0, 12.7),
                        arrowprops=dict(arrowstyle="-|>", color=style.C_GREEN, lw=2.2))
        ax.text(28, 17.9, "可用 (1,1)→(2,1)", ha="center", fontsize=10, color=style.C_GREEN)
        ax.text(52, 17.9, "(2,1)→(3,2)", ha="center", fontsize=10, color=style.C_GREEN)
        ax.text(74, 17.9, "(3,2)", ha="center", fontsize=10, color=style.C_GREEN)
        ax.text(40, 4.2, "存在安全序列 → 系统处于安全状态，本次分配可以实施",
                ha="center", fontsize=13, fontweight="bold", color=style.C_GREEN)
    elif s["contra"]:
        ax.text(40, 15.5, "三个进程的 Need 均无法满足（A 类需 1 / 1 / 3，均 > 可用 0）",
                ha="center", fontsize=12, fontweight="bold", color=style.C_RED)
        ax.text(40, 9.8, "找不到安全序列 → 不安全状态",
                ha="center", fontsize=14, fontweight="bold", color=style.C_RED)
        ax.text(40, 4.2, "不安全状态不一定死锁，但死锁一定处于不安全状态",
                ha="center", fontsize=11.5, color=style.C_ORANGE)
    else:
        if s["judge1"]:
            ax.text(31, 15.5, s["judge1"], ha="center", fontsize=12.5,
                    fontweight="bold", color=s["jcolor"])
        if s["judge2"]:
            ax.text(31, 9.8, s["judge2"], ha="center", fontsize=11.5,
                    color=style.C_GRAY)
    return fig, ax


def main():
    frames = []
    OK, WARN = style.C_LGREEN, style.C_YELLOW
    steps = [
        ("P1-表格与初值",
         dict(judge1="安全性检测：每轮找一个 Need ≤ Available 的进程",
              judge2="找到则假设其先运行完成并回收资源；全部能找完 → 安全")),
        ("P2a-P1判定",
         dict(rows=[WARN, "#FFFFFF", "#FFFFFF"],
              judge1="P1：Need(1,1) ≤ Available(1,1)？  1≤1 且 1≤1 → 成立",
              judge2="Need 不超过可用 → 可以假设 P1 先运行完成")),
        ("P2b-P1回收",
         dict(rows=[OK, "#FFFFFF", "#FFFFFF"], row_tc=[style.C_GREEN, style.C_TEXT, style.C_TEXT],
              avail=(2, 1), acolor=style.C_GREEN, recycle=0,
              recycle_label="回收 Alloc(1,0)：(1,1)+(1,0)=(2,1)",
              judge1="P1 可完成 → 回收其全部已分配资源",
              judge2="为什么可以假设完成：完成的进程最终会归还其全部已分配资源")),
        ("P3a-P2判定",
         dict(rows=[OK, WARN, "#FFFFFF"], row_tc=[style.C_GREEN, style.C_TEXT, style.C_TEXT],
              avail=(2, 1), acolor=style.C_GREEN,
              judge1="P2：Need(1,1) ≤ Available(2,1)？  1≤2 且 1≤1 → 成立",
              judge2="P1 已回收，可用资源变多，P2 的请求可以满足")),
        ("P3b-P2回收",
         dict(rows=[OK, OK, "#FFFFFF"], row_tc=[style.C_GREEN] * 2 + [style.C_TEXT],
              avail=(3, 2), acolor=style.C_GREEN, recycle=1,
              recycle_label="回收 Alloc(1,1)：(2,1)+(1,1)=(3,2)",
              judge1="P2 可完成 → 回收其全部已分配资源",
              judge2="可用资源恢复到总量 (3, 2)")),
        ("P4a-P3判定",
         dict(rows=[OK] * 2 + [WARN], row_tc=[style.C_GREEN] * 2 + [style.C_TEXT],
              avail=(3, 2), acolor=style.C_GREEN,
              judge1="P3：Need(3,1) ≤ Available(3,2)？  3≤3 且 1≤2 → 成立",
              judge2="三个进程都能按序完成")),
        ("P4b-P3回收",
         dict(rows=[OK] * 3, row_tc=[style.C_GREEN] * 3,
              avail=(3, 2), acolor=style.C_GREEN, recycle=2,
              recycle_label="回收 Alloc(0,1)：(3,2)+(0,1)=(3,2)",
              judge1="P3 可完成 → 回收其全部已分配资源",
              judge2="全部进程检查完毕，可以给出安全序列")),
        ("P5-安全序列",
         dict(rows=[OK] * 3, row_tc=[style.C_GREEN] * 3,
              avail=(3, 2), acolor=style.C_GREEN, seq=True)),
        ("P6-反例不安全",
         dict(rows=[style.C_LRED] * 3, row_tc=[style.C_RED] * 3,
              avail=(0, 1), acolor=style.C_RED, contra=True)),
    ]
    for tag, upd in steps:
        s = {**BASE, **upd}
        fig, ax = draw(s)
        style.snapshot(fig, frames, tag)
        style.hold(fig, frames, style.TAIL_HOLD if tag.endswith("不安全") else
                   (8 if tag.endswith("安全序列") else style.HOLD_MIN))
        plt.close(fig)

    style.save_gif(frames, OUT)


if __name__ == "__main__":
    main()
