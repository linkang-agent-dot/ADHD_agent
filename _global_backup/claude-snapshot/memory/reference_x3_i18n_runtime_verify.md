---
name: reference_x3_i18n_runtime_verify
description: X3 i18n 改动「导表→客户端→运行时」验证固定姿势——不重启 Play 逐语言热重载断言，全程 DebugUtils 桥
metadata: 
  node_type: memory
  type: reference
  originSessionId: b1394e45-ee3b-414f-bc83-acdb02f650bd
---

X3 i18n 文案改动的三层验证固定姿势（2026-07-16 兵种术语统一案实测跑通，L1+L2 各 47 断言全绿）：

**L1 · 导表产物断言（不碰 Unity）**
- 建 detached worktree（别动主仓分支）：`git worktree add C:/X3/gdconfig-dev-l1 origin/dev --detach`，跑 `Tools/table_exporter/ExportTable.py`（cwd 必须是 table_exporter 目录），产物落 `<worktree>/temp_dev/ProtoGen/i18n/*.bytes`。
- bytes 格式 = 简版 protobuf repeated Entry{key=1,value=2}，现成解析/断言/热重载扫描脚本在 `KB\产出-本地化与美术\X3_兵种术语统一验证_20260716\scripts\`（l1_assert.py 产物断言 / l2_runtime.py 运行时扫描 / patch_md5.py md5清单同步 / gen_report_html.py 出图文报告，改期望值表即可复用；该目录同存 任务书+报告md/html+6张截图 全案范本）。
- **语言码映射坑**：文件名 `zh`=繁体(策划口径 tw)、`po`=葡语(pt)。16 语言=cn de en fr id it jp kr pl po ru sp th tr ua zh。
- **头号假阴性**：客户端 `client/Assets/Res/Config/ProtoGen/i18n/*.bytes` 时间戳很新 ≠ 内容是目标分支——主仓可能在别的分支（如 dev_festival）导的。必须对客户端 bytes 也跑一遍断言确认「吃没吃到」。

**喂客户端**：只 copy `i18n/*.bytes` 16 个文件（别整目录覆盖 ProtoGen——可能有别的案子在途改动），并同步 patch `AllTableDataMd5.txt` 里 i18n 16 行（**分隔符坑**：worktree 产物清单用 `\`、客户端清单用 `/`，按文件名归一化匹配）。动手前备份原 16+1 个文件。

**L2 · 运行时全语言扫描（不重启 Play！）**
- `TFW.Localization.LocalizationMgr` 有 Editor-only 静态方法 `Update(lang)`：**强制从磁盘现读** `Assets/Res/Config/ProtoGen/i18n/{lang}.bytes` 并设为当前字典（只换 sCurLangDict 不动 sCurLanguage/不广播 OnLanguageChanged→UI 不闪）。配合 `Get(key)` 即可逐语言断言，扫完 `Update(原语言)` 恢复。
- 全程 DebugUtils 桥 Bash 调（不需要 unity-mcp MCP 注册、不需要在 x3-project 目录起会话）：
  `python C:\x3-project\.claude\skills\DebugUtils\scripts\client.py invoke --type TFW.Localization.LocalizationMgr --member Update --kind call --args kr`
- 查当前语言用私有字段 `eval --code "TFW.Localization.LocalizationMgr.sCurLanguage"`（公有属性 CurLanguage 反射 GetMember 取不到）。
- Console 异常面：`invoke --type UnityEditor.LogEntries --member GetCount` 可拿条目数；FormatException 扫 `%LOCALAPPDATA%\Unity\Editor\Editor.log`。
- 反射桥 **string.Format 多重载解析不动**，别用它验占位符——exact-match 期望值本身就证明 `{0}`/`<color>` 完好。

**L3 · UI 截图（2026-07-16 实测全自动跑通，en/kr/jp×2界面）**：feval 会话（`DebugUtils/scripts/feval_runtime_debug.py start/exec/stop`，`--skip-lint --no-console-fallback`，`--cwd` 必须绝对路径）可以：`new UI.UIHeroInfoData()` 构造数据（**字段赋值是静默 no-op**，用 `typeof(T).GetField("x").SetValue(obj, v)`；SetValue 第一参不能是 null——null 会变 Missing 报 method not found）→ `UI.WndMgr.Show<UI.UIHeroInfo>(d)` / `Show<UI.UIRoute>()` 开窗 → `UI.WndMgr.Get<UI.UIHeroInfo>().SelectSkill(9037)`（feval 可直调私有实例方法）→ ScreenCapture 截图。**整 UI 切语言**用 client.py 属性 set：`invoke --type TFW.Localization.LocalizationMgr --member CurrentLanguage --kind set --args en`（注意属性名是 **CurrentLanguage** 不是 CurLanguage；feval 里属性赋值也是静默 no-op 不能用）。切完 Hide+Show 重开窗才重渲染。测完恢复 zh。
- 坑：英雄技能页第三技能可能是**皮肤技能**（9037 挂皮肤 103405 而非英雄 1034 本体）——GM 加英雄/满级/满星都不出，要 `unlockheroskin`。
- UIRoute（航线先锋）在 beta 330 直接 `Show<UI.UIRoute>()` 能开（无需活动 GM），六路线名直出。

相关：[[reference_x3_unity_mcp]] [[reference_x3_tsv_export_migration]]
