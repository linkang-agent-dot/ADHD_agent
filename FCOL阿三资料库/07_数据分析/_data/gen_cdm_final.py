# -*- coding: utf-8 -*-
"""永恒后腰评价·定稿版页面（骨架=gen_cm_final.py，换权重表+官方位置集）
公式(用户逐档裁定,2026-07-27):
  终分 = [Σ(属性档位分×档位权重) + 最优特训增益] × 逆足系数
  档位分: 显示值>=165→4(07-28上调) / >=155→2 / >=145→1 / <145→0
  权重(三档制,用户砍掉x4与x0.5): 抢断·拦截·人盯人·强壮·平衡·短传·控球x3
        | 速度·加速·体力·反应·远射·射门力量·盘带·灵活·长传x2
        | 视野·侵略性·铲断·弧线·射术·冷静·站位·头球·弹跳·凌空x1 | 传中·任意球·点球x0
  特训: 全卡+5点/单项<=2点, 背包求最大档位增益
  逆足: 5逆x1.0 / 4逆x0.95 / 3逆x0.90（全体系最宽）
  口径: 接口裸值 +3显示 +8卡强化15 +球员等级4(假设待确证) +队套6 = +28
全员(68人非门将)都算后腰分, >=80进榜+正牌后腰不足80也列出(灰行警示)。CM中场客串=近亲参考。
"""
import json, os, itertools
SP = os.path.dirname(os.path.abspath(__file__))
full = json.load(open(os.path.join(SP, 'el_tm_attrs_full.json'), encoding='utf-8'))
el_list = json.load(open(os.path.join(SP, 'el_list.json'), encoding='utf-8'))['db']
stats = json.load(open(os.path.join(SP, 'el_stats.json'), encoding='utf-8'))
uid2 = {p['uid']: p['name'] for p in el_list}
info = {}
flair = {}
for u, r in stats.items():
    if u in uid2:
        pl = r['player']
        info[uid2[u]] = (int(pl['foot_weak']), pl['height'], pl['weight'], pl.get('bodytype_name', ''))
        flair[uid2[u]] = int(pl.get('skill_level') or 0)
B = 28
OFFPOS = ('CDM',)
TIERS = {3: ['standingtackle', 'interceptions', 'marking', 'strength', 'balance', 'shortpassing', 'ballcontrol'],
         2: ['sprintspeed', 'acceleration', 'stamina', 'reactions', 'longshots', 'shotpower', 'dribbling', 'agility', 'longpassing'],
         1: ['vision', 'aggression', 'slidingtackle', 'curve', 'finishing', 'composure', 'positioning', 'headingaccuracy', 'jumping', 'volleys']}
W = {k: w for w, ks in TIERS.items() for k in ks}
MAXS = sum(W.values()) * 4
CN = {'sprintspeed': '速度', 'acceleration': '加速', 'finishing': '射术', 'shotpower': '射门力量', 'longshots': '远射',
      'positioning': '站位', 'volleys': '凌空', 'shortpassing': '短传', 'vision': '视野', 'curve': '弧线',
      'dribbling': '盘带', 'ballcontrol': '控球', 'agility': '灵活', 'balance': '平衡', 'reactions': '反应',
      'headingaccuracy': '头球', 'strength': '强壮', 'stamina': '体力', 'jumping': '弹跳', 'composure': '冷静', 'crossing': '传中'}
CN0 = {'longpassing': '长传', 'freekickaccuracy': '任意球', 'penalties': '点球', 'marking': '人盯人',
       'standingtackle': '抢断', 'interceptions': '拦截', 'slidingtackle': '铲断', 'aggression': '侵略性'}
CN_ALL = {**CN, **CN0}
NAME_CN = {'Cristiano Ronaldo': 'C罗', 'L. Messi': '梅西', 'T. Henry': '亨利', 'Eusébio': '尤西比奥', 'Ronaldo': '大罗',
 'H. Sánchez': '桑切斯', 'A. Shevchenko': '舍瓦', "S. Eto'o": '埃托奥', 'Roberto Carlos': '卡洛斯', 'Ferenc Puskás': '普斯卡什',
 'W. Rooney': '鲁尼', 'L. Suárez': '苏亚雷斯', 'Z. Zidane': '齐达内', 'Z. Ibrahimović': '伊布', 'Fernando Torres': '托雷斯',
 'M. van Basten': '范巴斯滕', 'K. Benzema': '本泽马', 'R. van Persie': '范佩西', 'Kaká': '卡卡', 'Raúl': '劳尔',
 'D. Drogba': '德罗巴', 'B. Cha': '车范根', 'F. Lampard': '兰帕德', 'Y. Touré': '图雷', 'Gabriel Batistuta': '巴蒂',
 'Neymar Jr': '内马尔', 'S. Gerrard': '杰拉德', 'D. Beckham': '贝克汉姆', 'F. Totti': '托蒂', 'Marcelo': '马塞洛',
 'E. Cantona': '坎通纳', 'R. van Nistelrooy': '范尼', 'E. Hazard': '阿扎尔', 'A. Shearer': '希勒', 'F. Rijkaard': '里杰卡尔德',
 'R. Baggio': '巴乔', 'H. Son': '孙兴慜', 'P. Nedvěd': '内德维德', 'L. Thuram': '图拉姆', 'Xavi': '哈维',
 'T. Müller': '穆勒', 'P. Vieira': '维埃拉', 'M. Owen': '欧文', 'Roberto Firmino': '菲尔米诺', 'O. Giroud': '吉鲁',
 'Iniesta': '伊涅斯塔', 'T. Kroos': '克罗斯', 'B. Schweinsteiger': '小猪', 'Rivaldo': '里瓦尔多', 'J. Zanetti': '萨内蒂',
 'M. Essien': '埃辛', 'Casemiro': '卡塞米罗', 'E. Petit': '佩蒂特', 'Cesc Fàbregas': '法布雷加斯', 'Fernando Hierro': '耶罗',
 'R. Ferdinand': '费迪南德', 'F. Cannavaro': '卡纳瓦罗', 'A. Nesta': '内斯塔', 'N. Vidić': '维迪奇', 'Marquinhos': '马尔基尼奥斯',
 'G. Chiellini': '基耶利尼', 'Guti': '古蒂', 'L. Matthäus': '马特乌斯', 'A. Pirlo': '皮尔洛',
 'O. Solskjaer': '索尔斯克亚'}
