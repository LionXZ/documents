# -*- coding: utf-8 -*-
"""00023《高等数学（工本）》动图 2：分部积分公式的来源。

内容：由乘积求导法则 (uv)′ = u′v + uv′ 两边积分、移项，
     推出分部积分公式 ∫u dv = uv − ∫v du。纯文字排版动画（axis off）。
节奏（fps=2）：标题 6 -> 三行推导逐行各 6 -> 高亮 3 -> 移项 8 ->
     记号替换 3 -> 结论大字 16。
"""
import render_utils

OUT = ("/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/"
       "高等数学工本/images/calc-anim-integration-by-parts.gif")
SLUG = "integration-by-parts"

L1 = "乘积求导法则：(uv)′ = u′v + uv′"
L2 = "两边同时积分：∫(uv)′ dx = ∫u′v dx + ∫uv′ dx"
L3_ORIG = "左边就是 uv：uv = ∫u′v dx + ∫uv′ dx"
L3_MOVED = "∫u′v dx = uv − ∫uv′ dx"
L3_SUB = "∫v du = uv − ∫u dv"
SUB_NOTE = "记号替换：u′v = v du，uv′ = u dv"
FINAL = "∫u dv = uv − ∫v du"


def frame(lines_shown, phase):
    """重建一帧。lines_shown=已出现的正文行数(0~3)；
    phase: base|hl|moved|sub|final。"""
    fig, ax = render_utils.new_fig("分部积分公式从哪里来？")
    ax.set_position([0.04, 0.04, 0.92, 0.84])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    dim = phase == "final"          # 结论帧把推导行淡化
    col = render_utils.C_DIM if dim else "#2d3748"

    # 三行推导（行距 1.5 数据单位 >= 0.8）
    if lines_shown >= 1:
        ax.text(0.6, 8.4, L1, fontsize=16, ha="left", va="center", color=col)
    if lines_shown >= 2:
        ax.text(0.6, 6.9, L2, fontsize=16, ha="left", va="center", color=col)
    if lines_shown >= 3:
        if phase == "hl":           # 移项动作子帧：黄色高亮原式
            ax.text(0.6, 5.4, L3_ORIG, fontsize=16, ha="left", va="center",
                    color="#2d3748",
                    bbox=dict(boxstyle="round,pad=0.35", fc=render_utils.C_MARK,
                              ec="#d69e2e", alpha=0.85))
        elif phase == "moved":      # 移项后：红字 + 红箭头标注
            ax.text(0.6, 5.4, L3_MOVED, fontsize=16, ha="left", va="center",
                    color=render_utils.C_HIGH, fontweight="bold")
            # 箭头终点须在移项式文字右端之外（Annotation 的 extent 含箭头路径）；
            # 标注文字下移，避免顶到上一行 L2（实测 L2 底 335px）
            ax.annotate("移项", xy=(4.8, 5.6), xytext=(6.0, 5.95),
                        fontsize=15, color=render_utils.C_HIGH,
                        fontweight="bold",
                        arrowprops=dict(arrowstyle="->",
                                        color=render_utils.C_HIGH, lw=2))
        else:                       # base / sub / final
            t3 = L3_SUB if phase in ("sub", "final") else L3_ORIG
            ax.text(0.6, 5.4, t3, fontsize=16, ha="left", va="center",
                    color=render_utils.C_HIGH if phase == "sub" else col,
                    fontweight="bold" if phase == "sub" else "normal")

    # 记号替换提示行
    if phase in ("sub", "final"):
        ax.text(0.6, 4.0, SUB_NOTE, fontsize=14, ha="left", va="center",
                color=render_utils.C_DIM if dim else "#4a5568")

    # 结论大字
    if phase == "final":
        ax.text(5, 2.6, FINAL, fontsize=24, fontweight="bold",
                ha="center", va="center", color="#276749",
                bbox=dict(boxstyle="round,pad=0.5", fc="#e6ffed",
                          ec=render_utils.C_OK, lw=2))

    problems = render_utils.qa_figure(fig, f"n={lines_shown},phase={phase}")
    if problems:
        raise SystemExit(f"[QA] 发现 {problems} 处问题（n={lines_shown}, phase={phase}），需修布局")
    return fig


render_utils.set_style()
gb = render_utils.GifBuilder()
gb.add(frame(0, "base"), n=6)     # 标题
gb.add(frame(1, "base"), n=6)     # 乘积求导法则
gb.add(frame(2, "base"), n=6)     # 两边积分
gb.add(frame(3, "base"), n=6)     # 左边就是 uv
gb.add(frame(3, "hl"), n=3)       # 高亮待移项
gb.add(frame(3, "moved"), n=8)    # 移项
gb.add(frame(3, "sub"), n=3)      # 记号替换
gb.add(frame(3, "final"), n=16)   # 结论大字
ok = gb.save(OUT)
render_utils.export_keyframes(gb, SLUG)
print("[完成]" if ok else "[失败] 超 2MB")
