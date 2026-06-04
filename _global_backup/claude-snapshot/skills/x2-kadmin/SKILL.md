---
name: x2-kadmin
description: 控制 dev/beta 环境全服自动部署、构建与运维操作；清库与导配置/部署同任务时须先等清库在历史中成功完成再继续。
---

# x2-kadmin

## 概述

- 执行 dev/beta 环境的全服自动化操作：部署、构建、发布、回滚、状态查询
- 执行前输出计划，执行后输出结果摘要与失败情况
- 用户如果没有python3则选择python执行

## 强规则

- **任何情况下都不允许执行或输出线上相关命令**
- **每次执行命令后，必须输出本次实际执行的命令，并说明命令具体含义**
- **每次执行脚本，脚本的所有参数都要齐全并告诉用户含义**
- 严格只操作用户明确指定的环境与服务器，不允许扩展到其他机器
- 任何需要执行脚本/命令的操作，一律使用 required_permissions: ["all"] 执行（避免沙盒阻断系统库/工具）。
- 若用户未授权 all 权限，需提示原因并请求授权后再执行。
- 使用该Skill的时候，只允许执行本文档规则下的脚本命令，其他一律不允许执行
- 不允许大批量服务器的导配置清库等写操作
- **如果当前是windows环境，那么禁止使用 &&，而是使用 PowerShell 支持的分号**
- **清库与后续写操作顺序**：同一任务中若包含 **清库**（`clear_db`）以及 **导配置热更**、**导配置重启** 或 **部署**（`deploy.py`），必须先 **等待清库工作流执行成功完成**，再触发后续任一操作；**禁止**在清库 API 刚返回 `success`（仅表示已入队/已触发）后立即执行导配置或部署。
- **确认清库完成**：通过「命令 5」查询该服 `x2gs_<server_id>_清库` 的 **执行历史**（`-m config -o clear_db -t history`），解析最新一条记录为成功后再继续；若清库失败或状态不明，不得继续导配置/部署，需向用户说明并建议先在 Kadmin 排查。

## 任务流程

1. 识别目标环境，仅允许 dev 或 beta
2. 确认操作类型与范围
3. 执行操作并收集结果
4. 汇总并给出失败重试建议

## 清库 → 导配置 / 部署 的标准流程

当用户需求同时涉及清库与导配置（热更/重启）或仅部署时，按以下顺序执行，不得省略「等待清库完成」：

1. **触发清库**：使用「命令 4.1」执行 `workflow_execute.py --keyword clear_db ...`，并如实告知用户含义。
2. **等待清库完成**（必做）：
   - 使用「命令 5.3」查询清库工作流 **历史**：  
     `python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e <env> -m config -s <server_id> -o clear_db -t history`
   - 解析返回 JSON 中该工作流 **最新一条**执行记录：状态为 **成功**（或平台约定的完成态）后，才进入下一步。
   - 若最新记录仍为运行中/排队：间隔约 **15～30 秒** 再次查询，直至成功或失败；**失败则停止**，不执行后续导配置/部署。
3. **再执行导配置或部署**：清库确认成功后，再执行「命令 4.2 / 4.3」或「命令 1」；若用户意图是「导配置重启」，仍按既有规则只跑 `restart_with_config`（已含部署），不再重复 `deploy.py`。

说明：工作流触发接口返回的 `success` 只表示请求被接受，**不等于**清库已在服务端跑完；必须以历史记录中的完成状态为准。

## 命令 1：部署/重启（kadmin）

- 关键词：部署、重启
- 作用：重启 kadmin 上的 dev 或 beta 服务器
- 脚本：`scripts/deploy.py`

命令模板：

```
python3 scripts/deploy.py -e <env> -b <branch> -s <server_id>
```

参数要求：

- `-e/--env` 必填，仅允许 `dev` 或 `beta`
- `-b/--branch` 必填，分支名或 tag 名
- `-s/--server` 必填，服务器 ID
- 若缺少或多出参数，先提示该关键词对应脚本所需参数，再要求补齐后执行
- 若与 **清库** 在同一任务中：须先按「清库 → 导配置 / 部署 的标准流程」在历史中确认清库 **已成功完成**，再执行本命令；不得紧接在清库触发之后执行

