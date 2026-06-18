# -*- coding: utf-8 -*-
"""X3【非节日外显】投放图鉴 —— 带实物图 + 具体来源 + 分类页签 + 双时间轴。
时间轴双轴：绝对时间(版本发布 2024→2026) / 服务器时间(玩家生命周期 D0→D60+)。
数据源 C:/x3/gdconfig/tsv/（只读）；图标 C:/x3-project/client/Assets/Res/UI/Spirits。
"""
import base64, os, csv, glob
from PIL import Image

ASSET = r"C:/x3-project/client/Assets"
SPIR = os.path.join(ASSET, "Res/UI/Spirits")
TSV = r"C:/x3/gdconfig/tsv"
TEXT = os.path.join(TSV, "i18n", "Text__Text.tsv")

def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()
def dim(p):
    try:
        with Image.open(p) as im:
            return f"{im.width}×{im.height}"
    except Exception:
        return "?"
_cache = {}
def rfind(name):
    if not name:
        return ""
    name = name[3:] if name.startswith("DK_") else name
    if name in _cache:
        return _cache[name]
    hits = glob.glob(os.path.join(SPIR, "**", name + ".png"), recursive=True)
    if not hits:
        low = name.lower()
        hits = [p for p in glob.glob(os.path.join(SPIR, "**", "*.png"), recursive=True)
                if os.path.basename(p)[:-4].lower() == low]
    _cache[name] = hits[0] if hits else ""
    return _cache[name]
def rows(t):
    with open(os.path.join(TSV, t), encoding="utf-8") as f:
        return [r for r in csv.reader(f, delimiter="\t") if r and r[0].isdigit()]
_txt = {}
with open(TEXT, encoding="utf-8") as f:
    for r in csv.reader(f, delimiter="\t"):
        if r and r[0].startswith("TXT_") and len(r) > 3:
            _txt[r[0]] = r[3]
def tname(k):
    return _txt.get(k, k) if k else ""

# 英雄 id->中文名（4位基础英雄）
HERONAME, NAME2ID = {}, {}
for r in rows("Hero__Hero.tsv"):
    if len(r) > 3 and len(r[0]) == 4 and r[3]:
        HERONAME[r[0]] = r[3]
        NAME2ID.setdefault(r[3], int(r[0]))

# ============ 绝对时间轴(版本) / 服务器时间轴(D-day) 分桶 ============
ABS_DEF = [
 ("E0","常驻基建 · 开服即有","随版本一直在、与节日无关的常驻系统外显"),
 ("E1","2024 · 开服首年","首年节奏：早期英雄 + 24圣诞/春节 + 初代风暴逐鹿"),
 ("E2","2025 上半年","情人/愚人/儿童 + 海洋入侵/蒸汽/伟大航道 + 中期英雄"),
 ("E3","2025 下半年","海滨/周年/魂归之潮/魔海/骑士/凛冬 + GvG争霸 + 后期英雄"),
 ("E4","2026 至今","尼罗/白色花嫁/新春/世界杯 + 最新英雄 + 冠军之路"),
]
SRV_DEF = [
 ("S0","D0 开局","进游戏即解锁：初始皮肤/主城默认家具/功能入口/内置表情"),
 ("S1","D1–7 首周","格蕾丝/阿米娜/贝拉/芬贝克等开局英雄皮肤·公会商店·钻石商店装饰·俘获芳心·早期建筑纪念卡"),
 ("S2","D8–30 成长期","克里斯塔尔D12/柳柳D5·13/海瑟D9/斯隆D8/夜玫瑰D8/艾丽丝D16·赛米拉D8·中期建筑·声望船皮肤"),
 ("S3","D30–60 成熟期","KVK-S1(尼西斯D29/拉维耶D36/雷娜D43)·UP2艾琳娜D22爱莉希雅D29·玛琳娜D30·三星养成贴纸·PvP头衔头像框"),
 ("S4","D60+ 长线/循环","五星养成贴纸·二阶晋升(自由柳柳)·KVK-S2(诺瓦尔/艾娃)·世界征服顶段"),
 ("SF","随节庆(真实日历)","节庆活动按真实月份投放给全服→单个服的服务器D天因开服时间而异(见绝对时间轴)"),
 ("SX","时间不确定","养成进度因人而异 / 缺投放表数据——无固定服务器D天，不臆测"),
]
MORDER = {"m1":1,"m2":2,"m3":3,"m4":4,"m5":5,"m6":6,"m7":7,"m8":8}

