---
name: p2-card-album-media
description: |
  P2 项目集卡册专项美术生成流程 — 独立于 x2-media 的入口。
  套内卡 240×320、卡册封面 304×328 透明、GRFal generate_image、
  Bearer 异步 submit、config.json 统一管理参考图路径。
  触发词(中): P2 集卡册、拓荒节集卡册、册1–册8、套内卡、卡册主题图、
  集卡册封面 304、240×320 卡图、批跑卡册、p2_book、p2_cards、P2 卡册美术。
  NOT: X2 集卡、CardGallary 640×900、行军表情 — 用 x2-media。
alwaysApply: false
---

# P2 集卡册媒体生成

## 与 x2-media 的边界

| 项目 | 本 skill（P2 集卡册） | x2-media（X2 工程） |
|------|------------------------|----------------------|
| 套内卡规格 | **240×320** 竖版 | **640×900** 等 |
| 卡册封面 | **304×328** 透明 | X2 图鉴规范 |
| 主入口 | 本 SKILL | x2-media Type Router |

---

## 参考图配置

所有参考图路径统一在 `references/config.json` 管理，**不硬编码在脚本中**。

```
references/
  config.json          ← 参考图路径配置（角色/封面风格/元素）
  img/
    cover_outline_style.png   ← 封面描边风格参考（所有封面通用）
    monopoly_board_ui.png     ← 大富翁棋盘UI（仅大富翁组使用）
    （其他元素参考按需添加）
  pipeline-overview.md
```

**更新参考图**：替换 `img/` 下对应文件，config.json 路径不变。

---

## 完整执行流程

### Step 0 · 前置检查（自动）

读取 `references/config.json`，验证所有路径存在：
- Bearer token
- 角色参考图（Roger / Scott / Penguin）
- 封面描边风格参考
- 各元素参考图
- 输出目录

全部通过后继续，有缺失则提示修复。

---

### Step 1 · 角色分配确认

**自动推荐**，按规则生成分配表，用户确认后继续：

**分配规则：**
- Roger 主导（最熟悉角色），占比约 50%
- Scott 出现在体力/竞技/对弈场景，占比约 20%
- Penguin 出现在轻松/游戏场景，占比约 8%
- 双主角（Roger+Scott / Roger+Penguin）出现在重要/对话场景，占比约 18%
- 整体 72 张同一角色不超过 55%

**输出格式：**
```
| 组         | 角色分配（9张）           | 逻辑        |
| G1 工地日常 | Roger×6, R+S×2, Scott×1 | 体力场景S出场 |
...
汇总: Roger主×39  Scott主×14  Penguin×6  双主角×13
```

确认后进入各组生成。

---

### Step 2 · 套内卡生成（每组流程）

**每组按以下顺序执行：**

#### 2a · 生成前 Checklist（每组）

展示该组9张卡的完整配置，**每张卡两个参考图**：

```
| # | 卡名     | 角色   | 角色参考路径                | 元素参考路径                |
| 01| 修筑铁路 | Roger  | %TEMP%/p2_roger_correct.jpg| 无                         |
| 04| 打开奖赏 | Roger  | %TEMP%/p2_roger_correct.jpg| references/img/monopoly_board_ui.png |
...
⚠️ 确认后先出示例图，回复「确认 GN」
```

**元素参考规则：**
- `无` → 纯场景生成，角色+背景描述足够
- 有路径 → 场景中有特定道具/UI需要风格一致（棋盘、弹珠台等）

#### 2b · 示例图生成（第1张）

生成第1张卡作为示例，展示预览，等待确认：
```
✅ OK → 回复「继续 GN」，生成剩余8张
❌ 有问题 → 说明问题，重新生成示例
```

#### 2c · 剩余8张逐张生成

每张生成完立即展示预览，可随时说「重跑 N」。

#### 2d · 组完成 Review

全组9张完成后展示汇总，确认后进入下一组：
```
回复「GN 完成，继续 G(N+1)」
```

---

### Step 3 · 封面生成（304×328）

套内卡72张全部完成后触发。

#### 3a · 生成前 Checklist（8张封面）

```
| # | 封面名称    | 封面描边参考                              | 元素参考             |
| 01| 工地日常   | references/img/cover_outline_style.png  | 无                   |
| 04| 拓荒大富翁 | references/img/cover_outline_style.png  | references/img/monopoly_board_ui.png |
...
⚠️ 先出 cover_01 示例，确认风格后生成剩余7张
```

#### 3b · 示例封面

生成 cover_01，确认风格（描边/透明/尺寸）后继续。

#### 3c · 剩余7张生成

每张流程：`1:1白底生图 → rembg → 描边 → 落304×328画布 → 预览`

---

### Step 4 · 交配置线

```
输出目录:
  %TEMP%/p2_cards/集卡册资源/  (72张套内卡)
  %TEMP%/p2_cards/covers/      (8张封面)

→ 通知 card-collection-config 开始扫描目录
→ 配置线 阶段一 启动
```

---

## 技术依赖

- GRFal API：`{REPO}/.cursor/skills/grfal-api/scripts/call_grfal.py`
- GRFal 服务：`http://172.20.90.45:6018`
- Bearer token：`%USERPROFILE%/.config/grfal-api/token_store.json`
- 后处理：`rembg`（抠图）、`Pillow`（描边+画布）

## 输出规格

| 类型 | 尺寸 | 底色 | 命名 |
|------|------|------|------|
| 套内卡 | 240×320 | 无（透明或场景背景） | `{序号}_{卡名}.png` |
| 封面 | 304×328 | 透明 | `cover_{N:02d}_final.png` |
