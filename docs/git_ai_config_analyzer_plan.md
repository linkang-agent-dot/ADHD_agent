# Git AI 配置分析器项目计划

## 项目概述

基于现有的 `config-agent` 项目，开发一个新的工具：**Git AI 配置分析器**。该工具将检查 Git 分支的提交记录，分析 `C:\gdconfig\fo` 目录下的配置文件变更，并利用 AI 智能判断和总结哪些是功能需要新增的配置，生成详细的分析报告，方便开发过程中检查功能配置。

---

## 目标与功能

### 核心目标

1. **提交记录检查**：获取指定分支的所有提交记录
2. **变更文件分析**：识别 `fo/` 目录下的所有配置文件变更
3. **AI 智能分析**：使用 AI 模型分析变更内容，判断配置类型和用途
4. **报告生成**：生成结构化的分析报告，便于开发者快速了解配置变更

### 功能特性

| 功能 | 描述 |
|------|------|
| 提交历史解析 | 解析指定时间范围或分支范围内的所有提交 |
| 差异内容提取 | 获取配置文件的具体变更内容（新增行、删除行） |
| AI 配置分类 | 使用 AI 将配置变更分类为：功能配置、参数调整、bug修复、结构重构等 |
| 影响范围评估 | AI 评估配置变更对系统的潜在影响 |
| 新增配置识别 | 重点识别需要在其他环境/分支同步的新增配置 |
| 多格式报告 | 支持 Markdown、JSON、Console 等多种输出格式 |

---

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Git AI 配置分析器                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Git 层     │ -> │   分析层      │ -> │    AI 层         │  │
│  │              │    │              │    │                  │  │
│  │ - 提交获取    │    │ - 变更解析    │    │ - 配置分类       │  │
│  │ - 差异提取    │    │ - 内容提取    │    │ - 影响评估       │  │
│  │ - 分支管理    │    │ - 数据结构化  │    │ - 智能总结       │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                                 │
│                              ↓                                  │
│                    ┌──────────────────┐                         │
│                    │    报告生成层     │                         │
│                    │                  │                         │
│                    │ - Markdown 报告  │                         │
│                    │ - JSON 数据      │                         │
│                    │ - Console 输出   │                         │
│                    └──────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 模块设计

参考 `config-agent` 的模块结构，新项目将包含以下模块：

```
git-ai-config-analyzer/
├── src/
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── git_repo_manager.py    # Git 仓库操作（可复用）
│   ├── diff_extractor.py      # 差异内容提取器（新增）
│   ├── ai_analyzer.py         # AI 分析引擎（新增核心）
│   ├── config_classifier.py   # 配置分类器（新增）
│   ├── report_generator.py    # 报告生成器（扩展）
│   └── main.py                # 主程序入口
├── prompts/
│   ├── config_analysis.txt    # AI 分析提示词
│   └── summary_template.txt   # 总结模板
├── scripts/
│   ├── quick_analyze.bat      # 快速分析脚本
│   └── generate_ai_report.bat # 生成 AI 报告脚本
├── tests/
│   ├── __init__.py
│   ├── test_diff_extractor.py
│   ├── test_ai_analyzer.py
│   └── test_config_classifier.py
├── requirements.txt
├── README.md
└── setup.py
```

---

## 核心模块详细设计

### 1. 配置管理模块 (config.py)

```python
@dataclass
class AnalyzerConfig:
    """AI 配置分析器配置"""
    
    # Git 仓库路径
    repo_path: str = r"C:\gdconfig"
    
    # 目标检查目录
    target_dir: str = "fo/"
    
    # 基准分支
    base_branch: str = "bugfix"
    
    # 比较分支（None 表示当前分支）
    compare_branch: Optional[str] = None
    
    # 提交范围
    commit_range: Optional[str] = None
    
    # AI 模型配置
    ai_model: str = "gpt-4"  # 或使用本地模型
    ai_api_key: Optional[str] = None
    ai_base_url: Optional[str] = None
    
    # 分析选项
    include_diff_content: bool = True  # 是否包含差异内容
    max_diff_lines: int = 500          # 单文件最大差异行数
    
    # 输出配置
    output_format: str = "markdown"
    output_path: str = "ai_config_analysis_report.md"
```

### 2. 差异内容提取器 (diff_extractor.py)

