"""
主入口脚本 - 编排完整的分析流程。

支持命令行调用和模块化调用两种方式。

用法：
    # 命令行 - 直接传入 Excel（推荐）
    python main.py --excel <Excel文件路径> --output_dir <输出目录>

    # 命令行 - 传入 JSON
    python main.py --input <JSON文件路径> --output_dir <输出目录>

    # 生成空白 Excel 模板
    python main.py --generate-template --output_dir <输出目录>

    # 模块调用
    from main import run_analysis
    result = run_analysis(input_data, output_dir)
"""

import argparse
import json
import os
import sys

# Windows: 强制 UTF-8 IO，避免 GBK 乱码
if sys.platform == "win32":
    for stream in [sys.stdout, sys.stderr, sys.stdin]:
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

# 确保可以导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_validator import validate_input
from analyzers import (
    ReachAnalyzer, BehaviorAnalyzer, PaymentOverviewAnalyzer,
    RTierAnalyzer, ConversionAnalyzer, RewardAnalyzer, PackageAnalyzer,
)
from charts import (
    ReachFunnelChart, BehaviorChart, PaymentOverviewChart,
    RTierChart, ConversionChart, RewardChart, PackageChart,
)
from report_generator import ReportGenerator


def run_analysis(input_data: dict, output_dir: str) -> dict:
    """
    主流程编排函数。

    Args:
        input_data: 标准化输入数据（会先校验）
        output_dir: 输出目录

    Returns:
        {
            "charts": [图表路径列表],
            "analysis_results": [AnalysisResult列表],
            "notion_content": "Notion报告内容",
            "notion_title": "Notion页面标题",
            "wiki_content": "Wiki报告内容"
        }
    """
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: 数据校验
    print("[1/5] 校验输入数据...")
    validation = validate_input(input_data)
    if not validation["valid"]:
        error_msg = "数据校验失败:\n" + "\n".join(validation["errors"])
        print(f"  [FAIL] {error_msg}")
        raise ValueError(error_msg)
    for w in validation.get("warnings", []):
        print(f"  [WARN] {w}")
    print("  [OK] 数据校验通过")

    # Step 2: 运行 7 个分析器
    print("[2/5] 执行七维分析...")
    analyzers = [
        ReachAnalyzer(),
        BehaviorAnalyzer(),
        PaymentOverviewAnalyzer(),
        RTierAnalyzer(),
        ConversionAnalyzer(),
        RewardAnalyzer(),
        PackageAnalyzer(),
    ]

    analysis_results = []
    for analyzer in analyzers:
        result = analyzer.analyze(input_data)
        analysis_results.append(result)
        severity_mark = {"正常": "[OK]", "关注": "[!]", "异常": "[X]", "严重": "[XX]"}
        print(f"  {severity_mark.get(result.severity, '?')} {result.module_name}: [{result.severity}] {result.conclusion}")

    # Step 3: 生成图表
    print("[3/5] 生成图表...")
    chart_generators = [
        (ReachFunnelChart, "触达分析"),
        (BehaviorChart, "行为分析"),
        (PaymentOverviewChart, "付费整体分析"),
        (RTierChart, "R级付费分析"),
        (ConversionChart, "付费转化分析"),
        (RewardChart, "数值设计评估"),
        (PackageChart, "礼包分析"),
    ]

    charts = []
    for ChartClass, module_name in chart_generators:
        matched = [r for r in analysis_results if r.module_name == module_name]
        if matched and matched[0].chart_data:
            try:
                chart = ChartClass(output_dir)
                path = chart.generate(matched[0].chart_data)
                if path:
                    charts.append(path)
                    print(f"  [OK] {os.path.basename(path)}")
                else:
                    print(f"  [-] {module_name}: 跳过（数据不足）")
            except Exception as e:
                print(f"  [FAIL] {module_name} 图表生成失败: {e}")
        else:
            print(f"  [-] {module_name}: 无图表数据")

    # Step 4: 生成报告
    print("[4/5] 组装报告...")
    generator = ReportGenerator(input_data, analysis_results, output_dir)
    notion_title = generator.generate_notion_title()
    notion_content = generator.generate_notion_content()
    wiki_content = generator.generate_wiki_content()
    print(f"  [OK] Notion 报告: {notion_title}")
    print(f"  [OK] Wiki 报告已生成")

    # Step 5: 保存报告文件
    print("[5/5] 保存报告文件...")

    notion_path = os.path.join(output_dir, f"{_safe_name(notion_title)}.md")
    with open(notion_path, "w", encoding="utf-8") as f:
        f.write(notion_content)
    print(f"  [OK] Notion: {notion_path}")

    wiki_path = os.path.join(output_dir, f"{_safe_name(notion_title)}_wiki.md")
    with open(wiki_path, "w", encoding="utf-8") as f:
        f.write(wiki_content)
    print(f"  [OK] Wiki: {wiki_path}")

    print(f"\n完成! 共生成 {len(charts)} 张图表, 2 个报告版本。")

    return {
        "charts": charts,
        "analysis_results": analysis_results,
        "notion_content": notion_content,
        "notion_title": notion_title,
        "wiki_content": wiki_content,
    }


def _safe_name(name: str) -> str:
    """将名称转为安全的文件名"""
    return name.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")


