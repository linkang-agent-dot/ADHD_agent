# -*- coding: utf-8 -*-
"""
马戏节「福箱通行证」BP 建表脚本（克隆巡游通行证 2251 全套）

用法:
    python build_circus_boxpass.py --dry-run     # 只报告，不写盘
    python build_circus_boxpass.py               # 落盘

设计要点（踩过的坑，改节日复用时别丢）:
  1. 只 append 新行，绝不重写既有行 —— 按原始文本行做字段替换再 join，
     既有行的引号/空列/LF 一律零扰动（csv 全表重写会改引号，gate 会 mismatch）。
  2. BP 奖励行 id = 组×100+等级 是硬契约（BattlePassScoreReward），
     违反 → 点升级无响应但奖励显示正常，极易误判成积分配错。
  3. 奖励组必须克隆出**专属 Reward 块**，不能直接指向源 BP 的 RewardID ——
     共享块被改 = 连源节日 BP 一起改。
  4. Reward 的 col0(seq) 必须 Python 全表精确查 max，禁 awk 数值比较（会漏报真 max）；
     同一 RewardID 内 seq 必须连续 → 整块 fresh 连续追加。
  5. BattlePassScore 是 16385 列病态宽表，克隆按源行**精确列数**，别 pad 到猜测宽。
"""
import argparse, csv, io, os, sys

REPO = r'C:\x3\wt_circus_float'

# ---------------- ID 分配（写前全部断言空闲）----------------
SRC_AO,     DST_AO     = '102251', '102250'
SRC_BPS,    DST_BPS    = '2251',   '2250'      # BattlePassScore / ActvOnline.ContentID
SRC_RG,     DST_RG     = '149',    '152'       # BattlePassScoreReward.Group
SRC_PACKS,  DST_PACKS  = ['130047', '130048'], ['130051', '130052']
REWARD_BASES = [('40371', '40381'), ('40372', '40382'), ('40373', '40383')]  # 免费/高级/至尊三轨
LEVELS = 20

DST_GROUP_ID   = '144'          # 主 hub（开箱 101026 所在），巡游通行证在 143 子 hub
DST_TOPRESOURCE = '1209|1210'   # 马戏门票|马戏勋章（巡游那条是 1057|1202 罗盘|代币）

NAME_CN  = '福箱通行证'
NAME_EN  = 'Lucky Box Pass'
DESC_CN  = '开启马戏福箱，解锁通行证豪华奖励！'
DESC_EN  = 'Open Circus Lucky Boxes to unlock luxurious pass rewards!'
PACK_TEXT = {   # dst_pack -> (备注col2, 主数据名col35, cn, en)
    '130051': ('马戏福箱-高级通行证', '马戏福箱高级通行证', '马戏福箱高级通行证', 'Lucky Box Advanced Pass'),
    '130052': ('马戏福箱-至尊通行证', '马戏福箱至尊通行证', '马戏福箱至尊通行证', 'Lucky Box Supreme Pass'),
}

F = {
    'ao':     'tsv/ActvOnline__ActvOnline.tsv',
    'bps':    'tsv/ActvBattlePassScore__BattlePassScore.tsv',
    'bpsr':   'tsv/ActvBattlePassScore__BattlePassScoreReward.tsv',
    'reward': 'tsv/Reward__Reward.tsv',
    'pack':   'tsv/Pack__Pack.tsv',
    'text':   'tsv/i18n/Text__Text.tsv',
}

HEADER_ROWS = 6   # rows[0..5] = cs / type / 注释×3 / 字段名


# ---------------- 原始行工具（零扰动）----------------
def read_lines(path):
    with io.open(os.path.join(REPO, path), 'r', encoding='utf-8', newline='') as f:
        txt = f.read()
    if txt and not txt.endswith('\n'):
        txt += '\n'
    return txt.split('\n')[:-1], txt   # 去掉末尾空串


def col0(line):
    return line.split('\t', 1)[0]


