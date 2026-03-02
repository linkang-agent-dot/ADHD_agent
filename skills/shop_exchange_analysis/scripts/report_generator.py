"""
兑换商店报告生成模块
支持 Notion / Wiki / Markdown 三种输出格式
"""


class ShopReportGenerator:
    """兑换商店报告生成器"""

    def __init__(self, items: list[dict], analysis: dict, chart_dir: str, activity_name: str = "活动商店"):
        self.items = items
        self.analysis = analysis
        self.chart_dir = chart_dir
        self.activity_name = activity_name
        self.normal_items = [i for i in items if i.get("token_price", 0) < 50000]
        self.special_items = [i for i in items if i.get("token_price", 0) >= 50000]

    def generate_title(self) -> str:
        return f"{self.activity_name} \u2014 \u5546\u5e97\u5151\u6362\u6570\u636e\u6df1\u5ea6\u5206\u6790"

    # ============================================================
    # Notion 版本
    # ============================================================
    def generate_notion(self) -> str:
        parts = []
        parts.append(self._notion_summary())
        parts.append(self._notion_overview())
        parts.append(self._notion_saturation())
        parts.append(self._notion_consumption())
        parts.append(self._notion_cross())
        parts.append(self._notion_quadrant())
        if self.special_items:
            parts.append(self._notion_special())
        parts.append(self._notion_optimization())
        parts.append("---")
        parts.append("> \u62a5\u544a\u81ea\u52a8\u751f\u6210")
        return "\n".join(parts)

    def _notion_summary(self) -> str:
        ov = self.analysis["overview"]
        cs = self.analysis["consumption_structure"]
        sat = self.analysis["saturation"]
        sp = self.analysis["special_items"]

        points = []
        points.append(f"\u5546\u5e97\u4ee3\u5e01\u603b\u6d88\u8017 {int(ov['total_token_wan'])} \u4e07\uff0c{cs['top2_categories'][0]}+{cs['top2_categories'][1]}\u5360 {cs['top2_pct']}%")

        if sat["high_saturation"]:
            top = sat["high_saturation"][0]
            points.append(f"{top['item_name']}\u9971\u548c\u5ea6 {top.get('saturation_rate', 0)}% \u5c45\u9996\uff0c\u5b58\u5728\u4f9b\u4e0d\u5e94\u6c42\u4fe1\u53f7")

        if sat["low_saturation"]:
            points.append(f"{len(sat['low_saturation'])}\u9879\u9053\u5177\u9971\u548c\u5ea6\u4e0d\u8db3{sat['low_threshold']}%\uff0c\u9650\u8d2d\u8bbe\u7f6e\u8fc7\u4e8e\u5bbd\u677e")

        if sp.get("has_special") and sp.get("full_saturation_count", 0) > 0:
            points.append(f"\u9ad8\u4ef7\u9053\u5177{sp['full_saturation_count']}\u6b3e\u9971\u548c\u5ea6100%\uff0c\u5c5e\u6781\u9ad8R\u73a9\u5bb6\u4e13\u5c5e\u6d88\u8d39")

        lines = "\n".join([f"\t{i+1}. {p}" for i, p in enumerate(points)])
        return f"""<callout icon="\U0001f3ea" color="blue_bg">
\t**Executive Summary**: {points[0]}
{lines}
</callout>"""

    def _notion_overview(self) -> str:
        ov = self.analysis["overview"]
        return f"""## \u4e00\u3001\u6570\u636e\u603b\u89c8
<table>
<tr>
<td>\u6307\u6807</td>
<td>\u6570\u503c</td>
</tr>
<tr>
<td>\u5546\u5e97\u9053\u5177\u603b\u6570</td>
<td>{ov['total_items']} \u4ef6</td>
</tr>
<tr>
<td>\u603b\u4ee3\u5e01\u6d88\u8017</td>
<td>**{ov['total_token_consumption']:,}**\uff08\u7ea6 {int(ov['total_token_wan'])} \u4e07\uff09</td>
</tr>
<tr>
<td>\u8986\u76d6\u4eba\u6b21\u6700\u9ad8\u9053\u5177</td>
<td>{ov['top_users_item']} ({ov['top_users_value']:,} \u4eba)</td>
</tr>
<tr>
<td>\u5151\u6362\u6b21\u6570\u6700\u9ad8\u9053\u5177</td>
<td>{ov['top_count_item']} ({ov['top_count_value']:,} \u6b21)</td>
</tr>
<tr>
<td>\u9971\u548c\u5ea6\u6700\u9ad8</td>
<td>{ov['top_saturation_item']} ({ov['top_saturation_value']}%)</td>
</tr>
</table>
---"""

    def _notion_saturation(self) -> str:
        sat = self.analysis["saturation"]
        lines = ["""## \u4e8c\u3001\u5151\u6362\u9971\u548c\u5ea6\u5206\u6790"""]

        # 高饱和度表
        if sat["high_saturation"]:
            lines.append(f"""### \u9ad8\u9971\u548c\u5ea6\u9053\u5177\uff08>{sat['high_threshold']}%\uff09\u2014 \u5f3a\u521a\u9700\u4fe1\u53f7
<table>
<tr>
<td>\u9053\u5177</td>
<td>\u9971\u548c\u5ea6</td>
<td>\u5355\u4ef7</td>
<td>\u9650\u8d2d</td>
<td>\u5151\u6362\u4eba\u6b21</td>
</tr>""")
            for item in sat["high_saturation"]:
                lines.append(f"""<tr>
<td>{item['item_name']}</td>
<td>**{item.get('saturation_rate', 0)}%**</td>
<td>{item.get('token_price', 0):,}</td>
<td>{item.get('purchase_limit', 0):,}</td>
<td>{item.get('exchange_users', 0):,}</td>
</tr>""")
            lines.append("</table>")

        # 低饱和度表
        if sat["low_saturation"]:
            lines.append(f"""### \u4f4e\u9971\u548c\u5ea6\u9053\u5177\uff08<{sat['low_threshold']}%\uff09\u2014 \u4f9b\u8fc7\u4e8e\u6c42
<table>
<tr>
<td>\u9053\u5177</td>
<td>\u9971\u548c\u5ea6</td>
<td>\u9650\u8d2d</td>
<td>\u5151\u6362\u4eba\u6b21</td>
</tr>""")
            for item in sat["low_saturation"]:
                lines.append(f"""<tr>
<td>{item['item_name']}</td>
<td>{item.get('saturation_rate', 0)}%</td>
<td>{item.get('purchase_limit', 0):,}</td>
<td>{item.get('exchange_users', 0):,}</td>
</tr>""")
            lines.append("</table>")

        lines.append("---")
        return "\n".join(lines)

    def _notion_consumption(self) -> str:
        cs = self.analysis["consumption_structure"]
        lines = [f"""## \u4e09\u3001\u4ee3\u5e01\u6d88\u8017\u7ed3\u6784\u5206\u6790
<callout icon="\U0001f4b0" color="red_bg">
\t**\u5173\u952e\u7ed3\u8bba\uff1a** {cs['top2_categories'][0]} + {cs['top2_categories'][1]} \u5408\u8ba1\u5360\u4ee3\u5e01\u6d88\u8017\u7684 **{cs['top2_pct']}%**\uff0c\u662f\u5546\u5e97\u7684\u7edd\u5bf9\u6d88\u8017\u4e3b\u529b
</callout>
<table>
<tr>
<td>\u7c7b\u522b</td>
<td>\u4ee3\u5e01\u6d88\u8017\uff08\u4e07\uff09</td>
<td>\u5360\u6bd4</td>
<td>\u5151\u6362\u4eba\u6b21</td>
<td>\u4eba\u6b21\u5360\u6bd4</td>
</tr>"""]

        for cat in cs["categories"]:
            lines.append(f"""<tr>
<td>{cat['category']}</td>
<td>{int(cat['total_token_wan'])} \u4e07</td>
<td>**{cat['token_pct']}%**</td>
<td>{cat['total_users']:,}</td>
<td>{cat['users_pct']}%</td>
</tr>""")

        lines.append("</table>\n---")
        return "\n".join(lines)

    def _notion_cross(self) -> str:
        cross = self.analysis["cross_analysis"]
        q = cross.get("quadrants", {})
        lines = ["""## \u56db\u3001\u5151\u6362\u4eba\u6b21 vs \u4ee3\u5e01\u6d88\u8017\u5206\u6790"""]

        mapping = {
            "high_users_high_token": ("\u9ad8\u4eba\u6b21 \u00b7 \u9ad8\u6d88\u8017\uff08\u53f3\u4e0a\uff09", "\u8986\u76d6\u5e7f\u4e14\u6d88\u8017\u5927\u7684\u6838\u5fc3\u5355\u54c1"),
            "low_users_high_token": ("\u4f4e\u4eba\u6b21 \u00b7 \u9ad8\u6d88\u8017\uff08\u5de6\u4e0a\uff09", "\u5c11\u6570\u9ad8R\u73a9\u5bb6\u5927\u91cf\u6d88\u8017"),
            "high_users_low_token": ("\u9ad8\u4eba\u6b21 \u00b7 \u4f4e\u6d88\u8017\uff08\u53f3\u4e0b\uff09", "\u8986\u76d6\u5e7f\u4f46\u5355\u4ef7\u4f4e"),
            "low_users_low_token": ("\u4f4e\u4eba\u6b21 \u00b7 \u4f4e\u6d88\u8017\uff08\u5de6\u4e0b\uff09", "\u51b7\u95e8\u9053\u5177"),
        }

        for key, (label, desc) in mapping.items():
            items_in_q = q.get(key, [])
            if items_in_q:
                names = "\u3001".join(items_in_q[:3])
                lines.append(f"- **{label}\uff1a** {names} \u2014 {desc}")

        lines.append("---")
        return "\n".join(lines)

    def _notion_quadrant(self) -> str:
        qd = self.analysis["quadrant"]
        matrix = qd.get("matrix", {})

        lines = ["""## \u4e94\u3001\u56db\u8c61\u9650\u5b9a\u4f4d\u5206\u6790
<table>
<tr>
<td>\u8c61\u9650</td>
<td>\u7279\u5f81</td>
<td>\u5178\u578b\u9053\u5177</td>
<td>\u8fd0\u8425\u5efa\u8bae</td>
</tr>"""]

        suggestions = {
            "high_cost_high_sat": "\u6838\u5fc3\u5438\u91d1\u9053\u5177\uff0c\u53ef\u9002\u5f53\u63d0\u9ad8\u9650\u8d2d",
            "low_cost_high_sat": "\u8986\u76d6\u5e7f\u4f46\u53d8\u73b0\u6548\u7387\u4f4e\uff0c\u53ef\u8003\u8651\u8c03\u4ef7",
            "high_cost_low_sat": "\u4eba\u5747\u6d88\u8017\u9ad8\u4f46\u6e17\u900f\u4e0d\u591f\uff0c\u9700\u964d\u4f4e\u95e8\u69db",
            "low_cost_low_sat": "\u5b58\u5728\u611f\u4f4e\uff0c\u8003\u8651\u6346\u7ed1\u9500\u552e\u6216\u8c03\u6574\u9650\u8d2d",
        }

        for key, data in matrix.items():
            items_list = data.get("items", [])
            if items_list:
                names = "\u3001".join(items_list[:3])
                label = data["label"]
                sug = suggestions.get(key, "")
                lines.append(f"""<tr>
<td>{label}</td>
<td>{data.get('color', '')}</td>
<td>{names}</td>
<td>{sug}</td>
</tr>""")

        lines.append("</table>\n---")
        return "\n".join(lines)

    def _notion_special(self) -> str:
        sp = self.analysis["special_items"]
        lines = ["""## \u516d\u3001\u9ad8\u4ef7\u9053\u5177\u4e13\u9879\u5206\u6790
<callout icon="\U0001f3a8" color="purple_bg">"""]

        for pt in sp.get("analysis_points", []):
            lines.append(f"\t{pt}")
        lines.append("</callout>")

        # 明细表
        lines.append("""<table>
<tr>
<td>\u9053\u5177\u540d\u79f0</td>
<td>\u5151\u6362\u4eba\u6b21</td>
<td>\u5355\u4ef7</td>
<td>\u9650\u8d2d</td>
<td>\u9971\u548c\u5ea6</td>
</tr>""")
        for item in self.special_items:
            lines.append(f"""<tr>
<td>{item['item_name']}</td>
<td>{item.get('exchange_users', 0)}</td>
<td>{item.get('token_price', 0):,}</td>
<td>{item.get('purchase_limit', 0)}</td>
<td>{item.get('saturation_rate', 0)}%</td>
</tr>""")
        lines.append("</table>\n---")
        return "\n".join(lines)

    def _notion_optimization(self) -> str:
        opt = self.analysis["optimization"]
        lines = ["## \u4e03\u3001\u8fd0\u8425\u4f18\u5316\u5efa\u8bae"]

        # P1 限购
        if opt["p1_limit"]:
            lines.append("""### P1 - \u9650\u8d2d\u8c03\u6574\u5efa\u8bae
<table>
<tr>
<td>\u9053\u5177</td>
<td>\u5f53\u524d\u9650\u8d2d</td>
<td>\u9971\u548c\u5ea6</td>
<td>\u5efa\u8bae</td>
</tr>""")
            for s in opt["p1_limit"]:
                color = "red" if s["action"] == "increase" else "orange"
                lines.append(f"""<tr>
<td>{s['item']}</td>
<td>{s['current_limit']}</td>
<td>{s['saturation']}%</td>
<td><span color="{color}">**{s['suggestion']}**\uff0c{s['reason']}</span></td>
</tr>""")
            lines.append("</table>")

        # P2 定价
        if opt["p2_pricing"]:
            lines.append("### P2 - \u5b9a\u4ef7\u7b56\u7565\u5efa\u8bae")
            for s in opt["p2_pricing"]:
                lines.append(f"- <span color=\"orange\">{s}</span>")

        # P3 结构
        if opt["p3_structure"]:
            lines.append("### P3 - \u5546\u54c1\u7ed3\u6784\u5efa\u8bae")
            for s in opt["p3_structure"]:
                lines.append(f"- {s}")

        return "\n".join(lines)

    # ============================================================
    # Wiki 版本
    # ============================================================
    def generate_wiki(self) -> str:
        parts = []
        parts.append(self._wiki_summary())
        parts.append(self._wiki_overview())
        parts.append(self._wiki_saturation())
        parts.append(self._wiki_consumption())
        parts.append(self._wiki_cross())
        parts.append(self._wiki_quadrant())
        if self.special_items:
            parts.append(self._wiki_special())
        parts.append(self._wiki_optimization())
        parts.append("---")
        parts.append("报告自动生成")
        return "\n".join(parts)

    def _wiki_summary(self) -> str:
        ov = self.analysis["overview"]
        cs = self.analysis["consumption_structure"]
        sat = self.analysis["saturation"]

        lines = [f"# {self.activity_name} -- 商店兑换数据深度分析报告", ""]
        lines.append("## 核心发现")
        lines.append(f"- 商店代币总消耗【{int(ov['total_token_wan'])}万】，{cs['top2_categories'][0]}+{cs['top2_categories'][1]}占【{cs['top2_pct']}%】")

        if sat["high_saturation"]:
            top = sat["high_saturation"][0]
            lines.append(f"- {top['item_name']}饱和度【{top.get('saturation_rate', 0)}%】居首，存在供不应求信号")
        if sat["low_saturation"]:
            lines.append(f"- 【{len(sat['low_saturation'])}】项道具饱和度不足{sat['low_threshold']}%，限购设置过于宽松")

        return "\n".join(lines)

    def _wiki_overview(self) -> str:
        ov = self.analysis["overview"]
        return f"""
---

## 一、数据总览

| 指标 | 数值 |
|------|------|
| 商店道具总数 | {ov['total_items']} 件 |
| 总代币消耗 | 【{ov['total_token_consumption']:,}】（约 {int(ov['total_token_wan'])} 万） |
| 覆盖人次最高道具 | {ov['top_users_item']} ({ov['top_users_value']:,} 人) |
| 兑换次数最高道具 | {ov['top_count_item']} ({ov['top_count_value']:,} 次) |
| 饱和度最高 | {ov['top_saturation_item']} ({ov['top_saturation_value']}%) |"""

    def _wiki_saturation(self) -> str:
        sat = self.analysis["saturation"]
        lines = [f"\n---\n\n## 二、兑换饱和度分析\n\n> [图表] 请手动插入: chart1_saturation.png"]

        if sat["high_saturation"]:
            lines.append(f"\n### 高饱和度道具（>{sat['high_threshold']}%）-- 强刚需信号\n")
            lines.append("| 道具 | 饱和度 | 单价 | 限购 | 兑换人次 |")
            lines.append("|------|--------|------|------|----------|")
            for item in sat["high_saturation"]:
                lines.append(f"| {item['item_name']} | 【{item.get('saturation_rate', 0)}%】 | {item.get('token_price', 0):,} | {item.get('purchase_limit', 0):,} | {item.get('exchange_users', 0):,} |")

        if sat["low_saturation"]:
            lines.append(f"\n### 低饱和度道具（<{sat['low_threshold']}%）-- 供过于求\n")
            lines.append("| 道具 | 饱和度 | 限购 | 兑换人次 |")
            lines.append("|------|--------|------|----------|")
            for item in sat["low_saturation"]:
                lines.append(f"| {item['item_name']} | {item.get('saturation_rate', 0)}% | {item.get('purchase_limit', 0):,} | {item.get('exchange_users', 0):,} |")

        return "\n".join(lines)

    def _wiki_consumption(self) -> str:
        cs = self.analysis["consumption_structure"]
        lines = [f"\n---\n\n## 三、代币消耗结构分析\n\n> [图表] 请手动插入: chart3_category_pie.png"]
        lines.append(f"\n关键结论：{cs['top2_categories'][0]} + {cs['top2_categories'][1]} 合计占代币消耗的【{cs['top2_pct']}%】\n")
        lines.append("| 类别 | 代币消耗（万） | 占比 | 兑换人次 | 人次占比 |")
        lines.append("|------|---------------|------|----------|----------|")

        for cat in cs["categories"]:
            lines.append(f"| {cat['category']} | {int(cat['total_token_wan'])} 万 | 【{cat['token_pct']}%】 | {cat['total_users']:,} | {cat['users_pct']}% |")

        return "\n".join(lines)

    def _wiki_cross(self) -> str:
        cross = self.analysis["cross_analysis"]
        q = cross.get("quadrants", {})
        lines = ["\n---\n\n## 四、兑换人次 vs 代币消耗分析\n\n> [图表] 请手动插入: chart2_bubble.png\n"]

        mapping = {
            "high_users_high_token": ("高人次·高消耗（右上角）", "覆盖广且消耗大的核心单品"),
            "low_users_high_token": ("低人次·高消耗（左上角）", "少数高R玩家大量消耗"),
            "high_users_low_token": ("高人次·低消耗（右下角）", "覆盖广但单价低"),
            "low_users_low_token": ("低人次·低消耗（左下角）", "冷门道具"),
        }

        for key, (label, desc) in mapping.items():
            items_in_q = q.get(key, [])
            if items_in_q:
                names = "、".join(items_in_q[:3])
                lines.append(f"- {label}：{names} -- {desc}")

        return "\n".join(lines)

    def _wiki_quadrant(self) -> str:
        qd = self.analysis["quadrant"]
        matrix = qd.get("matrix", {})
        lines = ["\n---\n\n## 五、四象限定位分析\n\n> [图表] 请手动插入: chart4_quadrant.png\n"]
        lines.append("| 象限 | 特征 | 典型道具 | 运营建议 |")
        lines.append("|------|------|----------|----------|")

        suggestions = {
            "high_cost_high_sat": "核心吸金道具，可适当提高限购",
            "low_cost_high_sat": "覆盖广但变现效率低，可考虑调价",
            "high_cost_low_sat": "人均消耗高但渗透不够，需降低门槛",
            "low_cost_low_sat": "存在感低，考虑捆绑销售或调整限购",
        }

        for key, data in matrix.items():
            items_list = data.get("items", [])
            if items_list:
                names = "、".join(items_list[:3])
                label = data["label"]
                sug = suggestions.get(key, "")
                lines.append(f"| {label} | -- | {names} | {sug} |")

        return "\n".join(lines)

    def _wiki_special(self) -> str:
        sp = self.analysis["special_items"]
        lines = ["\n---\n\n## 六、高价道具专项分析\n\n> [图表] 请手动插入: chart5_special.png\n"]

        for pt in sp.get("analysis_points", []):
            lines.append(f"- {pt}")

        lines.append("\n| 道具名称 | 兑换人次 | 单价 | 限购 | 饱和度 |")
        lines.append("|----------|----------|------|------|--------|")
        for item in self.special_items:
            lines.append(f"| {item['item_name']} | {item.get('exchange_users', 0)} | {item.get('token_price', 0):,} | {item.get('purchase_limit', 0)} | {item.get('saturation_rate', 0)}% |")

        return "\n".join(lines)

    def _wiki_optimization(self) -> str:
        opt = self.analysis["optimization"]
        lines = ["\n---\n\n## 七、运营优化建议"]

        if opt["p1_limit"]:
            lines.append("\n### P1 - 限购调整建议\n")
            lines.append("| 道具 | 当前限购 | 饱和度 | 建议 |")
            lines.append("|------|----------|--------|------|")
            for s in opt["p1_limit"]:
                lines.append(f"| {s['item']} | {s['current_limit']} | {s['saturation']}% | 【{s['suggestion']}】，{s['reason']} |")

        if opt["p2_pricing"]:
            lines.append("\n### P2 - 定价策略建议\n")
            for s in opt["p2_pricing"]:
                lines.append(f"- {s}")

        if opt["p3_structure"]:
            lines.append("\n### P3 - 商品结构建议\n")
            for s in opt["p3_structure"]:
                lines.append(f"- {s}")

        return "\n".join(lines)

    # ============================================================
    # Markdown 版本（本地保存用）
    # ============================================================
    def generate_markdown(self) -> str:
        """生成标准 Markdown（适合本地保存和 GitHub）"""
        return self.generate_wiki()  # Wiki 版本即为标准 Markdown