def abs_era(s, hid=None):
    s = s or ""
    KW = [("E4",["世界杯","尼罗","花嫁","新春龙舞","新春特辑","冠军之路","内裤","再启征帆","天马","圣诞庆典","26","绿茵"]),
          ("E3",["海滨假日","七月盛典","烧烤","周年盛宴","这一年","魂归之潮","灵魂回响","望帆","人鱼","美人鱼","团圆","玉兔","秋季酿酒","魔海","魔山","骑士","继承者","救赎","光之双面","凛冬","魔女","公会合并","重铸","争霸","GvG","世界入侵","世界之战","永恒之岛","巢穴","回声","炎龙"]),
          ("E2",["2025","情人","愚人","松鼠","儿童","格蕾丝的游园","海洋入侵","新世界","蒸汽","少女与蒸汽","蔷薇","贵族之女","品酒","微醺","伟大航道","兔宝宝","夜下垂钓","俘获芳心","女仆","每日福利","满月","海洋女王","风暴逐鹿","风暴尽头","巨蟹","自由游行"]),
          ("E1",["2024","圣诞纪念","浪漫烟花"]),
          ("E0",["初始","默认","功能解锁","钻石商店","声望","注册","内置","达到","常驻","成就","主城"])]
    for era, ks in KW:
        if any(k in s for k in ks):
            return era
    if hid:
        return "E1" if hid<=1019 else "E2" if hid<=1032 else "E3" if hid<=1043 else "E4"
    return "E0"

def srv_era(s, hid=None, lvl=None, star=None):
    s = s or ""
    if star == 5: return "S4"
    if star == 3: return "S3"
    if lvl is not None:               # 建筑纪念卡：按建筑等级
        return "S0" if lvl<=2 else "S1" if lvl<=4 else "S2"
    if any(k in s for k in ["初始","默认","功能解锁","内置","D0","主城默认"]): return "S0"
    if any(k in s for k in ["注册","钻石商店 lv3","钻石商店 lv10","钻石商店 lv12"]): return "S1"
    if any(k in s for k in ["PvP","KvK","GvG","争霸","世界入侵","世界之战","永恒之岛","巢穴","世界征服","冠军之路","风暴逐鹿","魔海","魔山"]): return "S3"
    if any(k in s for k in ["声望"]): return "S2"
    if hid:                           # 英雄绑定：按英雄解锁早晚
        return "S1" if hid<=1010 else "S2" if hid<=1025 else "S3"
    if "晋升" in s and ("二阶" in s or "五星" in s): return "S4"
    if "晋升" in s: return "S3"
    return "S2"                        # 其余运营活动默认成长期

# ============ 英雄投放节奏（权威D天，来自GSheet「英雄投放节奏」页签） ============
# 文件列：英雄/皮肤id, 名称, 首次投放方式, 解锁条件, 首投day
HERO_DAY = {}   # id -> (name, way, cond, dayN or None)
import re as _re
def _parseday(day, cond, way):
    if day and day.startswith("D") and day[1:].isdigit():
        return int(day[1:])
    for txt in (cond, way):
        if not txt: continue
        m = _re.search(r"开放(\d+)\s*天", txt) or _re.search(r"(\d+)\s*天", txt)
        if m and ("开放" in txt or "海域" in txt):
            return int(m.group(1))
    return None
for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_hero_deploy_days.tsv"), encoding="utf-8"):
    c = ln.rstrip("\n").split("\t")
    if len(c) >= 2 and c[0].isdigit():
        nm, way, cond, day = (c+["","","",""])[1:5]
        HERO_DAY[c[0]] = (nm, way, cond, _parseday(day, cond, way))

def day2srv(d):
    if d is None: return None
    if d <= 0: return "S0"
    if d <= 7: return "S1"
    if d <= 30: return "S2"
    if d <= 60: return "S3"
    return "S4"

def when_srv(day=None, cond="", d0=False):
    """统一产出(投放时机字串, 服务器桶)。不确定就明说不确定，不臆测D天。"""
    if d0:
        return "🕐 D0 开局即有", "S0"
    if day is not None:
        return ("🕐 D" + str(day) + " 起" + (" · " + cond if cond else "")), day2srv(day)
    if cond:
        return "🕐 不确定 · " + cond, "SX"
    return "🕐 不确定", "SX"

