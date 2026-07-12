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
    sent = {}
    def fake_post(url, json=None, headers=None, timeout=None):
        sent.update(json=json)
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
    assert [c["type"] for c in sent["json"]["content"]] == ["text", "video_url", "image_url"]
