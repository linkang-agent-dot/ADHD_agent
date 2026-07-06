---
name: x3-mr
description: x3-project 仓 dev 是 protected branch，commit message 强制 X3NEW-/X3- 前缀；改动需走 feature branch + MR；GitLab API 一行创建 MR
metadata: 
  node_type: memory
  type: workflow
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## ⚠️ commit 踩坑(2026-06-22)
- **x3-project pre-commit hook：内嵌 gdconfig 子模块(`C:\x3-project\gdconfig`)有未提交内容时，拒绝 commit x3-project**（报 `[gdconfig] uncommitted gdconfig content changes block x3-project commit; commit/stash/revert inside gdconfig first; 超级仓不再自动提交config编辑`）。解法=进内嵌 gdconfig `git stash push <文件>`(可恢复)→提 x3-project→`git stash pop` 还原。内嵌 gdconfig 常停在别的分支(如 newbie)且带零星脏文件(GenProto.py 等)。
- **只提自己的文件用路径限定 commit**：`git commit -m "..." -- 文件1 文件2`（工作树混入别人 staged 的 DK/.asset/.meta/.spriteatlas/子模块指针时，路径限定只提指定文件、不卷入其它，其它原样留着另合）。
- **push feature 别用裸 `git push`**：本地 feature 分支常 track origin/dev，裸 push 会推 dev 被拒；用 `git push origin <feature分支名>` 显式推同名 feature ref。
- ⚠️**push 前必验 MR 三点 diff**：`git diff origin/dev...HEAD --stat`——分支可能混入别人之前的提交(如 DK 修复 fe3f456)，导致 MR 卷入非本功能改动。只领先1个 commit 才干净；多于1个先查 `git log origin/dev..HEAD` 是不是混了别人的，混了要 rebase --onto/cherry-pick 剔除(但工作树脏会挡 rebase)。
- ★**单提交隔离推法(2026-06-22 实证，工作树脏也能用)**：想把某个 commit 单独提 MR、又不想动当前脏工作区/不想 cherry-pick——若该 commit 的**父提交已在 origin/dev**(`git merge-base --is-ancestor <sha>^ origin/dev`)，直接 `git push origin <sha>:refs/heads/<新分支>` 把这一个提交推成新分支，MR diff = 纯该提交改动。无需 checkout/worktree/rebase，工作区零打扰。
- ⚠️**MR 标题+描述都必须 ASCII(2026-06-22 实证，推翻"只标题")**：GitLab API 创建 MR 时**描述含中文也会 500**，不只标题。两个字段都用纯 ASCII。

## 受保护分支规则

| 仓库 | 分支 | 是否受保护 | 直接 push |
|------|------|-----------|----------|
| **x3-project** (代码+资源仓) | dev | ✅ 受保护 | ❌ `pre-receive hook declined` |
| **gdconfig** (配置仓) | dev / qa | ❌ 不受保护 | ✅ 可直推 |
| **gdconfig** (配置仓) | **master** | ✅ 受保护(2026-07-02实证) | ❌ 被拒→cherry-pick→feature分支→MR(项目4454)→**API merge 自己有权限可自助**(MR!61实证:POST建MR用ASCII标题+PUT补中文+PUT /merge 一气呵成) |

## x3-project commit message 格式强制

pre-commit hook 检查 `git commit -m "..."` 必须匹配：
- `X3NEW-描述` — 新需求/新功能
- `X3-{n}描述` — 关联 jira 单号 X3-n

不符合就拒绝。**错误样例**：`X3夏日恋语 xxx`、`fix: yyy` 都会被拒。**正确样例**：`X3NEW-新增DK_img_Activity_summer_bg_12 xxx`。

## 改 x3-project dev 的标准流程（feature branch + MR）

```bash
cd /c/x3-project
# 1. 基于最新 dev 创建 feature 分支
git fetch origin dev
git checkout -B feature/my_change origin/dev

# 2. 做改动 + commit（注意 X3NEW- 前缀）
git add <files>
git commit -m "X3NEW-描述"

# 3. push feature 分支（feature 分支不受保护）
# 含 LFS 文件时先 push LFS 再 push branch
git lfs push origin feature/my_change   # 如有 LFS 大文件
git push -u origin feature/my_change

# 4. 用 GitLab API 创建 MR（不用手工开浏览器）
```

## GitLab API 创建 MR（Python，一次成功）

