---
name: x2-operation-banner
description: X2 活动 banner 真源路径 + 走 2112 banner_url 路径引用(非DK) + GRFal 换皮直出落地全链路
metadata: 
  node_type: memory
  type: reference
  originSessionId: beaa9cb5-adb3-4987-a66c-3c38558961fa
---

X2 活动 **banner 图**（节日礼包/任务/累充等的大图）的真源、引用方式、换皮直出落地链路。区别于 [[reference_x2_dk_system]]（DK 图标走数字系统），**banner 不走 DK，走文件路径**。

## 一、真源路径（最大坑：不在 client / D:\UGit）
X2 operation banner 实际落地仓 = `C:\ADHD_agent\in-game-remote-assets\in-game-remote-assets\Assets\X2\operation\EventBanner\`
- **不在** `D:\UGit\x2client`，**不在** `D:\UGit\X2-in-game-assets`（空），`D:\UGit\in-game-remote-assets` 下只有 `operation\P2dlcimg`（P2 的，没有 X2）。
- 每个 .png 配一个 `.png.meta`（Unity GUID）——**换图只覆盖 .png，不动 .meta**，GUID 保持不变。
- 客户端 `x2client\...\TextureNew\Activity` 里有的是部分**源图/分身**（如 `AstrologyChain_bg_Table`），但 operation 实投图以上面 remote 仓为准。

## 二、引用链：2112 activity_config 的 banner_url 列（不是 DK）
表 2112（`activity_config_QA`，resolve `2112_x2_activity_config`）每行活动直接写 banner 文件相对路径：
- col13 `banner_obj_url` / col14 `banner_url` / col25 `mini_banner_url` / col21 `calendar_banner_url`
- 值形如 `assets/x2/operation/EventBanner/labor2026_vertical_abstract_1.png` → 对应上面 remote 仓的同名文件。
- 查"某活动用哪张 banner / 缺哪张"：`gsheet_query.py search 2112_x2_activity_config <节日关键词>`，看这几列。
- ⚠️ **banner_obj_url(col13) vs banner_url(col14) 是不同槽位/尺寸，放错字段=显示错！** 实测：累计任务面板(gacha/挖矿)的 banner 必须放 **banner_obj_url(col13)**（gacha累计 21127382 就是 obj），放进 banner_url(col14) 会用错槽位/尺寸。换皮时**对齐同族活动用的是哪个字段**，别想当然。改字段后**必须导表**（2112=activity_config.tsv，行筛选 merge_rows）否则游戏读旧 tsv 不生效——2026拓荒挖矿就是 GSheet 改对了没导表，白改。
- **col15 `banner_version`（缓存键，换图必查）**：文件名不变只换内容时，客户端/CDN 可能按此版本号缓存旧图 → 换图后把 `banner_version` +1 强制刷新。

## 三、换皮直出落地全链路（本次 2026 拓荒节 2 张 banner 实操）
1. **定槽位**：2112 search 节日 → 拿目标 banner 文件名 + 尺寸（PIL 读 remote 仓现有文件）。
2. **双参考**（[[reference_x3_art_resource_spec]] D 维度）：占星节同槽 banner = 格式/结构锚；拓荒节已完成同族图 = 元素锚。
   - BP礼包(`labor_2026_labor_festival_pkg`)目标 `labor2026_vertical_abstract_1.png` 1536×2752；累计挖矿(`metro_minigame_labor26_task`)目标 `labor2026_mining_task_banner.png` = **2400×1792**（对齐同族 `gear_card_banner_2` 格式；原槽残留的 2752×1536 是错的，累计任务 banner 统一 2400×1792）。
3. **GRFal 生成**：`grfal-api` skill，`generate_image` model=gpt + `--file reference_images=<结构图> --file reference_images=<元素图>`。
4. **upscale**：`upscale_image` model=SeedVR scale=2。
5. **裁尺寸**：PIL `resize((W,H), LANCZOS)` 到原槽精确像素，存 PNG。
6. **覆盖**正式文件（保留 .meta），原文件先备份 `_ORIG_*`。终稿/备份归档 `KB\产出-本地化与美术\X2\活动banner\`。

## 四、GRFal 踩坑
- **generate_image 所有模型都是 long_running**（gpt-image-2 / gemini 实测都拒同步，不只 gpt）：同步 `/api/call` 会报"长任务需走 async"。必须 `--submit-only` 拿 task_id → `--check-task` 轮询（高峰拥堵可 10+ 分钟）。2026-06-05 拓荒装饰预览图复测确认。
- 结果是相对路径 `/api/output/...`，下载需 `https://grfal.tap4fun.com` + Bearer token（`~/.config/grfal-api/token_store.json` 的 access_token）。
- 无 `grfal:logs:read` scope，`--view-logs` 会 403，不影响生成。