COMMENT_CDM = {
 '马特乌斯': 'CM近亲客串第1：128分超过全部正牌后腰；双五、小模型扫荡、攻防双高',
 '皮尔洛': 'CM近亲客串：99分，出球满档但防守轴和对抗只够及格，不建议单后腰',
 '索尔斯克亚': '中锋客串，仅数值参考',
 '卡洛斯': '客串第1（107.3）：防守轴+出球轴全在档位上——第六个位置进前五、第三次登顶，七边形实锤',
 '里杰卡尔德': '正牌第1(全场#2)：攻防均衡的全能后腰，特训+9；里杰>维埃拉第四次复现（与阿三后腰篇一致）',
 '图雷': '中场客串近亲：防守项+强壮全达标；⚠−中场指挥官特性手感笨（公式外）',
 '马塞洛': '边卫客串：手感型，防守轴反而是短板但双速体力补回',
 '维埃拉': '正牌第2(全场#5)：192cm大架子（瘦小模型注意），拦截扫荡型',
 '杰拉德': '中场客串近亲：攻强守足',
 '贝克汉姆': '客串：短传长传高，防守轴一般',
 '梅西': '客串仅参考——别真拿梅西打后腰',
 '齐达内': '客串仅参考',
 '图拉姆': '中卫客串：速度对抗双全，等中卫算法才是他主场',
 '兰帕德': '中场客串近亲',
 '小猪': '中场客串近亲：特训+9',
 'C罗': '客串仅参考',
 '鲁尼': '客串仅参考',
 '卡塞米罗': '正牌第3(全场#15)：纯防守型，出球轴（短传控球）拖了后腿——现代清道夫的数值画像',
 '亨利': '客串仅参考',
 '哈维': '中场客串近亲：出球轴满分防守轴不足',
 '克罗斯': '中场客串近亲',
 '尤西比奥': '客串仅参考',
 '大罗': '客串仅参考',
 '苏亚雷斯': '客串仅参考',
 '普斯卡什': '客串仅参考',
 '萨内蒂': '边卫客串：防守+体力达标，正经能客串的类型',
 '伊布': '客串仅参考',
 '内德维德': '前腰客串：双源发动机防守面也不差',
 '埃辛': '正牌第4(全场#26)：均衡但档位强度平平',
 '本泽马': '客串仅参考',
 '坎通纳': '客串仅参考',
 '佩蒂特': '正牌第5(全场#29)：3逆×0.90最宽松档救回来的，全员过线的收尾者',
 '桑切斯': '客串仅参考',
 '卡卡': '客串仅参考',
 '耶罗': '中卫客串：3逆0.90下露头，出球型中卫的数值面',
 '费迪南德': '中卫客串：等中卫算法',
 '内斯塔': '中卫客串：等中卫算法',
 '欧文': '避雷',
 '菲尔米诺': '避雷',
 '吉鲁': '避雷',
}
COMMENT = COMMENT_CDM
_CM_COMMENT = {
 '图雷': '正牌第1=全场第1（133.5，七位置首个正牌登顶）：防守项×3+远射×4双吃；唯一坑=−中场指挥官特性手感笨（公式外），买前自查',
 '卡洛斯': '客串第2：射门力量/控球/平衡×4全是他的菜，4逆×0.90已扣',
 '杰拉德': '正牌第2(全场#3)：远射流双雄之一，×4档全兑现',
 '梅西': '客串',
 '马塞洛': '边卫客串：手感+体力型',
 '齐达内': '客串：手感组通吃',
 '亨利': '客串，特训+14',
 'C罗': '客串',
 '鲁尼': '客串：宽度型在中场公式里也在线',
 '兰帕德': '正牌第3(全场#10)：远射流双雄之二',
 '里杰卡尔德': '后腰客串头名：攻防均衡+特训+12，CDM里最像CM的',
 '苏亚雷斯': '客串，特训+14',
 '贝克汉姆': '客串：短传弧线高，4逆已扣',
 '尤西比奥': '客串',
 '内德维德': '前腰客串：远射双源在中场公式全兑现',
 '大罗': '客串',
 '伊布': '客串：射门力量控球高',
 '哈维': '正牌第4(全场#18)：传控轴心，4逆×0.90拖了一档',
 '维埃拉': '后腰客串：防守项×3受益',
 '克罗斯': '正牌第5(全场#20)：远射/短传/控球×4受益，5逆不扣——持仓稳',
 '普斯卡什': '客串，4逆已扣',
 '小猪': '正牌第6(全场#22)：特训+14全场前列把他拉回线上——买他=买练卡潜力',
 '坎通纳': '客串',
 '图拉姆': '中卫客串：速度对抗双全',
 '卡卡': '客串',
 '埃托奥': '客串',
 '桑切斯': '客串',
 '本泽马': '客串',
 '范佩西': '客串，特训+13',
 '托蒂': '客串',
 '内马尔': '客串',
 '德罗巴': '客串，特训+17全场最大',
 '范巴斯滕': '客串',
 '劳尔': '客串',
 '舍瓦': '客串，特训+12',
 '阿扎尔': '客串',
 '巴乔': '客串',
 '卡塞米罗': '后腰客串：纯防守型在中场公式里只能中游',
 '伊涅斯塔': '正牌第7(全场#39)：手感组高但×4档（远射射门力量）是他的短板——纯组织型在这版权重里吃亏',
 '巴蒂': '客串',
 '萨内蒂': '边卫客串',
 '埃辛': '后腰客串',
 '穆勒': '客串',
 '车范根': '客串',
 '希勒': '客串，4逆已扣',
 '范尼': '客串，4逆已扣',
 '佩蒂特': '后腰客串：3逆×0.75重扣',
 '雷乌斯': '客串',
 '孙兴慜': '客串',
 '耶罗': '中卫客串：3逆重扣',
 '托雷斯': '客串',
 '法布雷加斯': '正牌垫底(74.7)：全池中场最弱，档位全面不足+4逆——避雷',
 '欧文': '避雷',
 '菲尔米诺': '避雷',
 '吉鲁': '避雷',
}
_CAM2_COMMENT = {
 '梅西': '客串前腰全场第1——手感传球全满，前腰也能打',
 'C罗': '客串第2，双修王',
 '亨利': '客串第3',
 '卡洛斯': '客串第4：曾并列第1，4逆-5%压回来；短传152/视野141不高，全靠双速手感弧线堆分——"出球门槛"讨论主角，客串仅参考',
 '齐达内': '正牌第1(全场第5)：手感组几乎全165+的慢速大师，双速降三档后归位；特训+1.5成品卡',
 '图雷': '中场客串，远射强壮达标',
 '鲁尼': '客串，均衡',
 '杰拉德': '中场客串：远射射门力量在前腰公式里吃分',
 '大罗': '客串',
 '贝克汉姆': '客串：短传视野弧线全高，4逆扣完第10',
 '尤西比奥': '客串',
 '兰帕德': '中场客串，远射包吃分',
 '苏亚雷斯': '客串',
 '普斯卡什': '客串，技术流通吃，4逆已扣',
 '哈维': '中场客串：传球手感双满，双速二档拖累比中场算法小',
 '伊布': '客串：射门力量远射高',
 '里杰卡尔德': '后腰客串',
 '本泽马': '客串',
 '马塞洛': '客串',
 '卡卡': '正牌第2(全场#20)：速度红利在前腰算法里被砍(双速降三档)，从中场发动机变普通前腰——他更适合往边路/中场摆',
 '内马尔': '客串，手感组高',
 '范佩西': '客串',
 '埃托奥': '客串',
 '桑切斯': '客串',
 '内德维德': '正牌第3(全场#25)：特训+1.5又一张成品卡；远射双源在前腰公式里兑现，但基数撑不进头部',
 '劳尔': '客串',
 '托蒂': '客串：本该是前腰模板，档位强度不够',
 '巴乔': '客串：情怀分和数值分的差距在前腰位最刺眼',
 '坎通纳': '客串',
 '范巴斯滕': '客串',
 '克罗斯': '中场客串：短传视野长传高，双速沉底拖累小',
 '维埃拉': '后腰客串',
 '阿扎尔': '客串',
 '舍瓦': '客串：中锋专精，前腰用不上他的抢点包',
 '德罗巴': '客串',
 '巴蒂': '客串',
 '伊涅斯塔': '中场客串：手感组高但远射射门弱',
 '小猪': '中场客串',
 '托雷斯': '客串',
 '穆勒': '客串：站位视野包在前腰公式里也救不动双速',
 '里瓦尔多': '正牌第4但75.6跌破80线：3逆×0.85判死刑——古典左脚将在逆足制里没活路，情怀卡',
 '古蒂': '正牌垫底57：档位全面塌方，全池前腰最弱',
 '欧文': '避雷',
 '菲尔米诺': '避雷',
 '吉鲁': '避雷',
 '希勒': '客串',
 '范尼': '客串',
 '车范根': '客串',
}
_WG2_COMMENT = {
 '梅西': '边锋全场第一，反超C罗客串——双速+手感全满，边锋就是他的位置',
 'C罗': '客串边锋依然第2，双修王',
 '亨利': '客串第3，快马两头吃',
 '卡洛斯': '客串边锋全场第4=他进攻端最优解：传中/长传/强壮/双速全吃，比打中锋(第9)更合身',
 '尤西比奥': '客串，双修王之一',
 '大罗': '客串，盘带×3回来了，比中锋算法更吃他的招牌项',
 '普斯卡什': '客串边路意外合身(盘带手感全三档)，4逆已扣',
 '齐达内': '前腰客串边路第8——手感组通吃，就是不快',
 '鲁尼': '客串，均衡型哪里都能站',
 '苏亚雷斯': '客串，手感+终结双修',
 '埃托奥': '客串，快马通用',
 '桑切斯': '客串，小快灵天然适配边路',
 '贝克汉姆': '正牌第2：传中/弧线/长传全三档的传球机器，4逆-5%后仍稳——名次比中锋高15位，纯边路专精',
 '图雷': '中场客串：长传强壮达标+手感尚可，参考用',
 '卡卡': '前腰客串边路在线',
 '马塞洛': '边卫客串边锋，进攻属性齐',
 '兰帕德': '中场客串，长传远射包在边锋公式里吃分',
 '哈维': '中场里最吃边锋算法的(手感+传球)，但双速平庸',
 '内马尔': '正牌第3：特训+12大受益(一堆163卡线)，花式5星盘带流标杆',
 '杰拉德': '中场客串，参考',
 '阿扎尔': '正牌第4：手感组扎实，新特性红利在公式外再加一层',
 '舍瓦': '中锋专精，边锋名次掉15位——别拉边',
 '本泽马': '客串，均衡',
 '范佩西': '客串，阵地战属性在边路用不全',
 '伊布': '站桩型拉边=灾难，仅数值参考',
 '坎通纳': '客串，参考',
 '托蒂': '客串，参考',
 '托雷斯': '直线快马拉边功能重叠，不如留中路',
 '内德维德': '前腰客串，双源发动机边路也能踩',
 '劳尔': '客串，无尖属性边路更尴尬',
 '范巴斯滕': '禁区专精，拉边浪费',
 '车范根': '速度单核，拉边只剩跑',
 '里杰卡尔德': '后腰客串仅参考',
 '德罗巴': '支点拉边无意义，仅数值参考',
 '巴乔': '客串，手感在但速度撑不起边路',
 '克罗斯': '中场客串：长传弧线吃分，双速拖底',
 '孙兴慜': '正牌第5：特训+13全池前列(卡线怪)，但两榜都37名上下——数值层就是及格生，ID溢价自行判断',
 '伊涅斯塔': '中场客串，手感组高',
 '图拉姆': '中卫客串仅参考',
 '穆勒': '跑不动的空间阅读者，边路更没戏',
 '巴蒂': '重炮拉边浪费',
 '小猪': '中场客串，特训+15大',
 '维埃拉': '后腰客串仅参考',
 '范尼': '禁区之王拉边=自废，仅参考',
 '希勒': '上世纪炮台，拉边无意义',
 '里瓦尔多': '3逆-15%重扣，古典前腰在逆足制里吃大亏',
 '萨内蒂': '边卫客串，防守项达标进攻项平',
 '雷乌斯': '正牌第6，80.5压线："全员2档"体质——18项属性全在1-2档、零165零特训位(全池唯一+0)，市场低价=如实定价不是被低估',
 '马赫雷斯': '正牌第7未过80线：4逆-5%+手感组档位不足，花式5星救不回数值',
 '因西涅': '正牌垫底69.8：矮个快马但档位全面塌方，与职业选手避雷名单重合',
 '欧文': '两个位置都垫底，避雷',
 '菲尔米诺': '避雷',
 '吉鲁': '避雷',
}
_OLD2 = {
 'C罗_old': '没弱点，闭眼用。12项三档全场最多，唯一0档是短传',
 '梅西': '客串中锋全场第二——速度手感全满，但169cm/67kg瘦小模型没身体，数值行模型不行',
 '亨利': '又快又稳没人追得上，但188cm挂瘦小模型：有身高没对抗',
 '尤西比奥': '亨利平替，各项都齐，买到即巅峰',
 '大罗': '快+会带球，正面拿他没办法；中场指挥官手感在公式外，实战上限比名次高',
 '桑切斯': '小快灵全能，速度164特训1点解锁双速165',
 '舍瓦': '快+会抢点，就干中锋的活；一堆属性卡线，特训+10精确治愈，冲7逻辑成立',
 '埃托奥': '成品卡：属性全在档位正中，特训+0.5全场最低，买来就是这样不会更好',
 '卡洛斯': '后卫客串中锋比一半正牌强，168cm健硕小钢炮，速度射门强壮全有',
 '普斯卡什': '技术流古典前锋，特训+12能解锁双速165，但只有4逆(已扣5%)',
 '鲁尼': '啥都会啥都不顶尖，阵容缺哪补哪，当不了核心',
 '苏亚雷斯': '鲁尼偏射手版，射术弧线平衡三档',
 '齐达内': '大个子技术流客串支点',
 '伊布': '站桩支点，禁区里强跑不动；195cm/95kg全场最大架子，但体重被官方+了11kg，转身有隐性惩罚',
 '托雷斯': '直线快马功能单一，特训后双速满档',
 '范巴斯滕': '教科书终结者就干最后一下，双速平庸',
 '本泽马': '全场最平的分布，没有短板也没有记忆点',
 '范佩西': '阵地战射手（射术弧线控球凌空三档），反击用不上他',
 '卡卡': '前腰客串支点，速度带球都在线',
 '劳尔': '哪都不差哪都不尖，"劳尔悖论"的数值实体',
 '德罗巴': '重型支点，档位分布配不上身价人设；特训+12练前练后两张卡',
 '车范根': '极端速度单核：双速100%但技术56%宽度48%，跑得到拿不稳',
 '兰帕德': '中场客串支点意外能看，89kg大体格',
 '图雷': '数值能客串中锋，但-中场指挥官特性=手感笨(公式外老坑)',
 '巴蒂': '固定炮台：重炮三件套三档全场对抗组并列第一，双速拖后腿',
 '内马尔': '边锋客串，瘦小模型',
 '杰拉德': '中场客串支点，远射包在中锋公式里贬值',
 '贝克汉姆': '4逆已扣5%，客串仅参考',
 '托蒂': '技术底子在，档位强度不够的名气卡',
 '马塞洛': '边卫客串，速度手感型',
 '坎通纳': '四组均匀但全不高，低配版鲁尼',
 '范尼': '"全员163"体质：16项挤在157-164差一口气，三档仅3项+4逆。信165阈值论就绕开，不信就是被系统性低估',
 '阿扎尔': '边锋客串，手感组扎实',
 '希勒': '上世纪炮台，双速33%追不上现版本防线；特训+16全场最大但练完也中游',
 '里杰卡尔德': '后腰客串，对抗组高',
 '巴乔': '优雅但全面偏软，冷静是唯一三档',
 '孙兴慜': '正职左边锋，客串中锋88.5及格线上，等边锋算法才是主场',
 '内德维德': '前腰客串，远射红利在中锋公式里用不上',
 '图拉姆': '中卫客串到86分，速度对抗双全',
 '哈维': '170cm传球大师客串中锋纯属数值巧合，别真用',
 '穆勒': '空间阅读者跑不到自己算出来的空间：宽度71%全场前列vs双速33%',
 '维埃拉': '192cm瘦小竹竿，客串仅参考',
 '欧文': '这张卡官方就没给速度(162/163)，速度人设是别的赛季的印象；零三档+强壮139+4逆',
 '菲尔米诺': '工兵型伪九号，对抗组17%零三档，数值模型无处安放',
 '吉鲁': '全模型唯一双速交白卷(145不到)的中锋，纯桥头堡',
}
def tier(v):
    # 07-28: 165档3分->4分(145/155不变)
    return 4 if v >= 165 else 2 if v >= 155 else 1 if v >= 145 else 0
