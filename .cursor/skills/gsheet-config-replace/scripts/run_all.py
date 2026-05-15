#!/usr/bin/env python3
"""逐个跑所有活动换皮，每个独立配置，不跨活动累积子表ID"""

import json, subprocess, sys, io, shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = Path(__file__).parent
RESKIN = SCRIPT_DIR / 'activity_reskin.py'

SHARED = {
    "item_mapping": {
        "11119497": "111111314", "11119517": "111111315", "11119518": "111111316",
        "11119519": "111111317", "11119553": "111111318", "11119495": "111111319",
        "11119496": "111111320", "11119503": "111111321", "11119504": "111111322",
        "11119505": "111111323", "11119506": "111111324", "11119515": "111111325",
        "11119516": "111111326", "11119558": "111111327", "11119507": "111111328",
        "11119521": "111111336", "11119522": "111111337", "111111302": "111111338",
        "11119498": "111111345", "11119499": "111111346", "11119500": "111111347",
        "11119501": "111111348", "11119502": "111111349", "11119549": "111111315",
        "11119550": "111111316",
    },
    "activity_mapping": {
        "21127302": "21127362", "21127350": "21127363", "21127351": "21127364",
        "21127355": "21127365", "21127356": "21127366", "21127357": "21127367",
        "21127358": "21127368", "21127359": "21127369", "21127360": "21127370",
        "21127361": "21127371", "211200205": "21127372", "211200206": "21127373",
        "211200207": "21127374", "211200208": "21127375", "211200209": "21127376",
        "211200210": "21127377", "211200211": "21127378", "211200212": "21127379",
        "211200213": "21127380", "211200214": "21127381", "211200215": "21127382",
        "211200036": "21127383", "211200282": "21127384", "211200283": "21127385",
    },
    "text_replacements": {"占星节": "拓荒节", "占星": "拓荒"},
    "preserve_ids": [
        "21127224","21127225","21127223","21127183",
        "211201001","211201002","211201003","211201010",
        "21121012","211200099","211200077","21127141",
        "21127152","21127207","211200129","21121648",
        "21510014","21534001",
    ],
}

ACTIVITIES = [
    ("21127302","21127362","拓荒节-2026-wonder恶狼-砸金蛋","event_labor_festival_hegemony_2026"),
    ("21127350","21127363","拓荒节-2026-BP集结奖励（基金）","event_labor_bp_buy_number_bp_2026"),
    # 21127351/21127364 大富翁 已跑过，跳过
    # 21127355/21127365 每日gacha 已跑过，跳过
    ("21127356","21127366","拓荒节-2026-节日自选周卡","event_fes_labor_time_card_2026"),
    ("21127357","21127367","拓荒节-2026-限时抢购","event_fes_labor_flash_sale_2026"),
    ("21127358","21127368","拓荒节-2026-行军表情礼包","event_labor_emoji_2026"),
    ("21127359","21127369","拓荒节-掉落转付费-掉落活动","event_labor_2026_2_drop"),
    ("21127360","21127370","拓荒节-掉落转付费-礼包","event_labor_2026_2_drop_pkg"),
    ("21127361","21127371","拓荒节-掉落转付费-主活动","event_labor_2026_shop"),
    ("211200205","21127372","拓荒节-2026-强消耗","labor_2026_strong_consume"),
    ("211200206","21127373","拓荒节-2026-七日任务活动","labor_2026_event_x2_sevenday"),
    ("211200207","21127374","拓荒节-2026-自选卡包","labor_2026_pkg"),
    ("211200208","21127375","拓荒节-2026-BP","labor_2026_labor_festival_bp"),
    ("211200209","21127376","拓荒节-2026-BP礼包","labor_2026_labor_festival_pkg"),
    ("211200210","21127377","拓荒节-2026-连锁礼包-schema3-5","labor_chain_pack_2026_schema3_5"),
    ("211200211","21127378","拓荒节-2026-行军表情礼包v2","event_labor_emoji_2026_v2"),
    ("211200212","21127379","拓荒节-2026-掉落","event_labor_drop_2026"),
    ("211200213","21127380","拓荒节-2026-节日累充","event_2026_labor_packge_name"),
    ("211200214","21127381","拓荒节-2026-gacha","event_labor_gacha_2026"),
    ("211200215","21127382","拓荒节-2026-gacha累计任务","event_labor_2026_reward_gacha"),
    ("211200036","21127383","最强城主（矿工）","event_x2_strongest_monkey_labor_2026"),
    ("211200282","21127384","最强城主（矿工）-第三期","event_x2_strongest_monkey_labor_3_2026"),
    ("211200283","21127385","最强城主（矿工）-第四期","event_x2_strongest_monkey_labor_4_2026"),
]

def main():
    total_rows = 0
    results = []

    for i, (src, tgt, comment, constant) in enumerate(ACTIVITIES):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(ACTIVITIES)}] {src} → {tgt} {comment}")
        print(f"{'='*60}")

        # 跳过已有输出
        out_dir = SCRIPT_DIR / f'output_{tgt}'
        if out_dir.exists() and (out_dir / 'summary.txt').exists():
            print(f"  ⏭️ 已有输出，跳过")
            results.append((tgt, comment, "跳过"))
            continue

        cfg = {
            "project": "X2",
            "source_activity_id": src,
            "target_activity_id": tgt,
            "target_comment": comment,
            "target_constant": constant,
            **SHARED
        }

        tmp = SCRIPT_DIR / f'_tmp_{tgt}.json'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False)

        r = subprocess.run(
            [sys.executable, str(RESKIN), str(tmp)],
            capture_output=True, encoding='utf-8', errors='replace',
            cwd=str(SCRIPT_DIR)
        )

        tmp.unlink(missing_ok=True)

        # 提取关键输出
        rows = 0
        for line in r.stdout.split('\n'):
            if '完成' in line and '行' in line:
                print(f"  {line.strip()}")
                try:
                    rows = int(line.split('共')[1].split('行')[0].strip())
                except: pass
            elif '失败' in line or '残留' in line:
                print(f"  {line.strip()}")

        if r.returncode != 0:
            print(f"  ❌ 失败: {r.stderr[:200]}")
            results.append((tgt, comment, "❌失败"))
        else:
            total_rows += rows
            results.append((tgt, comment, f"✅ {rows}行"))

    print(f"\n\n{'='*60}")
    print(f"  汇总")
    print(f"{'='*60}")
    for tgt, comment, status in results:
        print(f"  {tgt} {comment}: {status}")
    print(f"\n  总行数: {total_rows}")

if __name__ == '__main__':
    main()
