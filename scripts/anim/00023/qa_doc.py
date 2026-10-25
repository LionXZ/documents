# -*- coding: utf-8 -*-
"""00023 备考攻略文档机检脚本（主会话独立验收用，改造自 02324 qa_doc.py）。

检查项：
1. 图片引用与 images/ 实际文件一一对应（不缺文件、不留未引用图）
2. 目录锚点与文内标题对应
3. 真题考期标注格式统计（【2026.4·单选 3】风格）
4. 第二节引用的真题在第三节汇编中有对应（联动检查）
5. 【官方】/【推导】/【待核实】标注统计
6. 拼接完整性：五节标题齐全、模块 A~E 齐全、无重复标题
"""
import re, sys, os, glob

DOC = sys.argv[1] if len(sys.argv) > 1 else "09-计算机基础/高等数学工本/00023高等数学工本-考试备考全攻略.md"
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

# 2. 目录锚点
toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', text)
heads = re.findall(r'^(#{1,3})\s+(.+)$', text, re.M)
def anchor(t):
    t = re.sub(r'[、，。：:（）()【】\[\]「」/★✅⚠️🔑📌🎯✍️📝🖼 ]', '', t)
    return t.lower()
head_anchors = {anchor(h[1]) for h in heads}
print(f"[2] 目录链接 {len(toc_links)} 条")
for label, a in toc_links:
    if a not in head_anchors and a.replace('-', '') not in {h.replace('-', '') for h in head_anchors}:
        print(f"  [锚点可疑] #{a} <- {label}")
        problems += 1

# 3. 考期标注格式
exam_tags = re.findall(r'【(\d{4})[\.．](\d+)[·・]([^】]+)】', text)
print(f"[3] 考期标注 {len(exam_tags)} 处")

# 4. 二节引用真题 ⊆ 三节汇编（联动）
sec3_start = text.find("## 三、历年真题汇编")
sec2_start = text.find("## 二、必考概念详解")
sec4_start = text.find("## 四、高频考点")
if sec3_start > 0 and sec2_start > 0:
    sec3_text = text[sec3_start:sec4_start if sec4_start > sec3_start else len(text)]
    sec23 = text[sec2_start:sec3_start]
    cited = set(re.findall(r'【((?:19|20)\d{2}[\.．]\d+[·・][^】]+)】', sec23))
    compiled = set(re.findall(r'【((?:19|20)\d{2}[\.．]\d+[·・][^】]+)】', sec3_text))
    missing = {c for c in cited if c not in compiled}
    print(f"[4] 二节引用真题 {len(cited)} 个；三节汇编 {len(compiled)} 个；二节独有 {len(missing)} 个")
    for m in sorted(missing):
        print(f"  [二节独有(需核对)] 【{m}】")

# 5. 标注统计
for pat, name in [("【官方】", "官方答案"), ("【官方 ", "官方答案(带说明)"), ("【推导", "推导"), ("【待核实】", "待核实"), ("【未核实】", "未核实")]:
    n = text.count(pat)
    print(f"[5] {name}: {n} 处")

# 6. 拼接完整性
required_heads = ["## 一、考试概况", "## 二、必考概念详解", "## 三、历年真题汇编",
                  "## 四、高频考点", "## 五、备考建议", "## 六、校验记录"]
for h in required_heads:
    c = text.count(h)
    print(f"[6] '{h}' 出现 {c} 次" + ("（应恰 1 次）" if c != 1 else " ✓"))
    if c != 1:
        problems += abs(c - 1) if c else 1
for m in ["### 模块 A ", "### 模块 B ", "### 模块 C ", "### 模块 D ", "### 模块 E "]:
    c = text.count(m)
    if c != 1:
        print(f"  [模块异常] '{m}' 出现 {c} 次")
        problems += abs(c - 1) if c else 1
print(f"[6] 模块 A~E 检查完毕")

# 7. 已知勘误点复查：2024.4-21 必须 R=1/2
for line_idx, line in enumerate(text.split("\n"), 1):
    if "2ⁿ/(2n+1)" in line or "2ⁿ/(2n+1)" in line:
        pass
bad_r = re.findall(r'2ⁿ/\(2n\+1\)[^\n]{0,80}(?:R\s*=\s*\*\*?2\*\*?|R\s*=\s*2|收敛区间\s*\(−2,\s*2\))', text)
print(f"[7] 2024.4-21 错误口径(R=2)残留 {len(bad_r)} 处")
problems += len(bad_r)

print(f"\n=== 机检完成：硬伤 {problems} 处 ===")
sys.exit(1 if problems else 0)
