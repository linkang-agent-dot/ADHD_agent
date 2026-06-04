---
name: mail-reissue-kb-path
description: 补发邮件固定产出路径 + 两件套格式（邮件导入多语言 / 补偿导入GBK），按项目分目录
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1d044da6-af2c-486e-8e48-674da0c4db05
---

补发/补偿邮件统一产出与模板路径，**按项目分目录**（用户 2026-06-01 指定固化）。

## 固定路径
```
C:\ADHD_agent\KB\产出-补发邮件\{项目}\        # 项目=X3 / X2 / P2
  ├─ _模板\邮件导入模板.csv      # 多语言邮件内容模板
  ├─ _模板\补偿导入模板.csv      # 收件人+道具模板
  └─ {YYYY-MM-DD}_{说明}_{玩家/范围}_邮件导入.csv
     {YYYY-MM-DD}_{说明}_{玩家/范围}_补偿导入.csv
```

## 两件套配套使用（iGame 批量发邮件需同时上传）
1. **邮件导入**（邮件文案，**UTF-8 with BOM**）：5 行 × 21 列
   - 列1=行标签，列2-21=20 种语言：`en cn zh fr de ru jp kr sp id th ar ro nl tr po it vi fa pls`
   - 行：`标题` / `内容` / `超链接文本内容` / `超链接地址`（后两行无链接时留空）
   - 含逗号/引号的文案要 CSV 转义（python csv 自动处理；引号→双写）
2. **补偿导入**（收件人+道具，**GBK 编码**）：见 [[x3-igame]]
   - 6 列：`服务器ID,玩家ID,道具信息,礼包信息,虚拟资产信息,自定义`
   - 道具列写 `"[道具ID*数量, ...]"`，道具ID=配置表数字ID（女王恩典卷=1128 / 尼罗邀请函=1132）

## 模板来源
- 邮件导入模板原件：`C:\Users\linkang\Downloads\[模版]导入多语言邮件内容.csv`（UTF-8-sig）
- 补偿导入样例：`C:\Users\linkang\Pictures\X3验收\海妖任务补偿_批量导入.csv`（GBK）

## 关联
- [[x3-igame]] X3 补偿导入 GBK 格式细节
- [[reference_bulk_mail_reissue]] P2/X2 用 assetType JSON（与 X3 不同）
- 补发前核查是否已发，避免重复补偿
