import base64
import mimetypes
import time
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
                url = d["content"]["video_url"]
                break
            if d["status"] in ("failed", "cancelled"):
                raise RuntimeError(f"video task {task_id} 失败: {d}")
            time.sleep(self.POLL_INTERVAL)
        out_path.write_bytes(requests.get(url, timeout=300).content)
        return out_path