def best_patch(vals):
    items = []
    for k, v in vals.items():
        w = W.get(k, 0)
        if not w:
            continue
        for th in (145, 155, 165):
            if v < th <= v + 2:
                items.append((th - v, w * (2 if th == 165 else 1), CN_ALL[k], th))
                break
    best = (0, [])
    for r in range(1, len(items) + 1):
        for comb in itertools.combinations(items, r):
            if sum(i[0] for i in comb) <= 5:
                g = sum(i[1] for i in comb)
                if g > best[0]:
                    best = (g, list(comb))
    return best
PEN = {5: 1.0, 4: 0.95, 3: 0.90, 2: 0.80}
rows = []
detail = {}
for p in el_list:
    n = p['name']
    if p['pos1'] == 'GK':
        continue
    el = full[n]['EL']
    vals = {k: int(el['attr'][k]['value']) + B for k in W if k in el['attr']}
    base = sum(W[k] * tier(v) for k, v in vals.items())
    g, alloc = best_patch(vals)
    w5, h, wt, bt = info.get(n, (5, 0, 0, ''))
    fin = (base + g) * PEN.get(w5, 1.0)
    plan = '+'.join('%s%d点→%d' % (cn, c, th) for c, w, cn, th in alloc)
    rows.append((n, p['pos1'], w5, base, g, fin, fin / MAXS * 100, h, wt, bt, plan, int(el['salary'])))
    trained = {cn2: th2 for c2, w2, cn2, th2 in alloc}
    items = []
    for k in list(W) + [k2 for k2 in CN_ALL if k2 not in W]:
        if k not in el['attr']:
            continue
        v = int(el['attr'][k]['value']) + B
        w = W.get(k, 0)
        tv = trained.get(CN_ALL[k], 0)
        items.append([CN_ALL[k], v, tier(v), w, round(w * tier(v), 1), tv, tier(tv) if tv else 0])
    items.sort(key=lambda x: (-x[3], -x[4], -x[1]))
    detail[NAME_CN.get(n, n)] = {'items': items, 'base': base, 'gain': g, 'plan': plan or '无可训项',
                                 'w5': w5, 'pen': PEN.get(w5, 1.0), 'fin': round(fin, 1),
                                 'phy': '%dcm / %dkg / %s' % (h, wt, bt)}
