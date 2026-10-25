# -*- coding: utf-8 -*-
"""极坐标换元教学动图：面积微元 dA = r·dr·dθ 的来历（dxdy → r dr dθ）。

画面：左图为圆域 D（半径 1.6）+ 极坐标网格（同心圆 r=0.4/0.8/1.2/1.6，射线每 30°）；
高亮小扇环微元（r∈[0.8,1.0]，θ∈[45°,60°]），径向边红色、切向边绿色；
右侧文字区给出换元要点与公式。
节奏（fps=2）：网格 6 → 扇环 6 → 微元标注 8 → 换元公式 6 → 结论 16。
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import render_utils

SLUG = "polar-substitution"
OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/高等数学工本/images/calc-anim-polar-substitution.gif"

TITLE = "极坐标换元：面积微元 dA = r·dr·dθ"
R_MAX = 1.6
TH1, TH2 = 45.0, 60.0   # 扇环角度范围（度）
R0, R1 = 0.8, 1.0       # 扇环半径范围


def left_axes(fig):
    """左侧极坐标图（正方形等比、无刻度）。"""
    axL = fig.add_axes([0.05, 0.06, 0.42, 0.78])
    axL.set_aspect("equal")
    axL.set_xlim(-2.05, 2.05)
    axL.set_ylim(-2.05, 2.05)
    axL.axis("off")
    return axL


def draw_grid(axL):
    """同心圆网格 + 每 30° 一条射线 + 外圆加粗。"""
    # 内部同心圆（灰虚线）
    for r in (0.4, 0.8, 1.2):
        axL.add_artist(plt.Circle((0, 0), r, fill=False, ls="--",
                                  ec="#a0aec0", lw=1.0, zorder=1))
    # 射线
    for deg in range(0, 360, 30):
        t = np.deg2rad(deg)
        axL.plot([0, R_MAX * np.cos(t)], [0, R_MAX * np.sin(t)],
                 color="#cbd5e0", lw=0.9, zorder=1)
    # 外圆（蓝粗）
    axL.add_artist(plt.Circle((0, 0), R_MAX, fill=False,
                              ec=render_utils.C_MAIN, lw=3.0, zorder=3))
    axL.plot(0, 0, marker="o", ms=4, color="#4a5568", zorder=4)


def wedge_patch(color, ec, lw=1.5, alpha=1.0):
    """小扇环微元（r∈[R0,R1]，θ∈[TH1,TH2]）。"""
    return Wedge((0, 0), R1, TH1, TH2, width=R1 - R0,
                 facecolor=color, edgecolor=ec, lw=lw, alpha=alpha, zorder=5)


def right_text(fig, ax):
    """右侧文字区改造为 axis off 的 0~1 相对坐标区。"""
    ax.set_position([0.52, 0.05, 0.45, 0.80])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return ax


def qa_or_die(fig, tag):
    """QA 机检：有任何越界/重叠直接终止。"""
    if render_utils.qa_figure(fig, f"{SLUG} {tag}"):
        plt.close(fig)
        sys.exit("QA 存在越界/重叠，请调整布局后重跑")


def main():
    render_utils.set_style()
    gb = render_utils.GifBuilder(fps=2)

    # ---------- 帧① 圆 + 极坐标网格（驻留 6） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_grid(axL)
    ax.text(0.06, 0.90, "同心圆：r = 0.4 / 0.8 / 1.2 / 1.6",
            ha="left", va="center", fontsize=13.5, color="#2d3748")
    ax.text(0.06, 0.76, "射线：每 30° 一条", ha="left", va="center",
            fontsize=13.5, color="#2d3748")
    qa_or_die(fig, "F1-网格")
    gb.add(fig, n=6)

    # ---------- 帧② 高亮小扇环（驻留 6） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_grid(axL)
    axL.add_patch(wedge_patch(render_utils.C_MARK, "#b7791f"))
    ax.text(0.06, 0.90, "小扇环：内外弧长差很小，近似矩形",
            ha="left", va="center", fontsize=13.5, color="#2d3748")
    qa_or_die(fig, "F2-扇环")
    gb.add(fig, n=6)

    # ---------- 帧③ 径向边/切向边标注 + dA 公式（驻留 8） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_grid(axL)
    axL.add_patch(wedge_patch(render_utils.C_MARK, "#b7791f"))
    # 径向边（红粗）：θ = TH1 与 TH2 两条线段
    for deg in (TH1, TH2):
        t = np.deg2rad(deg)
        axL.plot([R0 * np.cos(t), R1 * np.cos(t)],
                 [R0 * np.sin(t), R1 * np.sin(t)],
                 color=render_utils.C_HIGH, lw=3.0, zorder=6)
    # 切向边（绿粗）：r = R0 与 R1 两段弧
    ts = np.deg2rad(np.linspace(TH1, TH2, 40))
    for r in (R0, R1):
        axL.plot(r * np.cos(ts), r * np.sin(ts),
                 color=render_utils.C_OK, lw=3.0, zorder=6)
    ax.text(0.06, 0.90, "径向边 = dr（半径方向小段）", ha="left",
            va="center", fontsize=13.5, color=render_utils.C_HIGH)
    ax.text(0.06, 0.76, "切向边 = r·dθ（小弧长）", ha="left",
            va="center", fontsize=13.5, color=render_utils.C_OK)
    ax.text(0.06, 0.56, "dA = dr × r dθ = r dr dθ", ha="left", va="center",
            fontsize=15.5, color="#2d3748", fontweight="bold")
    qa_or_die(fig, "F3-微元")
    gb.add(fig, n=8)

    # ---------- 帧④ 换元要点三行（驻留 6） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_grid(axL)
    axL.add_patch(wedge_patch(render_utils.C_MARK, "#b7791f", alpha=0.55))
    ax.text(0.06, 0.92, r"$x = r\cos\theta$", ha="left", va="center",
            fontsize=14.5, color="#2d3748")
    ax.text(0.06, 0.79, r"$y = r\sin\theta$", ha="left", va="center",
            fontsize=14.5, color="#2d3748")
    ax.text(0.06, 0.62, r"$\iint_D f(x,y)\,dxdy$", ha="left", va="center",
            fontsize=14.5, color=render_utils.C_MAIN)
    ax.text(0.06, 0.44,
            r"$=\ \iint f(r\cos\theta,\, r\sin\theta)\cdot r\,dr\,d\theta$",
            ha="left", va="center", fontsize=14.5, color=render_utils.C_MAIN)
    qa_or_die(fig, "F4-换元")
    gb.add(fig, n=6)

    # ---------- 帧⑤ 结论大字（驻留 16） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_grid(axL)
    axL.add_patch(wedge_patch(render_utils.C_MARK, "#b7791f", alpha=0.55))
    ax.text(0.06, 0.66, "圆域/扇形域优先用极坐标", ha="left", va="center",
            fontsize=18.5, color=render_utils.C_OK, fontweight="bold")
    ax.text(0.06, 0.42, "别忘乘 r！", ha="left", va="center",
            fontsize=18.5, color=render_utils.C_OK, fontweight="bold")
    qa_or_die(fig, "F5-结论")
    gb.add(fig, n=16)

    ok = gb.save(OUT)
    render_utils.export_keyframes(gb, SLUG)
    print(f"[完成] {SLUG}: {'通过' if ok else '超限需修'}")


if __name__ == "__main__":
    main()
