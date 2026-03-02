"""
Git 仓库管理器测试
"""
import pytest
from pathlib import Path

from src.git_repo_manager import GitRepoManager, CommitInfo, FileChange


class TestGitRepoManager:
    """Git 仓库管理器测试类"""
    
    def test_validate_repo_invalid_path(self):
        """测试无效的仓库路径"""
        with pytest.raises(ValueError, match="仓库路径不存在"):
            GitRepoManager("C:\\nonexistent_path")
    
    def test_file_change_dataclass(self):
        """测试 FileChange 数据类"""
        change = FileChange(
            change_type="M",
            file_path="fo/test_config.csv"
        )
        assert change.change_type == "M"
        assert change.file_path == "fo/test_config.csv"
        assert change.old_path is None
    
    def test_commit_info_dataclass(self):
        """测试 CommitInfo 数据类"""
        commit = CommitInfo(
            hash="abc123",
            time="2026-02-02 10:00:00",
            author="Test User",
            message="Test commit"
        )
        assert commit.hash == "abc123"
        assert commit.author == "Test User"


# 注意：实际的 Git 操作测试需要真实的 Git 仓库
# 这里只测试数据结构和基础验证
