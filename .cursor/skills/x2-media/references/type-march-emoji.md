# 动态行军表情（march_emoji）完整流程

## 何时匹配

用户说：行军表情、制作行军表情、动态行军表情、做行军表情、行军表情包 等。

## 流程

1. **索要人物参考图**：必须先向用户索要**人物参考图**；未提供则提示「请提供一张人物参考图」
2. **模型**：未指定则先询问
3. **构造 prompt**：使用 `default-styles.md` 中 march_emoji 的 default_prompt 全文 + 用户补充描述（英文）
4. **调用 API**：`generate_image`，reference_images 传入用户提供的人物图
5. **下载 + 后处理**：产出须为 **256×256** 像素（下载后缩放）
6. **保存到下载目录**

## 关键规则

- 默认风格：2D 游戏 UI 图标、矢量插画、扁平色、贴纸质感、半身特写、白底
- reference_images 参数名是 `reference_images`（不是 image_paths）
- 必须用 `--file reference_images=<路径>` 传入