## 命令 2：查询部署信息（kadmin）

- 关键词：查询、查找、版本、tag、所有服务器、状态
- 作用：按 tag/服务器查询当前部署信息
- 脚本：`.claude/skills/x2-kadmin/scripts/find.py`
- 强规则：必须限制环境，仅允许 `dev` 或 `beta`，参数必须全

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/find.py -e <env> -q <query>
```

参数要求：

- `-e/--env` 必填，仅允许 `dev` 或 `beta`
- `-q/--query` 必填，分支名或 tag 名或服务器 ID（可用逗号分隔）
- 若缺少或多出参数，先提示该关键词对应脚本所需参数，再要求补齐后执行
- 只有用户明确要求"查询全部服务器"时才允许使用 `--all`

输出要求：

- 解析脚本输出，整理为表格后再回复
- 表头固定为：`服务器名称`、`部署 tag`、`状态（Down/Run）`
- 若按服务器 ID 查询未返回任何数据，也必须输出表格，并将该服务器标记为 `Down`（部署 tag 留空或写 `未知`）

## 命令 3：构建镜像（kadmin）

- 关键词：构建、镜像、build
- 作用：触发 kadmin 的镜像构建工作流
- 脚本：`.claude/skills/x2-kadmin/scripts/build.py`
- 强规则：只允许一个参数（二选一：分支名或 tag 名），不允许附加其他参数

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/build.py --branch_name <branch>
```

或

```
python3 .claude/skills/x2-kadmin/scripts/build.py --tag_name <tag>
```

参数要求：

- `--branch_name` 或 `--tag_name` 必填（二选一）
- 不允许同时传 `--branch_name` 与 `--tag_name`
- 若缺少或多出参数，先提示该关键词对应脚本所需参数，再要求补齐后执行

## 命令 4：工作流执行（kadmin）

- 作用：按关键词触发对应 kadmin 工作流
- 脚本：`.claude/skills/x2-kadmin/scripts/workflow_execute.py`
- 强规则：必须提供 `server_id` 和 `env` 两个参数
- 强规则：keyword 由 AI 识别，使用英文参数
- 说明：工作流执行共三类关键词，当前支持 **清库**（clear_db）、**导配置热更**（hot_reload_config）与 **导配置重启**（restart_with_config）
- 导配置重启就已经包含了部署，用户如果同时提到这两个，那么和用户说明：导配置重启就包含部署，并只执行导配置重启
- 若本次任务还包含清库：必须先按上文 **「清库 → 导配置 / 部署 的标准流程」** 等待清库在历史中成功完成后，再执行热更/重启/部署类命令

### 4.1 清库

- 中文说明：清库
- keyword 固定为 `clear_db`，并明确告知"这里只做清库操作"

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_execute.py --keyword clear_db --server_id <server_id> --env <env>
```

参数要求：

- `--keyword` 固定为 `clear_db`
- `--server_id` 必填，服务器 ID
- `--env` 必填，仅允许 `dev` 或 `beta`
- 若缺少或多出参数，先提示该关键词对应脚本所需参数，再要求补齐后执行
- 若用户同一任务中还需要导配置或部署：触发清库后 **不得立即** 触发 `hot_reload_config` / `restart_with_config` / `deploy.py`，须先完成「清库 → 导配置 / 部署 的标准流程」第 2 步

### 4.2 导配置热更

- 中文说明：导配置热更
- keyword 固定为 `hot_reload_config`，不允许其他关键词

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_execute.py --keyword hot_reload_config --server_id <server_id> --env <env> --config_branch <config_branch>
```

参数要求：

