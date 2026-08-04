# 图表技能思维导图后端扩展初始化报错

- 日期：2026-08-04
- 任务：制作 X3 节日外显养成线交互 HTML
- 现象：按 `generate_mind_map.md` 提供合法的 `data.name/children`、dark theme、rough texture 后，`scripts/generate.js` 返回 `Cannot read properties of undefined (reading 'key')`，堆栈位于远端 `setExtensions/setTransforms`。
- 根因：图表服务端运行时扩展配置缺失或兼容问题；不是本次数据节点缺少必填 name。
- 处理：不重试同一后端，改用自包含 HTML 内联 SVG/CSS 绘制角色分层地图，避免外链并满足离线交付要求。
- 状态：open
