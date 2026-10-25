# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》教学动图 2/4：导数的几何意义（割线逼近切线）。

主题：f(x)=x² 上过定点 P(1,1) 的割线随 Q→P 逼近切线，斜率趋于 f′(1)=2。
序列：①曲线 + P 点
      ②Q 依次取 x=3/2/1.5/1.2/1.05（虚线割线 + 右上角斜率读数，各驻留 5 帧）
      ③绿色切线出现（斜率 2，极限位置）
      ④结论 f′(1) = 2：切线的斜率（驻留 16 帧）。
"""
import sys
import numpy as np
import render_utils as ru

SLUG = "derivative-tangent"
OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-%s.gif" % SLUG)

# 动点 Q 的 5 个位置与对应割线斜率（(x²−1)/(x−1) = x+1）
QLIST = [(3.0, "Q(3,9) 割线斜率=4"),
         (2.0, "Q(2,4) 斜率=3"),
         (1.5, "Q(1.5,2.25) 斜率=2.5"),
         (1.2, "Q(1.2,1.44) 斜率=2.2"),
         (1.05, "Q(1.05,1.1025) 斜率=2.05")]


def build_frame(q_idx, show_tangent, show_conclusion):
    """构建一帧画面。

    q_idx: 当前 Q 下标（None 表示只有曲线与 P）；
    show_tangent: 是否显示绿色切线；show_conclusion: 是否显示底部结论。
    """
    fig, ax = ru.new_fig("割线逼近切线：导数的几何意义")
    ax.set_position([0.07, 0.14, 0.90, 0.71])
    ax.set_xlim(0, 3.05)
    ax.set_ylim(0, 10.5)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    # 曲线 y=x²
    xs = np.linspace(0, 3.05, 300)
    ax.plot(xs, xs ** 2, color=ru.C_MAIN, lw=2.4)
    # 定点 P(1,1)
    ax.plot(1, 1, "o", ms=10, color=ru.C_HIGH)
    ax.text(1, 0.55, "P(1,1)", ha="center", va="top",
            fontsize=12, color=ru.C_HIGH)
    # 已离开的 Q 位置：淡灰小点
    if q_idx is not None:
        for i in range(q_idx):
            xv, _ = QLIST[i]
            ax.plot(xv, xv ** 2, "o", ms=6, color=ru.C_DIM)
    if show_tangent:
        # 最后一条割线淡化保留，体现"极限位置"
        ax.plot([1, 1.05], [1, 1.1025], "--", color=ru.C_DIM, lw=1.4, alpha=0.7)
        ax.plot(1.05, 1.1025, "o", ms=6, color=ru.C_DIM)
        # 绿色切线：过 P(1,1)，斜率 2
        xt = np.array([0.51, 3.04])
        ax.plot(xt, 2 * xt - 1, color=ru.C_OK, lw=2.6)
        msg = "割线斜率 → 2（极限位置）"
        msg_color = ru.C_OK
    elif q_idx is not None:
        # 当前割线 P→Q（虚线）与 Q 点
        qx = QLIST[q_idx][0]
        qy = qx ** 2
        ax.plot([1, qx], [1, qy], "--", color=ru.C_HIGH, lw=1.8)
        ax.plot(qx, qy, "o", ms=9, color=ru.C_HIGH)
        msg = QLIST[q_idx][1]
        msg_color = ru.C_HIGH
    else:
        msg = None   # 首帧无割线、无读数
    # 右上角读数（白底圆角框，保证不被曲线视觉压盖）
    if msg is not None:
        ax.text(0.98, 0.955, msg, transform=ax.transAxes, ha="right", va="top",
                fontsize=13, color=msg_color,
                bbox=dict(boxstyle="round,pad=0.35", fc="white",
                          ec=ru.C_DIM, lw=1))
    # 底部结论
    if show_conclusion:
        axc = fig.add_axes([0.0, 0.0, 1.0, 0.08])
        axc.axis("off")
        axc.text(0.5, 0.5, "f′(1) = 2：切线的斜率", ha="center", va="center",
                 fontsize=17, fontweight="bold", color=ru.C_OK)
    return fig


def main():
    ru.set_style()
    gb = ru.GifBuilder(fps=2)
    total = {"qa": 0}

    def snap(fig, n, ctx):
        total["qa"] += ru.qa_figure(fig, ctx)
        gb.add(fig, n=n)

    # 阶段 1：曲线 + P 点
    snap(build_frame(None, False, False), 6, "f0-曲线P")
    # 阶段 2：Q 的 5 个位置（各驻留 5 帧）
    for i in range(5):
        snap(build_frame(i, False, False), 5, "f-q%d" % i)
    # 阶段 3：绿色切线（极限位置）
    snap(build_frame(4, True, False), 6, "f-切线")
    # 阶段 4：结论（驻留 16 帧 = 8 秒）
    snap(build_frame(4, True, True), 16, "f-结论")

    ok = gb.save(OUT)
    ru.export_keyframes(gb, SLUG)
    print("QA 问题总数:", total["qa"])
    if total["qa"] or not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
