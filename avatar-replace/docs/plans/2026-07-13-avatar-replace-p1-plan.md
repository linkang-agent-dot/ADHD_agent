# avatar-replace P1（管线核心）Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
> ⚠️ 全程禁止调用公司 GRFal；本计划所有测试用 mock/本地 ffmpeg 合成素材，不发起任何真实 AI 生成调用。真实 API 冒烟由用户配好 key 后自己触发（Task 11）。

**Goal:** CLI 跑通「视频 → VLM 打轴识别未成年人 → 人工确认 → 切段 → Seedance 替换为数字人 → 拼回」全流程管线。

**Architecture:** 纯 Python 管线包（`core/`），所有 AI 能力收口在 `core/providers/volc.py`（火山引擎方舟 API），媒体处理全走本地 ffmpeg subprocess。任务状态以 `jobs/<id>/job.json` 落盘，支持断点续跑。测试全部 mock Provider；集成测试用 FakeProvider 走通全链路零 API 调用。

**Tech Stack:** Python 3.10+、pytest、requests、PyYAML、ffmpeg/ffprobe（PATH 上）、argparse（无 Web 依赖——Web 壳是 P2）。

**工作目录:** `C:\ADHD_agent\avatar-replace\`（ADHD 仓内，提交只 add 本目录）。

---

## 任务目录结构（最终态）

```
avatar-replace/
├── core/
│   ├── __init__.py
│   ├── config.py            # Task 1
│   ├── media.py             # Task 2  ffprobe/抽帧/切割/拼接底层封装
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py          # Task 3  Provider 抽象 + FakeProvider
│   │   └── volc.py          # Task 3  火山方舟实现
│   ├── annotate.py          # Task 4
│   ├── cut.py               # Task 5
│   ├── replace.py           # Task 6
│   ├── stitch.py            # Task 7
│   ├── pipeline.py          # Task 8
│   └── cli.py               # Task 9
├── tests/
│   ├── conftest.py          # 合成测试视频 fixture
│   └── test_*.py
├── avatars/                 # P3 建库；P1 放一个假形象目录供测试
├── jobs/                    # gitignore
├── config.example.yaml
├── .env.example
├── requirements.txt
└── docs/plans/
```

---

### Task 0: 脚手架

**Files:**
- Create: `requirements.txt`, `config.example.yaml`, `.env.example`, `.gitignore`, `core/__init__.py`, `core/providers/__init__.py`, `tests/__init__.py`

**Step 1: 写脚手架文件**

`requirements.txt`:
```
requests>=2.31
PyYAML>=6.0
pytest>=8.0
```

`.gitignore`:
```
jobs/
.env
__pycache__/
*.pyc
.pytest_cache/
```

`config.example.yaml`:
```yaml
# 复制为 config.yaml 后填写。API key 不放这里，放 .env / 环境变量 ARK_API_KEY
ark:
  base_url: "https://ark.cn-beijing.volces.com/api/v3"
  vlm_model: "doubao-1-5-vision-pro-32k"      # Task 11 按官方文档核对最新模型ID
  video_model: "doubao-seedance-pro"           # Task 11 按官方文档核对（需支持参考视频+元素参考）
pipeline:
  frame_interval: 1.0        # 打轴抽帧间隔（秒）
  segment_max: 15.0          # Seedance 参考视频上限
  buffer: 0.5                # 命中时段外扩缓冲
  scene_align_tolerance: 2.0 # 镜头切点对齐搜索半径（秒）
  duration_drift_pct: 2.0    # 替换段时长偏差超此百分比则变速对齐
limits:
  max_video_seconds: 60
  max_video_mb: 200
```

`.env.example`:
```
ARK_API_KEY=your-volcano-ark-api-key
```

**Step 2: 验证 ffmpeg 可用**

Run: `ffmpeg -version | head -1 && ffprobe -version | head -1`
Expected: 打出版本号。若无 → 停下向用户报告（不要自己装）。

**Step 3: Commit**
```bash
cd /c/ADHD_agent && git add avatar-replace && git commit -m "chore(avatar-replace): P1 脚手架"
```

---

### Task 1: config.py

**Files:**
- Create: `core/config.py`
- Test: `tests/test_config.py`

**Step 1: 写失败测试**

```python
# tests/test_config.py
from pathlib import Path
from core.config import load_config

def test_load_config_merges_env_key(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "ark:\n  base_url: 'http://x'\n  vlm_model: m1\n  video_model: m2\n"
        "pipeline:\n  frame_interval: 1.0\n  segment_max: 15.0\n  buffer: 0.5\n"
        "  scene_align_tolerance: 2.0\n  duration_drift_pct: 2.0\n"
        "limits:\n  max_video_seconds: 60\n  max_video_mb: 200\n",
        encoding="utf-8")
    monkeypatch.setenv("ARK_API_KEY", "sk-test")
    cfg = load_config(cfg_file)
    assert cfg.ark.api_key == "sk-test"
    assert cfg.pipeline.segment_max == 15.0

def test_missing_key_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("ARK_API_KEY", raising=False)
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("ark: {base_url: x, vlm_model: a, video_model: b}", encoding="utf-8")
    import pytest
    with pytest.raises(RuntimeError, match="ARK_API_KEY"):
        load_config(cfg_file, require_key=True)
```

**Step 2:** Run `python -m pytest tests/test_config.py -v` → FAIL (module not found)

**Step 3: 实现**

```python
# core/config.py
import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class ArkCfg:
    base_url: str
    vlm_model: str
    video_model: str
    api_key: str = ""

