# -*- coding: utf-8 -*-
"""批量写 5国×2版 荣耀之路头像框 task json → x3-media tasks 目录。打印 taskid\tlabel 供派 worker。"""
import json, os, time, pathlib
TASKS = r"C:\Users\linkang\.claude\skills\x3-media\state\tasks"
OUTDIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\半决赛决赛外显\荣耀之路头像框_国家特色版"
FLAGS = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\flags_48"
ANCHOR = OUTDIR + r"\WC_SF_Frame_MAR_vA_建筑破形.png"  # 已认可的丰富度/等级/窗口格式锚

COMMON = ("Semi-realistic thick painterly render, ornate circular game avatar frame. ADOPT the richness, gold "
 "Final-Four laurel+football TIER SHIELD at the bottom, and the arch-topped transparent avatar WINDOW format of "
 "reference image 1 (a Moroccan frame) — but REPLACE every Moroccan motif with the country's OWN culture below. "
 "The silhouette must BREAK the plain circle using that country's own architecture/structure. Center portrait "
 "window AND outside filled with plain solid green screen background (NOT transparent, NOT checkerboard), removed "
 "in post. NO text, no faux-Arabic scribbles, no tiny footballer pictograms, no scene background. Colors anchored "
 "to reference image 2 (the national flag).")

# (code, slug, 中文label, 该版文化破形描述)
JOBS = [
 ("FRA","v1_铁艺","法国·新艺术铁艺","The ring is French Art Nouveau wrought-iron scrollwork (Guimard Paris-metro style), fleur-de-lis nodes, a proud Gallic rooster crest rising at the TOP breaking the silhouette, ornate iron lantern brackets jutting at the sides, blue-white-red enamel inlays."),
 ("FRA","v2_哥特","法国·哥特石构","The ring is framed by French Gothic cathedral stone tracery (Notre-Dame rose-window motifs), a pointed-arch stone crown at the TOP breaking the circle, flying-buttress brackets at the sides, fleur-de-lis, blue-white-red stained-glass panels behind."),
 ("NOR","v1_龙船","挪威·维京龙船","The ring is Norse Urnes-style interlaced knotwork in pewter-silver and gold, TWO carved Viking dragon-prow (drakkar) heads rising at the TOP breaking the silhouette, rune-carved side posts, flowing rosemaling floral accents, a faint aurora glow behind."),
 ("NOR","v2_木教堂","挪威·木构教堂","The ring is framed by Norwegian stave-church wooden architecture (steep carved gables with dragon-head finials, carved portals), a tall triangular wooden crown at the TOP breaking the circle, carved-wood corbel brackets at the sides, aurora glow behind."),
 ("ENG","v1_纹章","英格兰·三狮纹章","The ring bears three heraldic gold lions passant, a royal CROWN plus a St George's Cross shield at the TOP breaking the silhouette, Tudor-rose nodes, heraldic shield brackets at the sides, red-and-gold enamel."),
 ("ENG","v2_哥特","英格兰·哥特石构","The ring is framed by English Perpendicular Gothic stone architecture (Westminster tracery), a pointed-arch stone crown at the TOP breaking the circle, castle turret / portcullis brackets at the sides, Tudor roses, a red St George cross banner."),
 ("ESP","v1_摩尔拱","西班牙·摩尔宫拱","The ring is Andalusian Alhambra gold arabesque, a Moorish multifoil horseshoe-arch crown at the TOP breaking the silhouette, arched niche brackets at the sides, a flamenco ruffle flourish accent, red-and-gold baroque palette."),
 ("ESP","v2_巴洛克","西班牙·巴洛克斗牛","The ring is ornate Spanish Baroque Churrigueresque gold carving, a Spanish royal crest crown at the TOP breaking the silhouette, bold bull-horn motifs sweeping at the sides, a red carnation and flamenco fan accent, red-and-gold."),
 ("BEL","v1_霍塔","比利时·霍塔铁艺","The ring is Victor Horta Art Nouveau golden whiplash ironwork, a Red Devil horned crest at the TOP breaking the silhouette, ornate iron lantern brackets at the sides, black-gold-red palette."),
 ("BEL","v2_行会","比利时·哥特行会","The ring is framed by Brussels Grand-Place Gothic guild-hall gold-leaf architecture (ornate gables and spires), a tall spire crown at the TOP breaking the circle, turret brackets at the sides, a red devil emblem, black-gold-red."),
]

t0 = int(time.time())
lines = []
for i,(code,slug,label,desc) in enumerate(JOBS):
    tid = time.strftime("%Y%m%d-%H%M%S", time.localtime(t0)) + "-" + os.urandom(2).hex()
    t0 += 1  # 保证 id 唯一递增
    fname = f"WC_SF_Frame_{code}_{slug}.png"
    task = {
      "schema_version":1,"task_id":tid,"status":"pending","type":"uiframe",
      "user_prompt": f"荣耀之路头像框·{label}(荣耀之路四强专属框·建筑/文化破形版). {desc} {COMMON}",
      "params":{"model":"gemini",
        "reference_images":[ANCHOR, f"{FLAGS}\\{code}.png"],
        "output_dir":OUTDIR,"output_filename":fname,"aspect_ratio":"1:1",
        "postprocess":"remove_bg_transparent",
        "transparency_note":"纯绿幕实底(中心窗+框外都铺绿)→ grfal remove_background → verify_transparency.py 强制过闸门(exit0才落盘)。中心窗必须透明。破形外扩部分也要抠干净。"},
      "started_at":None,"finished_at":None,
      "result":{"saved_to":[],"history_lines_appended":0,"backend":None},
      "error":None,"retry_count":0,"created_by":"main-agent"}
    pathlib.Path(TASKS, tid+".json").write_text(json.dumps(task,ensure_ascii=False,indent=2),encoding="utf-8")
    lines.append(f"{tid}\t{label}\t{fname}")
print("\n".join(lines))
