"""
CheckConfig 单元测试
"""
import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CheckConfig


class TestCheckConfig(unittest.TestCase):
    """CheckConfig 测试用例"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = CheckConfig()
        
        self.assertEqual(config.repo_path, r"C:\gdconfig")
        self.assertEqual(config.target_dir, "fo/")
        self.assertEqual(config.base_branch, "main")
        self.assertIsNone(config.compare_branch)
        self.assertIsNone(config.commit_range)
        self.assertEqual(config.output_format, "console")
        
        print("✓ 默认配置测试通过")
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = CheckConfig(
            repo_path=r"D:\myrepo",
            target_dir="config/",
            base_branch="develop",
            compare_branch="feature",
            output_format="markdown"
        )
        
        self.assertEqual(config.repo_path, r"D:\myrepo")
        self.assertEqual(config.target_dir, "config/")
        self.assertEqual(config.base_branch, "develop")
        self.assertEqual(config.compare_branch, "feature")
        self.assertEqual(config.output_format, "markdown")
        
        print("✓ 自定义配置测试通过")
    
    def test_get_commit_range_default(self):
        """测试获取默认提交范围"""
        config = CheckConfig()
        commit_range = config.get_commit_range()
        
        self.assertEqual(commit_range, "main..HEAD")
        print(f"✓ 默认提交范围: {commit_range}")
    
    def test_get_commit_range_custom(self):
        """测试获取自定义提交范围"""
        config = CheckConfig(commit_range="develop..feature")
        commit_range = config.get_commit_range()
        
        self.assertEqual(commit_range, "develop..feature")
        print(f"✓ 自定义提交范围: {commit_range}")
    
    def test_output_paths(self):
        """测试输出路径配置"""
        config = CheckConfig(
            markdown_output_path="reports/my_report.md",
            json_output_path="reports/my_data.json"
        )
        
        self.assertEqual(config.markdown_output_path, "reports/my_report.md")
        self.assertEqual(config.json_output_path, "reports/my_data.json")
        
        print("✓ 输出路径配置测试通过")


if __name__ == "__main__":
    unittest.main(verbosity=2)
