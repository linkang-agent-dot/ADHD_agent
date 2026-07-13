from abc import ABC, abstractmethod
from pathlib import Path


class Provider(ABC):
    @abstractmethod
    def chat_vision(self, prompt: str, image_paths: list[Path]) -> str: ...

    @abstractmethod
    def video_edit(self, prompt: str, video_path: Path,
                   ref_images: list[Path], out_path: Path) -> Path:
        """参考视频+元素参考 → 生成替换后视频，下载到 out_path。

        ⚠️ 对本业务是死路：Seedance 公开 API 禁真人视频输入
        （InputVideoSensitiveContentDetected），仅保留作 API 能力封装，
        管线一律走 generate_clip（i2v）。"""

    @abstractmethod
    def generate_clip(self, prompt: str, first_frame: Path | None,
                      out_path: Path, last_frame: Path | None = None) -> Path:
        """i2v：场景关键帧作首帧（可选尾帧双锚点）+ 分镜文本 → 生成视频段。

        输入只有 CG 图与文本，天然过真人风控；产出段由 replace 裁齐时长。"""

    @abstractmethod
    def edit_image(self, prompt: str, image_path: Path, out_path: Path) -> Path:
        """图生图（Seedream i2i）：给数字人形象图换装/调体态，输入仅 CG 图。"""


class FakeProvider(Provider):
    """零 API 假实现：chat_vision 按预置脚本回答；video_edit 原样拷贝输入段；
    generate_clip 用 ffmpeg 造一段与源片参数不同的 5s 白场——故意异质，
    顺带覆盖 stitch 归一化路径（mock 盲区教训，见 test_stitch_normalizes_foreign_replace_segment）。"""

    def __init__(self, vision_responses: list[str] | None = None):
        self._responses = list(vision_responses or [])
        self.vision_calls: list[str] = []
        self.edit_calls: list[str] = []
        self.clip_calls: list[str] = []
        self.image_calls: list[str] = []

    def chat_vision(self, prompt, image_paths):
        self.vision_calls.append(prompt)
        return self._responses.pop(0) if self._responses else "[]"

    def video_edit(self, prompt, video_path, ref_images, out_path):
        self.edit_calls.append(prompt)
        import shutil
        shutil.copy(video_path, out_path)
        return out_path

    def generate_clip(self, prompt, first_frame, out_path, last_frame=None):
        self.clip_calls.append(prompt)
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=white:s=320x240:r=24:d=5",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
            check=True, capture_output=True)
        return out_path

    def edit_image(self, prompt, image_path, out_path):
        self.image_calls.append(prompt)
        import shutil
        shutil.copy(image_path, out_path)
        return out_path
