---
name: 配置BUG自动修复流程
description: BUG工作流拆分为巡检Agent(定时cron只读)+修复Agent(按需启动)，避免单session上下文膨胀
type: feedback
originSessionId: 59183ca4-8092-4018-98e1-f8b0db78970d
---
## 架构：双 Agent 拆分（2026-04-16 决定）

**Why:** 之前查BUG+改BUG放同一个 session，上下文越滚越大，一天 $80+ token。拆成两个 agent 后巡检是轻量新会话，修复按需启动。

### Agent A — BUG 巡检（Windows 定时任务，只读）
- **实现**: Windows Task Scheduler `ClaudeBugScan`
- **脚本**: `C:\Users\linkang\.claude\scripts\bug_scan.ps1` → 调用 `claude -p` 非交互模式
- **Prompt**: `C:\Users\linkang\.claude\scripts\bug_scan_prompt.txt`
- **调度**: 工作日 9:23-20:23 每小时（PT1H 重复，PT11H 窗口）
- **限制**: `--max-budget-usd 2`（单次上限 $2）
- **职责**: 查 Jira → 对比上次 → 写 `_my_bugs_summary.txt` → 追加日志到 `_bug_scan_log.txt` → 配置类写 `_bugs_to_fix.txt`
- **禁止**: 不改配置、不写 GSheet、不操作 Jira
- **上下文**: 每次是全新 `claude -p` 进程，零上下文积累

### Agent B — BUG 修复（按需，用户手动触发）
- **触发**: 用户看完巡检报告，说"修 P2DEV-XXXXX"
- **职责**: 读运维文档 → 查配置 → 用户确认 → 修复 → 沉淀
- **上下文**: 只加载单个 BUG 相关信息，修完即关

### 巡检结果文件
- 路径: `C:/Users/linkang/_my_bugs_summary.txt`
- 格式: `KEY [优先级] 标题`，每次覆写

## 触发条件

- 巡检: cron 自动触发（Agent A）
- 修复: 用户说"修BUG"/"改BUG"/"修 XXX"时启动（Agent B）

## 可自动修复的 BUG 类型

1. **ID 引用错误** — 如 2011 的 `actv_id` 指向错误活动
2. **字段值配置错误** — 如数值、条件配置不对
3. **缺失配置行** — 需要新增的配置行
4. **LC key 错误** — 本地化 key 拼写错误

## 执行流程（4步 + 2个用户确认点）

### Step 1: 问题识别
- 从 Jira 获取 BUG 详情（用 Jira API）
- 分析是否为配置类问题
- 输出：BUG 类型判断 + 涉及的表编号

### Step 2: 配置查询 ⚠️ 用户确认点1
- **⚠️ 必须先读配置知识库**：`C:\ADHD_agent\.cursor\config-library\`
  - `table-index.md` — 表编号→页签→SheetID 映射
  - `reskin-rules.md` — 追踪链规则、字段类型处理
- 根据 BUG 描述定位相关配置表
- 用 gws 查询 Google Sheet 数据
- 追踪配置引用链（如 2112 → 2135 → 2011）
- **输出给用户确认**：
  ```
  🔍 查询结果：
  - 问题定位：<具体哪个表哪个字段有问题>
  - 当前值：<错误的配置值>
  - 应该是：<正确的配置值>
  - 查询方式：<用了哪些表、哪些 ID>
  
  请确认查询方式是否正确？
  ```

### Step 3: 修复方案 ⚠️ 用户确认点2
- 确定需要修改的表、行、字段
- **输出给用户确认**：
  ```
  📝 修复方案：
  - 表：<表编号>(<页签>)
  - 行 ID：<具体行 ID>
  - 字段：<字段名>
  - 修改：<旧值> → <新值>
  - 目标分支：<bugfix/dev/etc>
  
  确认后我将执行修改并导表。
  ```

### Step 4: 执行修复
- 用 gws 更新 Google Sheet
- 用 P2-config-upload skill 导表到指定分支
- 输出提交结果
- （可选）通过 Jira API 更新 BUG 状态/添加评论

## 配置查询标准方法

### 追踪链（以礼包触发问题为例）
```
2112 activity_config
 └── A_ARR_activity_components → {"typ":"package","id":xxx}
       ↓
2135 activity_package
 └── A_INT_iap (col[2]) → 2011 ID
       ↓
2011 iap_config
 └── A_MAP_time_info → {"normal":[{"actv_id":应该等于2112活动ID}]}
```

### 常用 SheetID
见 `reference_config_library.md`

## 注意事项

- **不自动执行**：必须等用户确认后才修改
- **不改 1011 i18n**：临时禁令，需用户本机处理
- **记录修改**：每次修复后在 Jira 添加评论说明改了什么

## 典型案例

### 案例1：机甲抽奖礼包触发不出来（2026-04-10）
- **问题**：活动 21127807 的礼包无法触发
- **原因**：2011 表 4 个 IAP 的 `actv_id` 指向了 `21127202`（旧活动）
- **修复**：改为 `21127807`
- **追踪链**：2112(21127807) → 2135(21353246-49) → 2011(2011100482-85)
