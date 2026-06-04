---
name: bulk-mail-reissue
description: 批量补发邮件导入表生成。根据数据源 CSV（含 server_id、user_id、asset_id、amount 等列）生成 iGame 批量发邮件工具所需的导入 CSV（GBK 编码、逗号分隔、JSON 字段 CSV 转义）。触发条件：(1) 提到"补发"、"批量发邮件"、"批量导入邮件"、"回收补发"，(2) 用户提供源数据（玩家/服务器/道具/数量）并要求生成导入文件，(3) 提到"按模版生成附件导入表"。
---

# Bulk Mail Reissue Skill

**Skill 路径**: `~/.claude/skills/bulk-mail-reissue`

## 用途

把运营/数据同学给的"要给哪些玩家补发什么道具多少个"的数据源 CSV，转成 iGame 批量发邮件工具能直接吃的 CSV 导入表。

## 输入 / 输出

- **输入**：任意列名的源 CSV（UTF-8 / UTF-8-BOM / GBK），至少包含：
  - 服务器 ID（常见列名：`server_id`, `sid`, `server`）
  - 玩家 ID（常见列名：`user_id`, `uid`, `player_id`）
  - 道具 ID（常见列名：`asset_id`, `item_id`, `id`）
  - 数量（常见列名：`change_count`, `amount`, `count`, `cnt`, `qty`）

- **输出**：`{源文件名}_import.csv`，6 列 / GBK / 逗号分隔 / JSON 字段带 CSV 引号转义
  ```
  服务器 ID,玩家 ID,玩家信息,标题信息,附件资产信息,自定义
  2037402,34627750,,,,"[{""assetType"":""item"",""id"":11117402,""amount"":29}]"
  ```

## 关键兼容性要求（踩过的坑）

1. **编码必须是 GBK**，不是 UTF-8。iGame 导入工具按 GBK/ANSI 读取。
2. **分隔符是逗号**，不是 Tab。尽管文件叫"TSV"口头说法，实际是 CSV。
3. **JSON 字段必须用 CSV 规则转义** — 外层 `"..."` 包裹，内部 `"` → `""`。直接塞原始 JSON 会被解析器按双引号切列，奖励就跑到错误的列里去了。
4. **不要聚合** — 源数据即使同一玩家多条记录也保持 1:1 行数，每条记录对应一封独立邮件。

## 用法

```bash
python ~/.claude/skills/bulk-mail-reissue/generate.py <源CSV路径> [--output <输出路径>]
```

脚本会：
1. 自动探测源文件编码（utf-8-sig / utf-8 / gbk）
2. 自动识别列名（大小写不敏感，支持常见别名）
3. 若识别失败会打印源表列名并询问映射关系
4. 生成后做一次自检：行数一致、道具总量一致、无 JSON 解析错误

## 行为规范

- 列名识别不出来时**一定要问用户**，不要瞎猜
- 同一玩家 + 同一道具的多条记录保持分行（每条一封邮件）
- `assetType` 默认 `"item"`；若源数据有类型列，沿用源数据的值
- 生成完自动跑校验：行数对齐 + 道具总量对齐 + JSON 解析 0 错误

## 示例场景

**场景 1：矿石药水回收补发**
- 源：`p2_mining_potion_recycle.csv`（列：server_id, user_id, asset_id, change_count, ...）
- 输出：`p2_mining_potion_recycle_import.csv`
- 运行：`python generate.py C:/Users/linkang/Downloads/p2_mining_potion_recycle.csv`

**场景 2：列名非标准**
- 源列名是 `sid, uid, item_id, cnt`
- 脚本会自动映射；映射不出来时脚本会 print 所有列名并退出，由 Claude 询问用户后用 `--map` 参数覆盖
