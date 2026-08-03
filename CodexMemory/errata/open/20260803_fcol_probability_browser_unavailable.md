# FCOL 国服概率表核算时浏览器连接不可用
- 日期：2026-08-03
- 任务：读取国服7月抽奖活动的图片型概率表并计算BP期望值。
- 现象：按 browser skill 初始化默认浏览器后返回 `No browser is available`，无法直接检查活动页中的概率图片。
- 初判根因：当前会话没有可用的 in-app Browser/Chrome 绑定；后续改用活动页源码、图片URL及本地OCR/已有抓取脚本提取。
- 状态：open
