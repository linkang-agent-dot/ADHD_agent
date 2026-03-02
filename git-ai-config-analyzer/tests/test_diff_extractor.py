"""
差异提取器测试
"""
import pytest
from pathlib import Path

from src.diff_extractor import DiffExtractor, DiffContent, ConfigDiff


class TestDiffExtractor:
    """差异提取器测试类"""
    
    def test_parse_diff_output_basic(self):
        """测试基本的 diff 解析"""
        diff_text = """diff --git a/fo/test.csv b/fo/test.csv
index 1234567..abcdefg 100644
--- a/fo/test.csv
+++ b/fo/test.csv
@@ -1,3 +1,4 @@
 id,name,value
 1,item1,100
+2,item2,200
-3,item3,300
"""
        
        # 创建一个模拟的 DiffExtractor
        class MockGitManager:
            pass
        
        extractor = DiffExtractor(MockGitManager(), max_diff_lines=500)
        result = extractor.parse_diff_output(diff_text, "fo/test.csv")
        
        assert result.file_path == "fo/test.csv"
        assert len(result.added_lines) == 1
        assert len(result.removed_lines) == 1
        assert "2,item2,200" in result.added_lines
        assert "3,item3,300" in result.removed_lines
    
    def test_extract_table_name(self):
        """测试提取表名"""
        class MockGitManager:
            pass
        
        extractor = DiffExtractor(MockGitManager())
        
        # 测试不同路径格式
        assert extractor._extract_table_name("fo/user_config.csv") == "user_config"
        assert extractor._extract_table_name("fo/tables/item_config.csv") == "item_config"
        assert extractor._extract_table_name("config.csv") == "config"
    
    def test_parse_empty_diff(self):
        """测试空 diff"""
        class MockGitManager:
            pass
        
        extractor = DiffExtractor(MockGitManager())
        result = extractor.parse_diff_output("", "fo/test.csv")
        
        assert result.file_path == "fo/test.csv"
        assert len(result.added_lines) == 0
        assert len(result.removed_lines) == 0
        assert len(result.context_lines) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
