# iap_config：以 QA 为准同步到 master 说明

**文档表**：`2011_x2_iap_config`  

**链接**：https://docs.google.com/spreadsheets/d/1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY/edit

| 页签 | gid | 说明 |
|------|-----|------|
| `iap_config_x2qa` | 1985068165 | **为准（源）** |
| `iap_config_x2master` | 1032886231 | **待对齐（目标）** |

- QA 数据行数：**3415**；master 数据行数：**3415**
- 仅 QA 有、需整行复制到 master：**0** 行
- 两边都有但单元格不同：**5** 处

---

## 一、仅 QA 有（整行从 `iap_config_x2qa` 复制到 `iap_config_x2master`）

在 QA 页签中按 `Id` 搜索，选中**整行**（含所有列），复制后粘贴到 master 表数据区；勿覆盖前 7 行 meta。

| # | Id | PkgDesc（QA） |
|---|-----|---------------|

---

## 二、两边都有：把 master 改成与 QA 一致

| Id | PkgDesc | 列（fwcli） | master 当前（应改掉） | QA（为准，覆盖到 master） |
|----|---------|-------------|----------------------|---------------------------|
| 2011360045 | 周付费率礼包-1 | TimeInfo | {"normal":[{"actv_base_id":211200226}]} | {"normal":[{"actv_id":211200226}]} |
| 2011360046 | 周付费率礼包-2 | TimeInfo | {"normal":[{"actv_base_id":211200226}]} | {"normal":[{"actv_id":211200226}]} |
| 2011360047 | 周付费率礼包-3 | TimeInfo | {"normal":[{"actv_base_id":211200226}]} | {"normal":[{"actv_id":211200226}]} |
| 2011360048 | 周付费率礼包-4 | TimeInfo | {"normal":[{"actv_base_id":211200226}]} | {"normal":[{"actv_id":211200226}]} |
| 2011360049 | 周付费率礼包-5 | TimeInfo | {"normal":[{"actv_base_id":211200226}]} | {"normal":[{"actv_id":211200226}]} |

---

## 三、操作检查清单

1. 完成「一」中所有行的整行复制。
2. 对「二」中每一行，在 master 打开对应 `Id`，将所列列改为 QA 单元格内容（或直接复制 QA 该格）。
3. 保存后如需落 git，再按你们 `fwcli`/导表流程导出 TSV。
