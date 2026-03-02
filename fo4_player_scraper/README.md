# FC Online 传奇球员数据爬虫

从 FIFAaddict (cn.fifaaddict.com) 爬取 FC Online 传奇球员数据。

## 目标数据

- **传奇时刻 (ICTM)** - Icon Moment
- **传奇永恒 (ICTMB)** - Icon Moment Boost  
- **Icon传奇 (ICON)** - Icon卡

## 数据字段

### 基础信息
| 字段 | 说明 |
|------|------|
| 球员名称/简称 | 球员全名和简称 |
| 赛季全称/代码 | 如 "Icon Moment" / "ictm" |
| 位置 | ST, CAM, CM, CB 等 |
| 俱乐部/国籍 | 所属俱乐部和国籍 |
| 身高/体重/年龄 | 身体数据 |
| 惯用脚/逆足等级 | 左/右脚，逆足1-5 |
| 花式等级 | 1-5星 |
| 工资/能力总和 | 游戏内工资和34项能力值总和 |

### 六维汇总能力值
| 六维 | 说明 |
|------|------|
| 速度 | 速度+加速 平均 |
| 射门 | 射术、射门力量等平均 |
| 传球 | 短传、长传等平均 |
| 盘带 | 盘带、控球等平均 |
| 防守 | 抢断、铲断等平均 |
| 强壮 | 体力、强壮等平均 |

### 34项完整能力值（基础值）
| 分类 | 能力值 |
|------|--------|
| 速度 | 速度、加速 |
| 射门 | 射术、射门力量、远射、站位、凌空抽射、罚点球 |
| 传球 | 短传、视野、传中、长传、任意球、弧线 |
| 盘带 | 盘带、控球、灵活、平衡、反应 |
| 防守 | 人盯人、抢断、战术意识、头球、铲断 |
| 身体 | 强壮、体力、侵略性、弹跳、冷静 |
| 守门 | GK扑救、GK手控球、GK大脚开球、GK反应、GK防守站位 |

### 位置评分
各位置的OVR评分：ST, CF, LW/RW, CAM, CM, CDM, LB/RB, CB, GK 等

### 特性技能
球员拥有的特殊技能，如"偷猎者"、"外脚背射门"、"善于头球"等

## 关于强化/加成数据

⚠️ **重要说明**：FIFAaddict 网站的API只提供**基础能力值**，不包含：
- 强化后能力值（+1 ~ +10 强化）
- 球队加成后能力值
- 等级加成后能力值

这些加成数据需要在游戏内根据公式计算：
- 强化加成：每级强化按比例提升能力值
- 球队加成：同俱乐部/国籍球员组合加成
- 等级加成：球员等级提升带来的加成

如需这些数据，建议：
1. 获取基础数据后，根据游戏公式自行计算
2. 或查找提供这些数据的其他数据源

## 安装

```bash
# 1. 进入项目目录
cd fo4_player_scraper

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
python -m playwright install chromium
```

## 使用

### 推荐：使用最终版爬虫
```bash
python legend_scraper_final.py
```

### 文件说明
| 文件 | 说明 |
|------|------|
| `legend_scraper_final.py` | **推荐** - 完整版传奇球员爬虫 |
| `test_player_api.py` | 测试API数据获取 |
| `player_api_data.json` | API返回数据示例 |

## 输出

数据保存在 `output/` 目录：
```
output/
├── fc_legends_时间戳.json    # 完整JSON数据
├── fc_legends_时间戳.xlsx    # Excel汇总表
├── ictm_时间戳.xlsx          # 传奇时刻单独表
├── ictmb_时间戳.xlsx         # 传奇永恒单独表
└── icon_时间戳.xlsx          # Icon传奇单独表
```

## API数据结构

网站使用的API: `https://cn.fifaaddict.com/api2?fo4pid={球员ID}&locale=cn`

返回数据结构：
```json
{
  "db": { /* 球员基础信息 */ },
  "attr": {
    "sprintspeed": {"name": "速度", "value": 95},
    "finishing": {"name": "射术", "value": 92},
    // ... 34项能力值
  },
  "traits": { /* 特性技能 */ },
  "dbrelate": [ /* 同名球员其他卡片 */ ]
}
```

## 注意事项

1. **反爬机制**：网站可能有频率限制，脚本已添加0.5-1秒延迟
2. **动态渲染**：网站使用Nuxt.js，数据通过API加载
3. **筛选功能**：赛季筛选需要在页面上点击按钮，URL参数无效
4. **网络要求**：需要稳定网络连接，首次运行需要下载浏览器

## 自定义

### 修改目标赛季
```python
# legend_scraper_final.py
TARGET_SEASONS = {
    "ictm": "ICTM",      # 传奇时刻
    "ictmb": "ICTMB",    # 传奇永恒
    "icon": "ICON"       # Icon传奇
    # 可添加其他赛季...
}
```

### 调整爬取延迟
```python
await asyncio.sleep(1.0)  # 增加延迟避免被封
```

## 技术栈

- **Playwright** - 浏览器自动化，支持JS渲染
- **Pandas** - 数据处理和Excel导出
- **tqdm** - 进度条显示

## 免责声明

本工具仅供个人学习研究使用，请遵守网站使用条款，不要进行商业用途或大规模爬取。
