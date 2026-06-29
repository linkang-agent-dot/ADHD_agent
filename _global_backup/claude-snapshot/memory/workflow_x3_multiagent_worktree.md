---
name: workflow_x3_multiagent_worktree
description: "多个 agent 同机并发改 X3 配置=git worktree(每 agent 一个),取代手搓备份文件夹;含 post-checkout 钩子锁目录的坑"
metadata: 
  node_type: memory
  type: project
  originSessionId: b4b6bd26-69a0-497e-8409-e17563f53067
---

# X3 多 agent 并发改配置 = git worktree（取代备份文件夹）

**原理图解 HTML（讲解/培训用）**：`C:\ADHD_agent\KB\方法论\多Agent配置并行_worktree工作流_原理.html`（7板块:撞车问题→worktree原理→何时开→hook兜底→合并SOP→4坑→实战验证）。

**自动决策闸门在 `x3-config-export` SKILL.md「步骤0」**（不在本文）：开工先 `git status -sb`，工作区干净且无 `[ahead N]`=没人占→主目录直接干；有未提交改动或 `[ahead N]`=别人在改没收尾→开 worktree。本文只讲 worktree 怎么开/坑/prompt 模板。

**强制兜底闸门（PreToolUse hook，2026-06-24 加）**：全局 `settings.json` 注册了 `PreToolUse`(matcher `Edit|Write|MultiEdit|Bash`)→ `python C:/Users/linkang/.claude/scripts/x3_config_isolation_gate.py`。逻辑：碰主仓配置表那一刻（Edit/Write 主仓 `.tsv/.xlsx`，或 Bash 跑 `tsv_edit.py` 没 `--repo` 指向 worktree）→ 查主仓 `git status`：脏或 `[ahead N]` = 别人占着 → **exit 2 拦下**，提示开 worktree；干净 → 放行并在 `C:\Users\linkang\.claude\.x3_gate\<session_id>.ok` 落标记，本会话之后不再触发（避免自己改脏后误拦）。改 worktree 里的/跑别的命令一律放行；hook 出错一律放行(fail-open)。
- **被拦后两条出路**：① 开 worktree（带 `--repo`）；② 确认改动是自己的、要继续主仓干 → `New-Item -ItemType File "<那个.ok路径>" -Force` 后重试。
- 测试用 `X3_GATE_REPO` 环境变量可覆盖主仓路径（脚本顶部读）。
- 编码坑：脚本走 `sys.stdin/stderr.buffer` 二进制读写 UTF-8，不用 reconfigure（hook 管道下 reconfigure 不可靠，会让中文提示变 GBK 乱码喂给模型）。
- 代价：每次 Edit/Write/Bash 都 spawn 一个 python（~100ms），非 X3 调用秒放行。嫌慢可在 settings.json 删掉这条 PreToolUse，决策仍留在 skill 步骤0。

