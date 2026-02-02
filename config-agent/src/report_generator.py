"""
报告生成器 - 生成各种格式的检查报告
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from change_analyzer import TableChange


class ReportGenerator:
    """报告生成器"""
    
    def __init__(
        self,
        repo_path: str,
        target_dir: str,
        branch_name: str,
        base_branch: str,
        commit_range: str
    ):
        """
        初始化报告生成器
        
        Args:
            repo_path: 仓库路径
            target_dir: 目标目录
            branch_name: 当前分支名
            base_branch: 基准分支名
            commit_range: 提交范围
        """
        self.repo_path = repo_path
        self.target_dir = target_dir
        self.branch_name = branch_name
        self.base_branch = base_branch
        self.commit_range = commit_range
        self.check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_console_report(
        self,
        table_changes: Dict[str, TableChange],
        grouped_changes: Dict[str, List[TableChange]]
    ) -> str:
        """
        生成控制台文本报告
        
        Args:
            table_changes: 表变更信息
            grouped_changes: 按类型分组的变更
            
        Returns:
            报告文本
        """
        lines = []
        
        # 标题
        lines.append("=" * 60)
        lines.append("Git 配置变更检查报告")
        lines.append("=" * 60)
        
        # 摘要信息
        lines.append(f"检查时间: {self.check_time}")
        lines.append(f"仓库路径: {self.repo_path}")
        lines.append(f"检查目录: {self.target_dir}")
        lines.append(f"当前分支: {self.branch_name}")
        lines.append(f"比较基准: {self.base_branch}")
        lines.append(f"提交范围: {self.commit_range}")
        
        # 统计提交数量
        all_commits = set()
        for table_change in table_changes.values():
            for commit in table_change.commits:
                all_commits.add(commit.hash)
        lines.append(f"提交数量: {len(all_commits)}")
        
        lines.append("")
        lines.append("-" * 60)
        lines.append(f"变更表汇总 (共 {len(table_changes)} 个表)")
        lines.append("-" * 60)
        lines.append("")
        
        # 按类型显示变更
        change_type_names = {
            'A': '新增',
            'M': '修改',
            'D': '删除',
            'R': '重命名'
        }
        
        for change_type, type_name in change_type_names.items():
            changes = grouped_changes.get(change_type, [])
            if not changes:
                continue
            
            lines.append(f"【{type_name}】({len(changes)}个)")
            for table_change in changes:
                if change_type == 'R' and table_change.old_path:
                    lines.append(
                        f"  - {table_change.table_name} "
                        f"({table_change.old_path} -> {table_change.file_path})"
                    )
                else:
                    lines.append(f"  - {table_change.table_name} ({table_change.file_path})")
            lines.append("")
        
        # 详细提交记录
        lines.append("-" * 60)
        lines.append("详细提交记录")
        lines.append("-" * 60)
        lines.append("")
        
        # 收集所有提交并按时间排序
        commit_to_tables: Dict[str, List[TableChange]] = {}
        for table_change in table_changes.values():
            for commit in table_change.commits:
                if commit.hash not in commit_to_tables:
                    commit_to_tables[commit.hash] = []
                commit_to_tables[commit.hash].append(table_change)
        
        # 按时间排序提交
        sorted_commits = []
        for table_change in table_changes.values():
            for commit in table_change.commits:
                if commit not in sorted_commits:
                    sorted_commits.append(commit)
        sorted_commits.sort(key=lambda c: c.time)
        
        # 显示每个提交
        for idx, commit in enumerate(sorted_commits, 1):
            # 提交信息
            commit_time = commit.time.split()[0] + " " + commit.time.split()[1][:5]
            lines.append(f"[{idx}] {commit.hash[:7]} - {commit_time} - {commit.author}")
            lines.append(f"    消息: {commit.message}")
            
            # 该提交涉及的文件
            tables = commit_to_tables.get(commit.hash, [])
            if tables:
                lines.append("    变更:")
                for table in tables:
                    change_symbol = {
                        'A': '+',
                        'M': 'M',
                        'D': '-',
                        'R': 'R'
                    }.get(table.change_type, '?')
                    lines.append(f"          {change_symbol} {table.file_path}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def generate_markdown_report(
        self,
        table_changes: Dict[str, TableChange],
        grouped_changes: Dict[str, List[TableChange]]
    ) -> str:
        """
        生成 Markdown 格式报告
        
        Args:
            table_changes: 表变更信息
            grouped_changes: 按类型分组的变更
            
        Returns:
            Markdown 文本
        """
        lines = []
        
        # 标题
        lines.append("# Git 配置变更检查报告")
        lines.append("")
        
        # 摘要信息
        lines.append("## 摘要信息")
        lines.append("")
        lines.append(f"- **检查时间**: {self.check_time}")
        lines.append(f"- **仓库路径**: `{self.repo_path}`")
        lines.append(f"- **检查目录**: `{self.target_dir}`")
        lines.append(f"- **当前分支**: `{self.branch_name}`")
        lines.append(f"- **比较基准**: `{self.base_branch}`")
        lines.append(f"- **提交范围**: `{self.commit_range}`")
        
        # 统计提交数量
        all_commits = set()
        for table_change in table_changes.values():
            for commit in table_change.commits:
                all_commits.add(commit.hash)
        lines.append(f"- **提交数量**: {len(all_commits)}")
        lines.append(f"- **变更表数**: {len(table_changes)}")
        lines.append("")
        
        # 变更表汇总
        lines.append("## 变更表汇总")
        lines.append("")
        
        change_type_names = {
            'A': '新增',
            'M': '修改',
            'D': '删除',
            'R': '重命名'
        }
        
        for change_type, type_name in change_type_names.items():
            changes = grouped_changes.get(change_type, [])
            if not changes:
                continue
            
            lines.append(f"### {type_name} ({len(changes)}个)")
            lines.append("")
            for table_change in changes:
                if change_type == 'R' and table_change.old_path:
                    lines.append(
                        f"- **{table_change.table_name}**: "
                        f"`{table_change.old_path}` → `{table_change.file_path}`"
                    )
                else:
                    lines.append(f"- **{table_change.table_name}**: `{table_change.file_path}`")
            lines.append("")
        
        # 详细提交记录
        lines.append("## 详细提交记录")
        lines.append("")
        
        # 收集并排序提交
        commit_to_tables: Dict[str, List[TableChange]] = {}
        for table_change in table_changes.values():
            for commit in table_change.commits:
                if commit.hash not in commit_to_tables:
                    commit_to_tables[commit.hash] = []
                commit_to_tables[commit.hash].append(table_change)
        
        sorted_commits = []
        for table_change in table_changes.values():
            for commit in table_change.commits:
                if commit not in sorted_commits:
                    sorted_commits.append(commit)
        sorted_commits.sort(key=lambda c: c.time)
        
        # 显示每个提交
        for idx, commit in enumerate(sorted_commits, 1):
            commit_time = commit.time.split()[0] + " " + commit.time.split()[1][:5]
            lines.append(f"### [{idx}] {commit.message}")
            lines.append("")
            lines.append(f"- **提交**: `{commit.hash[:7]}`")
            lines.append(f"- **时间**: {commit_time}")
            lines.append(f"- **作者**: {commit.author}")
            
            # 该提交涉及的文件
            tables = commit_to_tables.get(commit.hash, [])
            if tables:
                lines.append("- **变更文件**:")
                for table in tables:
                    change_symbol = {
                        'A': '➕',
                        'M': '✏️',
                        'D': '➖',
                        'R': '🔄'
                    }.get(table.change_type, '❓')
                    lines.append(f"  - {change_symbol} `{table.file_path}`")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json_report(
        self,
        table_changes: Dict[str, TableChange],
        grouped_changes: Dict[str, List[TableChange]]
    ) -> str:
        """
        生成 JSON 格式报告
        
        Args:
            table_changes: 表变更信息
            grouped_changes: 按类型分组的变更
            
        Returns:
            JSON 文本
        """
        # 统计提交数量
        all_commits_set = set()
        for table_change in table_changes.values():
            for commit in table_change.commits:
                all_commits_set.add(commit.hash)
        
        # 构建报告数据
        report_data = {
            "summary": {
                "check_time": self.check_time,
                "repo_path": self.repo_path,
                "target_dir": self.target_dir,
                "branch_name": self.branch_name,
                "base_branch": self.base_branch,
                "commit_range": self.commit_range,
                "total_commits": len(all_commits_set),
                "total_tables": len(table_changes)
            },
            "changes_by_type": {},
            "tables": [],
            "commits": []
        }
        
        # 按类型分组的变更
        for change_type, changes in grouped_changes.items():
            if not changes:
                continue
            report_data["changes_by_type"][change_type] = [
                {
                    "table_name": tc.table_name,
                    "file_path": tc.file_path,
                    "old_path": tc.old_path
                }
                for tc in changes
            ]
        
        # 所有表的详细信息
        for table_change in table_changes.values():
            report_data["tables"].append({
                "table_name": table_change.table_name,
                "file_path": table_change.file_path,
                "change_type": table_change.change_type,
                "old_path": table_change.old_path,
                "commits": [
                    {
                        "hash": c.hash,
                        "time": c.time,
                        "author": c.author,
                        "message": c.message
                    }
                    for c in table_change.commits
                ]
            })
        
        # 所有提交的详细信息
        commit_to_tables: Dict[str, List[str]] = {}
        for table_change in table_changes.values():
            for commit in table_change.commits:
                if commit.hash not in commit_to_tables:
                    commit_to_tables[commit.hash] = []
                commit_to_tables[commit.hash].append(table_change.file_path)
        
        sorted_commits = []
        for table_change in table_changes.values():
            for commit in table_change.commits:
                if commit not in sorted_commits:
                    sorted_commits.append(commit)
        sorted_commits.sort(key=lambda c: c.time)
        
        for commit in sorted_commits:
            report_data["commits"].append({
                "hash": commit.hash,
                "time": commit.time,
                "author": commit.author,
                "message": commit.message,
                "changed_files": commit_to_tables.get(commit.hash, [])
            })
        
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    
    def save_report(self, content: str, output_path: str) -> None:
        """
        保存报告到文件
        
        Args:
            content: 报告内容
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding='utf-8')
