# -*- coding: utf-8 -*-
"""生成「世界杯竞猜 对阵生成器 + PACK 总表」单文件 HTML。
队号=FIFA三字码字母序1-48; 礼包号=894000+队号×10+档位(0免费/1=$4.99/2=$9.99/3=$19.99)。
数据已对 live Pack__Pack.tsv 验证(192包齐)。可复跑覆盖。"""
import io, sys, json, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ZH = {
"ALG":"阿尔及利亚","ARG":"阿根廷","AUS":"澳大利亚","AUT":"奥地利","BEL":"比利时","BIH":"波黑",
"BRA":"巴西","CAN":"加拿大","CIV":"科特迪瓦","COD":"刚果(金)","COL":"哥伦比亚","CPV":"佛得角",
"CRO":"克罗地亚","CUW":"库拉索","CZE":"捷克","ECU":"厄瓜多尔","EGY":"埃及","ENG":"英格兰",
"ESP":"西班牙","FRA":"法国","GER":"德国","GHA":"加纳","HAI":"海地","IRN":"伊朗",
"IRQ":"伊拉克","JOR":"约旦","JPN":"日本","KOR":"韩国","KSA":"沙特","MAR":"摩洛哥",
"MEX":"墨西哥","NED":"荷兰","NOR":"挪威","NZL":"新西兰","PAN":"巴拿马","PAR":"巴拉圭",
"POR":"葡萄牙","QAT":"卡塔尔","RSA":"南非","SCO":"苏格兰","SEN":"塞内加尔","SUI":"瑞士",
"SWE":"瑞典","TUN":"突尼斯","TUR":"土耳其","URU":"乌拉圭","USA":"美国","UZB":"乌兹别克斯坦",
}
codes = sorted(ZH.keys())
assert len(codes) == 48

# 对 live 验证
packf = pathlib.Path(r"C:\x3\gdconfig\tsv\Pack__Pack.tsv")
live = set()
for ln in packf.read_text(encoding='utf-8').split('\n'):
    if not ln: continue
    c = ln.split('\t')[0]
    if c.isdigit() and len(c) == 6 and c.startswith('894'):
        live.add(int(c))

teams = []
for i, code in enumerate(codes):
    num = i + 1
    base = 894000 + num * 10
    for t in range(4):
        assert base + t in live, f"MISSING {base+t} {code}"
    teams.append(dict(num=num, code=code, zh=ZH[code], base=base,
                      frame=80299 + num, emote=15419 + num,
                      badge=f"DK_WC_Badge_{code}", panel=f"DK_WC_TeamPanel_{code}"))
TEAMS_JS = json.dumps(teams, ensure_ascii=False)

TPL = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_tpl_对阵生成器.html").read_text(encoding='utf-8')
out = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\世界杯竞猜_对阵生成器.html")
out.write_text(TPL.replace("__TEAMS__", TEAMS_JS), encoding='utf-8')
print("VERIFIED 192 packs | teams", len(teams), "| WROTE", out)
