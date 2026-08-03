# API 调用规范（GRFal 主后端 + art-skills Fallback）

本文件规定所有媒体生成/处理的 API 调用方式。所有类型（生图、生视频、修图等）统一使用本文件的规范。

---

## 后端能力映射

| 能力 | GRFal（主） | art-skills（Fallback） |
|------|------------|----------------------|
| 文生图 | ✅ generate_image | ✅ generate_2d.py (NanoBanana/Seedream/GPT) |
| 图生图 | ✅ generate_image + reference_images | ✅ generate_2d.py (Kontext/Qwen/DreamOmni) |
| 生视频 | ✅ generate_video (vidu/seadance/hailuo/veo3/sora/kling/wan/runway) | ✅ generate_video.py (SeedDance/Kling) |
| 抠图 | ✅ remove_background | ✅ generate_2d.py RemoveBg |
| 超分 | ✅ upscale_image | ✅ generate_2d.py Upscale / generate_video.py VideoUpscale |
| 扩图 | ✅ image_extend | ✅ generate_2d.py Outpaint |
| 视频抠背景 | ✅ video_remove_background | ❌ |
| 视频SBS导出 | ✅ export_sbs_video | ❌ |
| 视频变速 | ✅ video_speed | ❌ |
| 口型同步 | ✅ video_lipsync | ❌ |
| 3D 模型 | ✅ generate_3d | ✅ generate_3d.py (混元3D/Seed3D/Hitem3D) |
| 虚拟试穿 | ✅ virtual_tryon | ❌ |
| LoRA | ✅ lora_generation | ❌ |
| 三视图 | ❌ | ✅ generate_2d.py ThreeView |
| Midjourney | ❌ | ✅ generate_2d.py Midjourney |
| 图片融合 | ❌ | ✅ generate_2d.py ImageCombine |
| 图片分层 | ❌ | ✅ generate_2d.py QwenLayered |

---

## 1. GRFal（主后端）

### 脚本路径

**统一使用项目 vendored 副本**（协议与服务端始终同步，Cookie 认证可用）：

```
<project skill 根>/vendor/grfal-api/scripts/call_grfal.py
```

Agent 按以下优先级定位「项目 skill 根」（找到即用）：

1. **相对当前工作区向上查找**：从 cwd 向上逐级检查 `<project>/vendor/grfal-api/scripts/call_grfal.py`（例如在 `<project>/UX/L1_xxx/` 下工作时，向上两级到 `<project>/`）
2. **Cursor skills 约定位置**：`<USERPROFILE>/.cursor/skills/<project>/vendor/grfal-api/scripts/call_grfal.py`
3. 回退：使用 `Glob` 搜 `**/<project>/vendor/grfal-api/scripts/call_grfal.py`

找不到时提示用户：「未找到 vendored call_grfal.py，请确认项目 skill 下有 `vendor/grfal-api/` 子目录」。

> ⚠️ **不要使用** grfal-api 全局副本（如 `~/.cursor/skills/grfal-api/`）——该副本协议可能超前升级（Bearer Token 等），与项目 Cookie 认证不兼容，会返回 `Not Found`。**始终优先项目 vendor。**

### 鉴权（Cookie）

只要需要把结果下载到本机，就需要 GRFal Cookie。

**GRFal 地址**：从 `config.json` 的 `grfal_url` 字段读取，默认 `http://172.20.90.45:6018`。

**首次使用引导**：
1. 检查 `config.json` 中 `grfal_cookie` 是否非空
2. 非空 → 设置 `$env:GRFAL_COOKIE = "<cookie值>"`
3. 为空 → **自动获取**：运行本 skill 的 `scripts/get_grfal_cookie.py`

```powershell
python "<x3-media skill 路径>/scripts/get_grfal_cookie.py" --config "<x3-media skill 路径>/config.json"
```

脚本会自动打开浏览器到 GRFal 登录页，用户在浏览器中完成登录后，脚本自动提取 Cookie 并写入 `config.json`。

