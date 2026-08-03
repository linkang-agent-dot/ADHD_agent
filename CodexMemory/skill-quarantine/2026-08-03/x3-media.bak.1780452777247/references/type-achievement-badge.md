# 成就徽章（achievement_badge）完整流程

## 何时匹配

用户说：成就徽章、成就图标、achievement badge 等。

## 流程

1. **获取内容**：用户提供徽章内容描述或中间内容的例图
2. **生成中央内容**：生成 **1 张中央内容图**（中央图标内容可由 GPT 等生成）
3. **合成最终徽章**：**5 张最终徽章** = 同一张中央内容 + 5 张不同底板（只换底板不换内容）
4. **中央图标金色化（推荐）**：默认「结晶金」——强 CLAHE、明暗映射为**暗金→亮金→高光**（避免褐土色）、再经 HSV 锁金黄相提饱和度；**外圈粗黑描边**；**内部细线**（弱、少，避免整块发褐）。`--gold-strength` 默认 **0.98**（减少原图土色残留），0 为保持原色；`--gold-soft` 为旧版平滑金。
5. **后处理**：产出 **128×128** 像素
6. **保存到下载目录**

## 关键规则

- 中央内容只生成 1 张，5 张最终徽章是合成出来的
- 5 张底板不同，但中央内容相同（经金色化后视觉一致）
- 最终尺寸 128×128

## 底板资源（固定 5 张）

随本 skill 提交（主仓库可 track，勿只放在 submodule 工作区）：

- 清单：`references/achievement_badge_manifest.json`
- PNG：`references/achievement_badge_bases/base_01_hex_sage.png` … `base_05_oct_purple.png`

合成脚本（主仓库随 skill 提交）：`scripts/compose_achievement_badge.py`；子模块工作区副本：`UX/game-video-workflow/compose_achievement_badge.py`（逻辑需与前者同步）。默认读取 `references/achievement_badge_manifest.json`；勿用单张图 + 色相偏移冒充 5 底板。