# 工资定价线：只用8名正牌边锋拟合（样本小，残差仅参考）
_st = [(r[11], r[5]) for r in rows if r[1] in OFFPOS]
_N = len(_st)
_sx = sum(s for s, f in _st); _sy = sum(f for s, f in _st)
_sxx = sum(s * s for s, f in _st); _sxy = sum(s * f for s, f in _st)
SLOPE = (_N * _sxy - _sx * _sy) / (_N * _sxx - _sx * _sx)
INTC = (_sy - SLOPE * _sx) / _N
rows.sort(key=lambda r: -r[5])
trs = ''
for i, (n, pos, w5, base, g, fin, pct, h, wt, bt, plan, sal) in enumerate(rows, 1):
    if fin < 80 and pos not in OFFPOS:
        continue
    cn = NAME_CN.get(n, n)
    cross = '' if pos in OFFPOS else ' cross'
    low = ' low' if fin < 80 else ''
    res = fin - (INTC + SLOPE * sal)
    rcls = 'style="color:#5cff8f;font-weight:bold"' if res >= 7 else ('style="color:#ff7b7b;font-weight:bold"' if res <= -7 else 'style="color:#8b93a7"')
    trs += ('<tr class="r%s%s" onclick="pop(\'%s\')"><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td><td>%d逆</td>'
            '<td class="sc">%.1f</td><td>%.0f%%</td><td>%.1f<span class="tg">+%.1f</span></td>'
            '<td>%d</td><td %s>%+.1f</td>'
            '<td class="ph">%dcm/%dkg·%s</td><td class="pl">%s</td><td class="cm">%s</td></tr>'
            % (cross, low, cn, i, cn, n, pos, w5, fin, pct, base, g, sal, rcls, res, h, wt, bt, plan or '—', COMMENT.get(cn, '')))
