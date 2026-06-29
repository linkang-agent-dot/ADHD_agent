---
name: reference_podcast_download_transcribe
description: 下载小宇宙/任意播客最新一期并转文字的链路与本机环境踩坑（yt-dlp/ffmpeg/whisper）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8e950365-4cff-4431-b096-a378d2dd6b6c
---

# 播客下载 + 转文字链路（本机已验证 2026-06-23）

任务：用 yt-dlp 下小宇宙播客「毕不了业(毕业进化录)」最新一期 + 转文字。

## 找音频直链（小宇宙没开放页面ID时的通法）
小宇宙 web 搜不到 podcast 页 ID。最可靠 = 走 **Apple Podcasts iTunes lookup API** 拿权威 RSS：
1. 搜到 Apple Podcasts 该节目的 id（如 毕不了业=`1744805485`）。
2. `curl -sL "https://itunes.apple.com/lookup?id=<id>"` → JSON 里 `feedUrl`（毕不了业=`https://proxy.wavpub.com/graduation.xml`）。
3. 下 RSS，解析第一个 `<item>` 的 `<enclosure url>` = mp3 直链（最新一期）。**别信 WebFetch 复述的 URL，从本地 XML `ET.parse` 精确取**（已对过字节数一致才算准）。
4. `python -m yt_dlp --ffmpeg-location <ff_bin> -o "名.%(ext)s" "<enclosure_url>"` 下载（wavpub 会 302 跳 media.wavpub.com，yt-dlp 自动跟）。

## 本机环境（坑都踩过）
- **yt-dlp/ffmpeg 默认没装**。yt-dlp=`pip install yt-dlp`（装到 ~/AppData，PATH 没有→用 `python -m yt_dlp`）。
- **ffmpeg：choco 装会失败（exit 1）；用 `winget install Gyan.FFmpeg`** 成功，路径 `C:\Users\linkang\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*-full_build\bin\`（ffmpeg.exe/ffprobe.exe）。
- **Git Bash 的 curl 对部分 https 主机 TLS 握手失败（exit 35 / HTTP 000）**（wavpub、firstory 都中招；itunes 正常）→ 改用 **PowerShell `Invoke-WebRequest`**（.NET TLS 栈）下 RSS。
- **Git Bash 写不进 `/tmp`**（FileNotFoundError）→ 临时文件一律用 scratchpad 绝对路径。

## 转文字（whisper）—— ⚠️Python 3.14 大坑
- 本机 `whisper`/`faster-whisper` 已装，torch=2.11.0+cpu（无 CUDA）。
- **致命坑：faster-whisper 在 Python 3.14 下对整段长音频一次性算 STFT，numpy 申请 >1GB complex128 直接 `_ArrayMemoryError`**。72 分钟音频必崩。
  - 解法 = **先用 ffmpeg 切 10 分钟分段（16k 单声道 wav），逐段 transcribe，按 `offset=段序×600s` 拼时间戳**。每段内存占用小，稳。
- **CPU 跑 medium 太慢**：10 分钟音频要 ~21 分钟（2x realtime），8 段 ~2.8 小时。**改 small 模型**（质量仍可用，快 ~4 倍）。要更快/更准建议直接用云端：飞书妙记 / 通义听悟 / 剪映识别字幕（72min 中文又快又好，比本地 CPU 划算）。
- 中文同音误差正常（如「进化录」转成「净化录」）。

## 复用脚本
切片转写脚本范本：`scratchpad/transcribe2.py`（ffmpeg 切段 + faster-whisper 逐段 + 拼 srt/txt + 时间戳 offset）。下次要本地转长音频直接抄它，改 model/AUDIO 路径即可。
