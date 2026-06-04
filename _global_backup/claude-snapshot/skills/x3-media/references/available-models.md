# 生图可用模型

生图前需确定使用的模型。**先检测网站可用的生图模型**，再在未指定时询问用户用哪个。

## 检测网站可用模型

1. **优先从 GRFal 站点获取**（若站点提供）：
   - 调用 GRFal 接口获取生图模型列表，例如：
     - `GET https://grfal.tap4fun.com/api/models`（若存在）
     - 或请求 MCP/工具 schema（如 `/api/mcp/tools`），从 `generate_image` 的 `model` 参数枚举中解析
   - 将返回的模型列表作为「当前可用生图模型」。
2. **若无法从网站获取**：使用下方「备用模型列表」，并告知用户「以下为文档中维护的常见模型，实际以站点为准」。

## 备用模型列表（当前站点支持）

以下为当前 GRFal 支持的生图模型，询问用户时按此列表展示；传参 `model` 时使用「模型 key」。

| 显示名       | 模型 key（供 API 传参） |
|-------------|--------------------------|
| 谷歌 Google | gemini                   |
| GPT         | gpt                      |
| 即梦豆包     | doubao 或 jimen_doubao   |
| Flux Max    | flux_max                 |
| Vidu        | vidu                     |
| 阿里万象     | wanxiang                 |
| Runway      | runway                   |
| 阿里千问     | qwen                     |
| Ideogram    | ideogram                 |
| 混元        | hunyuan                  |

询问用户时可说：「当前可用生图模型有：谷歌、GPT、即梦豆包、Flux Max、Vidu、阿里万象、Runway、阿里千问、Ideogram、混元，你想用哪个？」

## 视频模型列表

| 显示名 | 模型 key |
|--------|---------|
| Vidu | vidu（默认） |
| 即梦 | seadance |
| 海螺 | hailuo |
| VEO3 | veo3 |
| Sora | sora |
| 可灵 | kling |
| 万相 | wan |
| Runway | runway |

## 与流程的配合

- **用户已指定模型**（如「用 gemini 画」「用 flux 生成」）→ **不再询问**，直接使用该模型填入 `--params` 的 `model`。
- **config.json 中有偏好模型** → 使用偏好模型，不再询问。
- **用户未指定 + 无偏好** → 先按上文「检测网站可用模型」得到列表 → 询问用户选择 → 根据选择填入 `model`。
