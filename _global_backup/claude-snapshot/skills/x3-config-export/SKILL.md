---
name: x3-config-export
description: >
  X3 配置修改 + 导表一条龙（2026-05-29 起导表读 tsv 缓存，直接改 tsv 不改 xlsx）。
  覆盖：定位字段 → 安全改 tsv → 提交 → 触发 Jenkins 导表 → 自动验证构建结果。
  触发词：改X3配置、屏蔽礼包/下架礼包、改timecycle、改X3数值、改tsv、导X3配置、导表(X3)、
  X3配置生效、夏日/尼罗礼包屏蔽、ActvOnline改、Pack改。
  不含 i18n 翻译扫描（那走 x3-translation-automatic）。
---

# X3 配置修改 + 导表一条龙

## 背景（必读）

2026-05-29 X3 导表迁移：**Jenkins「X3导配置」读仓库里提交的 tsv 缓存，不再从 xlsx 现导**。
- **所有非翻译配置改动 → 直接改 `C:\x3\gdconfig\tsv\` 下的 tsv**，不碰 xlsx。
- ⚠️ **绝不对已 tsv-直接改过的表跑 `xlsx_to_tsv.py` 重生成**——xlsx 还是旧的，重生成会把 tsv 改动覆盖回去（尼罗/夏日屏蔽就只在 tsv）。
- xlsx 下周删除，目前仅作备份。
- 详见 memory `reference_x3_tsv_export_migration.md`。

tsv 命名：`tsv/{data下相对目录}/{xlsx文件名}__{Sheet名}.tsv`（顶层 data/ 无子目录前缀）。

## 工作流（5 步）

```powershell
# 0. 确认分支（X3 仓库分支敏感）
cd C:\x3\gdconfig ; git branch --show-current

# 1. 定位：打印目标行全字段+索引，确认要改的列号
python <skill>\scripts\tsv_edit.py show --file tsv/Pack__ChainPack.tsv --id 647

# 2. 安全改 tsv（断言旧值，命中数校验，保 LF，dry-run 先看）
python <skill>\scripts\tsv_edit.py set --file tsv/Pack__ChainPack.tsv --id 647 --col 2 --old 1 --new 0 --dry-run
python <skill>\scripts\tsv_edit.py set --file tsv/Pack__ChainPack.tsv --id 647 --col 2 --old 1 --new 0

# 3. 看 diff 确认只动了该动的（行级 diff = LF 没坏）
git diff

# 4. 提交（commit msg 用 X3NEW-/X3- 前缀）+ push
git add tsv/<改过的文件...> ; git commit -m "X3NEW-xxx ..." ; git push origin <branch>

