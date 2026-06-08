---
name: x2-dk-p2-dk-manager
description: X2 新增/换 DK 必须走 P2 数字系统 + x2-dk-manager skill，不是 k1 字符串系统；含活动界面图配置位置
metadata: 
  node_type: memory
  type: reference
  originSessionId: a569f119-e9ef-4f30-9fce-53638169a16d
---

X2 新增 DK / 换活动界面图的**正确链路**。2026-06-04 拓荒节 BP 书本图踩坑：一开始手刨改了 `k1/Editor/DisplayKey`(字符串key系统)，错的。

**Why:** X2 有两套 DK 并存——`cfg.DisplayKey` 是 **int**，配置表引用的是**数字 DK ID**(如 1511094082)。

## 正确系统 = P2 数字 DK
- 编辑期：`x2client/client/Assets/P2/Editor/DisplayKey/Display_<Type>.asset`
- 运行期：`x2client/client/Assets/P2/Res/DisplayKey/Path_<Type>.asset`
- 条目格式(JSON，数字key)：`- '{"key":1511094082,"type":"Icon","desc":"","dkObj":{"assetGuid":"<GUID>"},"intArg":0}'`
- key 分配：跨所有 Display_*.asset 取全局最大 +1
- ❌ `k1/Editor/DisplayKey`(Display_Activity 等，字符串 key `DK_xxx`)是**另一套**，别用

## ⚠️ 查/改 DK 两个铁坑（2026-06-05 拓荒令踩坑）
- **查 key 必须裸数字 grep**：Display_*.asset 条目有**两种写法**并存——单引号包裹 `'{"key":1511094076,...}'` 和**转义** `"{\"key\":1511094076,...}"`。用 `grep '"key":'` 只匹配前者，会**漏掉转义条目** → 误判"缺某 type"。正确：`grep -rn "1511094076" Display_*.asset`（裸数字）。本次就因此误判"拓荒令缺 Icon"（其实 Icon 早有，转义写法）。
- **绝不手改 Path_*.asset**：运行时 Path 文件的 `keys:` 是一长串打包 hex 索引，与下面 `values:` 列表**严格配对**。手删一条 values 会留下孤儿 key hash、索引错位。要回退某次导出：`git checkout HEAD -- <Path_xxx.asset>`（若该文件本次唯一改动就是你加的 key）或重新 Ctrl+Shift+E 导出，**不要手动删行**。
- **多人并发录 DK → push 被拒 → `git pull --rebase` 时 Path_*.asset 的 `keys:` hex 行冲突**（2026-06-05 挖矿镐）：Display_*.asset 是 JSON 行追加，通常能干净三方合并（两边 key 都留）；但 Path 的 `keys:` 单行 hex 不能手 merge。解法：① `git checkout --ours -- <Path_xxx.asset>`（rebase 中 --ours=上游，拿别人那份有效文件）→ `git add` → `git rebase --continue`；② 此时 Display 已含两边 key、但 Path 缺你的 key → **再 Ctrl+Shift+E 重导一次**，从 Display 重新生成 Path（你的+别人的 key 都进去）；③ 验证 `grep -c '^    - key:' Path_xxx.asset` 条目数只 +N 不减（确认没删上游条目）→ `git commit --amend` 折进 DK 提交 → push。
- **commit DK 只收自己的文件**：Ctrl+Shift+E 会把别人遗留在 Display_* 里未导出的改动一起刷进 Path_*（本次刷出 Path_Prefab 的 Theresae→Theresa 路径修正，与挖矿无关）→ commit 前 `git status` 逐个看，无关的 `git checkout -- <file>` 排除，只 `git add` 自己这套（Display_Icon/IconBg + Path_Icon/IconBg + png + meta）。png 走 LFS（`git add` 自动转指针，diff 里是 `oid sha256:`）。
- 推论：Ctrl+Shift+E 导出会按 key **自动去重** Display_*.asset（同 key 重复条目只留先出现的）；想改图要改原条目的 guid，不能靠追加新条目覆盖。

## 工具 = x2-dk-manager skill
- 位置：`C:\ADHD_agent\.cursor\skills\x2-dk-manager\SKILL.md`(Cursor侧，Claude Code 未注册，按 SKILL.md 手动执行)
- 流程：诊断(读.meta GUID→搜Display_*.asset)→分配key→写asset→Ctrl+Shift+E导出(用户)→验证 Path_*.asset→commit
- 方式A(图已在工程内)：不动 meta；方式B/C(丢图)：要质检+meta修Sprite规格

