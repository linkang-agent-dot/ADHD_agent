# 视频会议 (conference) 命令参考

> ⚡ 由 PC 版处理，`dws` wrapper 自动路由。

## 命令总览

| 子命令 | 用途 |
|-------|------|
| `meeting create` | 预约视频会议 |

---

## meeting create — 预约会议

```
Usage:
  dws conference meeting create [flags]
Example:
  dws conference meeting create --title "产品评审会" \
    --start 2026-03-11T14:00:00+08:00 --end 2026-03-11T15:00:00+08:00
Flags:
      --title string   会议标题 (必填)
      --start string   开始时间 ISO-8601 (必填)
      --end string     结束时间 ISO-8601 (必填)
```

> 注意：`conference meeting create` 不会自动关联日历日程。如需同时创建日程，需额外调用 `dws calendar event create`。

## 意图判断

用户说"预约视频会议/开会/线上会议" → `conference meeting create`
用户说"日程/会议室预定" → `calendar`（不是 conference）