**功能**：提取配置文件的具体变更内容，为 AI 分析提供上下文。

```python
@dataclass
class DiffContent:
    """差异内容"""
    file_path: str
    change_type: str      # A/M/D/R
    added_lines: List[str]
    removed_lines: List[str]
    context_lines: List[str]  # 上下文行
    
@dataclass  
class ConfigDiff:
    """配置变更详情"""
    file_path: str
    table_name: str
    change_type: str
    diff_content: DiffContent
    related_commits: List[CommitInfo]
    
class DiffExtractor:
    """差异内容提取器"""
    
    def extract_diff(self, commit_range: str, file_path: str) -> DiffContent:
        """提取文件的差异内容"""
        pass
    
    def extract_all_diffs(self, commit_range: str, target_dir: str) -> List[ConfigDiff]:
        """提取所有配置文件的差异内容"""
        pass
    
    def parse_diff_output(self, diff_text: str) -> DiffContent:
        """解析 git diff 输出"""
        pass
```

### 3. AI 分析引擎 (ai_analyzer.py)

**功能**：使用 AI 模型分析配置变更，提供智能判断和总结。

```python
@dataclass
class AIAnalysisResult:
    """AI 分析结果"""
    file_path: str
    table_name: str
    
    # 分类信息
    change_category: str        # 功能新增/参数调整/bug修复/结构重构
    is_new_feature_config: bool # 是否为功能新增配置
    
    # 分析内容
    summary: str                # 变更摘要
    purpose: str                # 变更目的
    impact_assessment: str      # 影响评估
    
    # 建议
    sync_required: bool         # 是否需要同步到其他环境
    review_priority: str        # 审查优先级：高/中/低
    related_systems: List[str]  # 可能影响的相关系统

class AIAnalyzer:
    """AI 分析引擎"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.client = self._init_ai_client()
    
    def analyze_single_change(self, config_diff: ConfigDiff) -> AIAnalysisResult:
        """分析单个配置变更"""
        prompt = self._build_analysis_prompt(config_diff)
        response = self._call_ai(prompt)
        return self._parse_ai_response(response, config_diff)
    
    def analyze_all_changes(self, config_diffs: List[ConfigDiff]) -> List[AIAnalysisResult]:
        """批量分析所有配置变更"""
        pass
    
    def generate_overall_summary(self, results: List[AIAnalysisResult]) -> str:
        """生成整体总结报告"""
        pass
    
    def _build_analysis_prompt(self, config_diff: ConfigDiff) -> str:
        """构建 AI 分析提示词"""
        pass
```

### 4. 配置分类器 (config_classifier.py)

**功能**：将配置变更分类，识别新增功能配置。

```python
class ConfigCategory(Enum):
    """配置变更类别"""
    NEW_FEATURE = "功能新增"       # 新功能相关的配置
    PARAMETER_ADJUST = "参数调整"  # 现有功能的参数调整
    BUG_FIX = "Bug修复"           # 修复问题的配置变更
    REFACTOR = "结构重构"         # 配置结构优化
    DEPRECATION = "废弃移除"      # 废弃或移除的配置
    UNKNOWN = "未知"              # 无法分类

@dataclass
class ClassificationResult:
    """分类结果"""
    category: ConfigCategory
    confidence: float           # 置信度 0-1
    reasoning: str              # 分类理由
    keywords: List[str]         # 关键词

class ConfigClassifier:
    """配置分类器"""
    
    def classify(self, analysis_result: AIAnalysisResult) -> ClassificationResult:
        """对 AI 分析结果进行分类"""
        pass
    
    def filter_new_feature_configs(
        self, 
        results: List[AIAnalysisResult]
    ) -> List[AIAnalysisResult]:
        """筛选出功能新增的配置"""
        pass
```

### 5. 报告生成器 (report_generator.py)

**功能**：生成包含 AI 分析结果的详细报告。

扩展现有的报告生成器，增加 AI 分析结果的展示：

