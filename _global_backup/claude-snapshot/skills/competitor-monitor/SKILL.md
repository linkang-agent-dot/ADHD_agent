---
name: competitor-monitor
description: |
  竞品游戏每日监控与日报生成。自动抓取应用商店、Discord、Reddit、SensorTower、data.ai 等多渠道数据，
  按日报模版生成竞品监控日报并写入 Obsidian。
  Use when: (1) 执行竞品监测/竞品日报任务,
  (2) 抓取特定竞品游戏的最新动态,
  (3) 定时任务触发的每日竞品监控。
  Triggers: "竞品监测", "竞品日报", "竞品监控", "competitor monitor",
  "Last Asylum Plague", "LAP监控", "跑一下竞品", "竞品数据"
---

# 竞品监控 Skill

自动抓取多渠道数据，生成竞品监控日报，写入 Obsidian。

## 配置

游戏配置文件位于 `<SKILL_DIR>/configs/` 目录，每个游戏一个 JSON 文件。
当前已配置：`last-asylum-plague.json`

配置包含脚本执行所需的结构化参数（ID、包名、频道 ID 等）。
人类可读的链接汇总和背景情报在 Obsidian 的「竞品监测链接大全」文档中维护。

## 执行流程

### 前置准备

```python
import json
SKILL_DIR = "C:/Users/linkang/.agents/skills/competitor-monitor"
CONFIG = f"{SKILL_DIR}/configs/last-asylum-plague.json"
with open(CONFIG) as f:
    config = json.load(f)
```

### Step 1: 版本动态 🔄

数据源：App Store Lookup API + SensorTower + Discord #patch-notes

```bash
# App Store 版本 + 评分
python <SKILL_DIR>/scripts/fetch_appstore.py --config <CONFIG> --country us

# Discord patch-notes 频道
python <SKILL_DIR>/scripts/fetch_discord.py --config <CONFIG> --hours 24 --channel patch-notes
```

SensorTower 补充 Android 版本号：
```python
import sys
sys.path.insert(0, "C:/Users/linkang/.agents/skills/sensortower-query/scripts")
from st_api import SensorTowerAPI
api = SensorTowerAPI()
app_info = api.get_app_info(["com.phs.global"])
```

填写：当前版本号、是否有更新、更新内容摘要、版本节奏判断。

### Step 2: 活动运营 🎯

数据源：Discord #event-news + #official-post + #giftcode

```bash
python <SKILL_DIR>/scripts/fetch_discord.py --config <CONFIG> --hours 24
```

重点关注 event-news 和 official-post 中的活动公告。
提取：活动名称、类型、起止时间、核心玩法/规则、付费点设计。
活动类型参考：限时充值/累充/抽卡/排行赛/节日活动/联动/签到/回流/新服活动。

### Step 3: 商业化观察 💰

数据源：Discord 公告 + SensorTower 收入 + 礼包码

```bash
# 礼包码
python <SKILL_DIR>/scripts/fetch_giftcodes.py --config <CONFIG>
```

SensorTower 收入趋势：
```python
from datetime import datetime, timedelta
start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
sales = api.get_sales_estimates(app_ids=["com.phs.global"], start_date=start, granularity="daily")
```

从 Discord 公告中提取礼包/促销信息。
填写：礼包名称、价格、内容、限购、展示位置、是否新增。

### Step 4: 投放素材 📢

数据源：Facebook 公开帖 + Discord 社区动态

```bash
# Facebook（best-effort）
python <SKILL_DIR>/scripts/fetch_facebook.py --config <CONFIG>
```

备选：用 `web_fetch` 抓取 Facebook 页面。
AppGrowing / BigSpy 需手动查看，在日报中标注"需手动补充"。

社媒运营部分从 Discord 各频道活跃度汇总。

### Step 4.5: YouTube 攻略频道 📺

数据源：config 中 `youtube.channels` 配置的攻略频道

**抓取近期视频：**
```bash
# 对每个频道，用 yt-dlp 抓取最近上传的视频列表
python -m yt_dlp --dump-json --playlist-end 3 --flat-playlist "https://www.youtube.com/channel/{channel_id}/videos"
```

如果 `--flat-playlist` 信息不足，改用搜索模式：
```bash
python -m yt_dlp --dump-json "ytsearch3:{channel_name} kingshot" 
```

从返回的 JSON 中提取：title, upload_date, view_count, id（拼接为 `https://youtu.be/{id}`）。
仅保留最近 7 天内上传的视频。

**视频内容概括（仅对活动/更新相关视频）：**

通过标题关键词（event, update, new, patch, 活动, 更新）筛选活动相关视频，调用 youtube-analyzer skill 概括：
```bash
export GEMINI_API_KEY="$GEMINI_API_KEY"
python C:/Users/linkang/.agents/skills/youtube-analyzer/scripts/analyze_youtube.py "https://youtu.be/{video_id}" "{config.youtube.analyze_prompt}" --model gemini-2.5-flash
```