@dataclass
class PipelineCfg:
    frame_interval: float = 1.0
    segment_max: float = 15.0
    buffer: float = 0.5
    scene_align_tolerance: float = 2.0
    duration_drift_pct: float = 2.0

@dataclass
class LimitsCfg:
    max_video_seconds: int = 60
    max_video_mb: int = 200

@dataclass
class Config:
    ark: ArkCfg
    pipeline: PipelineCfg = field(default_factory=PipelineCfg)
    limits: LimitsCfg = field(default_factory=LimitsCfg)

def load_config(path: Path | str = "config.yaml", require_key: bool = False) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    key = os.environ.get("ARK_API_KEY", "")
    if require_key and not key:
        raise RuntimeError("缺少 ARK_API_KEY 环境变量（.env）")
    return Config(
        ark=ArkCfg(api_key=key, **raw["ark"]),
        pipeline=PipelineCfg(**raw.get("pipeline", {})),
        limits=LimitsCfg(**raw.get("limits", {})),
    )
```

**Step 4:** Run 同上 → PASS
**Step 5:** Commit `feat(avatar-replace): config 加载`

---

### Task 2: media.py（ffmpeg 底层）

**Files:**
- Create: `core/media.py`
- Test: `tests/conftest.py`, `tests/test_media.py`

**Step 1: conftest 合成测试视频**（本地 ffmpeg lavfi，非 AI 生成）

```python
# tests/conftest.py
import subprocess, pytest
from pathlib import Path

@pytest.fixture(scope="session")
def sample_video(tmp_path_factory) -> Path:
    """20s 彩条+正弦音，带 5s/12s 两个画面突变（当镜头切点用）"""
    out = tmp_path_factory.mktemp("media") / "sample.mp4"
    parts = []
    d = tmp_path_factory.mktemp("media_parts")
    for i, (color, dur) in enumerate([("red", 5), ("blue", 7), ("green", 8)]):
        p = d / f"p{i}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=640x360:r=25:d={dur}",
            "-f", "lavfi", "-i", f"sine=frequency={220*(i+1)}:duration={dur}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(p)],
            check=True, capture_output=True)
        parts.append(p)
    lst = d / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(out)], check=True, capture_output=True)
    return out
```

**Step 2: 写失败测试**

```python
# tests/test_media.py
from core import media

def test_probe(sample_video):
    info = media.probe(sample_video)
    assert 19.5 < info.duration < 20.5
    assert info.width == 640 and info.has_audio

def test_extract_frames(sample_video, tmp_path):
    frames = media.extract_frames(sample_video, tmp_path, interval=2.0)
    assert 9 <= len(frames) <= 11
    assert all(f.path.exists() and f.t >= 0 for f in frames)

def test_scene_cuts(sample_video):
    cuts = media.scene_cuts(sample_video)
    assert any(abs(c - 5) < 0.5 for c in cuts)
    assert any(abs(c - 12) < 0.5 for c in cuts)

def test_cut_clip(sample_video, tmp_path):
    seg = tmp_path / "seg.mp4"
    media.cut_clip(sample_video, seg, 2.0, 6.0)
    assert abs(media.probe(seg).duration - 4.0) < 0.2
```

**Step 3:** Run → FAIL

**Step 4: 实现**

```python
# core/media.py
import json, re, subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MediaInfo:
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool

@dataclass
class Frame:
    t: float
    path: Path

def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r

def probe(path: Path | str) -> MediaInfo:
    r = _run(["ffprobe", "-v", "quiet", "-print_format", "json",
              "-show_format", "-show_streams", str(path)])
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = (v.get("avg_frame_rate") or "25/1").split("/")
    return MediaInfo(
        duration=float(d["format"]["duration"]),
        width=int(v["width"]), height=int(v["height"]),
        fps=float(num) / float(den or 1),
        has_audio=any(s["codec_type"] == "audio" for s in d["streams"]))

def extract_frames(path: Path | str, out_dir: Path, interval: float = 1.0) -> list[Frame]:
    out_dir.mkdir(parents=True, exist_ok=True)
    _run(["ffmpeg", "-y", "-i", str(path), "-vf", f"fps=1/{interval}",
          "-q:v", "3", str(out_dir / "f_%05d.jpg")])
    frames = sorted(out_dir.glob("f_*.jpg"))
    return [Frame(t=i * interval, path=p) for i, p in enumerate(frames)]

def scene_cuts(path: Path | str, threshold: float = 0.3) -> list[float]:
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',showinfo",
         "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]

def cut_clip(src: Path | str, dst: Path, start: float, end: float) -> None:
    # 重编码保帧精确；统一编码参数便于后续 concat
    _run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src),
          "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
          "-c:a", "aac", str(dst)])

def concat(parts: list[Path], dst: Path) -> None:
    lst = dst.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)])

def replace_audio(video: Path, audio_src: Path, dst: Path) -> None:
    """视频轨用 video，音轨整条用 audio_src 的（原片），时长以视频为准"""
    _run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio_src),
          "-map", "0:v", "-map", "1:a?", "-c:v", "copy", "-c:a", "aac",
          "-shortest", str(dst)])

def retime(src: Path, dst: Path, factor: float) -> None:
    """factor>1 拉长。仅动视频 PTS 后重编码（无音轨段用）"""
    _run(["ffmpeg", "-y", "-i", str(src), "-vf", f"setpts={factor}*PTS", "-an",
          "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", str(dst)])
