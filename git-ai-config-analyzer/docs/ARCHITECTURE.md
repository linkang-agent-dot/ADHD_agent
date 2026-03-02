# 架构设计文档

## 概述

Git AI 配置分析器是一个基于 Python 的命令行工具，使用 AI 技术智能分析 Git 仓库中配置文件的变更。

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Git AI 配置分析器                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐  │
│  │  CLI 层     │   │  核心逻辑层  │   │   AI 服务层     │  │
│  │             │   │             │   │                 │  │
│  │ - 参数解析  │──▶│ - 工作流控制 │──▶│ - OpenAI API   │  │
│  │ - 用户交互  │   │ - 数据转换   │   │ - 提示词构建   │  │
│  └─────────────┘   └─────────────┘   └─────────────────┘  │
│                           │                                 │
│           ┌───────────────┴───────────────┐                │
│           ▼                               ▼                │
│  ┌─────────────────┐           ┌─────────────────┐        │
│  │  Git 操作层      │           │  报告生成层      │        │
│  │                 │           │                 │        │
│  │ - 提交查询       │           │ - Markdown     │        │
│  │ - 差异提取       │           │ - JSON         │        │
│  │ - 文件分析       │           │ - Console      │        │
│  └─────────────────┘           └─────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 模块设计

### 1. 配置管理模块 (config.py)

**职责**：管理应用程序配置

**核心类**：
- `AnalyzerConfig`: 配置数据类

**配置项**：
- Git 仓库相关：repo_path, target_dir, base_branch
- AI 相关：ai_model, ai_api_key, ai_base_url
- 输出相关：output_format, output_path

### 2. Git 仓库管理模块 (git_repo_manager.py)

**职责**：封装 Git 操作

**核心类**：
- `GitRepoManager`: Git 操作管理器
- `CommitInfo`: 提交信息数据类
- `FileChange`: 文件变更数据类

**主要方法**：
```python
- get_current_branch() -> str
- get_commits(commit_range) -> List[CommitInfo]
- get_changed_files(commit_range, target_dir) -> List[FileChange]
- get_file_diff(commit_range, file_path) -> str
```

**设计要点**：
- 使用 subprocess 调用 Git 命令
- 统一的错误处理
- 结果解析和结构化

### 3. 差异提取模块 (diff_extractor.py)

**职责**：提取和解析配置文件差异

**核心类**：
- `DiffExtractor`: 差异提取器
- `DiffContent`: 差异内容数据类
- `ConfigDiff`: 配置差异数据类

**处理流程**：
```
获取 Git Diff
    ↓
解析 Diff 输出
    ↓
提取新增/删除/上下文行
    ↓
关联提交信息
    ↓
生成 ConfigDiff 对象
```

**关键算法**：
- Diff 输出解析：识别 +/-/空格 开头的行
- 上下文保留：记录变更周围的代码行
- 行数限制：避免超大文件占用过多资源

### 4. AI 分析模块 (ai_analyzer.py)

**职责**：使用 AI 分析配置变更

**核心类**：
- `AIAnalyzer`: AI 分析引擎
- `AIAnalysisResult`: AI 分析结果数据类

**分析流程**：
```
ConfigDiff
    ↓
构建提示词
    ↓
调用 OpenAI API
    ↓
解析 JSON 响应
    ↓
生成 AIAnalysisResult
```

**提示词设计**：
- 系统提示：定义 AI 角色和专业领域
- 用户提示：包含变更信息、差异内容
- 输出格式：JSON 格式，便于解析

**容错机制**：
- API 调用失败：回退到基础分析
- 响应解析失败：提取部分信息
- 无 API Key：提供基础功能

### 5. 报告生成模块 (report_generator.py)

**职责**：生成多种格式的分析报告

**核心类**：
- `AIReportGenerator`: 报告生成器

**支持格式**：
1. **Console**: 控制台文本，快速查看
2. **Markdown**: 结构化报告，易读易分享
3. **JSON**: 机器可读，便于集成

