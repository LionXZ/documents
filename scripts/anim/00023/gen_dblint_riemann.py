# -*- coding: utf-8 -*-
"""定积分 = 曲边梯形面积（矩形细分逼近）→ 二重积分同一思想 动图脚本。

画面：y = x²（x∈[0,1]）与 x 轴之间的曲边梯形，用统一右端点高度的矩形逼近。
矩形和公式验证：S_n = (1/n³)∑i² = n(n+1)(2n+1)/(6n³)
    n=4: 180/384   = 0.4688
    n=8: 1224/3072 = 0.3984
    n=16: 8976/24576 = 0.3652
    n=32: 68640/196608 = 0.3491
节奏（fps=2）：6 个画面，驻留 6/6/6/6/6/16 帧。
"""
import sys
import render_utils

SLUG = "dblint-riemann"
OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/高等数学工本/images/calc-anim-dblint-riemann.gif"

TITLE = "定积分 = 曲边梯形面积（矩形细分逼近）"
# 右端点矩形和精确值（n, 四舍五入 4 位显示值）
SUMS = {4: 0.4688, 8: 0.3984, 16: 0.3652, 32: 0.3491}


def rect_sum(n):
    """右端点矩形和 S_n = n(n+1)(2n+1)/(6n³)，并校验与规定值一致。"""
    val = n * (n + 1) * (2 * n + 1) / (6.0 * n ** 3)
    assert abs(round(val, 4) - SUMS[n]) < 1e-9, f"n={n} 矩形和 {val} 与规定值不符"
    return val


def base_axes():
    """画布 + 坐标系 + 曲线 y=x²（每帧公共部分）。"""
    fig, ax = render_utils.new_fig(TITLE)
    ax.set_xlim(-0.06, 1.62)
    ax.set_ylim(-0.16, 1.58)
    # 曲线与底边
    xs = [i / 200 for i in range(201)]
    ax.plot(xs, [x * x for x in xs], color=render_utils.C_MAIN, lw=3, zorder=3)
    ax.plot([0, 1], [0, 0], color="#4a5568", lw=1.6, zorder=2)
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_yticks([0.5, 1.0])
    ax.tick_params(labelsize=10)
    # 顶部步骤行（F1~F5 共用，居中于左半区，避免与右上文字块重叠）
    ax.text(0.44, 1.44, "分割 → 近似 → 求和 → 取极限",
            ha="center", va="center", fontsize=14.5, color="#4a5568")
    return fig, ax


def add_rects(ax, n, alpha_f=0.35):
    """右端点高度的 n 个矩形（半透明蓝）。"""
    for i in range(1, n + 1):
        h = (i / n) ** 2
        ax.bar((i - 0.5) / n, h, width=1.0 / n, align="center",
               color=render_utils.C_MAIN, alpha=alpha_f,
               edgecolor="#2c5282", linewidth=0.5, zorder=2)


def main():
    render_utils.set_style()
    gb = render_utils.GifBuilder(fps=2)
    rect_sum(4); rect_sum(8); rect_sum(16); rect_sum(32)  # 先跑数值校验

    # ---------- 帧① 曲线 + 步骤行 + 面积标签（驻留 6） ----------
    fig, ax = base_axes()
    ax.text(0.50, 0.62, "曲边梯形面积 =", ha="center", va="center",
            fontsize=15, color="#2d3748")
    ax.text(0.50, 0.40, r"$\int_0^1 x^2\,dx=\frac{1}{3}$",
            ha="center", va="center", fontsize=16, color=render_utils.C_MAIN)
    if render_utils.qa_figure(fig, f"{SLUG} F1"):
        plt_close_exit(fig)
    gb.add(fig, n=6)

    # ---------- 帧②~⑤ n = 4 / 8 / 16 / 32（各驻留 6） ----------
    for k, n in enumerate([4, 8, 16, 32]):
        fig, ax = base_axes()
        add_rects(ax, n)
        ax.text(1.05, 1.34, f"n={n} 个矩形", ha="left", va="center",
                fontsize=15, color=render_utils.C_MAIN, fontweight="bold")
        ax.text(1.05, 1.10, f"矩形和 S = {SUMS[n]:.4f}", ha="left", va="center",
                fontsize=14, color="#2d3748")
        if render_utils.qa_figure(fig, f"{SLUG} F{n}-矩形"):
            plt_close_exit(fig)
        gb.add(fig, n=6)

    # ---------- 帧⑥ 结论（驻留 16，保留 n=32 矩形淡化） ----------
    fig, ax = base_axes()
    add_rects(ax, 32, alpha_f=0.22)
    lines = [
        (1.34, "矩形越来越贴合曲线", render_utils.C_MAIN, "bold", 15),
        (1.10, "→ 面积趋近 1/3", render_utils.C_OK, "bold", 15),
        (0.86, "二重积分 = 曲顶柱体体积", "#2d3748", "normal", 14),
        (0.62, "同一思想", render_utils.C_OK, "bold", 15),
    ]
    for y, s, c, w, fs in lines:
        ax.text(1.05, y, s, ha="left", va="center", fontsize=fs, color=c,
                fontweight=w)
    if render_utils.qa_figure(fig, f"{SLUG} F6-结论"):
        plt_close_exit(fig)
    gb.add(fig, n=16)

    ok = gb.save(OUT)
    render_utils.export_keyframes(gb, SLUG)
    print(f"[完成] {SLUG}: {'通过' if ok else '超限需修'}")


def plt_close_exit(fig):
    plt_close = None
    import matplotlib.pyplot as plt
    plt.close(fig)
    sys.exit("QA 存在越界/重叠，请调整布局后重跑")


if __name__ == "__main__":
    main()
