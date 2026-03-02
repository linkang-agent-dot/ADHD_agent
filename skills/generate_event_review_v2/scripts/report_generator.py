"""
报告生成模块 - 将 7 个分析结果组装为 Notion + Wiki 双版本报告。
"""

import os
from datetime import datetime
from typing import List, Dict

from analyzers.base_analyzer import AnalysisResult


class ReportGenerator:
    """
    报告组装器。
    将 7 个 AnalysisResult 组装为 Notion-flavored Markdown 和 Wiki Markdown 双版本。
    """

    # 模块顺序
    MODULE_ORDER = [
        "触达分析", "行为分析", "付费整体分析",
        "R级付费分析", "付费转化分析", "数值设计评估", "礼包分析",
    ]

    SECTION_TITLES = {
        "触达分析": "一、触达转化分析",
        "行为分析": "二、行为数据分析",
        "付费整体分析": "三、付费整体分析",
        "R级付费分析": "四、R级付费分析",
        "付费转化分析": "五、付费转化分析",
        "数值设计评估": "六、数值设计评估",
        "礼包分析": "七、商业化礼包分析",
    }

    CHART_FILES = {
        "触达分析": "1_Reach_Funnel.png",
        "行为分析": "2_Behavior_Data.png",
        "付费整体分析": "3_Payment_Overview.png",
        "R级付费分析": "4_RTier_Payment.png",
        "付费转化分析": "5_Conversion_Compare.png",
        "数值设计评估": "6_Reward_Deviation.png",
        "礼包分析": "7_Package_Compare.png",
    }

    def __init__(self, data: dict, analysis_results: List[AnalysisResult], chart_dir: str):
        self.data = data
        self.results: Dict[str, AnalysisResult] = {r.module_name: r for r in analysis_results}
        self.chart_dir = chart_dir
        self.meta = data.get("meta", {})

    def generate_notion_title(self) -> str:
        """生成 Notion 页面标题"""
        event_name = self.meta.get("event_name", "活动")
        return f"{event_name} 复盘报告"

    def generate_notion_content(self) -> str:
        """生成 Notion-flavored Markdown 报告"""
        sections = []

        # Executive Summary
        sections.append(self._notion_executive_summary())

        # 基础信息
        sections.append(self._notion_meta_section())

        # 7 个分析模块
        for module in self.MODULE_ORDER:
            if module in self.results:
                sections.append(self._notion_analysis_section(module))

        # 综合建议
        sections.append(self._notion_suggestions())

        # 页脚
        sections.append(f"\n---\n> 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        return "\n\n".join(sections)

    def generate_wiki_content(self) -> str:
        """生成 Wiki 兼容 Markdown 报告（不用粗体/emoji/HTML）"""
        sections = []

        event_name = self.meta.get("event_name", "活动")
        sections.append(f"# {event_name} 复盘报告")

        # Executive Summary
        sections.append(self._wiki_executive_summary())

        # 基础信息
        sections.append(self._wiki_meta_section())

        # 7 个分析模块
        for module in self.MODULE_ORDER:
            if module in self.results:
                sections.append(self._wiki_analysis_section(module))

        # 综合建议
        sections.append(self._wiki_suggestions())

        # 页脚
        sections.append(f"\n---\n> 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        return "\n\n".join(sections)

    # ============================================================
    # Executive Summary
    # ============================================================
    def _generate_executive_summary(self) -> dict:
        """
        生成 Executive Summary 数据。
        Returns:
            {"overall": "整体评价", "key_findings": ["发现1", ...], "severity_summary": {...}}
        """
        severities = {r.module_name: r.severity for r in self.results.values()}
        severity_counts = {}
        for s in severities.values():
            severity_counts[s] = severity_counts.get(s, 0) + 1

        # 整体评价
        if severity_counts.get("严重", 0) > 0:
            overall = "存在严重问题，需重点关注"
        elif severity_counts.get("异常", 0) > 0:
            overall = "部分模块表现异常，建议优化"
        elif severity_counts.get("关注", 0) >= 3:
            overall = "多个模块需要关注，整体表现中等"
        else:
            overall = "整体表现良好"

        # Top3 关键发现（按严重程度排序）
        priority = {"严重": 0, "异常": 1, "关注": 2, "正常": 3}
        sorted_results = sorted(self.results.values(), key=lambda r: priority.get(r.severity, 4))
        key_findings = [r.conclusion for r in sorted_results[:3]]

        return {
            "overall": overall,
            "key_findings": key_findings,
            "severity_summary": severity_counts,
        }

    def _notion_executive_summary(self) -> str:
        """Notion 版 Executive Summary"""
        summary = self._generate_executive_summary()
        lines = []
        lines.append(f'<callout icon="⭐" color="yellow_bg">')
        lines.append(f'**Executive Summary**: {summary["overall"]}')
        lines.append("")
        for i, finding in enumerate(summary["key_findings"], 1):
            lines.append(f"{i}. {finding}")
        lines.append("</callout>")
        return "\n".join(lines)

    def _wiki_executive_summary(self) -> str:
        """Wiki 版 Executive Summary"""
        summary = self._generate_executive_summary()
        lines = []
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"> 【{summary['overall']}】")
        lines.append(">")
        for i, finding in enumerate(summary["key_findings"], 1):
            lines.append(f"> {i}. {finding}")
        return "\n".join(lines)

    # ============================================================
    # 基础信息
    # ============================================================
    def _collect_benchmark_names(self) -> str:
        """从各分析结果中聚合所有对标活动名称"""
        names = set()
        # 从 meta
        if self.meta.get("benchmark_event"):
            names.add(self.meta["benchmark_event"])
        # 从各分析器的 chart_data 中提取
        for r in self.results.values():
            cd = r.chart_data or {}
            # comparisons 格式
            for comp in cd.get("comparisons", []):
                event = comp.get("event", comp.get("benchmark_event", ""))
                if event:
                    names.add(event)
            # benchmarks 格式（R级）
            for bench in cd.get("benchmarks", []):
                if bench.get("event"):
                    names.add(bench["event"])
            # yoy_benchmarks 格式（付费整体）
            for bench in cd.get("yoy_benchmarks", []):
                if bench.get("event"):
                    names.add(bench["event"])
            # all_comps 格式（付费转化）
            for comp in cd.get("all_comps", []):
                if comp.get("event"):
                    names.add(comp["event"])
        return "、".join(sorted(names)) if names else self.meta.get("benchmark_event", "")

    def _notion_meta_section(self) -> str:
        """Notion 版基础信息"""
        benchmark_str = self._collect_benchmark_names()
        lines = ["## 基础信息", ""]
        lines.append('<table header-row="true">')
        lines.append("| 项目 | 内容 |")
        lines.append(f'| 活动名称 | {self.meta.get("event_name", "")} |')
        lines.append(f'| 活动类型 | {self.meta.get("event_type", "")} |')
        lines.append(f'| 活动周期 | {self.meta.get("event_start_date", "")} ~ {self.meta.get("event_end_date", "")} |')
        lines.append(f'| 对标活动 | {benchmark_str} |')
        lines.append(f'| 本期改动 | {self.meta.get("change_description", "")} |')
        lines.append("</table>")
        return "\n".join(lines)

    def _wiki_meta_section(self) -> str:
        """Wiki 版基础信息"""
        benchmark_str = self._collect_benchmark_names()
        lines = ["## 基础信息", ""]
        lines.append("| 项目 | 内容 |")
        lines.append("| --- | --- |")
        lines.append(f'| 活动名称 | {self.meta.get("event_name", "")} |')
        lines.append(f'| 活动类型 | {self.meta.get("event_type", "")} |')
        lines.append(f'| 活动周期 | {self.meta.get("event_start_date", "")} ~ {self.meta.get("event_end_date", "")} |')
        lines.append(f'| 对标活动 | {benchmark_str} |')
        lines.append(f'| 本期改动 | {self.meta.get("change_description", "")} |')
        return "\n".join(lines)

    # ============================================================
    # 分析模块
    # ============================================================
    def _notion_analysis_section(self, module_name: str) -> str:
        """Notion 版分析模块"""
        r = self.results[module_name]
        title = self.SECTION_TITLES.get(module_name, module_name)
        chart_file = self.CHART_FILES.get(module_name, "")

        lines = [f"## {title}", ""]

        # 严重程度标记
        severity_color = {
            "正常": "green", "关注": "orange", "异常": "red", "严重": "red",
        }
        color = severity_color.get(r.severity, "default")
        lines.append(f'<span color="{color}">**[{r.severity}]** {r.conclusion}</span>')
        lines.append("")

        # 详细分析
        if r.details:
            for detail in r.details:
                lines.append(f"- {detail}")
            lines.append("")

        # 图表占位
        if chart_file:
            chart_path = os.path.join(self.chart_dir, chart_file)
            if os.path.exists(chart_path):
                lines.append(f'<callout icon="📊">请在此处插入图表: {chart_file}</callout>')
            else:
                lines.append(f"> 图表未生成: {chart_file}")
            lines.append("")

        # 改进建议
        if r.suggestions:
            lines.append("**改进建议:**")
            for s in r.suggestions:
                lines.append(f"- {s}")

        return "\n".join(lines)

    def _wiki_analysis_section(self, module_name: str) -> str:
        """Wiki 版分析模块"""
        r = self.results[module_name]
        title = self.SECTION_TITLES.get(module_name, module_name)
        chart_file = self.CHART_FILES.get(module_name, "")

        lines = [f"## {title}", ""]

        # 结论
        lines.append(f"> [{r.severity}] {r.conclusion}")
        lines.append("")

        # 详细分析
        if r.details:
            for detail in r.details:
                lines.append(f"- {detail}")
            lines.append("")

        # 图表占位
        if chart_file:
            lines.append(f"> [图表] 请手动插入: {chart_file}")
            lines.append("")

        # 改进建议
        if r.suggestions:
            lines.append("### 改进建议")
            for s in r.suggestions:
                lines.append(f"- {s}")

        return "\n".join(lines)

    # ============================================================
    # 综合建议
    # ============================================================
    def _aggregate_suggestions(self) -> dict:
        """汇总建议，按 P0/P1/P2 分级"""
        p0, p1, p2 = [], [], []
        for r in self.results.values():
            for s in r.suggestions:
                if r.severity == "严重":
                    p0.append(f"[{r.module_name}] {s}")
                elif r.severity == "异常":
                    p1.append(f"[{r.module_name}] {s}")
                else:
                    p2.append(f"[{r.module_name}] {s}")
        return {"P0": p0, "P1": p1, "P2": p2}

    def _notion_suggestions(self) -> str:
        """Notion 版综合建议"""
        agg = self._aggregate_suggestions()
        lines = ["## 综合建议", ""]

        if agg["P0"]:
            lines.append("### P0 - 必须立即处理")
            for s in agg["P0"]:
                lines.append(f'- <span color="red">{s}</span>')
            lines.append("")

        if agg["P1"]:
            lines.append("### P1 - 下期重点优化")
            for s in agg["P1"]:
                lines.append(f'- <span color="orange">{s}</span>')
            lines.append("")

        if agg["P2"]:
            lines.append("### P2 - 持续观察")
            for s in agg["P2"]:
                lines.append(f"- {s}")

        if not any(agg.values()):
            lines.append("各模块表现良好，暂无需紧急处理的建议。")

        return "\n".join(lines)

    def _wiki_suggestions(self) -> str:
        """Wiki 版综合建议"""
        agg = self._aggregate_suggestions()
        lines = ["## 综合建议", ""]

        if agg["P0"]:
            lines.append("### P0 - 必须立即处理")
            for s in agg["P0"]:
                lines.append(f"- {s}")
            lines.append("")

        if agg["P1"]:
            lines.append("### P1 - 下期重点优化")
            for s in agg["P1"]:
                lines.append(f"- {s}")
            lines.append("")

        if agg["P2"]:
            lines.append("### P2 - 持续观察")
            for s in agg["P2"]:
                lines.append(f"- {s}")

        if not any(agg.values()):
            lines.append("各模块表现良好，暂无需紧急处理的建议。")

        return "\n".join(lines)