# ===== 活动开启时间：服务器D天(活动排期) + 绝对日历(运营日历) + KvK排期 =====
# 系统活动→服务器D天（来自 GSheet「活动排期」说明列）
ACT_DAY = {
 "开业回馈":1,"开业":1,"贝拉的期盼":1,"俘获芳心":1,"内裤":1,"烹饪盛宴":1,"远航战备":1,"远航":1,
 "舞娘助力":2,"知识进修":5,"玫瑰之恋":5,"玫瑰之约":5,"赛米拉":8,"伟大航道":8,"舰队扩编":8,
 "食材囤积":11,"海域交锋":14,"异域盛典":15,"夜下垂钓":4,"钓鱼":1,"女仆嘉奖":1,"女仆":1,
 "公会崛起":1,"运营大师":15,"生意兴隆":12,"怒海争锋":15,"永恒之主":23,"巢穴争霸":8,"巢穴":8,
 "永恒之岛":18,"最佳酒馆":6,"竞技场":8,"决胜时刻":8,"商会大促销":1,"酒后闲谈":1,"秘密问答":1,
 "船只改装":4,"运营大师":15,"赛米拉的故事":8,"赛米拉的冒险":9,
 # KvK / 跨服（来自「跨服战」首次开启）
 "公会争霸":7,"GvG":7,"世界入侵":35,"世界之战":35,"风暴逐鹿":42,"风暴":42,"魔海回声":49,"魔海":49,"魔山":49,
 # 英雄养成活动（投放节奏表确认）
 "巨蟹狂潮":5,"天下第一武道":2,"武道修行":15,"玫瑰晋升之路":8,"冠军之路":30,
}
# 节庆活动→绝对日历年月（来自 GSheet「运营日历」）
FEST_YM = {
 "圣诞纪念":"2024-12","2024圣诞":"2024-12","浪漫烟花":"2025-01","2024春节":"2025-01",
 "2025情人":"2025-02","蒸汽":"2025-04","少女与蒸汽":"2025-04","2025愚人":"2025-04","松鼠":"2025-04",
 "蔷薇盛典":"2025-05","贵族之女":"2025-05","春日品酒":"2025-05","微醺":"2025-05",
 "2025儿童":"2025-06","格蕾丝的游园":"2025-06","烧烤":"2025-06","烤肉":"2025-06",
 "七月盛典":"2025-07","自由游行":"2025-07","周年盛宴":"2025-07","这一年":"2025-07",
 "魂归之潮":"2025-07","灵魂回响":"2025-07","海滨假日":"2025-08","比基尼":"2025-08",
 "望帆":"2025-08","千帆":"2025-08","人鱼":"2025-09","美人鱼":"2025-09","炎龙":"2025-09","火舞":"2025-09",
 "团圆":"2025-10","玉兔":"2025-10","秋季酿酒":"2025-10","魔女":"2025-10","救赎":"2025-11","骑士":"2025-11","荣光的继承":"2025-11",
 "凛冬":"2025-12","圣诞庆典":"2025-12","礼物堆":"2025-12","再启征帆":"2026-01","天马":"2026-01",
 "尼罗":"2026-01","白色花嫁":"2026-02","我对你的誓言":"2026-02","新春龙舞":"2026-02","新春特辑":"2026-02",
 "世界杯":"2026-03","绿茵":"2026-03","公会合并":"2025-10","重铸":"2025-10","航海之路":"2025-08","美人鱼的梦境":"2025-08",
}
def ym_era(ym):
    y, m = ym.split("-"); y, m = int(y), int(m)
    if y <= 2024: return "E1"
    if y == 2025: return "E2" if m <= 6 else "E3"
    return "E4"
def match_act(src):
    best = None
    for k, d in ACT_DAY.items():
        if k in src and (best is None or len(k) > best[0]):
            best = (len(k), d)
    return best[1] if best else None
def match_fest(src):
    best = None
    for k, ym in FEST_YM.items():
        if k in src and (best is None or len(k) > best[0]):
            best = (len(k), ym)
    return best[1] if best else None
def act_time(src, hid=None):
    """活动类条目 → (when, srv桶, abs桶)。系统活动给服务器D天；节庆给绝对日历+随节庆桶。"""
    ad, fy = match_act(src), match_fest(src)
    a = ym_era(fy) if fy else abs_era(src, hid)
    if ad is not None:
        return ("🕐 服务器 D" + str(ad) + " 开启" + (f" · {fy} 当期" if fy else "")), day2srv(ad), a
    if fy:
        return ("🕐 随节庆 " + fy + " 投放（服务器D天随开服而异）"), "SF", a
    return ("🕐 不确定 · " + src), "SX", a

# ============ 收集所有条目 ALL ============
ALL = []  # dict: m, ml, id, name, dk, attr, src, abs, srv, when, big
def add(m, ml, iid, name, dk, attr, src, abs_, srv, big=False, ipath=None, when=""):
    ALL.append(dict(m=m, ml=ml, id=iid, name=name, dk=dk, attr=attr, src=src,
                    abs=abs_, srv=srv, big=big, ipath=ipath, when=when))

