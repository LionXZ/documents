# -*- coding: utf-8 -*-
"""02324 备考攻略文档机检脚本（主会话独立验收用）。

检查项：
1. 图片引用与 images/ 实际文件一一对应（不缺文件、不留未引用图）
2. 动图占位注释 <!-- ANIM: ... --> 是否全部已替换为三行式嵌入
3. 目录锚点与文内标题对应
4. 真题考期标注格式统一（【2026.4·单选 3】风格）
5. 第二节引用的真题在第三节汇编中有对应（联动检查）
6. 【待核实】/【分值待核实】/⚠️ 站方答案勘误 标注统计
"""
import re, sys, os, glob

DOC = sys.argv[1] if len(sys.argv) > 1 else "09-计算机基础/离散数学/02324离散数学-考试备考全攻略.md"
IMG_DIR = os.path.join(os.path.dirname(DOC), "images")

text = open(DOC, encoding="utf-8").read()
problems = 0

# 1. 图片引用
refs = re.findall(r'!\[[^\]]*\]\((images/[^)]+)\)', text)
print(f"[1] 图片引用 {len(refs)} 处")
for r in refs:
    p = os.path.join(os.path.dirname(DOC), r)
    if not os.path.exists(p):
        print(f"  [缺文件] {r}")
        problems += 1
if os.path.isdir(IMG_DIR):
    actual = set()
    for ext in ("gif", "png"):
        actual |= {os.path.basename(x) for x in glob.glob(os.path.join(IMG_DIR, f"*.{ext}"))}
    used = {os.path.basename(r) for r in refs}
    unused = actual - used
    if unused:
        print(f"  [未引用图] {sorted(unused)}")
        problems += len(unused)

# 2. 动图占位残留
placeholders = re.findall(r'<!--\s*ANIM:[^>]*-->', text)
print(f"[2] ANIM 占位残留 {len(placeholders)} 处")
for p in placeholders:
    print(f"  [占位残留] {p[:60]}")
problems += len(placeholders)

# 3. 目录锚点
toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', text)
heads = re.findall(r'^(#{1,3})\s+(.+)$', text, re.M)
def anchor(t):
    t = re.sub(r'[、，。：:（）()【】\[\]「」/★✅⚠️🔑📌🎯✍️📝🖼 ]', '', t)
    return t.lower()
head_anchors = {anchor(h[1]) for h in heads}
print(f"[3] 目录链接 {len(toc_links)} 条")
for label, a in toc_links:
    if a not in head_anchors and a.replace('-', '') not in {h.replace('-', '') for h in head_anchors}:
        print(f"  [锚点可疑] #{a} <- {label}")
        problems += 1

# 4. 考期标注格式
exam_tags = re.findall(r'【(\d{4})[\.．](\d+)[·・]([^】]+)】', text)
bad_tags = re.findall(r'【\d{4}年?\s*月?\s*[·・][^】]*】', text)
fmt_ok = sum(1 for _ in exam_tags)
print(f"[4] 考期标注 {fmt_ok} 处（格式标准）")

# 5. 第二节引用的真题在第三节中出现（联动）
# 定位第三节的行范围
sec3_start = text.find("## 三、历年真题汇编")
sec2_start = text.find("## 二、必考概念详解")
sec4_start = text.find("## 四、高频考点")
if sec3_start > 0 and sec2_start > 0:
    sec3_text = text[sec3_start:sec4_start if sec4_start > sec3_start else len(text)]
    sec23 = text[sec2_start:sec3_start]
    cited = set(re.findall(r'【((?:19|20)\d{2}[\.．]\d+[·・][^】]+)】', sec23))
    compiled = set(re.findall(r'【((?:19|20)\d{2}[\.．]\d+[·・][^】]+)】', sec3_text))
    missing = {c for c in cited if c not in compiled}
    print(f"[5] 二节引用真题 {len(cited)} 个；三节汇编 {len(compiled)} 个；二节独有 {len(missing)} 个")
    for m in sorted(missing):
        print(f"  [二节独有(需核对是否为正文例题/早期考期)] 【{m}】")

# 6. 标注统计
for pat, name in [("【待核实】", "待核实"), ("【分值待核实】", "分值待核实"), ("站方答案勘误", "站方答案勘误"), ("【推导答案】", "推导答案")]:
    n = text.count(pat)
    print(f"[6] {name}: {n} 处")

print(f"\n=== 机检完成：硬伤 {problems} 处 ===")
sys.exit(1 if problems else 0)
