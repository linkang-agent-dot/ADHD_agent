"""
AI 分析器测试
"""
import pytest

from src.ai_analyzer import AIAnalyzer, AIAnalysisResult
from src.config import AnalyzerConfig
from src.diff_extractor import ConfigDiff, DiffContent


class TestAIAnalyzer:
    """AI 分析器测试类"""
    
    def test_basic_summary_generation(self):
        """测试基础摘要生成（无 AI）"""
        config = AnalyzerConfig(ai_api_key=None)  # 禁用 AI
        analyzer = AIAnalyzer(config)
        
        # 创建测试数据
        diff_content = DiffContent(
            file_path="fo/user_config.csv",
            added_lines=["1,user1,100", "2,user2,200"],
            removed_lines=["1,old_user,50"]
        )
        
        config_diff = ConfigDiff(
            file_path="fo/user_config.csv",
            table_name="user_config",
            change_type="M",
            diff_content=diff_content
        )
        
        summary = analyzer._generate_basic_summary(config_diff)
        
        assert "user_config" in summary
        assert "修改" in summary
    
    def test_guess_category(self):
        """测试类别猜测"""
        config = AnalyzerConfig(ai_api_key=None)
        analyzer = AIAnalyzer(config)
        
        # 测试新增文件
        config_diff_add = ConfigDiff(
            file_path="fo/new_config.csv",
            table_name="new_config",
            change_type="A"
        )
        assert analyzer._guess_category(config_diff_add) == "功能新增"
        
        # 测试删除文件
        config_diff_del = ConfigDiff(
            file_path="fo/old_config.csv",
            table_name="old_config",
            change_type="D"
        )
        assert analyzer._guess_category(config_diff_del) == "废弃移除"
        
        # 测试修改文件
        config_diff_mod = ConfigDiff(
            file_path="fo/user_config.csv",
            table_name="user_config",
            change_type="M"
        )
        assert analyzer._guess_category(config_diff_mod) == "参数调整"
    
    def test_parse_ai_response_json(self):
        """测试解析 AI 响应（JSON 格式）"""
        config = AnalyzerConfig(ai_api_key=None)
        analyzer = AIAnalyzer(config)
        
        json_response = """{
            "summary": "新增用户配置表",
            "purpose": "支持新的用户等级系统",
            "change_category": "功能新增",
            "is_new_feature_config": true,
            "impact_assessment": "影响用户系统和奖励系统",
            "sync_required": true,
            "review_priority": "高",
            "related_systems": ["用户系统", "奖励系统"]
        }"""
        
        config_diff = ConfigDiff(
            file_path="fo/user_config.csv",
            table_name="user_config",
            change_type="A"
        )
        
        result = analyzer._parse_ai_response(json_response, config_diff)
        
        assert result.summary == "新增用户配置表"
        assert result.is_new_feature_config == True
        assert result.review_priority == "高"
        assert "用户系统" in result.related_systems


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