# ---- ① 技能皮肤 28 ----
SKILL = [
 ("10011","仙蒂公主·格蕾丝","格蕾丝","技能9001","Pack 19025/19052 营救礼包 $9.99（一阶晋升底层）"),
 ("10012","白雪公主·格蕾丝","格蕾丝","技能8001","格蕾丝二阶晋升礼包（PackHeroPromotion）"),
 ("10041","初妆·鲁比","鲁比","技能9004","公会商店「每周特供」· 50万公会贡献"),
 ("10042","钢羽战衣·鲁比","鲁比","纯外显","公会商店「每周特供」· 150万公会贡献"),
 ("10081","仙女教母·克里斯塔尔","克里斯塔尔","技能9008","克里斯塔尔一阶晋升礼包"),
 ("10111","微醺·哈珀","哈珀","技能9011","哈珀一阶晋升礼包"),
 ("10141","魔法师·柳柳","柳柳","技能9014","技能售卖活动「巨蟹狂潮」(ActvHeroSkillSell 4701 / Pack 19024)"),
 ("10142","自由·柳柳","柳柳","技能8014","柳柳二阶晋升礼包"),
 ("10161","战神·艾丽丝","艾丽丝","技能9016","艾丽丝一阶晋升礼包"),
 ("10201","海上女王·阿米娜","阿米娜","技能9020","Pack 18002/19008「阿米娜道具获取礼包」 $39.99"),
 ("10202","红绸剑姬·阿米娜","阿米娜","纯外显","26春节 跨服积分排名奖励（名次1~20）"),
 ("10211","传奇女仆·贝拉","贝拉","技能9021","珍宝商店「装扮」· 1500 胡萝卜纪念币（心动礼物）"),
 ("102102","内裤宗师·贝拉","贝拉","纯外显","「内裤的踪迹」活动大奖（集齐 FinalReward）"),
 ("10221","丰收女神·阿迪娜","阿迪娜","技能9022","Pack 18015/19084「阿迪娜采集道具礼包」 $39.99"),
 ("10241","海洋精灵·芬贝克","芬贝克","技能9024","珍宝商店「装扮」· 1500 胡萝卜纪念币"),
 ("10291","史诗舞者·奥黛丽","奥黛丽","技能9029","Pack 18005/19021 $29.99 ＋ 新服「舞娘助力」升星奖励"),
 ("10292","传奇舞者·奥黛丽","奥黛丽","技能8029","Pack 18004/19020「奥黛丽道具礼包」 $39.99"),
 ("10311","白衣梦魇·海瑟","海瑟","技能9031","Pack 19009 活动推送 $49.99 ／ Pack 18003 $39.99"),
 ("10321","艺术大师·斯隆","斯隆","技能9032","Pack 18001/19004「斯隆道具礼包」 $39.99"),
 ("103401","兔耳魅影·霍普金斯","霍普金斯","纯外显","⚠ 未在任何投放表找到（疑未上线/占位）"),
 ("103502","征服者·阿什顿","阿什顿","技能9035","Pack 18016/19148「征服者阿什顿礼包」 $49.99"),
 ("104001","足球宝贝·爱莉希雅","爱莉希雅","纯外显","世界杯：竞猜命中加送 ＋ 开箱跨服排名"),
 ("10421","圣光·夜玫瑰","夜玫瑰","技能9042","Pack 18012/19043「夜玫瑰圣光礼包」 $39.99"),
 ("10422","幻彩·夜玫瑰","夜玫瑰","技能8042","Pack 19088「夜玫瑰幻彩皮肤」 $39.99"),
 ("10431","伤痕累累·凌霜","凌霜","技能9043","Pack 18000/19003「凌霜伤痕累累礼包」 $39.99"),
 ("10432","凌霜·布鲁斯·李","凌霜","技能8043","Pack 18007/19023「布鲁斯李礼包」 $29.99"),
 ("10433","武道冠军·凌霜","凌霜","纯外显","英雄冠军之路「决赛」阶段奖励"),
 ("10471","狼魂之主·艾琳娜","艾琳娜","技能9047","Pack 19058「艾琳娜狼魂之主」 $39.99"),
 ("105601","霓裳羽衣·维丹蒂亚","维丹蒂亚","纯外显","争霸赛商店 · 10万 争霸赛徽章"),
]
hs_icon = {r[0]: r[5] for r in rows("Hero__HeroSkin.tsv") if len(r) > 6}
# 部分皮肤不在投放节奏表(用基础英雄首得日兜底)
BASE_DAY = {k: v[3] for k, v in HERO_DAY.items()}
for sid, name, hero, skill, src in SKILL:
    hid = NAME2ID.get(hero)
    nm_, way_, cond_, day_ = HERO_DAY.get(sid, ("", "", "", None))
    cond_disp = cond_ or way_ or ""        # 只用该皮肤自身的解锁条件，不拿基础英雄日臆测
    if day_ is not None:
        when, srv = when_srv(day_, cond_disp)
        ab = abs_era(src + name, hid)
    else:                                   # 投放表无固定D天→查活动排期/节庆，再不行才不确定
        when, srv, ab = act_time(src + " " + name, hid)
        if srv == "SX" and cond_disp:
            when = "🕐 不确定 · " + cond_disp
    add("m1","技能皮肤", sid, name, hs_icon.get(sid,""),
        f"{hero} · {skill}", src, ab, srv, big=True, when=when)

# ---- ② 纪念卡 79 ----
BUFFG = {"1001":"水手攻击","1002":"水手防御","1003":"猎人攻击","1004":"射手攻击","1005":"斗士攻击",
         "1006":"伤害","1008":"舰船航速","1010":"猎人防御","1011":"射手防御","1012":"斗士防御"}
