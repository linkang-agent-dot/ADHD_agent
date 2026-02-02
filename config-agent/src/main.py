"""
Git 配置变更检查工具 - 主程序入口
"""
import argparse
import sys
from pathlib import Path

from config import CheckConfig
from git_repo_manager import GitRepoManager
from change_analyzer import ChangeAnalyzer
from report_generator import ReportGenerator


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Git 配置变更检查工具 - 检查 fo 目录下的配置表变更"
    )
    
    parser.add_argument(
        "--repo-path",
        default=r"C:\gdconfig",
        help="Git 仓库路径（默认: C:\\gdconfig）"
    )
    
    parser.add_argument(
        "--target-dir",
        default="fo/",
        help="目标检查目录（默认: fo/）"
    )
    
    parser.add_argument(
        "--base-branch",
        default="bugfix",
        help="基准分支（默认: bugfix）"
    )
    
    parser.add_argument(
        "--compare-branch",
        default=None,
        help="比较分支（默认: 当前分支）"
    )
    
    parser.add_argument(
        "--commit-range",
        default=None,
        help="提交范围（默认: base-branch..HEAD）"
    )
    
    parser.add_argument(
        "--format",
        choices=["console", "markdown", "json", "all"],
        default="console",
        help="输出格式（默认: console）"
    )
    
    parser.add_argument(
        "--output",
        default=None,
        help="输出文件路径（仅对 markdown 和 json 格式有效）"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 创建配置
    config = CheckConfig(
        repo_path=args.repo_path,
        target_dir=args.target_dir,
        base_branch=args.base_branch,
        compare_branch=args.compare_branch,
        commit_range=args.commit_range,
        output_format=args.format
    )
    
    if args.output:
        if args.format == "markdown":
            config.markdown_output_path = args.output
        elif args.format == "json":
            config.json_output_path = args.output
    
    try:
        # 1. 初始化 Git 仓库管理器
        print(f"正在连接仓库: {config.repo_path}")
        git_manager = GitRepoManager(config.repo_path)
        
        # 2. 获取分支信息
        current_branch = git_manager.get_current_branch()
        if config.compare_branch:
            branch_name = config.compare_branch
        else:
            branch_name = current_branch
        
        print(f"当前分支: {current_branch}")
        print(f"基准分支: {config.base_branch}")
        
        # 3. 创建变更分析器
        analyzer = ChangeAnalyzer(git_manager, config.target_dir)
        
        # 4. 分析变更
        commit_range = config.get_commit_range()
        print(f"分析提交范围: {commit_range}")
        print(f"检查目录: {config.target_dir}")
        print()
        
        table_changes = analyzer.analyze_changes(commit_range)
        
        if not table_changes:
            print("未发现任何变更。")
            return
        
        # 5. 按变更类型分组
        grouped_changes = analyzer.group_by_change_type(table_changes)
        
        # 6. 生成报告
        report_gen = ReportGenerator(
            repo_path=config.repo_path,
            target_dir=config.target_dir,
            branch_name=branch_name,
            base_branch=config.base_branch,
            commit_range=commit_range
        )
        
        # 7. 输出报告
        if config.output_format == "console" or config.output_format == "all":
            console_report = report_gen.generate_console_report(
                table_changes,
                grouped_changes
            )
            print(console_report)
        
        if config.output_format == "markdown" or config.output_format == "all":
            markdown_report = report_gen.generate_markdown_report(
                table_changes,
                grouped_changes
            )
            report_gen.save_report(markdown_report, config.markdown_output_path)
            print(f"\nMarkdown 报告已保存到: {config.markdown_output_path}")
        
        if config.output_format == "json" or config.output_format == "all":
            json_report = report_gen.generate_json_report(
                table_changes,
                grouped_changes
            )
            report_gen.save_report(json_report, config.json_output_path)
            print(f"JSON 报告已保存到: {config.json_output_path}")
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
