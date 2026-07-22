# -*- coding: utf-8 -*-
# 马戏扭蛋机锚点礼包 5 档：Pack(PackType15) + Reward固定三件套 + ItemObtain type7 + Item.ObtainID 挂钩
import io
import re

BASE = r'C:\X3\wt_circus_float\tsv'
# 5 档: (新PackID, 克隆源链式包, 价格档, 券, 钻, VIP, 备注价)
TIERS = [
    ('13034', '13029', 20, 2500, 25, '4.99'),
    ('13035', '13030', 40, 5000, 50, '9.99'),
    ('13036', '13031', 80, 10000, 100, '19.99'),
    ('13037', '13032', 200, 25000, 250, '49.99'),
    ('13038', '13033', 400, 50000, 500, '99.99'),
]
IO_ROW_ID = '100413'   # 新 ItemObtain type7 行 id
REW_START = 15930170   # 新 Reward 行 id 起点


def load(p):
    return io.open(p, encoding='utf-8', newline='').read()


def save(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


# ---------- 1. Pack__Pack.tsv: 克隆 5 个 PackType15 锚点包 ----------
pk_path = BASE + r'\Pack__Pack.tsv'
pk = load(pk_path)
pk_lines = pk.split('\n')
pk_map = {ln.split('\t')[0]: ln for ln in pk_lines if ln.split('\t')[0].isdigit()}
eol = '\r' if pk_lines[5].endswith('\r') else ''
new_pack_lines = []
for newid, srcid, coin, gem, vip, price in TIERS:
    assert newid not in pk_map, ('Pack已存在', newid)
    c = pk_map[srcid].rstrip('\r').split('\t')
    c[0] = newid                       # ID
    c[2] = f'扭蛋高级券-锚点{price}'    # 备注
    c[9] = '15'                        # PackType 11->15
    c[13] = newid                      # Content(掉落包)
    c[20] = '0'                        # BuyCount 0=不限购
    new_pack_lines.append('\t'.join(c) + eol)
# 追加到文件末尾（去掉可能的尾空行再接）
while pk_lines and pk_lines[-1].strip() == '':
    pk_lines.pop()
pk_lines.extend(new_pack_lines)
save(pk_path, '\n'.join(pk_lines) + '\n')
print('Pack: 追加 5 个 PackType15 锚点包', [t[0] for t in TIERS])

# ---------- 2. Reward__Reward.tsv: 15 条固定三件套(Max留空=固定) ----------
rw_path = BASE + r'\Reward__Reward.tsv'
rw_lines = load(rw_path).split('\n')
reol = '\r' if rw_lines[6].endswith('\r') else ''
while rw_lines and rw_lines[-1].strip() == '':
    rw_lines.pop()
rid = REW_START
# 行格式(15列): id RewardID ItemType ItemID 备注 Min Max DropType DropPara _ _ _ _ _ DisplayOrder
def rrow(rid, pack, itemtype, itemid, note, num):
    cols = [str(rid), pack, '1', str(itemid), note, str(num), '', '1', '10000', '', '', '', '', '', str(rid)]
    return '\t'.join(cols) + reol
added = 0
for newid, srcid, coin, gem, vip, price in TIERS:
    rw_lines.append(rrow(rid, newid, 1, 1212, '高级扭蛋券', coin)); rid += 1
    rw_lines.append(rrow(rid, newid, 1, 1002, '钻石', gem)); rid += 1
    rw_lines.append(rrow(rid, newid, 1, 2022, 'VIP点数', vip)); rid += 1
    added += 3
save(rw_path, '\n'.join(rw_lines) + '\n')
print('Reward: 追加', added, '条固定三件套 (Max留空=固定显示)')

# ---------- 3. ItemObtain: 新增 type7 快捷购买行 ----------
io_path = BASE + r'\ItemObtain__ItemObtain.tsv'
io_lines = load(io_path).split('\n')
ieol = '\r' if io_lines[6].endswith('\r') else ''
# 克隆 712 行做模板(改 id/Value/图标/名字), 保列宽
row712 = next(ln for ln in io_lines if ln.split('\t')[0] == '712')
c = row712.rstrip('\r').split('\t')
c[0] = IO_ROW_ID
c[1] = '扭蛋高级券-锚点快捷购买'
c[3] = '535'                                   # Sort(1212是534)
c[4] = '7'                                      # ObtainType=7 礼包快捷购买
c[5] = '13034|13035|13036|13037|13038'          # Value=5锚点包
c[6] = 'DK_img_Activity_circus_gacha_icon'      # icon
c[7] = '高级扭蛋券'                              # 名字
while io_lines and io_lines[-1].strip() == '':
    io_lines.pop()
io_lines.append('\t'.join(c) + ieol)
save(io_path, '\n'.join(io_lines) + '\n')
print('ItemObtain: 追加 type7 行', IO_ROW_ID, 'Value=13034..13038')

# ---------- 4. Item 1212 ObtainID 挂钩(保留原有再加新行) ----------
it_path = BASE + r'\Item__Item.tsv'
it_lines = load(it_path).split('\n')
# ObtainID 列=10
hit = 0
for i, ln in enumerate(it_lines):
    cols = ln.rstrip('\r').split('\t')
    if cols and cols[0] == '1212':
        old = cols[10] if len(cols) > 10 else ''
        parts = [x for x in old.split('|') if x.strip()]
        if IO_ROW_ID not in parts:
            parts.append(IO_ROW_ID)
        cols[10] = '|'.join(parts)
        e = '\r' if ln.endswith('\r') else ''
        it_lines[i] = '\t'.join(cols) + e
        hit += 1
        print('Item 1212 ObtainID:', repr(old), '->', repr(cols[10]))
assert hit == 1, ('Item 1212 命中数', hit)
save(it_path, '\n'.join(it_lines))
print('全部写入完成')