**如果自动获取失败**（如 playwright 未安装），手动获取：
1. 浏览器访问 GRFal（地址见 `config.json` 的 `grfal_url`）并登录
2. F12 → Network → 点击任意请求 → Headers → 复制 Cookie 整串
3. 粘贴给 Agent，Agent 会写入 `config.json`

### 调用方式

```powershell
# 单张生图（GRFAL_URL 从 config.json 的 grfal_url 字段读取，默认 http://172.20.90.45:6018）
py "<脚本路径>/call_grfal.py" --tool generate_image --params-file _params.json --file reference_images=<图片路径> --url $GRFAL_URL --public-url none --timeout 180

# 生视频
py "<脚本路径>/call_grfal.py" --tool generate_video --params-file _params.json --url $GRFAL_URL --public-url none --timeout 600
```

**关键规则**：
- 长 JSON 用 `--params-file` 传入，避免 shell 转义
- 内网且需下载时：`--url <config.json 中的 grfal_url> --public-url none`
- **视频用 URL 传参**，不用 `--file`（视频太大会失败）
- **多张图并行**：Start-Job 启动 N 个进程，**禁止** for 循环串行
- **禁止新建封装脚本**：不得新建「批量生图」「循环生图」脚本

### 下载到本地

call_grfal.py 只返回 URL，需手动下载：

```powershell
$headers = @{ Cookie = $env:GRFAL_COOKIE }
Invoke-WebRequest -Uri "<结果URL>" -OutFile "<保存路径>" -Headers $headers -UseBasicParsing
```

默认保存到 `$env:USERPROFILE\Downloads`。

### 返回格式

```json
{
  "success": true,
  "result": ["https://<grfal_host>/.../output.png"],
  "backend": "fal"
}
```

失败时 `success: false`，`error` 字段含错误描述。

---

## 2. art-skills（Fallback 后端）

### 何时触发 Fallback

1. GRFal 返回 `success: false`
2. GRFal 请求超时（超过工具建议超时 × 1.5）
3. GRFal 返回结果 URL 无法访问
4. 用户明确要求使用 art-skills
5. 该能力仅 art-skills 支持（见上方映射表标记 ❌ 的项）

### 脚本路径

art-skills 脚本位于 art-skills skill 目录下：

- `<art-skills>/scripts/generate_2d.py` — 2D 图片
- `<art-skills>/scripts/generate_video.py` — 视频
- `<art-skills>/scripts/generate_3d.py` — 3D 模型
- `<art-skills>/scripts/upload_image.py` — 图片上传获取 fileKey

### 鉴权（Token）

- 环境变量 `ART_TOKEN`
- 从 `config.json` 的 `art_token` 字段读取
- 过期时提示用户：「AI 美术系统 Token 已过期，请前往系统右上角头像 → 生成令牌，将新 Token 提供给我」

### 返回格式

```json
{
  "success": true,
  "result": {
    "data": {
      "out_url": "https://cdn.example.com/output",
      "images": ["path/to/image1.png"]
    }
  }
}
```

完整 URL = `out_url + "/" + 相对路径`。

### Fallback 执行流程

```
GRFal 调用
  ├─ 成功 → 继续正常流程
  └─ 失败 →
      1. 记录失败原因到 state/history.jsonl
      2. 检查能力映射表，确认 art-skills 支持该能力
      3. 支持 → 切换到 art-skills 执行，告知用户「GRFal 不可用，已切换到 AI 美术系统」
      4. 不支持 → 告知用户「该功能暂时不可用，GRFal 返回错误：{error}」
```

---

## 3. 通用规则

1. **不得新建脚本**：只使用 `call_grfal.py` 和 art-skills 的 `generate_*.py`
2. **Cookie/Token 持久化**：首次获取后写入 `config.json` 对应字段
3. **超时设置**：参考 SKILL.md 工具速查表中的建议值
4. **结果展示**：下载完成后告知用户完整保存路径；若仅返回 URL 则以 markdown 链接展示
