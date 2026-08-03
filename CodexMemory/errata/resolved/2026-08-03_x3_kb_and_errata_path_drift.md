# X3 知识库与错误仓路径漂移导致读取失败

- 日期：2026-08-03
- 任务：查询 X3 礼包内容并更新 dim.iap 主数据表
- 现象：按会话 AGENTS.md 中 `.Codex\projects\...` 路径读取 X3 memory 失败；随后误把错误仓 README 读成 `errata\open\README.md`，再次报路径不存在（本轮续作时又重复了一次，16:xx 再次发生同一组合错误）；收工派 `task-checker` 时又把专用 `agent_type` 与全历史 fork 同时传入，工具拒绝启动；只更新了 GSheet `dim.iap`，未同步修改 X3 配置源，被用户指出后续同步会清理这些结果；检索多语言 TSV 时 PowerShell GBK 控制台输出韩文触发 `UnicodeEncodeError`；更关键的是，在没有明确业务分类标准时自行完成了 67 个礼包的性质分类，用户复核指出马戏和航海都应归“节日礼包”，并要求以后此类判断必须人工 double check；续作时又把问题抽象成两套新口径让用户选择，用户再次纠正：应先参考 `dim.iap` 现有归类；修正 HTML 后尝试用浏览器自动打开本地 `file:///` 页面，被浏览器 URL 安全策略明确拒绝；交付 HTML 仍只放在 `C:\Users\linkang`，未按收工规则归档进 ADHD_agent KB，被用户再次指出；用户最终又裁决沉船相关应归活动-沉船、红包礼包归社交、股契/股权归活动-IPO；同步沉淀时因错误记录已由 `open` 移到 `resolved`，多文件补丁仍引用旧路径而整体失败；随后又误判“分类只在 dim.iap、无需重新导表”，再次忽略主数据知识已明确要求追 `gdconfig → bi_upload → dim.iap` 上游同步链路，被用户当场纠正；重新追链时又对三个大目录做无约束全文检索，25 秒超时且无结果；随后把完整 SKILL 读取与 `jolt_verify.py --help` 合在同一短超时命令中，再次超时，未取得可靠输出；首次本地 `ExportTable.py` 又把进程总超时设为 60 秒，导表尚未结束便被工具终止；配置提交 `e5b94c78` 推到 feature 后，Jenkins 导表 #2422 返回 FAILURE，需先抓控制台根因再向 qa/dev 同步。
- 根因：本机共享项目 memory 的实际真源仍为 `.claude\projects\...`；错误仓规则文件位于 `CodexMemory\errata\README.md`，`open\` 只存待复核记录；专用 agent 类型要求非全历史 fork；执行主数据维护时把 GSheet 当成独立真源，未完整追踪 `gdconfig → bi_upload → dim.iap` 的生成链路，违反“写配置前追至少两层引用链”；文本检索未预先把 Python 输出编码设为 UTF-8；把“内容证据可推断”误当成“业务分类可定稿”，又把 taxonomy 设计当成当前任务，未把 `dim.iap` 现有相邻/同类行作为第一优先级模板。
- 处理：改读实际真源路径；按 `errata\README.md` 格式记录本条；专用验收 agent 改用 `fork_turns=none` 并在 prompt 内提供自包含上下文；后续 Python 检索多语言文本前显式设置 `PYTHONIOENCODING=utf-8`；X3 `dim.*` 主数据修改必须先确认并修改上游配置字段，完整追踪 `gdconfig → bi_upload → dim.iap`，禁止把分类误判为下游独立字段。分类任务先在 `dim.iap` 中按“同玩法/同入口/同 PackType/同内容结构”找已经稳定使用的先例，再以 Pack→Reward→Item 内容作交叉验证；只有现表无先例的边界项才提交业务 owner 判断。写前先产出“ID、现表先例、建议分类、判断依据、疑点”审阅清单，待 double check 后才写 GSheet 或配置；本轮最终按人工裁决完成两轮共 29 项修正。浏览器明确拒绝本地文件 URL 后不绕过策略，改用静态数据校验并把本地 HTML 链接交给用户自行打开。HTML 已补归档到 `KB\产出-配置生成\X3_dim_iap\`，增加 `_目录说明.md` 标 FINAL/工作副本/备份与接管口径，并把入口回写 `reference_x3_dim_iap_master.md`；后续任何正式 HTML 交付先完成“KB 归档 + 唯一入口挂载”再报完成。多文件补丁前先解析错误记录的当前真实位置；错误条目可能已被复核流程从 `open` 移至 `resolved`，不能沿用旧路径。追链检索先按文件名/脚本目录缩小范围，再对候选文件搜字段，禁止从仓库根无约束全文扫。长导表命令设置足够的总超时，并通过短周期 yield/wait 保持进度反馈，不再用 60 秒总超时截断。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 多问题合并条目。路径漂移=.Codex污染已批量修复;业务教训(分类先抄dim.iap现有归类+人工double check)已写入 reference_x3_dim_iap_master.md
- 状态：resolved

---
## 2026-08-03 补充：历史逻辑行对照脚本越界
- 现象：诊断 `TXT_RuleTips_Content_40002` 跨多个历史 ref 的物理行结构时，脚本无条件读取 `lines[j]` 作为下一条 key；遇到 `j == len(lines)` 时触发 `IndexError`，只读诊断中断。
- 根因：历史脏数据可能让逻辑块一直延伸到文件尾，脚本缺少 EOF 边界保护。
- 处理：后续历史 TSV 诊断对 `j < len(lines)` 做显式判断；输出摘要不再假设逻辑块后必有下一行。

## 2026-08-03 补充：`safe_edit_tsv.py` 安装路径假定错误
- 现象：按 `.agents\skills\x3-config-export\scripts\safe_edit_tsv.py` 调用失败，文件不存在。
- 根因：skill 文档位于 `.agents`，但本机 X3 导表执行脚本可能仍安装在 `.Codex\skills` 或共享 skill 真源，不能据 SKILL.md 所在目录假定脚本也已同步。
- 处理：执行前先用 `rg --files` 定位脚本真实路径；未找到则使用 `apply_patch` 做可审计的最小编辑。

## 2026-08-03 补充：`functions.exec` V8 无 `TextDecoder`
- 现象：准备以 base64 安全传递超长 UTF-8 TSV 行并用 `apply_patch` 回插时，组合执行器抛出 `ReferenceError: TextDecoder is not defined`。
- 影响：异常发生在 dry-run/删除/补丁之前，配置文件未发生改动。
- 处理：该运行时用 `atob` + 百分号字节串 + `decodeURIComponent` 解码 UTF-8，不再依赖未暴露的 Web API。

## 2026-08-03 补充：`functions.exec` V8 同样无 `atob`
- 现象：替代解码方案再次抛出 `ReferenceError: atob is not defined`。
- 影响：仍发生在任何文件修改之前。
- 处理：停止在隔离 V8 内做 base64 解码，改由只读 Python 直接输出原始 UTF-8 单行并用明确 marker 提取，再交给 `apply_patch`。

## 2026-08-03 补充：`tsv_delrows.py` 未删除无 key 的 48 条脏物理行
- 现象：工具 dry-run/执行均报告“删 1 逻辑行 / 1 物理行”；它只删除了 `TXT_RuleTips_Content_40002` 首行，后续 48 条旧稿碎片仍在，正确行回插后落在碎片末尾。
- 根因：这些历史碎片多数已经被补齐为 27 列，工具按“完整宽度行”把它们视为独立物理行，而不是目标 key 的多行 cell 延续。
- 处理：不能用 `tsv_delrows.py` 清这种历史畸形块；改以 git diff/相邻 key 为边界精确删除首行与下一合法 key 之间的所有无 key 行，再保留唯一 27 列正确行。

## 2026-08-03 补充：直接运行 `ExportTable.py` 出现 exit0 假绿灯
- 现象：在 worktree 根执行 `python Tools\table_exporter\ExportTable.py` 返回 exit 0，但日志显示 `InputPath: C:\tsv`、`源文件夹不存在，退出`，实际未导表。
- 根因：该入口依赖正确的启动目录或显式参数，不能只看进程退出码。
- 处理：导表验收同时检查日志必须指向当前 worktree 的 `tsv` 且真正执行完；先查仓库包装入口/参数再重跑，禁止把“源目录不存在”的 exit0 当成功。

## 2026-08-03 补充：Text TSV 合法空尾列触发 `git diff --check`
- 现象：规范化后的文本行固定为 27 列，20–27 列为空，因此行尾保留 8 个 tab；`git diff --check` 报 `trailing whitespace` 并返回非零。
- 判定：这是 TSV schema 的合法空尾列，不是可删除的格式噪音；删 tab 会把行降为 19 列。
- 处理：Text TSV 以“27 列断言 + ExportTable 真执行成功”为准；`git diff --check` 的该行尾 tab 告警记录后豁免，其他告警仍需处理。

## 2026-08-03 补充：并行 `jolt_verify` 遇 Jenkins 队列超时
- 现象：qa 与 dev_festival 并行触发时，dev_festival queue item 2550 在 10 分钟内未分配 build 号，脚本以“等待 build 号超时”退出；组合调用也未完整保留 qa 那一路回执。
- 判定：这是 Jenkins 排队/等待超时，不是配置构建 FAILURE，不能重复触发制造更多队列项。
- 处理：先查既有 queue item 与最近 build 的真实状态；后续多分支远端导表串行触发/验证，避免并行挤队列和丢失单路回执。

## 2026-08-03 补充：GitLab API 创建 MR 认证/项目定位失败
- 现象：用 `GITLAB_TAP4FUN_TOKEN` + URL 编码项目路径调用 API，查询返回 `404 Project Not Found`，创建返回 `401 Unauthorized`，结果字段全空。
- 影响：修复分支已成功推送，仅 MR 尚未创建。
- 处理：先检查 token 是否实际注入（只看存在性/长度，不输出值）和仓库现有 GitLab CLI 认证；优先用已认证 `glab mr create`，或解析仓库 numeric project id 后再调 API。