## 活动界面图配置位置(2112 activity_config)
- 表号 2112，QA表 `1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo` / 页签 `activity_config_QA`
- DK 字段：col17(R) `A_INT_icon_displaykey`(活动入口/列表图) + col24(X) `C_INT_title_icon`(标题栏图)
- 节日换皮常见坑：换皮自带的行(如拓荒节-2026-BP从占星节复制)这两列残留旧节日 DK，要一起换
- ⚠️ gsheet_query.py 输出的"row N" ≠ 表格实际行号，写入前必须用 get_values 读 B列id 核对实际行
- 导表：行筛选模式(fwcli googlexlsx -f 2112 写满 fo/config/*.tsv → merge_rows.py 只并目标行→提交)；fwcli 全表下载会夹带别人改的行，必须 merge 收敛

## 行军特效 DK 链路（march_effect.tsv，2026-06-04 拓荒节）
- 行军特效=行军轨迹 TroopsTrail，prefab 在 `Assets/x2/Res/Effect/Prefab/Decoration/Fx_(Deco_)TroopsTrail_<节日>.prefab`
- 配置表 `fo/config/march_effect.tsv` 每行 **3 个 DK 字段**：
  - `DisplayKey`(col5) → prefab 的 Effect DK（Display_Effect.asset，如 tuohuangjie=15119315）
  - `EffectKey`+`EffectExhibitKey`(col6/7) → **不是 DK 系统**，引用 `effect_list.tsv`(id→prefab路径，如 15120705→2024拓荒节)
- 同节日不同年份常复用同一套 prefab（2024淘金之梦=2026拓荒节都用 tuohuangjie）
- ⚠️**移动 prefab 会断运行期 Path_Effect**（2026-06-05 六月节gacha踩坑）：美术把 prefab 连 .meta 移到新文件夹（GUID 不变）→ 编辑期 `Display_Effect.asset`(按 GUID) 不受影响、DK 仍解析；但运行期 `Path_Effect.asset` 是 Ctrl+Shift+E 导出的**路径快照**(`- key:/objPath:` 明文格式，非 hex 打包)，objPath 还停在老路径→游戏按不存在的路径加载失败。修复=重导出 DK，或直接改那条 objPath 为新路径（明文格式改单个 value 值安全，结果与重导出一致）。排查：`grep -n -A1 "key: <DK>" Path_Effect.asset` 看 objPath 指向的文件是否 `ls` 得到。
- ⚠️**tsv 改对但 GSheet 没回写 = 静默回退隐患**：游戏读导出的 tsv，所以「实际表现对」≠「真源对」。节日行常从其它节日整行复制，3 个特效字段(display_key/effect_key/effect_exhibit_key)是**多节日混合残留**（六月节拓荒行：dk=占星 1511020871 + ek=夏日 15120892）。有人直接改 tsv 修对了部署、却没回写 GSheet→下次从 GSheet 导表把 tsv 冲回残留、特效当场坏。排查法：`awk -F'\t' '$2=="<id>"' x2gdconf/.../march_effect.tsv` 取部署值 vs `gsheet_query row 1365 <id>` 取真源值，逐列 diff，把差异写回 GSheet（备份页签→find_row_by_value 按 id 定位实际行→update_range E:H→gsheet_query 复查）。X2 真源=GSheet 见 [[改配置前先确认真源与落地路径]]。

## 活动 HUD 图标链路（activity_config.tsv=2112）
- `IconDisplaykey`(col18)=HUD入口图 + `TitleIcon`(col24)=标题图，都引用 Icon 类型 DK
- 道具图标 DK 在 `item.tsv` col7 `DisplayKey`；主城图标 DK 在 `city_skin.tsv`(节日主城皮肤 skin 字段)
- 反查图内容：`Path_Icon.asset` 按 `key:` 找 objPath（如 1511094083→Pioneer_icon_building）

## ⚠️ 节日复制残留是高频坑（每次换皮必查）
- 新节日整行从上一节日复制 → **DK 字段连 banner 都残留旧节日值**（拓荒节复制占星节：行军特效3字段+HUD的IconDK/TitleIcon 全是占星 1511020867/1511020786 残留）
- 排查：grep 旧节日英文key(astro_2025) / 旧 DK 在配置仓的出现位置；活动展示名(拓荒豪礼)≠配置 comment，要按英文 constant(labor_2026)/LC key 定位
- 改 tsv 安全姿势：**整段 banner+DK 在占星原行和新节日行都唯一**会撞，用 **PowerShell 按 id split 改列**(index17=IconDK/index23=TitleIcon)，保持 LF/无BOM，git diff 只动目标行不误伤旧节日行

关联 [[DK 资源层工作流规则]] [[X2导表工作流]]
