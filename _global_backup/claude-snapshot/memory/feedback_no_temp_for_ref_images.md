---
name: 禁止将参考图放在 TEMP 目录
description: 角色立绘等参考图严禁放 %TEMP%，TEMP 会被系统清理导致丢失
type: feedback
originSessionId: bdf1b351-c9bd-431c-8265-f5f9ae8ea39b
---
参考图（角色立绘、封面风格等）严禁放在 %TEMP% 目录下。

**Why:** TEMP 目录会被系统定期清理，放在这里的参考图会丢失，导致 skill 执行时找不到文件。

**How to apply:** 参考图应存放在持久化路径（如 skill 的 `references/img/` 目录或 `KB/产出-本地化与美术/` 下），同时更新 config.json 中的路径指向。P2 集卡册 skill 的 `characters` 字段（roger/scott/penguin）需要从 `%TEMP%` 迁移到持久路径。

**同族坑（2026-07-10 美需文档实锤）**：`~\.claude\image-cache\`（用户发进对话的截图缓存）同样是临时目录——生成文档/脚本要引用用户截图时必须**当场转存** KB `ref-images\` 再引用；直接引缓存路径，重跑脚本时图已被清（美需三件套参考图中招；后改从 X3 客户端现取真图标反而更准——能取真源就别用截图）。
