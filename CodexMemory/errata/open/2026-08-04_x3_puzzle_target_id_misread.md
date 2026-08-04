# X3 新拼图目标 ID 误读

- 日期：2026-08-04
- 任务：核查并补建马戏节新拼图活动。
- 现象：把用户所说的“新建拼图”误理解为处理既有 `101830`，并错误地将 `101829` 纳入新旧活动关系。
- 根因：只依据上周知识库中的 `101830` 事故记录推断目标，没有先确认本轮新增活动的明确 ID。
- 处理：用户澄清后固定口径为：`101829`、`101830` 均不改；新增 `101831`，完整复刻 `101830` 且使用独立子配置 ID。
- 状态：open；本轮实现和验证按上述口径执行。

## 用户复盘：为什么这轮理解困难

- “新建拼图”在知识库里紧邻 `101830` 误开放事故，我被历史事故锚定，先入为主地把 `101830` 当成本轮目标。
- 用户第一次说“101830 要建一个新活动”时，“101830”实际是复刻源语境的一部分，但我把它继续解释成目标 ID；随后又自行引入 `101829` 作为“老活动”，扩大了用户没有表达的关系。
- 根本问题不是缺资料，而是开工前没有把三个角色写成明确映射：`复刻源 101830 → 新活动 101831；101829/101830 均不改`。
- 后续硬规则：遇到“新建 / 复刻 / 老活动不变”且上下文出现多个相邻 ID，先用一行固定 `source → target；unchanged`；只有这行无歧义后才查表和落配置，知识库历史不能代替当前需求里的 ID 映射。

## 同轮工具错误

- 现象：创建 worktree 时把尚不存在的目标目录设成命令 `workdir`，命令在执行前即报“目录名称无效”。
- 处理：创建动作必须从现存主仓目录执行；创建成功后下一条命令再切进新 worktree。

- 现象：首次统计拼图子表时把 Reward 的 Group 列误按 col1、Task 的 Group 列也误按 col1，导致零命中并在空集合 `max()` 处退出。
- 处理：先读表头 field 行再取列；本案 `ActvPuzzleReward.Group=col3`、`ActvPuzzleTask.Group=col2`。

- 现象：打印 `Text__Text.tsv` 的 16 语行时，Python stdout 继承 GBK，遇到韩文字符触发 `UnicodeEncodeError`，脚本中途退出。
- 处理：所有读取多语言 TSV 的内联脚本开头固定 `sys.stdout.reconfigure(encoding='utf-8')`；不要依赖 Windows 控制台默认编码。

- 现象：向用户预报复刻规模时口算成 51 条，逐表复算实际为 48 条。
- 处理：批量克隆的规模只采用脚本按表统计结果；本案固定为 AO1 + Puzzle1 + TC1 + Task25 + PuzzleReward11 + Reward6 + i18n3 = 48。

- 现象：在 PowerShell 中给 `rg` 传裸 `README*` 路径模式，Windows 将其当非法字面路径，组合命令 exit 1。
- 处理：文件名筛选用 `rg --glob 'README*'`，或只扫描明确存在的目录；本次已从有效输出确认导表入口。

- 现象：运行 `circus_scan.py --help` 仍直接访问写死的 `C:\\x3\\gdconfig-circus\\tsv`，该旧 worktree 已不存在，报 `FileNotFoundError`。
- 处理：扫描器改为 argparse 接收 `--repo`，默认主仓；任何隔离 worktree 审计都显式传当前路径。

- 现象：按已注册 skill 目录 `.agents\\skills\\x3-config-export\\scripts` 调 `i18n_leak_audit.py`，该同步副本只有 `SKILL.md`、没有 scripts，Python 报文件不存在。
- 初次处理判断仍不完整：`x3-config-export` 的真路径下也没有该脚本；最终用 `rg --files` 定位到 `x3-translation-automatic\\scripts\\i18n_leak_audit.py`。
- 后续规则：工具归属不凭相似 skill 名推断；先在已知 skills 根目录按脚本名精确定位，再执行。`.agents` 副本只保证说明文件，不保证 scripts 同步。
