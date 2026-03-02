"""
报告生成器 - 生成包含 AI 分析结果的详细报告
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .ai_analyzer import AIAnalysisResult


class AIReportGenerator:
    """AI 分析报告生成器"""
    
    def __init__(
        self,
        repo_path: str,
        target_dir: str,
        branch_name: str,
        base_branch: str,
        commit_range: str
    ):
        """
        初始化报告生成器
        
        Args:
            repo_path: 仓库路径
            target_dir: 目标目录
            branch_name: 当前分支名
            base_branch: 基准分支名
            commit_range: 提交范围
        """
        self.repo_path = repo_path
        self.target_dir = target_dir
        self.branch_name = branch_name
        self.base_branch = base_branch
        self.commit_range = commit_range
        self.check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_console_report(
        self,
        results: List[AIAnalysisResult],
        overall_summary: str
    ) -> str:
        """生成控制台文本报告"""
        lines = []
        
        lines.append("=" * 70)
        lines.append("Git AI 配置分析报告")
        lines.append("=" * 70)
        
        # 摘要信息
        lines.append(f"分析时间: {self.check_time}")
        lines.append(f"仓库路径: {self.repo_path}")
        lines.append(f"分析目录: {self.target_dir}")
        lines.append(f"当前分支: {self.branch_name}")
        lines.append(f"比较基准: {self.base_branch}")
        lines.append(f"提交范围: {self.commit_range}")
        lines.append(f"变更配置数: {len(results)}")
        
        # 统计
        new_feature_count = len([r for r in results if r.is_new_feature_config])
        high_priority_count = len([r for r in results if r.review_priority == "高"])
        lines.append(f"功能新增配置: {new_feature_count}")
        lines.append(f"高优先级变更: {high_priority_count}")
        
        lines.append("")
        lines.append("-" * 70)
        lines.append("AI 分析总结")
        lines.append("-" * 70)
        lines.append(overall_summary)
        
        lines.append("")
        lines.append("-" * 70)
        lines.append("功能新增配置（重点关注）")
        lines.append("-" * 70)
        
        new_feature_configs = [r for r in results if r.is_new_feature_config]
        if new_feature_configs:
            for r in new_feature_configs:
                lines.append(f"\n[{r.table_name}]")
                lines.append(f"  文件: {r.file_path}")
                lines.append(f"  摘要: {r.summary}")
                lines.append(f"  目的: {r.purpose}")
                lines.append(f"  影响: {r.impact_assessment}")
                lines.append(f"  优先级: {r.review_priority}")
                if r.sync_required:
                    lines.append("  需要同步: 是")
        else:
            lines.append("无功能新增配置")
        
        lines.append("")
        lines.append("-" * 70)
        lines.append("所有变更列表")
        lines.append("-" * 70)
        
        for r in results:
            change_symbol = {'A': '+', 'M': 'M', 'D': '-', 'R': 'R'}.get(r.change_type, '?')
            lines.append(f"  [{change_symbol}] {r.table_name}: {r.summary}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def generate_markdown_report(
        self,
        results: List[AIAnalysisResult],
        overall_summary: str
    ) -> str:
        """生成 Markdown 格式报告"""
        lines = []
        
        # 标题
        lines.append("# Git AI 配置分析报告")
        lines.append("")
        
        # 执行摘要
        lines.append("## 执行摘要")
        lines.append("")
        lines.append(f"- **分析时间**: {self.check_time}")
        lines.append(f"- **仓库路径**: `{self.repo_path}`")
        lines.append(f"- **分析目录**: `{self.target_dir}`")
        lines.append(f"- **当前分支**: `{self.branch_name}`")
        lines.append(f"- **比较基准**: `{self.base_branch}`")
        lines.append(f"- **提交范围**: `{self.commit_range}`")
        lines.append(f"- **变更配置数**: {len(results)}")
        
        # 统计
        new_feature_count = len([r for r in results if r.is_new_feature_config])
        high_priority_count = len([r for r in results if r.review_priority == "高"])
        sync_required_count = len([r for r in results if r.sync_required])
        
        lines.append(f"- **功能新增配置**: {new_feature_count}")
        lines.append(f"- **高优先级变更**: {high_priority_count}")
        lines.append(f"- **需要同步**: {sync_required_count}")
        lines.append("")
        
        # AI 总结
        lines.append("## AI 分析总结")
        lines.append("")
        lines.append(overall_summary)
        lines.append("")
        
        # 功能新增配置
        lines.append("## 功能新增配置（重点关注）")
        lines.append("")
        
        new_feature_configs = [r for r in results if r.is_new_feature_config]
        if new_feature_configs:
            for idx, r in enumerate(new_feature_configs, 1):
                lines.append(f"### {idx}. {r.table_name}")
                lines.append("")
                lines.append(f"- **文件**: `{r.file_path}`")
                lines.append(f"- **变更类型**: {self._get_change_type_name(r.change_type)}")
                lines.append(f"- **摘要**: {r.summary}")
                lines.append(f"- **目的**: {r.purpose}")
                lines.append(f"- **影响范围**: {r.impact_assessment}")
                lines.append(f"- **审查优先级**: {r.review_priority}")
                lines.append(f"- **需要同步**: {'是' if r.sync_required else '否'}")
                if r.related_systems:
                    lines.append(f"- **相关系统**: {', '.join(r.related_systems)}")
                lines.append("")
        else:
            lines.append("无功能新增配置")
            lines.append("")
        
        # 按类别分组的变更
        lines.append("## 变更分类汇总")
        lines.append("")
        
        categories = {}
        for r in results:
            cat = r.change_category or "未分类"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)
        
        for cat, cat_results in categories.items():
            lines.append(f"### {cat} ({len(cat_results)}个)")
            lines.append("")
            lines.append("| 配置表 | 文件 | 摘要 | 优先级 |")
            lines.append("|--------|------|------|--------|")
            for r in cat_results:
                summary_short = r.summary[:30] + "..." if len(r.summary) > 30 else r.summary
                lines.append(f"| {r.table_name} | `{r.file_path}` | {summary_short} | {r.review_priority} |")
            lines.append("")
        
        # 高优先级变更
        high_priority = [r for r in results if r.review_priority == "高"]
        if high_priority:
            lines.append("## 高优先级变更（需立即关注）")
            lines.append("")
            for r in high_priority:
                lines.append(f"- **{r.table_name}**: {r.summary}")
                if r.impact_assessment:
                    lines.append(f"  - 影响: {r.impact_assessment}")
            lines.append("")
        
        # 需要同步的配置
        sync_required = [r for r in results if r.sync_required]
        if sync_required:
            lines.append("## 需要同步的配置")
            lines.append("")
            for r in sync_required:
                lines.append(f"- [ ] **{r.table_name}** (`{r.file_path}`)")
            lines.append("")
        
        # 所有变更详情
        lines.append("## 所有变更详情")
        lines.append("")
        
        for r in results:
            emoji = {'A': '➕', 'M': '✏️', 'D': '➖', 'R': '🔄'}.get(r.change_type, '❓')
            lines.append(f"### {emoji} {r.table_name}")
            lines.append("")
            lines.append(f"- **文件**: `{r.file_path}`")
            lines.append(f"- **变更类型**: {self._get_change_type_name(r.change_type)}")
            lines.append(f"- **分类**: {r.change_category}")
            lines.append(f"- **摘要**: {r.summary}")
            if r.purpose:
                lines.append(f"- **目的**: {r.purpose}")
            if r.impact_assessment:
                lines.append(f"- **影响**: {r.impact_assessment}")
            lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append("")
        lines.append("*报告由 Git AI 配置分析器自动生成*")
        
        return "\n".join(lines)
    
    def generate_json_report(
        self,
        results: List[AIAnalysisResult],
        overall_summary: str
    ) -> str:
        """生成 JSON 格式报告"""
        # 统计
        new_feature_count = len([r for r in results if r.is_new_feature_config])
        high_priority_count = len([r for r in results if r.review_priority == "高"])
        sync_required_count = len([r for r in results if r.sync_required])
        
        report_data = {
            "summary": {
                "check_time": self.check_time,
                "repo_path": self.repo_path,
                "target_dir": self.target_dir,
                "branch_name": self.branch_name,
                "base_branch": self.base_branch,
                "commit_range": self.commit_range,
                "total_changes": len(results),
                "new_feature_count": new_feature_count,
                "high_priority_count": high_priority_count,
                "sync_required_count": sync_required_count
            },
            "ai_summary": overall_summary,
            "new_feature_configs": [],
            "all_changes": [],
            "by_category": {},
            "by_priority": {
                "高": [],
                "中": [],
                "低": []
            }
        }
        
        # 填充数据
        for r in results:
            change_data = {
                "file_path": r.file_path,
                "table_name": r.table_name,
                "change_type": r.change_type,
                "change_category": r.change_category,
                "is_new_feature_config": r.is_new_feature_config,
                "summary": r.summary,
                "purpose": r.purpose,
                "impact_assessment": r.impact_assessment,
                "sync_required": r.sync_required,
                "review_priority": r.review_priority,
                "related_systems": r.related_systems
            }
            
            report_data["all_changes"].append(change_data)
            
            if r.is_new_feature_config:
                report_data["new_feature_configs"].append(change_data)
            
            cat = r.change_category or "未分类"
            if cat not in report_data["by_category"]:
                report_data["by_category"][cat] = []
            report_data["by_category"][cat].append(change_data)
            
            if r.review_priority in report_data["by_priority"]:
                report_data["by_priority"][r.review_priority].append(change_data)
        
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    
    def save_report(self, content: str, output_path: str) -> None:
        """保存报告到文件"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding='utf-8')
    
    def _get_change_type_name(self, change_type: str) -> str:
        """获取变更类型名称"""
        return {
            'A': '新增',
            'M': '修改',
            'D': '删除',
            'R': '重命名'
        }.get(change_type, change_type)
