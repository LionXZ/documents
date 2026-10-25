# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》动图 3：微分方程的解曲线族。

内容：y′=y 的通解 y = C·eˣ 是一族指数曲线（C=-1/0.5/1/2 逐条出现），
     初始条件 y(0)=1 的红点把 C=1 这条特解挑出来（其余变灰虚线）。
节奏（fps=2）：标题 6 -> 4 条曲线逐条各 4 -> 初始条件 6 ->
     C=1 被唯一确定 6 -> 结论大字 16。
"""
import numpy as np
import render_utils

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-ode-family.gif")
SLUG = "ode-family"
TITLE = "微分方程 y′=y 的通解：y = C·eˣ（一族曲线）"

# (C 值, 颜色, 线型)
CS = [(-1.0, "#805ad5", "--"), (0.5, "#dd6b20", "-."),
      (1.0, render_utils.C_OK, "-"), (2.0, render_utils.C_MAIN, ":")]


def frame(n_curves, phase):
    """重建一帧。n_curves=已出现的曲线条数(0~4)；
    phase: family|ic|pick|final。"""
    fig, ax = render_utils.new_fig(TITLE)
    ax.set_position([0.07, 0.26, 0.85, 0.60])
    ax.set_xlim(-2, 2)
    ax.set_ylim(-3, 5)
    ax.set_xticks(range(-2, 3))
    ax.set_yticks(range(-3, 6))
    ax.grid(alpha=0.3, lw=0.6)

    xs = np.linspace(-2, 2, 240)
    if phase in ("pick", "final"):
        # 其余曲线变灰虚线，C=1 加粗高亮
        for c, _, _ in CS:
            if abs(c - 1.0) > 1e-9:
                ax.plot(xs, c * np.exp(xs), color=render_utils.C_DIM,
                        ls="--", lw=1.5, alpha=0.6)
        ax.plot(xs, np.exp(xs), color="#276749", lw=3.5, zorder=5)
    else:
        for c, col, ls in CS[:n_curves]:
            ax.plot(xs, c * np.exp(xs), color=col, ls=ls, lw=2,
                    label=f"C={c:g}", zorder=4)
        if n_curves and phase in ("family", "ic"):
            ax.legend(loc="lower right", fontsize=12, framealpha=0.95)

    # 初始条件红点 + 标注（白底框衬线保证可读）
    if phase in ("ic", "pick", "final"):
        ax.plot([0], [1], "o", ms=11, color=render_utils.C_HIGH,
                mec="white", mew=1.5, zorder=6)
        ax.text(0.15, 1.72, "初始条件 y(0)=1", fontsize=14, ha="left",
                va="bottom", color=render_utils.C_HIGH, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec=render_utils.C_HIGH, alpha=0.9))
    if phase in ("pick", "final"):
        ax.text(-1.85, 4.3, "C=1 被唯一确定", fontsize=15, ha="left",
                va="bottom", color="#276749", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="#e6ffed",
                          ec="#276749", alpha=0.9))

    # 结论大字（底部 axis off 文字区）
    if phase == "final":
        axt = fig.add_axes([0.0, 0.0, 1.0, 0.20])
        axt.set_xlim(0, 10)
        axt.set_ylim(0, 2)
        axt.axis("off")
        axt.text(5, 1.0, "通解=带任意常数的解曲线族；初始条件 → 选出唯一的特解",
                 fontsize=17, fontweight="bold", ha="center", va="center",
                 color="#276749",
                 bbox=dict(boxstyle="round,pad=0.4", fc="#e6ffed",
                           ec=render_utils.C_OK, lw=1.5))

    problems = render_utils.qa_figure(fig, f"n={n_curves},phase={phase}")
    if problems:
        raise SystemExit(f"[QA] 发现 {problems} 处问题（n={n_curves}, phase={phase}），需修布局")
    return fig


render_utils.set_style()
gb = render_utils.GifBuilder()
gb.add(frame(0, "family"), n=6)        # 标题 + 空坐标系
for nc in (1, 2, 3, 4):                # 逐条出现曲线（图例同步）
    gb.add(frame(nc, "family"), n=4)
gb.add(frame(4, "ic"), n=6)            # 初始条件红点
gb.add(frame(4, "pick"), n=6)          # C=1 加粗、其余变灰
gb.add(frame(4, "final"), n=16)        # 结论大字
ok = gb.save(OUT)
render_utils.export_keyframes(gb, SLUG)
print("[完成]" if ok else "[失败] 超 2MB")
