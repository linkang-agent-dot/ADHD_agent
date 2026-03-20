# 案例：复活节卡册本地化配置

## 任务类型
任务类 → 集卡册本地化（Google Sheet 多区域编辑 + 格式整理）

## 源文档

| 项目 | 值 |
|------|---|
| Spreadsheet ID | `1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw` |
| 参考页签 | `卡册key（科技节）` (gid=205182742) |
| 目标页签 | `卡册key（复活节）+本地化` (gid=1585814535) |
| 整理版页签 | `复活节-整理版` (sheetId=512019199) |

## 输入 → 输出

**输入**：科技节已有完整本地化页签 + 复活节卡片基础数据（卡片名称、资源 ID、卡包名）

**输出**：复活节完整本地化页签，含 6 个数据区域 + 1 个卡册主题区域

## 原页签数据结构（6 + 1 区域）

### 区域 1：卡片清单 (R2-R82, Col A-G)
- 9 组 × 9 卡 = 81 行
- Col A: 卡组主题描述（仅首卡有值）
- Col B: 卡组主题图（通常为空）
- Col C: 卡片序号 (1-9)
- Col D: 卡片名称
- Col E: AI出图（空列）
- Col F: 资源 ID (1511xxxxx)
- Col G: 卡包名 (复活节卡包-xxx)

### 区域 2：卡包 Key 本地化 (R2-R25, Col J-L) ← **与区域1共享行**
- 12 个卡包 × (name + desc) = 24 行
- Col J: Key (`easter_fest_pack_{theme}_name/desc`)
- Col K: 中文名/描述
- Col L: 英文名/描述

### 区域 3：卡包描述本地化 (R27-R50, Col K-N) ← **与区域1共享行**
- R27 为表头，R28-R49 为 22 行数据
- Col K: 原文（长描述）
- Col L: 修改后中文（短名称）
- Col M: JSON Key (`{"typ":"lc","txt":"LC_EVENT_easter_fest_pack_{theme}_name/desc"}`)
- Col N: 英文翻译

### 区域 4：图片描述本地化 (R57-R63, Col K-M)
- R57 为表头，R58-R63 为 6 行
- Col K: 图片中文原文
- Col L: JSON Key
- Col M: 英文翻译

### 区域 5：卡册主题 (R83-R91, Col E-F) ← **科技节有、复活节需手动补**
- 9 个卡组主题，每个有独立资源 ID
- Col E: 资源 ID (1511xxxxx)
- Col F: 主题名 (`复活节卡册主题-{卡组名}`)

### 区域 6：卡组/卡片本地化详表 (R97-R195, Col F-J)
- R97 为表头，R98-R195 为 98 行
- 每组: 1 卡组名行 + 9 卡片行 + 1 分隔行(---) = 11 行 × 8 组 + 最后1组10行
- Col F: 编号 (`[卡組 1]` / `卡片 1-1`)
- Col G: 简体中文名
- Col H: JSON Key (`{"typ": "lc", "txt": "LC_EVENT_easter_fest_set/card_{group}_{card}"}`)
- Col I: 非 JSON Key (`easter_fest_set/card_{group}_{card}`)
- Col J: 英文翻译

### 区域 7：大富翁图像文字 (R197-R206)
- 左侧 (Col F-J): 大写 Key + LC_EVENT Key
- 右侧 (Col M-P): 序号 + JSON Key + 英文翻译
- 9 行数据（好运降临 ~ 大获全胜）

## Key 命名规则

### 卡包 Key (区域2)
```
easter_fest_pack_{theme}_name
easter_fest_pack_{theme}_desc
```
theme 列表: `core_decipher`, `underground`, `lucky_marble`, `coin_pusher`, `roaming`, `lab_rampage`, `common`, `excellent`, `rare`, `epic`, `legendary`, `selection`

### 卡组 Key (区域6)
```
easter_fest_set_{group}_name
```

### 卡片 Key (区域6)
```
easter_fest_card_{group}_{card_key}
```

### 9 卡组 Key 对照表

| 序号 | 中文卡组名 | group key | 英文名 |
|:---:|-----------|-----------|--------|
| 1 | 欢乐寻蛋 | joyegg | Joyful Egg Hunt |
| 2 | 彩绘时光 | painting | Painting Time |
| 3 | 春日花园 | garden | Spring Garden |
| 4 | 金蛋工坊 | workshop | Golden Egg Workshop |
| 5 | 拳击冒险 | boxing | Boxing Adventure |
| 6 | 极速飞车 | racing | Speed Racing |
| 7 | 矿洞寻宝 | mine | Mine Treasure Hunt |
| 8 | 彩蛋大亨 | tycoon | Easter Tycoon |
| 9 | 异族探秘 | alien | Alien Exploration |

## 资源 ID 分配

| 类型 | ID 范围 | 数量 |
|------|---------|------|
| 81 张卡片 | 151104889 - 151104969 | 81 |
| 9 个卡册主题 | 151105042 - 151105050 | 9 |

注意：卡册主题 ID **不一定**紧跟卡片 ID（科技节是连续的，但复活节有间隔）

## 整理版页签结构

将原始 7 个区域拆分为独立分区，每个分区有：
- 蓝色标题行（加粗 12pt，背景色 RGB 0.85/0.92/1.0）
- 灰色列头行（加粗，背景色 RGB 0.95/0.95/0.95）
- 数据行
- 空白分隔行

| 分区 | 行范围 | 数据行数 |
|------|--------|----------|
| 【卡片清单】 | R1-R92 | 9 主题 + 81 卡片 |
| 【卡包本地化】 | R93+ | 24 行 |
| 【卡包描述（修改版）】 | 接续 | 22 行 |
| 【图片描述本地化】 | 接续 | 6 行 |
| 【卡组/卡片本地化详表】 | 接续 | 98 行 |
| 【大富翁图像文字翻译】 | 末尾 | 9 行 |

## 坑 / 注意事项

### 1. PowerShell JSON 引号问题
Windows PowerShell 无法正确传递 JSON 参数给 `gws` 命令。
**解决**：用 Python 脚本调用 `subprocess.run([gws_cmd, ...])` 传参

### 2. 大批量写入失败
一次性写入 50+ 行含 JSON 的数据可能静默失败（无 stderr 但返回 None）。
**解决**：分批写入，每批 10-20 行，失败时逐行重试

### 3. 卡册主题 ID 不连续
科技节: 卡片 ID 151104404-151104484，主题 ID 紧跟 151104485-151104493
复活节: 卡片 ID 151104889-151104969，但主题 ID 跳到 151105042-151105050
**教训**：不能假设主题 ID = 卡片最大 ID + 1，需从实际数据确认

### 4. 简体 vs 繁体中文
原始 Section 6 的表头写着"中文名稱"（繁体），但实际内容用简体中文。
初次误用 `opencc` 转繁体，后改回简体。
**规则**：除非明确要求繁体，一律用简体中文

### 5. 列偏移量
复活节比科技节多一个"AI出图"空列（Col E），导致后续所有列索引 +1。
分析数据结构时必须确认实际列位置，不能直接套用参考页签的列号。

### 6. 行共享导致区域难以识别
原页签的区域 1/2/3/4 共享同一批行（R1-R82），只用不同列范围区分。
整理时需要将它们拆分成独立区域，每个区域从 A 列开始。