**⚠️ 闸门两个盲区（2026-06-29 实证：并发改配置却没触发 worktree 流程的根因）**：这次我直接用 `python -c "open('tsv/...','w')"` 改主仓 tsv，闸门**完全没拦、没落 .ok 标记**，事后查出两个洞：
1. **Bash 检测只认 `tsv_edit.py`**（`x3_config_isolation_gate.py` line 66 `if "tsv_edit.py" in cmd`）。**裸 `python -c open()` / `sed` / `>` 重定向写主仓 .tsv 一律识别不到** → `hits_main_config=False` 直接放行，连主仓 status 都不查。**=改配置不走 tsv_edit.py 就绕过了闸门**。Edit/Write 工具改 .tsv/.xlsx 能拦（line 58-62），但我没用 Edit、用的 Bash 裸脚本。
2. **"有没有别人占"只看主仓 dirty/ahead，不查 `git worktree list`**（line 84-99 只 `git -C 主仓 status`）。**别的 agent 若正经隔离在自己 worktree（如 `gdconfig-bugfix-island`/`feature/bugfix-island`），主仓工作树是干净的** → 闸门判"没人占→主目录直接干"=假阴性。我撞到的 index.lock/莫名残留行是**共享 .git** 被对方 worktree 的 git 操作并发锁/写引起，不是共享工作树。
- **+ 我自己也漏**：这次没调 `x3-config-export` skill（手搓 tsv），skill 步骤0 那道主闸门压根没跑。**教训：手改 X3 主仓配置前，自己先 `git worktree list`（不止 `git status`）——有 `gdconfig-*` 其它 worktree 在 = 有人在改，主动开自己的 worktree。**
- **✅ 两盲区已加固（2026-06-29，`x3_config_isolation_gate.py` 改完+6 用例验证过）**：
  1. **裸脚本写主仓**：Bash 分支新增 `bash_writes_main_config(cmd)`——命中主仓路径(正则 `x3[\\/]+gdconfig(?![-\w])`，`(?![-\w])` 排除 worktree gdconfig-xxx) + 有 `.tsv/.xlsx` 字面 + 写指纹(重定向到.tsv/.xlsx、`sed -i ...tsv`、`open(...,'w'/'a')`、`.writerows/.to_csv` 等) → 判为改主仓。读/grep/cp备份**不**误判。
  2. **worktree-aware**：主仓 status 干净时再跑 `git worktree list --porcelain`，除主仓外**还有别的 worktree → 也拦**(提示开自己的/或废弃就 override+清)。
  - override 出路不变：`New-Item -ItemType File "<.x3_gate\<session>.ok>" -Force`。fail-open 不变。原备份在本会话 scratchpad `x3_config_isolation_gate.py.bak`。

