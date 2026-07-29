# X3 功能整体撤除手法（代码 + prefab 全清，不动主仓工作区）

> 场景：一个活动/功能做完了但要**推倒重做**（或砍掉），要把它在 `x3-project` 里的实现全部撤掉再推上去。
> 首次沉淀：2026-07-28 马戏节限时抢购推倒重做（清除提交 `973997a92ce`，120 文件 / 19.7 万行纯删除）。
> 配套脚本：`tools/feature_strip.py`

---

## 一、开工前必须先问清楚的三件事（少问一件就会返工）

| 问题 | 为什么必须问 |
|---|---|
| **配置仓要不要一起清？** | 表结构 def 在 gdconfig，`*.proto` / `ProtoGen/*.bytes` / `CfgProtos/*.cs` 是**导表生成物**。只清代码不清配置 → 下次跑 jolt 导表，这些文件全自己长回来。留配置是合法选择，但必须让用户知道会长回来，不然会被当成「漏清」。 |
| **清到哪条分支？** | 功能 commit 经常早就合进 `origin/dev` 了。只在 `dev_festival` 撤，dev 上还留着，要等发版合并才带过去。`dev` 是受保护分支，要单独走 MR。 |
| **feature 分支 / worktree 留不留？** | 重做时要回头翻旧实现，默认建议留作存档。 |

## 二、不要在主仓工作区干这件事

X3 主仓 `C:\x3-project` 基本**永远是脏的**（别的会话/别人在途改动）。撤除动作会碰几十上百个文件，在主仓做等于拿别人的在途工作赌命。

两个安全姿势：

1. **index-only revert（推荐，本次用的）**：全程只操作一个临时 index，不落任何工作区、不额外 checkout 十几个 G。
   ```bash
   export GIT_INDEX_FILE=/path/to/tmp.idx
   git read-tree origin/<分支>
   # ... 各种 git apply --cached / update-index ...
   TREE=$(git write-tree)
   COMMIT=$(echo "$MSG" | git commit-tree $TREE -p origin/<分支>)
   git push origin $COMMIT:refs/heads/<分支>
   ```
   **不要动本地分支 ref** —— 本地分支一移，用户工作区里那堆还在磁盘上的文件会全变成未跟踪/冲突，一片红。推远端就行，让用户自己挑时机 pull。
2. sparse worktree（要看真实文件时用），见 [[reference_x3_new_actvtype_playbook]] 的 sparse worktree 姿势。

## 三、主流程：补丁回退 + 结构摘块，两条腿

### 3.1 先算出「这个功能碰过哪些路径」
```bash
for c in <commit1> <commit2> ...; do git diff-tree --no-commit-id --name-only -r $c; done | sort -u
```

### 3.2 逐**文件**（不是逐 commit）反向打补丁
```bash
git diff-tree -p --binary --no-commit-id -r $c -- "$p" | git apply -R --cached -C1 --whitespace=nowarn -
```
两个关键点：
- **逐文件、不逐 commit**：`git apply` 是**整份补丁原子生效**的，一个文件打不上会导致整个 commit 的回退全部回滚，后面的 commit 跟着连环失败，看起来像"全崩了"，其实只坏一两个文件。
- `-C1` 放宽上下文匹配，能吃掉相邻行被改动的情况；比 `--3way` 好用（`--3way` 会往 index 里塞冲突标记，index-only 模式下很难收拾）。

### 3.3 打不上的那几个 → 用 `feature_strip.py` 结构摘块

**为什么打不上**：合并 dev 之后往往跑过一次 **proto/DK 重生成**（本次是 `328ef08170f`），生成文件被重排 + 字段让号（限时抢购的 `flashSaleData` 从 67 让到 70），补丁上下文全对不上。**这类文件永远别指望补丁回退。**

固定会中招的一批：
- `client/Assets/Scripts/Protos/activity.cs`（客户端生成 pb）
- `client/Assets/Scripts/CSSharedHotfix/Common/Protos/activity.cs`（hotfix 生成 pb）
- `client/Assets/TFWConfig/Protobuf/activity.proto` / `msgid.def`
- 追加式注册表：`ActivityConst.cs` / `MetaConst.cs` / `ErrCode.Activity.cs` / `SysOpReason.cs` / `TEventType.Activity.cs`

