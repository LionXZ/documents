# -*- coding: utf-8 -*-
"""verify_gifs.py —— 13180《操作系统》五张教学动图（07~11）交付自检。

检查口径：
1. duration 集合必须恰为 {500}（fps=2，逐帧独立存储，无合并帧）
2. 尾帧段（结尾连续相同画面）>= 16 帧
3. 文件大小 <= 2MB
4. 每张抽 3 帧（首 / 中 / 尾）导出 PNG 到 preview/ 供目检

通过标准：全部检查项 OK，退出码 0；任一失败退出码 1。
"""

import os
import sys

from PIL import Image

IMG_DIR = "/Users/xiexiaoluo/Desktop/code/documents/09-计算机基础/操作系统/images"
PREVIEW_DIR = "/Users/xiexiaoluo/Desktop/code/documents/scripts/anim/13180/preview"

GIFS = [
    "os-anim-01-state.gif",
    "os-anim-02-pv.gif",
    "os-anim-03-banker.gif",
    "os-anim-04-sched.gif",
    "os-anim-05-page.gif",
    "os-anim-06-addr.gif",
    "os-anim-07-disk.gif",
    "os-anim-08-deadlock.gif",
    "os-anim-09-tlb.gif",
    "os-anim-10-partition.gif",
    "os-anim-11-io.gif",
]


def read_gif(path):
    """读取 GIF 全部帧：返回 (帧字节列表, duration 列表, 尺寸)。

    帧字节剔除末尾 3 字节（右下角 1 像素）——save_gif 为防 Pillow 合并帧
    会对重复帧做该像素微扰，画面段比较应忽略它。
    """
    im = Image.open(path)
    datas, durs, size = [], [], None
    for i in range(im.n_frames):
        im.seek(i)
        datas.append(im.convert("RGB").tobytes()[:-3])
        durs.append(im.info.get("duration"))
        size = im.size
    return datas, durs, size


def segments(datas):
    """把连续相同的帧合并成段，返回 [(起始帧, 段长)] —— 即画面段"""
    segs = []
    start = 0
    for i in range(1, len(datas) + 1):
        if i == len(datas) or datas[i] != datas[start]:
            segs.append((start, i - start))
            start = i
    return segs


def main():
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    all_ok = True
    for name in GIFS:
        path = os.path.join(IMG_DIR, name)
        print(f"== {name} ==")
        if not os.path.exists(path):
            print("  [FAIL] 文件不存在")
            all_ok = False
            continue
        size_bytes = os.path.getsize(path)
        datas, durs, size = read_gif(path)
        segs = segments(datas)
        dur_set = set(durs)
        tail = segs[-1][1] if segs else 0

        ok_dur = dur_set == {500}
        ok_tail = tail >= 16
        ok_size = size_bytes <= 2 * 1024 * 1024
        all_ok &= ok_dur and ok_tail and ok_size

        print(f"  帧数={len(datas)}  尺寸={size[0]}x{size[1]}  "
              f"大小={size_bytes / 1024:.0f}KB  duration集合={sorted(dur_set)}")
        print(f"  画面段共 {len(segs)} 段，段长={[s[1] for s in segs]}")
        print(f"  尾帧段={tail} 帧（要求>=16）")
        print(f"  duration={{500}}: {'OK' if ok_dur else 'FAIL'}  "
              f"尾帧>=16: {'OK' if ok_tail else 'FAIL'}  "
              f"<=2MB: {'OK' if ok_size else 'FAIL'}")

        # 抽 3 帧：首 / 中 / 尾
        stem = name[: -len(".gif")]
        for tag, idx in (("f1", 0), ("f2", len(datas) // 2), ("f3", len(datas) - 1)):
            im = Image.open(path)
            im.seek(idx)
            out_png = os.path.join(PREVIEW_DIR, f"{stem}-{tag}.png")
            im.convert("RGB").save(out_png)
            print(f"  预览: {out_png}（第 {idx + 1} 帧）")
    print("=" * 40)
    print("总体结论:", "全部通过" if all_ok else "存在 FAIL 项")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
