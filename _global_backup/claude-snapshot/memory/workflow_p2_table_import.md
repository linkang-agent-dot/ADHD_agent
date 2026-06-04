---
name: P2导表工作流
description: P2项目配置表从Google Sheets下载并推送到gdconfig指定分支的完整流程
type: reference
originSessionId: e02faab5-8b06-455f-8afa-a56433a9e538
---
# P2 导表工作流

## 工具
- 路径：`C:\gdconfig\scripts\GSheetDownloader.exe`
- 仓库：`C:\gdconfig`（P2 配置表 git 仓库）

## 交互输入顺序（管道方式运行）

**⚠️ 关键：input 文件必须写到 `$env:TEMP` 等仓库外路径，绝对不能写到 `C:\gdconfig\scripts\` 里。** GSheetDownloader 在 push 前会把 working tree 任何 diff 一起带上,即使 `.gitignore` 里有 `_input.txt`(2026-05-28 实测仍被 commit),曾发生过整张表因数据报错被跳过,而 `_input.txt` 的 LF/CRLF 变更被当成"成功 commit" push 到 hotfix 的事故。

```bash
INPUT="/c/Users/linkang/AppData/Local/Temp/_gsd_input.txt"
cd /c/gdconfig/scripts
python -c "
import sys
tables = '2112 2121'
msg = '[配置更新]2112-activity_config+2121-activity_special-bugfix'
sys.stdout.buffer.write(('1\n' + tables + '\ny\n' + msg + '\n').encode('gbk'))
" > $INPUT && PYTHONIOENCODING=utf-8 ./GSheetDownloader.exe < $INPUT
```

> **注意**：必须用 `.encode('gbk')`，GSheetDownloader.exe 是 Windows 程序默认 GBK 读文件，用 UTF-8 写会导致提交信息乱码。

## 验证导表是否真的成功

跑完后看输出最后几行,**只有 `成功: N` 中 N>0 才算导成功**。看到:
- `成功: 0, 失败: 0` → 全部被跳过(通常是 int/float 字段空值),即使最终 push 了也是垃圾 commit
- `! int error on row X col Y : 字段名` / `invalid literal for int()` → 该字段空值,先去 GSheet 填好再重跑

| 步骤 | 输入 | 说明 |
|------|------|------|
| 1 | `1` | keep current branch（当前在哪个分支就传到哪） |
| 2 | `2112 2121`（按需） | 空格分隔表号，工具按前缀匹配 |
| 3 | `y` | 确认 commit & push |
| 4 | 提交信息 | 格式：`[配置更新]2112-activity_config+2121-activity_special-bugfix` |

**⚠️ 有表导入失败时工具会自动中断，不会提交——需要先排查错误再重跑。**

## 常用分支
- `bugfix` — bug修复专用（日常最常用）
- `hotfix` — 紧急热修
- `dev` — 开发分支

## 常用表号速查
| 表号 | 文件名 | 说明 |
|------|--------|------|
| 2112 | activity_config.tsv | 活动配置表 |
| 2121 | activity_special.tsv | 活动特殊处理 |
| 2115 | activity_task.tsv | 任务模块配置 |
| 2135 | activity_package.tsv（多页签） | 活动礼包 |
| 1111 | item.tsv | 道具表 |
| 2011 | iap_config.tsv | IAP配置 |

## 提交信息格式
`[配置更新]<表号1>-<表名1>+<表号2>-<表名2>-<分支名>`

## 注意事项
- 运行前确认当前在目标分支（`git branch` 看一下）
- 工具会先 `git pull` 拉最新再写文件
- 选项 `1`（keep）= 不切分支，保持当前；选项 `2`=dev，选项 `3`=qa