# ===== vs 时刻 模块（与主榜同三档制145/155/165，两卡同权重同特训同逆足；含时刻独有卡） =====
TH4 = (145, 155, 165)  # 07-27用户裁定:时刻计分与永恒一致,135档作废
TMONLY_CN = {'Pelé': '贝利', 'D. Maradona': '马拉多纳', 'F. Beckenbauer': '贝肯鲍尔', 'J. Cruyff': '克鲁伊夫',
 'G. Müller': '盖德·穆勒', 'L. Matthäus': '马特乌斯', 'Garrincha': '加林查', 'Ronaldinho': '小罗',
 'Jairzinho': '雅伊尔济尼奥', 'P. Maldini': '马尔蒂尼', 'Zico': '济科', 'F. Baresi': '巴雷西', 'R. Gullit': '古利特',
 'G. Best': '乔治·贝斯特', 'B. Charlton': '博比·查尔顿', 'Cafu': '卡福', 'D. Bergkamp': '博格坎普',
 'Luís Figo': '菲戈', 'A. Pirlo': '皮尔洛', 'M. Ballack': '巴拉克', 'Carlos Alberto': '卡洛斯·阿尔贝托',
 'R. Koeman': '科曼', 'I. Rush': '拉什', 'A. Del Piero': '皮耶罗', 'P. Lahm': '拉姆', 'Xabi Alonso': '哈维·阿隆索',
 'K. Dalglish': '达格利什', 'P. Scholes': '斯科尔斯', 'M. Klose': '克洛泽', 'C. Puyol': '普约尔',
 'B. Moore': '博比·摩尔', 'Dunga': '邓加', 'C. Seedorf': '西多夫', 'C. Makélélé': '马克莱莱',
 'D. Trezeguet': '特雷泽盖', 'Park Ji Sung': '朴智星', 'R. Keane': '罗伊·基恩', 'M. Desailly': '德塞利',
 'H. Stoichkov': '斯托伊奇科夫', 'H. Crespo': '克雷斯波', 'F. Ribéry': '里贝里', 'G. Hagi': '哈吉',
 'Butragueño': '布特拉格诺', 'G. Lineker': '莱因克尔', 'M. Laudrup': '大劳德鲁普', 'L. Blanc': '布兰克',
 'G. Bale': '贝尔', 'G. Zambrotta': '赞布罗塔'}
def tier4(v):
    n = sum(1 for t in TH4 if v >= t)
    return 4 if n == 3 else n
