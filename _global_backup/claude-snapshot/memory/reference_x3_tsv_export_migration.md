---
name: x3-tsv-export-migration
description: X3 导表 2026-05-29 迁移到 TSV 缓存——导入只认 tsv；2026-06-04 起新增 jenkins-xlsx-tsv-gate 强制 xlsx 与 tsv 一致（旧"xlsx下周删/只改tsv"已被推翻，见顶部章节）。改X3配置/导表前必读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6d162bb7-4b67-48ce-a1e5-225a2fab7f22
---

## ⚠️ 2026-06-04 重大变化：jenkins-xlsx-tsv-gate（推翻下方"xlsx下周删/只改tsv"）

xlsx **没删**，反而新增了 Jenkins gate（导表 job `X3导配置` 内置 stage），**强制 xlsx 与 tsv 保持一致**。提交者署名 `jenkins-xlsx-tsv-gate`，commit msg `Keep XLSX and TSV synchronized for dev`。本次会话（夏日装饰礼包 210917/918/919 补钻石/VIP）实测观察到的规则：

| 改动方式 | gate 行为 |
|----------|-----------|
| **只改一边**（单边漂移，如只改 tsv） | gate `auto-safe decision direction=tsv->xlsx`，自动把改动同步到另一边、生成同步提交；**但本次 build `gate_rc=24` 标 FAILURE**，需基于 gate 同步提交再导一次才 SUCCESS（两步） |
| **两边都改且不一致**（divergent dual-sided） | gate **拒绝**：`Rejected: Auto-merging divergent dual-sided edits \| direction is ambiguous` |
| **两边一致** | 通过（无漂移，`gate_rc=0`） |

`gate_rc` 速查：`0`=一致通过；`24`=单边漂移已 auto-fix 同步、需基于同步提交重导；`21`=**手动 jolt 触发时 before==after 没 diff、退化成纯一致性检查发现 `mismatch=1`**（xlsx≠tsv 但 gate 拿不到方向 → `FAIL Safe formatted-diff sync failed`）。rc=21 的解法：本地跑 `python scripts/sync_xlsx_tsv.py --from-tsv --files data/<表>.xlsx` 把 tsv 同步进 xlsx，或等 gate 处理真实 push diff 时自动同步（会生成 `Keep XLSX and TSV synchronized` 提交，pull 下来即一致）。

gate 日志关键行：`[sync_xlsx_tsv] auto-safe decision group=data/Reward.xlsx direction=tsv->xlsx reason=one-sided ... refs <old>-><new>` + 末尾 `gate_rc=24` / `exit 24` → `marked build as failure`。校验 `mismatch=0 crlf=0` 表示数据已同步一致。提交信息明写 **`Directive: Do not bypass the Jenkins XLSX/TSV gate for config branches`**。

**实操结论（覆盖下方旧指引）**：
- 想一次过 → **xlsx 和 tsv 两边同时改成完全一致**（同一提交），gate 看一致直接放行。
- 嫌改 xlsx 麻烦 → **只改 tsv**，接受 gate 两步：第一次导表 rc=24 失败+自动同步 xlsx 生成提交 → `git pull` 后基于该同步提交再触发导表才 SUCCESS。
- 副作用：gate 会产生大量自动提交 + 偶发 `Revert "...rebase 残留"`，dev 顶端会很乱；push 前先 `git pull --rebase`。
- ⚠️ 旧 `jolt_verify.py` **不认识 gate 两步**，只会报第一次的 FAILURE(rc=24)——需手动判断是不是 gate 同步导致的"假失败"，再追同步后的那次 build（待把 gate 逻辑并入脚本）。

**导表 FAILURE 归因（别被 build 红叉误导成"我改错了"）**：导表 job 串了多个独立检查，FAILURE 要看 console 末尾真正报错分类——
- `gate_rc=21/24` → xlsx/tsv 一致性问题（见上）
- `rewardID:xxx ID不连续, minID/maxID` → Reward 表同 RewardID 内行 ID 断号（见 [[reference_x3_reward_table_rules]]）
- `Pack.xlsx column order changed; hot update may not support it; programmer confirmation is required` → **另一个独立 push 钩子**（`pre_push_check.py`/`excel_diff`）检测到列顺序/类型漂移（如 `#礼包表备份` sheet '10011'字符串→数字），常由**别人合并/openpyxl 重存**引入，**与你的改动无关**，需程序员确认放行。2026-06-04 实测：我只改 Reward，gate_rc=0/mismatch=0 全过，但龚亮海妖3合 dev 带进 Pack.xlsx 列漂移 → 整个 dev 导表 FAILURE。先 `git log -- data/<报错表>.xlsx` 看是不是自己改的，不是就别背锅、找对应改动人。
- `! [rejected] HEAD -> dev (fetch first)` + `failed to push some refs to 'git@git.tap4fun.com:x3/x3-project.git'` → **导表 job 末尾把生成的配置推回 x3-project(client_master)仓时撞了并发 push**（别人同时也在 push x3-project/dev）。**表转换/depend_checks 全过了，纯下游 push race，跟你的数据无关**。解法：直接**重新触发导表**（job 会重新 fetch 再 push）；可能 build 已在队列中（`触发失败:任务已在队列`），轮询那个 build 号即可。2026-06-05 实测：#612 因此 FAILURE，重触发 #613 SUCCESS。
- **本地 pre-commit 钩子已自动同步**：只改 tsv 时，gdconfig 的 `git commit` 本地 pre-commit hook (`sync_xlsx_tsv`) 会当场 `direction=tsv->xlsx` 把改动同步进 data/<表>.xlsx 并**把重生成的 xlsx 一起 add 进本次 commit**（输出末尾 `mismatch=0 crlf=0`）→ 提交即 xlsx/tsv 一致，导表一步过，**不再是旧版的 rc=24 两步**。副作用：commit 会顺带带进 xlsx 里别人之前只改 tsv 攒下的历史漂移（一次性刷掉，正常）。

