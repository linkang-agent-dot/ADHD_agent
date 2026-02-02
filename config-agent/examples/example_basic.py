"""
基本使用示例 - 检查配置变更
"""
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CheckConfig
from git_repo_manager import GitRepoManager
from change_analyzer import ChangeAnalyzer
from report_generator import ReportGenerator


def example_basic_check():
    """基本检查示例"""
    print("=" * 60)
    print("示例 1: 基本配置变更检查")
    print("=" * 60)
    print()
    
    # 创建配置
    config = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        base_branch="main"
    )
    
    try:
        # 1. 初始化 Git 管理器
        print(f"连接仓库: {config.repo_path}")
        git_manager = GitRepoManager(config.repo_path)
        
        # 2. 获取当前分支
        current_branch = git_manager.get_current_branch()
        print(f"当前分支: {current_branch}")
        print()
        
        # 3. 创建分析器并分析
        analyzer = ChangeAnalyzer(git_manager, config.target_dir)
        table_changes = analyzer.analyze_changes(config.get_commit_range())
        
        # 4. 分组显示
        grouped = analyzer.group_by_change_type(table_changes)
        
        # 5. 生成并显示报告
        report_gen = ReportGenerator(
            repo_path=config.repo_path,
            target_dir=config.target_dir,
            branch_name=current_branch,
            base_branch=config.base_branch,
            commit_range=config.get_commit_range()
        )
        
        report = report_gen.generate_console_report(table_changes, grouped)
        print(report)
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = example_basic_check()
    sys.exit(0 if success else 1)
