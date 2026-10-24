# -*- coding: utf-8 -*-
"""GIF 抽帧检查工具：抽第 1、中间、最后帧存 PNG 到 /tmp 供目检。

用法：python inspect_gif.py <gif路径>
打印帧数 / 尺寸 / 总时长，并把首、中、尾帧存为
/tmp/02324-png/<gif名>-first|mid|last.png
"""
import sys, os
from PIL import Image


def main():
    if len(sys.argv) < 2:
        print("用法: python inspect_gif.py <gif路径>")
        sys.exit(1)
    path = sys.argv[1]
    im = Image.open(path)
    frames = []
    durs = []
    i = 0
    while True:
        try:
            im.seek(i)
        except EOFError:
            break
        frames.append(im.copy().convert("RGB"))
        durs.append(im.info.get("duration", 0))
        i += 1
    n = len(frames)
    print(f"{os.path.basename(path)}: {n} 帧 / 尺寸 {im.size} / "
          f"总时长 {sum(durs)/1000:.1f}s / 单帧 {durs[0]}ms")
    out_dir = "/tmp/02324-png"
    os.makedirs(out_dir, exist_ok=True)
    tag = os.path.splitext(os.path.basename(path))[0]
    picks = {"first": frames[0], "mid": frames[n // 2], "last": frames[-1]}
    for name, fr in picks.items():
        p = os.path.join(out_dir, f"{tag}-{name}.png")
        fr.save(p)
        print(f"  已存 {p}")


if __name__ == "__main__":
    main()
