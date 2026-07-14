# Palworld 工具箱（2026-07-13 建）

图鉴数据管线：paldb.cn → pals_full.json → 桌面《幻兽帕鲁1.0_全图鉴.html》

| 文件 | 作用 |
|---|---|
| `paldb_crawl.py` | 爬 paldb 全帕鲁：读同目录 `paldb_pals.html`（列表页 SSR 快照，过期就重新 curl 存一份）→ 逐只抓详情页（301 个，带重试+断点续传）。字段：三围/工种等级/伙伴技能+效果/骑乘/飞行/鞍具科技等级/minlv 野外最早等级 |
| `inject_data.py` | 把 `pals_full.json`（需在 cwd）精简注入图鉴 HTML 的 `const PALS` 行，可重复执行 |
| `pals_full.json` | 2026-07-14 快照，299 只（已去重+技能补全，唯枯星龙官网500无数据） |
| `paldb_pals.html` | 列表页快照（1.28MB，SSR 含全量卡片） |

**刷新流程**（游戏出平衡补丁后）：
1. 重新下载列表页：`python -c "import urllib.request;open('paldb_pals.html','w',encoding='utf-8').write(urllib.request.urlopen(urllib.request.Request('https://paldb.cn/pals',headers={'User-Agent':'Mozilla/5.0'})).read().decode())"`
2. `python -X utf8 paldb_crawl.py`（约 10 分钟；改了解析字段要先删旧 json 或调断点条件）
3. 把 pals_full.json 放 cwd 跑 `python -X utf8 inject_data.py`

**解析坑**（改代码前必读）：
- 三围正则必须在"去标签后文本"上用 `\|HP\|+(\d+)` 形态（带前导竖线）
- 列表页卡片的 `<a href>` 开在 `<img>` 之前 → 按 img 切分时 href 归上一段，取 `parts[i-1]` 尾部
- minlv 要在「出现地点」后 4000 字符窗口内抓**带区间**的 `Lv\.\d+[–-]\d+`，否则会把主动技能的 Lv 吃进来
- 详情页 href 尾段 = 官方英文名（Direhowl 等），是英→中映射的可靠键

上层知识入口：memory `project_palworld_guide.md`

## Artifact 发布（给别人看的 Claude 网页）
- 线上地址：https://claude.ai/code/artifact/7328e1d7-c918-49da-b40c-3741b3e77ed8（默认私密，页面分享菜单可开）
- claude.ai 国内不翻墙打不开；国内分享=直接传 paldex_artifact.html 单文件（自包含，本目录有备份）或走 html-deployer 内网 demo
- 适配点：去 Google Fonts 外链 / 去本地互链 / 加数据来源脚注；重发布=同会话同路径重调 Artifact 工具（URL 不变），跨会话传 url 参数