import re
for r in rows("MemorialCard__MemorialCard.tsv"):
    if len(r) < 11: continue
    iid, name, icon, src, grp = r[0], r[2], r[4], (r[7] or "—"), r[9]
    lvl = None
    mlv = re.search(r"达到(\d+)级", src)
    if mlv: lvl = int(mlv.group(1))//2 if "港口" in src or "营地" in src or "仓库" in src else int(mlv.group(1))
    if "达到" in src:   # 建筑等级解锁=确定(随建筑升级必得)
        lvl = int(re.search(r"(\d+)级", src).group(1))
    if lvl is not None:
        sv, ab = ("S0" if lvl <= 9 else "S1" if lvl <= 14 else "S2"), "E0"
        when = "🕐 " + src + "（随建筑升级）"
    else:               # 运营/节庆活动→活动排期D天 或 节庆真实日历
        when, sv, ab = act_time(src)
    add("m2","纪念卡", iid, name, icon, f"{BUFFG.get(grp,grp)}加成 · 可升级", src,
        ab, sv, when=when)

# ---- ③ 家具 ----
FURN_PAY = {"31001041":"内购礼包20200 $4.99","31001048":"内购礼包20201 $19.99","31001049":"内购礼包20202 $2.99",
 "31001050":"内购礼包20203 $19.99","31001051":"内购礼包20204 $9.99","31001056":"内购礼包20205 $9.99",
 "31001057":"内购礼包20206 $9.99","31001061":"内购礼包20207 $29.99","31001062":"内购礼包20208 $19.99",
 "31001071":"内购礼包20209 $49.99","31001042":"成就（默认）","31001043":"成就（默认）","31001044":"成就（默认）"}
FUNC = {"61001001":"功能解锁·台账","61001002":"功能解锁·拜访","61001003":"功能解锁·甜心助力","61001004":"功能解锁·世界新闻",
        "61001005":"功能解锁·钓鱼","61001007":"功能解锁·黑市","61001008":"功能解锁·商店","61001009":"功能解锁·竞技场",
        "61001010":"功能解锁·开拓航道","61001011":"功能解锁·纪念卡"}
furn_def_n = 0
for r in rows("FurnitureDecorate__FurnitureDecorate.tsv"):
    if len(r) < 29: continue
    iid, name, icon, tc = r[0], r[1], r[6], (r[24] if len(r) > 24 else "")
    if tc.strip(): continue
    if iid in FURN_PAY:
        w, sv = ("🕐 D0 开局即有","S0") if "成就" in FURN_PAY[iid] else ("🕐 不确定 · 常驻内购礼包","SX")
        add("m3","家具", iid, name, icon, "城内家具", FURN_PAY[iid], "E0", sv, when=w)
    elif iid in FUNC:
        add("m3","家具", iid, name, icon, "功能入口家具", FUNC[iid], "E0", "S0", when="🕐 功能解锁即出现")
    elif furn_def_n < 24:
        furn_def_n += 1
        add("m3","家具", iid, name, icon, "常驻装修件", "主城默认", "E0", "S0", when="🕐 D0 开局即有")

# ---- ④ 装饰 16 ----
DECO_SRC = {"1001001":"初始解锁","1001002":"钻石商店 lv10·1万钻","1001003":"钻石商店 lv15·2万钻","1001004":"钻石商店 lv18·5万钻",
 "2001001":"初始解锁","2001003":"钻石商店 lv3·1万钻","2001004":"钻石商店 lv12·1.5万钻","2001005":"钻石商店 lv15·3万钻",
 "2001006":"钻石商店 lv18·5万钻","2001007":"钻石商店 lv22·8万钻","2001009":"注册第4天礼包(TC6010)",
 "3001001":"初始解锁","3001002":"钻石商店 lv10·1万钻","3001003":"钻石商店 lv12·2万钻","3001004":"钻石商店 lv18·5万钻",
 "3001006":"注册第4天礼包(TC6010)"}
for r in rows("FurnitureSkin__FurnitureSkin.tsv"):
    if r[0] not in DECO_SRC: continue
    iid, name, icon = r[0], r[1], r[3]
    buff = r[21] if len(r) > 21 and r[21] else "无buff"
    t = "横梁" if iid.startswith("1001") else ("地板" if iid.startswith("2001") else "墙纸")
    src = DECO_SRC[iid]
    if "初始" in src:
        when, sv = "🕐 D0 开局即有", "S0"
    elif "注册" in src:
        when, sv = "🕐 D4 注册第4天礼包", "S1"
    else:               # 钻石商店：按解锁等级(确定)
        mlv = re.search(r"lv(\d+)", src)
        lv = int(mlv.group(1)) if mlv else 99
        when, sv = f"🕐 主城lv{lv}解锁（钻石购买）", ("S1" if lv <= 12 else "S2")
    add("m4","装饰", iid, name, icon, f"{t} · {buff}", src, "E0", sv, when=when)

