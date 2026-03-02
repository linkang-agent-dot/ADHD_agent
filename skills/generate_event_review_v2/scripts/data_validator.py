"""
数据校验模块 - 校验输入数据的完整性和合法性。

校验 7 大数据块的必填字段、数据条数、数值范围等。
behavior_data 为可选模块（空 Sheet 仅产生警告，不阻断流程）。
"""

from typing import List


def validate_input(data: dict) -> dict:
    """
    校验输入数据完整性和合法性。

    Args:
        data: 输入数据字典

    Returns:
        {"valid": True, "warnings": [...]} 或 {"valid": False, "errors": [...], "warnings": [...]}
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. 顶层结构检查（behavior_data 可选）
    required_blocks = [
        "meta", "reach_conversion",
        "payment_overview", "r_tier_payment", "payment_conversion",
        "core_reward", "gift_packages"
    ]
    optional_blocks = ["behavior_data"]

    for block in required_blocks:
        if block not in data:
            errors.append(f"缺少必填数据块: {block}")
    for block in optional_blocks:
        if block not in data:
            data[block] = {"metrics": []}
            warnings.append(f"[{block}] 数据块缺失，已自动补充空结构")

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    # 2. meta 校验
    _validate_meta(data.get("meta", {}), errors)

    # 3. reach_conversion 校验
    _validate_reach_conversion(data.get("reach_conversion", {}), errors)

    # 4. behavior_data 校验（可选：空数据仅警告）
    bd = data.get("behavior_data", {})
    bd_metrics = bd.get("metrics", [])
    if not isinstance(bd_metrics, list) or len(bd_metrics) < 1:
        warnings.append("[behavior_data] 行为数据为空，将跳过行为分析模块")
    else:
        _validate_behavior_data(bd, errors)

    # 5. payment_overview 校验
    _validate_payment_overview(data.get("payment_overview", {}), errors)

    # 6. r_tier_payment 校验
    _validate_r_tier_payment(data.get("r_tier_payment", {}), errors)

    # 7. payment_conversion 校验
    _validate_payment_conversion(data.get("payment_conversion", {}), errors)

    # 8. core_reward 校验
    _validate_core_reward(data.get("core_reward", {}), errors)

    # 9. gift_packages 校验
    _validate_gift_packages(data.get("gift_packages", {}), errors)

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}
    return {"valid": True, "warnings": warnings}


def _validate_meta(meta: dict, errors: List[str]):
    """校验 meta 基础信息"""
    if not meta.get("event_name"):
        errors.append("[meta] 缺少必填字段: event_name（活动名称）")
    if not meta.get("change_description"):
        errors.append("[meta] 缺少必填字段: change_description（本期改动简述）")


def _validate_reach_conversion(rc: dict, errors: List[str]):
    """校验触达转化数据"""
    stages = rc.get("stages", [])
    if not isinstance(stages, list) or len(stages) < 3:
        errors.append("[reach_conversion] stages 至少需要 3 层漏斗阶段，当前 {} 条".format(len(stages) if isinstance(stages, list) else 0))
        return

    for i, stage in enumerate(stages):
        if not stage.get("stage"):
            errors.append(f"[reach_conversion] 第 {i+1} 个阶段缺少 stage 名称")
        users = stage.get("users")
        if users is None or not isinstance(users, (int, float)) or users < 0:
            errors.append(f"[reach_conversion] 第 {i+1} 个阶段 users 无效（须为 >= 0 的数值）")

    # 校验漏斗单调递减（警告级别，不阻断）
    user_counts = [s.get("users", 0) for s in stages]
    for i in range(1, len(user_counts)):
        if user_counts[i] > user_counts[i - 1]:
            errors.append(
                f"[reach_conversion] 警告: 第 {i+1} 层人数({user_counts[i]}) > 第 {i} 层({user_counts[i-1]})，漏斗不单调"
            )


def _validate_behavior_data(bd: dict, errors: List[str]):
    """校验行为数据"""
    metrics = bd.get("metrics", [])
    if not isinstance(metrics, list) or len(metrics) < 1:
        errors.append("[behavior_data] metrics 至少需要 1 个行为指标")
        return

    for i, m in enumerate(metrics):
        if not m.get("metric_name"):
            errors.append(f"[behavior_data] 第 {i+1} 个指标缺少 metric_name")
        if m.get("current_value") is None:
            errors.append(f"[behavior_data] 第 {i+1} 个指标缺少 current_value")
        if not m.get("unit"):
            errors.append(f"[behavior_data] 第 {i+1} 个指标缺少 unit")


def _validate_payment_overview(po: dict, errors: List[str]):
    """校验付费整体数据"""
    ts = po.get("time_series", [])
    if not isinstance(ts, list) or len(ts) < 6:
        errors.append("[payment_overview] time_series 至少需要 6 条数据，当前 {} 条".format(len(ts) if isinstance(ts, list) else 0))
        return

    required_fields = ["event", "revenue", "pay_rate", "arpu", "arppu"]
    for i, item in enumerate(ts):
        for field in required_fields:
            if item.get(field) is None:
                errors.append(f"[payment_overview] time_series 第 {i+1} 条缺少字段: {field}")

        # 数值合法性
        if isinstance(item.get("revenue"), (int, float)) and item["revenue"] < 0:
            errors.append(f"[payment_overview] time_series 第 {i+1} 条 revenue 不能为负")
        pay_rate = item.get("pay_rate")
        if isinstance(pay_rate, (int, float)) and (pay_rate < 0 or pay_rate > 100):
            errors.append(f"[payment_overview] time_series 第 {i+1} 条 pay_rate 须在 0~100 之间")


def _validate_r_tier_payment(rtp: dict, errors: List[str]):
    """校验 R 级付费数据"""
    tiers = rtp.get("tiers", [])
    if not isinstance(tiers, list) or len(tiers) < 1:
        errors.append("[r_tier_payment] tiers 列表不能为空")

    ts = rtp.get("time_series", [])
    if not isinstance(ts, list) or len(ts) < 6:
        errors.append("[r_tier_payment] time_series 至少需要 6 条数据，当前 {} 条".format(len(ts) if isinstance(ts, list) else 0))
        return

    for i, item in enumerate(ts):
        if not item.get("event"):
            errors.append(f"[r_tier_payment] time_series 第 {i+1} 条缺少 event")
        data = item.get("data", {})
        if not isinstance(data, dict) or len(data) == 0:
            errors.append(f"[r_tier_payment] time_series 第 {i+1} 条 data 为空")
            continue
        for tier_name, tier_data in data.items():
            for field in ["revenue", "pay_rate", "arpu", "arppu"]:
                if tier_data.get(field) is None:
                    errors.append(f"[r_tier_payment] time_series 第 {i+1} 条 {tier_name} 缺少 {field}")


def _validate_payment_conversion(pc: dict, errors: List[str]):
    """校验付费转化数据"""
    current = pc.get("current", {})
    if not current:
        errors.append("[payment_conversion] 缺少 current 数据")
        return

    price_tiers = current.get("price_tiers", [])
    if not isinstance(price_tiers, list) or len(price_tiers) < 3:
        errors.append("[payment_conversion] current.price_tiers 至少需要 3 个价位，当前 {} 个".format(
            len(price_tiers) if isinstance(price_tiers, list) else 0
        ))
        return

    for i, pt in enumerate(price_tiers):
        for field in ["price", "purchases", "payers"]:
            val = pt.get(field)
            if val is None or not isinstance(val, (int, float)) or val < 0:
                errors.append(f"[payment_conversion] price_tiers 第 {i+1} 条 {field} 无效")


def _validate_core_reward(cr: dict, errors: List[str]):
    """校验核心奖励数据"""
    items = cr.get("items", [])
    if not isinstance(items, list) or len(items) < 1:
        errors.append("[core_reward] items 至少需要 1 条奖励数据")
        return

    for i, item in enumerate(items):
        if not item.get("reward_name"):
            errors.append(f"[core_reward] 第 {i+1} 条缺少 reward_name")
        if item.get("expected_value") is None:
            errors.append(f"[core_reward] 第 {i+1} 条缺少 expected_value")
        if item.get("actual_value") is None:
            errors.append(f"[core_reward] 第 {i+1} 条缺少 actual_value")
        if not item.get("unit"):
            errors.append(f"[core_reward] 第 {i+1} 条缺少 unit")


def _validate_gift_packages(gp: dict, errors: List[str]):
    """校验商业化礼包数据"""
    packages = gp.get("packages", [])
    if not isinstance(packages, list) or len(packages) < 1:
        errors.append("[gift_packages] packages 至少需要 1 个礼包")
        return

    for i, pkg in enumerate(packages):
        if not pkg.get("package_name"):
            errors.append(f"[gift_packages] 第 {i+1} 个礼包缺少 package_name")
        for field in ["price", "revenue", "payers"]:
            val = pkg.get(field)
            if val is None or not isinstance(val, (int, float)) or val < 0:
                errors.append(f"[gift_packages] 第 {i+1} 个礼包 {field} 无效")
