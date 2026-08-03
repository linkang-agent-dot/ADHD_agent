---
name: reference-html-deployer-gotchas
description: html-deployer(demo.tap4fun.com) 部署实操坑——Git Bash 下 curl 传文件必须用 Windows 风格路径；历史文件 ~/.demo-tap4fun-history.json 是 GBK 编码；中文文件名先改 ASCII 再传
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4b545fd8-12f2-448a-874e-0a08c503490b
  modified: 2026-07-29T08:30:58.288Z
---

# html-deployer 部署实操坑（2026-07-08 实测）

1. **Git Bash 里 curl 是 Windows curl.exe，`-F "file=@..."` 读不了 POSIX 路径**（`/tmp/...`、`/c/...` → `curl: (26) Failed to open/read local data`）。传参用 Windows 风格 `C:/Users/...`（正斜杠即可）。
2. **`~/.demo-tap4fun-history.json` 是 GBK 编码**（本机中文 Windows locale 写入的）。用 `encoding='utf-8'` 读会 UnicodeDecodeError；读用 gbk/utf-8 双 fallback，**写回也保持 GBK**（skill 模板裸 `open()` 走 locale 默认，改成 utf-8 会害后续读）。
3. **中文文件名别直接传**：目录段会变成中文 URL（curl 不自动 percent-encode，易断）。做法=拷一份 ASCII 名（如 `x3_cosmetics_art_demo.html`）上传，history 的 `source` 记真源 KB 路径（保重复部署去重）。
4. **登录闸门 + KB 本地双击共存**：注入闸门时加 `if (location.protocol === "file:") return;` 豁免——demo 域名正常鉴权，KB 归档文件本地打开不弹登录（VERIFY/LOGIN 端点原样不动）。实例见 `KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌\_add_workflow_tabs.py`。
5. 🔴**存量分享包里的闸门没有 file: 豁免——离线分发前必须剥掉**（2026-07-29 实测）：`X3_下期节日优化清单\_分享包\` 的 **10 个 html 每个都被注入了一段**无豁免版闸门（fetch `demo-auth/verify`，`.catch` 里直接 `location.href = LOGIN`）。离线/本地/iframe 里 fetch 必失败 → 整页被顶去登录页，**表现为永远卡在 Loading**，很容易误判成"我的打包脚本坏了"。
   - 判据＝打不开时先 grep 源文件有没有 `demo-auth`，别先怀疑自己的代码。
   - 打包工具 `KB\方法论\tools\html_bundle_site.py` **默认剥离**（`--keep-auth` 可保留），会打印剥了几段。
   - 第 4 条的豁免只对**之后新部署**的有效，**不会回溯修好已部署/已归档的老文件**。
