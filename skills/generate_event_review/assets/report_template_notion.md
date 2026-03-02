> 对标活动: {{BENCHMARK_EVENT}} | 生成时间: {{GENERATED_AT}}

---

## 1. Executive Summary

<callout icon="⭐" color="yellow_bg">
{{EXECUTIVE_SUMMARY_SHORT}}
</callout>

{{EXECUTIVE_SUMMARY_DETAIL}}

---

## 2. 核心大盘趋势

**趋势判断: <span color="red">{{TREND_PATTERN}}</span>**

{{TREND_DESCRIPTION}}

**关键指标速览:**

<table header-row="true">
	<tr>
		<td>指标</td>
		<td>数值</td>
		<td>环比</td>
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

---

## 3. 模块营收结构

**当期模块占比:**

<table header-row="true">
	<tr>
		<td>模块</td>
		<td>占比</td>
		<td>营收</td>
		<td>备注</td>
	</tr>
	<tr>
		<td>外显类</td>
		<td>{{MODULE_APPEARANCE_SHARE}}</td>
		<td>${{MODULE_APPEARANCE_REVENUE}}</td>
		<td>{{MODULE_APPEARANCE_NOTE}}</td>
	</tr>
	<tr>
		<td><span color="red">**小游戏**</span></td>
		<td><span color="red">**{{MODULE_MINIGAME_SHARE}}**</span></td>
		<td><span color="red">**${{MODULE_MINIGAME_REVENUE}}**</span></td>
		<td><span color="red">**{{MODULE_MINIGAME_NOTE}}**</span></td>
	</tr>
	<tr>
		<td>混合/养成</td>
		<td>{{MODULE_HYBRID_SHARE}}</td>
		<td>${{MODULE_HYBRID_REVENUE}}</td>
		<td>{{MODULE_HYBRID_NOTE}}</td>
	</tr>
</table>

{{MODULE_INSIGHT}}

---

## 4. 用户分层分析

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

{{USER_TIER_INSIGHT}}

---

## 5. 子活动诊断

### 5.1 Keep - 表现优秀，建议保留

{{KEEP_LIST_NOTION}}

### 5.2 Optimize - 待优化项

{{OPTIMIZE_LIST_NOTION}}

---

## 6. Action Items

{{ACTION_ITEMS_NOTION}}

---

*本报告由 generate\_event\_review Skill 自动生成*