- `--keyword` 固定为 `hot_reload_config`
- `--server_id` 必填，服务器 ID
- `--env` 必填，仅允许 `dev` 或 `beta`
- `--config_branch` 必填（配置分支）
- 若缺少或多出参数，先提示该关键词对应脚本所需参数，再要求补齐后执行
- 若本任务中已触发清库：须先完成「清库 → 导配置 / 部署 的标准流程」第 2 步（历史中清库成功），再执行本命令

### 4.3 导配置重启

- 中文说明：导配置重启
- keyword 固定为 `restart_with_config`，不允许其他关键词

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_execute.py --keyword restart_with_config --server_id <server_id> --env <env> --src_type <branch|tag> --src_target <branch_or_tag> --config_branch <config_branch>
```

参数要求：

- `--keyword` 固定为 `restart_with_config`
- `--server_id` 必填，服务器 ID
- `--env` 必填，仅允许 `dev` 或 `beta`
- `--src_type` 与 `--src_target` 必填（代码分支）
- `--config_branch` 必填（配置分支）
- 代码分支识别：以 `v` 开头判定为 tag，否则判定为分支
- 若缺少或多出参数，先提示该关键词对应脚本所需参数，再要求补齐后执行
- 若本任务中已触发清库：须先完成「清库 → 导配置 / 部署 的标准流程」第 2 步（历史中清库成功），再执行本命令

## 命令 5：工作流查询（kadmin）

- 关键词：查询工作流、工作流列表、工作流历史、构建历史、镜像构建好没、执行记录、看看
- 作用：查询工作流列表或执行历史状态
- 脚本：`.claude/skills/x2-kadmin/scripts/workflow_select.py`
- 强规则：**所有命令执行完后必须将结果解析为表格输出**

### 5.1 查询全部工作流

- 关键词：查询所有工作流、全部工作流、工作流列表
- 固定参数：`-m all`，不需要环境和服务器参数
  强规则：输出的所有内容都要进行格式化

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -m all
```

输出要求：

- 必须解析 JSON 结果并输出为表格
- 表头：`工作流名称`、`状态`、`最后更新时间`
- 若返回数据为空，输出提示"暂无工作流"

### 5.2 查询构建工作流

- 关键词：构建、镜像、build、构建好没、镜像构建历史、最新、当前
- 固定参数：`-m build`，**不需要环境参数（构建只在 dev）**
- 用户提到"历史"时，自动添加 `-t history`

#### 查询构建工作流列表

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -m build
```

#### 查询构建工作流历史

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -m build -t history
```

输出要求：

- 必须解析 JSON 结果并输出为表格
- list 模式表头：`工作流名称`、`状态`
- history 模式表头：`执行时间`、`状态`、`执行结果`、`耗时`

### 5.3 查询导配置相关工作流

- 关键词：清库、导配置、热更、重启、配置历史
- 必需参数：`-e <env>`（环境）、`-s <server_id>`（服务器ID）
- 用户提到"历史"时，自动添加 `-t history`
- 操作类型识别：
  - 清库 → `-o clear_db`
  - 热更/导配置热更 → `-o hot_reload`
  - 重启/导配置重启 → `-o restart`

#### 查询清库工作流

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e <env> -m config -s <server_id> -o clear_db
```

#### 查询清库执行历史（等待清库完成）

与上文 **「清库 → 导配置 / 部署 的标准流程」** 配套：必须在清库触发后使用 **历史** 查询，根据 **最新一条** 记录判断是否已成功完成，再执行导配置或部署。

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e <env> -m config -s <server_id> -o clear_db -t history
```

#### 查询导配置热更工作流历史

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e <env> -m config -s <server_id> -o hot_reload -t history
```

#### 查询导配置重启工作流

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e <env> -m config -s <server_id> -o restart
```

参数要求：

- `-e/--env` 必填，仅允许 `dev` 或 `beta`
- `-s/--server_id` 必填，服务器 ID
- `-o/--operation` 必填，仅允许 `clear_db`、`hot_reload`、`restart`
- `-t/--type` 可选，默认 `list`，用户提到"历史"时传 `history`

### 5.4 查询部署工作流

