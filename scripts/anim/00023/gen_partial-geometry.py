# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》教学动图 3/4：偏导数的几何意义。

主题：曲面 z=x²+y² 上点 (1,1,2) 处沿两个坐标方向的切线斜率，
      用两幅 2D 截线图呈现：
      左图固定 y=1：截线 z=x²+1，∂z/∂x|(1,1) = 2x|(1) = 2；
      右图固定 x=1：截线 z=y²+1，∂z/∂y|(1,1) = 2y|(1) = 2。
序列：①两幅截线 + P 点 → ②左切线 → ③右切线 → ④结论（驻留 16 帧）。
"""
import sys
import numpy as np
import render_utils as ru

SLUG = "partial-geometry"
OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-%s.gif" % SLUG)


def build_frame(stage, show_conclusion):
    """构建一帧画面。

    stage: 0 仅截线+P；1 加左切线与 ∂z/∂x；2 再加右切线与 ∂z/∂y；
    show_conclusion: 是否显示顶部结论行。
    """
    fig, ax = ru.new_fig("")
    ax.axis("off")   # 底板仅承载 suptitle
    fig.suptitle("偏导数的几何意义：沿两个坐标方向的切线斜率",
                 fontsize=16, fontweight="bold", y=0.965)
    # 左右两幅截线图
    ax_l = fig.add_axes([0.05, 0.07, 0.42, 0.70])
    ax_r = fig.add_axes([0.53, 0.07, 0.42, 0.70])
    for a, ttl in ((ax_l, "固定 y=1：截线 z=x²+1"),
                   (ax_r, "固定 x=1：截线 z=y²+1")):
        a.set_xlim(-1.5, 1.5)
        a.set_ylim(0.4, 4.2)
        a.set_xticks([-1, 0, 1])
        a.set_yticks([1, 2, 3, 4])
        a.set_title(ttl, fontsize=13, fontweight="bold", pad=8)
    t = np.linspace(-1.5, 1.5, 300)
    ax_l.plot(t, t ** 2 + 1, color=ru.C_MAIN, lw=2.2)
    ax_r.plot(t, t ** 2 + 1, color=ru.C_MAIN, lw=2.2)
    # 两个截面上的同一点 (1,1,2)：截线上坐标 (1,2)
    for a in (ax_l, ax_r):
        a.plot(1, 2, "o", ms=9, color=ru.C_HIGH)
        a.text(0.55, 2.1, "P(1,2)", ha="center", va="center",
               fontsize=12, color=ru.C_HIGH)
    # 左图切线：z=2x（过 (1,2) 斜率 2），画 x∈[0.45,1.5] 避开底部公式文字
    if stage >= 1:
        xs = np.array([0.45, 1.5])
        ax_l.plot(xs, 2 * xs, color=ru.C_OK, lw=2.4)
        ax_l.text(0, 0.70, "∂z/∂x|(1,1) = 2x|(1) = 2",
                  ha="center", va="center", fontsize=12, color=ru.C_OK)
    # 右图切线：z=2y（过 (1,2) 斜率 2）
    if stage >= 2:
        ys = np.array([0.45, 1.5])
        ax_r.plot(ys, 2 * ys, color=ru.C_OK, lw=2.4)
        ax_r.text(0, 0.70, "∂z/∂y|(1,1) = 2y|(1) = 2",
                  ha="center", va="center", fontsize=12, color=ru.C_OK)
    # 顶部结论行（总标题下方、两子图标题上方的独立区）
    if show_conclusion:
        axc = fig.add_axes([0.0, 0.845, 1.0, 0.055])
        axc.axis("off")
        axc.text(0.5, 0.55, "偏导数 = 把另一个变量看成常数后的一元导数",
                 ha="center", va="center", fontsize=15,
                 fontweight="bold", color=ru.C_OK)
    return fig


def main():
    ru.set_style()
    gb = ru.GifBuilder(fps=2)
    total = {"qa": 0}

    def snap(fig, n, ctx):
        total["qa"] += ru.qa_figure(fig, ctx)
        gb.add(fig, n=n)

    # 阶段 1：两幅截线 + P 点
    snap(build_frame(0, False), 6, "f0-截线")
    # 阶段 2：左图切线 + ∂z/∂x
    snap(build_frame(1, False), 6, "f1-左切线")
    # 阶段 3：右图切线 + ∂z/∂y
    snap(build_frame(2, False), 6, "f2-右切线")
    # 阶段 4：结论（驻留 16 帧 = 8 秒）
    snap(build_frame(2, True), 16, "f-结论")

    ok = gb.save(OUT)
    ru.export_keyframes(gb, SLUG)
    print("QA 问题总数:", total["qa"])
    if total["qa"] or not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
