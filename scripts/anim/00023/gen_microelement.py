# -*- coding: utf-8 -*-
"""微元法教学动图：先取一条窄条（dA ≈ f(x)·dx），再把所有窄条积分累加。

画面：y = x² + 0.5（x∈[0,2]）下方的曲边梯形。
验算：∫₀² x² dx = 8/3，∫₀² 0.5 dx = 1，合计 8/3 + 1 = 11/3 ≈ 3.6667。
节奏（fps=2）：标题与轮廓 6 → 窄条特写 6 → 窄条滑动 3×5 → 全域累加 8 → 结论 16。
"""
import sys
import matplotlib.pyplot as plt
import render_utils

SLUG = "microelement"
OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/高等数学工本/images/calc-anim-microelement.gif"

TITLE = "微元法：先取一条窄条，再把所有窄条累加"
DX = 0.12  # 窄条宽度（示意用夸张宽度，便于看清）


def f(x):
    """被积函数 f(x) = x² + 0.5。"""
    return x * x + 0.5


def base_axes():
    """画布 + 坐标系 + 曲线与区域轮廓（每帧公共部分）。"""
    fig, ax = render_utils.new_fig(TITLE)
    ax.set_xlim(-0.15, 3.0)
    ax.set_ylim(-0.45, 5.9)
    xs = [i / 200 for i in range(401)]
    ax.plot(xs, [f(x) for x in xs], color=render_utils.C_MAIN, lw=3, zorder=3)
    # 区域轮廓：底边 + 右边线（左边线与 y 轴重合）
    ax.plot([0, 2], [0, 0], color="#4a5568", lw=1.6, zorder=2)
    ax.plot([2, 2], [0, f(2)], color="#4a5568", lw=1.6, zorder=2)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([1, 2, 3, 4])
    ax.tick_params(labelsize=10)
    return fig, ax


def strip(ax, x0):
    """在 [x0, x0+DX] 画黄色高亮窄条。"""
    ax.bar(x0 + DX / 2, f(x0 + DX), width=DX, align="center",
           color=render_utils.C_MARK, alpha=0.95,
           edgecolor="#b7791f", linewidth=1.2, zorder=4)


def qa_or_die(fig, tag):
    """QA 机检：有任何越界/重叠直接终止，修完布局再跑。"""
    if render_utils.qa_figure(fig, f"{SLUG} {tag}"):
        plt.close(fig)
        sys.exit("QA 存在越界/重叠，请调整布局后重跑")


def main():
    render_utils.set_style()
    gb = render_utils.GifBuilder(fps=2)

    # ---------- 帧① 曲线 + 区域轮廓（驻留 6） ----------
    fig, ax = base_axes()
    ax.text(1.55, 1.5, "曲边梯形", ha="center", va="center",
            fontsize=15, color="#4a5568")
    qa_or_die(fig, "F1-轮廓")
    gb.add(fig, n=6)

    # ---------- 帧② x=0.5 窄条特写 + dA 标注（驻留 6） ----------
    fig, ax = base_axes()
    strip(ax, 0.5)
    ax.text(-0.05, 5.35, "窄条面积 dA ≈ f(x)·dx", ha="left", va="center",
            fontsize=14, color="#2d3748")
    ax.annotate("", xy=(0.56, 1.05), xytext=(0.30, 5.05),
                arrowprops=dict(arrowstyle="->", color="#b7791f", lw=1.6))
    qa_or_die(fig, "F2-窄条")
    gb.add(fig, n=6)

    # ---------- 帧③ 窄条滑动 x = 1.0 / 1.5 / 1.88（各驻留 5，旧位置清除） ----------
    for x0 in (1.0, 1.5, 1.88):
        fig, ax = base_axes()
        strip(ax, x0)
        ax.text(-0.05, 5.35, "窄条面积 dA ≈ f(x)·dx", ha="left", va="center",
                fontsize=14, color="#2d3748")
        ax.text(-0.05, 4.80, f"当前 x = {x0:.2f}", ha="left", va="center",
                fontsize=14, color=render_utils.C_HIGH)
        qa_or_die(fig, f"F3-滑动{x0}")
        gb.add(fig, n=5)

    # ---------- 帧④ 全域淡蓝填充 + 积分式（驻留 8） ----------
    fig, ax = base_axes()
    xs = [i / 400 for i in range(801)]
    ax.fill_between(xs, 0, [f(x) for x in xs], color=render_utils.C_MAIN,
                    alpha=0.28, zorder=1)
    ax.text(-0.05, 5.35, "全部窄条累加：", ha="left", va="center",
            fontsize=14, color="#2d3748")
    ax.text(-0.05, 4.80, r"$A=\int_0^2 (x^2+0.5)\,dx=\frac{11}{3}$",
            ha="left", va="center", fontsize=15, color=render_utils.C_MAIN)
    ax.text(-0.05, 4.15, "验算：x² 积 8/3，0.5 积 1，合计 11/3 = 3.6667",
            ha="left", va="center", fontsize=13, color="#4a5568")
    qa_or_die(fig, "F4-累加")
    gb.add(fig, n=8)

    # ---------- 帧⑤ 结论（驻留 16，保留累加画面） ----------
    fig, ax = base_axes()
    ax.fill_between(xs, 0, [f(x) for x in xs], color=render_utils.C_MAIN,
                    alpha=0.28, zorder=1)
    ax.text(-0.05, 5.35, r"$A=\int_0^2 (x^2+0.5)\,dx=\frac{11}{3}$",
            ha="left", va="center", fontsize=15, color=render_utils.C_MAIN)
    steps = [
        (2.6, "微元法三步：", "bold", 15.5),
        (2.0, "取微元 → 写 dA", "normal", 14.5),
        (1.4, "→ 积分累加", "normal", 14.5),
    ]
    for y, s, w, fs in steps:
        ax.text(2.06, y, s, ha="left", va="center", fontsize=fs,
                color=render_utils.C_OK if w == "bold" else "#2d3748",
                fontweight=w)
    qa_or_die(fig, "F5-结论")
    gb.add(fig, n=16)

    ok = gb.save(OUT)
    render_utils.export_keyframes(gb, SLUG)
    print(f"[完成] {SLUG}: {'通过' if ok else '超限需修'}")


if __name__ == "__main__":
    main()
