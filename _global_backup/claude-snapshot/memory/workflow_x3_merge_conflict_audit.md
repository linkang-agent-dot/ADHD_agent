---
name: x3
description: dev-summer-love-song 合并到 dev 时配置字段被错误覆盖的审计方法；含按 ID/字段对比模板 + 公式缓存丢失误诊修复
metadata: 
  node_type: memory
  type: workflow
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 触发场景

合并节日分支 → dev 后，怀疑某些字段被错误覆盖（dev 上原本对的值被节日分支的旧值替代）。2026-05-26 X3 dev-summer-love-song → dev MR!218 实战：

- `ActvScoreTask 1701.Score` 50000 → 错被覆盖（已 linkang 手工修 `3eb61b0`）
- `ActvScoreTask 1802.Score` 10000 → 错被覆盖成 3000（漏修，user 发现后 `c9dbed3` 修）
- `ActvScoreMulti R21-R26` 公式缓存丢失，**xlrd 读出 None** → 误诊为"数据缺失"，实际数据完整只需 Excel 重算（`10ae652`）

## 审计三方对比模板（按 ID/字段，非行号）

```python
import openpyxl, subprocess, os

# 取 3 个 ref 的 xlsx 副本
for ref_name, ref in [('before', '0b8e6cd^1'), ('sls', '0b8e6cd^2'), ('now', 'HEAD')]:
    tmp = rf'C:\Users\linkang\AppData\Local\Temp\audit_{ref_name}_{file}.xlsx'
    subprocess.run(['git', 'show', f'{ref}:data/{file}'], stdout=open(tmp, 'wb'))

def read_by_id_field(fp):
    """sheet -> id -> field_name -> value"""
    out = {}
    # ⚠️ 必须 read_only=False！read_only=True 会漏读 col1 为 None 公式行
    wb = openpyxl.load_workbook(fp, data_only=True)
    for sn in wb.sheetnames:
        if sn.startswith('#'): continue
        ws = wb[sn]
        if ws.max_row < 7: continue
        header = [ws.cell(row=6, column=c).value for c in range(1, ws.max_column+1)]
        m = {}
        for r in range(7, ws.max_row + 1):
            idv = ws.cell(row=r, column=1).value
            if idv is None or not isinstance(idv, (int, float, str)): continue
            fields = {}
            for ci, fname in enumerate(header, 1):
                if not fname: continue
                v = ws.cell(row=r, column=ci).value
                if v is not None: fields[str(fname).strip()] = v
            if fields: m.setdefault(idv, fields)
        out[sn] = m
    wb.close()
    return out

# 对比：before 有值 但 now 跟 sls 一样（合并选了 sls 的值，丢了 dev 的）
suspects = []
for sn in before:
    if sn not in now: continue
    for idv in set(before[sn]) & set(now[sn]):
        for field in set(before[sn][idv]) | set(now[sn][idv]):
            vb = before[sn][idv].get(field)
            vn = now[sn][idv].get(field)
            vs = sls.get(sn, {}).get(idv, {}).get(field)
            if vb != vn and vn == vs and vb != vs:
                suspects.append((sn, idv, field, vb, vs, vn))
```

## 假阳性排除

3 类常见假阳性（**不是合并丢值，要识别后忽略**）：

| 类型 | 特征 | 例 |
|------|------|----|
| 1. 合并正确选了新版本 | `before` 是旧值，`sls` 是新版本（来自更早的有效改动），`now` = `sls` 是对的 | ActvScoreMulti 7173-7177 RankID 141-145 → 619-625（X3NEW-735 改跨服） |
| 2. 表结构增列导致 col 号错位 | `before` col9=A 字段、`sls`/`now` col9=B 字段（中间插入了新列） | ChainPack col9 在 dev_before 是"备注"，sls/now 是"Video"（备注移到 col10）|
| 3. 公式缓存丢失看似数据缺失 | xlrd / openpyxl read_only=True 读公式列 = None，实际数据在公式里 | ActvScoreMulti R21-R26 col1/col3/col7 都是公式 `=A20+1`/`=C20`/`=G20+1`，缓存丢则读 None |