# 5. 触发导表 + 自动验证（替代裸 jolt_export.py）
python <skill>\scripts\jolt_verify.py <branch>
```

`<skill>` = `C:\Users\linkang\.claude\skills\x3-config-export`

## 换皮档案（批量 / 多活动换皮时必建，换人不丢信息）

多活动 / 整轮换皮开工前，复制模板 `C:\ADHD_agent\KB\换皮档案\_模板_换皮档案.md` 到
`C:\ADHD_agent\KB\换皮档案\X3\{日期}.md`，按活动模块分节。三步铁律：

1. **开工先读** — 接手 / 新会话第一件事读本轮档案：进度到哪、已知坑、改了哪些 tsv、列号定位。
2. **随手回写** — 定位的列号、改动、状态、踩到 BUG（如 depend_checks 失败），立刻写回档案。
3. **收工更新** — 更新各模块进度 + BUG 解决情况。

**索引 + 改BUG 背景**：开工时在 `C:\ADHD_agent\KB\换皮档案\索引.md` 登记本轮（状态 🔄进行中），收工改 ✅已完结。中途单独派改 BUG 的 agent，**必须把本轮档案路径给它当背景**；BUG 修完回写本档案。

> 单条改动（如屏蔽单个礼包）不必建；多活动 / 整轮换皮才建。
> 发现通用规律 → 同时回写对应 memory（本档案只留本轮特有信息）。

## 工具

### tsv_edit.py — 安全改 tsv
- `show  --file <tsv> --id <行ID> [--max 32]` 打印字段+索引，定位列号
- `set   --file <tsv> --id <ID或逗号列表> --col <N> --old <旧> --new <新> [--dry-run]`
  改前断言每行该列==旧值，命中ID数必须等于传入数，否则不写盘
- `remove --file <tsv> --id <行ID> --cols 49,50 --ids 210917,210918,210919 [--dry-run]`
  从管道列表 `a|b|c` 里移除若干ID，每列实删数必须等于ID数
- `add    --file <tsv> --id <行ID> --cols 49,50 --ids 210917,210918,210919 --after 210921 [--dry-run]`
  往管道列表锚点ID后插入（`remove` 逆操作，解屏蔽/恢复用）；断言锚点存在、ID未重复
- 默认 repo `C:\x3\gdconfig`；--file 相对该目录；写盘保 LF（不被 Windows 翻 CRLF）

### jolt_verify.py — 触发导表 + 验证
- `python jolt_verify.py <branch>`：jolt 触发 → 轮询队列拿 build 号 → 轮询构建 → 报 SUCCESS/FAILURE + 分支 + 结尾行
- 退出码 0=SUCCESS / 2=FAILURE / 3=超时或已有构建在跑 / 1=异常
- 输出 `触发失败: 任务已在/正在执行` 时退回查 lastBuild（不算错误，已有构建会带上你的提交）

## 列位置速查表（本会话已验证）

### 屏蔽 / 下架礼包（启用标志 1→0 + 从累充活动移除）
| 表 | 行 | 列 | 改动 |
|----|----|----|----|
| `Pack__ChainPack.tsv` | 阶梯礼包链ID（如647夏日/648尼罗） | field[2] | `1`→`0` |
| `Pack__Pack.tsv` | 各档礼包ID（如210917/918/919） | field[12] | `1`→`0` |
| `Pack__PackTypeInfo.tsv` | 代表礼包ID（首档，如210917） | field[1] | `1`→`0` |
| `ActvOnline__ActvOnline.tsv` | 累充活动ID（如100595夏日/100594尼罗） | field[49]=Pack列；若 field[50] 也含则一并 | 移除礼包ID |

- field[49] 是表头定义的 `Pack`(int[]) 列；field[50] 无表头名但同为礼包ID列表，**有的活动两列都含礼包、有的只 field[49]**——先 `show` 看哪几列含目标ID再 remove。
- ActvOnline 行名可能是历史复用名（如夏日累充行名叫"26情人节-累充"），**按 TimeCycle 值/含的礼包ID判断，不认名字**（见 memory `feedback_x3_timecycle_name_legacy`）。

### 解屏蔽 / 上架礼包（屏蔽的逆操作，对称反转）
1. ChainPack/Pack/PackTypeInfo 启用标志 `0→1`（`set` 同上，old/new 反过来）
2. ActvOnline 累充把礼包ID **加回原位**：`tsv_edit.py add ... --after <原前一个ID>`（先 `show` 看屏蔽前的邻居ID确定锚点）

### ⚠️ depend_checks 依赖规则（导表会强校验）
**ActvOnline 活动引用的 ChainPack 必须是启用状态**，否则导表报：
`Exception: data_name: ChainPack, depend_keys: {647} not existed`。
- 推论：屏蔽某 ChainPack 时，**任何引用它的 ActvOnline 活动行也必须一并删/停**，否则导表失败。
- 反之解屏蔽时只要把 ChainPack 启用回来，依赖即成立。
- 2026-05-29 踩坑：port 了引用 ChainPack 647 的 ActvOnline 106101，但 647 仍屏蔽 → 导表 FAILURE(#352)；解开 647 后 #353 SUCCESS。

### 其他表
列位置因表而异，**一律先 `tsv_edit.py show` 确认列号再 set**，别凭记忆。常用表参见 memory `reference_x3_score_activity` / `reference_config_library`。

## i18n 翻译例外

翻译文本（`tsv/i18n/Text__Text.tsv`）涉及扫描/翻译工具链，仍可走 xlsx：改 `data/i18n/Text.xlsx` → `python C:\x3\gdconfig\scripts\xlsx_to_tsv.py --files data/i18n/Text.xlsx` 重生成 → 提交 tsv。或直接改 tsv 的语言列（状态列改 `AI`）。详见 `reference_x3_i18n_workflow`。

## 安全红线
1. **不碰 xlsx**（非翻译场景）；**不对已 tsv-改过的表重生成 tsv**。
2. 改前 `git branch --show-current` 确认分支。
3. `set` 用断言、`remove` 用计数校验；先 `--dry-run`。
4. push 可能被拒（多人并行）→ `git fetch` 比对，若与远端 blob 逐字节相同直接 `git reset --hard origin/<branch>` 丢重复提交。
5. 改完必须 `jolt_verify.py` 确认 SUCCESS，别只触发不看结果。
