"""
差异内容提取器 - 提取配置文件的具体变更内容
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import re

from .git_repo_manager import GitRepoManager, CommitInfo, FileChange


@dataclass
class DiffContent:
    """差异内容"""
    file_path: str
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    context_lines: List[str] = field(default_factory=list)
    raw_diff: str = ""


@dataclass
class ConfigDiff:
    """配置变更详情"""
    file_path: str
    table_name: str
    change_type: str  # A/M/D/R
    diff_content: Optional[DiffContent] = None
    related_commits: List[CommitInfo] = field(default_factory=list)
    old_path: Optional[str] = None


class DiffExtractor:
    """差异内容提取器"""
    
    def __init__(self, git_manager: GitRepoManager, max_diff_lines: int = 500):
        """
        初始化差异提取器
        
        Args:
            git_manager: Git 仓库管理器
            max_diff_lines: 单文件最大差异行数
        """
        self.git_manager = git_manager
        self.max_diff_lines = max_diff_lines
    
    def extract_diff(self, commit_range: str, file_path: str) -> DiffContent:
        """
        提取单个文件的差异内容
        
        Args:
            commit_range: 提交范围
            file_path: 文件路径
            
        Returns:
            差异内容
        """
        try:
            raw_diff = self.git_manager.get_file_diff(commit_range, file_path)
        except RuntimeError:
            # 文件可能是新增或删除的
            raw_diff = ""
        
        return self.parse_diff_output(raw_diff, file_path)
    
    def parse_diff_output(self, diff_text: str, file_path: str) -> DiffContent:
        """
        解析 git diff 输出
        
        Args:
            diff_text: git diff 输出文本
            file_path: 文件路径
            
        Returns:
            解析后的差异内容
        """
        added_lines = []
        removed_lines = []
        context_lines = []
        
        if not diff_text:
            return DiffContent(
                file_path=file_path,
                added_lines=added_lines,
                removed_lines=removed_lines,
                context_lines=context_lines,
                raw_diff=diff_text
            )
        
        lines = diff_text.split("\n")
        line_count = 0
        in_diff_body = False
        
        for line in lines:
            # 跳过 diff 头部信息
            if line.startswith("diff --git") or line.startswith("index "):
                continue
            if line.startswith("---") or line.startswith("+++"):
                in_diff_body = True
                continue
            if line.startswith("@@"):
                in_diff_body = True
                continue
            
            if not in_diff_body:
                continue
            
            line_count += 1
            if line_count > self.max_diff_lines:
                break
            
            if line.startswith("+") and not line.startswith("+++"):
                # 新增行
                added_lines.append(line[1:])  # 去掉 + 号
            elif line.startswith("-") and not line.startswith("---"):
                # 删除行
                removed_lines.append(line[1:])  # 去掉 - 号
            elif line.startswith(" "):
                # 上下文行
                context_lines.append(line[1:])
        
        return DiffContent(
            file_path=file_path,
            added_lines=added_lines,
            removed_lines=removed_lines,
            context_lines=context_lines,
            raw_diff=diff_text[:5000] if len(diff_text) > 5000 else diff_text  # 限制原始 diff 大小
        )
    
    def extract_all_diffs(
        self,
        commit_range: str,
        target_dir: str,
        file_changes: List[FileChange],
        commits: List[CommitInfo]
    ) -> List[ConfigDiff]:
        """
        提取所有配置文件的差异内容
        
        Args:
            commit_range: 提交范围
            target_dir: 目标目录
            file_changes: 文件变更列表
            commits: 提交列表
            
        Returns:
            配置差异列表
        """
        config_diffs = []
        
        # 建立文件路径到提交的映射
        file_to_commits = self._build_file_commit_map(commits, target_dir)
        
        for file_change in file_changes:
            # 提取表名
            table_name = self._extract_table_name(file_change.file_path)
            
            # 提取差异内容
            diff_content = None
            if file_change.change_type != 'D':  # 删除的文件无法获取 diff
                diff_content = self.extract_diff(commit_range, file_change.file_path)
            
            # 获取相关提交
            related_commits = file_to_commits.get(file_change.file_path, [])
            
            config_diffs.append(ConfigDiff(
                file_path=file_change.file_path,
                table_name=table_name,
                change_type=file_change.change_type,
                diff_content=diff_content,
                related_commits=related_commits,
                old_path=file_change.old_path
            ))
        
        return config_diffs
    
    def _build_file_commit_map(
        self,
        commits: List[CommitInfo],
        target_dir: str
    ) -> dict:
        """
        建立文件路径到提交的映射
        
        Args:
            commits: 提交列表
            target_dir: 目标目录
            
        Returns:
            文件路径到提交列表的映射
        """
        file_to_commits = {}
        
        for commit in commits:
            commit_files = self.git_manager.get_commit_files(commit.hash)
            for file_change in commit_files:
                if file_change.file_path.startswith(target_dir):
                    if file_change.file_path not in file_to_commits:
                        file_to_commits[file_change.file_path] = []
                    file_to_commits[file_change.file_path].append(commit)
        
        return file_to_commits
    
    def _extract_table_name(self, file_path: str) -> str:
        """
        从文件路径提取表名
        
        Args:
            file_path: 文件路径
            
        Returns:
            表名
        """
        filename = Path(file_path).name
        table_name = Path(filename).stem
        return table_name
