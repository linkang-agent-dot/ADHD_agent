---
name: reference-html-deployer-gotchas
description: html-deployer(demo.tap4fun.com) 部署实操坑——Git Bash 下 curl 传文件必须用 Windows 风格路径；历史文件 ~/.demo-tap4fun-history.json 是 GBK 编码；中文文件名先改 ASCII 再传
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4b545fd8-12f2-448a-874e-0a08c503490b
---

# html-deployer 部署实操坑（2026-07-08 实测）

1. **Git Bash 里 curl 是 Windows curl.exe，`-F "file=@..."` 读不了 POSIX 路径**（`/tmp/...`、`/c/...` → `curl: (26) Failed to open/read local data`）。传参用 Windows 风格 `C:/Users/...`（正斜杠即可）。
2. **`~/.demo-tap4fun-history.json` 是 GBK 编码**（本机中文 Windows locale 写入的）。用 `encoding='utf-8'` 读会 UnicodeDecodeError；读用 gbk/utf-8 双 fallback，**写回也保持 GBK**（skill 模板裸 `open()` 走 locale 默认，改成 utf-8 会害后续读）。
3. **中文文件名别直接传**：目录段会变成中文 URL（curl 不自动 percent-encode，易断）。做法=拷一份 ASCII 名（如 `x3_cosmetics_art_demo.html`）上传，history 的 `source` 记真源 KB 路径（保重复部署去重）。
4. **登录闸门 + KB 本地双击共存**：注入闸门时加 `if (location.protocol === "file:") return;` 豁免——demo 域名正常鉴权，KB 归档文件本地打开不弹登录（VERIFY/LOGIN 端点原样不动）。实例见 `KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌\_add_workflow_tabs.py`。
