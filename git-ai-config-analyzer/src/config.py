"""
Git AI 配置分析器 - 配置文件
"""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class AnalyzerConfig:
    """AI 配置分析器配置"""
    
    # Git 仓库路径
    repo_path: str = r"C:\gdconfig"
    
    # 目标检查目录
    target_dir: str = "fo/"
    
    # 基准分支
    base_branch: str = "bugfix"
    
    # 比较分支（None 表示当前分支）
    compare_branch: Optional[str] = None
    
    # 提交范围（None 表示使用 base_branch..HEAD）
    commit_range: Optional[str] = None
    
    # AI 模型配置
    ai_model: str = "gpt-4"
    ai_api_key: Optional[str] = None
    ai_base_url: Optional[str] = None
    
    # 分析选项
    include_diff_content: bool = True  # 是否包含差异内容
    max_diff_lines: int = 500          # 单文件最大差异行数
    
    # 输出配置
    output_format: str = "markdown"  # console, markdown, json, all
    output_path: str = "ai_config_analysis_report.md"
    json_output_path: str = "ai_config_analysis_report.json"
    
    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量获取 API Key
        if self.ai_api_key is None:
            self.ai_api_key = os.getenv("OPENAI_API_KEY")
        
        if self.ai_base_url is None:
            self.ai_base_url = os.getenv("OPENAI_BASE_URL")
    
    def get_commit_range(self) -> str:
        """获取提交范围"""
        if self.commit_range:
            return self.commit_range
        return f"{self.base_branch}..HEAD"
