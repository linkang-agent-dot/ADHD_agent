# 贡献指南

感谢你对 Git AI 配置分析器项目的关注！

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 先在 [Issues](../../issues) 中搜索是否已有相关问题
2. 如果没有，创建新的 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤（如果是 bug）
   - 期望的行为
   - 实际的行为
   - 环境信息（操作系统、Python 版本等）

### 提交代码

1. **Fork 项目**

2. **创建特性分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **编写代码**
   - 遵循现有代码风格
   - 添加必要的注释
   - 更新相关文档

4. **运行测试**
   ```bash
   python -m pytest tests/ -v
   ```

5. **提交更改**
   ```bash
   git commit -m "添加某某功能"
   ```

6. **推送到 Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **创建 Pull Request**

## 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/git-ai-config-analyzer.git
cd git-ai-config-analyzer
```

### 2. 安装依赖
```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

## 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- 使用 4 空格缩进
- 类名使用 PascalCase
- 函数名使用 snake_case
- 常量使用 UPPER_CASE

### 文档字符串

使用 Google 风格的文档字符串：

```python
def function_name(param1: str, param2: int) -> bool:
    """
    函数的简短描述
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
        
    Returns:
        返回值描述
        
    Raises:
        ValueError: 异常情况描述
    """
    pass
```

### 提交信息

提交信息格式：

```
<type>: <subject>

<body>

<footer>
```

类型（type）：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat: 添加配置缓存功能

实现了配置分析结果的缓存机制，避免重复分析相同的配置变更。

Closes #123
```

## 测试

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 运行单个测试文件
```bash
python -m pytest tests/test_ai_analyzer.py -v
```

### 生成覆盖率报告
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### 编写测试

测试文件命名：`test_<module_name>.py`

```python
import pytest

def test_something():
    """测试某个功能"""
    # Arrange
    expected = "result"
    
    # Act
    actual = some_function()
    
    # Assert
    assert actual == expected
```

## 项目结构

```
git-ai-config-analyzer/
├── src/                    # 源代码
│   ├── config.py          # 配置管理
│   ├── git_repo_manager.py # Git 操作
│   ├── diff_extractor.py  # 差异提取
│   ├── ai_analyzer.py     # AI 分析
│   ├── report_generator.py # 报告生成
│   └── main.py            # 主入口
├── tests/                 # 测试代码
├── scripts/               # 辅助脚本
├── prompts/              # 提示词模板
└── reports/              # 报告输出
```

## 发布流程

1. 更新版本号
   - `src/__init__.py`
   - `setup.py`

2. 更新 CHANGELOG.md

3. 创建标签
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

## 需要帮助？

- 📧 Email: your.email@example.com
- 💬 Issues: [项目 Issues](../../issues)

## 行为准则

请遵守以下准则：

- 尊重他人
- 欢迎新手
- 建设性讨论
- 专注于项目目标

---

再次感谢你的贡献！🎉
