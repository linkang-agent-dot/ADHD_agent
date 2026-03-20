# 节日卡册道具配置 Skill

## 触发条件
当用户提到"卡册配置"、"卡包道具"、"item_card_asset"、"节日卡包"、"保底卡包"、"主题卡包"时使用。

## 使用方法

1. 读取 6001/6002/6003 表（用 gws CLI）
2. 找到目标节日的 book_id（6001）和 group_id 列表（6002）
3. 参照 references/cases/ 里最近的节日案例生成配置

## 参考案例
- `references/cases/easter_fest_card_pack.md` — 复活节卡册道具配置（2026），含完整 ID 映射、drop 模板、坑点
- `references/cases/easter_fest_localization.md` — 复活节卡册本地化配置（2026），含 Google Sheet 结构、Key 命名规则、整理版格式
- `references/gotchas.md` — 通用坑点汇总，持续追加
