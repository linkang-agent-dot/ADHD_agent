"""
报告生成器测试
"""
import pytest

from src.report_generator import AIReportGenerator
from src.ai_analyzer import AIAnalysisResult


class TestReportGenerator:
    """报告生成器测试类"""
    
    def test_console_report_generation(self):
        """测试控制台报告生成"""
        generator = AIReportGenerator(
            repo_path="C:\\gdconfig",
            target_dir="fo/",
            branch_name="feature",
            base_branch="bugfix",
            commit_range="bugfix..feature"
        )
        
        # 创建测试数据
        results = [
            AIAnalysisResult(
                file_path="fo/user_config.csv",
                table_name="user_config",
                change_type="A",
                summary="新增用户配置表",
                is_new_feature_config=True,
                review_priority="高"
            ),
            AIAnalysisResult(
                file_path="fo/item_config.csv",
                table_name="item_config",
                change_type="M",
                summary="修改道具配置",
                is_new_feature_config=False,
                review_priority="中"
            )
        ]
        
        overall_summary = "本次共有 2 个配置变更"
        
        report = generator.generate_console_report(results, overall_summary)
        
        assert "Git AI 配置分析报告" in report
        assert "user_config" in report
        assert "item_config" in report
        assert "2" in report  # 变更数量
    
    def test_markdown_report_generation(self):
        """测试 Markdown 报告生成"""
        generator = AIReportGenerator(
            repo_path="C:\\gdconfig",
            target_dir="fo/",
            branch_name="feature",
            base_branch="bugfix",
            commit_range="bugfix..feature"
        )
        
        results = [
            AIAnalysisResult(
                file_path="fo/user_config.csv",
                table_name="user_config",
                change_type="A",
                summary="新增用户配置表",
                is_new_feature_config=True,
                review_priority="高",
                sync_required=True
            )
        ]
        
        overall_summary = "本次新增用户配置功能"
        
        report = generator.generate_markdown_report(results, overall_summary)
        
        assert "# Git AI 配置分析报告" in report
        assert "## 执行摘要" in report
        assert "## 功能新增配置" in report
        assert "user_config" in report
        assert "- [ ]" in report  # 检查 checkbox
    
    def test_json_report_generation(self):
        """测试 JSON 报告生成"""
        import json
        
        generator = AIReportGenerator(
            repo_path="C:\\gdconfig",
            target_dir="fo/",
            branch_name="feature",
            base_branch="bugfix",
            commit_range="bugfix..feature"
        )
        
        results = [
            AIAnalysisResult(
                file_path="fo/user_config.csv",
                table_name="user_config",
                change_type="A",
                change_category="功能新增",
                summary="新增用户配置表",
                is_new_feature_config=True,
                review_priority="高"
            )
        ]
        
        overall_summary = "测试总结"
        
        report = generator.generate_json_report(results, overall_summary)
        
        # 验证是否为有效 JSON
        data = json.loads(report)
        
        assert "summary" in data
        assert data["summary"]["total_changes"] == 1
        assert data["summary"]["new_feature_count"] == 1
        assert len(data["all_changes"]) == 1
        assert data["all_changes"][0]["table_name"] == "user_config"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