# ---- ⑤ 表情 ----
for iid, name, dk in [(r[0], r[1], r[2]) for r in rows("ChatEmojyReply__ChatEmojyReply.tsv")]:
    add("m5","表情", iid, name, dk, "快捷回复 72×72", "内置免费", "E0", "S0", when="🕐 D0 内置即有")
EMO_FEST = {"130","132","140","170","210","220","230","240"}
for r in rows("Emoticons__Emoticons.tsv"):
    if len(r) < 7: continue
    iid = r[0]
    if iid in EMO_FEST or (300 <= int(iid) <= 360): continue
    dk, pack, face, role, src = r[1], r[2], r[3], r[4], (r[6] or "—")
    s = f"礼包 {pack} $4.99" if pack else src
    icon = "icon_global_" + dk[3:] if dk.startswith("DK_") else dk
    if "内置" in src or not src or src == "—":
        when, sv, ab = "🕐 D0 内置即有", "S0", "E0"
    else:
        when, sv, ab = act_time(src)        # 问答/礼包/活动→排期D天
    add("m5","表情", iid, f"{role}{face}", icon, "聊天表情", s, ab, sv, when=when)

# ---- ⑥ 头衔 + 头像框 ----
QMAP = {"0":"蓝","1":"紫","2":"橙","3":"橙+"}
for r in rows("PlayerTitle__PlayerTitle.tsv"):
    if len(r) < 7: continue
    iid, name, icon, src = r[0], r[1], r[2], (r[5] or "—")
    q = QMAP.get(r[7], r[7]) if len(r) > 7 else ""
    if "初始" in src:
        when, sv, ab = "🕐 D0 开局即有", "S0", "E0"
    else:
        when, sv, ab = act_time(src)
    add("m6","头衔/头像框", iid, name, icon, f"头衔·{q}品·站位Buff", src, ab, sv, when=when)
FRAME_FEST = {"10006","10009","10011","10012","10015","10016","10017","10018","10019","10020","10026","10027"}
for r in rows("Personalize__PersonalizeAvatarFrameCfg.tsv"):
    if len(r) < 7: continue
    iid = r[0]
    if iid in FRAME_FEST or int(iid) >= 10028: continue
    icon, src = r[4], (r[5] or "—")
    name = r[9] if len(r) > 9 else iid
    buff = f"{r[6]}+{r[7]}" if len(r) > 7 and r[6] and r[7] else "无"
    if "初始" in src:
        when, sv, ab = "🕐 D0 开局即有", "S0", "E0"
    else:
        when, sv, ab = act_time(src)
    add("m6","头衔/头像框", iid, name, icon, f"头像框·Buff {buff}", src, ab, sv, when=when)

# ---- ⑦ 航迹 + 船皮肤 ----
TRAIL_FEST = {"3002","3006","3007","3008","3009","3010","3012"}
for r in rows("Skin__Skin.tsv"):
    if len(r) < 9 or r[2] != "2" or r[0] in TRAIL_FEST: continue
    src = r[5] or "—"
    when, sv = ("🕐 D0 默认","S0") if "默认" in src else ("🕐 不确定 · " + src, "SX")
    add("m7","航迹/船", r[0], r[1], r[8], "拖尾特效·无属性", src, abs_era(src+r[1]), sv, when=when)
for r in rows("Ship__ShipSkin.tsv"):
    if len(r) < 7 or int(r[0]) > 8: continue
    iid, name, icon, rep, fx, buff = r[0], r[1], r[2], r[4], r[5], (r[6] or "无")
    if not rep or rep == "0":
        src, when, sv = "初始默认", "🕐 D0 默认", "S0"
    else:
        src, when, sv = f"声望解锁 {rep}", f"🕐 不确定 · 累积{rep}声望（玩家进度）", "SX"
    add("m7","航迹/船", iid, name, icon, f"船皮肤·Buff {buff}·绑航迹{fx}", src,
        "E0", sv, when=when)

# ---- ⑧ 羁绊贴纸 27 ----
LCG = {}
for r in rows("HeroStickers__LightConditionGroup.tsv"):
    if len(r) < 5: continue
    LCG.setdefault(r[1], []).append((r[2], r[3], r[4]))
