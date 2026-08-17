#!/usr/bin/env python3
"""Generate the seven scene-aware TTS clips for the V04 voice mix.

Each item is still one independent Doubao Speech HTTP request.  Keeping the
requests separate lets us retime or rewrite a single shot without touching the
other approved voice clips.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from doubao_tts_segment import (
    DEFAULT_ENV_FILE,
    DEFAULT_SPEAKER,
    load_env_file,
    synthesize,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "audio" / "tts_scene_v02"

SEGMENTS = [
    {
        "id": "VO01",
        "name": "开头吐槽",
        "start": 1.96,
        "text": "军训最尴尬的，就是显痕。",
        "context": (
            "18岁大学新生刚结束烈日军训，闷热出汗后发现白色上衣显出内衣痕迹；"
            "她正对同学自然吐槽，有一点尴尬和无奈，短促、口语化、灵动，重点落在“显痕”，"
            "不要播音腔，不要叫卖。"
        ),
        "speech_rate": 38,
    },
    {
        "id": "VO02",
        "name": "商品揭晓",
        "start": 4.70,
        "text": "换成粉底肤无痕款，藏在白T里面自然多了。",
        "context": (
            "18岁大学新生把刚发现的粉底肤无痕内衣举给同学看；情绪从刚才的尴尬转成轻松和小惊喜，"
            "像真心分享好用的小发现，语气亲切灵动，强调“粉底肤”和“自然多了”，不要广告播报。"
        ),
        "speech_rate": 12,
    },
    {
        "id": "VO03",
        "name": "跑跳验证",
        "start": 12.33,
        "text": "跑跳也不显痕。",
        "context": (
            "18岁大学新生在操场跑跳测试后，发现白T依然干净；她松了一口气，带一点“果然有效”的开心，"
            "这是一句镜头内极短对白，轻快利落，重点落在“不显痕”，不要拖尾。"
        ),
        "speech_rate": 38,
    },
    {
        "id": "VO04",
        "name": "结构讲解",
        "start": 13.73,
        "text": "一片式平整杯面，细肩带配宽幅下围，贴身更平整。",
        "context": (
            "18岁学姐边指产品结构边给同学解释，像认真分享购买经验；语气清楚、有把握但不端着，"
            "轻强调“一片式”“细肩带”“宽幅下围”，整体自然口语，不要科普播音腔。"
        ),
        "speech_rate": 14,
    },
    {
        "id": "VO05",
        "name": "冰丝体验",
        "start": 19.10,
        "text": "冰丝摸起来凉凉的，透气、柔软，还有弹。",
        "context": (
            "18岁大学新生正在摸和轻拉冰丝面料，真实感受到清凉和弹力；语气清爽、带一点惊喜，"
            "像边摸边说，三个卖点“透气、柔软、还有弹”逐个轻快落下，不要硬广腔。"
        ),
        "speech_rate": 12,
    },
    {
        "id": "VO06",
        "name": "正背无痕",
        "start": 23.40,
        "text": "正面不透色，背面也不显痕。",
        "context": (
            "白T正面与背面依次展示，18岁学姐用结果做简短总结；语气轻松、笃定，前后两句形成自然对照，"
            "强调“不透色”和“不显痕”，不要夸张，不要播报。"
        ),
        "speech_rate": 12,
    },
    {
        "id": "VO07",
        "name": "收尾推荐",
        "start": 27.10,
        "text": "军训内搭，就选粉底肤无痕款。",
        "context": (
            "傍晚军训操场，18岁大学新生拿着产品做收尾推荐；经历前面的验证后很有把握，"
            "语气轻快、亲近、有一点笑意，像给同学一句省心建议，结尾干净收住，不要喊麦。"
        ),
        "speech_rate": 10,
    },
]


def main() -> int:
    load_env_file(DEFAULT_ENV_FILE)
    api_key = os.environ.get("VOLC_SPEECH_API_KEY", "").strip()
    resource_id = os.environ.get("VOLC_TTS_RESOURCE_ID", "").strip() or "seed-tts-2.0"
    if not api_key:
        raise RuntimeError("VOLC_SPEECH_API_KEY is missing")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for segment in SEGMENTS:
        output = OUTPUT_DIR / f"{segment['id']}_{segment['name']}.mp3"
        result = synthesize(
            text=segment["text"],
            context=segment["context"],
            output=output,
            speaker=DEFAULT_SPEAKER,
            speech_rate=segment["speech_rate"],
            resource_id=resource_id,
            api_key=api_key,
        )
        result["id"] = segment["id"]
        result["name"] = segment["name"]
        result["start"] = segment["start"]
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)

    manifest = OUTPUT_DIR / "generation_manifest.json"
    manifest.write_text(
        json.dumps({"segments": SEGMENTS, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "manifest": str(manifest)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