## 假阳性 3 的特别修法（公式缓存丢失）

不用改任何数据，让 Excel COM 强制重算：

```python
import pythoncom, win32com.client
pythoncom.CoInitialize()
xl = win32com.client.gencache.EnsureDispatch('Excel.Application')
xl.Visible = False
xl.DisplayAlerts = False
try:
    wb = xl.Workbooks.Open(fp)
    wb.Application.CalculateFull()  # 关键
    wb.Save()
    wb.Close(SaveChanges=False)
finally:
    xl.Quit()
    pythoncom.CoUninitialize()
```

执行后 xlrd 读公式列就能拿到缓存值，导表 KeyError / 数据丢失类报错通常消失。

## 完整审计清单（合并 PR 后跑一遍）

1. **dev 独有 commits 列表**：`git log first-parent 0b8e6cd^2..0b8e6cd^1 --oneline -- 'data/*.xlsx'`
2. **每个 commit 看改了哪些 (sheet, ID, field)**：对比 commit^ vs commit 提取实际改动
3. **3 方对比当前 dev**：每条改动验证 `now` 是否保留了 `before` 的值（或正确合并了 sls 的新值）
4. **公式缓存检查**：对含公式的表跑 CalculateFull，看 xlrd 读出来的关键字段是不是非空
5. **修补漏掉的合并冲突**：单独 commit 修每处，message 写 `fix: <字段> 合并冲突错误覆盖修复，<合并 commit hash>`

## TSV 迁移后合并 dev 的标准流程（2026-06-02 dev_fix_pack_type 实战）

迁移到 tsv 后，合并 dev 进功能分支会遇到一个**结构性坑**：因日常「改 tsv 不碰 xlsx」，分支的 xlsx 早已滞后于 tsv。git 合并时 xlsx 是二进制（只能整取一边）、tsv 是文本（3 方合并），结果 **dev 带进来的旧 xlsx 与合并后正确的 tsv 不一致**。若放任 pre-commit 钩子（`scripts/sync_xlsx_tsv.py --staged`）跑正向 `xlsx→tsv`，会用旧 xlsx **覆盖掉分支在 tsv 里的修复**（dev_fix_pack_type 差点丢掉 20 行 Pack 修复）。

正确流程：
1. `git merge --no-commit --no-ff dev`（不自动提交，先看冲突）。
2. **tsv 冲突**（真源）：脚本逐字段对比两边，**只在冲突块内保留正确侧、删标记**，不要 `git checkout --ours`（会丢另一边的非冲突自动合并改动）。判断哪侧正确：`git diff <merge-base> dev -- tsv/X.tsv` 看 dev 改了啥，对比本分支意图。
3. **xlsx 一致性**：跑 `python scripts/sync_xlsx_tsv.py --staged --check`（dry-run），凡报「正向(xlsx→tsv)」的表都要警惕——用临时目录 `xlsx_to_tsv.convert_one(xp, data, tmp)` + `filecmp` 验证正向是否幂等。**不幂等的表（xlsx≠合并后tsv），以 tsv 为真源整表重建 xlsx**（openpyxl `Workbook`，按 `tsv_to_xlsx.sheet_member_map` 的 sheet 顺序逐 sheet 写入，空串写 None；无公式表可放心整存），写后用 read_only+data_only 往返校验 `== read_tsv_rows`。
4. 重建后再跑 dry-run 直到「0 阻断、正向幂等」，正常 `git commit`（无需 --no-verify，钩子正向变幂等空操作）。
5. 功能分支已含 dev 全部时，`dev_fix_pack_type → dev` 是 `git merge --ff-only`（无新提交无冲突）。

## 相关

- 导入只认 tsv、改 tsv 不碰 xlsx：[[reference_x3_tsv_export_migration]]（旧 xlsx 公式缓存/CalculateFull 问题随 xlsx 弃用已不适用）
- 任务完成必带知识库更新：[[feedback_proactive_knowledge_update]]