SB = {r[0]: r[3] for r in rows("HeroStickers__StickerBuff.tsv") if len(r) > 3}
for r in rows("HeroStickers__HeroStickers.tsv"):
    if len(r) < 11: continue
    iid, name, icon, grp, sbid, heros = r[0], r[1], r[3], r[5], r[7], r[9]
    hnames = "·".join(HERONAME.get(h, h) for h in heros.split("|"))
    parts, star = [], None
    for t, val, note in LCG.get(grp, []):
        if t == "3":
            h, st = (val.split("|") + ["?"])[:2]
            parts.append(f"{HERONAME.get(h,h)}达{st}星"); star = max(star or 0, int(st) if st.isdigit() else 0)
        elif t == "2":
            parts.append("拥有该皮肤")
        elif t == "1":
            parts.append("拥有"+HERONAME.get(val, val))
    cond = " + ".join(dict.fromkeys(parts)) or "拥有英雄"
    pct = ""
    if sbid in SB and SB[sbid].isdigit():
        pct = f"永久+{int(SB[sbid])/10000:.2f}%"
    hids = [h for h in heros.split("|")]
    hdays = [BASE_DAY.get(h) for h in hids if BASE_DAY.get(h) is not None]
    eday = min(hdays) if hdays else None
    base = f"{hnames} D{eday}起解锁" if eday else f"拥有{hnames}"
    if star == 5:
        when, srv = f"🕐 不确定 · {base}→升5星（养成因人而异）", "SX"
    elif star == 3:
        when, srv = f"🕐 不确定 · {base}→升3星（养成因人而异）", "SX"
    elif eday:
        when, srv = f"🕐 D{eday} 起（拥有{hnames}即点亮）", day2srv(eday)
    else:
        when, srv = f"🕐 不确定 · 拥有{hnames}即点亮", "SX"
    add("m8","羁绊贴纸", iid, name, icon,
        f"英雄：{hnames} · 点亮：{cond}", pct or "永久Buff",
        abs_era("", min((int(h) for h in hids), default=1050)), srv, when=when)

# ============ 渲染 ============
def card_html(it):
    p = it["ipath"] or rfind(it["dk"])
    if not p or not os.path.exists(p):
        thumb, d = '<div class="thumb miss">缺图</div>', "缺图"
    else:
        cls = "thumb big" if it["big"] else "thumb"
        thumb = f'<div class="{cls}"><img src="data:image/png;base64,{b64(p)}"></div>'
        d = dim(p)
    w = "card big" if it["big"] else "card"
    whenh = f'<div class="sub when">{it["when"]}</div>' if it.get("when") else ""
    return (f'<div class="{w}" data-m="{it["m"]}" data-mo="{MORDER[it["m"]]}" '
            f'data-abs="{it["abs"]}" data-srv="{it["srv"]}">{thumb}'
            f'<div class="meta"><b>{it["name"]}</b> <span class="tag">{it["ml"]}</span>'
            f'<div class="sub px">ID {it["id"]} · {d}</div>'
            f'<div class="sub">{it["attr"]}</div>'
            f'{whenh}'
            f'<div class="sub src">{it["src"]}</div></div></div>')

cards = "\n".join(card_html(it) for it in ALL)
import json
absj = json.dumps(ABS_DEF, ensure_ascii=False)
srvj = json.dumps(SRV_DEF, ensure_ascii=False)

CSS = """
body{font-family:"Microsoft YaHei",sans-serif;background:#f4f5f7;margin:0;padding:0 24px 40px;color:#222}
h1{font-size:22px;padding-top:20px}
.d{color:#666;font-size:13px;line-height:1.7;max-width:1080px}
.bar{position:sticky;top:0;background:#f4f5f7;padding:10px 0;z-index:9;border-bottom:1px solid #e0e0e0}
.bar button{border:1px solid #cfd6e4;background:#fff;color:#33408a;border-radius:16px;padding:5px 13px;margin:3px 4px 3px 0;font-size:12.5px;cursor:pointer}
.bar button.on{background:#4a6cf7;color:#fff;border-color:#4a6cf7;font-weight:600}
.axis{margin:8px 0 2px}.axis span{color:#888;font-size:12px;margin-right:6px}
.axis button{border:1px solid #d8b48a;background:#fff;color:#9a5b1d;border-radius:6px;padding:4px 12px;margin-right:6px;font-size:12.5px;cursor:pointer}
.axis button.on{background:#e8862e;color:#fff;border-color:#e8862e;font-weight:600}
.erasec{margin-top:24px}
.erasec h2{border-left:5px solid #4a6cf7;padding-left:11px;font-size:17px;margin-bottom:2px}
.erasec h2 small{color:#999;font-size:12px;font-weight:400;margin-left:6px}
.erasec .cnt{background:#eef1ff;color:#4a6cf7;border-radius:10px;padding:1px 9px;font-size:12px;margin-left:6px}
.edesc{color:#888;font-size:12px;margin:2px 0 10px;padding-left:12px}
.grid{display:flex;flex-wrap:wrap;gap:12px}
.card{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:152px;overflow:hidden}
.card.big{width:170px}
.thumb{display:flex;align-items:center;justify-content:center;height:124px;background:repeating-conic-gradient(#e6e8ec 0 25%,#f2f3f6 0 50%) 50%/16px 16px}
.thumb.big{height:200px}.thumb img{max-width:142px;max-height:118px}.thumb.big img{max-width:164px;max-height:194px}
.thumb.miss{color:#bbb;font-size:12px}
.meta{padding:7px 9px;font-size:11px;line-height:1.5}.meta b{font-size:12px}
.sub{color:#777;margin-top:2px}.sub.px{color:#bbb;font-size:10px}.sub.src{color:#b5651d;font-weight:600}
.sub.when{color:#1a7f5a;font-weight:600;background:#eafaf2;border-radius:4px;padding:2px 5px}
.tag{background:#4a6cf7;color:#fff;border-radius:4px;padding:1px 6px;font-size:10px}
code{background:#eef;border-radius:3px;padding:1px 4px;font-size:12px}
#pool{display:none}
"""