**下载缩略图：**

为每个视频下载 YouTube 缩略图，保存到日报同级目录的 `thumbnails/` 文件夹：
```python
import urllib.request, os
thumb_dir = f"{config['output']['vault_path']}/{config['output']['folder']}/thumbnails"
os.makedirs(thumb_dir, exist_ok=True)
for vid_id, title in videos:
    url = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
    path = f"{thumb_dir}/{vid_id}.jpg"
    try:
        urllib.request.urlretrieve(url, path)
    except:
        urllib.request.urlretrieve(f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg", path)
```

**用浏览器打开视频链接：**

日报生成完成后，自动用资源管理器打开所有近期视频链接，方便用户直接观看：
```bash
# Windows: 用 start 命令在默认浏览器中打开
start "" "https://youtu.be/{video_id}"
```

每个视频链接间隔 1 秒打开，避免浏览器卡顿。

**填写到日报：**

在日报中新增「YouTube 攻略动态」板块，格式：
```markdown
## X. YouTube 攻略动态 📺

| 频道 | 视频标题 | 发布日期 | 播放量 | 缩略图 |
|------|----------|----------|--------|--------|
| {channel} | [{title}](https://youtu.be/{id}) | {date} | {views} | ![[thumbnails/{id}.jpg\|200]] |

### 视频内容概括
- **[视频标题]**：（AI 概括内容）

### 评论区精选
- **[视频标题]**（{评论数}条评论）：
  - "评论内容"（{likes}赞）— 简要标注评论主题
```

如果近 7 天无新视频，写"近 7 天无新视频更新"。

### Step 5: 游戏内容观察 🎮

数据源：Discord #dev-dialogue + #status-update + 攻略站

```bash
python <SKILL_DIR>/scripts/fetch_discord.py --config <CONFIG> --hours 24 --channel dev-dialogue
python <SKILL_DIR>/scripts/fetch_discord.py --config <CONFIG> --hours 24 --channel status-update
```

攻略站用 `web_fetch` 抓取：
- https://lastasylumplague.com/ — 新英雄、建筑升级
- https://lastasylum.com/ — FAQ、礼包码

填写：新英雄/角色、新系统、数值变化、玩家体验备注。

### Step 6: 应用商店数据 📊

数据源：SensorTower 排名 + data.ai + App Store 评论

```bash
# App Store 评论分析
python <SKILL_DIR>/scripts/fetch_appstore.py --config <CONFIG> --reviews --country us
```

SensorTower 排名：
```python
rankings = api.get_category_rankings(app_ids=["com.phs.global"])
```

data.ai 补充：
```python
import sys
sys.path.insert(0, "C:/Users/linkang/.agents/skills/appannie-query/scripts")
from aa_api import AppAnnieAPI
aa = AppAnnieAPI()
ratings = aa.app_ratings("google-play", "com.phs.global")
```

填写：畅销榜排名变化、评分变化、近期差评/好评关键词。

### Step 7: 竞品对比备注 📌

基于以上所有数据，AI 综合分析生成：
- 与我方产品的差异化观察
- 值得借鉴的点
- 风险/威胁点

### Step 8: 生成日报

读取 Obsidian 日报模版：
```
C:\ADHD_agent\竞品调研\竞品日报模版.md
```

填充所有板块数据，头部信息：
- 游戏名称：{config.display_name or config.game_name}
- 日期：YYYY-MM-DD（周X）
- 记录人：Nomi（自动监控）

**笔记属性（Frontmatter）格式：**
确保 `game` 属性不包含冒号，与 Obsidian 现有属性一致。
```yaml
---
tags:
  - 竞品日报
game: {config.game_name}
---
```

**活动/礼包名称引用规则：**
- 优先使用中文名链接（与独立笔记文件名一致），如 `[[寻医之道]]`
- 如果日报正文需要显示英文名，用别名语法：`[[寻医之道|Path of Healing]]`
- 确保独立笔记的 frontmatter `aliases` 中包含英文原名，这样 Obsidian 也能识别英文链接

用 `write` 工具写入文件。

## 数据源详细参考

各数据源的 API 细节、认证方式、限制和注意事项见：
`<SKILL_DIR>/references/data-source-guide.md`

## 定时任务

建议通过 cron 每天 10:00-11:00 (Asia/Shanghai) 触发，抓取前 24 小时数据。

cron 任务文本示例：
```
读取 competitor-monitor skill，执行 Last Asylum Plague 竞品监测日报，抓取过去 24 小时数据，生成日报写入 Obsidian。
```

## 扩展

添加新竞品游戏：
1. 在 `configs/` 下新建 JSON 配置文件
2. 在 Obsidian 中创建对应的「竞品监测链接大全」文档
3. 用相同流程执行，脚本通过 `--config` 参数切换目标