```

**Step 5:** Run → PASS（scene_cuts 阈值不中就调 threshold，彩条突变很明显应该稳过）
**Step 6:** Commit `feat(avatar-replace): ffmpeg 媒体底层封装`

---

### Task 3: Provider 抽象 + 火山方舟实现

**Files:**
- Create: `core/providers/base.py`, `core/providers/volc.py`
- Test: `tests/test_volc.py`

**Step 1: base.py（先写抽象 + FakeProvider，供集成测试）**

```python
# core/providers/base.py
from abc import ABC, abstractmethod
from pathlib import Path

class Provider(ABC):
    @abstractmethod
    def chat_vision(self, prompt: str, image_paths: list[Path]) -> str: ...
    @abstractmethod
    def video_edit(self, prompt: str, video_path: Path,
                   ref_images: list[Path], out_path: Path) -> Path:
        """参考视频+元素参考 → 生成替换后视频，下载到 out_path"""

class FakeProvider(Provider):
    """零 API 假实现：chat_vision 按预置脚本回答；video_edit 原样拷贝输入段"""
    def __init__(self, vision_responses: list[str] | None = None):
        self._responses = list(vision_responses or [])
        self.vision_calls: list[str] = []
        self.edit_calls: list[str] = []
    def chat_vision(self, prompt, image_paths):
        self.vision_calls.append(prompt)
        return self._responses.pop(0) if self._responses else "[]"
    def video_edit(self, prompt, video_path, ref_images, out_path):
        self.edit_calls.append(prompt)
        import shutil; shutil.copy(video_path, out_path)
        return out_path
```

**Step 2: 写 volc 失败测试（mock requests，不发真网络）**

```python
# tests/test_volc.py
from pathlib import Path
from core.config import ArkCfg
from core.providers.volc import VolcProvider

class FakeResp:
    def __init__(self, payload, status=200):
        self._p, self.status_code = payload, status
    def json(self): return self._p
    @property
    def content(self): return b"fakevideo"
    def raise_for_status(self):
        if self.status_code >= 400: raise RuntimeError(self.status_code)

def test_chat_vision_builds_multimodal_payload(monkeypatch, tmp_path):
    img = tmp_path / "a.jpg"; img.write_bytes(b"\xff\xd8fake")
    sent = {}
    def fake_post(url, json=None, headers=None, timeout=None):
        sent.update(url=url, json=json, headers=headers)
        return FakeResp({"choices": [{"message": {"content": "ok"}}]})
    monkeypatch.setattr("requests.post", fake_post)
    p = VolcProvider(ArkCfg(base_url="http://ark", vlm_model="vlm", video_model="vid", api_key="sk"))
    assert p.chat_vision("看图", [img]) == "ok"
    assert sent["headers"]["Authorization"] == "Bearer sk"
    types = [c["type"] for c in sent["json"]["messages"][0]["content"]]
    assert types == ["text", "image_url"]
    assert sent["json"]["messages"][0]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,")

def test_video_edit_submits_polls_downloads(monkeypatch, tmp_path):
    vid = tmp_path / "seg.mp4"; vid.write_bytes(b"v"); ref = tmp_path / "r.png"; ref.write_bytes(b"i")
    calls = {"n": 0}
    def fake_post(url, json=None, headers=None, timeout=None):
        return FakeResp({"id": "task-1"})
    def fake_get(url, headers=None, timeout=None):
        calls["n"] += 1
        if url.endswith("task-1"):
            if calls["n"] < 2:
                return FakeResp({"status": "running"})
            return FakeResp({"status": "succeeded",
                             "content": {"video_url": "http://cdn/out.mp4"}})
        return FakeResp({})  # 下载
    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr("time.sleep", lambda s: None)
    p = VolcProvider(ArkCfg(base_url="http://ark", vlm_model="vlm", video_model="vid", api_key="sk"))
    out = p.video_edit("换人", vid, [ref], tmp_path / "out.mp4")
    assert out.read_bytes() == b"fakevideo"
```

**Step 3:** Run → FAIL

**Step 4: 实现 volc.py**

```python
# core/providers/volc.py
import base64, mimetypes, time
from pathlib import Path
import requests
from core.config import ArkCfg
from core.providers.base import Provider

