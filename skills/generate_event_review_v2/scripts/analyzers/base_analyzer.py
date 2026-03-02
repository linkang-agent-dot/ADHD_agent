"""
分析器基类 - 定义标准化分析结果和通用工具方法。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class AnalysisResult:
    """分析结果标准结构"""
    module_name: str                          # 模块名称（如 "触达分析"）
    conclusion: str = ""                      # 核心结论（1-2 句话）
    severity: str = "正常"                    # 严重程度: "正常" / "关注" / "异常" / "严重"
    details: List[str] = field(default_factory=list)      # 详细分析要点
    suggestions: List[str] = field(default_factory=list)  # 改进建议
    chart_data: Optional[dict] = None         # 传递给图表生成器的数据
    raw_metrics: dict = field(default_factory=dict)       # 计算出的原始指标


class BaseAnalyzer(ABC):
    """分析器基类"""

    @abstractmethod
    def analyze(self, data: dict) -> AnalysisResult:
        """执行分析，返回标准化结果"""
        pass

    def _calc_change_rate(self, current: float, previous: float) -> float:
        """计算变化率（百分比）"""
        if previous == 0:
            return 0.0 if current == 0 else 100.0
        return round((current - previous) / previous * 100, 2)

    def _detect_anomaly(self, values: list, threshold: float = 2.0) -> List[int]:
        """
        基于 Z-score 的异常检测，返回异常值的索引。

        Args:
            values: 数值列表
            threshold: Z-score 阈值，默认 2.0

        Returns:
            异常值索引列表
        """
        if len(values) < 3:
            return []

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance) if variance > 0 else 0

        if std == 0:
            return []

        anomalies = []
        for i, v in enumerate(values):
            z_score = abs((v - mean) / std)
            if z_score > threshold:
                anomalies.append(i)
        return anomalies

    def _format_number(self, value: float, is_currency: bool = False) -> str:
        """格式化数字（千分位 + 可选货币符号）"""
        if is_currency:
            return f"¥{value:,.0f}"
        if isinstance(value, float) and value != int(value):
            return f"{value:,.1f}"
        return f"{value:,.0f}"

    def _format_change(self, rate: float) -> str:
        """格式化变化率"""
        sign = "+" if rate > 0 else ""
        return f"{sign}{rate:.1f}%"

    def _severity_from_change(self, change_rate: float, positive_is_good: bool = True) -> str:
        """根据变化率判断严重程度"""
        effective_rate = change_rate if positive_is_good else -change_rate
        if effective_rate >= 5:
            return "正常"
        elif effective_rate >= -5:
            return "关注"
        elif effective_rate >= -20:
            return "异常"
        else:
            return "严重"
