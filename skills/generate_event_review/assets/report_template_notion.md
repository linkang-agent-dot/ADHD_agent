> 对标活动: {{BENCHMARK_EVENT}} | 生成时间: {{GENERATED_AT}} | 完整版

<table_of_contents/>

---

## 1. Executive Summary

<callout icon="⭐" color="yellow_bg">
{{EXECUTIVE_SUMMARY_SHORT}}
</callout>

{{RISK_CALLOUT}}

---

## 2. 核心大盘指标

{{CORE_METRICS_TABLE}}

<callout icon="💡" color="gray_bg">
{{CORE_METRICS_INSIGHT}}
</callout>

---

## 3. 核心大盘趋势

<callout icon="📊" color="blue_bg">
	请在此处插入图表: 1\_Revenue\_Trend.png（核心大盘趋势折线图）
</callout>

**趋势判断: **<span color="red">**{{TREND_PATTERN}}**</span>

{{TREND_DESCRIPTION}}

<table header-row="true">
	<tr>
		<td>指标</td>
		<td>数值</td>
		<td>环比 (vs {{PREVIOUS_EVENT}})</td>
		<td>同比 (vs {{BENCHMARK_EVENT}})</td>
	</tr>
	<tr>
		<td>当期营收</td>
		<td>**${{CURRENT_REVENUE}}**</td>
		<td>{{MOM_REVENUE_COLOR}}</td>
		<td>{{YOY_REVENUE_COLOR}}</td>
	</tr>
	<tr>
		<td>当期 ARPU</td>
		<td>**${{CURRENT_ARPU}}**</td>
		<td>{{MOM_ARPU_COLOR}}</td>
		<td>{{YOY_ARPU_COLOR}}</td>
	</tr>
	<tr>
		<td>付费率</td>
		<td>**{{CURRENT_PAY_RATE}}**</td>
		<td>{{MOM_PAY_RATE}}</td>
		<td>{{YOY_PAY_RATE}}</td>
	</tr>
</table>

{{HISTORICAL_REVENUE_TABLE}}

---

## 4. 模块营收结构

<callout icon="📊" color="blue_bg">
	请在此处插入图表: 2\_Module\_Structure.png（模块营收堆叠面积图）
</callout>

{{MODULE_DETAIL_TABLE}}

<callout icon="💡" color="gray_bg">
{{MODULE_INSIGHT}}
</callout>

---

## 5. 各活动效率排名

{{ACTIVITY_RANKING_TABLE}}

<callout icon="🎯" color="purple_bg">
{{EFFICIENCY_TIER_INSIGHT}}
</callout>

<callout icon="🔑" color="orange_bg">
{{SUCCESS_MODEL_INSIGHT}}
</callout>

<callout icon="📎" color="gray_bg">
{{SKU_EFFICIENCY_INSIGHT}}
</callout>

---

## 6. 用户分层趋势

<callout icon="📊" color="blue_bg">
	请在此处插入图表: 3\_User\_Growth.png（用户分层 ARPU 分组柱状图）
</callout>

### 6.1 各层级 ARPU 对比

<table header-row="true">
	<tr>
		<td>用户层级</td>
		<td>{{EVENT_NAME}}</td>
		<td>{{PREVIOUS_EVENT}}</td>
		<td>{{BENCHMARK_EVENT}}</td>
		<td>同比变化</td>
		<td>环比变化</td>
	</tr>
{{USER_TIER_TABLE_ROWS}}
</table>

### 6.2 付费玩家人数趋势

{{TIER_HEADCOUNT_TABLE}}

### 6.3 趋势诊断

{{TIER_TREND_DIAGNOSIS}}

---

## 7. 日维度营收分析（可选）

{{DAILY_RHYTHM_INSIGHT}}

{{DAILY_REVENUE_TABLE}}

---

## 8. 子活动诊断

### 8.1 Keep - 表现优秀，建议保留

{{KEEP_LIST_NOTION}}

### 8.2 Optimize - 待优化项

{{OPTIMIZE_LIST_NOTION}}

### 8.3 Watch - 需持续监控

{{WATCH_LIST_NOTION}}

---

## 9. Action Items

{{ACTION_ITEMS_NOTION}}

---

## 10. 待人工补充清单

<callout icon="📋" color="orange_bg">
以下为数据分析无法覆盖的决策项，需人工补充后报告才算完整。
</callout>

{{HUMAN_CHECKLIST}}

---

## 11. 总结

<callout icon="📝" color="blue_bg">
{{FINAL_SUMMARY}}
</callout>

---

*本报告由 generate\_event\_review Skill 自动生成*
