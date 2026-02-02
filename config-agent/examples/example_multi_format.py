"""
多格式输出示例 - 同时生成所有格式的报告
"""
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CheckConfig
from git_repo_manager import GitRepoManager
from change_analyzer import ChangeAnalyzer
from report_generator import ReportGenerator


def example_multi_format():
    """生成多种格式报告示例"""
    print("=" * 60)
    print("示例 5: 生成多种格式报告")
    print("=" * 60)
    print()
    
    # 配置
    config = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        base_branch="main",
        markdown_output_path="reports/changes.md",
        json_output_path="reports/changes.json"
    )
    
    try:
        # 初始化
        git_manager = GitRepoManager(config.repo_path)
        current_branch = git_manager.get_current_branch()
        
        print(f"仓库: {config.repo_path}")
        print(f"分支: {current_branch} (比较基准: {config.base_branch})")
        print(f"检查目录: {config.target_dir}")
        print()
        
        # 分析变更
        print("正在分析变更...")
        analyzer = ChangeAnalyzer(git_manager, config.target_dir)
        table_changes = analyzer.analyze_changes(config.get_commit_range())
        
        if not table_changes:
            print("未发现变更")
            return True
        
        grouped = analyzer.group_by_change_type(table_changes)
        
        # 创建报告生成器
        report_gen = ReportGenerator(
            repo_path=config.repo_path,
            target_dir=config.target_dir,
            branch_name=current_branch,
            base_branch=config.base_branch,
            commit_range=config.get_commit_range()
        )
        
        # 1. 控制台输出
        print("1. 控制台报告")
        print("-" * 60)
        console_report = report_gen.generate_console_report(
            table_changes,
            grouped
        )
        print(console_report)
        print()
        
        # 2. Markdown 报告
        print("2. 生成 Markdown 报告...")
        markdown_report = report_gen.generate_markdown_report(
            table_changes,
            grouped
        )
        report_gen.save_report(markdown_report, config.markdown_output_path)
        print(f"   ✓ 已保存: {config.markdown_output_path}")
        
        # 3. JSON 报告
        print("3. 生成 JSON 报告...")
        json_report = report_gen.generate_json_report(
            table_changes,
            grouped
        )
        report_gen.save_report(json_report, config.json_output_path)
        print(f"   ✓ 已保存: {config.json_output_path}")
        
        print()
        print("=" * 60)
        print("所有报告生成完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = example_multi_format()
    sys.exit(0 if success else 1)