**报告结构**：
```
执行摘要
    ↓
AI 分析总结
    ↓
功能新增配置（重点）
    ↓
变更分类汇总
    ↓
高优先级变更
    ↓
需要同步的配置
    ↓
所有变更详情
```

### 6. 主程序模块 (main.py)

**职责**：协调各模块，控制执行流程

**工作流程**：
```
1. 解析命令行参数
2. 初始化配置
3. 连接 Git 仓库
4. 获取提交和变更
5. 提取差异内容
6. AI 分析变更
7. 生成整体总结
8. 生成报告输出
```

## 数据流

```
命令行参数
    ↓
AnalyzerConfig
    ↓
GitRepoManager ──▶ CommitInfo[]
    ↓              FileChange[]
DiffExtractor  ──▶ ConfigDiff[]
    ↓
AIAnalyzer     ──▶ AIAnalysisResult[]
    ↓
AIReportGenerator ──▶ Report (Markdown/JSON/Console)
```

## 依赖关系

```
main.py
  ├─ config.py
  ├─ git_repo_manager.py
  ├─ diff_extractor.py
  │   └─ git_repo_manager.py
  ├─ ai_analyzer.py
  │   ├─ config.py
  │   └─ diff_extractor.py
  └─ report_generator.py
      └─ ai_analyzer.py
```

## 关键设计决策

### 1. 为什么使用 subprocess 而不是 GitPython？

**原因**：
- 更轻量，无需额外依赖
- 更灵活，可以执行任意 Git 命令
- 更稳定，不依赖第三方库的维护

### 2. 为什么将提示词硬编码而不是使用模板文件？

**当前实现**：硬编码在 ai_analyzer.py 中

**原因**：
- 简化部署，无需管理额外文件
- 便于调试和修改

**未来改进**：
- v1.1.0 将支持从 prompts/ 目录加载模板
- 支持用户自定义提示词

### 3. 为什么同时支持有 AI 和无 AI 模式？

**原因**：
- 灵活性：不是所有用户都有 API Key
- 成本考虑：可以先用无 AI 模式筛选，再用 AI 详细分析
- 可靠性：AI 服务不可用时仍能提供基础功能

### 4. 为什么使用数据类（dataclass）？

**优势**：
- 自动生成 __init__、__repr__ 等方法
- 类型提示，提高代码可维护性
- 支持默认值和 post_init 处理

## 性能考虑

### 1. 差异内容限制
- `max_diff_lines`: 限制单文件分析行数
- 避免超大文件消耗过多内存和 API token

### 2. 批量处理
- 一次性获取所有提交和变更
- 减少 Git 命令调用次数

### 3. API 调用优化
- 每个文件独立分析，支持并行（未来版本）
- 可配置 AI 模型，平衡成本和质量

## 扩展性

### 计划中的扩展点

1. **支持更多 AI 模型**
   - Claude (Anthropic)
   - 本地模型（Ollama）
   - Azure OpenAI

2. **插件系统**
   - 自定义分析器
   - 自定义报告格式

3. **配置文件支持**
   - 除了 CSV，支持 JSON、YAML、XML

4. **缓存机制**
   - 缓存 AI 分析结果
   - 避免重复分析

## 安全考虑

1. **敏感信息保护**
   - API Key 从环境变量读取
   - .env 文件不提交到版本控制

2. **输入验证**
   - 验证 Git 仓库路径
   - 验证分支名称

3. **错误处理**
   - 捕获并处理异常
   - 提供清晰的错误信息

## 测试策略

1. **单元测试**
   - 每个模块的核心功能
   - 边界条件和异常情况

2. **集成测试**
   - 完整工作流测试
   - 不同参数组合

3. **模拟测试**
   - 模拟 Git 操作
   - 模拟 AI API 调用

---

*最后更新: 2026-02-02*
