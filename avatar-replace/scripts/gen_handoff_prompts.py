"""细化打轴 → 即梦手动出片逐镜 prompt 清单（2026-07-14）。

自动 refs 模式的分镜 prompt 刻意中性（避 Seedance 文本风控）；手动在即梦出片
没有那层限制，服装/动作可抠细。本脚本对 job 每个 replace 段：
  - 服装：读换装后数字人形象图（front/back）细抠外层服装，全 job 共用一次
  - 动作：从 source.mp4 按段密集抽帧（3fps）逐拍分解动作/手势/朝向/镜头
组装成成年人设 + 合规声明的细化 prompt，写清单 txt。

⚠️ 合规红线（写进 prompt）：只描述外层服装、动作编排、镜头；不描述内衣/贴身
衣物细节、不描述身体身材、不提年龄；人设固定成年女性。

用法：先灌 .env 进环境变量，再
  python scripts/gen_handoff_prompts.py <job_id> <片号> [<job_id> <片号> ...] --out <txt路径>
"""
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.config import load_config          # noqa: E402
from core.providers.volc import VolcProvider  # noqa: E402
from core import media                        # noqa: E402

OUTFIT_PROMPT = """这是一位成年数字人演员的正面与背面形象图。请详细描述她身上的外层服装，输出 JSON：
{"outfit": "一句话描述外层服装：款式、颜色、领型、袖型、版型与长度、材质光泽、拼色或图案、正面与背面的差异。只描述外穿衣物本身，措辞中性专业"}
只输出 JSON。"""

BEATS_PROMPT = """这是广告视频某个镜头按时间顺序的密集抽帧。之后要用一位成年数字人演员逐拍复刻同一个镜头。请仔细观察并输出 JSON：
{"beats": ["按时间先后逐拍列出主要人物的动作，每一拍一句，包含身体朝向的角度变化、手部的具体动作、头部朝向"],
 "camera": "镜头运动与景别变化，一句话（如：从中景缓慢推近到上半身特写）",
 "others": "画面中其他人物的位置、朝向与动作概述，无则空串"}
只描述姿态、动作编排与镜头；不要描述内衣或贴身衣物细节，不要描述身体部位或身材，不要提及年龄。措辞中性专业。只输出 JSON。"""


def _json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group())
    except Exception:
        return {}


def outfit_of(p: VolcProvider, job_dir: Path) -> str:
    imgs = [job_dir / "avatar" / n for n in ("front.jpg", "back.jpg")]
    imgs = [i for i in imgs if i.exists()]
    if not imgs:
        return ""
    return str(_json(p.chat_vision(OUTFIT_PROMPT, imgs)).get("outfit", "")).strip()


def beats_of(p: VolcProvider, src: Path, start: float, end: float) -> dict:
    with tempfile.TemporaryDirectory() as td:
        frames = media.extract_frames(src, Path(td), interval=max(0.3, (end - start) / 10))
        picks = [f for f in frames if start - 1e-6 <= f.t <= end + 1e-6][:10]
        if not picks:  # 段太短，退回取中点最近一帧
            mid = min(frames, key=lambda f: abs(f.t - (start + end) / 2))
            picks = [mid]
        d = _json(p.chat_vision(BEATS_PROMPT, [f.path for f in picks]))
    beats = d.get("beats", [])
    return {"beats": [str(b).strip() for b in beats if str(b).strip()],
            "camera": str(d.get("camera", "")).strip() or "固定",
            "others": str(d.get("others", "")).strip()}


def _clean(s: str) -> str:
    return s.strip().rstrip("。.；;，, ").strip()


def _has_person(others: str) -> bool:
    # VLM 有时把背景环境塞进 others；只有明确提到人且非"无…人"时才当有人物
    if not others:
        return False
    if re.search(r"无(其他|额外|明显).{0,6}人", others):
        return False
    return bool(re.search(r"人物|人员|女性|同伴|另一人|一人", others))


def build_prompt(scene: str, outfit: str, b: dict) -> str:
    beats = "；".join(_clean(x) for x in b["beats"] if _clean(x)) or "自然展示动作"
    camera = _clean(b["camera"]).lstrip("镜头").strip() or "固定"
    others = f"画面中另有其他成年人：{_clean(b['others'])}，装扮自然。" \
        if _has_person(b["others"]) else ""
    return (
        f"真实实拍摄影质感，写实非动画，自然光影与皮肤质感。场景：{_clean(scene)}。"
        f"一位成年女性（约23岁，黑色低马尾），服装：{_clean(outfit)}。"
        f"动作逐拍：{beats}。镜头{camera}。{others}"
        f"场景、光线与参考图严格一致并全程保持不变，动作自然连贯。"
        f"出镜人物均为成年人，产品展示，无不良引导。"
    )


def main():
    a = sys.argv[1:]
    out_path = Path(a[a.index("--out") + 1]) if "--out" in a else ROOT / "handoff.txt"
    pairs = [x for x in a[:a.index("--out")]] if "--out" in a else a
    cfg = load_config(ROOT / "config.yaml", require_key=True)
    p = VolcProvider(cfg.ark)
    lines = ["即梦手动出片 · 细化逐镜清单（服装+逐拍动作细抠版）",
             "=" * 60,
             "用法：图生视频，拖对应场景图，贴 prompt，5s / 9:16 / 参考选构图整体",
             "开头“真实实拍摄影质感”必留；人设固定成年女性；保留合规声明句",
             "=" * 60, ""]
    jobs_root = ROOT / "jobs"
    for jid, tag in zip(pairs[0::2], pairs[1::2]):
        jdir = jobs_root / jid
        job = json.loads((jdir / "job.json").read_text(encoding="utf-8"))
        src = jdir / "source.mp4"
        outfit = outfit_of(p, jdir)
        lines.append(f"【{tag}.mp4】 服装基准：{outfit}\n")
        i = 0
        for s in job["segments"]:
            if s["mode"] != "replace":
                continue
            sb = s.get("storyboard", {})
            b = beats_of(p, src, s["start"], s["end"])
            prompt = build_prompt(sb.get("scene", ""), outfit, b)
            dur = s["end"] - s["start"]
            # 即梦时长档通常 5s/10s；段都 <5s，统一选 5s 档，出片后裁到原片时长对齐
            lines.append(f"■ 镜头{i:03d} → {tag}_镜头{i:03d}.jpg")
            lines.append(f"   原片时长 {dur:.1f}s ｜ 即梦选 5s 档，出片后裁前 {dur:.1f}s 对齐（拼回时管线自动裁，手动则用剪映掐头）")
            lines.append(prompt)
            lines.append("")
            print(f"{tag} 镜头{i:03d} done", flush=True)
            i += 1
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {out_path}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
