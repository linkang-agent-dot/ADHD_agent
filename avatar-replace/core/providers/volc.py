import base64
import mimetypes
import time
from pathlib import Path

import requests

from core.config import ArkCfg
from core.providers.base import Provider


class VolcProvider(Provider):
    """火山方舟 v3。契约已核对（2026-07-13，官方 volcengine-python-sdk arkruntime 源码 + Seedance 2.0 文档）：

    - VLM 视觉理解：POST {base}/chat/completions，OpenAI 兼容；
      图片支持 data URL base64（data:image/<fmt>;base64,...，fmt 小写）。
    - 视频生成：POST {base}/contents/generations/tasks；
      content 元素需带 role（参考视频=reference_video / 参考图=reference_image，
      另有 first_frame/last_frame，与参考模式互斥）；
      resolution/ratio/duration/generate_audio/watermark 为 body 顶层字段（非 prompt 内文本命令）；
      GET {base}/contents/generations/tasks/{id} 轮询，
      status ∈ queued/running/succeeded/failed/cancelled/expired，
      成功取 content.video_url（签名直链，约 24h 有效）。
    - 仅 doubao-seedance-2.0 系列支持参考视频输入（1.x 只有文生/图生）。

    ⚠️ 待冒烟验证（docs/SMOKE.md）：官方文档标注参考视频仅支持公网 URL
      （mp4/mov，单段 2-15s，≤50MB，≤3 段），"不支持 base64"；图片 base64 明确支持。
      本地管线无上传基建，视频暂以 data URL 传入作为最合理假设——真实 key 冒烟若报
      InvalidParameter，需改走 TOS/公网 URL（方舟另有 POST /files 素材上传 API 可选）。
      请求体总大小 ≤64MB（segment_max=15s 的 720p 段一般不超）。
    """
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
        # ⚠️ 死路存档：真人视频输入必撞 InputVideoSensitiveContentDetected（2026-07-13 实测），
        # 管线走 generate_clip。prompt 中用"视频1/图片1"按 content 顺序指代素材。
        content = [{"type": "text", "text": prompt},
                   {"type": "video_url", "video_url": {"url": self._data_url(video_path)},
                    "role": "reference_video"}] + [
                   {"type": "image_url", "image_url": {"url": self._data_url(p)},
                    "role": "reference_image"} for p in ref_images]
        body = {"model": self.cfg.video_model, "content": content,
                "resolution": self.cfg.video_resolution,
                "ratio": self.cfg.video_ratio,          # adaptive=跟随输入
                "duration": self.cfg.video_duration,    # -1=模型自适应（4-15s）
                "generate_audio": self.cfg.generate_audio,  # 拼回时原片音轨整条铺回，默认不生成省费
                "watermark": self.cfg.watermark}
        return self._submit_and_poll(body, out_path)

    def generate_clip(self, prompt, first_frame, out_path: Path) -> Path:
        """i2v 主路径（2026-07-13 实测通）：数字人图作首帧 + 文本。

        ⚠️ mini 系列不接受 duration 参数（传了报 InvalidParameter）——不传，
        产出约 5s/24fps，时长裁齐在 replace 层做；ratio=adaptive 跟随首帧画幅。"""
        if first_frame is None:
            raise ValueError("generate_clip 需要首帧参考图（avatars/<名>/front|back）")
        content = [{"type": "text", "text": prompt},
                   {"type": "image_url", "image_url": {"url": self._data_url(first_frame)},
                    "role": "first_frame"}]
        body = {"model": self.cfg.video_model, "content": content,
                "resolution": self.cfg.video_resolution,
                "ratio": self.cfg.video_ratio,
                "generate_audio": self.cfg.generate_audio,
                "watermark": self.cfg.watermark}
        return self._submit_and_poll(body, out_path)

    def edit_image(self, prompt, image_path, out_path: Path) -> Path:
        """Seedream 图生图（2026-07-13 已实测通路径：POST /images/generations + image 字段）。"""
        body = {"model": self.cfg.image_model, "prompt": prompt,
                "image": self._data_url(image_path),
                "response_format": "url", "watermark": False}
        r = requests.post(f"{self.cfg.base_url}/images/generations",
                          headers=self.headers, json=body, timeout=300)
        r.raise_for_status()
        url = r.json()["data"][0]["url"]
        out_path.write_bytes(requests.get(url, timeout=300).content)
        return out_path

    def _submit_and_poll(self, body: dict, out_path: Path) -> Path:
        r = requests.post(f"{self.cfg.base_url}/contents/generations/tasks",
                          headers=self.headers, json=body, timeout=120)
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
                url = d["content"]["video_url"]
                break
            if d["status"] in ("failed", "cancelled", "expired"):
                raise RuntimeError(f"video task {task_id} 失败: {d}")
            time.sleep(self.POLL_INTERVAL)
        out_path.write_bytes(requests.get(url, timeout=300).content)
        return out_path
