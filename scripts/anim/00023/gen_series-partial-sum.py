# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》动图 1：级数部分和收敛摆动。

内容：交错级数 1 - 1/2 + 1/3 - 1/4 + ... 的部分和数列 {Sn} 逐项摆动，
     振幅递减并收敛到极限 ln2 ≈ 0.6931（红虚线）。
节奏（fps=2）：标题+虚线 6 帧 -> 8 个部分和逐点出现各 4 帧 ->
     三行结论文字 6 帧 -> 结论大字 16 帧。
"""
import render_utils

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-series-partial-sum.gif")
SLUG = "series-partial-sum"
TITLE = "部分和数列的摆动与收敛：1 − 1/2 + 1/3 − 1/4 + …"

# 部分和数列 S1 ~ S8（与文档例题数值一致）
S = [1.0000, 0.5000, 0.8333, 0.5833, 0.7833, 0.6167, 0.7595, 0.6345]


def frame(k, mode):
    """重建一帧。k=已出现的部分和个数；mode: none|lines|conclusion。"""
    fig, ax = render_utils.new_fig(TITLE)
    ax.set_position([0.08, 0.32, 0.86, 0.54])
    ax.set_xlim(0, 12.7)
    ax.set_ylim(0.4, 1.1)
    ax.set_xticks(range(1, 13))
    ax.set_yticks([0.4 + i * 0.1 for i in range(8)])
    ax.set_xlabel("n", labelpad=4)
    ax.set_ylabel("Sn", labelpad=4)
    ax.grid(alpha=0.3, lw=0.6)

    # 极限参考线：红色虚线 + 右侧上方标注
    ax.axhline(0.6931, color=render_utils.C_HIGH, ls="--", lw=1.6, zorder=2)
    ax.text(9.6, 0.715, "极限 ln2 ≈ 0.6931", color=render_utils.C_HIGH,
            fontsize=13, ha="left", va="bottom")

    # 折线 + 各点（白面蓝边小点），当前点红色大点
    if k >= 1:
        xs = list(range(1, k + 1))
        ax.plot(xs, S[:k], color=render_utils.C_MAIN, lw=2, zorder=3,
                marker="o", ms=6, mfc="white", mec=render_utils.C_MAIN, mew=1.6)
        ax.plot([k], [S[k - 1]], marker="o", ms=9,
                color=render_utils.C_HIGH, zorder=4)

    # 关键值标签：S1/S7 标上方，S2/S8 标下方，避免互相重叠
    for idx, dy, va in [(0, 0.045, "bottom"), (1, -0.045, "top"),
                        (6, 0.045, "bottom"), (7, -0.045, "top")]:
        if k > idx:
            ax.text(idx + 1, S[idx] + dy, f"S{idx + 1}={S[idx]:.4f}",
                    ha="center", va=va, fontsize=12,
                    color=render_utils.C_MAIN, fontweight="bold")

    # 底部文字区（axis off），QA 会检测其中的文字
    if mode in ("lines", "conclusion"):
        axt = fig.add_axes([0.0, 0.0, 1.0, 0.26])
        axt.set_xlim(0, 10)
        axt.set_ylim(0, 3)
        axt.axis("off")
        if mode == "lines":
            rows = [(2.35, "部分和数列 {Sn}", True),
                    (1.35, "Sn 摆动但振幅越来越小", False),
                    (0.35, "若 {Sn} 有极限 → 级数收敛", False)]
            for y, s, bold in rows:
                axt.text(0.5, y, s, fontsize=15, ha="left", va="center",
                         fontweight="bold" if bold else "normal")
        else:
            axt.text(5, 1.5, "级数收敛 ⇐ 部分和数列有极限：S = lim(n→∞) Sn",
                     fontsize=19, fontweight="bold", ha="center", va="center",
                     color="#276749",
                     bbox=dict(boxstyle="round,pad=0.45", fc="#e6ffed",
                               ec=render_utils.C_OK, lw=1.5))

    problems = render_utils.qa_figure(fig, f"k={k},mode={mode}")
    if problems:
        raise SystemExit(f"[QA] 发现 {problems} 处问题（k={k}, mode={mode}），需修布局")
    return fig


render_utils.set_style()
gb = render_utils.GifBuilder()
gb.add(frame(0, "none"), n=6)                 # 标题 + 极限虚线
for k in range(1, 9):                         # 逐项出现部分和
    gb.add(frame(k, "none"), n=4)
gb.add(frame(8, "lines"), n=6)                # 三行结论文字
gb.add(frame(8, "conclusion"), n=16)          # 结论大字
ok = gb.save(OUT)
render_utils.export_keyframes(gb, SLUG)
print("[完成]" if ok else "[失败] 超 2MB")
