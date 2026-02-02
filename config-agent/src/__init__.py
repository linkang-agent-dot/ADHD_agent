"""
Git 配置变更检查工具
"""

__version__ = "1.0.0"
__author__ = "ADHD Agent Team"
__description__ = "检查 Git 仓库中配置文件的变更记录"

from .config import CheckConfig
from .git_repo_manager import GitRepoManager, CommitInfo, FileChange
from .change_analyzer import ChangeAnalyzer, TableChange
from .report_generator import ReportGenerator

__all__ = [
    "CheckConfig",
    "GitRepoManager",
    "CommitInfo",
    "FileChange",
    "ChangeAnalyzer",
    "TableChange",
    "ReportGenerator",
]
