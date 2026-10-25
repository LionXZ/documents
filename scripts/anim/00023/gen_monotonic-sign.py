# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》教学动图 4/4：导数符号决定单调性。

主题：f(x)=x³-3x（f′(x)=3x²-3）的分段单调性与极值。
序列：①曲线 + 驻点虚线 → ②[-2.5,-1] 染绿上升 → ③[-1,1] 染红下降
      → ④[1,2.5] 染绿上升 → ⑤驻点处短切线 + 标注
      → ⑥结论（驻留 16 帧）。
"""
import sys
import numpy as np
import render_utils as ru

SLUG = "monotonic-sign"
OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-%s.gif" % SLUG)


def f(x):
    """f(x)=x³-3x。"""
    return x ** 3 - 3 * x


def build_frame(stage, show_conclusion):
    """构建一帧画面。

    stage: 0 曲线；1 加左绿段；2 加中红段；3 加右绿段；
           4 加驻点短切线与标注；show_conclusion: 底部结论。
    """
    fig, ax = ru.new_fig("导数符号决定单调性：f(x)=x³-3x，f′(x)=3x²-3")
    ax.set_position([0.07, 0.13, 0.90, 0.73])
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-4, 4)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_yticks([-4, -2, 0, 2, 4])
    ax.axhline(0, color=ru.C_DIM, lw=0.8)
    # 曲线本体（超出 y 范围由画布裁剪）
    xs = np.linspace(-2.5, 2.5, 500)
    ax.plot(xs, f(xs), color=ru.C_MAIN, lw=2.0)
    # 驻点虚线：曲线点到 x 轴
    for x0, y0 in ((-1, 2), (1, -2)):
        ax.plot([x0, x0], [0, y0], "--", color=ru.C_DIM, lw=1.2)
    # 阶段 2：区间 [-2.5,-1] 染绿 + 上坡箭头 + 文字
    if stage >= 1:
        m = (xs >= -2.5) & (xs <= -1)
        ax.plot(xs[m], f(xs[m]), color=ru.C_OK, lw=3.8,
                solid_capstyle="round")
        ax.annotate("", xy=(-1.5, 1.25), xytext=(-2.25, -2.6),
                    arrowprops=dict(arrowstyle="-|>", color=ru.C_OK, lw=2.4))
        ax.text(-2.05, 2.9, "f′>0：上升", ha="center", va="center",
                fontsize=12, color=ru.C_OK)
    # 阶段 3：区间 [-1,1] 染红 + 下坡箭头 + 文字
    if stage >= 2:
        m = (xs >= -1) & (xs <= 1)
        ax.plot(xs[m], f(xs[m]), color=ru.C_HIGH, lw=3.8,
                solid_capstyle="round")
        ax.annotate("", xy=(0.7, -1.25), xytext=(-0.7, 1.25),
                    arrowprops=dict(arrowstyle="-|>", color=ru.C_HIGH, lw=2.4))
        ax.text(0, 2.9, "f′<0：下降", ha="center", va="center",
                fontsize=12, color=ru.C_HIGH)
    # 阶段 4：区间 [1,2.5] 染绿 + 上坡箭头 + 文字
    if stage >= 3:
        m = (xs >= 1) & (xs <= 2.5)
        ax.plot(xs[m], f(xs[m]), color=ru.C_OK, lw=3.8,
                solid_capstyle="round")
        ax.annotate("", xy=(2.15, 1.9), xytext=(1.6, -1.9),
                    arrowprops=dict(arrowstyle="-|>", color=ru.C_OK, lw=2.4))
        ax.text(2.0, -2.9, "f′>0：上升", ha="center", va="center",
                fontsize=12, color=ru.C_OK)
    # 阶段 5：驻点处水平短切线 + 标注 f′=0
    if stage >= 4:
        ax.plot([-1.45, -0.55], [2, 2], color=ru.C_OK, lw=2.4)
        ax.plot([0.55, 1.45], [-2, -2], color=ru.C_OK, lw=2.4)
        ax.text(-1.55, 2.5, "f′=0 驻点", ha="center", va="center",
                fontsize=12, color=ru.C_HIGH)
        ax.text(1.55, -2.5, "f′=0 驻点", ha="center", va="center",
                fontsize=12, color=ru.C_HIGH)
    # 底部结论
    if show_conclusion:
        axc = fig.add_axes([0.0, 0.0, 1.0, 0.10])
        axc.axis("off")
        axc.text(0.5, 0.5,
                 "f′>0 单调增；f′<0 单调减；驻点两侧变号才取极值（x=-1 极大，x=1 极小）",
                 ha="center", va="center", fontsize=13.5,
                 fontweight="bold", color=ru.C_OK)
    return fig


def main():
    ru.set_style()
    gb = ru.GifBuilder(fps=2)
    total = {"qa": 0}

    def snap(fig, n, ctx):
        total["qa"] += ru.qa_figure(fig, ctx)
        gb.add(fig, n=n)

    # 阶段 1：曲线 + 驻点虚线
    snap(build_frame(0, False), 6, "f0-曲线")
    # 阶段 2~4：三个区间依次染色
    snap(build_frame(1, False), 6, "f1-左绿")
    snap(build_frame(2, False), 6, "f2-中红")
    snap(build_frame(3, False), 6, "f3-右绿")
    # 阶段 5：驻点短切线 + 标注
    snap(build_frame(4, False), 6, "f4-驻点")
    # 阶段 6：结论（驻留 16 帧 = 8 秒）
    snap(build_frame(4, True), 16, "f-结论")

    ok = gb.save(OUT)
    ru.export_keyframes(gb, SLUG)
    print("QA 问题总数:", total["qa"])
    if total["qa"] or not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