JS = """
const ABS=%s, SRV=%s;
let AXIS='abs', MOD='all';
const pool=document.getElementById('pool'), view=document.getElementById('view');
function render(){
  document.querySelectorAll('#view .card').forEach(c=>pool.appendChild(c));
  view.innerHTML='';
  const defs = AXIS==='abs'?ABS:SRV;
  for(const [bid,title,desc] of defs){
    const cs=[...pool.children].filter(c=>c.dataset[AXIS]===bid && (MOD==='all'||c.dataset.m===MOD));
    if(!cs.length) continue;
    cs.sort((a,b)=>(a.dataset.mo-b.dataset.mo)||0);
    const sec=document.createElement('div'); sec.className='erasec';
    sec.innerHTML=`<h2>${title}<span class=cnt>${cs.length}</span></h2><div class=edesc>${desc}</div>`;
    const g=document.createElement('div'); g.className='grid';
    cs.forEach(c=>g.appendChild(c));
    sec.appendChild(g); view.appendChild(sec);
  }
}
function setMod(m,btn){MOD=m;document.querySelectorAll('.bar button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');render();}
function setAxis(a,btn){AXIS=a;document.querySelectorAll('.axis button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');render();}
window.onload=render;
""" % (absj, srvj)

MODS = [("all","全部"),("m1","①技能皮肤"),("m2","②纪念卡"),("m3","③家具"),("m4","④装饰"),
        ("m5","⑤表情"),("m6","⑥头衔/头像框"),("m7","⑦航迹/船"),("m8","⑧羁绊贴纸")]
barbtns = "".join(f'<button class="{"on" if m=="all" else ""}" onclick="setMod(\'{m}\',this)">{l}</button>' for m, l in MODS)

H = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>X3 非节日外显 · 时间轴图鉴</title>',
 f'<style>{CSS}</style>',
 '<h1>X3 非节日外显投放图鉴 · 双时间轴</h1>',
 '<p class="d">每件外显贴实物图 + <b style="color:#b5651d">具体礼包/活动来源</b>（橙字）+ <b style="color:#1a7f5a">投放D天/解锁条件</b>（绿字，如「🕐 D8 起 · 获得斯隆后2天」）。'
 '上排<b>分类页签</b>筛模块；下排<b>时间轴切换</b>：'
 '<b>绝对时间</b>=内容版本发布顺序(2024→2026)；<b>服务器时间</b>=玩家生命周期 D0→D60+（每件在一个服里第几天可得）。'
 '英雄/皮肤 D 天来自 GSheet「英雄投放节奏」表（权威），配置真源 <code>C:\\x3\\gdconfig\\tsv\\</code>，2026-06-18。</p>',
 '<div class="bar">'
 f'<div>{barbtns}</div>'
 '<div class="axis"><span>时间轴：</span>'
 '<button class="on" onclick="setAxis(\'abs\',this)">绝对时间（版本发布）</button>'
 '<button onclick="setAxis(\'srv\',this)">服务器时间（D0→D60+）</button></div>'
 '</div>',
 '<div id="view"></div>',
 f'<div id="pool">{cards}</div>',
 f'<script>{JS}</script>',
 '<p class="d" style="margin-top:36px;color:#999;border-top:1px solid #ddd;padding-top:12px">'
 '配置真源 <code>C:\\x3\\gdconfig\\tsv\\</code>（只读）· 图标 <code>Res/UI/Spirits</code> · 生成脚本 <code>_gen_nonfestival_cosmetics.py</code>，重跑刷新。'
 '时间轴为版本/生命周期的<b>合理分桶</b>（X3 走 TimeCycle 服务器相对时间，非绝对日历；绝对轴用纪念卡年份+英雄发行序为锚）。</p>',
 '</html>']

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "X3非节日外显投放图鉴.html")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(H))
print("WROTE", out, os.path.getsize(out))
from collections import Counter
print("total cards:", len(ALL))
print("by module:", Counter(i["m"] for i in ALL))
print("by abs:", Counter(i["abs"] for i in ALL))
print("by srv:", Counter(i["srv"] for i in ALL))