```python
import urllib.request, json, ssl
TOKEN = '<从 $env:GITLAB_TAP4FUN_TOKEN 取，Windows User 环境变量>'
body = json.dumps({
    'source_branch': 'feature/my_change',
    'target_branch': 'dev',
    'title': 'X3NEW-描述',
    'description': '...',
    'remove_source_branch': True,  # 合并后自动删源分支
}, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    'https://git.tap4fun.com/api/v4/projects/2859/merge_requests',
    data=body, method='POST',
    headers={'PRIVATE-TOKEN': TOKEN, 'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=30) as r:
    data = json.loads(r.read())
print(f'MR iid={data["iid"]} url={data["web_url"]}')
```

**⚠️ 500 错误的真正根因是 title/description 里有中文，不是 form-data**（2026-06-05 实测修正旧说法）：同一个 `curl --data-urlencode` form-data POST，中文 title → `500 Internal Server Error`；换成**纯 ASCII title** → 立刻 `HTTP 201` 建单成功。是服务端某个 hook（疑似 Jira/钉钉集成）解析中文挂掉。
- **稳妥做法：title 用纯 ASCII**（如 `X3NEW-443 restore 6 festival DK regs`），中文说明放 commit message 或建单后口头同步。
- 中文 description 同样会 500（建单后再 PUT `description=中文` 也失败）→ 干脆 description 也用 ASCII 或留空。
- 这跟 form-data/JSON 无关（两种都试过），别再归因到 Content-Type。
- GET（读 project/branch/MR 列表）中文无影响，只有「**写**带中文的 MR」触发。
- 🟢**2026-06-26 gdconfig 仓实测出可用解法(与上面 x3-project 结论冲突,疑项目差异或 POST/PUT 差异)**：`gdconfig`(项目 **id=4454**, path `x3/gdconfig`)上 **POST form-data 中文 title→500**(一致),但**先用纯英文 title `POST` 建出 MR(HTTP201),再用 `PUT /merge_requests/{iid}` + JSON body(`Content-Type: application/json`, utf-8, `json.dumps(...,ensure_ascii=False)`) 补中文 title+description → 成功**(MR!43 实证,标题描述都中文落地)。→ **遇中文 MR 500 先试"英文POST建单 + 中文JSON PUT补"**;x3-project(2859)是否也吃这招待复验(旧记录说 PUT 也失败,可能当时用的 form-data 不是 JSON)。
- **项目 id 速查**：x3-project=**2859** / gdconfig(配置仓)=**4454**。

## LFS 大文件 push 30 秒超时坑

png > 1 MB 的图（如 AI 生成的活动 banner 4-5 MB）走 LFS。
- 第一次 `git push` 可能超时（`Scanning repository for blobs stored in LFS ... cancelled after 29799.14ms`）
- 临时解决：先 `git lfs push origin <branch>` 单独 push LFS 对象，再 `git push` 推 ref
- LFS 上传跟 ref push 是两阶段操作

## 实战 commit（2026-05-27）

| 项 | 值 |
|----|-----|
| 改动 | 加 `DK_img_Activity_summer_bg_12` 注册 + 4.7 MB png（LFS）|
| feature 分支 | `dev_summer_bg_12_pick` |
| cherry-pick 自 | `dev-summer-love-song` 9122ca5cecc（保留单 commit，不带 194 个无关 commit）|
| MR | [!224](https://git.tap4fun.com/x3/x3-project/-/merge_requests/224) source → dev |
| API 调用 | JSON body，1 次成功 |

## ⚠️ MR 只为「合进受保护的 dev」,推工作分支不用 MR(2026-06-17 澄清)
受保护的**只有 `dev`**。`dev_festival` / `dev_summer_*` / `dev-xxx` 这类**工作分支可直接 `git push origin <分支>`,不需要 MR**(仓里一堆 dev_summer_bg_12_v2/v4/v5 就是直推的)。
- **只为测试验证** → 客户端改动 push 到工作分支(如当前活跃的 `dev_festival`),让测试客户端从该分支出包即可,**全程不开 MR**。
- **要进正式线 `dev`** → 才走 feature branch + MR + review(dev 直接 push 会被拒)。
- 别为一次测试就开 MR 走 review,白增负担。

## 相关

- x3-project 仓配置详情：[[reference_x3_project_repo]]
- GITLAB_TAP4FUN_TOKEN：从 Windows User 环境变量取（`powershell -Command "[Environment]::GetEnvironmentVariable('GITLAB_TAP4FUN_TOKEN','User')"`）
