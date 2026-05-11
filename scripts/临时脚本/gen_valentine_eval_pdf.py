# -*- coding: utf-8 -*-
"""2026情人节活动复盘 - 评估报告 PDF 生成脚本"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ---------- 字体注册 ----------
FONT_DIR = "C:/Windows/Fonts"
font_candidates = [
    ("MSYaHei", "msyh.ttc"),
    ("MSYaHei", "msyh.ttf"),
    ("SimHei", "simhei.ttf"),
    ("SimSun", "simsun.ttc"),
]
CN_FONT = None
for name, fname in font_candidates:
    fp = os.path.join(FONT_DIR, fname)
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont(name, fp))
            CN_FONT = name
            break
        except Exception:
            continue

if CN_FONT is None:
    raise RuntimeError("未找到可用中文字体，请确认 Windows Fonts 目录")

BOLD_FONT = CN_FONT  # TTF 无 bold 变体时复用

# ---------- 颜色 ----------
C_PRIMARY   = HexColor("#1a1a2e")
C_ACCENT    = HexColor("#e94560")
C_GREEN     = HexColor("#0f9b58")
C_ORANGE    = HexColor("#f39c12")
C_BLUE      = HexColor("#2196f3")
C_GRAY      = HexColor("#666666")
C_LIGHT_BG  = HexColor("#f8f9fa")
C_WHITE     = HexColor("#ffffff")
C_RED_BG    = HexColor("#fce4ec")
C_GREEN_BG  = HexColor("#e8f5e9")
C_YELLOW_BG = HexColor("#fff8e1")
C_BLUE_BG   = HexColor("#e3f2fd")

# ---------- 样式 ----------
def make_style(name, font=CN_FONT, size=10, color=C_PRIMARY, leading=None,
               space_before=0, space_after=0, align=0, bold=False):
    return ParagraphStyle(
        name, fontName=font, fontSize=size, textColor=color,
        leading=leading or size * 1.5, spaceBefore=space_before,
        spaceAfter=space_after, alignment=align,
    )

S_TITLE    = make_style("title", size=22, color=C_ACCENT, space_after=4, align=1)
S_SUBTITLE = make_style("subtitle", size=11, color=C_GRAY, space_after=12, align=1)
S_H1       = make_style("h1", size=16, color=C_PRIMARY, space_before=14, space_after=6)
S_H2       = make_style("h2", size=13, color=C_BLUE, space_before=10, space_after=4)
S_BODY     = make_style("body", size=10, color=C_PRIMARY, space_after=4, leading=16)
S_BULLET   = make_style("bullet", size=10, color=C_PRIMARY, space_after=3, leading=15)
S_CALLOUT  = make_style("callout", size=10, color=HexColor("#333333"), leading=15)
S_SMALL    = make_style("small", size=9, color=C_GRAY, leading=13)
S_SCORE    = make_style("score", size=36, color=C_ACCENT, align=1, space_after=2)
S_SCORE_LB = make_style("score_label", size=11, color=C_GRAY, align=1, space_after=8)

# ---------- 辅助函数 ----------
def heading(text, style=S_H1):
    return Paragraph(text, style)

def body(text):
    return Paragraph(text, S_BODY)

def bullet(text):
    return Paragraph(f"• {text}", S_BULLET)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#dddddd"),
                       spaceBefore=6, spaceAfter=6)

def callout_box(text, bg=C_BLUE_BG):
    """带背景色的提示框"""
    t = Table([[Paragraph(text, S_CALLOUT)]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t

def score_card(score, label):
    """大号评分卡片"""
    elements = []
    elements.append(Paragraph(str(score), S_SCORE))
    elements.append(Paragraph(label, S_SCORE_LB))
    return elements

def data_table(headers, rows, col_widths=None):
    """通用数据表格"""
    style_h = ParagraphStyle("th", fontName=CN_FONT, fontSize=9,
                              textColor=C_WHITE, leading=13, alignment=1)
    style_d = ParagraphStyle("td", fontName=CN_FONT, fontSize=9,
                              textColor=C_PRIMARY, leading=13, alignment=1)
    data = [[Paragraph(h, style_h) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), style_d) for c in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), C_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    # 交替行背景
    for i in range(1, len(data)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), C_LIGHT_BG))
    t.setStyle(TableStyle(ts))
    return t

# ========== 构建文档 ==========
OUTPUT = "C:/Users/linkang/2026情人节活动复盘_评估报告.pdf"
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm,
    topMargin=18 * mm, bottomMargin=18 * mm,
)

story = []

# ===== 封面 =====
story.append(Spacer(1, 40 * mm))
story.append(Paragraph("2026 情人节活动复盘", S_TITLE))
story.append(Paragraph("独立评估报告", make_style("t2", size=16, color=C_PRIMARY, align=1, space_after=8)))
story.append(Spacer(1, 6 * mm))
story.append(Paragraph("评估日期：2026-03-19 ｜ 对标活动：2025情人节", S_SUBTITLE))
story.append(Spacer(1, 20 * mm))

# 综合评分
story.extend(score_card("A", "活动表现评级"))
story.append(callout_box(
    "总营收 $839,629，同比 +111%；付费ARPU $61.67，同比 +218.4%。"
    "活动结构健康，核心模块贡献集中，但 chaoR 流失风险需高度关注。"
))
story.append(Spacer(1, 8 * mm))

# 报告完善度评分
story.extend(score_card("A-", "报告完善度评级"))
story.append(callout_box(
    "7.7 / 10（初版 5.8 → 五版 7.7）。经过五轮迭代，累计修复 12 项数据问题 + 3 项可操作性改进。"
    "数据准确性、完整性、可操作性均已达标，无高严重度错误。"
))
story.append(PageBreak())

# ===== 一、总体评估 =====
story.append(heading("一、总体评估"))
story.append(hr())

story.append(heading("1.1 核心指标速览", S_H2))
story.append(data_table(
    ["指标", "2026情人节", "2025情人节", "同比变化", "评价"],
    [
        ["总营收",      "$839,629", "$397,996", "+111.0%", "优秀"],
        ["付费ARPU",    "$61.67",   "$19.36",   "+218.4%", "优秀"],
        ["ARPPU",       "$186.73",  "$68.92",   "+171.0%", "优秀"],
        ["付费率",      "33.0%",    "28.09%",   "+4.9pp",  "良好"],
        ["节日占比",    "49.3%",    "25.03%",   "+24.3pp", "优秀"],
    ],
    col_widths=[28*mm, 28*mm, 28*mm, 25*mm, 20*mm],
))
story.append(Spacer(1, 4*mm))
story.append(callout_box(
    "所有核心指标全面超越2025同期，且在近12个节日中排名前列（仅次于周年庆、圣诞节）。"
    "付费率 33% 处于历史高位，说明活动覆盖面和吸引力均达到较好水平。",
    C_GREEN_BG
))

story.append(Spacer(1, 4*mm))
story.append(heading("1.2 历史纵向定位", S_H2))
story.append(body(
    "在近 25 个节日活动中，2026情人节总营收排名第 6（前五为周年庆 $1.67M、科技节 $1.04M、"
    "深海节 $989K、复活节 $982K、圣诞节 $939K），ARPU 排名第 4。"
    "考虑到情人节并非年度旗舰档期，这一表现已属上乘。"
))

# ===== 二、分维度评估 =====
story.append(PageBreak())
story.append(heading("二、分维度评估"))
story.append(hr())

# 评分表
story.append(heading("2.1 五维评分", S_H2))
story.append(data_table(
    ["评估维度", "评分", "权重", "加权得分", "说明"],
    [
        ["营收增长",     "9.5/10", "30%", "2.85", "同比+111%，远超预期"],
        ["付费深度",     "8.5/10", "20%", "1.70", "ARPPU $186.73，R级分层合理"],
        ["用户覆盖",     "8.0/10", "15%", "1.20", "付费率33%，xiaoR转化仍有空间"],
        ["活动结构",     "8.5/10", "20%", "1.70", "T1活动贡献96.8%，结构清晰"],
        ["可持续性",     "6.0/10", "15%", "0.90", "chaoR流失-18.6%，最大隐患"],
        ["综合",         "—",      "100%","8.35", "A 级（优秀）"],
    ],
    col_widths=[25*mm, 18*mm, 15*mm, 20*mm, 62*mm],
))

story.append(Spacer(1, 4*mm))
story.append(heading("2.2 营收结构评估", S_H2))
story.append(data_table(
    ["模块", "营收", "占比", "评价"],
    [
        ["小游戏",      "$339,622", "40.4%", "核心引擎，挖孔小游戏是MVP"],
        ["外显类",      "$277,033", "33.0%", "稳定贡献，机甲GACHA需迭代"],
        ["混合/养成",   "$222,974", "26.6%", "结构均衡，BP覆盖面广"],
    ],
    col_widths=[28*mm, 28*mm, 20*mm, 64*mm],
))
story.append(Spacer(1, 3*mm))
story.append(body(
    "三大模块占比 40:33:27，结构相对均衡。小游戏模块首次超越外显成为第一大收入来源，"
    "说明「广覆盖+高频复购」模型已跑通。"
))

# ===== 三、活动效率评估 =====
story.append(Spacer(1, 4*mm))
story.append(heading("2.3 活动效率评估", S_H2))
story.append(data_table(
    ["活动", "收入", "占比", "ARPU", "效率评级"],
    [
        ["挖孔小游戏",  "$243,319", "35.0%", "$54.12", "S — 绝对核心"],
        ["云上探宝",    "$125,495", "18.0%", "$27.91", "A — 需提升高R深度"],
        ["机甲GACHA",   "$75,801",  "10.9%", "$16.86", "B+ — 衰减明显"],
        ["节日大富翁",  "$75,618",  "10.9%", "$16.82", "A — 稳定贡献"],
        ["限时抢购",    "$54,615",  "7.9%",  "$12.15", "B+ — 中规中矩"],
        ["送花礼包",    "$50,610",  "7.3%",  "$11.26", "B — 窄覆盖高客单"],
        ["情人节BP",    "$47,665",  "6.9%",  "$10.60", "B+ — 覆盖面最广"],
    ],
    col_widths=[28*mm, 24*mm, 16*mm, 20*mm, 52*mm],
))

# ===== 四、风险评估 =====
story.append(PageBreak())
story.append(heading("三、风险评估"))
story.append(hr())

story.append(heading("3.1 chaoR 流失 — 最大风险", S_H2))
story.append(callout_box(
    "chaoR（超R）人数从圣诞节 1,108 人持续下降至情人节 875 人，降幅 -21.0%。"
    "这批用户贡献了 64.9% 的节日收入（$545,010），是绝对的收入支柱。",
    C_RED_BG
))
story.append(Spacer(1, 3*mm))
story.append(body("量化影响测算："))
story.append(bullet("当前 chaoR ARPU = $475.58/人"))
story.append(bullet("若 chaoR 继续以每节日 -5% 速度流失，3个节日后约 750 人"))
story.append(bullet("仅 chaoR 流失带来的收入缺口 ≈ $59,448/节日（约 -7.1%）"))
story.append(bullet("叠加 ARPPU 可能的疲劳衰减，实际影响可能更大"))

story.append(Spacer(1, 4*mm))
story.append(heading("3.2 结构性风险", S_H2))
story.append(bullet("送花礼包 chaoR 占比 91.6%、节日大富翁 78.3%、机甲GACHA 73.5% — 极度依赖头部"))
story.append(bullet("xiaoR 付费率仅 11.2%（vs 全体 33%），转化漏斗存在断层"))
story.append(bullet("机甲GACHA 从巅峰 $150K 下滑至 $75K（-50%），生命周期进入衰退期"))

story.append(Spacer(1, 4*mm))
story.append(heading("3.3 风险矩阵", S_H2))
story.append(data_table(
    ["风险项", "影响程度", "发生概率", "风险等级", "应对建议"],
    [
        ["chaoR持续流失",     "极高", "高",   "P0", "专项召回+专属内容"],
        ["机甲GACHA衰退",     "中",   "高",   "P1", "5月换投放形式"],
        ["xiaoR转化低",       "中",   "中",   "P1", "低价入门礼包引导"],
        ["节日疲劳效应",      "中",   "中",   "P2", "控制节奏，差异化内容"],
    ],
    col_widths=[30*mm, 20*mm, 20*mm, 18*mm, 52*mm],
))

# ===== 五、亮点与建议 =====
story.append(PageBreak())
story.append(heading("四、亮点总结"))
story.append(hr())

story.append(bullet(
    "挖孔小游戏验证了「多SKU分层定价 + 高频复购」模型，48个SKU、人均3.9次购买，"
    "是可复制的标杆设计"
))
story.append(bullet(
    "付费率 33% 创情人节档期历史新高（2025仅28.09%），说明活动入口和引导优化有效"
))
story.append(bullet(
    "节日礼包占总收入 49.3%，较2025的25.03%大幅提升，节日内容的付费吸引力显著增强"
))
story.append(bullet(
    "付费节奏均匀（前8天33.3%、中8天45.2%、后8天30.5%），没有出现首日冲高后断崖式下跌"
))
story.append(bullet(
    "zhongR ARPU $30.70 同比增长 +109%（2025: $14.67），中层付费深度明显提升"
))

story.append(Spacer(1, 6*mm))
story.append(heading("五、优化建议"))
story.append(hr())

story.append(heading("5.1 P0 — 立即行动", S_H2))
story.append(bullet(
    "chaoR 召回计划：建立流失预警机制，对连续2个节日未付费的 chaoR 启动定向召回"
    "（专属礼包、1v1运营触达）"
))
story.append(bullet(
    "chaoR 专属内容：考虑增加高价值限定内容（如限量皮肤、专属称号），"
    "提升 chaoR 的情感绑定和沉没成本"
))

story.append(heading("5.2 P1 — 下期落地", S_H2))
story.append(bullet(
    "云上探宝深度优化：当前 ARPPU $17.57 仅为机甲GACHA的 1/3，"
    "建议增加成就礼包层级，拉升高R参与深度"
))
story.append(bullet(
    "机甲GACHA 换新：5月更换投放形式，8月升级皮肤品质，"
    "打破当前的审美疲劳和付费衰减"
))
story.append(bullet(
    "xiaoR 转化提升：设计 $1-$5 低门槛入门礼包，降低首次付费心理门槛，"
    "目标将 xiaoR 付费率从 11.2% 提升至 15%+"
))

story.append(heading("5.3 P2 — 中期规划", S_H2))
story.append(bullet(
    "小游戏矩阵扩展：挖孔小游戏已验证成功，可探索更多小游戏玩法"
    "（如消除、跑酷等），形成小游戏付费矩阵"
))
story.append(bullet(
    "R级迁移通道：设计 zhongR → daR 的付费升级路径，"
    "通过累计消费奖励和阶梯解锁机制，推动中层用户向上迁移"
))

# ===== 六、报告质量评估（基于第五版 2026-03-19） =====
story.append(PageBreak())
story.append(heading("六、原报告质量评估"))
story.append(hr())

story.append(callout_box(
    "以下是对 Notion 原报告第五版的完善度审查。本版主要改进了第10章优化建议的可操作性，"
    "新增了量化目标和分阶段里程碑。数据层面与第四版一致，无新增数据错误。",
    C_BLUE_BG
))
story.append(Spacer(1, 4*mm))

# 6.0 本轮改进项
story.append(heading("6.0 本轮改进内容", S_H2))
story.append(data_table(
    ["改进项", "上版状态", "本版状态"],
    [
        ["云上探宝量化目标",  "仅「高R参与深度不够」定性描述", "新增目标 ARPU 69.373（对标春节抽奖），6月落地 ✓"],
        ["机甲GACHA分阶段目标","仅「5月替换+8月替换」笼统描述",
         "拆为两阶段：5月投放优化→10W、8月套装升级→30W ✓"],
        ["P0 结构优化",       "P0含机甲GACHA迭代",            "机甲GACHA移至P1专项优化，P0聚焦稳态运营 ✓"],
    ],
    col_widths=[35*mm, 50*mm, 55*mm],
))

# 6.1 量化目标验证
story.append(Spacer(1, 4*mm))
story.append(heading("6.1 新增量化目标审查", S_H2))
story.append(callout_box(
    "严重程度：低 ｜ 类型：表述清晰度",
    C_YELLOW_BG
))
story.append(Spacer(1, 2*mm))

story.append(body("问题 1：机甲GACHA 提升比例与目标金额不完全匹配"))
story.append(bullet(
    "原文：「预计提升到50%到10W」— 当前 7.5W × 1.5 = 11.25W ≠ 10W"
))
story.append(bullet(
    "原文：「预计提升到200%到30W」— 若基于 5月后的 10W，10W × 3 = 30W ✓（+200%）"
))
story.append(bullet(
    "建议：第一阶段改为「预计提升33%到10W」或「预计提升50%到11W」，使百分比与金额一致"
))

story.append(Spacer(1, 3*mm))
story.append(body("问题 2：云上探宝目标参照物不在本报告内"))
story.append(bullet(
    "原文：「ARPPU仅17.57（春节GACHA的1/4）」— 比较对象从本报告的机甲GACHA（$60.84）"
    "改为春节GACHA，但春节GACHA的数据未在本报告中出现，读者无法验证"
))
story.append(bullet(
    "原文：「目标数据到春节抽奖的ARPU：69.373」— 精确到3位小数，且未标注是人次ARPPU还是节日ARPU"
))
story.append(bullet(
    "建议：补充春节GACHA的参考数据，或改回本报告内可验证的机甲GACHA作为对标"
))

# 6.2 数据交叉验证（与v4一致）
story.append(Spacer(1, 4*mm))
story.append(heading("6.2 数据交叉验证", S_H2))
story.append(callout_box(
    "数据层面与第四版一致，全量核验均通过，无新增数据错误",
    C_GREEN_BG
))

# 6.3 残留问题
story.append(Spacer(1, 4*mm))
story.append(heading("6.3 残留问题（低严重度）", S_H2))
story.append(data_table(
    ["问题", "严重度", "说明"],
    [
        ["「，7.2」笔误",         "低", "子节标题前多余顿号，五版均未修复"],
        ["第9章周收入差额",        "低", "$846,995 vs $839,629，差$7,366（0.88%）"],
        ["第4章付费ARPU列名",      "低", "同一列名在不同行分母不同"],
        ["第1章101W未拆解",        "低", "含返场内容，构成未说明"],
    ],
    col_widths=[35*mm, 15*mm, 90*mm],
))

# 6.4 缺失内容
story.append(Spacer(1, 4*mm))
story.append(heading("6.4 剩余提升方向", S_H2))
story.append(data_table(
    ["缺失项", "重要性", "说明"],
    [
        ["活动前目标/KPI",     "中", "没有预设目标，无法判断是否「达标」，仅能做同比"],
        ["新增 vs 回流付费",   "中", "不知道收入来自老用户复购还是新用户转化"],
        ["第5章缺 Stop 类建议","中", "只有 Keep/Optimize，框架不完整"],
    ],
    col_widths=[35*mm, 18*mm, 87*mm],
))
story.append(Spacer(1, 2*mm))
story.append(body(
    "注：chaoR 流失属于导量（用户获取）层面的问题，与活动设计质量无关，不纳入活动复盘评估范围。"
    "活动成本/ROI 因成本难以精确归因，暂不作为必要评估项。"
))

# 6.5 综合评分
story.append(Spacer(1, 4*mm))
story.append(heading("6.5 报告完善度评分", S_H2))
story.append(data_table(
    ["评估维度", "初版", "二版", "三版", "四版", "五版", "说明"],
    [
        ["数据完整性",   "7.0", "7.0", "8.5", "8.5", "8.5", "（—）"],
        ["数据一致性",   "5.0", "6.5", "6.0", "8.0", "8.0", "（—）"],
        ["结构规范性",   "5.0", "7.5", "7.5", "7.5", "7.5", "（—）"],
        ["分析深度",     "6.0", "6.0", "6.0", "6.0", "7.0", "chaoR流失归因属导量范畴，不纳入；缺Stop建议（+1.0）"],
        ["可操作性",     "6.0", "6.5", "6.5", "6.5", "7.5", "新增量化目标和分阶段里程碑（+1.0）"],
        ["综合",         "5.8", "6.7", "7.0", "7.4", "7.7", "A- 级"],
    ],
    col_widths=[24*mm, 11*mm, 11*mm, 11*mm, 11*mm, 11*mm, 61*mm],
))

story.append(Spacer(1, 4*mm))
story.append(callout_box(
    "总结：第五版在可操作性上有实质提升 — 云上探宝有了明确的 ARPU 目标（69.373），"
    "机甲GACHA 拆为两阶段里程碑（5月→10W、8月→30W），P0/P1 职责划分也更清晰。\n\n"
    "经过五轮迭代，累计修复 12 项数据问题 + 3 项可操作性改进，评分从 5.8 提升至 7.7。"
    "当前无高严重度错误，仅有少量表述清晰度问题（提升比例与金额不匹配、目标参照物缺失）。\n\n"
    "剩余提升方向：① 第5章补充 Stop 类建议 ② 增加活动前预设目标/KPI ③ 新增vs回流付费拆分。",
    C_YELLOW_BG
))

# ===== 七、结论 =====
story.append(Spacer(1, 6*mm))
story.append(heading("七、总结结论"))
story.append(hr())
story.append(callout_box(
    "活动表现评级 A（8.35/10）：营收、ARPU、付费率全面超越历史同期，"
    "活动结构健康，挖孔小游戏成为新的收入引擎。核心风险在于 chaoR 用户的持续流失，"
    "这批用户贡献了近 65% 的节日收入，建议列为 P0 优先级。\n\n"
    "报告质量评级 A-（7.7/10，初版 5.8 → 五版 7.7）：\n"
    "经过五轮迭代，数据准确性、完整性、可操作性均已达标。"
    "剩余提升空间集中在 Stop 类建议和活动前 KPI 设定。",
    C_YELLOW_BG
))

# ===== 页脚 =====
story.append(Spacer(1, 10*mm))
story.append(Paragraph("— 评估报告完 —", make_style("end", size=10, color=C_GRAY, align=1)))

# ---------- 生成 ----------
doc.build(story)
print(f"PDF 已生成: {OUTPUT}")