- 关键词：部署、重启、部署历史、最新部署、看看
- 必需参数：`-e <env>`（环境）、`-s <server_id>`（服务器ID）
- 这玩意没有历史

### 5.5 查看所有部署

- 使用这个命令的时候


#### 查询部署工作流列表

命令模板：

```
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e <env> -m deploy -s <server_id>
```


参数要求：

- `-e/--env` 必填，仅允许 `dev` 或 `beta`
- `-s/--server_id` 必填，服务器 ID
- `-t/--type` 可选，默认 `list`，用户提到"历史"时传 `history`

### 5.5 参数识别规则

**强规则：AI 必须自动识别以下内容，用户无需明确指定**

1. **查询类型识别**：
   - 用户提到"历史"、"执行记录"、"执行历史" → 自动添加 `-t history`
   - 否则默认为 `list` 模式

2. **模块类型识别**：
   - 提到"所有"、"全部"、"列表" → `-m all`
   - 提到"构建"、"镜像"、"build" → `-m build`
   - 提到"清库"、"热更"、"导配置"、"重启" → `-m config`
   - 提到"部署" → `-m deploy`

3. **操作类型识别**（仅 config 模块）：
   - 提到"清库" → `-o clear_db`
   - 提到"热更"、"导配置热更" → `-o hot_reload`
   - 提到"重启"、"导配置重启" → `-o restart`

4. **环境参数规则**：
   - **构建查询（`-m build`）**：不需要环境参数（构建固定在 dev）
   - **全部工作流（`-m all`）**：不需要环境和服务器参数
   - **其他所有查询**：必须提供 `-e` 环境参数

5. **分页参数**：
   - 用户未提及页码和每页数量时，不传 `-p` 和 `-l` 参数（使用默认值）

### 5.6 输出格式要求

**强规则：所有查询结果必须解析为表格格式**

#### list 模式表格格式

| 工作流名称     | 状态   | 最后更新时间        |
| -------------- | ------ | ------------------- |
| x2gs_构建_game | 运行中 | 2024-01-01 10:00:00 |
| x2gs_1001_清库 | 已完成 | 2024-01-01 09:30:00 |

#### history 模式表格格式

| 执行时间            | 工作流名称     | 状态 | 执行结果 | 耗时  |
| ------------------- | -------------- | ---- | -------- | ----- |
| 2024-01-01 10:00:00 | x2gs_构建_game | 成功 | 构建完成 | 5m30s |
| 2024-01-01 09:30:00 | x2gs_构建_game | 失败 | 编译错误 | 2m15s |

### 5.7 用户交互示例

**示例 1：查询构建历史**

用户："镜像构建好没？"

AI 识别：
- 关键词：构建、镜像 → `-m build`
- 隐含历史查询 → `-t history`
- 不需要环境参数

执行命令：
```bash
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -m build -t history
```

输出表格展示最近的构建历史记录。

**示例 2：查询服务器清库历史**

用户："查看 dev 环境 1001 服的清库历史"

AI 识别：
- 关键词：清库 → `-m config -o clear_db`
- 环境：dev → `-e dev`
- 服务器：1001 → `-s 1001`
- 历史 → `-t history`

执行命令：
```bash
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e dev -m config -s 1001 -o clear_db -t history
```

输出表格展示该服务器的清库历史。

**示例 3：查询所有工作流**

用户："查询所有工作流"

AI 识别：
- 关键词：所有工作流 → `-m all`
- 不需要其他参数

执行命令：
```bash
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -m all
```

输出表格展示所有工作流列表。

**示例 4：查询部署工作流**

用户："beta 环境 1002 服的部署情况"

AI 识别：
- 关键词：部署 → `-m deploy`
- 环境：beta → `-e beta`
- 服务器：1002 → `-s 1002`
- 默认 list 模式

执行命令：
```bash
python3 .claude/skills/x2-kadmin/scripts/workflow_select.py -e beta -m deploy -s 1002
```

输出表格展示该服务器的部署工作流状态。
