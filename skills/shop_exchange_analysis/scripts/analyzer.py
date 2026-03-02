"""
兑换商店分析引擎
五维分析：饱和度 / 消耗结构 / 人次-消耗交叉 / 四象限定位 / 高价道具专项
"""

from collections import defaultdict
import statistics


class ShopExchangeAnalyzer:
    """兑换商店数据分析器"""

    # 默认阈值
    HIGH_SATURATION = 10.0
    MED_SATURATION = 5.0
    LOW_SATURATION = 1.0
    SKIN_PRICE_THRESHOLD = 50000

    def __init__(self, items: list[dict], thresholds: dict = None):
        self.items = items
        self.all_items = items
        # 分离普通道具和高价道具（皮肤等）
        self.normal_items = [i for i in items if i.get("token_price", 0) < self.SKIN_PRICE_THRESHOLD]
        self.special_items = [i for i in items if i.get("token_price", 0) >= self.SKIN_PRICE_THRESHOLD]

        if thresholds:
            self.HIGH_SATURATION = thresholds.get("high_saturation", self.HIGH_SATURATION)
            self.MED_SATURATION = thresholds.get("med_saturation", self.MED_SATURATION)
            self.LOW_SATURATION = thresholds.get("low_saturation", self.LOW_SATURATION)
            self.SKIN_PRICE_THRESHOLD = thresholds.get("skin_price_threshold", self.SKIN_PRICE_THRESHOLD)

    def run_all(self) -> dict:
        """运行全部分析，返回结果字典"""
        results = {
            "overview": self.analyze_overview(),
            "saturation": self.analyze_saturation(),
            "consumption_structure": self.analyze_consumption_structure(),
            "cross_analysis": self.analyze_cross(),
            "quadrant": self.analyze_quadrant(),
            "special_items": self.analyze_special_items(),
            "optimization": self.generate_optimization(),
        }
        return results

    # ============================================================
    # 1. 总览分析
    # ============================================================
    def analyze_overview(self) -> dict:
        total_token = sum(i.get("total_token_consumption", 0) for i in self.all_items)
        total_items = len(self.all_items)
        top_users_item = max(self.all_items, key=lambda x: x.get("exchange_users", 0))
        top_count_item = max(self.all_items, key=lambda x: x.get("exchange_count", 0))

        # 最高饱和度（排除高价道具）
        if self.normal_items:
            top_sat_item = max(self.normal_items, key=lambda x: x.get("saturation_rate", 0))
        else:
            top_sat_item = max(self.all_items, key=lambda x: x.get("saturation_rate", 0))

        return {
            "total_items": total_items,
            "total_token_consumption": total_token,
            "total_token_wan": round(total_token / 10000, 0),
            "top_users_item": top_users_item["item_name"],
            "top_users_value": top_users_item["exchange_users"],
            "top_count_item": top_count_item["item_name"],
            "top_count_value": top_count_item["exchange_count"],
            "top_saturation_item": top_sat_item["item_name"],
            "top_saturation_value": top_sat_item.get("saturation_rate", 0),
        }

    # ============================================================
    # 2. 饱和度分析
    # ============================================================
    def analyze_saturation(self) -> dict:
        items = self.normal_items if self.normal_items else self.all_items
        sorted_items = sorted(items, key=lambda x: x.get("saturation_rate", 0), reverse=True)

        high = [i for i in sorted_items if i.get("saturation_rate", 0) >= self.HIGH_SATURATION]
        medium = [i for i in sorted_items if self.MED_SATURATION <= i.get("saturation_rate", 0) < self.HIGH_SATURATION]
        low = [i for i in sorted_items if i.get("saturation_rate", 0) < self.LOW_SATURATION]

        analysis_points = []
        if high:
            names = "、".join([i["item_name"] for i in high[:3]])
            analysis_points.append(f"高饱和道具({len(high)}项): {names}等，存在供不应求信号")
        if low:
            analysis_points.append(f"低饱和道具({len(low)}项): 限购设置过高或需求不足")

        return {
            "sorted_items": sorted_items,
            "high_saturation": high,
            "medium_saturation": medium,
            "low_saturation": low,
            "high_threshold": self.HIGH_SATURATION,
            "med_threshold": self.MED_SATURATION,
            "low_threshold": self.LOW_SATURATION,
            "analysis_points": analysis_points,
        }

    # ============================================================
    # 3. 消耗结构分析
    # ============================================================
    def analyze_consumption_structure(self) -> dict:
        cat_data = defaultdict(lambda: {"token": 0, "users": 0, "count": 0, "items": 0})

        for item in self.all_items:
            cat = item.get("category", "其他")
            cat_data[cat]["token"] += item.get("total_token_consumption", 0)
            cat_data[cat]["users"] += item.get("exchange_users", 0)
            cat_data[cat]["count"] += item.get("exchange_count", 0)
            cat_data[cat]["items"] += 1

        total_token = sum(d["token"] for d in cat_data.values())
        total_users = sum(d["users"] for d in cat_data.values())

        categories = []
        for cat, data in sorted(cat_data.items(), key=lambda x: x[1]["token"], reverse=True):
            token_pct = round(data["token"] / total_token * 100, 1) if total_token > 0 else 0
            users_pct = round(data["users"] / total_users * 100, 1) if total_users > 0 else 0
            categories.append({
                "category": cat,
                "total_token": data["token"],
                "total_token_wan": round(data["token"] / 10000, 0),
                "token_pct": token_pct,
                "total_users": data["users"],
                "users_pct": users_pct,
                "total_count": data["count"],
                "item_count": data["items"],
            })

        # 找出消耗前两大类别
        top2_names = [c["category"] for c in categories[:2]]
        top2_pct = sum(c["token_pct"] for c in categories[:2])

        return {
            "categories": categories,
            "total_token": total_token,
            "total_users": total_users,
            "top2_categories": top2_names,
            "top2_pct": round(top2_pct, 1),
        }

    # ============================================================
    # 4. 人次-消耗交叉分析
    # ============================================================
    def analyze_cross(self) -> dict:
        items = self.normal_items if self.normal_items else self.all_items
        if not items:
            return {"quadrants": {}}

        users_list = [i.get("exchange_users", 0) for i in items]
        token_list = [i.get("total_token_consumption", 0) for i in items]

        median_users = statistics.median(users_list) if users_list else 0
        median_token = statistics.median(token_list) if token_list else 0

        quadrants = {
            "high_users_high_token": [],  # 右上
            "low_users_high_token": [],   # 左上
            "high_users_low_token": [],   # 右下
            "low_users_low_token": [],    # 左下
        }

        for item in items:
            users = item.get("exchange_users", 0)
            token = item.get("total_token_consumption", 0)
            if users >= median_users and token >= median_token:
                quadrants["high_users_high_token"].append(item["item_name"])
            elif users < median_users and token >= median_token:
                quadrants["low_users_high_token"].append(item["item_name"])
            elif users >= median_users and token < median_token:
                quadrants["high_users_low_token"].append(item["item_name"])
            else:
                quadrants["low_users_low_token"].append(item["item_name"])

        return {
            "median_users": median_users,
            "median_token": median_token,
            "quadrants": quadrants,
        }

    # ============================================================
    # 5. 四象限定位分析（人均消耗 × 饱和度）
    # ============================================================
    def analyze_quadrant(self) -> dict:
        items = self.normal_items if self.normal_items else self.all_items
        if not items:
            return {"matrix": []}

        cost_list = [i.get("avg_token_cost", 0) for i in items]
        sat_list = [i.get("saturation_rate", 0) for i in items]

        median_cost = statistics.median(cost_list) if cost_list else 0
        median_sat = statistics.median(sat_list) if sat_list else 0

        matrix = {
            "high_cost_high_sat": {"label": "高消耗·高饱和（刚需高价值）", "items": [], "color": "red"},
            "low_cost_high_sat": {"label": "低消耗·高饱和（高性价比热门）", "items": [], "color": "green"},
            "high_cost_low_sat": {"label": "高消耗·低饱和（高门槛低转化）", "items": [], "color": "orange"},
            "low_cost_low_sat": {"label": "低消耗·低饱和（低关注度）", "items": [], "color": "grey"},
        }

        for item in items:
            cost = item.get("avg_token_cost", 0)
            sat = item.get("saturation_rate", 0)
            if cost >= median_cost and sat >= median_sat:
                matrix["high_cost_high_sat"]["items"].append(item["item_name"])
            elif cost < median_cost and sat >= median_sat:
                matrix["low_cost_high_sat"]["items"].append(item["item_name"])
            elif cost >= median_cost and sat < median_sat:
                matrix["high_cost_low_sat"]["items"].append(item["item_name"])
            else:
                matrix["low_cost_low_sat"]["items"].append(item["item_name"])

        return {
            "median_cost": median_cost,
            "median_saturation": median_sat,
            "matrix": matrix,
        }

    # ============================================================
    # 6. 高价道具/皮肤专项分析
    # ============================================================
    def analyze_special_items(self) -> dict:
        if not self.special_items:
            return {"has_special": False, "items": [], "analysis_points": []}

        total_token = sum(i.get("total_token_consumption", 0) for i in self.special_items)
        total_users = sum(i.get("exchange_users", 0) for i in self.special_items)

        # 统计饱和度100%的数量
        full_sat = [i for i in self.special_items if i.get("saturation_rate", 0) >= 99.9]

        analysis_points = []
        if full_sat:
            analysis_points.append(f"{len(full_sat)}款限购道具饱和度达100%，有需求的玩家全部完成购买")
        if total_users < 20:
            analysis_points.append(f"购买人数极少（合计{total_users}人次），属极高R值玩家专属消费")
        analysis_points.append(f"合计消耗约{round(total_token/10000, 0)}万代币")

        return {
            "has_special": True,
            "items": self.special_items,
            "total_token": total_token,
            "total_users": total_users,
            "full_saturation_count": len(full_sat),
            "analysis_points": analysis_points,
        }

    # ============================================================
    # 7. 运营优化建议
    # ============================================================
    def generate_optimization(self) -> dict:
        suggestions = {"p1_limit": [], "p2_pricing": [], "p3_structure": []}

        # P1: 限购调整
        for item in self.normal_items:
            sat = item.get("saturation_rate", 0)
            limit = item.get("purchase_limit", 0)
            name = item["item_name"]

            if sat >= 15:
                # 高饱和 → 建议提高限购
                new_limit = min(limit * 2, limit + 50)
                suggestions["p1_limit"].append({
                    "item": name,
                    "current_limit": limit,
                    "saturation": sat,
                    "action": "increase",
                    "suggestion": f"提高至 {int(new_limit)}",
                    "reason": f"饱和度{sat}%，需求强烈",
                })
            elif sat < 0.5 and limit >= 5000:
                # 极低饱和 + 极高限购 → 建议降低限购
                new_limit = max(limit // 5, 500)
                suggestions["p1_limit"].append({
                    "item": name,
                    "current_limit": limit,
                    "saturation": sat,
                    "action": "decrease",
                    "suggestion": f"降低至 {int(new_limit)}",
                    "reason": f"饱和度仅{sat}%，限购过于宽松",
                })

        # P2: 定价策略
        high_sat_low_price = [i for i in self.normal_items
                              if i.get("saturation_rate", 0) >= 10 and i.get("token_price", 0) < 200]
        if high_sat_low_price:
            suggestions["p2_pricing"].append(
                "低价高饱和道具可考虑适当调价或推出捆绑包提高客单价"
            )

        low_sat_cats = defaultdict(list)
        for item in self.normal_items:
            if item.get("saturation_rate", 0) < 1:
                low_sat_cats[item.get("category", "其他")].append(item["item_name"])
        for cat, names in low_sat_cats.items():
            if len(names) >= 2:
                suggestions["p2_pricing"].append(
                    f"{cat}类多个道具饱和度不足1%，可考虑降价或增加兑换返利"
                )

        # P3: 结构建议
        cat_counts = defaultdict(int)
        for item in self.all_items:
            cat_counts[item.get("category", "其他")] += 1
        total = len(self.all_items)

        # 检查是否偏重养成材料
        growth_pct = sum(cat_counts.get(c, 0) for c in ["英雄养成", "装备养成", "军备养成"]) / total * 100
        if growth_pct > 50:
            suggestions["p3_structure"].append(
                f"养成类道具占比{growth_pct:.0f}%，可增加趣味性/社交性道具丰富商品结构"
            )

        # 检查皮肤价格带
        if self.special_items:
            prices = set(i.get("token_price", 0) for i in self.special_items)
            if len(prices) <= 2:
                suggestions["p3_structure"].append(
                    "高价道具价格带单一，可增设中端价位扩大购买群体"
                )

        return suggestions
