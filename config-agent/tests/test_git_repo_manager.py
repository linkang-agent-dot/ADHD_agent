"""
GitRepoManager 单元测试
"""
import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from git_repo_manager import GitRepoManager, CommitInfo, FileChange


class TestGitRepoManager(unittest.TestCase):
    """GitRepoManager 测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 注意: 需要根据实际环境修改路径
        self.test_repo_path = r"C:\gdconfig"
        
    def test_invalid_repo_path(self):
        """测试无效的仓库路径"""
        with self.assertRaises(ValueError):
            GitRepoManager("C:\\nonexistent_repo")
    
    def test_not_git_repo(self):
        """测试非 Git 仓库路径"""
        with self.assertRaises(ValueError):
            GitRepoManager("C:\\Windows")
    
    def test_valid_repo(self):
        """测试有效的仓库"""
        try:
            manager = GitRepoManager(self.test_repo_path)
            self.assertIsNotNone(manager)
        except ValueError:
            self.skipTest(f"测试仓库不存在: {self.test_repo_path}")
    
    def test_get_current_branch(self):
        """测试获取当前分支"""
        try:
            manager = GitRepoManager(self.test_repo_path)
            branch = manager.get_current_branch()
            self.assertIsInstance(branch, str)
            self.assertTrue(len(branch) > 0)
            print(f"当前分支: {branch}")
        except ValueError:
            self.skipTest(f"测试仓库不存在: {self.test_repo_path}")
    
    def test_get_all_branches(self):
        """测试获取所有分支"""
        try:
            manager = GitRepoManager(self.test_repo_path)
            branches = manager.get_all_branches()
            self.assertIsInstance(branches, list)
            self.assertTrue(len(branches) > 0)
            print(f"分支列表: {branches}")
        except ValueError:
            self.skipTest(f"测试仓库不存在: {self.test_repo_path}")
    
    def test_get_commits(self):
        """测试获取提交记录"""
        try:
            manager = GitRepoManager(self.test_repo_path)
            commits = manager.get_commits("HEAD~5..HEAD")
            self.assertIsInstance(commits, list)
            
            if commits:
                # 检查第一个提交的结构
                commit = commits[0]
                self.assertIsInstance(commit, CommitInfo)
                self.assertTrue(len(commit.hash) > 0)
                self.assertTrue(len(commit.message) > 0)
                print(f"最新提交: {commit.hash[:7]} - {commit.message}")
        except ValueError:
            self.skipTest(f"测试仓库不存在: {self.test_repo_path}")
    
    def test_get_changed_files(self):
        """测试获取变更文件"""
        try:
            manager = GitRepoManager(self.test_repo_path)
            changes = manager.get_changed_files("HEAD~5..HEAD", "fo/")
            self.assertIsInstance(changes, list)
            
            if changes:
                # 检查第一个变更的结构
                change = changes[0]
                self.assertIsInstance(change, FileChange)
                self.assertIn(change.change_type, ['A', 'M', 'D', 'R'])
                self.assertTrue(change.file_path.startswith("fo/"))
                print(f"变更文件: {change.change_type} {change.file_path}")
        except ValueError:
            self.skipTest(f"测试仓库不存在: {self.test_repo_path}")


class TestCommitInfo(unittest.TestCase):
    """CommitInfo 数据类测试"""
    
    def test_create_commit_info(self):
        """测试创建 CommitInfo 对象"""
        commit = CommitInfo(
            hash="abc123",
            time="2026-02-02 10:00:00",
            author="developer",
            message="测试提交"
        )
        
        self.assertEqual(commit.hash, "abc123")
        self.assertEqual(commit.time, "2026-02-02 10:00:00")
        self.assertEqual(commit.author, "developer")
        self.assertEqual(commit.message, "测试提交")


class TestFileChange(unittest.TestCase):
    """FileChange 数据类测试"""
    
    def test_create_file_change(self):
        """测试创建 FileChange 对象"""
        change = FileChange(
            change_type="M",
            file_path="fo/config.csv"
        )
        
        self.assertEqual(change.change_type, "M")
        self.assertEqual(change.file_path, "fo/config.csv")
        self.assertIsNone(change.old_path)
    
    def test_create_rename_change(self):
        """测试创建重命名变更"""
        change = FileChange(
            change_type="R",
            file_path="fo/new_name.csv",
            old_path="fo/old_name.csv"
        )
        
        self.assertEqual(change.change_type, "R")
        self.assertEqual(change.file_path, "fo/new_name.csv")
        self.assertEqual(change.old_path, "fo/old_name.csv")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
