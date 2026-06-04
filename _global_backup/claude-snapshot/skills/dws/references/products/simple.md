# 单命令产品合集

以下产品命令较少，合并参考。

---

## devdoc — 开放平台文档

### 搜索开放平台文档
```
Usage:
  dws devdoc article search [flags]
Example:
  dws devdoc article search --keyword "OAuth2 接入" --page 1 --size 10
Flags:
      --keyword string   搜索关键词 (必填)
      --page string      页码 (默认 1)
      --size string      每页数量 (默认 10)
```

---

## approval — 审批

### 查询审批表单
```
Usage:
  dws approval list-forms [flags]
Example:
  dws approval list-forms --format json
```

### 查询审批实例详情
```
Usage:
  dws approval detail --instance-id <ID> [flags]
Example:
  dws approval detail --instance-id <ID> --format json
```

### 查询审批任务
```
Usage:
  dws approval tasks --instance-id <ID> [flags]
Example:
  dws approval tasks --instance-id <ID> --format json
```

---

## 意图判断

- 用户说"开发文档/API 文档/接口文档" → `devdoc article search`
- 用户说"审批/请假/报销/出差" → `approval`

## 上下文传递表

| 操作 | 从返回中提取 | 用于 |
|------|-------------|------|
| `devdoc article search` | 文档链接 | 直接展示给用户 |
| `approval list-forms` | processCode | `approval detail` / `approval tasks` 等 |
| `approval tasks` | taskId | `approval approve` / `approval reject` |
