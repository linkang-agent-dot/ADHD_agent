# -*- coding: utf-8 -*-
"""纪念卡轮2:正面x2+侧面x2,输出到 候选_轮2/。脸锚FINAL+格式锚76。"""
import json, datetime, secrets, pathlib, time, os
SR = r"C:\Users\linkang\.claude\skills\x3-media"
out = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\候选_轮2"
os.makedirs(out, exist_ok=True)
ref76 = r"C:\x3-project\client\Assets\Res\UI\Spirits\MemorialCard\img_card_image_76.png"
face = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_FINAL.png"
base = ("A single collectible MEMORIAL CARD with a THIN ornate golden rounded-rectangle frame (match reference image 1: "
"thin gold border, corner filigree, rounded card, a full painted scene fills inside). Inside: the silver-white-haired "
"woman from reference image 2 (white-and-gold soccer cheerleader crop top, golden trophy emblem, number 10, gold-white "
"pom-poms), waist-up. Keep face/identity from reference image 2 with the SAME calm soft closed-mouth smile (NO teeth grin). "
"Behind: green World Cup stadium pitch, golden championship trophy, falling golden confetti, warm light. Cartoon semi-painted "
"game-art style. Tasteful. Vertical portrait card. NO flags. ONE card, no grid. ")
POSE = {
 "front": "POSE: faces the viewer FRONT-ON, body squared to camera, upright and centered (NOT side, NOT profile).",
 "side": "POSE: graceful 3/4 SIDE view, slight twist toward camera, elegant dynamic stance (clearly a side angle).",
}
ids = []
for pose in ["front", "side"]:
    for i in range(2):
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        tid = f"{ts}-{secrets.token_hex(2)}"
        t = {"schema_version": 1, "task_id": tid, "status": "pending", "type": "general",
             "user_prompt": base + POSE[pose],
             "params": {"model": "gpt", "reference_images": [ref76, face], "output_dir": out,
                        "output_filename": f"WC_{pose}_{i+1}.png", "postprocess": "none", "note": "纪念卡轮2"},
             "started_at": None, "finished_at": None,
             "result": {"saved_to": [], "history_lines_appended": 0, "backend": None},
             "error": None, "retry_count": 0, "created_by": "main-agent"}
        pathlib.Path(SR, "state", "tasks", f"{tid}.json").write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
        ids.append((tid, f"{pose}_{i+1}"))
        time.sleep(1.05)
for t, k in ids:
    print(t, k)
