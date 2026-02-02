# 测试文档

本目录包含项目的单元测试。

## 测试结构

```
tests/
├── __init__.py
├── test_config.py              # CheckConfig 配置类测试
├── test_git_repo_manager.py    # GitRepoManager 测试
├── test_change_analyzer.py     # ChangeAnalyzer 测试
└── README.md                   # 本文档
```

## 运行测试

### 运行所有测试

**Windows:**
```bash
scripts\run_tests.bat
```

**Linux/Mac:**
```bash
python -m unittest discover tests
```

### 运行单个测试文件

```bash
# 测试配置模块
python tests/test_config.py

# 测试 Git 仓库管理器
python tests/test_git_repo_manager.py

# 测试变更分析器
python tests/test_change_analyzer.py
```

### 运行特定测试类

```bash
python -m unittest tests.test_config.TestCheckConfig
```

### 运行特定测试方法

```bash
python -m unittest tests.test_config.TestCheckConfig.test_default_config
```

## 测试说明

### 1. test_config.py

测试配置类 `CheckConfig` 的功能：

- ✓ 默认配置值
- ✓ 自定义配置
- ✓ 提交范围计算
- ✓ 输出路径设置

**示例输出：**
```
test_default_config (__main__.TestCheckConfig) ... ok
test_custom_config (__main__.TestCheckConfig) ... ok
test_get_commit_range_default (__main__.TestCheckConfig) ... ok
test_get_commit_range_custom (__main__.TestCheckConfig) ... ok
```

### 2. test_git_repo_manager.py

测试 Git 仓库操作功能：

- ✓ 仓库路径验证
- ✓ 获取当前分支
- ✓ 获取所有分支
- ✓ 获取提交记录
- ✓ 获取变更文件
- ✓ CommitInfo 和 FileChange 数据类

**注意事项：**
- 需要有效的测试仓库路径
- 默认使用 `C:\gdconfig`
- 如果仓库不存在，部分测试会被跳过

### 3. test_change_analyzer.py

测试变更分析功能：

- ✓ 表名提取
- ✓ 按变更类型分组
- ✓ 空变更处理
- ✓ 有数据的变更分析
- ✓ TableChange 数据类

**使用 Mock 对象：**
此测试使用 `unittest.mock` 模拟 Git 操作，不需要实际的仓库。

## 测试覆盖率

运行测试覆盖率分析（需要安装 `coverage`）：

```bash
# 安装 coverage
pip install coverage

# 运行测试并收集覆盖率
coverage run -m unittest discover tests

# 查看覆盖率报告
coverage report

# 生成 HTML 报告
coverage html
```

## 添加新测试

### 测试模板

```python
import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from your_module import YourClass


class TestYourClass(unittest.TestCase):
    """YourClass 测试用例"""
    
    def setUp(self):
        """测试前准备"""
        pass
    
    def tearDown(self):
        """测试后清理"""
        pass
    
    def test_feature(self):
        """测试某个功能"""
        # 准备
        obj = YourClass()
        
        # 执行
        result = obj.some_method()
        
        # 断言
        self.assertEqual(result, expected_value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## 常见问题

### Q: 测试失败怎么办？

**A**: 检查以下几点：
1. 测试仓库路径是否正确
2. Git 是否已安装并在 PATH 中
3. 仓库是否有足够的提交记录
4. 是否有权限访问仓库

### Q: 如何调试测试？

**A**: 使用详细模式运行：
```bash
python -m unittest tests.test_config -v
```

或在测试代码中添加 print 语句。

### Q: 如何跳过某些测试？

**A**: 使用 `@unittest.skip` 装饰器：
```python
@unittest.skip("暂时跳过")
def test_something(self):
    pass
```

## 贡献指南

添加新功能时，请同时添加相应的测试：

1. 在 `tests/` 目录创建测试文件
2. 遵循命名规范：`test_<module_name>.py`
3. 每个测试方法以 `test_` 开头
4. 添加清晰的文档字符串
5. 确保所有测试通过后再提交

## 持续集成

项目可以集成到 CI/CD 流程中：

```yaml
# 示例：GitHub Actions
- name: Run tests
  run: |
    python -m unittest discover tests
```

---

更多信息请参考：
- [Python unittest 文档](https://docs.python.org/3/library/unittest.html)
- [项目 README](../README.md)
