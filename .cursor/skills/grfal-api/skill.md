---
name: grfal-api
description: |
  GRFal AI media tools via direct HTTP API (no MCP needed).
  Generates images, videos, 3D models and processes media (upscale, remove background, extend, resize, etc.)
  by calling GRFal service directly.
  Use when: (1) generating images (AI art, game assets, illustrations),
  (2) generating videos (text-to-video, image-to-video),
  (3) processing images (upscale, remove background, extend, resize, lighting removal),
  (4) processing videos (upscale, lipsync, reframe, speed change, remove background),
  (5) 3D model generation, virtual try-on, LoRA training,
  (6) creative workflows (character design, PPT generation),
  (7) describing images/videos, PDF processing, screenshot localization.
  Triggers: "generate image", "generate video", "create image", "make video",
  "upscale", "remove background", "3D model", "virtual try-on", "lora",
  "grfal", "AI art", "video editing", "image processing",
  "画图", "画一个", "帮我画", "做图", "P图", "修图", "AI画画", "生成图片",
  "图片生成", "视频生成", "做视频", "抠图", "超分", "换背景", "扩图", "放大图片",
  "去背景", "图生视频", "文生图", "文生视频"
---

# GRFal API - Direct HTTP Tool Calling

Call 39 GRFal AI tools via HTTP POST without MCP protocol.

## Quick Start

```bash
python "<skill_path>/scripts/call_grfal.py" --tool generate_image --params "{\"prompt\": \"a futuristic cityscape\", \"model\": \"gemini\", \"num_images\": 1}"
```

`<skill_path>` refers to the directory containing this SKILL.md file. Always use the absolute path.

## Configuration

By default, API calls go directly to `https://grfal.tap4fun.com` (the fixed domain). This means:
- IP changes only need DNS updates, no skill changes needed
- Server returns domain URLs directly, no rewriting needed

**Note**: This skill requires access to the company intranet.

Overrides:
- `--url`: Force a specific API endpoint
- `--public-url`: Override URL prefix for result rewriting
- `--insecure`: Skip SSL certificate verification (for testing)
- `GRFAL_API_URL` env var: Override API endpoint

**Retry**: Transient network errors are automatically retried up to 2 times with 2s delay.

## Core Workflow

### 1. Call a tool

```bash
python call_grfal.py --tool <tool_name> --params "<json_params>"
```

### 2. Read results

```json
{"success": true, "result": ["https://...url1.png"], "backend": "fal"}
{"success": false, "error": "descriptive error message"}
```

Result URLs are directly downloadable.

### 3. Handle file inputs

| Method | Usage | When |
|--------|-------|------|
| **URL (recommended)** | `--params "{\"image_paths\": [\"https://...\"]}"` | File already has a public URL |
| **Local file** | `--file image_paths=C:\path\image.png` | Local file, auto-converts to base64 |
| **Base64 inline** | `--params "{\"image_paths\": [\"data:image/png;base64,...\"]}"` | Already have base64 |

Multiple files with same key: `--file image_paths=file1.png --file image_paths=file2.png`

### 4. Timeout & Async Mode

| Scope | Default | Mode |
|-------|---------|------|
| Image tools | 300s (5 min) | Synchronous |
| Video/3D/training tools | 1800s (30 min) | **Async polling** |

**Async polling mode** (automatic for video/3D/training):
- Task is submitted, returns immediately with task_id
- Polls server every 15s for status
- More reliable for long-running tasks (no connection timeout)
- Use `--sync` to force synchronous mode if needed

**Background task mode** (automatic for very long tasks):

These tools **automatically** use background mode (return task_id, no waiting):
- Video: `generate_video`, `video_avatar`, `video_lipsync`, `video_portrait`, `video_upscale`, `video_modify`
- Training: `train_model`
- Other: `screenshot_localization`, `pdf_enhancement`

```bash
# Automatic background mode
python call_grfal.py --tool video_avatar --params "..."
# → {"task_id": "video_avatar_xxx", "note": "using background mode automatically"}

# Check status later
python call_grfal.py --check-task video_avatar_xxx
# → {"status": "running"} OR {"success": true, "result": "..."}

# Force polling mode (override background)
python call_grfal.py --tool video_avatar --sync --params "..."
```

**Agent workflow for background tasks:**
1. Call tool → get task_id immediately
2. **IMPORTANT: Save the task_id** — you'll need it to check status later
3. Tell user: "Task submitted (task_id: xxx), I'll check back in a few minutes"
4. Set a reminder/cron job to check status in 2-5 minutes
5. Use `--check-task <task_id>` to poll until completed
6. If still running, set another check; if done, deliver result to user