class VolcProvider(Provider):
    """火山方舟。⚠️ 端点/字段以 Task 11 核对的官方文档为准，本实现按方舟 v3 通用契约编写。"""
    POLL_INTERVAL = 5
    POLL_TIMEOUT = 900

    def __init__(self, cfg: ArkCfg):
        self.cfg = cfg
        self.headers = {"Authorization": f"Bearer {cfg.api_key}"}

    @staticmethod
    def _data_url(path: Path) -> str:
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

    def chat_vision(self, prompt: str, image_paths: list[Path]) -> str:
        content = [{"type": "text", "text": prompt}] + [
            {"type": "image_url", "image_url": {"url": self._data_url(p)}} for p in image_paths]
        r = requests.post(f"{self.cfg.base_url}/chat/completions", headers=self.headers,
                          json={"model": self.cfg.vlm_model,
                                "messages": [{"role": "user", "content": content}]},
                          timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def video_edit(self, prompt, video_path, ref_images, out_path: Path) -> Path:
        content = [{"type": "text", "text": prompt},
                   {"type": "video_url", "video_url": {"url": self._data_url(video_path)}}] + [
                   {"type": "image_url", "image_url": {"url": self._data_url(p)}} for p in ref_images]
        r = requests.post(f"{self.cfg.base_url}/contents/generations/tasks",
                          headers=self.headers,
                          json={"model": self.cfg.video_model, "content": content}, timeout=120)
        r.raise_for_status()
        task_id = r.json()["id"]
        deadline = time.time() + self.POLL_TIMEOUT
        while True:
            if time.time() > deadline:
                raise TimeoutError(f"video task {task_id} 超时")
            s = requests.get(f"{self.cfg.base_url}/contents/generations/tasks/{task_id}",
                             headers=self.headers, timeout=60)
            s.raise_for_status()
            d = s.json()
            if d["status"] == "succeeded":
                url = d["content"]["video_url"]; break
            if d["status"] in ("failed", "cancelled"):
                raise RuntimeError(f"video task {task_id} 失败: {d}")
            time.sleep(self.POLL_INTERVAL)
        out_path.write_bytes(requests.get(url, timeout=300).content)
        return out_path
```

**Step 5:** Run → PASS
**Step 6:** Commit `feat(avatar-replace): Provider 抽象 + 火山方舟实现(mock测试)`

---

### Task 4: annotate.py（打轴）

**Files:**
- Create: `core/annotate.py`
- Test: `tests/test_annotate.py`

**逻辑:** 抽帧 → **粗扫**（每批 ≤8 帧带时间戳送 VLM，问「哪些帧含疑似未成年人」，回 JSON 帧索引）→ 相邻命中帧合并为时段（间隔 ≤2×interval 视为连续）→ **细化**（每时段取中间样帧，问外观描述）→ timeline JSON。

**Step 1: 写失败测试**

```python
# tests/test_annotate.py
import json
from core.annotate import annotate, merge_hits
from core.providers.base import FakeProvider

def test_merge_hits():
    # 帧时间 0..9，命中 2,3,4 和 8 → 两个时段
    spans = merge_hits([2.0, 3.0, 4.0, 8.0], interval=1.0)
    assert spans == [(2.0, 5.0), (8.0, 9.0)]  # 末端 +interval

def test_annotate_two_pass(sample_video, tmp_path):
    fake = FakeProvider(vision_responses=[
        json.dumps({"hits": [2, 3, 4]}),          # 粗扫批1 (0-7s帧)
        json.dumps({"hits": []}),                  # 粗扫批2
        json.dumps({"hits": []}),                  # 粗扫批3(若有)
        "画面中央穿红色T恤的男孩，约8岁，在奔跑",     # 细化
    ])
    tl = annotate(sample_video, tmp_path, provider=fake, interval=1.0)
    assert len(tl) == 1
    assert tl[0]["start"] == 2.0 and tl[0]["end"] == 5.0
    assert "红色T恤" in tl[0]["person_desc"]
    assert tl[0]["sample_frame"]
    # 粗扫 prompt 必须要求 JSON 输出
    assert "JSON" in fake.vision_calls[0]
```

（FakeProvider 回复条数按 20s/1fps/8帧一批=3批 调整，多余的空 hits 不碍事——`annotate` 按需 pop。）

**Step 2:** Run → FAIL

**Step 3: 实现**

```python
# core/annotate.py
import json, re
from pathlib import Path
from core import media
from core.providers.base import Provider

COARSE_PROMPT = """你在做广告素材合规审查。下面按顺序给出视频抽帧（第0张对应索引0）。
找出画面中出现疑似未成年人（看起来不满18岁的真人）的帧。
只输出 JSON：{"hits": [命中的帧索引数组]}，没有则 {"hits": []}。"""

DETAIL_PROMPT = """这是广告视频中出现未成年人的画面。用一句话描述这个未成年人，
供后续视频编辑指令定位使用，格式如「画面左侧穿蓝色连衣裙的女孩，约6岁，正在挥手」。
如有多个未成年人，逐个描述用分号隔开。只输出描述本身。"""

BATCH = 8

def merge_hits(hit_times: list[float], interval: float) -> list[tuple[float, float]]:
    if not hit_times:
        return []
    spans, start, prev = [], hit_times[0], hit_times[0]
    for t in hit_times[1:]:
        if t - prev <= 2 * interval:
            prev = t
        else:
            spans.append((start, prev + interval)); start = prev = t
    spans.append((start, prev + interval))
    return spans

def _parse_hits(text: str) -> list[int]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        return [int(i) for i in json.loads(m.group())["hits"]]
    except Exception:
        return []

def annotate(video: Path, workdir: Path, provider: Provider, interval: float = 1.0) -> list[dict]:
    frames = media.extract_frames(video, workdir / "frames", interval=interval)
    hit_times = []
    for i in range(0, len(frames), BATCH):
        batch = frames[i:i + BATCH]
        resp = provider.chat_vision(COARSE_PROMPT, [f.path for f in batch])
        for idx in _parse_hits(resp):
            if 0 <= idx < len(batch):
                hit_times.append(batch[idx].t)
    timeline = []
    for start, end in merge_hits(sorted(hit_times), interval):
        mid = min(frames, key=lambda f: abs(f.t - (start + end) / 2))
        desc = provider.chat_vision(DETAIL_PROMPT, [mid.path]).strip()
        timeline.append({"start": start, "end": end,
                         "person_desc": desc, "sample_frame": str(mid.path),
                         "confirmed": False})
    (workdir / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline
```

**Step 4:** Run → PASS
**Step 5:** Commit `feat(avatar-replace): VLM 两遍打轴`

---

### Task 5: cut.py（切段规划 + 执行）

**Files:**
- Create: `core/cut.py`
- Test: `tests/test_cut.py`

**逻辑:** 确认后的时段 → 外扩 buffer → 吸附到 tolerance 内最近镜头切点 → 与视频首尾裁剪 → 时段间重叠合并 → 生成全片分段计划 `[{start,end,mode:keep|replace,desc}]`（首尾相接覆盖全片）→ replace 段 >15s 二分 → ffmpeg 切出所有段。

**Step 1: 写失败测试**

```python
# tests/test_cut.py
from core.cut import plan_segments, execute_cut
from core import media

def test_plan_basic():
    tl = [{"start": 2.0, "end": 5.0, "person_desc": "红衣男孩", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[5.0, 12.0],
                         buffer=0.5, tolerance=2.0, segment_max=15.0)
    # 2.0-0.5=1.5 无切点可吸附→1.5；末端 5.5 吸附到切点 5.0? 5.0<5.5 且在tolerance内但会截掉命中区→只向外吸附→保持5.5
    assert [s["mode"] for s in segs] == ["keep", "replace", "keep"]
    assert segs[0]["start"] == 0.0 and segs[-1]["end"] == 20.0
    r = segs[1]
    assert r["start"] <= 1.5 and r["end"] >= 5.5

def test_plan_split_over_15s():
    tl = [{"start": 0.0, "end": 18.0, "person_desc": "x", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.0,
                         tolerance=0.0, segment_max=15.0)
    rep = [s for s in segs if s["mode"] == "replace"]
    assert len(rep) == 2 and all(s["end"] - s["start"] <= 15.0 for s in rep)

def test_plan_skips_unconfirmed():
    tl = [{"start": 2.0, "end": 5.0, "person_desc": "x", "confirmed": False}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.5,
                         tolerance=2.0, segment_max=15.0)
    assert all(s["mode"] == "keep" for s in segs)

def test_execute_cut(sample_video, tmp_path):
    segs = [{"start": 0.0, "end": 6.0, "mode": "keep"},
            {"start": 6.0, "end": 11.0, "mode": "replace", "desc": "x"},
            {"start": 11.0, "end": 20.0, "mode": "keep"}]
    out = execute_cut(sample_video, segs, tmp_path)
    assert len(out) == 3
    assert abs(media.probe(out[1]["path"]).duration - 5.0) < 0.3
```

**Step 2:** Run → FAIL

**Step 3: 实现**

```python
# core/cut.py
from pathlib import Path
from core import media

def _snap_out(t: float, cuts: list[float], tolerance: float, direction: int) -> float:
    """只向外吸附（direction=-1 起点向前 / +1 终点向后），避免截掉命中区"""
    cand = [c for c in cuts
            if (direction < 0 and t - tolerance <= c <= t) or
               (direction > 0 and t <= c <= t + tolerance)]
    return (min(cand) if direction < 0 else max(cand)) if cand else t

def plan_segments(timeline, duration, scene_cuts, buffer, tolerance, segment_max):
    spans = []
    for item in timeline:
        if not item.get("confirmed"):
            continue
        s = _snap_out(max(0.0, item["start"] - buffer), scene_cuts, tolerance, -1)
        e = _snap_out(min(duration, item["end"] + buffer), scene_cuts, tolerance, +1)
        spans.append([s, e, item["person_desc"]])
    spans.sort()
    merged = []
    for s, e, d in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
            merged[-1][2] = merged[-1][2] if d in merged[-1][2] else merged[-1][2] + "；" + d
        else:
            merged.append([s, e, d])
    segs, cursor = [], 0.0
    for s, e, d in merged:
        if s > cursor:
            segs.append({"start": cursor, "end": s, "mode": "keep"})
        n = 1
        while (e - s) / n > segment_max:
            n += 1
        step = (e - s) / n
        for i in range(n):
            segs.append({"start": s + i * step, "end": s + (i + 1) * step,
                         "mode": "replace", "desc": d})
        cursor = e
    if cursor < duration:
        segs.append({"start": cursor, "end": duration, "mode": "keep"})
    return segs

def execute_cut(video: Path, segs: list[dict], workdir: Path) -> list[dict]:
    seg_dir = workdir / "segs"
    seg_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for i, s in enumerate(segs):
        p = seg_dir / f"{i:03d}_{s['mode']}.mp4"
        media.cut_clip(video, p, s["start"], s["end"])
        out.append({**s, "path": p})
    return out
```

**Step 4:** Run → PASS（`test_plan_basic` 的吸附断言若与实现有出入，以「只向外吸附、绝不截掉命中区」为原则修测试）
**Step 5:** Commit `feat(avatar-replace): 切段规划(镜头对齐/15s二分)+执行`

---

### Task 6: replace.py

**Files:**
- Create: `core/replace.py`
- Test: `tests/test_replace.py`

**Step 1: 写失败测试**

```python
# tests/test_replace.py
from pathlib import Path
from core.replace import build_prompt, replace_segment
from core.providers.base import FakeProvider

def test_build_prompt():
    p = build_prompt("画面左侧穿蓝裙的女孩，约6岁")
    assert "视频1" in p and "图片1" in p and "蓝裙" in p
    assert "运镜" in p  # 必须锁运镜

def test_replace_segment(tmp_path):
    seg = tmp_path / "seg.mp4"; seg.write_bytes(b"v")
    refs = [tmp_path / "front.png"]; refs[0].write_bytes(b"i")
    fake = FakeProvider()
    out = replace_segment(fake, seg, "红衣男孩", refs, tmp_path / "out")
    assert out.exists()
    assert "红衣男孩" in fake.edit_calls[0]
```

**Step 2:** Run → FAIL

**Step 3: 实现**

```python
# core/replace.py
from pathlib import Path
from core.providers.base import Provider

PROMPT_TMPL = (
    "将视频1中的{desc}替换为图片1中的数字人形象，"
    "数字人的外观、服装、比例严格以参考图片为准。"
    "视频中其余人物、场景、光线、运镜、动作节奏完全保持不变，"
    "替换后人物的动作与原人物动作保持一致。"
)

def build_prompt(person_desc: str) -> str:
    return PROMPT_TMPL.format(desc=person_desc)

def replace_segment(provider: Provider, seg_path: Path, person_desc: str,
                    avatar_refs: list[Path], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / seg_path.name.replace("_replace", "_replaced")
    return provider.video_edit(build_prompt(person_desc), seg_path, avatar_refs, out)
```

**Step 4:** Run → PASS
**Step 5:** Commit `feat(avatar-replace): 段替换+prompt模板`

---

### Task 7: stitch.py

**Files:**
- Create: `core/stitch.py`
- Test: `tests/test_stitch.py`

**逻辑:** 替换段时长校验（偏差 > drift_pct → `media.retime` 变速对齐原段时长）→ 所有段统一重编码参数已在 cut/retime 保证 → concat → 原片音轨整条铺回。

**Step 1: 写失败测试**

```python
# tests/test_stitch.py
from core.stitch import stitch
from core import media

def test_stitch_full_length(sample_video, tmp_path):
    segs = []
    for i, (s, e) in enumerate([(0, 6), (6, 11), (11, 20)]):
        p = tmp_path / f"{i:03d}.mp4"
        media.cut_clip(sample_video, p, s, e)
        segs.append({"path": p, "start": float(s), "end": float(e),
                     "mode": "replace" if i == 1 else "keep"})
    final = stitch(segs, original=sample_video, workdir=tmp_path, drift_pct=2.0)
    info = media.probe(final)
    assert abs(info.duration - 20.0) < 0.5
    assert info.has_audio

def test_stitch_retimes_drifted_segment(sample_video, tmp_path, monkeypatch):
    # 中段替换结果被人为拉长 20% → 应触发 retime 回到 ~5s
    segs = []
    for i, (s, e) in enumerate([(0, 6), (6, 11), (11, 20)]):
        p = tmp_path / f"{i:03d}.mp4"
        media.cut_clip(sample_video, p, s, e)
        segs.append({"path": p, "start": float(s), "end": float(e),
                     "mode": "replace" if i == 1 else "keep"})
    drift = tmp_path / "drift.mp4"
    media.retime(segs[1]["path"], drift, factor=1.2)
    segs[1]["path"] = drift
    final = stitch(segs, original=sample_video, workdir=tmp_path, drift_pct=2.0)
    assert abs(media.probe(final).duration - 20.0) < 0.5
```

**Step 2:** Run → FAIL

**Step 3: 实现**

```python
# core/stitch.py
from pathlib import Path
from core import media

def stitch(segs: list[dict], original: Path, workdir: Path, drift_pct: float = 2.0) -> Path:
    fixed = []
    for i, s in enumerate(segs):
        expect = s["end"] - s["start"]
        actual = media.probe(s["path"]).duration
        if s["mode"] == "replace" and abs(actual - expect) / expect * 100 > drift_pct:
            adj = workdir / f"retime_{i:03d}.mp4"
            media.retime(s["path"], adj, factor=expect / actual)
            fixed.append(adj)
        else:
            fixed.append(Path(s["path"]))
    joined = workdir / "joined.mp4"
    media.concat(fixed, joined)
    final = workdir / "final.mp4"
    media.replace_audio(joined, original, final)
    return final
```

⚠️ 注意：replace 段经 `retime` 后无音轨、keep 段有音轨，concat `-c copy` 混流可能报错。若 Step 4 遇到 → 在 `execute_cut`/`retime` 统一都 `-an` 去音轨（反正最后整条铺原片音轨），`cut_clip` 加 `-an` 即可，同步修 Task 2 的 `test_cut_clip`（不再断言音轨）。

**Step 4:** Run → PASS
**Step 5:** Commit `feat(avatar-replace): 拼回+时长对齐+原音轨铺回`

---

### Task 8: pipeline.py（状态机 + 断点续跑）

**Files:**
- Create: `core/pipeline.py`
- Test: `tests/test_pipeline.py`

**状态:** `created → annotated → confirmed → cut → replacing → stitched(done)`；段级状态存 `job.json` 的 `segments[i].status`（pending/done/failed），续跑跳过 done。

**Step 1: 写失败测试**

```python
# tests/test_pipeline.py
import json
from pathlib import Path
from core.pipeline import Job
from core.providers.base import FakeProvider
from core.config import Config, ArkCfg, PipelineCfg, LimitsCfg

def _cfg():
    return Config(ark=ArkCfg(base_url="x", vlm_model="a", video_model="b"),
                  pipeline=PipelineCfg(), limits=LimitsCfg())

def test_full_run_with_fake_provider(sample_video, tmp_path):
    fake = FakeProvider(vision_responses=[
        json.dumps({"hits": [6, 7]}), json.dumps({"hits": []}), json.dumps({"hits": []}),
        "红色T恤男孩",
    ])
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    job.annotate(fake)
    assert job.state == "annotated" and len(job.timeline) == 1
    for item in job.timeline:
        item["confirmed"] = True
    job.confirm()
    job.run(fake, avatar_refs=[])          # cut → replace → stitch
    assert job.state == "done"
    assert (job.dir / "final.mp4").exists()

def test_resume_skips_done_segments(sample_video, tmp_path):
    fake = FakeProvider(vision_responses=[
        json.dumps({"hits": [6, 7]}), json.dumps({"hits": []}), json.dumps({"hits": []}),
        "男孩"])
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    job.annotate(fake)
    for item in job.timeline: item["confirmed"] = True
    job.confirm()
    job.run(fake, avatar_refs=[])
    # 重新加载同一 job，再 run：不应产生新的 video_edit 调用
    fake2 = FakeProvider()
    job2 = Job.load(job.dir, cfg=_cfg())
    job2.run(fake2, avatar_refs=[])
    assert fake2.edit_calls == []
```

**Step 2:** Run → FAIL

**Step 3: 实现**

```python
# core/pipeline.py
import json, shutil, time, uuid
from pathlib import Path
from core import media, annotate as ann, cut as cutmod, replace as repmod, stitch as stitchmod
from core.config import Config
from core.providers.base import Provider

class Job:
    def __init__(self, jdir: Path, cfg: Config):
        self.dir, self.cfg = jdir, cfg
        self._meta = json.loads((jdir / "job.json").read_text(encoding="utf-8"))

    # ---- 属性 ----
    @property
    def state(self): return self._meta["state"]
    @property
    def timeline(self): return self._meta["timeline"]
    def _save(self):
        (self.dir / "job.json").write_text(
            json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 生命周期 ----
    @classmethod
    def create(cls, video: Path, jobs_root: Path, cfg: Config) -> "Job":
        info = media.probe(video)
        if info.duration > cfg.limits.max_video_seconds:
            raise ValueError(f"视频 {info.duration:.0f}s 超上限 {cfg.limits.max_video_seconds}s")
        jid = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        jdir = jobs_root / jid
        jdir.mkdir(parents=True)
        shutil.copy(video, jdir / "source.mp4")
        (jdir / "job.json").write_text(json.dumps({
            "id": jid, "state": "created", "duration": info.duration,
            "timeline": [], "segments": []}, ensure_ascii=False), encoding="utf-8")
        return cls(jdir, cfg)

    @classmethod
    def load(cls, jdir: Path, cfg: Config) -> "Job":
        return cls(jdir, cfg)

    def annotate(self, provider: Provider):
        self._meta["timeline"] = ann.annotate(
            self.dir / "source.mp4", self.dir, provider,
            interval=self.cfg.pipeline.frame_interval)
        self._meta["state"] = "annotated"; self._save()

    def confirm(self):
        if not any(t.get("confirmed") for t in self._meta["timeline"]):
            raise ValueError("没有已确认的时段")
        self._meta["state"] = "confirmed"; self._save()

    def run(self, provider: Provider, avatar_refs: list[Path]):
        p = self.cfg.pipeline
        src = self.dir / "source.mp4"
        if not self._meta["segments"]:
            segs = cutmod.plan_segments(
                self._meta["timeline"], self._meta["duration"],
                media.scene_cuts(src), p.buffer, p.scene_align_tolerance, p.segment_max)
            cut_out = cutmod.execute_cut(src, segs, self.dir)
            self._meta["segments"] = [
                {**{k: v for k, v in s.items() if k != "path"},
                 "path": str(s["path"]), "status": "pending"} for s in cut_out]
            self._meta["state"] = "cut"; self._save()
        for s in self._meta["segments"]:
            if s["mode"] != "replace" or s["status"] == "done":
                continue
            out = repmod.replace_segment(
                provider, Path(s["path"]), s.get("desc", ""), avatar_refs, self.dir / "out")
            s["path"] = str(out); s["status"] = "done"; self._save()
        final = stitchmod.stitch(
            [{**s, "path": Path(s["path"])} for s in self._meta["segments"]],
            original=src, workdir=self.dir, drift_pct=p.duration_drift_pct)
        self._meta["state"] = "done"; self._meta["final"] = str(final); self._save()
```

（注意 keep 段 status 初始也是 pending 但永不置 done——续跑判断只看 replace 段，测试2里 fake2.edit_calls 为空的关键是所有 replace 段已 done。）

**Step 4:** Run → PASS
**Step 5:** Commit `feat(avatar-replace): 任务状态机+断点续跑`

---

### Task 9: cli.py

**Files:**
- Create: `core/cli.py`
- Test: `tests/test_cli.py`（只测参数解析路由，业务已被上层测过）

**命令设计:**
```
python -m core.cli annotate <video>                 # 建任务+打轴，打印 job_id 和 timeline
python -m core.cli confirm <job_id> --all           # P1 简化：--all 全确认，或 --spans 0,2 选择性确认
python -m core.cli run <job_id> --avatar <形象名>    # 切段+替换+拼回
python -m core.cli status <job_id>
```

**Step 1: 写失败测试**

```python
# tests/test_cli.py
from core.cli import build_parser

def test_parser_routes():
    p = build_parser()
    a = p.parse_args(["annotate", "v.mp4"])
    assert a.cmd == "annotate" and a.video == "v.mp4"
    a = p.parse_args(["confirm", "jid", "--all"])
    assert a.cmd == "confirm" and a.all
    a = p.parse_args(["run", "jid", "--avatar", "girl_a"])
    assert a.avatar == "girl_a"
```

**Step 2:** Run → FAIL

**Step 3: 实现**

```python
# core/cli.py
import argparse, json, sys
from pathlib import Path
from core.config import load_config
from core.pipeline import Job

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"

def build_parser():
    p = argparse.ArgumentParser(prog="avatar-replace")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("annotate"); a.add_argument("video")
    c = sub.add_parser("confirm"); c.add_argument("job_id")
    c.add_argument("--all", action="store_true"); c.add_argument("--spans", default="")
    r = sub.add_parser("run"); r.add_argument("job_id"); r.add_argument("--avatar", required=True)
    s = sub.add_parser("status"); s.add_argument("job_id")
    return p

def _provider(cfg):
    from core.providers.volc import VolcProvider
    return VolcProvider(cfg.ark)

def main(argv=None):
    args = build_parser().parse_args(argv)
    cfg = load_config(ROOT / "config.yaml", require_key=(args.cmd in ("annotate", "run")))
    if args.cmd == "annotate":
        job = Job.create(Path(args.video), JOBS, cfg)
        job.annotate(_provider(cfg))
        print(f"job: {job.dir.name}")
        print(json.dumps(job.timeline, ensure_ascii=False, indent=2))
    elif args.cmd == "confirm":
        job = Job.load(JOBS / args.job_id, cfg)
        picks = set(range(len(job.timeline))) if args.all else \
                {int(i) for i in args.spans.split(",") if i.strip()}
        for i, t in enumerate(job.timeline):
            t["confirmed"] = i in picks
        job.confirm(); print(f"confirmed: {sorted(picks)}")
    elif args.cmd == "run":
        job = Job.load(JOBS / args.job_id, cfg)
        refs = sorted((ROOT / "avatars" / args.avatar).glob("*.png")) + \
               sorted((ROOT / "avatars" / args.avatar).glob("*.jpg"))
        if not refs:
            sys.exit(f"形象 {args.avatar} 无参考图（avatars/{args.avatar}/*.png|jpg）")
        job.run(_provider(cfg), avatar_refs=refs)
        print(f"done: {job._meta['final']}")
    elif args.cmd == "status":
        job = Job.load(JOBS / args.job_id, cfg)
        print(json.dumps({k: job._meta[k] for k in ("id", "state")} |
              {"segments": [(s["mode"], s["status"]) for s in job._meta["segments"]]},
              ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

**Step 4:** Run → PASS；再跑全量 `python -m pytest tests/ -v` → 全 PASS
**Step 5:** Commit `feat(avatar-replace): CLI 入口`

---

### Task 10: 全链路集成冒烟（零 API）

**Step 1:** 放一个假形象：`avatars/_test/front.png`（任意小图，ffmpeg 生成：`ffmpeg -f lavfi -i color=c=pink:s=256x256:d=1 -frames:v 1 avatars/_test/front.png`）

**Step 2:** 写一次性脚本（scratchpad，不进仓）用 `FakeProvider` 从 `Job.create` 走到 `done`，输入用 conftest 同款合成视频，验证 `final.mp4` 时长 ≈ 源片、有音轨。

**Step 3:** 跑通后删脚本，Commit（若有修复）`fix(avatar-replace): 集成冒烟修复`

---

### Task 11: 真实 API 契约核对 + 用户冒烟清单（文档任务，不发调用）

**Files:**
- Create: `docs/SMOKE.md`

**Step 1:** WebFetch 火山引擎方舟官方文档（豆包 VLM chat/completions、Seedance 视频生成任务 API），核对 `volc.py` 的：端点路径、请求字段名（`content` 数组里 video_url/image_url 的确切结构、参考类型字段）、任务状态字段值、结果 URL 字段、模型 ID。发现出入 → 修 `volc.py` + `config.example.yaml` + mock 测试，单独 commit。
⚠️ 重点核对 Seedance「参考视频+元素参考」的 API 表达方式（GRFal 里的 `ref_types` 是 GRFal 自己的抽象，方舟原生 API 字段大概率不同）。

**Step 2:** 写 `docs/SMOKE.md` 用户冒烟清单：
1. 火山引擎开通方舟 → 建推理接入点（VLM + Seedance）→ 子账号 key 最小权限 → **控制台设消费限额+预警**
2. `cp config.example.yaml config.yaml` 填模型 ID；`.env` 填 `ARK_API_KEY`
3. 拿一条 ≤60s 真素材：`annotate → confirm → run`
4. 验收四点：打轴准确率 / 形象跨段一致性 / 非替换区保真 / 音画同步
5. 效果不行的调参抓手：prompt 模板（replace.py）、参考图张数与角度、segment_max 调小

**Step 3:** Commit `docs(avatar-replace): API契约核对+冒烟清单`

---

## 风险与后置项

| 风险 | 处理 |
|------|------|
| Seedance 人物替换效果不达标 | P1 最大不确定性；用户冒烟后判断，不行早止损 |
| 方舟 API 契约与本计划假设不符 | Task 11 核对，volc.py 是唯一改动点 |
| VLM 年龄误判 | 人工确认步兜底（P1 CLI --spans，P2 UI 可视化确认） |
| 替换段与原段画质/色彩微差 | P1 接受；P2 若明显再加统一滤镜 |
| P2 Web 壳 / P3 形象库 / P4 部署 | 见设计文档，P1 验收通过后另出计划 |