def find_line(lines, ident, col=0):
    """按第 col 列精确匹配，返回唯一一行；命中≠1 直接炸。"""
    hits = [l for l in lines[HEADER_ROWS:] if len(l.split('\t')) > col and l.split('\t')[col] == ident]
    if len(hits) != 1:
        raise SystemExit(f'!! {ident} 在第{col}列命中 {len(hits)} 行（期望恰好 1）')
    return hits[0]


def find_all(lines, ident, col):
    return [l for l in lines[HEADER_ROWS:] if len(l.split('\t')) > col and l.split('\t')[col] == ident]


def swap(line, changes):
    """changes = {列号: 新值}，其余字段原样保留（含引号/空列）。"""
    fs = line.split('\t')
    for i, v in changes.items():
        if i >= len(fs):
            raise SystemExit(f'!! 列号 {i} 超出行宽 {len(fs)}')
        fs[i] = v
    return '\t'.join(fs)


def assert_free(lines, ident, col, label):
    n = len(find_all(lines, ident, col))
    if n:
        raise SystemExit(f'!! {label} {ident} 已被占用（{n} 行），中止')


def append(path, new_lines, dry):
    full = os.path.join(REPO, path)
    if dry:
        print(f'   [dry-run] {path}  +{len(new_lines)} 行')
        return
    with io.open(full, 'a', encoding='utf-8', newline='') as f:
        for l in new_lines:
            f.write(l + '\n')
    print(f'   ✅ {path}  +{len(new_lines)} 行')


def pad(fields, width):
    return fields + [''] * (width - len(fields))