**问题**：多个 agent 在同一台机器、同一个 `C:\x3\gdconfig\` 仓干活，普通 git 一个目录只能停一个分支，A 切分支会换掉 B 的文件 → 冲突 / 混乱。以前的土办法是各自备份到文件夹手动合，靠人记 → 会忘合并。

**正解**：git worktree —— 同一个仓拆多个独立工作目录，各挂自己分支，共享同一个 `.git`（不重复 clone、不占多份磁盘），改动互不可见。验证过隔离有效（A 目录的改动 B 和主目录都看不到）。

**实操配方**：
```bash
cd /c/x3/gdconfig
git worktree add ../gdconfig-agentA -b feature/agentA dev_festival   # 从 dev_festival 拉
git worktree add ../gdconfig-agentB -b feature/agentB dev_festival
# 各 agent 在自己目录改 tsv→commit→push→发 MR 合回 dev_festival
git worktree list            # 一查就知道谁还没收尾（取代"忘记合并"的人脑记忆）
git worktree remove ../gdconfig-agentA --force && git branch -D feature/agentA
```

**⚠️ 成败关键（X3 专属）**：`x3-config-export` 的 `tsv_edit.py` **默认 repo 写死 `C:\x3\gdconfig`（主目录）**，但支持 `--repo` 覆盖。所以多窗口/多 agent 时**光开 worktree 不够**——prompt 必须明确要求：① `tsv_edit.py` 一律带 `--repo <worktree路径>`；② commit/push 都 `cd` 到该 worktree 做；③ 绝不碰主目录。漏了这步它会按 skill 默认值静默写回主目录，worktree 白开。

**更省事**：Claude Code 的 Agent 工具自带 `isolation: "worktree"` 参数，派子 agent 时加上，harness 自动开临时 worktree、干完无改动自动清。

**⚠️ 坑（实测）**：X3 gdconfig 有 `post-checkout` 钩子，每次 `worktree add` 都会在新目录后台跑 `ExportTable.py` 从 tsv 重建 xlsx 视图（~2分钟，不进 git），期间**锁住该 worktree 目录**。所以**刚建完马上 `worktree remove` 会报 `Permission denied` / `Device or resource busy`**。
- 真实干活不受影响（活儿都干超过 2 分钟）。
- 只有"建完立刻拆"（如演示）才撞上。解法：等对应 `ExportTable.py` 进程退出再删 —— `Get-Process -Id <pid>; $p.WaitForExit()` 后 `Remove-Item -Recurse -Force`，再 `git worktree prune` + `git branch -D`。

**开窗 prompt 模板**（多 Claude Code 窗口并发，每窗一份，改占位符）：
```
你接下来改 X3「<功能名>」配置。这台机器同时有别的窗口在改别的，为避免冲突先隔离到独立 worktree，全程只在这里改：
1. 建并进 worktree：cd /c/x3/gdconfig && git worktree add ../gdconfig-<短名> -b feature/<短名> dev_festival（已存在就直接用别重建）
2. 铁律——不碰主目录 C:\x3\gdconfig：① tsv_edit.py 每条都带 --repo C:\x3\gdconfig-<短名>；② git add/commit/push 都先 cd 该 worktree，分支 feature/<短名>；③ 提交前 git branch --show-current 确认。
3. 任务：<具体改什么>
改完 push 发 MR 合回 dev_festival，告诉我合完了再拆 worktree。
```
用时注意：① 两窗隔几秒开，别同秒 `worktree add`（共享 .git 会撞 `.git/worktrees` 锁）；② 第2条"带 --repo"铁律不能删（删了静默写回主目录）。

## 改完合并回 dev_festival（本地直合，不走 MR）

dev_festival 是工作分支（不受保护）、gdconfig 仓本身也不受保护 → **本地 merge + 直接 push 即可，不开 MR**（MR 只为进受保护的 `dev`，[[workflow_x3_protected_branch_mr]]）。

**方向铁律：把 dev_festival 合进 feature（在 worktree 里解冲突），再让 dev_festival ff 上来。** 冲突解决全程在 worktree（隔离、hook 放行），dev_festival 只做干净 ff，不在主仓产生冲突编辑——这是多 worktree 下最稳的方向。

**步骤**：
0. **前置（一次性，全 worktree 通用）**：merge driver 注册在 `.git/config`、**不随 clone**，但 worktree 共享同一 .git 所以注册一次即可。查 `git -C C:\x3\gdconfig config --get merge.tsv3way.driver` 为空 → `cd C:\x3\gdconfig && python scripts/install_hooks.py`。**没注册就 merge = 退化：tsv 炸 `<<<<` 标记 + xlsx 二进制选边静默丢改动（头号坑，见审计 KB §⑥①）**。
1. **串行化（关键判断）**：同一时刻只许一个 agent 往 dev_festival 整合——整合=改共享分支=临界区。开整合前确认没别的 worktree 正在推 dev_festival。
2. **worktree 内合 dev_festival 进 feature**：`cd <worktree>` → `git fetch origin dev_festival` → `git merge --no-commit --no-ff origin/dev_festival`，按 [[workflow_x3_merge_conflict_audit]] 全套解冲突（driver cell-union；撞 ID 先验业务键别看 seq；含公式表禁 openpyxl）。
3. **验收四连（push 前必全过，都在 worktree 跑）**：① `python scripts/sync_xlsx_tsv.py --check` mismatch=0 → ② `python ~/.claude/skills/x3-config-export/scripts/merge_tsv_audit.py` 双向 lost 行=0 → ③ `cd Tools/table_exporter && python ExportTable.py` **exit 0**（前三过≠能导表，这才是硬门，[[workflow_x3_merge_conflict_audit]] §⑧）→ ④ commit（中文 msg 用 `-F` UTF8 文件 + X3NEW- 前缀）。
4. **整合并推（临界区内尽量快）**：`cd C:\x3\gdconfig` → `git fetch origin dev_festival && git merge --ff-only origin/dev_festival`（本地同步到远端）→ `git merge --ff-only feature/<短名>`（feature 已含 dev_festival → 干净 ff）→ `git push origin dev_festival` → `python ~/.claude/skills/x3-config-export/scripts/jolt_verify.py dev_festival skip_check=true`。**ff-only 失败 = 整合期间 dev_festival 被别人推进了 → 回步骤2 重合再来**（串行没守住时的兜底）。
5. **收尾**：`git worktree remove ../gdconfig-<短名> --force && git branch -D feature/<短名>`。

**⚠️ 审计"合回没合回"看 `origin/dev_festival`，不要看本地（2026-06-24 实测踩坑）**：这套流程是 push 到远端、别的窗口的本地 dev_festival 不会自动 pull，所以**本地 dev_festival 常滞后 origin**。用 `git merge-base --is-ancestor <commitOrBranch> dev_festival`（本地）判会误报"未并入/工作丢失"——必须查 `origin/dev_festival`，或 `git branch -a --contains <sha>` 看是否命中 `remotes/origin/dev_festival`。监听脚本同理：判合回用 `origin/dev_festival` 或"worktree 目录消失"，别用本地分支。bpfix-monopoly-bp 首个完整成功案例就靠这个才核对清楚（本地落后 2 条，差点误判丢活）。

## 推广到 x3-project（客户端/代码/资源）——同隔离概念，合并回与成本反着来

x3-project（`C:\x3-project\`，代码+资源，**dev 受保护**）。worktree 隔离概念照样适用（多窗口改代码/资源同样撞共享 checkout、切分支互掀工作区），但**合并回和成本跟 gdconfig 相反，照搬必翻车**：

**① 合并回看目标分支，MR 不是必须。**（权限实测：linkang=项目2859 **Developer(30)**；Developer 对非保护分支全权、对保护 dev 只能开 MR 不能点合并。）
- **合进 `dev_festival`（非保护工作分支，日常）**：跟 gdconfig 一样**自助、不用 MR**——push feature → 在 dev_festival 整合 → push dev_festival，不用等任何人。
- **`dev_festival` → `dev`（受保护，发版）**：才需要 MR，且 Developer **只能开单、Maintainer 才能合**（"你开单大哥合"）。GitLab API 建 MR 时 **title/desc 纯 ASCII 否则 500**。
- **不论目标，x3-project 跨分叉的二进制 merge 都是雷区**（ProtoGen `.bytes` 冲突 + LFS pointer + `git clean` 误删合法 Unity 目录，见 [[reference_x3_project_repo]] 末节）：本地只做干净 ff，**跨分叉合并交给远端/MR/大哥**，别本地硬合。

**② worktree 成本高（与 gdconfig 相反）。** client 多 GB + 58GB LFS，建一个 worktree=再铺一份完整工作树（磁盘+checkout+LFS smudge，`du client` 直接超时）。所以：x3-project 的 worktree **要长寿、按 feature 用，别随建随拆**；只改代码（server/*.cs）不碰资源时用 **sparse worktree**（`git worktree add --no-checkout ../x3p-<名> -b feature/<名> dev` → `cd` 进去 `git sparse-checkout set server/` → `git checkout`）只铺需要的子树，省几 GB；注意磁盘别铺满。

**③ 内嵌 gdconfig + 子模块。** gdconfig 不是标准 submodule（`.gitmodules` 无映射），靠仓 hook 在 pull/merge 时自动 ff，新 worktree 不一定自动 populate；但本地服 config 读 `client/.../ProtoGen/*.bytes`（在主工作树内随 checkout 走）不读内嵌 gdconfig → 纯代码/资源 worktree 通常不受影响。

**④ 提交规则不变**：X3NEW-/X3- 前缀；提交前内嵌 gdconfig 子模块必须干净（脏则 stash）；大文件先 `git lfs push`；MR title/desc 纯 ASCII。

**两仓对照速查**：
| | gdconfig（配置） | x3-project（代码/资源） |
|---|---|---|
| dev 保护 | 否，可直推 | 是，必 MR |
| worktree 成本 | 极低(~2080文件) | 高(多GB+LFS) |
| worktree 用法 | 随建随拆 | 长寿/按feature/sparse |
| 合并回 | 本地 merge+ff+push dev_festival | push feature + MR；本地禁跨分叉 merge |
| 串行化 | 本地整合需排队 | MR 服务端天然排队 |

**隔离 hook 现状**：`x3_config_isolation_gate.py` 只管 gdconfig 主仓。x3-project 的等价规则=「**别在受保护 dev 上直接改，先开 feature 分支/worktree**」，语义不同（这里没有"干净就在主仓干"），需要时另做一道（暂未建）。

关联：[[reference_x3_gdconfig_repo]] [[reference_x3_project_repo]] [[workflow_x3_protected_branch_mr]] [[feedback_x3_branch_strategy]] [[workflow_x3_merge_conflict_audit]]
