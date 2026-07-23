# -*- coding: utf-8 -*-
import os, shutil, re
BASE = r"C:\ADHD_agent\KB\产出-数值设计\X3_下期节日优化清单"
SHARE = os.path.join(BASE, "_分享包")
FRAME = r"C:\ADHD_agent\KB\产出-数据分析\X3_深海世界杯_框架回归"
CARD  = r"C:\ADHD_agent\KB\产出-数值设计\X3_卡册优化"
SKIN  = r"C:\ADHD_agent\KB\产出-数值设计\X3_皮肤开箱优化"
KOU   = r"C:\ADHD_agent\KB\产出-数据分析\深海节&世界杯回归"

# 1) 目录
if os.path.exists(SHARE): shutil.rmtree(SHARE)
os.makedirs(os.path.join(SHARE, "assets"))
os.makedirs(os.path.join(SHARE, "回归报告"))

# 2) 清单 HTML
shutil.copy(os.path.join(BASE, "X3下期节日优化清单.html"), os.path.join(SHARE, "X3下期节日优化清单.html"))
# 3) assets 全拷(图)
for f in os.listdir(os.path.join(BASE, "assets")):
    if f.lower().endswith((".png",".jpg",".jpeg",".gif",".webp")):
        shutil.copy(os.path.join(BASE,"assets",f), os.path.join(SHARE,"assets",f))
# 4) 回归报告
reports = {
 FRAME: ["母题1_大盘增量_20260716.html","母题4_改动效果清单_20260716.html","深海大富翁回归_20260716.html",
         "深海转盘回归_20260716.html","深海节礼包模块回归_20260716.html","深海节功能模块回归_20260716.html",
         "世界杯开箱回归_20260716.html","世界杯竞猜回归_20260716.html"],
 CARD:  ["X3卡册获取回归_深海世界杯_20260713.html","X3纪念卡现状调研.html"],
 SKIN:  ["皮肤开箱优化方案_v1_20260716.html"],
 KOU:   ["数据口径统一.md"],
}
for d, fs in reports.items():
    for f in fs:
        src=os.path.join(d,f)
        if os.path.exists(src): shutil.copy(src, os.path.join(SHARE,"回归报告",f))
        else: print("缺失:",f)

# 5) 改写清单里的回归目录链接 → 回归报告/
p=os.path.join(SHARE,"X3下期节日优化清单.html")
s=open(p,encoding="utf-8").read()
s=s.replace("../../产出-数据分析/X3_深海世界杯_框架回归/","回归报告/")
s=s.replace("../X3_卡册优化/","回归报告/")
s=s.replace("../../产出-数据分析/深海节%26世界杯回归/","回归报告/")
open(p,"w",encoding="utf-8").write(s)

# 6) 改写 开箱回归 里指向皮肤方案v1的外链 → 同文件夹
op=os.path.join(SHARE,"回归报告","世界杯开箱回归_20260716.html")
if os.path.exists(op):
    t=open(op,encoding="utf-8").read()
    t=t.replace("../../产出-数值设计/X3_皮肤开箱优化/皮肤开箱优化方案_v1_20260716.html","皮肤开箱优化方案_v1_20260716.html")
    open(op,"w",encoding="utf-8").write(t)

print("=== 分享包结构 ===")
for root,dirs,files in os.walk(SHARE):
    lvl=root.replace(SHARE,"").count(os.sep)
    print("  "*lvl+os.path.basename(root)+"/")
    for f in sorted(files): print("  "*(lvl+1)+f)
