# -*- coding: utf-8 -*-
"""动图 08：哈希冲突与链地址法（拉链法）解决冲突。

数据与文档【例 7-3】一致：哈希函数 H(k) = k mod 7，
依次插入 19, 14, 23, 1, 68, 20, 84, 27（19 与 68、14 与 84、20 与 27 分别冲突）。
文档对应：第 7 章 查找 - 7.4 哈希表。
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common13003 import *   # noqa

SEQ = [19, 14, 23, 1, 68, 20, 84, 27]
M = 7
rec = Recorder()
qa = []

# buckets[i] = 按插入顺序的链
buckets = {i: [] for i in range(M)}

def bucket_xy(i, j):
    """桶 i 的第 j 个结点坐标。"""
    y = 44 - i * 6.2
    x = 26 + j * 10.5
    return x, y

def draw(title, note, cur=None, cur_j=0, chain=(), hold=SUB):
    fig, ax = new_fig(title, note)
    # 表头箭头
    for i in range(M):
        x, y = bucket_xy(i, -1)
        ax.add_patch(plt.Rectangle((x - 4.4, y - 2.2), 8.8, 4.4, fc=C_QUEUE, ec=C_EDGE, lw=1.5, zorder=3))
        ax.text(x, y, str(i), ha="center", va="center", fontsize=11.5, fontweight="bold", zorder=4)
        ax.annotate("", xy=(x + 5.6, y), xytext=(x + 4.4, y),
                    arrowprops=dict(arrowstyle="->", color=C_EDGE, lw=1.6), zorder=2)
    # 结点
    for i in range(M):
        for j, v in enumerate(buckets[i]):
            x, y = bucket_xy(i, j)
            on = chain and (i, j) in chain
            fc = C_HL if on else C_NODE
            ax.add_patch(plt.Rectangle((x - 4.4, y - 2.2), 8.8, 4.4, fc=fc, ec=C_EDGE, lw=1.6, zorder=3))
            ax.text(x, y, str(v), ha="center", va="center", fontsize=12, fontweight="bold", zorder=4)
            ax.annotate("", xy=(x + 5.6, y), xytext=(x + 4.4, y),
                        arrowprops=dict(arrowstyle="->", color=C_EDGE, lw=1.6), zorder=2)
        # NULL 尾
        x, y = bucket_xy(i, len(buckets[i]))
        ax.text(x + 2.2, y, "∧", ha="center", va="center", fontsize=11, color=C_DIM, zorder=2)
    if cur is not None:
        ax.text(74, 30, f"插入 {cur}", ha="center", fontsize=16, fontweight="bold", color="#E65100")
        ax.text(74, 24, f"H({cur}) = {cur} mod 7 = {cur % M}", ha="center", fontsize=13.5, color="#0D47A1")
    img = rec.add(fig, hold=hold)
    qa.extend(f"帧{len(rec.frames)}: " + p for p in check_frame(fig))
    plt.close(fig)

# 幕 0：方法说明
draw("链地址法（拉链法）· 方法", "同义词（哈希地址相同）链成单链表挂在对应桶后；查找/插入在链上进行",
     hold=HOLD)

for i, v in enumerate(SEQ):
    h = v % M
    draw(f"插入 {v}（第 {i+1} 个）", f"计算 H({v}) = {v} mod 7 = {h}，挂到桶 {h} 的链尾",
         cur=v, hold=SUB)
    buckets[h].append(v)
    chain = [(h, j) for j in range(len(buckets[h]))]
    conflict = len(buckets[h]) > 1
    draw(f"插入 {v}（第 {i+1} 个）",
         f"插入后桶 {h} 链：" + " → ".join(str(t) for t in buckets[h]) + ("（发生冲突，链长 2）" if conflict else ""),
         cur=v, chain=chain, hold=HOLD)

# 结论幕
fig, ax = new_fig("链地址法 · 结论", "")
ax.text(45, 40, "① 同义词存同一链表：冲突不「挤占」别的地址，插删方便", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 33.5, "② 查找长度 = 沿链比较次数；装填因子 α = 元素数 ÷ 表长（本例 8÷7 ≈ 1.14）", ha="center", fontsize=13.5, color=C_TEXT)
ax.text(45, 27, "③ 本例 ASL（成功，等概率）：桶 0 比较链长 2 → 2/2？按每元素：",
        ha="center", fontsize=12.5, color=C_TEXT)
ax.text(45, 21, "各链长 [2,1,1,0,0,2,2] → ASL = (1+2 + 1 + 1 + 1+2 + 1+2) ÷ 8 = 11 ÷ 8 ≈ 1.4", ha="center",
        fontsize=13, color="#0D47A1", fontweight="bold")
ax.text(45, 14.5, "④ 适合插删频繁的情形；与之对照：开放定址法（线性探测等）删除须做标记",
        ha="center", fontsize=13, color=C_TEXT)
ax.text(45, 8, "记忆锚点：哈希地址 = k mod m（m 取质数）；冲突 = 不同关键字映射到同一地址",
        ha="center", fontsize=13, color="#1B5E20", fontweight="bold")
img = rec.add(fig, hold=FINAL_HOLD)
qa.extend("尾帧: " + p for p in check_frame(fig))
plt.close(fig)

rec.qa_problems = qa
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../../09-计算机基础/数据结构与算法/images/13003-anim-hashchain.gif")
check_and_save(rec, out)
