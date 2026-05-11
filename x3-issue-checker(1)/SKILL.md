---
name: x3-issue-checker
description: |
  X3 (Tavern Legend) 线上问题自动排查工具。收到社区反馈或线上问题后，自动分析问题类型，
  查询本地配置表（160个xlsx/407个子表）验证数据，输出排查结论。
  适用场景：(1) 钉钉群收到玩家反馈/QA问题，需要查配置表验证
  (2) 活动奖励、礼包内容、英雄数值、道具配置等数据类问题排查
  (3) 判断问题是配置错误还是代码bug，决定转策划还是转研发
  触发词：问题排查、查配置、线上问题、玩家反馈、配置检查、X3问题、
  活动奖励不对、礼包内容错误、数值异常、issue check
---

# X3 Issue Checker

收到线上问题反馈后，自动排查是否为配置问题。

## 流程

```
收到问题反馈
    ↓
Step 1: 解析问题 → 提取关键信息（系统、ID、数值）
    ↓
Step 2: 分类判断
  - 数据/配置类 → Step 3
  - 明显 bug/崩溃/卡顿 → 直接标记"转研发"，输出结论
  - 不确定 → 先查一轮配置表
    ↓
Step 3: 查配置表 → 用 config_lookup.py 检索验证
    ↓
Step 4: 输出结论（发到群里 @策划审核）
```

## Step 1: 解析问题

从反馈文本中提取：
- 涉及系统：活动/礼包/英雄/船只/装备/建筑/KVK/...
- 具体标识：活动ID、礼包ID、英雄名、道具名、数值
- 问题描述：什么不对（数量错、缺失、不一致）

## Step 2: 分类判断

能查配置表的典型问题：
- 活动奖励数量/内容不对
- 礼包价格/内容/折扣异常
- 英雄属性/技能数值不对
- 道具描述/效果不匹配
- 活动时间/条件配置错误
- 多语言文本错误

不能查配置表的（转研发）：
- 闪退/崩溃/卡死
- UI 显示异常（布局错乱、图片缺失）
- 网络/登录/支付问题
- 战斗逻辑 bug（配置正确但表现不对）
- 性能问题

## Step 3: 查配置表

### 工具

```bash
# 查看所有配置文件
python3 scripts/config_lookup.py files

# 查看文件的 sheet 列表
python3 scripts/config_lookup.py sheets Pack.xlsx

# 读取 sheet 数据（可搜索、可指定列）
python3 scripts/config_lookup.py read Pack.xlsx -s Pack -q "关键词" -n 20

# 全局搜索（跨所有文件）
python3 scripts/config_lookup.py search "关键词" -f "文件名过滤" -n 5
```

脚本路径：`~/.clawdbot/workspace/skills/x3-issue-checker/scripts/config_lookup.py`
配置表路径：`/Users/zouhanling/Desktop/X3/design/data_master/`（⚠️ 线上问题必须查 master 环境）

### 其他人使用须知
- `config_lookup.py` 第 14 行：改成自己本地 SVN 的 X3 `data_master` 路径
- `send_to_qa.py` 的 webhook 地址：当前指向 X3-客服问题反馈专用群，共用不需要改

### 定位配置文件

根据问题涉及的系统，查阅 `references/config-index.md` 定位对应的 xlsx 文件和 sheet。

关键映射速查：
- 活动总表 → ActvOnline.xlsx（ActvOnline / ActvGroup / ActvGroupSchedule）
- 活动类型 1~59 → 各 Actv*.xlsx（详见 config-index.md 活动编号索引）
- 礼包 → Pack.xlsx（15个子表）/ PackAllowance / PackHeroPromotion / PackRecommend
- 英雄 → Hero.xlsx（Hero / HeroSkill / HeroSkin 等 15 个子表）
- 道具 → Item.xlsx
- 船只装备 → ShipEquip.xlsx（11个子表）
- 建筑 → Building.xlsx
- VIP → VIP.xlsx
- 大KVK → ActvKvk*.xlsx 系列
- 奖励 → Reward.xlsx（被大量其他表引用）

### 查询策略

1. 先用 `search` 全局搜索关键词，快速定位在哪个文件
2. 用 `sheets` 确认目标 sheet
3. 用 `read -q` 精确查询，提取相关行
4. 如果涉及关联表（如活动引用 Reward ID），跨表追查

## Step 4: 输出结论

格式：

```
🔍 X3 问题排查报告

📋 问题：[原始反馈内容摘要]
🏷️ 分类：配置问题 / 代码问题 / 待确认
📊 涉及系统：[活动/礼包/英雄/...]

🔎 排查过程：
- 查询了 [文件名] / [sheet名]
- 找到 [具体配置数据]
- [对比分析]

✅ 结论：[配置确实有误 / 配置正确可能是代码问题 / 需要更多信息]
💡 建议：[修改配置 / 转研发排查 / 需要补充信息]

⏳ 等待策划确认
```

## 注意事项

- 配置表是 SVN 本地副本，可能不是最新版。如果结论存疑，提醒策划确认 SVN 版本
- xlsx 中 `cs` 行（通常 row 2-4）是注释/说明行，实际数据从之后开始
- `IsOn` 字段：0 或空 = 未启用，1 = 启用
- 活动 ID 关联关系：ActvOnline.ContentId → 各活动类型表的 ID
- Reward ID 是跨表引用的核心字段，很多表的奖励都指向 Reward.xlsx
