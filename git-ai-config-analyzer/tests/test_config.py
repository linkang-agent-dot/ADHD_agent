"""
配置模块测试
"""
import pytest
from pathlib import Path

from src.config import AnalyzerConfig


class TestAnalyzerConfig:
    """配置类测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = AnalyzerConfig()
        
        assert config.repo_path == r"C:\gdconfig"
        assert config.target_dir == "fo/"
        assert config.base_branch == "bugfix"
        assert config.ai_model == "gpt-4"
        assert config.output_format == "markdown"
        assert config.max_diff_lines == 500
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = AnalyzerConfig(
            repo_path="C:\\custom_path",
            target_dir="configs/",
            base_branch="main",
            ai_model="gpt-3.5-turbo",
            max_diff_lines=1000
        )
        
        assert config.repo_path == "C:\\custom_path"
        assert config.target_dir == "configs/"
        assert config.base_branch == "main"
        assert config.ai_model == "gpt-3.5-turbo"
        assert config.max_diff_lines == 1000
    
    def test_get_commit_range_default(self):
        """测试获取默认提交范围"""
        config = AnalyzerConfig(base_branch="bugfix")
        commit_range = config.get_commit_range()
        assert commit_range == "bugfix..HEAD"
    
    def test_get_commit_range_custom(self):
        """测试获取自定义提交范围"""
        config = AnalyzerConfig(commit_range="abc123..def456")
        commit_range = config.get_commit_range()
        assert commit_range == "abc123..def456"
    
    def test_env_var_loading(self):
        """测试环境变量加载"""
        # 设置测试环境变量
        os.environ["OPENAI_API_KEY"] = "test_key_123"
        os.environ["OPENAI_BASE_URL"] = "https://test.api.com"
        
        config = AnalyzerConfig()
        
        assert config.ai_api_key == "test_key_123"
        assert config.ai_base_url == "https://test.api.com"
        
        # 清理
        del os.environ["OPENAI_API_KEY"]
        del os.environ["OPENAI_BASE_URL"]
