---
name: x3-tsv-export-migration
description: X3 导表 2026-05-29 迁移到 TSV 缓存——导入只认 tsv，配置改动直接改 tsv 不碰 xlsx；xlsx 仅历史备份(下周删)。改X3配置/导表前必读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6d162bb7-4b67-48ce-a1e5-225a2fab7f22
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
