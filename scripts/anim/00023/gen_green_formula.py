# -*- coding: utf-8 -*-
"""格林公式教学动图：闭曲线积分 = 区域二重积分（∮ vs ∬ 的转化）。

画面：左图为圆 L（圆心 (1.2,1)，半径 1，蓝粗线）+ 内部区域 D 淡红填充，
圆上出现逆时针正向箭头；右侧文字区给出公式、条件与本课程真题考法。
节奏（fps=2）：圆与区域 6 → 正向箭头 3×2 → 公式 8 → 考法 6 → 结论 16。
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import render_utils

SLUG = "green-formula"
OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/高等数学工本/images/calc-anim-green-formula.gif"

TITLE = "格林公式：闭路线积分 = 区域二重积分"
CX, CY, R = 1.2, 1.0, 1.0   # 圆 L 参数


def left_axes(fig):
    """左侧圆域图（等比、无刻度）。"""
    axL = fig.add_axes([0.05, 0.06, 0.42, 0.78])
    axL.set_aspect("equal")
    axL.set_xlim(-0.4, 2.8)
    axL.set_ylim(-0.5, 2.5)
    axL.axis("off")
    return axL


def draw_circle(axL):
    """区域 D 淡红填充 + 圆 L 蓝粗线 + D/L 标记。"""
    t = np.linspace(0, 2 * np.pi, 200)
    axL.fill(CX + R * np.cos(t), CY + R * np.sin(t),
             color="#fc8181", alpha=0.25, zorder=1)
    axL.plot(CX + R * np.cos(t), CY + R * np.sin(t),
             color=render_utils.C_MAIN, lw=3.2, zorder=3)
    axL.text(CX, CY, "D", ha="center", va="center", fontsize=20,
             color="#c53030", fontweight="bold")
    axL.text(CX + 1.12, CY + 0.95, "L", ha="left", va="center",
             fontsize=17, color=render_utils.C_MAIN, fontweight="bold")


def ccw_arrow(axL, deg):
    """圆上 deg 处画一个逆时针切向箭头（正向：区域在左手边）。"""
    t = np.deg2rad(deg)
    x, y = CX + R * np.cos(t), CY + R * np.sin(t)
    dx, dy = -np.sin(t), np.cos(t)          # 逆时针单位切向量
    ln = 0.30                                # 箭头长度
    axL.annotate("", xy=(x + ln * dx, y + ln * dy), xytext=(x - ln * dx, y - ln * dy),
                 arrowprops=dict(arrowstyle="-|>", color=render_utils.C_HIGH,
                                 lw=2.6, mutation_scale=22), zorder=5)


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

    # ---------- 帧① 圆 L + 区域 D（驻留 6） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_circle(axL)
    ax.text(0.06, 0.90, "闭曲线 L 包住区域 D", ha="left", va="center",
            fontsize=14, color="#2d3748")
    qa_or_die(fig, "F1-圆域")
    gb.add(fig, n=6)

    # ---------- 帧② 逆时针正向箭头 3 子画面（各驻留 2，累计出现） ----------
    for k, deg in enumerate((90, 210, 330), start=1):
        fig, ax = render_utils.new_fig(TITLE)
        right_text(fig, ax)
        axL = left_axes(fig)
        draw_circle(axL)
        for d in (90, 210, 330)[:k]:
            ccw_arrow(axL, d)
        ax.text(0.06, 0.90, "L 取正向：沿边界走，区域始终在左手边",
                ha="left", va="center", fontsize=13.5, color="#2d3748")
        qa_or_die(fig, f"F2-箭头{k}")
        gb.add(fig, n=2)

    # ---------- 帧③ 格林公式 + 条件（驻留 8） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_circle(axL)
    for d in (90, 210, 330):
        ccw_arrow(axL, d)
    ax.text(0.06, 0.88,
            r"$\oint_L P\,dx + Q\,dy = \iint_D (\frac{\partial Q}{\partial x}"
            r" - \frac{\partial P}{\partial y})\,dxdy$",
            ha="left", va="center", fontsize=13, color=render_utils.C_MAIN)
    ax.text(0.06, 0.68, "条件：P、Q 在 D 内有一阶连续偏导数",
            ha="left", va="center", fontsize=13.5, color="#2d3748")
    qa_or_die(fig, "F3-公式")
    gb.add(fig, n=8)

    # ---------- 帧④ 真题考法一行（驻留 6） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_circle(axL)
    for d in (90, 210, 330):
        ccw_arrow(axL, d)
    ax.text(0.06, 0.88,
            r"$\oint_L P\,dx + Q\,dy = \iint_D (\frac{\partial Q}{\partial x}"
            r" - \frac{\partial P}{\partial y})\,dxdy$",
            ha="left", va="center", fontsize=13, color=render_utils.C_MAIN)
    ax.text(0.06, 0.68, "条件：P、Q 在 D 内有一阶连续偏导数",
            ha="left", va="center", fontsize=13.5, color="#2d3748")
    ax.text(0.06, 0.46, "考法：Qx-Py 常数化 → 圆域极坐标算二重积分",
            ha="left", va="center", fontsize=13.5, color=render_utils.C_HIGH)
    qa_or_die(fig, "F4-考法")
    gb.add(fig, n=6)

    # ---------- 帧⑤ 结论（驻留 16） ----------
    fig, ax = render_utils.new_fig(TITLE)
    right_text(fig, ax)
    axL = left_axes(fig)
    draw_circle(axL)
    for d in (90, 210, 330):
        ccw_arrow(axL, d)
    ax.text(0.06, 0.28, "闭曲线上的线积分不用逐段参数化，",
            ha="left", va="center", fontsize=15.5,
            color=render_utils.C_OK, fontweight="bold")
    ax.text(0.06, 0.10, "转化成二重积分更快", ha="left", va="center",
            fontsize=15.5, color=render_utils.C_OK, fontweight="bold")
    qa_or_die(fig, "F5-结论")
    gb.add(fig, n=16)

    ok = gb.save(OUT)
    render_utils.export_keyframes(gb, SLUG)
    print(f"[完成] {SLUG}: {'通过' if ok else '超限需修'}")


if __name__ == "__main__":
    main()