```python
class AIReportGenerator(ReportGenerator):
    """AI 分析报告生成器"""
    
    def generate_ai_markdown_report(
        self,
        analysis_results: List[AIAnalysisResult],
        overall_summary: str
    ) -> str:
        """生成 AI 分析 Markdown 报告"""
        pass
    
    def _generate_executive_summary(self, results: List[AIAnalysisResult]) -> str:
        """生成执行摘要"""
        pass
    
    def _generate_new_feature_section(self, results: List[AIAnalysisResult]) -> str:
        """生成功能新增配置章节"""
        pass
    
    def _generate_change_detail_section(self, results: List[AIAnalysisResult]) -> str:
        """生成变更详情章节"""
        pass
    
    def _generate_action_items(self, results: List[AIAnalysisResult]) -> str:
        """生成行动项建议"""
        pass
```

---

## AI 分析提示词设计

### 配置分析提示词模板

```text
你是一个专业的游戏配置分析专家。请分析以下配置文件的变更，并提供详细的分析报告。

## 变更信息

**文件路径**: {file_path}
**表名**: {table_name}
**变更类型**: {change_type}
**相关提交**: {commits}

## 变更内容

### 新增内容
{added_lines}

### 删除内容
{removed_lines}

### 上下文
{context_lines}

## 请提供以下分析

1. **变更摘要**: 用一句话描述这个变更
2. **变更目的**: 分析这个变更的目的是什么
3. **变更分类**: 从以下选项中选择
   - 功能新增：新功能需要的配置
   - 参数调整：现有功能的参数修改
   - Bug修复：修复问题的配置
   - 结构重构：配置结构优化
   - 废弃移除：废弃或移除的配置

4. **是否为功能新增配置**: 是/否
5. **影响评估**: 这个变更可能影响哪些系统或功能
6. **是否需要同步**: 是否需要同步到其他环境（开发/测试/生产）
7. **审查优先级**: 高/中/低
8. **其他建议**: 任何需要注意的事项

请以 JSON 格式输出分析结果。
```

### 总结报告提示词模板

```text
你是一个专业的配置管理专家。请根据以下所有配置变更的分析结果，生成一份整体总结报告。

## 变更分析结果汇总

{all_analysis_results}

## 请提供以下内容

1. **整体变更概览**: 总结这段时间的配置变更情况
2. **功能新增配置列表**: 列出所有需要关注的功能新增配置
3. **高优先级变更**: 列出需要重点关注的变更
4. **配置同步建议**: 哪些配置需要同步到其他环境
5. **潜在风险提示**: 可能存在的配置风险
6. **行动建议**: 建议的后续行动

请以结构化的方式输出报告。
```

---

## 报告输出格式

### Markdown 报告结构

```markdown
# Git AI 配置分析报告

## 执行摘要

- **分析时间**: 2026-02-02 10:30:00
- **仓库路径**: C:\gdconfig
- **分析目录**: fo/
- **提交范围**: bugfix..HEAD
- **总提交数**: 15
- **变更配置数**: 8
- **功能新增配置数**: 3

## AI 分析总结

{AI 生成的整体总结}

## 功能新增配置（重点关注）

### 1. user_level_config

- **文件**: fo/user_level_config.csv
- **变更类型**: 新增
- **AI 分析**:
  - **摘要**: 新增用户等级配置表，支持新的等级系统
  - **目的**: 支持新的用户等级功能上线
  - **影响范围**: 用户系统、奖励系统
  - **同步建议**: 需要同步到测试和生产环境
  - **优先级**: 高

### 2. reward_config

- **文件**: fo/reward_config.csv
- **变更类型**: 修改
- **AI 分析**:
  - **摘要**: 新增 5 条奖励配置项
  - **目的**: 支持春节活动奖励
  - **影响范围**: 奖励系统、活动系统
  - **同步建议**: 需要同步到测试环境
  - **优先级**: 中

## 参数调整配置

{列出参数调整类型的配置变更}

## Bug 修复配置

{列出 Bug 修复类型的配置变更}

## 详细变更记录

{按时间顺序的详细提交记录}

## 行动建议

1. [ ] 同步 user_level_config 到生产环境
2. [ ] 验证 reward_config 的奖励数值
3. [ ] 检查 xxx_config 的兼容性

---

*报告由 Git AI 配置分析器自动生成*
```

---

## 实现步骤

### 阶段一：基础框架搭建

1. **创建项目结构**
   - 初始化项目目录
   - 创建配置文件和依赖管理

2. **复用 Git 操作模块**
   - 复用 `config-agent` 的 `git_repo_manager.py`
   - 添加差异内容提取功能

3. **实现差异提取器**
   - 解析 git diff 输出
   - 提取新增/删除行
   - 保留上下文信息

