"""
分析器7: 商业化礼包分析 - 礼包合理性评估与调整建议。
"""

from .base_analyzer import BaseAnalyzer, AnalysisResult


class PackageAnalyzer(BaseAnalyzer):
    """
    礼包分析器。

    分析逻辑：
    1. 计算每个礼包的人均消费
    2. 按 revenue 排序，找到 Top3
    3. 计算各礼包占总营收的比例
    4. 与 comparison 对比同类礼包变化
    5. 合理性评估（引流/营收主力/鸡肋检测）
    """

    def analyze(self, data: dict) -> AnalysisResult:
        gp = data.get("gift_packages", {})
        packages = gp.get("packages", [])

        # 多对标支持：优先读取 comparisons 数组，兼容 comparison_packages
        comparisons = gp.get("comparisons", [])
        if not comparisons:
            comp_packages = gp.get("comparison_packages", [])
            if comp_packages:
                comparisons = [{"event": "对标", "packages": comp_packages}]

        result = AnalysisResult(module_name="礼包分析")
        details = []
        suggestions = []

        if not packages:
            result.conclusion = "无礼包数据"
            result.severity = "关注"
            return result

        # 1. 基础指标计算
        total_revenue = sum(p["revenue"] for p in packages)
        total_payers = sum(p["payers"] for p in packages)

        pkg_stats = []
        for pkg in packages:
            revenue = pkg["revenue"]
            payers = pkg["payers"]
            price = pkg["price"]
            avg_spend = round(revenue / payers, 1) if payers > 0 else 0
            share = round(revenue / total_revenue * 100, 1) if total_revenue > 0 else 0
            purchases_per_payer = round(revenue / (price * payers), 1) if price > 0 and payers > 0 else 0

            stat = {
                "name": pkg["package_name"],
                "price": price,
                "revenue": revenue,
                "payers": payers,
                "avg_spend": avg_spend,
                "share": share,
                "purchases_per_payer": purchases_per_payer,
                "bench_changes": [],  # 多对标的变化
            }
            pkg_stats.append(stat)

        # 2. 按营收排序
        pkg_stats.sort(key=lambda x: x["revenue"], reverse=True)
        top3 = pkg_stats[:3]
        details.append(f"礼包总营收: {self._format_number(total_revenue, is_currency=True)}")
        details.append(f"Top 3 礼包:")
        for i, p in enumerate(top3, 1):
            details.append(
                f"  {i}. {p['name']}（{self._format_number(p['price'])}元）"
                f"- 营收 {self._format_number(p['revenue'], is_currency=True)}（占比 {p['share']}%）"
                f"- {self._format_number(p['payers'])}人购买"
            )

        # 3. 对标对比（支持多对标）
        for comp_item in comparisons:
            comp_event = comp_item.get("event", "对标")
            comp_pkgs = comp_item.get("packages", [])
            if not comp_pkgs:
                continue

            comp_map = {p["package_name"]: p for p in comp_pkgs}
            for stat in pkg_stats:
                matched_comp = None
                for comp_name, comp_data in comp_map.items():
                    if comp_data["price"] == stat["price"]:
                        matched_comp = comp_data
                        break

                if matched_comp:
                    rev_change = self._calc_change_rate(stat["revenue"], matched_comp["revenue"])
                    payer_change = self._calc_change_rate(stat["payers"], matched_comp["payers"])
                    stat["bench_changes"].append({
                        "event": comp_event,
                        "rev_change": rev_change,
                        "payer_change": payer_change,
                    })
                    # 向后兼容：主对标写入顶层
                    if len(stat["bench_changes"]) == 1:
                        stat["rev_change"] = rev_change
                        stat["payer_change"] = payer_change
                    details.append(
                        f"  {stat['name']} vs {comp_event}: 营收 {self._format_change(rev_change)}, 人数 {self._format_change(payer_change)}"
                    )

        # 4. 合理性评估
        severity = "正常"
        low_price_pkgs = [p for p in pkg_stats if p["price"] <= 30]
        high_price_pkgs = [p for p in pkg_stats if p["price"] >= 300]

        # 低价礼包引流功能检查
        if low_price_pkgs:
            low_payer_share = sum(p["payers"] for p in low_price_pkgs) / total_payers * 100 if total_payers > 0 else 0
            if low_payer_share > 50:
                details.append(f"低价礼包(≤30元) 人数占比 {low_payer_share:.1f}%，引流功能正常")
            else:
                details.append(f"低价礼包(≤30元) 人数占比仅 {low_payer_share:.1f}%，引流效果偏弱")
                suggestions.append("建议优化低价礼包内容或增加曝光，提升引流效果")

        # 高价礼包营收主力检查
        if high_price_pkgs:
            high_rev_share = sum(p["revenue"] for p in high_price_pkgs) / total_revenue * 100 if total_revenue > 0 else 0
            if high_rev_share > 30:
                details.append(f"高价礼包(≥300元) 营收占比 {high_rev_share:.1f}%，承担营收主力")
            else:
                details.append(f"高价礼包(≥300元) 营收占比仅 {high_rev_share:.1f}%")
                suggestions.append("高价礼包营收贡献偏低，建议优化内容价值感或定价策略")

        # 鸡肋礼包检测（人数少 + 营收低）
        chicken_ribs = [p for p in pkg_stats if p["share"] < 5 and p["payers"] < total_payers * 0.05]
        if chicken_ribs:
            names = ", ".join(p["name"] for p in chicken_ribs)
            details.append(f"鸡肋礼包（人数少+营收低）: {names}")
            suggestions.append(f"建议移除或重新设计以下礼包: {names}")
            if severity == "正常":
                severity = "关注"

        # 综合结论
        if not suggestions:
            result.conclusion = "礼包设计合理，高低价格梯度覆盖良好"
        elif len(suggestions) <= 1:
            result.conclusion = "礼包设计基本合理，有小幅优化空间"
        else:
            result.conclusion = "礼包设计存在多处可优化点"
            severity = "关注"

        result.severity = severity
        result.details = details
        result.suggestions = suggestions
        result.chart_data = {
            "packages": packages,
            "pkg_stats": pkg_stats,
            "comparisons": comparisons,
            "comp_packages": comparisons[0].get("packages", []) if comparisons else [],  # 向后兼容
            "total_revenue": total_revenue,
        }
        result.raw_metrics = {
            "pkg_stats": pkg_stats,
            "total_revenue": total_revenue,
            "total_payers": total_payers,
        }

        return result