# ---------------- 主流程 ----------------
def main(dry):
    print('=== 福箱通行证 BP 建表 ===')
    print(f'repo = {REPO}\n')

    # ---------- 1. Reward：克隆 60 组专属奖励块 ----------
    rw_lines, _ = read_lines(F['reward'])
    seqs = [int(col0(l)) for l in rw_lines[HEADER_ROWS:] if col0(l).strip().isdigit()]
    if len(seqs) != len(set(seqs)):
        raise SystemExit('!! Reward col0 已有重复 seq，先修表')
    next_seq = max(seqs) + 1
    print(f'[1/6] Reward  当前 max seq={max(seqs)} → 新块从 {next_seq} 起')

    reward_new = []
    pairs = []          # (src_rid, dst_rid)
    for src_base, dst_base in REWARD_BASES:
        for lv in range(1, LEVELS + 1):
            pairs.append((f'{src_base}{lv:02d}', f'{dst_base}{lv:02d}'))

    for src_rid, dst_rid in pairs:
        assert_free(rw_lines, dst_rid, 1, 'Reward RewardID')
        srcs = find_all(rw_lines, src_rid, 1)
        if not srcs:
            raise SystemExit(f'!! 源 RewardID {src_rid} 不存在')
        for s in srcs:
            reward_new.append(swap(s, {0: str(next_seq), 1: dst_rid}))
            next_seq += 1
    print(f'      克隆 {len(pairs)} 组 / {len(reward_new)} 行（seq 连续 → {next_seq - 1}）')

    # ---------- 2. BattlePassScoreReward：Group 152，行 id=组×100+等级 ----------
    bpsr_lines, _ = read_lines(F['bpsr'])
    if find_all(bpsr_lines, DST_RG, 1):
        raise SystemExit(f'!! BattlePassScoreReward Group {DST_RG} 已存在')
    bpsr_new = []
    for lv in range(1, LEVELS + 1):
        src = find_line(bpsr_lines, f'{SRC_RG}{lv:02d}', 0)
        bpsr_new.append(swap(src, {
            0: f'{DST_RG}{lv:02d}',                 # 硬契约：组×100+等级
            1: DST_RG,
            4: f'{REWARD_BASES[0][1]}{lv:02d}',     # 免费轨
            5: f'{REWARD_BASES[1][1]}{lv:02d}',     # 高级轨
            6: f'{REWARD_BASES[2][1]}{lv:02d}',     # 至尊轨
        }))
    print(f'[2/6] BattlePassScoreReward  Group {DST_RG}  {DST_RG}01-{DST_RG}{LEVELS}  ({len(bpsr_new)} 档)')

    # ---------- 3. BattlePassScore：16385 列宽表 ----------
    bps_lines, _ = read_lines(F['bps'])
    assert_free(bps_lines, DST_BPS, 0, 'BattlePassScore')
    src = find_line(bps_lines, SRC_BPS, 0)
    width = len(src.split('\t'))
    bps_new = [swap(src, {0: DST_BPS, 1: '马戏福箱-BP',
                          4: '|'.join(DST_PACKS), 5: DST_RG})]
    print(f'[3/6] BattlePassScore  {DST_BPS}  任务源原样照抄  行宽={width}')

    # ---------- 4. Pack：两档解锁包 ----------
    pk_lines, _ = read_lines(F['pack'])
    pack_new = []
    for s_id, d_id in zip(SRC_PACKS, DST_PACKS):
        assert_free(pk_lines, d_id, 0, 'Pack')
        s = find_line(pk_lines, s_id, 0)
        memo, mdname, _, _ = PACK_TEXT[d_id]
        pack_new.append(swap(s, {0: d_id, 2: memo, 35: mdname}))
    print(f'[4/6] Pack  {DST_PACKS[0]}($9.99) / {DST_PACKS[1]}($19.99)  价格档位与公会礼物照抄')

    # ---------- 5. ActvOnline ----------
    ao_lines, _ = read_lines(F['ao'])
    assert_free(ao_lines, DST_AO, 0, 'ActvOnline')
    s = find_line(ao_lines, SRC_AO, 0)
    ao_new = [swap(s, {
        0: DST_AO, 1: '马戏福箱-BP', 2: NAME_CN, 3: DESC_CN,
        4: DST_BPS, 33: DST_TOPRESOURCE, 38: DST_GROUP_ID,
    })]
    print(f'[5/6] ActvOnline  {DST_AO}  ContentID={DST_BPS}  group={DST_GROUP_ID}  '
          f'TopResource={DST_TOPRESOURCE}  MailID/TC/RuleTips 照抄')

    # ---------- 6. Text i18n（cn+en 兜底，14 语走 x3-translation-automatic）----------
    tx_lines, _ = read_lines(F['text'])
    tw = len(tx_lines[5].split('\t'))
    existing = {col0(l) for l in tx_lines[HEADER_ROWS:]}
    text_rows = [
        (f'TXT_ActvOnline_ActvName_{DST_AO}', NAME_CN, NAME_EN),
        (f'TXT_ActvOnline_ActvDesc_{DST_AO}', DESC_CN, DESC_EN),
        (f'TXT_Pack_Name_{DST_PACKS[0]}', PACK_TEXT[DST_PACKS[0]][2], PACK_TEXT[DST_PACKS[0]][3]),
        (f'TXT_Pack_Name_{DST_PACKS[1]}', PACK_TEXT[DST_PACKS[1]][2], PACK_TEXT[DST_PACKS[1]][3]),
    ]
    text_new = []
    for key, cn, en in text_rows:
        if key in existing:
            raise SystemExit(f'!! Text key {key} 已存在')
        text_new.append('\t'.join(pad([key, 'AI', '', cn, en], tw)))
    print(f'[6/6] Text  {len(text_new)} 个自动 key（cn+en）  行宽={tw}')

    # ---------- 落盘 ----------
    print('\n--- 写盘 ---')
    append(F['reward'], reward_new, dry)
    append(F['bpsr'],   bpsr_new,   dry)
    append(F['bps'],    bps_new,    dry)
    append(F['pack'],   pack_new,   dry)
    append(F['ao'],     ao_new,     dry)
    append(F['text'],   text_new,   dry)
    print('\n完成。' + ('（dry-run，未写盘）' if dry else ' 下一步：本地 ExportTable 验证 → commit → jolt_verify'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    main(a.dry_run)
