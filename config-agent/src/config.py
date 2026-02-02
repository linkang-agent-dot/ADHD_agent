"""
Git 配置变更检查工具 - 配置文件
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckConfig:
    """检查配置参数"""
    
    # Git 仓库路径
    repo_path: str = r"C:\gdconfig"
    
    # 目标检查目录
    target_dir: str = "fo/"
    
    # 基准分支
    base_branch: str = "main"
    
    # 比较分支（None 表示当前分支）
    compare_branch: Optional[str] = None
    
    # 提交范围（None 表示使用 base_branch..HEAD）
    commit_range: Optional[str] = None
    
    # 报告输出格式：console, markdown, json
    output_format: str = "console"
    
    # Markdown 报告输出路径
    markdown_output_path: str = "git_change_report.md"
    
    # JSON 报告输出路径
    json_output_path: str = "git_change_report.json"
    
    def get_commit_range(self) -> str:
        """获取提交范围"""
        if self.commit_range:
            return self.commit_range
        return f"{self.base_branch}..HEAD"
