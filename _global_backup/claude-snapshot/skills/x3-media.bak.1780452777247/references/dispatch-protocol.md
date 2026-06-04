# dispatch-protocol：x3-media 异步任务协议（主/子 agent 单一事实来源）

> 主 agent 与 `media-worker` 子 agent 都按本文档协作。schema 改动必须同步更新本文件。

---

## 1. 状态机

```
       派发                   开始执行
pending ────► (worker 接管) ────► running
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
            success              failed              needs_auth
         （成功落盘）          （重试 1 次仍失败）   （Cookie 过期，专用终态）
```

- 主 agent 仅写入 `pending`
- worker 在 Step 2 改 `running`，在 Step 5 改终态（success/failed/needs_auth）
- `pending → success` 跳过 `running` 视为协议违反（worker 必须先标 running）

---

## 2. task json schema

文件路径：`state/tasks/<task_id>.json`

`<task_id>` 格式：`yyyyMMdd-HHmmss-<4字符随机十六进制>`，例：`20260509-143022-a7f3`

完整 schema：

```json
{
  "schema_version": 1,
  "task_id": "20260509-143022-a7f3",
  "status": "pending | running | success | failed | needs_auth",
  "type": "skill_icon | card_gallery | march_emoji | dynamic_march_emoji | achievement_badge | game_video | ui_extract | activity_icon | effect_texture | general",
  "user_prompt": "用户原话或主 agent 整理后的语义化描述",
  "params": {
    "model": "gpt | gemini | nano-banana | flux | vidu | ...",
    "reference_images": ["<本地路径或 URL>"],
    "output_dir": "<绝对路径，必填>",
    "output_filename": "<可选，工作流自定>",
    "postprocess": "<type 专属后处理标识，如 skill_icon_256_edge | ui_extract_individual | none>",

    "<其他 type 专属字段>": "..."
  },
  "started_at": null,
  "finished_at": null,
  "result": {
    "saved_to": [],
    "history_lines_appended": 0,
    "backend": null
  },
  "error": null,
  "retry_count": 0,
  "created_by": "main-agent"
}
```

### 字段说明

| 字段 | 写入方 | 必填 | 说明 |
|---|---|---|---|
| `schema_version` | main | ✅ | 当前固定 `1`，未来兼容性保留 |
| `task_id` | main | ✅ | 派发时生成，全局唯一 |
| `status` | main + worker | ✅ | 主只写 pending；worker 写其他 |
| `type` | main | ✅ | Type Router 中的 type key |
| `user_prompt` | main | ✅ | 用户原话或精炼后描述（中英文皆可） |
| `params` | main | ✅ | 完整执行参数；worker 仅按这里的字段执行 |
| `params.output_dir` | main | ✅ | 必须是绝对路径，默认 `%USERPROFILE%\Downloads` |
| `params.reference_images` | main | 视情况 | 涉及 X3 角色时**必填**（已在 Skill 通用工作流强制） |
| `started_at` | worker | — | ISO8601 含时区，worker Step 2 写 |
| `finished_at` | worker | — | ISO8601 含时区，worker Step 5 写 |
| `result.saved_to` | worker | 成功必填 | 完整本地路径列表 |
| `result.history_lines_appended` | worker | 成功必填 | 写入 history.jsonl 的行数 |
| `result.backend` | worker | 成功必填 | `grfal` 或 `art-skills` |
| `error.message` | worker | 失败必填 | 简短错误说明 |
| `error.step` | worker | 失败必填 | `auth` / `generate` / `download` / `postprocess` / `history` |
| `retry_count` | worker | — | API 调用累计重试次数（0 或 1） |
| `created_by` | main | — | 固定 `"main-agent"`；将来支持 `--resume <id>` 时改 `"resume"` |

---

## 3. 主 agent 派发模板（伪代码）

```python
import json, datetime, secrets, pathlib

def dispatch_task(type_key: str, user_prompt: str, params: dict) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    rand4 = secrets.token_hex(2)
    task_id = f"{ts}-{rand4}"

    task = {
        "schema_version": 1,
        "task_id": task_id,
        "status": "pending",
        "type": type_key,
        "user_prompt": user_prompt,
        "params": params,
        "started_at": None,
        "finished_at": None,
        "result": {"saved_to": [], "history_lines_appended": 0, "backend": None},
        "error": None,
        "retry_count": 0,
        "created_by": "main-agent",
    }

    # state/tasks 是 skill 内的相对路径，主 agent 按 skill 根目录拼出实际位置
    path = pathlib.Path(SKILL_ROOT) / "state" / "tasks" / f"{task_id}.json"
    path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")

    # 主 agent 调用 Agent 工具：
    # Agent(
    #     subagent_type="media-worker",                # 通用 worker，由 SKILL_ROOT 区分 skill
    #     run_in_background=True,
    #     prompt=f"TASK_ID={task_id}\nSKILL_ROOT=C:\\Users\\caoxinying\\.claude\\skills\\x3-media",
    #     description=f"x3-media {type_key} {task_id}",
    # )

    return task_id
```