对这些**改成从「当前 origin 版本」按结构整块摘除**（而不是反向打补丁）：
```bash
python tools/feature_strip.py --token FlashSale \
  --file csharp:activity_client.cs \
  --file csharp:activity_hotfix.cs \
  --file proto:activity.proto \
  --file lines:msgid.def
```
生成代码规整得可怕，摘除点就固定那几类：顶层消息类整块 / 宿主消息的字段属性 / Encode 的 `if (xxx != null)` 块 / Decode 的 `case NNN:` 块 / 复位行 / `RegisterType` 行。脚本用**大括号配平**找边界，不靠行号硬编码。

### 3.4 导表生成物单独处理
`ProtoGen/*.bytes` + `.meta` 直接 `git update-index --force-remove`；`AllTableDataMd5.txt` 删掉对应几行。这些文件**每次导表都在变**，用补丁回退必挂。

## 四、收口三道验证（缺一道都不算干净）

```bash
TREE=$(git write-tree)
# 1. 路径零残留
git ls-tree -r --name-only $TREE | grep -i <token>
# 2. 内容零残留（全树 grep，注意 token 的驼峰/下划线/中文三种写法都要扫）
git grep -I -i -l -e "flashsale" -e "flash_sale" -e "限时抢购" $TREE --
# 3. 必须是纯删除、零新增
git diff --numstat origin/<分支> $TREE | awk '$1>0 {print "新增"$1"行: "$3}'   # 应为空
```
再加一道**行数对账**：删除行数 ≈ 当初各 commit 的新增行数。对不上的文件（本次 hotfix 833 vs 当初 841）说明中间被重生成过，去看 diff 接缝确认没误伤。

## 五、push 之后必须复核父提交

X3 主仓经常有别的会话在同时推。`git push` 输出里的 `old..new` 的 old **可能不是你 fetch 时看到的那个**。落地后一定要：
```bash
git log --format="%H %P" -1 <你的commit>          # 看真实父提交是谁
git diff --shortstat <真实父提交> <你的commit>     # 确认只有你那些改动
```
本次真实父提交是别人中途推的皮肤视频 commit，diff 复核确认没覆盖任何人。**只看"推成功了"不够。**

## 六、收尾要跟用户交代清楚的

1. 配置留着 → 下次导表 proto/bytes/CfgProtos 会长回来，**是预期不是漏清**。
   **已实证（限时抢购案 07-29）**：清除后第 2 天，Jenkins 导表 robot 提交 `edad74aa187` 就把 18 个文件带回了 dev_festival
   （`Res/Config/Proto/ActvFlashSale{,Pack,Reward}.proto` + `ProtoGen/*.bytes` + `CfgProtos/ActvFlashSale*.cs`，各带 .meta）。
   同时复核：玩法代码 / prefab / 共享注册**零残留**——即回来的**只有纯数据类空壳，无人引用，不影响编译运行**。
   用户拍板不动（重做沿用表结构还省事）。**结论：撤除后隔天再看到这批生成物，不要当成漏清、不要二次去清**；
   真要连它一起清，得先动 gdconfig（删 `*_def.py` + tsv + `actvonline_def.py` 的类型登记 + PostProcessData 登记）再导一次表。
2. 用户主仓工作区里那些**未提交**的挂钩（本次是 `ActivityMeta.cs` 6 处 + DisplayKey 注册）没被清，要自己剥；里面往往还夹着**无关的在途改动**，别顺手删
3. 本地分支还停在老位置、跟远端分叉了，pull 前先收在途改动
4. 只清了一条分支的话，明说另一条分支上还留着、什么时候才会带过去

## 关联
- [[workflow_x3_merge_conflict_audit]] · [[reference_x3_new_actvtype_playbook]] · [[workflow_x3_multiagent_worktree]]
- [[project_x3_flashsale_reskin]]（首个案例）
