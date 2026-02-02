"""
JSON 导出示例 - 用于程序化处理
"""
import sys
import json
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CheckConfig
from git_repo_manager import GitRepoManager
from change_analyzer import ChangeAnalyzer
from report_generator import ReportGenerator


def example_json_export():
    """导出 JSON 格式数据示例"""
    print("=" * 60)
    print("示例 3: 导出 JSON 格式数据")
    print("=" * 60)
    print()
    
    # 配置
    config = CheckConfig(
        repo_path=r"C:\gdconfig",
        target_dir="fo/",
        base_branch="main",
        json_output_path="reports/config_changes.json"
    )
    
    try:
        # 初始化
        git_manager = GitRepoManager(config.repo_path)
        current_branch = git_manager.get_current_branch()
        
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
        
        # 生成并保存 JSON
        json_report = report_gen.generate_json_report(table_changes, grouped)
        report_gen.save_report(json_report, config.json_output_path)
        
        print(f"✓ JSON 报告已保存: {config.json_output_path}")
        
        # 解析并显示摘要
        data = json.loads(json_report)
        summary = data['summary']
        
        print()
        print("摘要信息:")
        print(f"  - 检查时间: {summary['check_time']}")
        print(f"  - 提交数量: {summary['total_commits']}")
        print(f"  - 变更表数: {summary['total_tables']}")
        
        print()
        print("变更统计:")
        for change_type, tables in data['changes_by_type'].items():
            type_names = {'A': '新增', 'M': '修改', 'D': '删除', 'R': '重命名'}
            print(f"  - {type_names.get(change_type, change_type)}: {len(tables)} 个")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    success = example_json_export()
    sys.exit(0 if success else 1)