主 agent 必须在派发后立即在对话里告知用户：

```
已派发 N 个任务：
- a7f3  skill_icon  铁匠/火焰锤击
- b1c2  skill_icon  铁匠/旋风斩
完成后通知。继续提需求？
```

---

## 4. worker 接收输入

主 agent 调用 Agent 工具时，prompt 必须传**两行**：

```
TASK_ID=<task_id>
SKILL_ROOT=<absolute skill root path>
```

例：

```
TASK_ID=20260509-143022-a7f3
SKILL_ROOT=C:\Users\caoxinying\.claude\skills\x3-media
```

- `TASK_ID` 用于在 `<SKILL_ROOT>/state/tasks/<TASK_ID>.json` 定位本次任务
- `SKILL_ROOT` 让通用 `media-worker` 知道当前任务隶属哪个 skill（x2-media / x3-media / …），所有 SKILL.md、references、scripts、state、history 路径都从这里拼出

worker 的所有上下文都从 task json + skill 文件读取，主 agent **不要**在 prompt 里塞其他参数副本（信息冗余且容易不一致）。

---

## 5. task-notification 触达后主 agent 必做项

1. 读 `state/tasks/<task_id>.json`
2. 按 `status` 播报：
   - `success`：`✅ 任务 <id> 完成（<type>）。已保存：<saved_to[0]>` (多文件列前 3 个)
   - `failed`：`❌ 任务 <id> 失败（<error.step>）：<error.message>。重试 / 改参数 / 跳过？`
   - `needs_auth`：`⚠️ 任务 <id> Cookie 过期。请运行 scripts/get_grfal_cookie.py 刷新；完成后告诉我"Cookie 已刷新"，我会自动重派该任务。`
3. **不要**重新读 SKILL.md 或 type-*.md 来"二次校验"——worker 已写好结果
4. **不要**回头主动调 call_grfal 修复——按上面的选项让用户决定

---

## 6. 重派（resume）协议

用户刷新 Cookie 后说"Cookie 已刷新，重派 a7f3"：

1. 主 agent 读 `state/tasks/a7f3.json`，确认 `status == needs_auth`
2. 主 agent 改写：
   - `status = "pending"`
   - `started_at = null`
   - `finished_at = null`
   - `error = null`
   - `retry_count = 0`
   - `created_by = "resume"`
3. 主 agent 派一个新 worker（同一个 task_id）：
   ```
   Agent(subagent_type="media-worker", run_in_background=True, prompt="TASK_ID=a7f3\nSKILL_ROOT=C:\\Users\\caoxinying\\.claude\\skills\\x3-media")
   ```

不要新生成 task_id——这样能在历史里看到"原任务 + 重派"的连续性。

---

## 7. 历史归档

- 完成（success/failed/needs_auth）的 task json 在 `state/tasks/` 保留 7 天
- 超过 7 天的归档到 `state/archive/<yyyy-MM>/<task_id>.json`（P1，可手动）
- `state/history.jsonl` 永久保留，由各 worker 在成功后追加

---

## 8. 主 agent 进度查询响应模板

用户问"现在有几个任务在跑？" / "活跃任务" / "list tasks"：

```
glob state/tasks/*.json
filter status in (pending, running)
sort by started_at asc
```

输出示例：

```
进行中 2 个：
| task_id              | type        | 描述              | 状态     | 已耗时   |
|----------------------|-------------|-------------------|----------|----------|
| 20260509-143022-a7f3 | skill_icon  | 铁匠/火焰锤击     | running  | 2分15秒  |
| 20260509-143108-b1c2 | game_video  | 战斗演示          | running  | 8分02秒  |
```

近期完成（24 小时内）可加一段 `tail`：

```
近期完成 3 个：
- a1b2 ✅ skill_icon 已保存到 ...
- c3d4 ✅ activity_icon 已保存到 ...
- e5f6 ❌ ui_extract 失败：Cookie 过期
```
