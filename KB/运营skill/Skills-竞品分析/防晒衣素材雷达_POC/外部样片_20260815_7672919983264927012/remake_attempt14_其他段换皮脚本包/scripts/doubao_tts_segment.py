#!/usr/bin/env python3
"""Generate one short voice-over segment with Doubao Speech TTS 2.0.

The script deliberately handles one segment per invocation so a failed or
overlong line can be revised without regenerating the full 30-second video.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path


API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
DEFAULT_ENV_FILE = Path(r"C:\ADHD_agent\avatar-replace\.env")
DEFAULT_SPEAKER = "zh_female_shuangkuaisisi_uranus_bigtts"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def decode_concatenated_json(raw: str) -> list[dict]:
    decoder = json.JSONDecoder()
    items: list[dict] = []
    index = 0
    while index < len(raw):
        while index < len(raw) and raw[index].isspace():
            index += 1
        if index >= len(raw):
            break
        item, index = decoder.raw_decode(raw, index)
        if isinstance(item, dict):
            items.append(item)
    return items


def synthesize(
    *,
    text: str,
    context: str,
    output: Path,
    speaker: str,
    speech_rate: int,
    resource_id: str,
    api_key: str,
) -> dict:
    request_id = str(uuid.uuid4())
    req_params = {
        "text": text,
        "speaker": speaker,
        "audio_params": {
            "format": "mp3",
            "sample_rate": 24000,
            "speech_rate": speech_rate,
            "loudness_rate": 0,
        },
    }
    if context:
        req_params["context_texts"] = [context]

    body = {
        "user": {"uid": "personal-video-voiceover"},
        "req_params": req_params,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
            "X-Api-Resource-Id": resource_id,
            "X-Api-Request-Id": request_id,
            "X-Control-Require-Usage-Tokens-Return": "*",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            log_id = response.headers.get("X-Tt-Logid", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"TTS HTTP {exc.code}: {detail[:800]}") from exc

    events = decode_concatenated_json(raw)
    chunks: list[bytes] = []
    final_event: dict | None = None
    failure_event: dict | None = None
    for event in events:
        data = event.get("data")
        if isinstance(data, str) and data:
            chunks.append(base64.b64decode(data))
        code = event.get("code")
        if code == 20000000:
            final_event = event
        elif code not in (None, 0, 20000000):
            failure_event = event

    if failure_event:
        raise RuntimeError(
            "TTS service error: "
            + json.dumps(failure_event, ensure_ascii=False)[:1000]
            + (f"; X-Tt-Logid={log_id}" if log_id else "")
        )
    audio = b"".join(chunks)
    if not audio or final_event is None:
        raise RuntimeError(
            f"TTS returned no complete audio: events={len(events)}, bytes={len(audio)}, "
            f"X-Tt-Logid={log_id or 'missing'}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio)
    return {
        "ok": True,
        "output": str(output),
        "bytes": len(audio),
        "events": len(events),
        "speaker": speaker,
        "resource_id": resource_id,
        "speech_rate": speech_rate,
        "text_chars": len(text),
        "context_chars": len(context),
        "request_id": request_id,
        "log_id": log_id,
        "usage": final_event.get("usage"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument(
        "--context",
        default="",
        help="One-line scene and emotion instruction sent as context_texts.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--speaker", default=DEFAULT_SPEAKER)
    parser.add_argument("--speech-rate", type=int, default=8)
    parser.add_argument("--resource-id")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    args = parser.parse_args()

    if not -50 <= args.speech_rate <= 100:
        parser.error("--speech-rate must be between -50 and 100")
    load_env_file(args.env_file)
    api_key = os.environ.get("VOLC_SPEECH_API_KEY", "").strip()
    resource_id = (
        args.resource_id
        or os.environ.get("VOLC_TTS_RESOURCE_ID", "").strip()
        or "seed-tts-2.0"
    )
    if not api_key:
        parser.error("VOLC_SPEECH_API_KEY is missing")

    result = synthesize(
        text=args.text.strip(),
        context=args.context.strip(),
        output=args.output,
        speaker=args.speaker,
        speech_rate=args.speech_rate,
        resource_id=resource_id,
        api_key=api_key,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
