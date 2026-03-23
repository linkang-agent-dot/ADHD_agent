# Drop 随机掉落配置总结

## 搜索结果

在表格 `2121_p2_activity_special` 中找到了以下 drop 相关配置：

### 1. **lucky_drop** - 幸运掉落配置 ⭐ 推荐复用

**配置 ID**: 21211308  
**注释**: 月度异族-跨服幸运奖  
**类型**: `lucky_drop`

**配置详情**:
- **arg1**: 3
- **表达式 (A_MAP_expr)**: 
  ```json
  {
    "args": [
      {"typ":"lucky_drop","id":0,"val":3000},
      {"typ":"lucky_drop","id":201,"val":2000},
      {"typ":"lucky_drop","id":301,"val":1500},
      {"typ":"lucky_drop","id":401,"val":1000},
      {"typ":"lucky_drop","id":501,"val":700},
      {"typ":"lucky_drop","id":601,"val":500},
      {"typ":"lucky_drop","id":1001,"val":300},
      {"typ":"lucky_drop","id":1501,"val":100}
    ]
  }
  ```
- **数组 (A_ARR_array)**: `[11117107,10000,2000,7000,1,1000,2000]`
- **状态 (A_ARR_status)**: 包含 IAP 权重配置

**特点**: 这是最完整的随机掉落配置，支持多级掉落概率配置，可以复用。

---

### 2. **daily_drop_limit** - 每日掉落上限

**配置 ID**: 21211468  
**注释**: 泳池派对每日抽奖上限  
**类型**: `daily_drop_limit`

**配置详情**:
- **arg1**: 1100 (每日上限次数)

**特点**: 用于限制每日掉落/抽奖次数上限。

---

### 3. **random** - 随机数生成

**配置 ID**: 21211062  
**注释**: 玩家邀请活动-随机数  
**类型**: `random`

**配置详情**:
- **arg1**: 1
- **arg2**: 2

**特点**: 简单的随机数生成配置。

---

### 4. **7days_log_in_random** - 7天登录随机奖励

**配置 ID**: 21211201-21211204  
**注释**: 前7天登录活动_完美/极好/不错/一般  
**类型**: `7days_log_in_random`

**配置详情**:
- 每个配置有不同的 arg1/arg2 参数
- 每个配置有对应的奖励 (A_ARR_reward)

**示例**:
- 21211201 (完美): arg1=2, arg2=4, 奖励 item 11116228 x8
- 21211202 (极好): arg1=3, arg2=3, 奖励 item 11116228 x7
- 21211203 (不错): arg1=1, arg2=2, 奖励 item 11116228 x6
- 21211204 (一般): arg1=1, arg2=1, 奖励 item 11116228 x5

**特点**: 用于登录活动的随机奖励池配置。

---

## 推荐复用配置

### 最推荐: **lucky_drop** (ID: 21211308)

这个配置最完整，包含：
- 多级掉落概率配置（通过 A_MAP_expr 中的 args 数组）
- 掉落物品配置（通过 A_ARR_array）
- 权重配置（通过 A_ARR_status）

**复用方式**:
1. 复制配置 ID 21211308 的整行数据
2. 修改 A_MAP_expr 中的掉落概率和 ID
3. 修改 A_ARR_array 中的掉落物品列表
4. 根据需要调整 A_ARR_status 中的权重配置

---

## 配置字段说明

- **A_STR_type**: 配置类型，决定配置的行为
- **A_MAP_expr**: 表达式配置，用于定义掉落规则和概率
- **A_ARR_reward**: 奖励数组，直接奖励
- **A_ARR_array**: 数组配置，通常用于掉落物品列表
- **A_ARR_status**: 状态数组，用于权重、条件等配置
- **arg1/arg2/arg3**: 通用参数，根据类型不同有不同含义

---

## 表格链接

https://docs.google.com/spreadsheets/d/1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc/edit?gid=485397688#gid=485397688
