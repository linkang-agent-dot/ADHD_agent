"""
Markdown 报告生成示例
"""
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CheckConfig
from git_repo_manager import GitRepoManager
from change_analyzer import ChangeAnalyzer
from report_generator import ReportGenerator


def example_markdown_report():
    """生成 Markdown 报告示例"""
    print("=" * 60)
    print("示例 2: 生成 Markdown 报告")
    print("=" * 60)
    print()
    
    # 配置
    config = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        base_branch="main",
        markdown_output_path="reports/config_changes.md"
    )
    
    try:
        # 初始化
        git_manager = GitRepoManager(config.repo_path)
        current_branch = git_manager.get_current_branch()
        
        print(f"仓库: {config.repo_path}")
        print(f"分支: {current_branch}")
        print(f"基准: {config.base_branch}")
        print()
        
        # 分析变更
        analyzer = ChangeAnalyzer(git_manager, config.target_dir)
        table_changes = analyzer.analyze_changes(config.get_commit_range())
        
        if not table_changes:
            print("未发现变更")
            return True
        
        grouped = analyzer.group_by_change_type(table_changes)
        
        # 生成报告
        report_gen = ReportGenerator(
            repo_path=config.repo_path,
            target_dir=config.target_dir,
            branch_name=current_branch,
            base_branch=config.base_branch,
            commit_range=config.get_commit_range()
        )
        
        # 生成 Markdown
        markdown_report = report_gen.generate_markdown_report(
            table_changes,
            grouped
        )
        
        # 保存文件
        report_gen.save_report(markdown_report, config.markdown_output_path)
        
        print(f"✓ Markdown 报告已保存: {config.markdown_output_path}")
        print(f"✓ 变更表数量: {len(table_changes)}")
        
        # 统计各类型数量
        for change_type, changes in grouped.items():
            if changes:
                type_names = {'A': '新增', 'M': '修改', 'D': '删除', 'R': '重命名'}
                print(f"  - {type_names.get(change_type, change_type)}: {len(changes)} 个")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    success = example_markdown_report()
    sys.exit(0 if success else 1)
