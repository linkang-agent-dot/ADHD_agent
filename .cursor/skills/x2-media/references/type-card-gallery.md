# 集卡册卡片（card_gallery）完整流程

## 何时匹配

用户说：集卡册卡片、图鉴卡片、卡牌图鉴、CardGallary、集卡 等。

## 流程

1. **确认信息**：与用户确认主体人物、使用模型（未指定则先询问）
2. **构造 prompt**：使用 `default-styles.md` 中 card_gallery 的 default_prompt 全文 + 用户描述
3. **参数**：params 须带 `"aspect_ratio": "3:4"`（与 640×900 同比例）
4. **构图参考图（必须）**：传入 `scripts/grfal-api/card_gallery_reference/template_640x900.png`（若不存在可运行 `py -3 scripts/grfal-api/card_gallery_reference/gen_template.py` 生成）
5. **面部一致**：若有人物立绘/设定图，务必传入 reference_images 以保证面部一致；无立绘时提醒用户提供
6. **调用 API**：见 `api-calling.md`
7. **下载 + 后处理**：批量处理为 640×900 像素（`image_resize width=640 height=900` 或本地缩放）
8. **清理**：完成后删除当次一次性临时文件

## 关键规则

- **无边框**：产出为无边框的卡片画面
- **多张系列**：人物**动作要有变动**，避免重复姿势（如第1张举手、第2张持书、第3张微笑）
- **人物全身入画**：保留适当边距，避免裁切过猛
- **风格参考**：项目内 `client/Assets/x2/Res/UI/TextureNew/MiniGame/pic` 目录的 CardGallary_*.png — 环境光、叙事姿势、多样场景，避免过度粒子/光斑
- **保存位置**：默认下载目录
