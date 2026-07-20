---
name: x3-gdconfig-repo
description: X3 配置仓库（git.tap4fun.com/x3/gdconfig）；导入只认 tsv（C:\x3\gdconfig\tsv\），配置改动直接改 tsv 不碰 xlsx，旧 C:\X3\、C:\x3dev\ 已弃用
metadata: 
  node_type: memory
  type: reference
  originSessionId: 22c25965-252c-40fd-9575-d6ee02470233
---

## X3 配置仓库（2026-05-25 起）

| 项 | 值 |
|----|----|
| Remote | `https://git.tap4fun.com/x3/gdconfig` |
| 本地仓库根 | `C:\x3\gdconfig\` |
| **配置真源（改这里）** | `C:\x3\gdconfig\tsv\`（导入只认 tsv） |
| xlsx 目录 | `C:\x3\gdconfig\data\` — **仅历史备份，下周删，不要改/导** |
| 常用分支 | `master` / `dev` / `feature/summer-love-song` / `dev-summer-love-song` |

## ⚠️ 已弃用路径（不要读写）

- `C:\X3\` — SVN 时代残留，无 .git
- `C:\x3dev\` — 中间过渡目录残留，无 .git
- `C:\x3\gdconfig\data\*.xlsx` — 仅备份；**导入/改表绝不找 xlsx**，全部在 `tsv\` 下操作

## ⚠️ 导入只认 tsv（2026-05-29 起）

Jenkins「X3导配置」读仓库里提交的 **tsv 缓存**，不读 xlsx。**配置改动直接改 `tsv\` 下文件**（用 `x3-config-export` skill 的 `tsv_edit.py`），改完 commit tsv → push → jolt 导表。**绝不对已 tsv-改过的表跑 xlsx_to_tsv 重生成**（xlsx 是旧的，会覆盖回去）。详见 [[reference_x3_tsv_export_migration]]。

## 常用配置表速查（tsv 真源）

tsv 命名：`tsv/{文件名}__{Sheet名}.tsv`。具体 sheet 用 `tsv_edit.py show` 确认。

| 用途 | tsv（部分 sheet） |
|------|------|
| 主活动表 | `tsv/ActvOnline__ActvOnline.tsv` |
| 时间周期 | `tsv/TimeCycle__*.tsv` |
| 累充任务档位 | `tsv/ActvTask__*.tsv` |
| 拜访礼包 | `tsv/ActvVisitPack__*.tsv` |
| 礼包 | `tsv/Pack__Pack.tsv` / `Pack__ChainPack.tsv` / `Pack__PackTypeInfo.tsv` |
| 奖励组 | `tsv/Reward__*.tsv` |
| 排行榜 | `tsv/Rank__RankCfg.tsv` / `Rank__RankRewardSlotCfg.tsv` |
| 每日榜 | `tsv/ActvDailyRank__*.tsv` |

## 工作流

- 改配置一条龙（定位→改tsv→提交→导表→验证）：skill `x3-config-export`
- push 后触发并验证导表：[[workflow_x3_auto_jolt_export]]（用 jolt_verify.py）
- Reward 写入约束：见 [[reference_x3_reward_table_rules]]
- 累充隔离机制：见 [[reference_x3_recharge_isolation]]

**How to apply:** X3 配置读写一律走 `C:\x3\gdconfig\tsv\`。看到上下文提 `data\*.xlsx`、`C:\X3\`、`C:\x3dev\` 等旧路径要主动纠正——导入这块永远不找 xlsx。

## 2026-07-14 实测更正（手册推广案）
- **本地导表真入口 = `Tools/table_exporter/ExportTable.py`**（在该目录下直接 `python ExportTable.py`，exit 0=全绿）；`scripts/ExportTable.py` 不存在（旧记录过时）。`export_table.bat` 结尾带 `pause`，**后台跑必挂**，要么前台要么直调 py。
- **worktree 模式**：主仓被隔离闸门保护（多 agent 并发），改配置标准姿势=`git worktree add ../gdconfig-<名> <分支>`，tsv 改动/commit/导表全在 worktree 目录做。
- **x3-project commit-msg hook 要求提交信息以分支型前缀开头**（如 `X3NEW-xxx：...`），不合格式直接拒。
- 登录购买手册(type27)配置链**四环**：ActvOnline.ContentID→ALP(Pack/Pack2/Group)→**ActvLoginPurchase__ActvLoginRewardGroup(Group→Day→Reward,别漏这张)**→Reward。
- **本地生效链手动分步版**（local_reload.bat 各分支带 pause 不适合无头跑）：①`Tools/table_exporter/ExportTable.py`（产物→`temp_dev/{Proto,ProtoGen}` + 本目录生成 numeric .cs）②`copy_numeric_files.py`（⚠️**拷完删源**，二跑 GenCSharp 会报 CfgProtoTextEx.cs 缺失——顺序必须 GenCSharp 在前或知道此行为）③GenCSharp 依赖 `local.json`（不吃 CLIENT_PATH 环境变量，格式 `{"client_path": "C:/x3-project/client"}`）④`protogen-csharp/win/TableProtoGen.exe --only_gen True --client_path <client>` 重生成 CfgProtos ⑤temp_dev/ProtoGen 递归拷 client 与 `server/Resource/Assets/Res/Config/ProtoGen`（server 二进制必须重编再起服，否则 config 预载崩）。
- **🔴手加 CfgProtos tag 必以真导表为准**：导表按 tsv 列序重排 proto tag（2026-07-14 实证：新加 2 列生成 tag=52/53，把原 AffixInfos 从 52 挤到 54；手按"尾部+1"猜 53/54=读错字段）。正确流=先跑真导表看生成 proto 再对齐，或直接用 TableProtoGen 生成覆盖手写。
- **TableProtoGen 全量重写会清空 `Proto/custom_types.json`**（0增228删）——重生成后 checkout 恢复它，且只挑本功能的 proto/cs 提交（其余为行尾/版本 drift）。
- **🔴新 DK 三处注册缺一不可（2026-07-14 换皮验证实踩）**：①`Path_Activity.asset` keys 列表+objPath 映射（手文本加行可用）②图片+meta 进工程 ③**`tableResInfo.txt`（导表产物`Tools/table_exporter/`下生成,copy_numeric_files 拷到 client `Assets/Editor/Config/` 后删源）= Editor 模式 DK 白名单**——`ToDisplayKeyAssetPath` 在 UNITY_EDITOR 下先查 `sValidDisplayKeys`,不在名单=报"未被配置表使用"并返回空=**静默不换图**（三件套全哑）。新 DK 被 tsv 引用后**必须重跑 ExportTable 刷新此清单再拷 client**。症状=配置数值全对但换皮全不生效。