def _resolve_path(path: str) -> str:
    """
    解析文件路径，自动修复 Windows 中文路径编码问题。

    Windows 上 PowerShell/cmd 向 Python 传递包含中文的路径时，
    UTF-8 字节可能被系统代码页（GBK/cp936）错误解读，导致路径乱码。
    此函数通过三级策略修复：
    1. 直接检查路径是否存在
    2. 尝试常见编码组合还原
    3. 目录扫描 + 模拟编码错位匹配正确文件
    """
    if os.path.exists(path):
        return os.path.abspath(path)

    # 策略 2：尝试编码组合还原
    encoding_pairs = [
        ("gbk", "utf-8"),
        ("utf-8", "gbk"),
        ("cp1252", "utf-8"),
        ("utf-8", "cp1252"),
        ("latin-1", "utf-8"),
    ]
    for src, dst in encoding_pairs:
        try:
            fixed = path.encode(src).decode(dst)
            if os.path.exists(fixed):
                print(f"  [PATH-FIX] 编码还原成功: {src} -> {dst}")
                return os.path.abspath(fixed)
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue

    # 策略 3：目录扫描 + 模拟编码错位匹配
    parent = os.path.dirname(path)
    garbled_name = os.path.basename(path)

    # 尝试修复 parent 路径
    resolved_parent = parent
    if parent and not os.path.isdir(parent):
        for src, dst in encoding_pairs:
            try:
                fixed_parent = parent.encode(src).decode(dst)
                if os.path.isdir(fixed_parent):
                    resolved_parent = fixed_parent
                    break
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue

    if os.path.isdir(resolved_parent):
        # 对目录中每个文件，模拟「UTF-8 编码 → GBK 解读」的错位过程
        # Shell 层面与 Python codec 的替换字符不同（? vs U+FFFD），
        # 且 Shell 可能吞掉紧跟在无效字节后的 '.'，所以用模糊匹配
        def _normalize_garble(s):
            return s.replace("\ufffd", "?").replace(".", "")

        normalized_target = _normalize_garble(garbled_name)
        for real_name in os.listdir(resolved_parent):
            try:
                simulated = real_name.encode("utf-8").decode("gbk", errors="replace")
                if _normalize_garble(simulated) == normalized_target:
                    resolved = os.path.join(resolved_parent, real_name)
                    print(f"  [PATH-FIX] 目录扫描匹配成功: {real_name}")
                    return os.path.abspath(resolved)
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue

        # 兜底：扩展名匹配（只有 1 个同类型文件时可用）
        ext = os.path.splitext(garbled_name)[1].lower()
        if not ext:
            for try_ext in [".xlsx", ".xls", ".json", ".csv"]:
                if garbled_name.lower().endswith(try_ext[1:]):
                    ext = try_ext
                    break
        if ext:
            candidates = [f for f in os.listdir(resolved_parent)
                          if f.lower().endswith(ext)]
            if len(candidates) == 1:
                resolved = os.path.join(resolved_parent, candidates[0])
                print(f"  [PATH-FIX] 扩展名唯一匹配: {candidates[0]}")
                return os.path.abspath(resolved)
            elif len(candidates) > 1:
                print(f"  [WARN] 目录下有 {len(candidates)} 个 {ext} 文件，无法自动定位")

    return os.path.abspath(path)


def _fix_new_path(path: str) -> str:
    """
    修复尚不存在的目标路径（如 output_dir）的中文编码问题。

    与 _resolve_path 不同，此路径可能尚未被创建，
    因此不能用 os.path.exists() 验证，而是通过反向编码还原。
    """
    if os.path.exists(path):
        return os.path.abspath(path)

    # 尝试反向编码修复
    encoding_pairs = [
        ("gbk", "utf-8"),
        ("utf-8", "gbk"),
        ("cp1252", "utf-8"),
    ]
    for src, dst in encoding_pairs:
        try:
            fixed = path.encode(src).decode(dst)
            parent = os.path.dirname(fixed)
            if not parent or os.path.isdir(parent):
                print(f"  [PATH-FIX] 输出路径编码修复: {os.path.basename(fixed)}")
                return os.path.abspath(fixed)
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue

    return os.path.abspath(path)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="活动复盘报告生成器 V2")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--excel", help="输入 Excel 文件路径（推荐，自动解析+校验+分析）")
    group.add_argument("--input", help="输入数据 JSON 文件路径")
    group.add_argument("--generate-template", action="store_true", help="生成 Excel 模板")
    parser.add_argument("--output_dir", required=True, help="输出目录")
    args = parser.parse_args()

    if args.generate_template:
        from excel_handler import generate_template
        output_dir = _fix_new_path(args.output_dir)
        template_path = os.path.join(output_dir, "event_review_v2_template.xlsx")
        path = generate_template(template_path)
        print(f"Excel 模板已生成: {path}")
        return

    if args.excel:
        # Excel 一步到位流程：解析 + 校验 + 补算 + 分析 + 报告
        from excel_handler import parse_excel, save_as_json
        excel_path = _resolve_path(args.excel)
        output_dir = _fix_new_path(args.output_dir)
        print(f"[0/5] 解析 Excel: {excel_path}")
        data = parse_excel(excel_path)
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, "input_data.json")
        save_as_json(data, json_path)
        print(f"  [OK] 数据已保存: {json_path}")
    else:
        # JSON 输入
        input_path = _resolve_path(args.input)
        output_dir = _fix_new_path(args.output_dir)
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # 运行分析
    result = run_analysis(data, output_dir)


if __name__ == "__main__":
    main()
