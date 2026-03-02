"""
兑换商店数据分析 - 主入口
支持命令行调用和模块导入两种方式
"""

import sys
import os
import json
import argparse

# 确保模块路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from data_parser import parse_text_input, parse_json, parse_excel, auto_categorize, validate_items
from analyzer import ShopExchangeAnalyzer
from chart_generator import ShopChartGenerator
from report_generator import ShopReportGenerator


def run_shop_analysis(
    items: list[dict] = None,
    raw_text: str = None,
    json_path: str = None,
    excel_path: str = None,
    activity_name: str = "活动商店",
    output_dir: str = "report_images/shop_exchange/",
    output_format: str = "both",
    custom_category_rules: dict = None,
    thresholds: dict = None,
) -> dict:
    """
    兑换商店数据分析主函数。

    参数:
        items: 已解析的道具数据列表 (list[dict])
        raw_text: 原始文本数据（Tab分隔表格）
        json_path: JSON 文件路径
        excel_path: Excel 文件路径
        activity_name: 活动名称
        output_dir: 输出目录
        output_format: 'notion' / 'wiki' / 'both' / 'markdown'
        custom_category_rules: 自定义分类规则
        thresholds: 分析阈值配置

    返回:
        dict: {
            'items': 解析后的道具数据,
            'analysis': 分析结果,
            'charts': 图表文件路径列表,
            'notion_content': Notion 格式报告,
            'notion_title': Notion 标题,
            'wiki_content': Wiki 格式报告,
            'markdown': Markdown 格式报告,
        }
    """

    # ============================
    # Step 1: 数据解析
    # ============================
    if items is None:
        if raw_text:
            items = parse_text_input(raw_text)
        elif json_path:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items = parse_json(data)
            if not activity_name or activity_name == "活动商店":
                activity_name = data.get("activity_name", activity_name)
        elif excel_path:
            items = parse_excel(excel_path)
        else:
            raise ValueError("必须提供 items / raw_text / json_path / excel_path 之一")

    # 自动分类
    items = auto_categorize(items, custom_category_rules)

    # 数据校验
    validation = validate_items(items)
    if not validation["valid"]:
        error_msg = "\n".join(validation["errors"])
        raise ValueError(f"数据校验失败:\n{error_msg}")

    if validation["warnings"]:
        for w in validation["warnings"]:
            print(f"[WARNING] {w}")

    print(f"[INFO] 成功解析 {len(items)} 条道具数据")

    # ============================
    # Step 2: 分析
    # ============================
    analyzer = ShopExchangeAnalyzer(items, thresholds)
    analysis = analyzer.run_all()
    print("[INFO] 分析完成")

    # ============================
    # Step 3: 图表生成
    # ============================
    os.makedirs(output_dir, exist_ok=True)
    chart_gen = ShopChartGenerator(items, analysis, output_dir)
    charts = chart_gen.generate_all()
    print(f"[INFO] 已生成 {len(charts)} 张图表")

    # ============================
    # Step 4: 报告生成
    # ============================
    report_gen = ShopReportGenerator(items, analysis, output_dir, activity_name)

    notion_content = ""
    notion_title = ""
    wiki_content = ""
    markdown_content = ""

    if output_format in ("notion", "both"):
        notion_content = report_gen.generate_notion()
        notion_title = report_gen.generate_title()
        print("[INFO] Notion 报告已生成")

    if output_format in ("wiki", "both", "markdown"):
        wiki_content = report_gen.generate_wiki()
        markdown_content = report_gen.generate_markdown()
        print("[INFO] Wiki/Markdown 报告已生成")

        # 保存本地 Markdown
        md_path = os.path.join(output_dir, "商店兑换数据分析报告.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"[INFO] 本地 Markdown 已保存: {md_path}")

    # ============================
    # 输出摘要
    # ============================
    ov = analysis["overview"]
    print(f"\n{'='*50}")
    print(f"商店兑换数据分析摘要")
    print(f"{'='*50}")
    print(f"总代币消耗: {ov['total_token_consumption']:,} ({int(ov['total_token_wan'])}万)")
    print(f"道具总数: {ov['total_items']}")
    print(f"饱和度最高: {ov['top_saturation_item']} ({ov['top_saturation_value']}%)")
    print(f"覆盖人次最广: {ov['top_users_item']} ({ov['top_users_value']:,}人)")
    print(f"图表保存至: {output_dir}")
    print(f"{'='*50}")

    return {
        "items": items,
        "analysis": analysis,
        "charts": charts,
        "notion_content": notion_content,
        "notion_title": notion_title,
        "wiki_content": wiki_content,
        "markdown": markdown_content,
    }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="兑换商店数据分析")
    parser.add_argument("--input", type=str, help="输入 JSON 文件路径")
    parser.add_argument("--excel", type=str, help="输入 Excel 文件路径")
    parser.add_argument("--output_dir", type=str, default="report_images/shop_exchange/", help="输出目录")
    parser.add_argument("--activity", type=str, default="活动商店", help="活动名称")
    parser.add_argument("--format", type=str, default="both", choices=["notion", "wiki", "both", "markdown"],
                       help="输出格式")

    args = parser.parse_args()

    result = run_shop_analysis(
        json_path=args.input,
        excel_path=args.excel,
        activity_name=args.activity,
        output_dir=args.output_dir,
        output_format=args.format,
    )

    return result


if __name__ == "__main__":
    main()