### 5. List tools

```bash
python call_grfal.py --list-tools
```

## Tool Selection Guide

Choose the right tool by task. For **detailed parameters**, read [references/tool_catalog.md](references/tool_catalog.md).

| Task | Tool | Key Params |
|------|------|------------|
| Text/image → image | `generate_image` | prompt, model, reference_images |
| LoRA preset image | `lora_generation` | prompt, preset, model |
| Style transfer | `kontext_lora` | image_paths, preset |
| Image upscale | `upscale_image` | image_paths, model, scale |
| Remove background | `remove_background` | image_paths |
| Replace background | `replace_background` | image_paths, background_prompt |
| Extend canvas | `image_extend` | image_paths, prompt, aspect_ratio |
| Resize image | `image_resize` | image_paths, width, height |
| Text/image → video | `generate_video` | prompt, model, reference_images, duration |
| Video upscale | `video_upscale` | video_path |
| Video style change | `video_modify` | video_path, prompt |
| Add audio to video | `video_to_audio` | video_path, prompt |
| Lip sync | `video_lipsync` | video_path, audio_path, sync_mode (latentsync=高质量/lipsync=快速) |
| Character animation | `video_portrait` | image_path, video_path, portrait_mode (视频替换角色/视频动作驱动图片) |
| Audio-driven avatar | `video_avatar` | image_path, audio_path |
| Change aspect ratio | `video_reframe` | video_path, target_ratio |
| Text/image → 3D | `generate_3d` | prompt or image_paths, model |
| Describe media | `describe_media` | media_path, prompt |
| Virtual try-on | `virtual_tryon` | model_image, garment_image |
| Creative pipeline | `creative_workflow` | user_input, tool_id |

Additional tools: `image_remove_lighting`, `image_group_photo`, `image_camera_angle`, `image_keyframe`, `image_layered`, `image_split`, `video_remove_background`, `video_speed`, `export_sbs_video`, `synthesize_card`, `correct_yellow_tint`, `vector_generation`, `screenshot_localization`, `pdf_enhancement`, `pdf_compression`, `reduce_face`, `train_model`.

## Common Examples

```bash
# Generate image
python call_grfal.py --tool generate_image --params "{\"prompt\": \"a cute cat in space\", \"model\": \"gemini\", \"num_images\": 2}"

# Remove background (local file)
python call_grfal.py --tool remove_background --file image_paths=C:\Users\photo.png

# Generate video from image
python call_grfal.py --tool generate_video --params "{\"prompt\": \"camera slowly zooms in\"}" --file reference_images=keyframe.png

# Upscale image
python call_grfal.py --tool upscale_image --file image_paths=low_res.png --params "{\"model\": \"SeedVR\"}"

# Describe an image
python call_grfal.py --tool describe_media --file media_path=screenshot.png --params "{\"prompt\": \"describe this image in detail\"}"
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Connection failed | Server not running / not on intranet | Start GRFal or connect to company network |
| SSL certificate error | Self-signed cert | Use `--insecure` or install CA cert |
| Timeout | Long-running task | Increase `--timeout` |
| Tool not found | Invalid tool name | Run `--list-tools` to check |
| File not found | Wrong local path | Verify file path exists |

## Troubleshooting with Server Logs

**IMPORTANT**: When encountering unexplained errors (task disappears, unexpected failures, backend issues), **always check server logs first**:

```bash
# View systemd journal (real-time server output)
python call_grfal.py --view-logs

# View more lines
python call_grfal.py --view-logs --log-lines 500

# View specific date's runtime log
python call_grfal.py --view-logs grfal_20260204.log
```

**When to check logs:**
- Task submitted but result never arrives
- Unexpected "task not found" errors
- Backend failover issues
- Any error message that doesn't make sense

**Log types:**
- `systemd-journal` (default): Real-time stdout/stderr from systemd service
- `grfal_YYYYMMDD.log`: Daily runtime logs with detailed processing info

**Web UI**: https://grfal.tap4fun.com/api/logs/viewer

## grfal-api vs grfal-mcp

- **grfal-api** (this skill): Direct HTTP calls. Works immediately, no restart needed.
- **grfal-mcp**: MCP SSE connection. Requires Claude Code restart, depends on MCP client support.

Prefer `grfal-api` when MCP is unavailable or unreliable.
