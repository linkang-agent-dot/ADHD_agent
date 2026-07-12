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
        import shutil
        shutil.copy(video_path, out_path)
        return out_path
