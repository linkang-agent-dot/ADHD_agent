---
name: reference_x3_worktree_cleanup
description: C:\X3 下 gdconfig 一堆 worktree 哪些能删的三步安全判定法
metadata: 
  node_type: memory
  type: reference
  originSessionId: a547f8e5-b67e-45e6-ac45-392e1175419f
  modified: 2026-07-29T14:39:53.396Z
---

# X3 gdconfig worktree 清理：能否安全删的三步判定

`C:\X3\` 下 `gdconfig` 是主仓（挂 `dev_festival`），其余 `gdconfig-*` 都是 `git worktree`。判「哪些能删」别凭目录名猜，跑 `git worktree list` 后对每个按下面三步过。

**核心前提**：`git worktree remove` 只删工作目录，**不删分支 ref**；`origin/*` 远端分支更不受影响。真正会丢东西的只有两种：① 未提交改动 ② 只活在本地、远端一个分支都没有的提交。

## 🔴 第 0 步（2026-07-29 x3-project 实战补，先于三步判定）：查有没有**未完成的 git 中间态**
三步判定有个致命盲区——**卡在中间态的 worktree，「独有提交」可能正好是 0**（活儿还没 commit，全在 staged 区），按老判据会判成"可删"，一删就毁了别人做到一半的工作。开工先跑：
```bash
G=$(git -C <wt> rev-parse --git-dir)
for f in MERGE_HEAD CHERRY_PICK_HEAD REBASE_HEAD; do [ -f "$G/$f" ] && echo "⚠️ 未完成的 $f"; done
git -C <wt> status --porcelain | grep -E "^(UU|AA|DD|.U|U.)"   # 未解决冲突
```
本次实证：`wt_dev_spec` 相对 origin/dev **独有提交 0 笔**，但 `CHERRY_PICK_HEAD` 在、`tableResInfo.txt` 是 `UU` 冲突、6 个皮肤资源是 `A`(staged)——**正是有人 cherry-pick 做到一半**。老判据会说"可删"，删掉即事故。**`A`/`M `(staged) 状态的文件＝已 add 未 commit 的真实工作，比未跟踪文件更危险**。

## 🪤 判「独有提交」要先确认这个 worktree 跟的是**哪条线**（本次我第一次就判错）
`git log origin/dev_festival..HEAD` 只在该 worktree 确实跟 dev_festival 时才有意义。本次 `wt_dev_spec` 跟的是 **dev**，拿 dev_festival 当基准算出一堆"独有提交"（其实是 dev 线的正常提交），换成 `origin/dev..HEAD` 才是真值 0。**先看 HEAD 提交信息/`git log -1` 判断它属于哪条线，再选基准。**

## 🪤 父仓 `git status` 里的 `??` 目录可能是 worktree，不是垃圾
worktree 目录在**父仓**看是未跟踪（`?? wt_xxx/`），清理本地改动时极易被当垃圾 `rm`。**删前一律先 `git worktree list` 对一遍**；确认要删也必须走 `git worktree remove <路径>`，直接 `rm -rf` 会留下损坏的 worktree 注册项。

## 🪤 执行删除时的三个实操坑（2026-07-29 一次清掉 3 个 worktree 实证）
1. **`git worktree remove --force` 报 `Directory not empty` ≠ 失败**：Windows 上常见（文件被占用/未跟踪残留）。此时**注册项其实已经解除**——判成功与否**看 `git worktree list` 里还在不在，别看命令报错**，否则会误以为没删又去重跑。目录残留补一刀 `rm -rf <路径>` 即可（此时已不是 worktree，安全）。
2. **删残留目录前先分清「仓库跟踪 vs 独有内容」**：`git cat-file -e HEAD:<顶层项>` 逐个验——命中＝仓库有、远端可恢复、随便删；不命中＝独有内容，要看清是不是有价值产物（本次 piggybank 残留 `server`/`skills-lock.json` 是跟踪内容，`x3-docs` 虽独有但是空目录，故全部可删）。
3. **别用 `du -sh` 统计 worktree 体积**：几万文件的目录上会跑穿 2 分钟超时。要判大小用 `find -type f | wc -l` 数文件数，或直接看 `df` 前后差值。

## 🔴 识别「sparse worktree 用完没清干净」的残骸：index 坏掉（2026-07-29 x3-wt-push2 实证）
症状组合：**`git status` 报几万个 `D ` (staged deletion，第一列D)，可工作区文件明明还在**，且连 `.gitattributes`/`.gitignore` 这种仓库必跟踪的文件都被列成 `??` 未跟踪。
- **先排除 sparse**：`git config core.sparseCheckout` + `git sparse-checkout list` 都空 → 不是 sparse 表象，是 **index 真坏了**（git 丢失了工作区文件与 HEAD 的对应关系）。
- 🔴**危险性**：在这种 worktree 里 `git add -A` / `git commit -a` 会把那几万个删除**真的提交上去**。发现即停用。
- **处置**：先跑独有提交检查（本次 0 笔＝内容全在远端）→ **直接删掉重开，别费劲修 index**（修完也不可信，重开一个干净的更省事）。
- **成因**：多为「sparse worktree cherry-pick 推代码」用完只删了文件没 `worktree remove` 留下的。**用完 sparse worktree 当场 `git worktree remove`**，别留到下次。

## 三步判定（全过 = 安全删）

1. **有没有未提交改动** → `git -C <wt> status --porcelain | wc -l`，非 0 就先别删（会丢），除非确认丢弃。
2. **本地独有提交在远端有没有备份** → 关键不是"是否 merged"，而是"内容在不在远端任一分支"：
   - `git log --no-merges origin/dev_festival..<branch>` 看有没有**非 merge 的真实内容提交**；只有 merge 提交 = 零独有内容，删掉零损失。
   - 或对每个内容提交 `git branch -r --contains <hash>`，返回空 = 仅本地 = 真丢。
3. **长期共享分支**（`dev`/`dev_festival`/`qa`/`qa_sync`）的 worktree：内容只要在 `origin/*` 就随时 `git worktree add ../xx <branch>` 重拉，删本地 ref 无损。

## 常见误判（2026-07-16 实操踩到的）

- **"NO-UPSTREAM 未跟踪远端" ≠ 会丢**：deepsea-recharge/turntable 分支没跟远端，但独有的全是 `Merge dev/qa` 提交、零内容，删掉零损失。
- **"ahead 35/482 commits" ≠ 有独有工作**：feature 分支基于 dev 会天然领先 dev_festival 一大截；handbook-v2 领先 411 但已并入 origin/dev。要看的是**非 merge 内容提交在不在远端**，不是 ahead 数字。
- **本地 qa 领先 origin/qa 35 个**：那 31 个内容提交全已在 `origin/dev_festival`（qa 只是把 dev_festival 合进来没 push），删本地 qa 零损失。判据永远是"内容在不在远端"。
- **非 git 残留目录**：`git worktree list` 不列、但磁盘上有（如曾出现的 `gdconfig-qa-m3`，`.git` 都没有）→ 直接 `rm -rf`。

## 删除命令模板

```bash
cd /c/X3/gdconfig
git worktree remove /c/X3/gdconfig-<name>     # 干净才成功；有改动加 --force(慎)
git branch -D <branch>                         # 顺手删本地 ref（远端不受影响）
rm -rf /c/X3/<非git残留目录>
```

跟 [[workflow_x3_multiagent_worktree]]（多 agent 并发用 worktree）配套：那篇讲怎么开，这篇讲怎么收。