> 下面 2026-05-29 的"只改 tsv 不碰 xlsx / xlsx 下周删"是 gate 出现**之前**的旧流程，保留作沿革；以本章节为准。

---

## 核心变化（2026-05-29，廖强/zhangli/常潇允 推动）

X3 导表（Jenkins **X3导配置**）已从「读 xlsx 现导」迁移为「**读提交的 tsv 缓存**」。三个主分支已同步。

**所有配置改动以 tsv 为准。** xlsx 下周删除，目前仅作备份过渡（`改表和实际生效都走 tsv`）。

| 项 | 说明 | 来源 commit |
|----|------|------|
| 导表改读 tsv 缓存 | 不再从 xlsx 现导 | `ec5c043` Route config export through TSV cache |
| tsv 生成手动化 | pre-push hook 明写 "TSV cache generation is manual-only" | `7538887` |
| 脚本递归镜像子目录 | `data/i18n/Text.xlsx → tsv/i18n/Text__Text.tsv` | `240e944` Cover nested i18n workbooks |
| push 自动跑一次 xlsx→tsv | 常潇允补充，**但后续会干掉，别依赖** | — |

## 主流程：直接改 tsv（非翻译配置）

实践已确认（zhangli 屏蔽尼罗/夏日礼包、林康改数值都如此）：**非翻译的配置改动直接改 `tsv/` 下文件，不碰 xlsx**。一条龙 skill + 工具：

- **Skill `x3-config-export`**（`C:\Users\linkang\.claude\skills\x3-config-export\`）：定位→安全改tsv→提交→导表→验证全流程，含「屏蔽礼包」等列位置速查表。触发词「改X3配置/屏蔽礼包/改timecycle/改tsv/导X3配置」。
- `scripts/tsv_edit.py`：安全改 tsv（`show`定位列 / `set`断言旧值改单元格 / `remove`从管道列表删ID；保LF、dry-run）。替代每次临时写脚本。
- `scripts/jolt_verify.py`：jolt 触发 + 自动轮询构建 + 报 SUCCESS/FAILURE+分支。替代裸 `jolt_export.py`。

⚠️ **对已 tsv-直接改过的表，绝不能再 `xlsx_to_tsv.py` 重生成**——xlsx 是旧的，重生成会覆盖回去（尼罗/夏日屏蔽只在 tsv，一重生成就还原）。

## 唯一仍碰 xlsx 的窄例外：i18n 翻译扫描

只有翻译走 `x3-translation-automatic` 的扫描工具链（CompositeI18n）时会读/写 `data/i18n/Text.xlsx`。**即便这样，导入仍只读 `tsv/i18n/Text__Text.tsv`**——改完 Text.xlsx 必须 `python scripts/xlsx_to_tsv.py --files data/i18n/Text.xlsx` 重生成那一个 tsv 并提交。或干脆直接改 tsv 的语言列（状态列标 `AI`）。**除此之外任何配置都不碰 xlsx。**

- tsv 命名：`tsv/{data下相对目录}/{xlsx文件名}__{Sheet名}.tsv`（顶层 data/ 无子目录前缀）。
- tsv **是入库的**（不是 .gitignore），导表直接吃它。
- ⚠️ 重生成只针对「确实从 xlsx 改的那个文件」；**绝不全量 `--all` 或对已 tsv-直接改过的表重生成**，否则覆盖回旧值。

## 血泪教训（2026-05-29 X3NEW-734 / 礼包timecycle）

**只改 xlsx 不重生成 tsv = 修复完全无效**，因为导表读旧 tsv：
- 礼包 timecycle 修复改了 `Pack.xlsx`（commit 84f59ff），但 tsv 还是旧 timecycle 1096 → 导出仍旧错。
- ActvScoreTask 208/209/213 翻译写进 `Text.xlsx`（commit 5e738e7），但 `tsv/i18n/Text__Text.tsv` 仍是 `新增`+空翻译 → 俄服仍显中文。
- 重生成 tsv（zhangli 96ed6d0 / 我本地同结果）后两个修复才真正落地。

会话开头的 Jenkins 报错 `tsv/i18n/Text__Text.tsv file not exist，无法正常多语言转换` 根因也在此：i18n 子目录 tsv 没被旧脚本覆盖生成（240e944 修脚本递归后解决）。

## 隐性坑

- openpyxl/merge 驱动碰过 xlsx 后，`data/*.xlsx` 可能出现 +几字节的假阳性改动（zip 元数据，`0 insertions/0 deletions`）。提交前 `git hash-object` 对比 HEAD，确认是假阳性就 `git checkout HEAD -- <xlsx>` 还原，再从干净 xlsx 重生成 tsv。
- 多人会并行做同一份 tsv 重生成 → push 可能被拒（rejected, fetch first）。先 fetch 比对 blob 哈希，若与远端逐字节相同直接 `git reset --hard origin/<branch>` 丢掉重复提交，无内容损失。

## 关联
- [[reference_x3_gdconfig_repo]] [[workflow_x3_auto_jolt_export]] [[reference_x3_i18n_workflow]]
