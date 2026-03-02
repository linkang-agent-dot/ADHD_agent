# Git AI 配置分析器

<div align="center">

**使用 AI 智能分析 Git 仓库中配置文件的变更，自动识别功能新增配置，生成详细的分析报告**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen)]()

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](USAGE.md) • [更新日志](CHANGELOG.md)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [项目结构](#项目结构)
- [注意事项](#注意事项)
- [贡献指南](#贡献指南)
- [License](#license)

---

## 🎯 项目简介

Git AI 配置分析器是一个智能化的 Git 配置文件变更分析工具，特别适用于游戏开发、配置管理等场景。

**核心价值**：
- 🚀 **提高效率**：自动分析配置变更，节省人工检查时间
- 🤖 **AI 驱动**：利用 GPT 模型智能识别配置用途和影响
- 📊 **全面分析**：从提交记录到影响评估，全流程覆盖
- 📝 **多格式输出**：支持 Console、Markdown、JSON 多种格式

---

## ✨ 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| 📚 **提交记录检查** | 获取指定分支范围内的所有提交 |
| 🔍 **差异内容提取** | 提取配置文件的具体变更内容（新增/删除行） |
| 🤖 **AI 智能分析** | 使用 GPT 模型判断配置变更的类型和目的 |
| 🏷️ **功能新增识别** | 自动识别需要关注的功能新增配置 |
| ⚖️ **影响评估** | AI 评估配置变更对系统的潜在影响 |
| 📝 **多格式报告** | 支持 Console、Markdown、JSON 输出 |
| 🚫 **无 AI 模式** | 不需要 API Key 也能生成基础报告 |

### AI 分析能力

- ✅ 自动分类：功能新增 / 参数调整 / Bug修复 / 结构重构 / 废弃移除
- ✅ 影响范围评估：识别可能影响的系统和功能
- ✅ 优先级判断：高 / 中 / 低优先级自动标注
- ✅ 同步建议：判断是否需要同步到其他环境
- ✅ 智能总结：生成整体变更概览和行动建议

## 🚀 快速开始

### 方式一：使用脚本（推荐新手）

```batch
# 1. 安装依赖
scripts\install_deps.bat

# 2. 配置 API Key
copy .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY=你的密钥

# 3. 快速分析
scripts\quick_analyze.bat

# 或生成完整报告
scripts\generate_report.bat
```

### 方式二：命令行（推荐开发者）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入 OPENAI_API_KEY

# 3. 运行分析
# 控制台输出
python src/main.py --format console

# 生成 Markdown 报告
python src/main.py --format markdown --output report.md

# 无 AI 模式（不需要 API Key）
python src/main.py --no-ai
```

### 首次使用提示

⚠️ **如果没有 OpenAI API Key**：
- 使用 `--no-ai` 参数可以生成基础分析报告
- 或者使用兼容 OpenAI API 的国内服务

✅ **推荐配置**：
- 日常开发：使用 `gpt-3.5-turbo`（成本低）
- 重要发布：使用 `gpt-4`（分析更准确）

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--repo-path` | `C:\gdconfig` | Git 仓库路径 |
| `--target-dir` | `fo/` | 目标检查目录 |
| `--base-branch` | `bugfix` | 基准分支 |
| `--compare-branch` | 当前分支 | 比较分支 |
| `--commit-range` | `base-branch..HEAD` | 提交范围 |
| `--format` | `markdown` | 输出格式: console/markdown/json/all |
| `--output` | `ai_config_analysis_report.md` | 输出文件路径 |
| `--ai-model` | `gpt-4` | AI 模型 |
| `--no-ai` | - | 禁用 AI 分析 |
| `--max-diff-lines` | `500` | 单文件最大差异行数 |

## 📖 使用示例

### 场景 1：检查当前分支的配置变更

```bash
# 与 bugfix 分支对比（默认）
python src/main.py

# 与 main 分支对比
python src/main.py --base-branch main
```

### 场景 2：对比两个指定分支

```bash
python src/main.py --base-branch release --compare-branch feature/new-system
```

### 场景 3：快速查看（无 AI）

```bash
# 使用脚本
scripts\analyze_no_ai.bat

# 或命令行
python src/main.py --no-ai --format console
```

### 场景 4：生成完整报告（所有格式）

```bash
python src/main.py --format all
```

输出文件：
- `ai_config_analysis_report.md` - Markdown 报告
- `ai_config_analysis_report.json` - JSON 数据
- 控制台输出 - 即时查看

### 场景 5：使用 GPT-3.5 节省成本

```bash
python src/main.py --ai-model gpt-3.5-turbo
```

### 场景 6：自定义输出路径

```bash
# 按日期生成报告
python src/main.py --output "reports\config_analysis_2026-02-02.md"
```

---

更多使用场景和详细说明，请查看 **[使用指南 USAGE.md](USAGE.md)**

## 报告说明

### Markdown 报告包含

1. **执行摘要**：基本统计信息
2. **AI 分析总结**：整体变更概览
3. **功能新增配置**：需要重点关注的新配置
4. **变更分类汇总**：按类别分组的变更列表
5. **高优先级变更**：需要优先处理的变更
6. **需要同步的配置**：待同步到其他环境的配置

### 配置变更分类

- **功能新增**：新功能需要的配置
- **参数调整**：现有功能的参数修改
- **Bug修复**：修复问题的配置
- **结构重构**：配置结构优化
- **废弃移除**：废弃或移除的配置

## 📁 项目结构

```
git-ai-config-analyzer/
├── src/                        # 源代码目录
│   ├── __init__.py            # 模块初始化
│   ├── config.py              # 配置管理
│   ├── git_repo_manager.py    # Git 仓库操作
│   ├── diff_extractor.py      # 差异内容提取器
│   ├── ai_analyzer.py         # AI 分析引擎（核心）
│   ├── report_generator.py    # 报告生成器
│   └── main.py                # 主程序入口
│
├── scripts/                    # 批处理脚本
│   ├── install_deps.bat       # 安装依赖
│   ├── quick_analyze.bat      # 快速分析（控制台）
│   ├── analyze_no_ai.bat      # 无 AI 分析
│   ├── generate_report.bat    # 生成完整报告
│   ├── generate_ai_report.bat # 生成 AI 报告
│   ├── generate_all_reports.bat # 生成所有格式
│   └── run_tests.bat          # 运行测试
│
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_diff_extractor.py
│   ├── test_ai_analyzer.py
│   └── test_report_generator.py
│
├── prompts/                    # AI 提示词模板
│   ├── config_analysis.txt    # 配置分析提示词
│   └── summary_template.txt   # 总结模板
│
├── reports/                    # 报告输出目录
│   └── .gitkeep
│
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略配置
├── requirements.txt           # Python 依赖
├── setup.py                   # 安装脚本
├── LICENSE                    # MIT 许可证
├── README.md                  # 项目说明（本文件）
├── USAGE.md                   # 详细使用指南
└── CHANGELOG.md               # 更新日志
```

## ⚠️ 注意事项

### 1. API 成本控制

| 模型 | 成本 | 适用场景 |
|------|------|----------|
| gpt-4 | 较高 | 重要发布、详细分析 |
| gpt-3.5-turbo | 较低 | 日常开发、快速检查 |
| 无 AI 模式 | 免费 | 只需基础信息 |

**建议**：
- 使用 `--max-diff-lines` 限制分析内容量
- 日常开发使用 gpt-3.5-turbo
- 重要发布前使用 gpt-4 详细分析

### 2. 敏感信息保护

⚠️ **重要**：配置文件内容会发送到 AI 服务进行分析

**建议**：
- 确保不分析包含敏感信息的配置
- 考虑使用本地部署的 AI 模型
- 或使用 `--no-ai` 模式仅生成基础报告

### 3. 分析准确性

- ✅ AI 分析结果**仅供参考**
- ✅ 建议对高优先级变更进行**人工复核**
- ✅ 持续优化提示词以提高准确性

### 4. 性能考虑

- 大量文件变更时，分析可能需要较长时间
- 可以使用 `--target-dir` 缩小分析范围
- 建议定期运行，而不是一次性分析大量提交

---

## 🤝 贡献指南

欢迎贡献代码、报告问题、提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 运行测试

```bash
# 使用脚本
scripts\run_tests.bat

# 或命令行
python -m pytest tests/ -v
```

---

## 📜 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

---

## 📄 License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- 基于 [config-agent](../config-agent/) 项目扩展开发
- 感谢 OpenAI 提供的强大 AI 能力

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

Made with ❤️ by ADHD Agent Team

</div>
