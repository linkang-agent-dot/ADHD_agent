# P2 配置表上传工具 (p2-config-upload)

P2 项目的配置表上传 Skill，支持从 Google Sheet 下载配置表并提交到 gdconfig 仓库。

## 功能

- **全表模式**：输入表编号（如 `2115`），下载整张表并提交
- **行筛选模式**：输入行 ID（如 `211552039`），只更新指定行，其余行保持不变
- **内置 898 张表**的编号→页签映射，无需手动查找
- **SheetID 完整索引**：`references/table_index.md`

## 触发词

`P2导表`、`传表`、`导表`、`上传配置`、或直接给出数字编号+分支名

## 文件结构

```
├── SKILL.md                  # Skill 定义（含 898 表速查）
├── README.md                 # 本文件
├── references/
│   ├── table_index.md        # SheetID 完整索引
│   └── cases/                # 历史配置案例
└── scripts/
    └── merge_rows.py         # 行筛选模式合并脚本
```
