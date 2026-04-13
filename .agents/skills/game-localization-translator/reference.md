# 参考文档

## 页签映射规则

根据文本内容类型自动推断目标页签：

| 内容类型 | 页签 | 内容类型 | 页签 |
|----------|------|----------|------|
| 商店/商城 | ITEM | 英雄/角色 | HERO |
| 联盟/公会 | UNION | 邮件 | MAIL |
| 活动 | EVENT | 战斗/竞技 | ARENA |
| 建筑/城建 | BUILDING | 地图/世界 | MAP |
| 任务 | QUEST | 士兵/部队 | SOLDIER |
| 推送 | PUSH | 错误提示 | ERRCODE |
| 引导 | FTE | 提示/Tips | TIP |
| 菜单/设置 | MENU | 社交 | SOCIAL |
| 对话/剧情 | dialogue | 登录/账户 | login |
| 排行榜 | LEADERBOARD | 新闻/公告 | NEWS |
| 研究/科技 | RESEARCH | 资源 | RSS |
| 玩家 | PLAYER | NPC | NPC |
| 小游戏 | minigame | UI通用 | ui |
| 冒险 | adventure | 蓝图 | blueprint |
| BUFF | BUFF | 美术资源 | ART |
| 其他/待分类 | AI翻译页签 | — | — |

## 现有页签列表

```
Operation Mail, AI翻译页签, MENU, ART, ARENA, ASSET, BUFF, BUILDING,
CHINA, ERRCODE, EVENT, HERO, HORDE, FTE, IAP, ITEM, KVK, LEADERBOARD,
MAIL, MAP, METRO, NEWS, NPC, PLAYER, PUSH, QUEST, RESEARCH, RSS,
SATELLITE, SITUATION, SOCIAL, SOLDIER, STORY, TIP, TRIGGER, UNION,
login, blueprint, dialogue, adventure, minigame, ui
```

## 跳过的非数据页签

以下页签不参与 key 扫描和 TM 构建：

```
AI翻译暂存, 回车检查, 本地化使用说明, AI翻译页签, 页签说明, checkncwj
```

## 18 语言列顺序

| 序号 | 代码 | 语言 | 序号 | 代码 | 语言 |
|------|------|------|------|------|------|
| 1 | cn | 简体中文 | 10 | ru | 俄语 |
| 2 | en | 英语 | 11 | tr | 土耳其语 |
| 3 | fr | 法语 | 12 | vi | 越南语 |
| 4 | de | 德语 | 13 | it | 意大利语 |
| 5 | po | 葡萄牙语 | 14 | pl | 波兰语 |
| 6 | zh | 繁体中文 | 15 | ar | 阿拉伯语 |
| 7 | id | 印尼语 | 16 | jp | 日语 |
| 8 | th | 泰语 | 17 | kr | 韩语 |
| 9 | sp | 西班牙语 | 18 | cns | 简体中文(备份=cn) |

## 表格精准搜索

避免 Token 过长，按列搜索：

| 搜索类型 | 列 | Range 格式 |
|----------|-----|-----------|
| 中文文本 | C | `{页签}!C:C` |
| 英文文本 | D | `{页签}!D:D` |
| ID | B | `{页签}!B:B` |
| ID_int | A | `{页签}!A:A` |
| 完整行 | A~T | `{页签}!A{行号}:T{行号}` |

## ID_int 编码规则

| 类型 | 前缀 | 格式 | 示例 |
|------|------|------|------|
| 原有数据 | 1011 | `1011` + 2位页签编码 + 4位行编码 | `1011010001` |
| AI新增 | 2011 | `2011` + 2位页签编码 + 4位行编码 | `2011040001` |

> 暂存区不填 ID_int。提交时由 Apps Script 读取目标页签最后一行 ID_int + 1 自动顺延。

### 页签编码表

| 页签 | 编码 | 页签 | 编码 | 页签 | 编码 |
|------|------|------|------|------|------|
| MENU | 01 | HERO | 02 | ITEM | 03 |
| EVENT | 04 | ARENA | 05 | BUILDING | 06 |
| MAP | 07 | QUEST | 08 | SOLDIER | 09 |
| MAIL | 10 | UNION | 11 | PUSH | 12 |
| ERRCODE | 13 | FTE | 14 | TIP | 15 |
| SOCIAL | 16 | dialogue | 17 | login | 18 |
| LEADERBOARD | 19 | NEWS | 20 | RESEARCH | 21 |
| RSS | 22 | PLAYER | 23 | NPC | 24 |
| minigame | 25 | ui | 26 | adventure | 27 |
| blueprint | 28 | BUFF | 29 | ART | 30 |
| AI翻译页签 | 99 | (新建) | 90+ | — | — |

## 富文本标签

| 语义 | 颜色代码 | 使用场景 |
|------|----------|----------|
| 绿色 | `#3ef742` | 成功/达成/拥有 |
| 红色 | `#CD2F2F` | 不足/限制/错误 |

```html
<color=#3ef742>已达成</color>
<color=#CD2F2F>资源不足</color>
```
