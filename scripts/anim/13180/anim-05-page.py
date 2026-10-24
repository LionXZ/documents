# -*- coding: utf-8 -*-
"""13180《操作系统》动图 05：页面置换算法对比 LRU vs OPT。

数据（同源真题 02326·2023.4 综合题 38）：访问序列 1,2,3,4,5,3,4,1,6,7,8,7,8,5
（共 14 次访问），内存 4 帧，初始为空。LRU 缺页 10 次；OPT 缺页 8 次。
分镜：题面 → LRU 逐访问推演（装入/命中/淘汰，槽下标注上次使用时刻）
      → LRU 定格 10 次 → OPT 推演（槽下标注未来使用，灰点标记未来位置）
      → OPT 定格 8 次 → 尾帧对比（OPT 理论基准，LRU 接近 OPT）。
QA 由 style.snapshot 内置检测。
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style

OUT = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images/os-anim-05-page.gif"

TITLE = "页面置换算法对比：LRU vs OPT（同源真题 02326·2023.4 数据）"
SEQ = [1, 2, 3, 4, 5, 3, 4, 1, 6, 7, 8, 7, 8, 5]
N = len(SEQ)
GRID_X, GRID_W = 8, 6.0            # 序列条起点与格宽
SLOT_X, SLOT_W = 26, 10.0          # 内存槽起点与槽宽


def last_use(page, pos):
    """LRU：page 在 pos 及之前最近一次使用的下标。"""
    for j in range(pos, -1, -1):
        if SEQ[j] == page:
            return j
    return None


def next_use(page, pos):
    """OPT：page 在 pos 之后最近一次使用的下标。"""
    for j in range(pos + 1, N):
        if SEQ[j] == page:
            return j
    return None


def slot_notes(algo, slots, pos):
    """槽下小标注：LRU 上次使用 / OPT 未来使用。"""
    out = []
    for p in slots:
        if p is None:
            out.append("")
        elif algo == "LRU":
            j = last_use(p, pos)
            out.append(f"上次 t{j + 1}" if j is not None else "")
        else:
            j = next_use(p, pos)
            out.append(f"未来 t{j + 1}" if j is not None else "永不再用")
    return out


def draw(s):
    fig, ax = style.new_fig(title=TITLE)
    pos, hits = s["pos"], s["hits"]
    # ---- 顶部访问序列条 ----
    for i, p in enumerate(SEQ):
        x0 = GRID_X + i * GRID_W
        if i in hits:
            fc, ec, lw = "#C6F6D5", style.C_GREEN, 2.0
        elif i == pos:
            fc, ec, lw = "#FDE68A", style.C_RED, 2.0
        elif i <= pos:
            fc, ec, lw = "#D6E4FF", style.C_GRAY, 1.2
        else:
            fc, ec, lw = "#FFFFFF", style.C_GRAY, 1.2
        ax.add_patch(plt.Rectangle((x0, 50), GRID_W, 6, fc=fc, ec=ec, lw=lw))
        ax.text(x0 + GRID_W / 2, 53, str(p), ha="center", va="center",
                fontsize=12.5, fontweight="bold", color=style.C_TEXT)
        ax.text(x0 + GRID_W / 2, 48.7, f"t{i + 1}", ha="center", va="top",
                fontsize=7.5, color=style.C_GRAY)
    # ---- 内存 4 槽 ----
    for k in range(4):
        x0 = SLOT_X + k * SLOT_W
        p = s["slots"][k]
        flash = (s["flash"] == k)
        hitted = (k in s["slot_hit"])
        ec = style.C_GREEN if hitted else (style.C_RED if flash else style.C_GRAY)
        lw = 2.4 if (hitted or flash) else 1.5
        fc = "#FFF5F5" if flash else ("#F0FFF4" if hitted else
                                      (style.C_LIGHT if p else "#FFFFFF"))
        ax.add_patch(plt.Rectangle((x0, 36), SLOT_W, 9, fc=fc, ec=ec, lw=lw))
        if p:
            ax.text(x0 + SLOT_W / 2, 40.5, str(p), ha="center", va="center",
                    fontsize=15, fontweight="bold", color=style.C_TEXT)
        note = s["slot_notes"][k]
        if note:
            ax.text(x0 + SLOT_W / 2, 34.3, note, ha="center", va="center",
                    fontsize=8.5, color=style.C_GRAY)
    # ---- OPT 淘汰画面：未来仍会访问的位置画灰点 ----
    if s["gray_future"]:
        for p in s["slots"]:
            j = next_use(p, pos) if p else None
            if j is not None:
                ax.plot(GRID_X + j * GRID_W + GRID_W / 2, 55.2, marker="o",
                        ms=3, color=style.C_GRAY)
    # ---- 缺页计数卡 ----
    ax.add_patch(plt.Rectangle((76, 36), 18, 9, fc="#F7FAFC",
                               ec=style.C_BLUE, lw=1.5))
    ax.text(85, 42.4, "缺页", ha="center", va="center", fontsize=10.5,
            color=style.C_GRAY)
    ax.text(85, 38.5, str(s["faults"]), ha="center", va="center",
            fontsize=21, fontweight="bold", color=style.C_RED)
    # ---- 底部旁注 ----
    if s["note1"]:
        ax.text(50, 28.8, s["note1"], ha="center", fontsize=12.5,
                fontweight="bold", color=style.C_TEXT)
    if s["note2"]:
        ax.text(50, 24.6, s["note2"], ha="center", fontsize=11.5,
                color=style.C_GRAY)
    return fig, ax


def main():
    frames = []
    # 通用状态：slot_notes 自动计算；命中槽自动描绿边
    def step(tag, hold, **kw):
        s = dict(pos=0, slots=[None] * 4, faults=0, hits=set(), flash=-1,
                 slot_hit=set(), gray_future=False, algo="LRU",
                 note1=None, note2=None)
        s.update(kw)
        # 命中位置对应的内存槽描绿边
        hit_slots = set()
        for i in s["hits"]:
            page = SEQ[i]
            if page in s["slots"]:
                hit_slots.add(s["slots"].index(page))
        s["slot_hit"] = hit_slots
        s["slot_notes"] = slot_notes(s["algo"], s["slots"], s["pos"])
        fig, ax = draw(s)
        style.snapshot(fig, frames, tag)
        style.hold(fig, frames, hold)
        plt.close(fig)

    # ---- 题面 ----
    step("P1-题面", style.HOLD_MIN, pos=-1,
         note1="访问序列 1,2,3,4,5,3,4,1,6,7,8,7,8,5（共 14 次访问）",
         note2="内存 4 帧，初始为空 —— 先推演 LRU（最近最久未使用）")

    # ---- LRU 推演 ----
    step("L1-装入1234", style.HOLD_MIN, pos=3, slots=[1, 2, 3, 4], faults=4,
         note1="依次访问 1,2,3,4：内存全空 → 4 次全部缺页装入",
         note2="每个槽下方标注该页上次使用的时刻（LRU 的淘汰依据）")
    step("L2-访问5淘汰1", style.HOLD_MIN, pos=4, slots=[5, 2, 3, 4], faults=4, flash=0,
         note1="访问 5：缺页 → 淘汰页 1，装入页 5（缺页 5 次）",
         note2="页 1 上次使用 t1，是最近最久未使用的页 → LRU 淘汰它")
    step("L3-命中34", 3, pos=6, slots=[5, 2, 3, 4], faults=5, hits={5, 6},
         note1="访问 3、4：都命中",
         note2="命中后刷新该页的上次使用时间（3 → t6，4 → t7）")
    step("L4-访问1淘汰2", style.HOLD_MIN, pos=7, slots=[5, 1, 3, 4], faults=5, flash=1,
         note1="访问 1：缺页 → 淘汰页 2，装入页 1（缺页 6 次）",
         note2="页 2 上次使用 t2，比 5(t5)、3(t6)、4(t7) 都早")
    step("L5-访问6淘汰5", style.HOLD_MIN, pos=8, slots=[6, 1, 3, 4], faults=6, flash=0,
         note1="访问 6：缺页 → 淘汰页 5，装入页 6（缺页 7 次）",
         note2="页 5 上次使用 t5，是当前最久未使用的页")
    step("L6-访问78淘汰34", style.HOLD_MIN, pos=10, slots=[6, 1, 7, 8], faults=7,
         note1="访问 7：淘汰页 3（t6 最久）；访问 8：淘汰页 4（t7 最久）",
         note2="两次连续缺页，累计缺页 9 次")
    step("L7-命中78", 3, pos=12, slots=[6, 1, 7, 8], faults=9, hits={11, 12},
         note1="访问 7、8：都命中",
         note2="命中刷新时间标记：7 → t12，8 → t13")
    step("L8-访问5淘汰1", style.HOLD_MIN, pos=13, slots=[6, 5, 7, 8], faults=9, flash=1,
         note1="访问 5：缺页 → 淘汰页 1，装入页 5（缺页 10 次）",
         note2="页 1 上次使用 t8，比 6(t9)、7(t12)、8(t13) 早")
    step("L9-LRU定格", style.HOLD_MIN, pos=13, slots=[6, 5, 7, 8], faults=10,
         note1="LRU 推演结束：缺页 10 次（14 次访问）",
         note2="接下来用 OPT（最佳置换）推演同一序列")

    # ---- OPT 推演 ----
    step("O1-装入1234", style.HOLD_MIN, algo="OPT", pos=3, slots=[1, 2, 3, 4], faults=4,
         note1="OPT（最佳置换）：淘汰未来最长时间不再使用的页",
         note2="前 4 次访问全部缺页装入（与 LRU 相同）")
    step("O2-访问5淘汰2", style.HOLD_MIN, algo="OPT", pos=4, slots=[1, 5, 3, 4],
         faults=4, flash=1, gray_future=True,
         note1="访问 5：缺页 → 淘汰页 2（缺页 5 次）",
         note2="向前看：页 2 以后永不再用；灰点标出其余页未来仍要访问的位置")
    step("O3-命中341", 3, algo="OPT", pos=7, slots=[1, 5, 3, 4], faults=5, hits={5, 6, 7},
         note1="访问 3、4、1：全部命中")
    step("O4-访问67淘汰16", style.HOLD_MIN, algo="OPT", pos=9, slots=[7, 5, 3, 4],
         faults=5, gray_future=True,
         note1="访问 6：淘汰页 1；访问 7：淘汰页 6（缺页 7 次）",
         note2="两页以后都永不再用，按槽位顺序淘汰；页 5 未来 t14 仍要用")
    step("O5-访问8淘汰3", style.HOLD_MIN, algo="OPT", pos=10, slots=[7, 5, 8, 4],
         faults=7, flash=2, gray_future=True,
         note1="访问 8：缺页 → 淘汰页 3（缺页 8 次）",
         note2="页 3、4 以后都不再用；页 7、5 分别在 t12、t14 还要用")
    step("O6-命中785", 3, algo="OPT", pos=13, slots=[7, 5, 8, 4], faults=8, hits={11, 12, 13},
         note1="访问 7、8、5：全部命中")
    step("O7-OPT定格", style.HOLD_MIN, algo="OPT", pos=13, slots=[7, 5, 8, 4], faults=8,
         note1="OPT 推演结束：缺页 8 次（14 次访问）",
         note2="OPT 需要预知未来的访问序列，实际系统无法实现")

    # ---- 尾帧：对比总结 ----
    fig, ax = style.new_fig(title="LRU vs OPT：缺页次数对比")
    ax.text(50, 53, "OPT 为理论最低缺页率：需要预知未来，不可实现，仅作评价基准",
            ha="center", fontsize=12.5, color=style.C_TEXT)
    ax.text(50, 48, "LRU 按过去的「最近最久未使用」预测未来，实际效果接近 OPT",
            ha="center", fontsize=12.5, color=style.C_TEXT)
    ax.text(50, 41, "缺页次数对比（同样 14 次访问、4 帧）", ha="center",
            fontsize=12.5, fontweight="bold", color=style.C_TEXT)
    bars = [("LRU", 10, style.C_BLUE, 32), ("OPT", 8, style.C_GREEN, 22)]
    for name, val, color, y in bars:
        ax.text(16, y + 2.5, name, ha="right", va="center", fontsize=13,
                fontweight="bold", color=color)
        ax.add_patch(plt.Rectangle((18, y), val * 3.6, 5, fc=color, ec="none"))
        ax.text(18 + val * 3.6 + 1.5, y + 2.5, f"{val} 次", ha="left",
                va="center", fontsize=13, fontweight="bold", color=color)
    style.snapshot(fig, frames, "P19-尾帧对比")
    style.hold(fig, frames, style.TAIL_HOLD)
    plt.close(fig)

    style.save_gif(frames, OUT)


if __name__ == "__main__":
    main()
