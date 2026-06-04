---
name: x3-mr
description: x3-project 仓 dev 是 protected branch，commit message 强制 X3NEW-/X3- 前缀；改动需走 feature branch + MR；GitLab API 一行创建 MR
metadata: 
  node_type: memory
  type: workflow
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 受保护分支规则

| 仓库 | dev 是否受保护 | 直接 push dev |
|------|--------------|--------------|
| **x3-project** (代码+资源仓) | ✅ 受保护 | ❌ 失败：`pre-receive hook declined` |
| **gdconfig** (配置 xlsx 仓) | ❌ 不受保护 | ✅ 可以直接 push |

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

**注意 form-data POST 会触发 GitLab 500 错误**（中文 title 可能不被识别），必须用 **JSON body + `Content-Type: application/json`**。

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

## 相关

- x3-project 仓配置详情：[[reference_x3_project_repo]]
- GITLAB_TAP4FUN_TOKEN：从 Windows User 环境变量取（`powershell -Command "[Environment]::GetEnvironmentVariable('GITLAB_TAP4FUN_TOKEN','User')"`）
