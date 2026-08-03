# pytest 从仓库外启动导致本地包无法导入

- 日期：2026-08-03
- 任务：Codex 旧流程 skill 清理与同步排除
- 现象：从 `C:\Users\linkang` 运行 `pytest C:\ADHD_agent\tests\...` 时，收集阶段报 `ModuleNotFoundError: CodexRuntime`。
- 根因：测试依赖仓库根目录进入 Python import path；绝对测试路径不会自动加入其项目根。
- 处理：将测试命令工作目录设为 `C:\ADHD_agent` 后重跑；以后仓库测试默认从 repo root 启动。
- 状态：open
