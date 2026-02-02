"""
ChangeAnalyzer 单元测试
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from change_analyzer import ChangeAnalyzer, TableChange
from git_repo_manager import GitRepoManager, CommitInfo, FileChange


class TestChangeAnalyzer(unittest.TestCase):
    """ChangeAnalyzer 测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟的 GitRepoManager
        self.mock_git_manager = Mock(spec=GitRepoManager)
        self.analyzer = ChangeAnalyzer(
            self.mock_git_manager,
            target_dir="fo/"
        )
    
    def test_extract_table_name(self):
        """测试提取表名"""
        test_cases = [
            ("fo/user_config.csv", "user_config"),
            ("fo/item_config.json", "item_config"),
            ("fo/subdir/level_config.yaml", "level_config"),
            ("fo/test_table_v1.csv", "test_table_v1"),
        ]
        
        for file_path, expected_name in test_cases:
            result = self.analyzer._extract_table_name(file_path)
            self.assertEqual(result, expected_name)
            print(f"✓ {file_path} -> {result}")
    
    def test_group_by_change_type(self):
        """测试按变更类型分组"""
        # 创建测试数据
        table_changes = {
            "table1": TableChange(
                table_name="table1",
                file_path="fo/table1.csv",
                change_type="A",
                commits=[]
            ),
            "table2": TableChange(
                table_name="table2",
                file_path="fo/table2.csv",
                change_type="M",
                commits=[]
            ),
            "table3": TableChange(
                table_name="table3",
                file_path="fo/table3.csv",
                change_type="M",
                commits=[]
            ),
            "table4": TableChange(
                table_name="table4",
                file_path="fo/table4.csv",
                change_type="D",
                commits=[]
            ),
        }
        
        grouped = self.analyzer.group_by_change_type(table_changes)
        
        # 验证分组
        self.assertEqual(len(grouped['A']), 1)
        self.assertEqual(len(grouped['M']), 2)
        self.assertEqual(len(grouped['D']), 1)
        self.assertEqual(len(grouped['R']), 0)
        
        print(f"✓ 新增: {len(grouped['A'])} 个")
        print(f"✓ 修改: {len(grouped['M'])} 个")
        print(f"✓ 删除: {len(grouped['D'])} 个")
    
    def test_analyze_changes_empty(self):
        """测试分析空变更"""
        # 模拟返回空结果
        self.mock_git_manager.get_commits.return_value = []
        self.mock_git_manager.get_changed_files.return_value = []
        
        result = self.analyzer.analyze_changes("main..HEAD")
        
        self.assertEqual(len(result), 0)
        print("✓ 空变更测试通过")
    
    def test_analyze_changes_with_data(self):
        """测试分析有变更的情况"""
        # 创建模拟提交
        mock_commits = [
            CommitInfo(
                hash="abc123",
                time="2026-02-02 10:00:00",
                author="dev1",
                message="更新配置"
            )
        ]
        
        # 创建模拟文件变更
        mock_file_changes = [
            FileChange(
                change_type="M",
                file_path="fo/user_config.csv"
            ),
            FileChange(
                change_type="A",
                file_path="fo/new_config.json"
            )
        ]
        
        # 创建模拟提交文件
        mock_commit_files = [
            FileChange(
                change_type="M",
                file_path="fo/user_config.csv"
            )
        ]
        
        # 配置模拟对象
        self.mock_git_manager.get_commits.return_value = mock_commits
        self.mock_git_manager.get_changed_files.return_value = mock_file_changes
        self.mock_git_manager.get_commit_files.return_value = mock_commit_files
        
        result = self.analyzer.analyze_changes("main..HEAD")
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertIn("user_config", result)
        self.assertIn("new_config", result)
        
        print(f"✓ 分析到 {len(result)} 个表变更")
        for table_name, table_change in result.items():
            print(f"  - {table_name}: {table_change.change_type}")


class TestTableChange(unittest.TestCase):
    """TableChange 数据类测试"""
    
    def test_create_table_change(self):
        """测试创建 TableChange 对象"""
        commits = [
            CommitInfo(
                hash="abc123",
                time="2026-02-02 10:00:00",
                author="dev1",
                message="更新"
            )
        ]
        
        table_change = TableChange(
            table_name="user_config",
            file_path="fo/user_config.csv",
            change_type="M",
            commits=commits
        )
        
        self.assertEqual(table_change.table_name, "user_config")
        self.assertEqual(table_change.file_path, "fo/user_config.csv")
        self.assertEqual(table_change.change_type, "M")
        self.assertEqual(len(table_change.commits), 1)
        print("✓ TableChange 对象创建成功")


if __name__ == "__main__":
    unittest.main(verbosity=2)
