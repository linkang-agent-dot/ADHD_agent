# 全 Assets 搜索 EffectDisplay 超时

- 日期：2026-08-06
- 任务：核查英雄主页视频展示生命周期
- 现象：在 `client\Assets` 全量递归搜索 `class EffectDisplay|VideoDisplayKey` 超过工具时限并被终止。
- 根因：X3 Unity 资产仓体量大，直接对全 Assets 扫全部 `.cs` 范围过宽。
- 处理：先用 `rg --files` 按文件名定位组件，再仅搜索脚本目录/命中文件；本次只读检查未造成工程改动。
- 状态：open
