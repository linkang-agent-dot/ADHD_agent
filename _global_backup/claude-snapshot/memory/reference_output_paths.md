---
name: 活动设计全链路产出路径规范
description: 活动设计各环节（数值方案、美术需求、出图、数据分析）的固定产出路径
type: reference
originSessionId: 8b887c7c-4a4b-436d-8073-e5f718d1200d
modified: 2026-07-29T08:41:41.768Z
---
## 数值方案
```
C:\ADHD_agent\KB\产出-数值设计\{项目}_{年份节日}\{项目}_{年份节日}_{活动类型}_数值方案.md
```
例：`X2_2026科技节\X2_2026科技节_集卡册_数值方案.md`

## 美术需求文档
```
C:\ADHD_agent\KB\产出-本地化与美术\{项目}_{年份节日}_{类型}_美需.md
```

## 美术参考图 / 出图
```
C:\ADHD_agent\KB\产出-本地化与美术\ref-images\{节日}\          ← GRFal 参考图
C:\ADHD_agent\KB\产出-本地化与美术\{项目}\{类型子文件夹}\{类型}_{模型}_{日期时间}.png  ← 生成图
```

## 赛后数据分析
```
C:\ADHD_agent\KB\产出-数据分析\{节日}\
  图表1_Revenue_Trend.png
  图表2_Module_Structure.png
  图表3_User_Growth.png
  input_data.json
  notion_content.md
  wiki_content.md
```

## 要发给别人的 HTML → 必须出「单文件自包含版」（2026-07-29 新增）
凡是要**发出去**的 HTML（验收速览 / 交互原型 / 报告 / 对比页），除维护用的外链版外，
再产一个把图片视频 base64 内嵌的单文件版——对方本地没素材目录也能开，也省得部署内网 demo。
```
python C:\ADHD_agent\KB\方法论\tools\html_inline_assets.py <源.html>   → <源>_单文件.html
```
自动压缩：png/jpg→WebP(约1/6)、mp4→H.264 CRF28 去音轨(约1/4)；带缓存、缺素材中止、>15MB 告警。

**多页分享包**（index + reports/*.html + assets/）用另一个：
```
python C:\ADHD_agent\KB\方法论\tools\html_bundle_site.py <入口.html>   → <目录名>_单文件版.html
```
递归收链到的 html、内嵌全部素材、**默认剥离 demo 登录闸门**（见 [[reference_html_deployer_gotchas]] 第5条，
不剥的话离线打开永远卡 Loading）。范式＝`KB\产出-数值设计\X3_下期节日优化清单\`：10 页 9.9MB → 单文件 3.1MB。
🔑**架构定案（踩过坑别回改）**：srcdoc iframe 实测 **contentDocument 取不到、postMessage 也不通**（http/file 都一样），
所以父子零通信——跨页链接在**打包期**重写成 `#p/<key>` + `target="_top"` 走顶层 hash 路由；
高度不测量、iframe 固定 `calc(100vh - 头高)` 内部滚；进页滚锚点靠把脚本拼在 srcdoc 末尾由子页自己跑。
🪤**srcdoc 的 base URL 继承父文档 → 页内锚点会把外壳自己加载进 iframe（页面套娃、header 两层）**：
子页里的 `href="#sec"` 被解析成「外壳URL#sec」而不是页内跳转。必须给每个子页注入 anchor-fix 脚本，
把纯锚点点击改成 `scrollIntoView({block:"start"})`（放行 `target="_top"` 的 `#p/` 路由）。
**别加 `behavior:"smooth"`**——长文档里会出现"点了半天在空白区滑"，原生 hash 跳转本来就是瞬间的。
🪤`--exclude <页名>` 可剔掉不想收的页（页签不出现），指向它的链接自动降级成不可点，免得点出 404。
💡**入口选谁 = 决定发出去的是哪一份**：以某个子报告为入口，就只打包它 + 它链到的页，得到一份独立可发的文件。
只有一页时自动**不套外壳**（没有可跳转对象，空页签栏碍事）。2026-07-29 就是这么从同一个分享包切出三份：
`X3下期节日优化清单_单文件版`(9页·index入口) / `X3双节回归_改动效果清单_单文件版`(5页·m4-changes入口) /
`X3双节回归_大盘增量_单文件版`(单页无壳·m1-daipan入口)。
范式＝`KB\产出-数值设计\X3_马戏节\_马戏节_验收_7.29.html`(外链版·改文案用) + `_单文件版.html`(发人用)。
🪤竖屏视频别直接 `<video>` 塞进固定高卡片（cover 会裁掉大半）→ 卡片放**原分辨率 poster**＋播放钮，
点击进 lightbox 按原比例播；poster 用 `ffmpeg -ss N -i x.mp4 -frames:v 1 -q:v 2`（**别加 scale**，加了就是放大糊图）。

## 交互原型（活原型+实时说明 一体 HTML）
```
C:\ADHD_agent\KB\产出-交互原型\{项目}_{年份节日}\{模块}_交互原型.html
```
例：`X3_2026深海节\大富翁_珍珠贝进度系统_交互原型.html`；范本：`KB\方法论\范本_交互模块_限时商店一体原型.html`。
原型即交互说明（可直接给测试/程序，不必再写文字说明）；策划案 sheet 里放**单独页签**存归档链接 + 派生美术（非首页签）。详见 [[quality-gate]] 交互模块工作流。
