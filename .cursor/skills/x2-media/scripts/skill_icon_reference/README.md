# 技能图标生图构图/比例参考图

本文件夹为技能图标生图提供**本地参考图**，因生图接口无法仅靠 prompt 可靠约束输出尺寸与比例，改为通过 **reference_images** 传入本目录下的参考图，让模型参考画幅与圆形构图，减少裁切与比例偏差。

## 文件说明

- **template_256x256_circle.png**：256×256 圆形技能图标**贴边**构图参考图（透明底 + 圆边贴画布边、内容贴满圆），生图时**必须**作为 reference_images **第一张**传入，让模型产出贴边设计；图2 放第二张。
- **skill_icon_style_grid.png**：已有技能图标风格参考图（多角色多技能示例），生图时可选作为 reference_images 第三张传入。主流程见 **x2-skill-icon** SKILL.md。
- 可在此目录增加其他比例或风格的参考图（如 template_1024x1024_circle.png），在 skill 中指定使用。

## 使用方式

调用 generate_image 时：

```bash
# call_grfal 来自 grfal-api skill，贴边模板来自本 skill 的 scripts/
py -3 <grfal-api路径>/scripts/call_grfal.py --tool generate_image --params-file params.json \
  --file reference_images=<x2-media路径>/scripts/skill_icon_reference/template_256x256_circle.png \
  --file reference_images=path/to/hero_image.png
```

**注意**：顺序固定为 1) 贴边构图 2) 英雄形象图（图2）。

## 生成模板图

若 template_256x256_circle.png 缺失，可运行：

```bash
py -3 <x2-media路径>/scripts/skill_icon_reference/gen_template.py
```

会在此目录生成 template_256x256_circle.png（256×256，透明底 + 圆形边界 + 安全区内圆）。
