# -*- coding: utf-8 -*-
"""轮3:照图#8(alt1)样子重出。锚=alt1(完整卡:金框+透明圆角+腰上构图+画风+身份)。出侧面版+正面版。"""
import json, datetime, secrets, pathlib, time, os
SR = r"C:\Users\linkang\.claude\skills\x3-media"
out = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\候选_轮3"
os.makedirs(out, exist_ok=True)
ref8 = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯纪念卡\WC_MemorialCard_Aerisia_v4直出_alt1.png"

base = ("Regenerate a collectible MEMORIAL CARD that closely MATCHES the reference image in every way: same ornate GOLDEN "
"rounded-rectangle frame with corner filigree, same transparent rounded corners outside the card, same white-and-gold soccer "
"cheerleader (silver-white hair, golden trophy emblem, number 10, gold-white pom-poms), same World Cup stadium scene with golden "
"trophy + falling confetti + warm light, same semi-painted game-art style, same waist-up framing filling the card. "
"Keep her face and identity faithful to the reference. High quality, clean. Vertical portrait card. NO flags. ONE card, no grid. ")
POSE = {
 "thisver": "POSE: same elegant 3/4 angle as the reference (long flowing hair, body slightly turned), just a cleaner regeneration.",
 "front": "POSE: she faces the viewer FRONT-ON, body squared to camera, upright and centered (front view, not side).",
}
ids = []
for k in ["thisver", "front"]:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S"); tid = f"{ts}-{secrets.token_hex(2)}"
    t = {"schema_version": 1, "task_id": tid, "status": "pending", "type": "general", "user_prompt": base + POSE[k],
         "params": {"model": "gpt", "reference_images": [ref8], "output_dir": out,
                    "output_filename": f"WC_r3_{k}.png", "postprocess": "none", "note": "轮3照图8重出"},
         "started_at": None, "finished_at": None, "result": {"saved_to": [], "history_lines_appended": 0, "backend": None},
         "error": None, "retry_count": 0, "created_by": "main-agent"}
    pathlib.Path(SR, "state", "tasks", f"{tid}.json").write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
    ids.append((tid, k)); time.sleep(1.05)
for t, k in ids:
    print(t, k)