## 五、BP礼包/IAP 图有两个槽位（易混，2026拓荒踩坑）
同一个"BP礼包"的 banner 实际有**两处独立配置**，别只改一处：
- **活动面板顶图** = 2112 `banner_url`（如 21127376 → `labor2026_vertical_abstract_1.png` 1536×2752 竖）。
- **商店礼包主视觉** = **2013 IAP `banner_url`(col26)**（如 拓荒BP礼包5档 `2013920164~168` rows6777-6781 → 原 `Activity_bg_AstrologyFestival10.png` 886×1258）。
- ⚠️ **2013 这张图被占星节2025 BP礼包(rows6626-6630)共用** → 换拓荒皮**必须新建文件 + repoint 5 行**，绝不能覆盖原文件（会连占星节一起改）。换皮铁律=不破坏复用源。
- 2013 表头关键列：col3 config_id / col6 pkg_title(LC) / col8 price / col26 banner_url / col27 pop_banner_url；BP礼包按价格分5行(4.99/9.99/19.99/49.99/99.99)同享一张 banner。
- 2013 真源=GSheet(`iap_template_x2（qa）`)，改完需走 X2 导表管线生效。
- ⚠️ **gsheet_query 的 "row N" = 实际 sheet 行 N+1**（差 1）！写 GSheet 前**必用 gsheet_utils 读 B列id 复核真实行号**再 update，否则写错行（2026拓荒实测：query说row6777其实是6778）。
- **X2 导表 iap_template 实操**：`fwcli googlexlsx -r 1z2-AK4... -f 2013_x2_iap_template` 会**直接覆盖写** `fo/config/iap_template.tsv`（全表，不是下到 tmp_xlsx）→ `git diff --numstat` 看是否只有自己的行变（干净就直接 commit，混了别人改动才需 merge_rows.py 回滚非目标行）；x2gdconf 节日配置在 `dev_festival` 分支。

## 六、★生效链路：提交 PNG ≠ 生效，必须触发 CDN 构建（2026-06-05 踩坑）
这些 operation banner 是 **CDN 动态资源**，跟客户端发版无关：
- 链路：改 PNG + push git → **jenkins `import_dynamic_assets`**（在 in-game-remote-assets 这个 Unity 工程跑 `Tools\import.py` = `Builder.ImportAssets` 打 AssetBundle）→ 推**运维 CDN svn 仓**（README 写明）→ 玩家运行时从 CDN 拉新图。
- **光 `git commit/push` 不生效！** 判据：正常加图后 git log 会有一条 jenkins 回提交 `<内容commit> >> http://t4f-mba-2505032:8080/job/import_dynamic_assets/<N>/`；**没有这条 = 构建没跑 = CDN 还是旧图 = 游戏里没生效**。
- 要构建的是 **运营资源仓 in-game-remote-assets**，**不是客户端 x2client**（client 仓里根本没有 EventBanner，不随客户端发版/热更）。
- jenkins `http://t4f-mba-2505032:8080/job/import_dynamic_assets/`（host 172.20.75.66，能 ping；API 裸访问 403 需鉴权/token）。本地跑不了 import.py（需 Unity+jenkins env）。→ 换图后**必须确认这条 jenkins 跑过**（或让有权限的人/上传工具触发），否则白改。
- import.py 只回提交 `*.meta`/`*.gif`，PNG 由上传方先提交；webhook 触发条件存疑（裸 git push 实测未必触发回提交，可能要走团队上传工具）。

## 七、需求沟通
- "稿子挖矿" = **镐子**挖矿（同音），语音转文字常见；拿不准的同音词结合上下文确认。