def best_patch4(vals):
    items = []
    for k, v in vals.items():
        w = W.get(k, 0)
        if not w:
            continue
        for t in TH4:
            if v < t <= v + 2:
                items.append((t - v, w * (2 if t == 165 else 1), CN_ALL.get(k, k), t))
                break
    best = (0, [])
    for r in range(1, len(items) + 1):
        for comb in itertools.combinations(items, r):
            if sum(i[0] for i in comb) <= 5:
                g = sum(i[1] for i in comb)
                if g > best[0]:
                    best = (g, list(comb))
    return best
def score4(attrs, Bx, w5):
    vals = {k: int(attrs[k]['value']) + Bx for k in W if k in attrs}
    base = sum(W[k] * tier4(v) for k, v in vals.items())
    g, alloc = best_patch4(vals)
    return (base + g) * PEN.get(w5, 1.0), base, g, alloc, vals
def tm_detail(attrs, Bx):
    its = []
    for k in list(W) + [k2 for k2 in CN_ALL if k2 not in W]:
        if k not in attrs:
            continue
        v = int(attrs[k]['value']) + Bx
        w = W.get(k, 0)
        its.append([CN_ALL[k], v, tier4(v), w, round(w * tier4(v), 1)])
    its.sort(key=lambda x: (-x[3], -x[4], -x[1]))
    return its
tm_rows = []
dtl = {}
for p in el_list:
    n = p['name']
    rec = full[n]
    if not rec.get('TM') or p['pos1'] == 'GK':
        continue
    w5 = info.get(n, (5, 0, 0, ''))[0]
    t8, tb, tg, talloc, _ = score4(rec['TM']['attr'], 28, w5)
    e6 = score4(rec['EL']['attr'], 21, w5)[0]   # 永恒6卡=+3+8+4+6
    e8 = score4(rec['EL']['attr'], 28, w5)[0]
    tsal = int(rec['TM'].get('salary') or 0)
    esal = int(rec['EL']['salary'])
    cnm = NAME_CN.get(n, n)
    tm_rows.append((n, cnm, p['pos1'], t8, e6, e8, e8 - t8, tsal, esal, w5))
    dtl[cnm] = {'items': tm_detail(rec['TM']['attr'], 28), 'base': tb, 'gain': tg,
                'plan': '+'.join('%s%d点→%d' % (c2, c1, t2) for c1, w2, c2, t2 in talloc) or '无可训项',
                'w5': w5, 'pen': PEN.get(w5, 1.0), 'fin': round(t8, 1),
                'phy': '%scm / %skg' % (rec['TM'].get('height', '?'), rec['TM'].get('weight', '?'))}
TMONLY_PATH = os.path.join(SP, 'tm_only_attrs.json')
if os.path.exists(TMONLY_PATH):
    for n, rec in json.load(open(TMONLY_PATH, encoding='utf-8')).items():
        if rec.get('pos1') == 'GK':
            continue
        w5 = int(rec.get('db', {}).get('foot_weak') or 5)
        t8, tb, tg, talloc, _ = score4(rec['attr'], 28, w5)
        tsal = int(rec.get('salary') or 0)
        cnm = TMONLY_CN.get(n, n)
        tm_rows.append((n, cnm, rec.get('pos1', '?'), t8, None, None, None, tsal, None, w5))
        dtl[cnm] = {'items': tm_detail(rec['attr'], 28), 'base': tb, 'gain': tg,
                    'plan': '+'.join('%s%d点→%d' % (c2, c1, t2) for c1, w2, c2, t2 in talloc) or '无可训项',
                    'w5': w5, 'pen': PEN.get(w5, 1.0), 'fin': round(t8, 1),
                    'phy': '%scm / %skg · 时刻独有(无永恒版)' % (rec.get('height', '?'), rec.get('weight', '?'))}
tm_rows.sort(key=lambda r: -r[3])
tm_trs = ''
for i, (n, cn, pos, t8, e6, e8, d, tsal, esal, w5) in enumerate(tm_rows, 1):
    tq = t8 / tsal if tsal else 0
    if e8 is None:
        tm_trs += ('<tr class="tmo" onclick="popT(\'%s\')"><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td>'
                   '<td>%.1f</td><td>%d</td><td>%.2f</td>'
                   '<td>—</td><td>—</td><td>—</td><td>—</td><td style="color:#8b93a7">无永恒</td></tr>'
                   % (cn, i, cn, n, pos, t8, tsal, tq))
        continue
    dcls = ' style="color:#ff7b7b;font-weight:bold"' if d < 35 else (' style="color:#5cff8f"' if d >= 50 else '')
    eq = e8 / esal if esal else 0
    qcls = ' style="color:#5cff8f;font-weight:bold"' if tq > eq else ''
    tm_trs += ('<tr onclick="popT(\'%s\')"><td>%d</td><td class="nm">%s<span class="en">%s</span></td><td>%s</td>'
               '<td>%.1f</td><td>%d</td><td%s>%.2f</td>'
               '<td>%.1f</td><td>%.1f</td><td>%d</td><td>%.2f</td><td%s>%+.1f</td></tr>'
               % (cn, i, cn, n, pos, t8, tsal, qcls, tq, e6, e8, esal, eq, dcls, d))
