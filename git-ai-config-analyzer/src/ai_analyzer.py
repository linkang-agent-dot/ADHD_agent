"""
AI 分析引擎 - 使用 AI 模型分析配置变更
"""
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from .config import AnalyzerConfig
from .diff_extractor import ConfigDiff


@dataclass
class AIAnalysisResult:
    """AI 分析结果"""
    file_path: str
    table_name: str
    change_type: str
    
    # 分类信息
    change_category: str = ""        # 功能新增/参数调整/Bug修复/结构重构
    is_new_feature_config: bool = False  # 是否为功能新增配置
    
    # 分析内容
    summary: str = ""                # 变更摘要
    purpose: str = ""                # 变更目的
    impact_assessment: str = ""      # 影响评估
    
    # 建议
    sync_required: bool = False      # 是否需要同步到其他环境
    review_priority: str = "中"      # 审查优先级：高/中/低
    related_systems: List[str] = field(default_factory=list)
    
    # 原始数据
    raw_ai_response: str = ""


class AIAnalyzer:
    """AI 分析引擎"""
    
    def __init__(self, config: AnalyzerConfig):
        """
        初始化 AI 分析引擎
        
        Args:
            config: 分析器配置
        """
        self.config = config
        self.client = None
        self._init_ai_client()
    
    def _init_ai_client(self):
        """初始化 AI 客户端"""
        try:
            from openai import OpenAI
            
            api_key = self.config.ai_api_key
            if not api_key:
                print("警告: 未配置 OPENAI_API_KEY，AI 分析功能将不可用")
                return
            
            client_kwargs = {"api_key": api_key}
            if self.config.ai_base_url:
                client_kwargs["base_url"] = self.config.ai_base_url
            
            self.client = OpenAI(**client_kwargs)
        except ImportError:
            print("警告: 未安装 openai 库，AI 分析功能将不可用")
            print("请运行: pip install openai")
    
    def analyze_single_change(self, config_diff: ConfigDiff) -> AIAnalysisResult:
        """
        分析单个配置变更
        
        Args:
            config_diff: 配置差异
            
        Returns:
            AI 分析结果
        """
        # 基础结果
        result = AIAnalysisResult(
            file_path=config_diff.file_path,
            table_name=config_diff.table_name,
            change_type=config_diff.change_type
        )
        
        # 如果没有 AI 客户端，返回基础分析
        if not self.client:
            result.summary = self._generate_basic_summary(config_diff)
            result.change_category = self._guess_category(config_diff)
            return result
        
        # 构建提示词
        prompt = self._build_analysis_prompt(config_diff)
        
        try:
            # 调用 AI
            response = self._call_ai(prompt)
            result = self._parse_ai_response(response, config_diff)
        except Exception as e:
            print(f"AI 分析出错 ({config_diff.file_path}): {e}")
            result.summary = self._generate_basic_summary(config_diff)
            result.change_category = self._guess_category(config_diff)
        
        return result
    
    def analyze_all_changes(self, config_diffs: List[ConfigDiff]) -> List[AIAnalysisResult]:
        """
        批量分析所有配置变更
        
        Args:
            config_diffs: 配置差异列表
            
        Returns:
            AI 分析结果列表
        """
        results = []
        total = len(config_diffs)
        
        for idx, config_diff in enumerate(config_diffs, 1):
            print(f"正在分析 [{idx}/{total}]: {config_diff.table_name}")
            result = self.analyze_single_change(config_diff)
            results.append(result)
        
        return results
    
    def generate_overall_summary(self, results: List[AIAnalysisResult]) -> str:
        """
        生成整体总结报告
        
        Args:
            results: 所有分析结果
            
        Returns:
            整体总结文本
        """
        if not self.client:
            return self._generate_basic_overall_summary(results)
        
        # 构建总结提示词
        prompt = self._build_summary_prompt(results)
        
        try:
            return self._call_ai(prompt)
        except Exception as e:
            print(f"生成总结出错: {e}")
            return self._generate_basic_overall_summary(results)
    
    def _build_analysis_prompt(self, config_diff: ConfigDiff) -> str:
        """构建分析提示词"""
        # 获取提交信息
        commits_text = ""
        if config_diff.related_commits:
            commits_text = "\n".join([
                f"- {c.hash[:7]} | {c.author} | {c.message}"
                for c in config_diff.related_commits[:5]
            ])
        
        # 获取差异内容
        added_lines = ""
        removed_lines = ""
        if config_diff.diff_content:
            added_lines = "\n".join(config_diff.diff_content.added_lines[:50])
            removed_lines = "\n".join(config_diff.diff_content.removed_lines[:50])
        
        change_type_map = {
            'A': '新增文件',
            'M': '修改文件',
            'D': '删除文件',
            'R': '重命名文件'
        }
        
        prompt = f"""你是一个专业的游戏配置分析专家。请分析以下配置文件的变更，并提供详细的分析报告。

## 变更信息

**文件路径**: {config_diff.file_path}
**表名**: {config_diff.table_name}
**变更类型**: {change_type_map.get(config_diff.change_type, config_diff.change_type)}

## 相关提交
{commits_text if commits_text else "无提交信息"}

## 变更内容

### 新增内容
```
{added_lines if added_lines else "无新增内容"}
```

### 删除内容
```
{removed_lines if removed_lines else "无删除内容"}
```

## 请提供以下分析（以 JSON 格式输出）

{{
    "summary": "用一句话描述这个变更",
    "purpose": "分析这个变更的目的",
    "change_category": "功能新增/参数调整/Bug修复/结构重构/废弃移除 中的一个",
    "is_new_feature_config": true或false,
    "impact_assessment": "这个变更可能影响哪些系统或功能",
    "sync_required": true或false,
    "review_priority": "高/中/低",
    "related_systems": ["可能影响的系统列表"]
}}

请只输出 JSON，不要有其他内容。
"""
        return prompt
    
    def _build_summary_prompt(self, results: List[AIAnalysisResult]) -> str:
        """构建总结提示词"""
        # 汇总各类变更
        new_feature_configs = [r for r in results if r.is_new_feature_config]
        high_priority = [r for r in results if r.review_priority == "高"]
        
        changes_summary = []
        for r in results:
            changes_summary.append(f"- {r.table_name}: {r.summary}")
        
        prompt = f"""你是一个专业的配置管理专家。请根据以下配置变更的分析结果，生成一份整体总结报告。

## 变更统计
- 总变更数: {len(results)}
- 功能新增配置数: {len(new_feature_configs)}
- 高优先级变更数: {len(high_priority)}

## 各配置变更摘要
{chr(10).join(changes_summary)}

## 请提供以下内容（使用 Markdown 格式）

1. **整体变更概览**: 总结这段时间的配置变更情况（2-3句话）
2. **功能新增配置**: 列出需要重点关注的功能新增配置
3. **高优先级变更**: 需要优先处理的变更
4. **配置同步建议**: 哪些配置需要同步到其他环境
5. **行动建议**: 建议的后续行动（以 checkbox 列表形式）

请直接输出 Markdown 格式的报告。
"""
        return prompt
    
    def _call_ai(self, prompt: str) -> str:
        """调用 AI API"""
        response = self.client.chat.completions.create(
            model=self.config.ai_model,
            messages=[
                {"role": "system", "content": "你是一个专业的游戏配置分析专家，擅长分析配置文件的变更并给出专业建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    def _parse_ai_response(self, response: str, config_diff: ConfigDiff) -> AIAnalysisResult:
        """解析 AI 响应"""
        result = AIAnalysisResult(
            file_path=config_diff.file_path,
            table_name=config_diff.table_name,
            change_type=config_diff.change_type,
            raw_ai_response=response
        )
        
        try:
            # 尝试提取 JSON
            json_match = response
            if "```json" in response:
                json_match = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_match = response.split("```")[1].split("```")[0]
            
            data = json.loads(json_match.strip())
            
            result.summary = data.get("summary", "")
            result.purpose = data.get("purpose", "")
            result.change_category = data.get("change_category", "")
            result.is_new_feature_config = data.get("is_new_feature_config", False)
            result.impact_assessment = data.get("impact_assessment", "")
            result.sync_required = data.get("sync_required", False)
            result.review_priority = data.get("review_priority", "中")
            result.related_systems = data.get("related_systems", [])
            
        except (json.JSONDecodeError, IndexError) as e:
            print(f"解析 AI 响应失败: {e}")
            result.summary = response[:200] if response else ""
        
        return result
    
    def _generate_basic_summary(self, config_diff: ConfigDiff) -> str:
        """生成基础摘要（无 AI 时使用）"""
        change_type_map = {
            'A': '新增',
            'M': '修改',
            'D': '删除',
            'R': '重命名'
        }
        action = change_type_map.get(config_diff.change_type, '变更')
        
        lines_info = ""
        if config_diff.diff_content:
            added = len(config_diff.diff_content.added_lines)
            removed = len(config_diff.diff_content.removed_lines)
            if added or removed:
                lines_info = f"（+{added}/-{removed}行）"
        
        return f"{action}配置表 {config_diff.table_name}{lines_info}"
    
    def _guess_category(self, config_diff: ConfigDiff) -> str:
        """猜测变更类别（无 AI 时使用）"""
        if config_diff.change_type == 'A':
            return "功能新增"
        elif config_diff.change_type == 'D':
            return "废弃移除"
        else:
            return "参数调整"
    
    def _generate_basic_overall_summary(self, results: List[AIAnalysisResult]) -> str:
        """生成基础整体总结（无 AI 时使用）"""
        new_count = len([r for r in results if r.change_type == 'A'])
        modify_count = len([r for r in results if r.change_type == 'M'])
        delete_count = len([r for r in results if r.change_type == 'D'])
        
        summary = f"""## 变更概览

本次共有 {len(results)} 个配置表发生变更：
- 新增: {new_count} 个
- 修改: {modify_count} 个
- 删除: {delete_count} 个

### 新增配置表
"""
        new_tables = [r for r in results if r.change_type == 'A']
        if new_tables:
            for r in new_tables:
                summary += f"- **{r.table_name}**: {r.file_path}\n"
        else:
            summary += "无\n"
        
        summary += "\n### 修改的配置表\n"
        modify_tables = [r for r in results if r.change_type == 'M']
        if modify_tables:
            for r in modify_tables:
                summary += f"- **{r.table_name}**: {r.summary}\n"
        else:
            summary += "无\n"
        
        return summary
