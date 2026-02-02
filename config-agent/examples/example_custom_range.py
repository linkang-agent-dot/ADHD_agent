"""
自定义提交范围示例
"""
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CheckConfig
from git_repo_manager import GitRepoManager
from change_analyzer import ChangeAnalyzer
from report_generator import ReportGenerator


def example_custom_range():
    """自定义提交范围检查示例"""
    print("=" * 60)
    print("示例 4: 自定义提交范围")
    print("=" * 60)
    print()
    
    # 方式1: 使用分支比较
    print("方式 1: 比较两个分支")
    print("-" * 40)
    
    config1 = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        commit_range="main..develop"  # 比较 main 和 develop 分支
    )
    
    try:
        git_manager = GitRepoManager(config1.repo_path)
        analyzer = ChangeAnalyzer(git_manager, config1.target_dir)
        
        table_changes = analyzer.analyze_changes(config1.get_commit_range())
        print(f"✓ 发现 {len(table_changes)} 个配置表变更")
        
        # 显示变更的表名
        if table_changes:
            print("变更的表:")
            for table_name in sorted(table_changes.keys()):
                tc = table_changes[table_name]
                print(f"  - {table_name} ({tc.change_type}): {tc.file_path}")
        
    except Exception as e:
        print(f"错误: {e}")
    
    print()
    print("方式 2: 检查最近 N 次提交")
    print("-" * 40)
    
    # 方式2: 检查最近的提交
    config2 = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        commit_range="HEAD~5..HEAD"  # 最近 5 次提交
    )
    
    try:
        git_manager = GitRepoManager(config2.repo_path)
        analyzer = ChangeAnalyzer(git_manager, config2.target_dir)
        
        table_changes = analyzer.analyze_changes(config2.get_commit_range())
        print(f"✓ 最近 5 次提交中发现 {len(table_changes)} 个配置表变更")
        
    except Exception as e:
        print(f"错误: {e}")
    
    print()
    print("方式 3: 检查特定提交")
    print("-" * 40)
    
    # 方式3: 检查特定的两个提交之间
    config3 = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        commit_range="abc123..def456"  # 两个具体的提交哈希
    )
    
    print(f"提交范围: {config3.get_commit_range()}")
    print("(注意: 需要替换为实际的提交哈希)")


if __name__ == "__main__":
    example_custom_range()