html = ('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
'<title>永恒后腰评价·定稿版</title><style>'
'body{font-family:"Microsoft YaHei";background:#0f1420;color:#dde3ee;margin:0;line-height:1.55}'
'.wrap{max-width:1240px;margin:0 auto;padding:24px 14px 70px}'
'h1{color:#ffd35c;font-size:20px}h2{color:#7ec8ff;font-size:15px;margin-top:24px}'
'.note{color:#9aa3b8;font-size:12.8px;line-height:1.75;background:#151c2e;border-radius:8px;padding:12px 16px}'
'.note b{color:#ffd35c}'
'table{border-collapse:collapse;width:100%;font-size:12.4px;margin-top:10px}'
'th{background:#1d2740;color:#9fb4d8;padding:5px 7px;position:sticky;top:0}'
'td{padding:4px 7px;border-bottom:1px solid #1d2438;text-align:center}'
'td.nm{text-align:left;font-weight:bold;color:#fff;white-space:nowrap}'
'.en{display:block;font-weight:normal;color:#5c6579;font-size:10.5px}'
'td.sc{color:#5cff8f;font-weight:bold;font-size:13.5px}'
'td.cm{text-align:left;color:#c9d2e4;font-size:12px;max-width:330px}'
'td.pl{text-align:left;color:#8b93a7;font-size:11px;max-width:200px}'
'td.ph{color:#9aa3b8;font-size:11.5px;white-space:nowrap}'
'.tg{color:#ffd35c;font-size:10.5px;margin-left:3px}'
'tr.cross td.nm{color:#7ec8ff}'
'tr.low td{opacity:.55}'
'tbody tr{cursor:pointer}tbody tr:hover td{background:#1a2540}'
'#ov{display:none;position:fixed;inset:0;background:rgba(5,8,16,.82);z-index:50}'
'#md{position:fixed;top:4vh;left:50%;transform:translateX(-50%);width:min(680px,94vw);max-height:90vh;overflow-y:auto;'
'background:#141b2d;border:1px solid #2a3555;border-radius:10px;padding:18px 22px;z-index:51}'
'#md h3{color:#ffd35c;margin:0 0 4px;font-size:17px}'
'#md .sub{color:#8b93a7;font-size:12px;margin-bottom:10px}'
'#md table{font-size:12.3px}#md td,#md th{padding:2px 8px}'
'#md .t3{color:#5cff8f;font-weight:bold}#md .t4{color:#4dffc6;font-weight:bold}#md .t2{color:#dde3ee}#md .t1{color:#c9a44a}#md .t0{color:#ff7b7b}'
'tr.tmo td.nm{color:#e8b4ff}'
'#md .w0{opacity:.45}'
'#md .sum{margin-top:10px;background:#1d2740;border-radius:7px;padding:9px 13px;font-size:13px;line-height:1.9}'
'#md .sum b{color:#5cff8f}'
'#md .x{position:sticky;top:0;float:right;color:#8b93a7;cursor:pointer;font-size:20px;line-height:1}'
'</style></head><body><div class="wrap">'
'<h1>永恒后腰评价 · 定稿版（2026-07-27，用户逐档裁定权重）</h1>'
'<div class="note"><b>终分 = [ Σ(属性档位分 × 档位权重) + 最优特训增益 ] × 逆足系数</b><br>'
'档位分：显示值≥165→<b>4</b>（07-28上调） / ≥155→2 / ≥145→1 / ＜145→0（阈值机制：突破档位才算数，档内堆点无效）<br>'
'权重（<b>三档制</b>）：<b>抢断·拦截·人盯人·强壮·平衡·短传·控球×3</b>｜<b>速度·加速·体力·反应·远射·射门力量·盘带·灵活·长传×2</b>｜'
'<b>视野·侵略性·铲断·弧线·射术·冷静·站位·头球·弹跳·凌空×1</b>｜<b>传中·任意球·点球×0</b>（Σ权重49，满分196）<br>'
'特训：全卡共+5点、单项≤2点，按背包求最大档位增益<br>'
'逆足：5逆×1.0 / 4逆×0.95 / 3逆×0.90（后腰全体系最宽）　｜　口径：接口裸值+3显示+8卡强化15+<b>球员等级4(假设待游戏内确证)</b>+队套6<br>'
'得分率=终分÷满分196（⚠与其他位置页不同量纲，<b>跨位置比较用名次</b>，见全位置拉通页）。'
'<b>全员68人(非门将)都算后腰分，≥80进榜</b>；蓝名=非后腰客串（CM中场客串=近亲参考，其余仅数值参考）；'
'灰行=不足80的正牌后腰（明确别当后腰买）。身高/体重/模型仅参考不计分。<br>'
'<b>工资残差</b>=终分 − 市场定价线（5名正牌后腰拟合，样本极小仅参考 终分≈' + '%.0f+%.1f×工资' % (INTC, SLOPE) + '）——'
'<span style="color:#5cff8f">绿≥+7超模</span> / <span style="color:#ff7b7b">红≤−7工资坑</span>。</div>'
'<table><tr><th>#</th><th>球员</th><th>官方位置</th><th>逆足</th><th>终分</th><th>得分率</th><th>原分+特训</th><th>薪</th><th>工资残差</th><th>身材/模型</th><th>最优特训方案</th><th>评语</th></tr>'
+ trs + '</table>'
'<h2>模型层备注</h2><div class="note">'
'公式外因素（买前自查）：①特性——大罗+中场指挥官封神/图雷-指挥官手感笨/渗透者需高AI，特性是可投资项；'
'②体重造假——伊布被官方+11kg（唯一物理劣化）；③模型手感——梅西169瘦小打中锋数值行模型不行；'
'④范尼问题——"全员163"体质是阈值制最大受害者，信不信165阈值论决定他被低估还是被如实定价。</div>'
'<h2>vs 时刻：同名卡对比 + 时刻独有卡（按时刻8卡分排名）</h2>'
'<div class="note">口径：两边同用后腰权重+特训+逆足；档位与主榜一致（145/155/165=1/2/3，'
'07-27起时刻计分与永恒统一，<b>本表分数与主榜同量纲可直接比</b>）。永恒6卡=强化+8口径（现实持有状态）。<br>'
'<b>加减(永恒8卡−时刻8卡)读法：加减小=溢价大=避雷（花永恒的钱买不到提升）；加减大=永恒真升级。</b>'
'红=加减&lt;35（智商税区：欧文+20.9全场最小/巴乔/车范根）；绿=加减≥50（换代刀刃：亨利+52/马塞洛+59/兰帕德+57/图雷+55.5，'
'中场组整体+49~57——时刻中场是重灾区，永恒换代收益最高的是中场）。'
'紫名行=<b>时刻独有</b>（贝利/马拉多纳/克鲁伊夫等51人无永恒版，永恒列显—）。<b>全表可点击</b>：点任意行弹出该时刻卡29项属性的档位/权重/得分清单+特训方案+逆足算式。</div>'
'<table><tr><th>#</th><th>球员</th><th>官方位置</th><th>时刻8卡</th><th>时刻薪</th><th>时刻每薪</th><th>永恒6卡</th><th>永恒8卡</th><th>永恒薪</th><th>永恒每薪</th><th>加减</th></tr>'
+ tm_trs + '</table>'
'<div class="note" style="margin-top:6px">每薪=该卡8卡分÷自己的工资（与主榜同量纲）。<b>时刻薪普遍低3-5点</b>，'
'绿色=时刻每薪&gt;永恒每薪（工资效率上时刻更划算——预算/工资帽紧时的参考）。</div>'
'</div>'
'<div id="ov" onclick="hide()"></div><div id="md" style="display:none"></div>'
'<script>var D=' + json.dumps(detail, ensure_ascii=False) + ';\n'
'function hide(){document.getElementById("ov").style.display="none";document.getElementById("md").style.display="none"}\n'
'function pop(n){var d=D[n];if(!d)return;var h="<span class=x onclick=hide()>&times;</span><h3>"+n+" · 后腰分算分清单</h3>"\n'
'+"<div class=sub>"+d.phy+"　|　"+d.w5+"逆足</div>"\n'
'+"<table><tr><th>属性</th><th>显示值</th><th>档位</th><th>权重</th><th>得分</th></tr>";\n'
'for(var i=0;i<d.items.length;i++){var it=d.items[i];\n'
'var tv=it[5]||0,tt=it[6]||0;var tc=tv?tt:it[2];\n'
'var vx=tv?(it[1]+"→<b>"+tv+"</b>"):it[1];var dx=tv?(it[2]+"档→<b>"+tt+"档</b>"):(it[2]+"档");\n'
'h+="<tr class=\'"+(it[3]?"":"w0")+"\'><td>"+it[0]+(tv?" <span style=\'color:#ffd35c;font-size:10px\'>[特训]</span>":"")+"</td><td class=t"+tc+">"+vx+"</td><td class=t"+tc+">"+dx+"</td><td>"+(it[3]?"×"+it[3]:"×0")+"</td><td class=t"+tc+">"+(it[3]?it[4]:"—")+"</td></tr>";}\n'
'h+="</table><div class=sum>基础分 <b>"+d.base.toFixed(1)+"</b>　＋　特训 <b>+"+d.gain.toFixed(1)+"</b>（"+d.plan+"）<br>"\n'
'+"× 逆足系数 <b>"+d.pen+"</b>（"+d.w5+"逆）　＝　终分 <b>"+d.fin+"</b></div>";\n'
'var m=document.getElementById("md");m.innerHTML=h;m.style.display="block";document.getElementById("ov").style.display="block"}\n'
'var DT=' + json.dumps(dtl, ensure_ascii=False) + ';\n'
'function popT(n){var d=DT[n];if(!d)return;var h="<span class=x onclick=hide()>&times;</span><h3>"+n+" · 时刻8卡属性清单（145/155/165三档制，与主榜同口径）</h3>"\n'
'+"<div class=sub>"+d.phy+"　|　"+d.w5+"逆足</div>"\n'
'+"<table><tr><th>属性</th><th>显示值</th><th>档位</th><th>权重</th><th>得分</th></tr>";\n'
'for(var i=0;i<d.items.length;i++){var it=d.items[i];var tc=Math.min(it[2],4);\n'
'h+="<tr class=\'"+(it[3]?"":"w0")+"\'><td>"+it[0]+"</td><td class=t"+tc+">"+it[1]+"</td><td class=t"+tc+">"+it[2]+"档</td><td>"+(it[3]?"×"+it[3]:"×0")+"</td><td class=t"+tc+">"+(it[3]?it[4]:"—")+"</td></tr>";}\n'
'h+="</table><div class=sum>基础分 <b>"+d.base.toFixed(1)+"</b>　＋　特训 <b>+"+d.gain.toFixed(1)+"</b>（"+d.plan+"）<br>"\n'
'+"× 逆足系数 <b>"+d.pen+"</b>（"+d.w5+"逆）　＝　时刻分 <b>"+d.fin+"</b></div>";\n'
'var m=document.getElementById("md");m.innerHTML=h;m.style.display="block";document.getElementById("ov").style.display="block"}\n'
'document.addEventListener("keydown",function(e){if(e.key==="Escape")hide()});\n'
'function sortT(t,i,th){var rows=Array.prototype.slice.call(t.querySelectorAll("tr")).slice(1);'
'var dir=th.dataset.d==="a"?"d":"a";'
't.querySelectorAll("th").forEach(function(h){delete h.dataset.d;h.textContent=h.textContent.replace(/ [\\u25b2\\u25bc]$/,"")});'
'th.dataset.d=dir;th.textContent=th.textContent+(dir==="a"?" \\u25b2":" \\u25bc");'
'rows.sort(function(r1,r2){var a=(r1.cells[i]?r1.cells[i].innerText:"").trim(),b=(r2.cells[i]?r2.cells[i].innerText:"").trim();'
'var na=parseFloat(a.replace(/[^0-9.+\\-]/g,"")),nb=parseFloat(b.replace(/[^0-9.+\\-]/g,""));'
'var c=(!isNaN(na)&&!isNaN(nb))?na-nb:a.localeCompare(b,"zh");return dir==="a"?c:-c});'
'rows.forEach(function(r){t.appendChild(r)})}\n'
'document.querySelectorAll(".wrap table").forEach(function(t){t.querySelectorAll("tr:first-child th").forEach(function(th,i){'
'th.style.cursor="pointer";th.title="\\u70b9\\u51fb\\u6392\\u5e8f";th.addEventListener("click",function(){sortT(t,i,th)})})});\n'
'</script></body></html>')
P = r'C:\ADHD_agent\FCOL阿三资料库\07_数据分析\永恒后腰评价_定稿版_20260727.html'
tmp = P + '.tmp'
open(tmp, 'w', encoding='utf-8').write(html)
os.replace(tmp, P)
print('ok', P)
