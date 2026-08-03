# Browser首次加载失败后过早判定不可用
- 日期：2026-08-03
- 任务：直接加载Browser打开腾讯FCOL国服官网。
- 现象：显式 `agent.browsers.get("iab")` 返回 `Browser is not available: iab`；继续调用 `getForUrl("https://fco.qq.com/")` 报 `ENOENT`，缺少 `C:\Users\linkang\.codex\plugins\cache\openai-bundled\browser\26.715.31925\docs\browser-safety.md`。
- 根因：运行时先加载了旧缓存版本 `26.715.31925`，该版本缺少 `docs/browser-safety.md` 和 `docs/bootstrap-troubleshooting.md`；本机同时存在完整的新版本 `26.727.51351`，但首次失败后没有立即枚举版本、切换完整版本并执行标准发现流程，而是过早对用户报告 Browser 不可用。
- 正确恢复链：①检查 Browser 缓存版本及必需文件；②切到最新完整版本并重建运行时；③按 troubleshooting 调用一次 `agent.browsers.list()`；④若 iab 不可用但 Chrome extension 在线，读取 Chrome 完整文档并用 `agent.browsers.get("chrome")` 连接；⑤实际打开目标网址，以标题、URL、DOM 三项验证。
- 验证结果：Chrome 插件成功连接，并打开 `https://fco.qq.com/main.shtml`，标题为“FC Online足球在线官方网站-腾讯游戏-热爱新生”。
- 教训：单一 selector 或单一缓存版本失败，只能证明该路径失败，不能证明 Browser 能力不可用。向用户报告不可用前，必须完成“完整版本检查 → troubleshooting → 浏览器实例发现 → 实页验证”的自恢复闭环；不得要求用户知道或提示内部加载流程。
- 状态：resolved

---
## 复核结论（2026-08-03，Claude 批量分诊）
- browser恢复链知识已沉淀于 CodexMemory feedback_browser_self_recovery.md,本条为其案例
- 状态：resolved
