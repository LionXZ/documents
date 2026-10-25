# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》教学动图 1/4：极限的逼近过程。

主题：x→0 时 sinx/x 动态趋近 1（重要极限）。
序列：①曲线 + (0,1) 空心圈（0/0 无定义）
      ②右侧数值表出现表头
      ③逐行填入 x=0.5/0.2/0.1/0.05（每行 2 帧高亮 + 2 帧停留）
      ④动点沿曲线从 x=1.5 滑向 x=0.05（3 个子画面）
      ⑤结论 lim(x→0) sinx/x = 1（驻留 16 帧）。
"""
import sys
import numpy as np
import render_utils as ru

SLUG = "limit-sinx-over-x"
OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-%s.gif" % SLUG)

# 数值表数据（x 从大到小逼近 0，数值与文档一致）
TABLE = [(0.5, 0.9589), (0.2, 0.9933), (0.1, 0.9983), (0.05, 0.9996)]
# 动点滑动的 3 个子画面位置（x 从 1.5 滑向 0.05）
DOT_XS = [1.5, 0.4, 0.05]


def sx(x):
    """sinx/x。"""
    return np.sin(x) / x


def build_frame(rows, hi_row, dot_x, show_table, show_conclusion):
    """构建一帧画面。

    rows: 数值表已填行数；hi_row: 高亮行下标（无则 None）；
    dot_x: 动点横坐标（无则 None）；show_table: 是否显示右侧数值表；
    show_conclusion: 是否显示底部结论。
    """
    fig, ax = ru.new_fig("极限的逼近：sinx/x 当 x→0")
    ax.set_position([0.06, 0.14, 0.52, 0.74])
    ax.set_xlim(-3.3, 3.3)
    ax.set_ylim(0, 1.45)
    ax.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    ax.set_yticks([0, 0.5, 1])
    # 水平虚线 y=1（极限值）
    ax.axhline(1, color=ru.C_DIM, ls="--", lw=1.2)
    # 曲线 y=sinx/x，挖掉 x=0
    xl = np.linspace(-3, -0.004, 300)
    xr = np.linspace(0.004, 3, 300)
    ax.plot(xl, sx(xl), color=ru.C_MAIN, lw=2.2)
    ax.plot(xr, sx(xr), color=ru.C_MAIN, lw=2.2)
    # (0,1) 空心圈：x=0 处 0/0 未定义
    ax.plot(0, 1, "o", ms=10, mfc="none", mec=ru.C_HIGH, mew=1.8)
    ax.annotate("(0,0) 处 0/0 无定义", xy=(0.02, 1.04), xytext=(0.35, 1.24),
                fontsize=12, color=ru.C_HIGH,
                arrowprops=dict(arrowstyle="->", color=ru.C_HIGH, lw=1.2))
    # 已填行在曲线上的联动标记点
    for i in range(rows):
        xv, yv = TABLE[i]
        ax.plot(xv, yv, "o", ms=7, color=ru.C_MAIN)
    # 动点（沿曲线滑向 0）
    if dot_x is not None:
        dy = sx(dot_x)
        ax.plot(dot_x, dy, "o", ms=11, color=ru.C_HIGH)
        ax.text(dot_x, dy - 0.20, "x=%g" % dot_x, ha="center", va="top",
                fontsize=12, color=ru.C_HIGH)
    # 底部结论
    if show_conclusion:
        axc = fig.add_axes([0.0, 0.0, 1.0, 0.08])
        axc.axis("off")
        axc.text(0.5, 0.5, "lim(x→0) sinx/x = 1（重要极限）",
                 ha="center", va="center", fontsize=17,
                 fontweight="bold", color=ru.C_OK)
    # 右侧数值表
    if show_table:
        ax2 = fig.add_axes([0.60, 0.14, 0.37, 0.74])
        ax2.axis("off")
        ax2.set_xlim(0, 10)
        ax2.set_ylim(0, 10)
        ax2.text(5, 9.6, "数值表（x → 0）", ha="center", va="center",
                 fontsize=13, fontweight="bold")
        ax2.text(3.6, 8.7, "x", ha="center", va="center",
                 fontsize=13, fontweight="bold")
        ax2.text(6.4, 8.7, "sinx/x", ha="center", va="center",
                 fontsize=13, fontweight="bold")
        ax2.plot([2.2, 7.8], [8.15, 8.15], color=ru.C_DIM, lw=1)
        ax2.plot([4.9, 4.9], [2.9, 9.2], color=ru.C_DIM, lw=0.8, alpha=0.6)
        # 逐行填入（行距 1.2 数据单位 ≥ 0.8）
        for i in range(rows):
            xv, yv = TABLE[i]
            yy = 7.5 - 1.2 * i
            if i == hi_row:   # 高亮帧：黄色圆角底 + 红框
                bb = dict(boxstyle="round,pad=0.3", fc=ru.C_MARK,
                          ec=ru.C_HIGH, lw=1.4)
            else:             # 停留帧：无底色
                bb = None
            ax2.text(4.3, yy, "%g" % xv, ha="right", va="center",
                     fontsize=13, bbox=bb)
            ax2.text(5.5, yy, "%.4f" % yv, ha="left", va="center",
                     fontsize=13, bbox=bb)
        ax2.text(5, 2.2, "x 越小，sinx/x 越接近 1", ha="center", va="center",
                 fontsize=12, color="#7a8a99")
    return fig


def main():
    ru.set_style()
    gb = ru.GifBuilder(fps=2)
    total = {"qa": 0}

    def snap(fig, n, ctx):
        """QA 通过后收帧；有问题则累计（脚本退出码非 0）。"""
        total["qa"] += ru.qa_figure(fig, ctx)
        gb.add(fig, n=n)

    # 阶段 1：曲线 + 未定义点标注
    snap(build_frame(0, None, None, False, False), 6, "f0-曲线")
    # 阶段 2：数值表表头
    snap(build_frame(0, None, None, True, False), 4, "f1-表头")
    # 阶段 3：逐行填入（每行 2 帧高亮 + 2 帧停留）
    for i in range(4):
        snap(build_frame(i + 1, i, None, True, False), 2, "f-row%d-hi" % i)
        snap(build_frame(i + 1, None, None, True, False), 2, "f-row%d-hold" % i)
    # 阶段 4：动点沿曲线滑向 0（3 个子画面）
    for dx in DOT_XS:
        snap(build_frame(4, None, dx, True, False), 3, "f-dot-%g" % dx)
    # 阶段 5：结论（尾帧驻留 16 帧 = 8 秒）
    snap(build_frame(4, None, None, True, True), 16, "f-结论")

    ok = gb.save(OUT)
    ru.export_keyframes(gb, SLUG)
    print("QA 问题总数:", total["qa"])
    if total["qa"] or not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
