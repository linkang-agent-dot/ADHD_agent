"""
变更分析器 - 分析文件变更并提取表信息
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

from git_repo_manager import CommitInfo, FileChange, GitRepoManager


@dataclass
class TableChange:
    """配置表变更信息"""
    table_name: str
    file_path: str
    change_type: str  # A=新增, M=修改, D=删除, R=重命名
    commits: List[CommitInfo] = field(default_factory=list)
    old_path: str = None  # 重命名时的旧路径


class ChangeAnalyzer:
    """变更分析器"""
    
    def __init__(self, git_manager: GitRepoManager, target_dir: str = "fo/"):
        """
        初始化变更分析器
        
        Args:
            git_manager: Git 仓库管理器
            target_dir: 目标目录
        """
        self.git_manager = git_manager
        self.target_dir = target_dir
    
    def analyze_changes(
        self,
        commit_range: str
    ) -> Dict[str, TableChange]:
        """
        分析变更，提取配置表信息
        
        Args:
            commit_range: 提交范围
            
        Returns:
            表名到变更信息的映射
        """
        # 1. 获取所有提交
        commits = self.git_manager.get_commits(commit_range)
        
        # 2. 获取所有变更文件（只关注 target_dir）
        all_changes = self.git_manager.get_changed_files(
            commit_range,
            self.target_dir
        )
        
        # 3. 按表名分组
        table_changes: Dict[str, TableChange] = {}
        
        # 创建文件路径到提交的映射
        file_to_commits: Dict[str, List[CommitInfo]] = defaultdict(list)
        
        # 遍历每个提交，建立文件到提交的映射
        for commit in commits:
            commit_files = self.git_manager.get_commit_files(commit.hash)
            for file_change in commit_files:
                # 只关注目标目录下的文件
                if file_change.file_path.startswith(self.target_dir):
                    file_to_commits[file_change.file_path].append(commit)
        
        # 4. 处理每个变更文件
        for file_change in all_changes:
            # 提取表名
            table_name = self._extract_table_name(file_change.file_path)
            
            # 如果该表已存在，合并信息
            if table_name in table_changes:
                # 合并提交信息
                existing_commits = {c.hash for c in table_changes[table_name].commits}
                for commit in file_to_commits.get(file_change.file_path, []):
                    if commit.hash not in existing_commits:
                        table_changes[table_name].commits.append(commit)
                
                # 更新变更类型（优先级：D > A > M）
                if file_change.change_type == 'D':
                    table_changes[table_name].change_type = 'D'
                elif (file_change.change_type == 'A' and 
                      table_changes[table_name].change_type == 'M'):
                    table_changes[table_name].change_type = 'A'
            else:
                # 创建新的表变更记录
                table_changes[table_name] = TableChange(
                    table_name=table_name,
                    file_path=file_change.file_path,
                    change_type=file_change.change_type,
                    commits=file_to_commits.get(file_change.file_path, []).copy(),
                    old_path=file_change.old_path
                )
        
        # 5. 按时间排序每个表的提交记录
        for table_change in table_changes.values():
            table_change.commits.sort(key=lambda c: c.time)
        
        return table_changes
    
    def _extract_table_name(self, file_path: str) -> str:
        """
        从文件路径提取表名
        
        Args:
            file_path: 文件路径，如 'fo/user_config.csv'
            
        Returns:
            表名，如 'user_config'
        """
        # 获取文件名（不含目录）
        filename = Path(file_path).name
        
        # 去除扩展名
        table_name = Path(filename).stem
        
        # 处理可能的版本号后缀，如 'table_v1' -> 'table'
        # 这里简单处理，可根据实际情况调整
        # if '_v' in table_name:
        #     table_name = table_name.rsplit('_v', 1)[0]
        
        return table_name
    
    def group_by_change_type(
        self,
        table_changes: Dict[str, TableChange]
    ) -> Dict[str, List[TableChange]]:
        """
        按变更类型分组
        
        Args:
            table_changes: 表变更信息
            
        Returns:
            变更类型到表列表的映射
        """
        grouped: Dict[str, List[TableChange]] = {
            'A': [],  # 新增
            'M': [],  # 修改
            'D': [],  # 删除
            'R': [],  # 重命名
        }
        
        for table_change in table_changes.values():
            change_type = table_change.change_type
            if change_type in grouped:
                grouped[change_type].append(table_change)
            else:
                # 其他类型归入修改
                grouped['M'].append(table_change)
        
        # 按表名排序
        for changes_list in grouped.values():
            changes_list.sort(key=lambda x: x.table_name)
        
        return grouped
