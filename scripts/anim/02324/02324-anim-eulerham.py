# -*- coding: utf-8 -*-
"""欧拉回路 vs 哈密顿回路 并排对比动图脚本。
数据来源：自编教学数据，与文档例题同步（ANIM_SPEC 第 10 条锚定）。
左图 5 顶点「中心 + 外圈」结构，边集取全偶度方案：
  中心 O 连 A/B/C/D 四条辐条 + 顶边 AB + 底边 CD（各点度 4,2,2,2,2 全偶，
  保证欧拉回路存在），回路 O-A-B-O-C-D-O 共 6 条边每边恰一次。
右图 5 顶点五边形 + 两条对角线（对角线是干扰项，不走），
  哈密顿回路 1-2-3-4-5-1 每点恰一次。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_utils import (set_style, new_fig, GifBuilder, qa_figure,
                          C_MAIN, C_HIGH, C_OK, C_DIM, C_BG, C_MARK)
from matplotlib.patches import Circle
import math

OUT = os.path.join("09-计算机基础", "离散数学", "images", "02324-anim-eulerham.gif")
set_style()

# ---------- 左图（欧拉）：中心 + 四外圈，全偶度 ----------
EPOS = {"O": (2.5, 3.1), "A": (1.3, 4.6), "B": (3.7, 4.6), "C": (1.3, 1.6), "D": (3.7, 1.6)}
EEDGES = [("O", "A"), ("O", "B"), ("O", "C"), ("O", "D"), ("A", "B"), ("C", "D")]
EPATH = ["O", "A", "B", "O", "C", "D", "O"]          # 欧拉回路（6 条边）
EDEG = {"O": 4, "A": 2, "B": 2, "C": 2, "D": 2}
# 度数标签位置（放在点外侧，避免与点标签重叠）
EDEG_LBL = {"O": (2.5, 3.62), "A": (0.95, 4.95), "B": (4.05, 4.95),
            "C": (0.92, 1.28), "D": (4.08, 1.28)}

# ---------- 右图（哈密顿）：五边形 + 两条对角线 ----------
CX, CY, RR = 7.5, 3.1, 1.5
HPOS = {}
for i in range(5):
    ang = math.radians(90 - 72 * i)                  # 顶点 1 在正上方，顺时针排
    HPOS[i + 1] = (CX + RR * math.cos(ang), CY + RR * math.sin(ang))
HEDGES = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)]    # 五边形边
HDIG = [(1, 3), (2, 4)]                              # 对角线（干扰项，不走）
HPATH = [1, 2, 3, 4, 5, 1]                           # 哈密顿回路（5 个点）
R = 0.26                                              # 顶点半径


def draw_graph(ax, pos, edges, done_pairs, cur_pair, done_nodes, cur_node, dig=None):
    """在 ax 上画一个图。done_pairs=已走过的边集合；cur_pair=当前高亮边；
    done_nodes=已访问点集合；cur_node=当前高亮点；dig=灰虚对角线列表。"""
    for a, b in (dig or []):                          # 对角线：始终灰虚（不参与回路）
        (x0, y0), (x1, y1) = pos[a], pos[b]
        ax.plot([x0, x1], [y0, y1], color=C_DIM, lw=1.8, ls=(0, (4, 3)), zorder=1)
    for e in edges:
        a, b = (e if e[0] in pos else e)              # 边端点
        key = (a, b) if (a, b) in done_pairs else ((b, a) if (b, a) in done_pairs else None)
        (x0, y0), (x1, y1) = pos[a], pos[b]
        if key:                                       # 已走：绿
            ax.plot([x0, x1], [y0, y1], color=C_OK, lw=4, zorder=2)
        elif cur_pair and set(cur_pair) == {a, b}:    # 当前步：红
            ax.plot([x0, x1], [y0, y1], color=C_HIGH, lw=4.5, zorder=2)
        else:                                         # 未走：蓝
            ax.plot([x0, x1], [y0, y1], color=C_MAIN, lw=2, zorder=2)
    for k, (x, y) in pos.items():
        if k == cur_node:                             # 当前点：红且加大
            ax.add_patch(Circle((x, y), R + 0.07, fc=C_HIGH, ec="white", lw=1.5, zorder=5))
        elif k in done_nodes:                         # 已访点：绿
            ax.add_patch(Circle((x, y), R, fc=C_OK, ec="white", lw=1.5, zorder=5))
        else:                                         # 未访点：蓝
            ax.add_patch(Circle((x, y), R, fc=C_MAIN, ec="white", lw=1.5, zorder=5))
        ax.text(x, y, str(k), fontsize=13, color="white", ha="center",
                va="center", fontweight="bold", zorder=6)


def make_frame(euler_n, ham_n, show_deg=False):
    """euler_n=欧拉已走边数(0~6)；ham_n=哈密顿已走边数(0~5)；show_deg=是否标左图度数。"""
    fig, ax = new_fig("欧拉回路 vs 哈密顿回路：一个看边，一个看点")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    # 左右小标题
    ax.text(2.5, 5.22, "欧拉回路：每条边恰一次", fontsize=13, fontweight="bold",
            color=C_MAIN, ha="center")
    ax.text(7.5, 5.22, "哈密顿回路：每个点恰一次", fontsize=13, fontweight="bold",
            color=C_MAIN, ha="center")
    # 左图状态
    ep = EPATH[:euler_n + 1]
    epairs = {(ep[i], ep[i + 1]) for i in range(len(ep) - 1)}
    enodes = set(ep[:euler_n + 1])
    ecur = EPATH[euler_n] if euler_n < len(EPATH) - 1 else None
    epair = (EPATH[euler_n], EPATH[euler_n + 1]) if euler_n < len(EPATH) - 1 else None
    draw_graph(ax, EPOS, EEDGES, epairs, epair, enodes, ecur)
    # 右图状态（对角线灰虚始终画着，但不进回路）
    hp = HPATH[:ham_n + 1]
    hpairs = {(hp[i], hp[i + 1]) for i in range(len(hp) - 1)}
    hnodes = set(hp[:ham_n + 1])
    hcur = HPATH[ham_n] if ham_n < len(HPATH) - 1 else None
    hpair = (HPATH[ham_n], HPATH[ham_n + 1]) if ham_n < len(HPATH) - 1 else None
    draw_graph(ax, HPOS, HEDGES, hpairs, hpair, hnodes, hcur, dig=HDIG)
    # 左图度数标注（仅度数讲解帧）
    if show_deg:
        for k, (x, y) in EDEG_LBL.items():
            ax.text(x, y, f"d={EDEG[k]}", fontsize=11.5, color=C_HIGH, ha="center")
    # 底部状态行
    if show_deg:
        ax.text(2.5, 0.85, "各点度数全为偶数，存在欧拉回路", fontsize=12,
                color=C_HIGH, ha="center")
        ax.text(7.5, 0.85, "哈密顿回路不看点度，只看能否过每点", fontsize=12,
                color="#555555", ha="center")
    elif euler_n == 6 and ham_n == 0:
        ax.text(2.5, 0.85, "6 条边各走一次，回到 O", fontsize=12, color=C_OK, ha="center")
    elif 0 < euler_n < 6:
        ax.text(2.5, 0.85, f"欧拉：第 {euler_n}/6 条边", fontsize=12,
                color=C_HIGH, ha="center")
    elif ham_n == 5:
        ax.text(7.5, 0.85, "5 个点各过一次；对角线不必走", fontsize=12,
                color=C_OK, ha="center")
    elif ham_n > 0:
        ax.text(7.5, 0.85, f"哈密顿：第 {ham_n}/5 步", fontsize=12,
                color=C_HIGH, ha="center")
    return fig


# ================= 主流程：建帧 =================
def main():
    gb = GifBuilder(fps=2)
    qa_total = 0

    def emit(fig, n, ctx):
        """QA 机检后加帧；问题数累计，最后统一报告。"""
        nonlocal qa_total
        qa_total += qa_figure(fig, ctx)
        gb.add(fig, n=n)

    # 1. 开场：两图并排，驻留 6 帧
    emit(make_frame(0, 0), 6, "开场")
    # 2. 度数讲解帧（欧拉存在性依据），驻留 6 帧
    emit(make_frame(0, 0, show_deg=True), 6, "度数")
    # 3. 欧拉回路逐边走（每步 3 帧）
    for k in range(1, 7):
        emit(make_frame(k, 0), 3, f"欧拉第{k}边")
    emit(make_frame(6, 0), 6, "欧拉完成")
    # 4. 哈密顿回路逐点走（每步 3 帧）
    for k in range(1, 6):
        emit(make_frame(6, k), 3, f"哈密顿第{k}步")
    emit(make_frame(6, 5), 6, "哈密顿完成")
    # 5. 总结尾帧（驻留 16 帧 = 8 秒）：两图走完 + 结论行
    fig, ax = new_fig("欧拉回路 vs 哈密顿回路：一个看边，一个看点")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis("off")
    ax.text(2.5, 5.22, "欧拉回路：每条边恰一次", fontsize=13, fontweight="bold",
            color=C_MAIN, ha="center")
    ax.text(7.5, 5.22, "哈密顿回路：每个点恰一次", fontsize=13, fontweight="bold",
            color=C_MAIN, ha="center")
    draw_graph(ax, EPOS, EEDGES, {(a, b) for a, b in EEDGES}, None, set(EPOS), None)
    draw_graph(ax, HPOS, HEDGES, {(a, b) for a, b in HEDGES}, None, set(HPOS), None, dig=HDIG)
    ax.text(5.0, 0.25, "欧拉看边：连通 + 全为偶度 ｜ 哈密顿看点：每点恰过一次",
            fontsize=15, color=C_OK, fontweight="bold", ha="center")
    emit(fig, 16, "总结")

    gb.save(OUT)
    print(f"[QA] eulerham 问题总数 = {qa_total}")
    sys.exit(1 if qa_total > 0 else 0)


if __name__ == "__main__":
    main()

