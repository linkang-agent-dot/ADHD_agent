# -*- coding: utf-8 -*-
import os, shutil, glob, re

tsv = r'C:\x3\gdconfig\tsv\Personalize__PersonalizeAvatarFrameCfg.tsv'
final_dir = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL'

# 48队三字码(以FINAL目录实际落地为准) -> (国家中文, 头像框名 世界杯+国家风格)
NAMES = {
 'BRA':('巴西','桑巴军团'),'ARG':('阿根廷','潘帕雄鹰'),'FRA':('法国','高卢雄鸡'),
 'GER':('德国','日耳曼战车'),'ESP':('西班牙','红色斗牛士'),'ENG':('英格兰','三狮之环'),
 'POR':('葡萄牙','五盾之心'),'NED':('荷兰','橙衣军团'),'BEL':('比利时','欧陆红魔'),
 'URU':('乌拉圭','天蓝荣光'),'MEX':('墨西哥','阿兹特克鹰'),'USA':('美国','星条之环'),
 'JPN':('日本','蓝色武士'),'KOR':('韩国','太极之虎'),'AUS':('澳大利亚','袋鼠之环'),
 'CRO':('克罗地亚','格子军团'),'SUI':('瑞士','十字劲旅'),'MAR':('摩洛哥','阿特拉斯雄狮'),
 'SEN':('塞内加尔','特兰加雄狮'),'GHA':('加纳','黑色之星'),'CIV':('科特迪瓦','非洲大象'),
 'NGA_PLACEHOLDER':('',''),  # 占位防误用,实际无
 'EGY':('埃及','法老雄鹰'),'ALG':('阿尔及利亚','沙漠之狐'),'TUN':('突尼斯','迦太基之鹰'),
 'IRN':('伊朗','波斯之环'),'KSA':('沙特','绿鹰之环'),'QAT':('卡塔尔','栗红之环'),
 'IRQ':('伊拉克','美索之环'),'JOR':('约旦','契斯特之环'),'UZB':('乌兹别克','白狼之环'),
 'COL':('哥伦比亚','黄色咖啡'),'ECU':('厄瓜多尔','赤道之环'),'PAR':('巴拉圭','瓜拉尼之环'),
 'PAN':('巴拿马','运河之环'),'CAN':('加拿大','枫叶之环'),'CRC_PLACEHOLDER':('',''),
 'NOR':('挪威','北欧海盗'),'SWE':('瑞典','北欧蓝黄'),'SCO':('苏格兰','蓟花之环'),
 'AUT':('奥地利','阿尔卑斯之鹰'),'CZE':('捷克','波西米亚之环'),'BIH':('波黑','巴尔干之龙'),
 'NZL':('新西兰','全白之环'),'RSA':('南非','彩虹之国'),'COD':('刚果金','豹之环'),
 'CPV':('佛得角','蓝色海角'),'CUW':('库拉索','加勒比之蓝'),'HAI':('海地','加勒比之环'),
}

# 实际落地的三字码(规范名)
codes = sorted(set(re.search(r'WC_([A-Z]{3})\.png$', os.path.basename(f)).group(1)
                   for f in glob.glob(os.path.join(final_dir, 'Img_Player_AvatarFrame_WC_*.png'))
                   if re.search(r'WC_[A-Z]{3}\.png$', os.path.basename(f))))
print('落地队数', len(codes), codes)

# 统一字段
REMARK = '所有水手攻击 <color=#00B309>{0}</color>'
UNLOCK = '1'
PROPTYPE = '220000'   # 所有水手攻击
PROPNUM = '50'        # 0.5% = 万分比50
POWER = '20000'
SOURCE = '竞猜礼包获取'

# 读现有,确定起始ID/Order
with open(tsv, encoding='utf-8') as f:
    lines = f.read().split('\n')
# 数据行从第9行(index8)起,最后一非空数据行
data_rows = [l for l in lines[8:] if l.strip()]
last = data_rows[-1].split('\t')
start_id = int(last[0]) + 1      # 10028
start_order = int(last[2]) + 1   # 28
print('起始ID', start_id, '起始Order', start_order)

# 列序: ID 备注 Order Unlock ImgRes SourceDesc PropType PropNum Power Name FramePrefab (11列)
new_lines = []
for i, c in enumerate(codes):
    nm = NAMES.get(c)
    name = nm[1] if nm and nm[1] else c  # 兜底用码
    row = [str(start_id+i), REMARK, str(start_order+i), UNLOCK,
           f'DK_Img_Player_AvatarFrame_WC_{c}', SOURCE,
           PROPTYPE, PROPNUM, POWER, name, '']
    assert len(row) == 11, f'列数错 {c}'
    new_lines.append('\t'.join(row))

# 备份
shutil.copy(tsv, tsv + '.bak_wc48')
# append (保持文件结尾)
out = [l for l in lines]
# 去掉尾部空行再接
while out and out[-1].strip() == '':
    out.pop()
out.extend(new_lines)
with open(tsv, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(out) + '\n')

# 校验
with open(tsv, encoding='utf-8') as f:
    chk = [l for l in f.read().split('\n') if l.strip()]
bad = [l.split('\t')[0] for l in chk[8:] if len(l.split('\t')) != 11]
print('写入', len(new_lines), '行 | 列数异常行', bad)
print('新ID段', new_lines[0].split(chr(9))[0], '~', new_lines[-1].split(chr(9))[0])