### 阶段二：AI 分析功能

4. **实现 AI 分析引擎**
   - 集成 AI API（OpenAI/本地模型）
   - 设计分析提示词
   - 解析 AI 返回结果

5. **实现配置分类器**
   - 根据 AI 分析结果分类
   - 识别功能新增配置
   - 计算置信度

### 阶段三：报告生成

6. **扩展报告生成器**
   - 增加 AI 分析结果展示
   - 生成功能新增配置专项报告
   - 生成行动建议

7. **实现主程序**
   - 整合所有模块
   - 提供命令行接口
   - 支持多种输出格式

### 阶段四：测试与优化

8. **编写测试用例**
   - 单元测试
   - 集成测试
   - AI 分析准确性验证

9. **优化与文档**
   - 性能优化
   - 编写使用文档
   - 创建示例脚本

---

## 依赖项

### Python 依赖

```txt
# requirements.txt

# AI 相关
openai>=1.0.0           # OpenAI API 客户端
tiktoken>=0.5.0         # Token 计算

# 现有依赖（复用）
gitpython>=3.1.0        # Git 操作（可选，目前用 subprocess）

# 工具库
dataclasses-json>=0.6.0 # 数据类 JSON 序列化
pydantic>=2.0.0         # 数据验证
python-dotenv>=1.0.0    # 环境变量管理

# 输出格式
jinja2>=3.0.0           # 模板引擎（用于报告生成）

# 测试
pytest>=7.0.0
pytest-cov>=4.0.0
```

### 环境变量

```env
# .env.example

# AI 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，用于代理

# 或使用本地模型
# AI_MODEL_TYPE=local
# LOCAL_MODEL_URL=http://localhost:11434/api/generate

# Git 配置
DEFAULT_REPO_PATH=C:\gdconfig
DEFAULT_TARGET_DIR=fo/
DEFAULT_BASE_BRANCH=bugfix
```

---

## 使用示例

### 命令行使用

```bash
# 基本使用
python src/main.py

# 指定参数
python src/main.py --repo-path "C:\gdconfig" --target-dir "fo/" --base-branch "bugfix"

# 指定输出格式
python src/main.py --format markdown --output "report.md"

# 使用特定 AI 模型
python src/main.py --ai-model "gpt-4" --include-diff
```

### 脚本使用

```batch
@echo off
REM quick_analyze.bat - 快速分析脚本

cd /d "%~dp0.."

python src\main.py ^
    --repo-path "C:\gdconfig" ^
    --target-dir "fo/" ^
    --format markdown ^
    --output "reports\ai_analysis_%date:~0,4%%date:~5,2%%date:~8,2%.md"

echo 分析报告已生成！
pause
```

---

## 注意事项

1. **AI API 成本**
   - 每次分析会调用 AI API，需注意 token 消耗
   - 可以设置批量分析来减少 API 调用次数
   - 建议使用 gpt-3.5-turbo 进行日常分析，重要分析使用 gpt-4

2. **敏感信息处理**
   - 确保不将敏感配置内容发送给外部 AI 服务
   - 可以考虑使用本地部署的模型
   - 对敏感字段进行脱敏处理

3. **性能考虑**
   - 大量文件变更时，考虑分批处理
   - 设置最大差异行数限制
   - 缓存 AI 分析结果避免重复分析

4. **准确性验证**
   - AI 分析结果仅供参考，最终需人工确认
   - 建议对高优先级变更进行人工复核
   - 持续优化提示词以提高准确性

---

## 后续扩展

1. **Web 界面**：提供可视化的配置变更分析界面
2. **CI/CD 集成**：集成到持续集成流程，自动分析每次提交
3. **历史趋势**：分析配置变更的历史趋势
4. **配置依赖分析**：分析配置之间的依赖关系
5. **自动同步建议**：根据分析结果自动生成同步脚本

---

## 总结

本项目基于现有的 `config-agent` 项目进行扩展，核心新增功能是 **AI 智能分析**。通过 AI 分析，可以自动判断配置变更的类型和目的，特别是识别出**功能新增配置**，帮助开发者在开发过程中快速了解需要关注的配置变更，提高配置管理的效率和准确性。

---

*文档创建时间: 2026-02-02*
*项目参考: C:\ADHD_agent\config-agent*
