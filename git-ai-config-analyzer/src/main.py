"""
Git AI 配置分析器 - 主程序入口
"""
import argparse
import sys
import os
from pathlib import Path

# 添加当前目录到路径，支持直接运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AnalyzerConfig
from git_repo_manager import GitRepoManager
from diff_extractor import DiffExtractor
from ai_analyzer import AIAnalyzer
from report_generator import AIReportGenerator


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Git AI 配置分析器 - 使用 AI 分析配置文件变更"
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
        default="markdown",
        help="输出格式（默认: markdown）"
    )
    
    parser.add_argument(
        "--output",
        default=None,
        help="输出文件路径"
    )
    
    parser.add_argument(
        "--ai-model",
        default="gpt-4",
        help="AI 模型（默认: gpt-4）"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="禁用 AI 分析，只生成基础报告"
    )
    
    parser.add_argument(
        "--max-diff-lines",
        type=int,
        default=500,
        help="单文件最大差异行数（默认: 500）"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 创建配置
    config = AnalyzerConfig(
        repo_path=args.repo_path,
        target_dir=args.target_dir,
        base_branch=args.base_branch,
        compare_branch=args.compare_branch,
        commit_range=args.commit_range,
        output_format=args.format,
        ai_model=args.ai_model,
        max_diff_lines=args.max_diff_lines
    )
    
    if args.output:
        if args.format == "json":
            config.json_output_path = args.output
        else:
            config.output_path = args.output
    
    if args.no_ai:
        config.ai_api_key = None  # 禁用 AI
    
    try:
        print("=" * 60)
        print("Git AI 配置分析器")
        print("=" * 60)
        
        # 1. 初始化 Git 仓库管理器
        print(f"\n[1/6] 连接仓库: {config.repo_path}")
        git_manager = GitRepoManager(config.repo_path)
        
        # 2. 获取分支信息
        current_branch = git_manager.get_current_branch()
        branch_name = config.compare_branch or current_branch
        
        print(f"      当前分支: {current_branch}")
        print(f"      基准分支: {config.base_branch}")
        
        # 3. 获取提交和变更文件
        commit_range = config.get_commit_range()
        print(f"\n[2/6] 获取提交记录: {commit_range}")
        
        commits = git_manager.get_commits(commit_range)
        print(f"      找到 {len(commits)} 个提交")
        
        file_changes = git_manager.get_changed_files(commit_range, config.target_dir)
        print(f"      找到 {len(file_changes)} 个变更文件")
        
        if not file_changes:
            print("\n未发现任何变更，分析结束。")
            return
        
        # 4. 提取差异内容
        print(f"\n[3/6] 提取差异内容...")
        diff_extractor = DiffExtractor(git_manager, config.max_diff_lines)
        config_diffs = diff_extractor.extract_all_diffs(
            commit_range,
            config.target_dir,
            file_changes,
            commits
        )
        print(f"      提取了 {len(config_diffs)} 个配置差异")
        
        # 5. AI 分析
        print(f"\n[4/6] AI 分析配置变更...")
        ai_analyzer = AIAnalyzer(config)
        analysis_results = ai_analyzer.analyze_all_changes(config_diffs)
        
        # 6. 生成整体总结
        print(f"\n[5/6] 生成整体总结...")
        overall_summary = ai_analyzer.generate_overall_summary(analysis_results)
        
        # 7. 生成报告
        print(f"\n[6/6] 生成报告...")
        report_gen = AIReportGenerator(
            repo_path=config.repo_path,
            target_dir=config.target_dir,
            branch_name=branch_name,
            base_branch=config.base_branch,
            commit_range=commit_range
        )
        
        # 输出报告
        if config.output_format == "console" or config.output_format == "all":
            console_report = report_gen.generate_console_report(
                analysis_results,
                overall_summary
            )
            print("\n")
            print(console_report)
        
        if config.output_format == "markdown" or config.output_format == "all":
            markdown_report = report_gen.generate_markdown_report(
                analysis_results,
                overall_summary
            )
            report_gen.save_report(markdown_report, config.output_path)
            print(f"\nMarkdown 报告已保存到: {config.output_path}")
        
        if config.output_format == "json" or config.output_format == "all":
            json_report = report_gen.generate_json_report(
                analysis_results,
                overall_summary
            )
            report_gen.save_report(json_report, config.json_output_path)
            print(f"JSON 报告已保存到: {config.json_output_path}")
        
        # 统计输出
        new_feature_count = len([r for r in analysis_results if r.is_new_feature_config])
        high_priority_count = len([r for r in analysis_results if r.review_priority == "高"])
        
        print("\n" + "=" * 60)
        print("分析完成!")
        print(f"  - 总变更数: {len(analysis_results)}")
        print(f"  - 功能新增配置: {new_feature_count}")
        print(f"  - 高优先级变更: {high_priority_count}")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
