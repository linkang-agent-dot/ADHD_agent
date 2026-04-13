# 技能图标（skill_icon）完整流程

本文件自包含技能图标生成的全部规则：流程、prompt 构造、参考图、后处理、命名。

---

## 流程（必须按序执行）

1. **索要图2**：向用户索要**英雄形象参考图（图2）**；未提供则提示「请提供英雄形象参考图（人物立绘或全身/半身图）」
2. **确认英雄**：与用户确认**英雄序号或英雄中文名**，在 1964_x2_HeroSkillStatsSheet 中查询；**未找到则提示并终止**
3. **确认英文名**：获取该角色的英文名（仅用于文件命名），**必须使用用户指定的准确拼写**；未提供则提醒
4. **模型**：未指定模型且 config 无偏好 → **必须先询问**
5. **技能描述**：从表中取（见下方「技能描述来源」），**写 prompt 前必须先思考转化**
6. **构造 prompt**：default_prompt 全文 + 转化后的技能描述（英文）
7. **调用 API**：见 `api-calling.md`，reference_images 必须传两张
8. **下载**：保存到下载目录
9. **后处理**：缩放 256×256 + 贴边脚本
10. **产出**：按命名规则保存 + 输出技能命名（中英文） + 删除临时文件

---

## Prompt 通用约束

- **必须只生成单张图标**：`ONE SINGLE circular game skill icon, do NOT generate multiple icons or a grid`
- **透明底板**：`transparent background, no white background, no solid flat background, use gradient or atmospheric depth if any background tone`
- **无边框**：`completely borderless, NO circular outline, NO drawn circle, NO edge line, NO stroke, shape formed naturally by content`
- **无明显描边**：`no obvious outline no stroke around character or objects soft edge no dark contour`
- **元素不超出圆边**：`The entire illustration MUST be strictly contained within a perfect circle with wide transparent padding around it. Nothing should extend beyond the circular edge`
- **边缘锐利**：`sharp crisp edges, no blur, no feathering at boundary, hard edge, clean cut`
- **实心剪影**：若有角色 → `solid dark silhouette completely filled no hollow parts no internal transparency no facial details`
- **单主体**：`single subject only one figure no multiple characters`

## 构图规则

- 人物和特效可在任意位置，不固定左右分布
- **按需出现人物**：根据技能描述判断是否需要人物剪影（纯概念技能如光环、被动属性可完全不画人物）
- 光效、粒子等**必须在圆内截止**
- 各图标必须**差异化**，禁止雷同构图

## 色调统一

同一角色的技能图标需色调统一：
- 已生成过 → 沿用首张的主色
- 首张 → 在 prompt 中确定主色（结合立绘/设定或用户指定）
- 示例：主色绿色 → `green and golden-orange palette, dark green silhouette, electric green and gold-orange accents`

---

## 技能描述来源

**表名**：1964_x2_HeroSkillStatsSheet

**查询方式**：按英雄序号（Comment1）或英雄中文名（Comment2）匹配

**列映射**：

| fwcli_name | fwcli_desc |
|------------|------------|
| Id | Id |
| Comment1 | 序号 |
| Comment2 | 名称 |
| Comment3 | 品质 |
| Comment4 | 种族 |
| Comment5 | 职业 |
| Comment6 | 武器 |
| Comment7 | 定位 |
| Comment8 | 技能倾向 |
| Comment9 | 普通攻击1.5 |
| Comment10 | 必杀技能12-30、4-10 |
| Comment11 | 主动技能5-15、3-5 |
| Comment12 | 被动技能 |
| Comment13 | 兵种 |
| Comment14 | 标签 |
| Comment15 | 主动技能 |
| Comment16 | 被动技能-1 |
| Comment17 | 被动技能-2 |

**技能类型 → 取数列**：

| 技能类型 | 取数列 | 说明 |
|---------|--------|------|
| 必杀 | Comment10 | 必杀技能描述 |
| 主动 | Comment11 | 主动技能描述 |
| 被动 | Comment9 | 被动/普攻描述 |
| SLG 主动 | Comment15 | SLG 主动技能 |
| SLG 被动-1 | Comment16 | 被动技能-1 |
| SLG 被动-2 | Comment17 | 被动技能-2 |

**表路径**：`x2gdconf/fo/json/HeroSkillStatsSheet.json`

**线上表**：[1964_x2_HeroSkillStatsSheet](https://docs.google.com/spreadsheets/d/1_ULazgUpI98yOpausRPuElw0C_6HZgsteQqFuJgHq4o/edit?gid=800383838#gid=800383838)

---

## 技能描述 → Prompt 转化（必须思考，禁止直译）

1. **理解**：结合图2（立绘）、英雄种族/职业/武器/定位，理解技能描述含义
2. **提炼视觉元素**：提取可画面化的元素（光效、护盾、爆炸、治疗光等）和情绪氛围
3. **写成审美化英文**：用简洁、具象的英文词组描述画面，保证美感和构图清晰
4. **拼接**：最终 prompt = default_prompt 全文 + 转化后的描述

示例：表内「展开持续 8 秒力场，友军免疫控制并每秒回血」→ `protective force field aura, healing light for allies, debuff zone for enemies, golden shield glow`

---

## Reference Images（必须传两张）

1. **第一张**：256×256 贴边构图参考图 `scripts/skill_icon_reference/template_256x256_circle.png`
2. **第二张**：图2（用户提供的英雄形象图）

**不向用户索要技能图标参考图**，风格完全由 default_prompt 和本文档限定。

---

## 后处理（必须执行）

1. 将下载的图片缩放到 **256×256**
2. 运行 `scripts/skill_icon_postprocess.py <图片路径>`（或 `--dir <目录>` 批量处理）
   - 脚本用 alpha≥50 检测实心内容边界框
   - 按边界框裁剪后缩放到 256×256，使内容四边贴画布
   - 覆盖原文件，处理后自检四边是否贴边
   - 需 Python + Pillow（`pip install Pillow`）
3. 若白底须去背景为透明

---

## 文件命名

| 技能类型 | 文件名格式 | 示例（英雄名 huygens） |
|---------|-----------|---------------------|
| 主动 | `hero_英雄名_skill.png` | hero_huygens_skill.png |
| 必杀 | `hero_英雄名_active.png` | hero_huygens_active.png |
| 被动 | `hero_英雄名_passive.png` | hero_huygens_passive.png |
| SLG 主动 | `hero_英雄名_slg_active.png` | hero_huygens_slg_active.png |
| SLG 被动-1 | `hero_英雄名_slg_passive1.png` | hero_huygens_slg_passive1.png |
| SLG 被动-2 | `hero_英雄名_slg_passive2.png` | hero_huygens_slg_passive2.png |

晋升/多形态英雄加形态标识：`hero_theresa_nightingale_33_1_skill.png`

---

## 技能命名要求

- 中文 + 英文均需提供
- 贴合技能描述
- **避免撞名**：参考本地化表中已有技能名称
  - 中文：`client/Assets/P2/Config/cn/i18n/cn.tsv`
  - 英文：`client/Assets/P2/Config/Gen/i18n/en.tsv` 或 `client/Assets/P2/Config/fo/i18n/en.tsv`

---

## 临时文件清理

生成完成后删除当次产生的临时文件：
- `_hero*_*.json`（参数文件）
- `out_*.txt`、`err_*.txt`（输出日志）
- 仅保留最终技能图标图片
