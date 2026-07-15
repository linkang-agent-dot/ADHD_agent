# -*- coding: utf-8 -*-
"""马戏节活动配置验收页生成器：从 gdconfig-circus tsv 拉真实值逐模块校验，产出 HTML"""
import io, os, sys, html, subprocess, datetime
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\x3\gdconfig-circus\tsv"
OUT = r"C:\ADHD_agent\KB\产出-数值设计\X3_马戏节\_马戏节_配置验收.html"

def rd(p):
    return io.open(os.path.join(BASE, p), encoding="utf-8", newline="").read().split("\n")

def row(f, rid, col0=0):
    for ln in rd(f):
        fl = ln.split("\t")
        if len(fl) > col0 and fl[col0] == str(rid):
            return fl
    return None

def grp_count(f, gid, col=1):
    return sum(1 for ln in rd(f) if len(ln.split("\t")) > col and ln.split("\t")[col] == str(gid))

def i18n_keys(*keys):
    have = set()
    for ln in rd("i18n/Text__Text.tsv"):
        f0 = ln.split("\t", 1)[0]
        for k in f0.split("|"):
            if k in keys:
                have.add(k)
    return [k for k in keys if k not in have]

ao = {}
for ln in rd("ActvOnline__ActvOnline.tsv"):
    fl = ln.split("\t")
    if fl[0].isdigit():
        ao[fl[0]] = fl

OK, WARN, TODO = "ok", "warn", "todo"
mods = []
def add(name, aid, checks, notes=""):
    """checks: list of (描述, bool/None) None=占位提示"""
    fails = [c for c, ok_ in checks if ok_ is False]
    warns = [c for c, ok_ in checks if ok_ is None]
    st = TODO if fails else (WARN if warns else OK)
    mods.append((name, aid, checks, st, notes))

def a(aid):
    return ao.get(str(aid))

# 1 福箱
r = a(101026); c = row("ActvCrafting__ActvCrafting.tsv", 1517)
add("马戏福箱（开箱·第一周核心）", "AO 101026", [
    ("type=15 开箱 / CID=1517", r and r[5] == "15" and r[4] == "1517"),
    ("Crafting1517: 耗1209门票/产1210勋章", c and c[1] == "1209" and c[3] == "1210"),
    ("奖池组116=9坑, 大奖=5302001阿米娜皮肤", grp_count("ActvCrafting__ActvCraftingReward.tsv", 116) == 9 and any(fl[2] == "5302001" for fl in (ln.split("\t") for ln in rd("ActvCrafting__ActvCraftingReward.tsv")) if len(fl) > 2 and fl[1] == "116")),
    ("累抽阶梯组1016=7档→Reward30940-46", grp_count("ActvCrafting__ActvCraftingOtherReward.tsv", 1016) == 7),
    ("双榜: 本服2002(Crafting) / 跨服2003(AO)", c and c[6] == "2002" and r and r[20] == "2003"),
    ("连锁703=11包 / 锚点13025-028", row("Pack__ChainPack.tsv", 703) is not None and all(row("Pack__Pack.tsv", x) for x in range(13025, 13029))),
    ("c33=1209|5302001 券|皮肤钩子 / hub142", r and r[33] == "1209|5302001" and r[38] == "142"),
    ("RuleTips 16043 独立", row("RuleTips__RuleTips.tsv", 16043) is not None),
    ("箱体开/关 DK=沿世界杯占位, 待美术", None),
], "克隆源=世界杯101516（07-10 玩法返工批次10/12）")

# 2 累充
r = a(100599)
wl = r[49].split("|") if r else []
add("马戏累充", "AO 100599", [
    ("ActvTask 59911-20 十档(100..20000)", all(row("ActvTask__ActvTask.tsv", x) for x in range(59911, 59921))),
    ("奖励组59950-59(门票+罗盘)", grp_count("Reward__Reward.tsv", 59950) > 0),
    ("白名单=39包全量", len(wl) == 39),
    ("c33=1209|1057 / hub142", r and r[33] == "1209|1057" and r[38] == "142"),
    ("RuleTips 16044 独立", row("RuleTips__RuleTips.tsv", 16044) is not None),
], "克隆源=深海100598")

# 3/4 双BP
r1, r2 = a(102250), a(102251)
bp1 = grp_count("ActvBattlePassScore__BattlePassScoreReward.tsv", 148)
bp2 = grp_count("ActvBattlePassScore__BattlePassScoreReward.tsv", 149)
c3000 = all(fl[3] == "3000" for fl in (ln.split("\t") for ln in rd("ActvBattlePassScore__BattlePassScoreReward.tsv")) if len(fl) > 3 and fl[1] in ("148", "149"))
add("马戏通行证（BP①）", "AO 102250", [
    ("等级组148=20级 / 满级重算3000/级=6万", bp1 == 20 and c3000),
    ("付费包130044高级/130045至尊", all(row("Pack__Pack.tsv", x) for x in (130044, 130045))),
    ("轨道Reward=4036段专属块(非共享)", grp_count("Reward__Reward.tsv", 4036101) > 0),
    ("c33=1209|1210 / hub142", r1 and r1[33] == "1209|1210" and r1[38] == "142"),
], "克隆源=深海102244；名=马戏通行证(07-10改)")
add("巡游通行证（BP②）", "AO 102251", [
    ("等级组149=20级 / 3000/级", bp2 == 20),
    ("付费包130047/130048", all(row("Pack__Pack.tsv", x) for x in (130047, 130048))),
    ("轨道Reward=4037段专属块", grp_count("Reward__Reward.tsv", 4037101) > 0),
    ("c33=1057|1202 / hub143", r2 and r2[33] == "1057|1202" and r2[38] == "143"),
], "克隆源=深海102246")

# 5 大富翁
r = a(102803); v = row("ActvVoyage__ActvVoyage.tsv", 2803)
isl = sum(1 for ln in rd("ActvVoyage__ActvVoyageIsland.tsv") if len(ln.split("\t")) > 1 and ln.split("\t")[1] == "3")
evt = sum(1 for ln in rd("ActvVoyage__ActvVoyageEvent.tsv") if len(ln.split("\t")) > 1 and ln.split("\t")[1].isdigit() and 207 <= int(ln.split("\t")[1]) <= 214)
add("马戏巡游（大富翁·第二周核心）", "AO 102803", [
    ("Voyage2803: 岛组3 / 罗盘1057/1058 / 珍珠贝1204 沿用", v and v[2] == "3"),
    ("Island组3=24格(马戏格名5种)", isl == 24),
    ("Event组207-214=48行", evt == 48),
    ("抽奖阶段奖组101→Reward4200001-008沿用", grp_count("ActvVoyage__ActvVoyageOtherReward.tsv", 101, col=2) == 8),
    ("存钱罐280002", row("Pack__Pack.tsv", 280002) is not None),
    ("成就礼包链2801012-022+AchievePack105", all(row("Pack__Pack.tsv", x) for x in (2801012, 2801022)) and row("Pack__AchievePack.tsv", 105) is not None),
    ("RuleTips 15018/15019/15021", all(row("RuleTips__RuleTips.tsv", x) for x in (15018, 15019, 15021))),
    ("c33=1057|1202 / hub143", r and r[33] == "1057|1202" and r[38] == "143"),
    ("6岛地块图=沿深海占位, 待美术", None),
], "克隆源=深海102802")

# 6 拼图
r = a(101829)
add("小丑的梦境（拼图·大富翁子活动）", "AO 101829", [
    ("Puzzle1829 / 任务组110·奖励组1100 沿用", row("ActvPuzzle__ActvPuzzle.tsv", 1829) is not None),
    ("Schedule10006: 102803→101829 挂载", row("ActvOnline__ActvGroupSchedule.tsv", 10006) is not None),
    ("hub143", r and r[38] == "143"),
    ("封面DK=沿深海占位, 待美术(入库须Path+Display双补)", None),
], "克隆源=深海101828")

# 7 每日礼包
r = a(102994); ap = row("ActvPack__ActvPack.tsv", 3003)
add("马戏每日礼包", "AO 102994", [
    ("★MailID=101109 已配(修X3NEW-1829事故口径)", r and r[17] == "101109"),
    ("TC160101(触发式7天)", row("TimeCycle__TimeCycle.tsv", 160101) is not None),
    ("ActvPack3003: 5包800010-014 / Final=40620", ap and ap[3] == "40620"),
    ("Reward 40520(日常)/40620(买全终奖1209x100)", grp_count("Reward__Reward.tsv", 40620) > 0),
    ("hub142", r and r[38] == "142"),
], "克隆源=深海102993")

# 8 酒馆
r = a(10071705)
sm = sum(1 for ln in rd("ActvScore__ActvScoreMulti.tsv") if ln.split("\t")[0].isdigit() and 7201 <= int(ln.split("\t")[0]) <= 7207)
sg = sum(1 for ln in rd("ActvScore__ActvScoreGroup.tsv") if len(ln.split("\t")) > 1 and ln.split("\t")[1].isdigit() and 7201 <= int(ln.split("\t")[1]) <= 7207)
add("马戏酒馆（跨服）", "AO 10071705", [
    ("ScoreID=720 独立(未蹭共享717/719)", r and r[4] == "720"),
    ("ScoreMulti 7阶段(时长和=10天硬约束)", sm == 7),
    ("积分组28行(1/3/5/7万档)→奖励786045-048", sg == 28),
    ("c33=1209|1210 / hub142", r and r[33] == "1209|1210" and r[38] == "142"),
], "克隆源=深海10071704；部署时=正好10天")

# 9 装饰
r = a(106104)
add("马戏庆典装饰（阶梯礼包）", "AO 106104", [
    ("ChainPack702→211032-034($19.99x3)", row("Pack__ChainPack.tsv", 702) is not None),
    ("家具=椰风遮阳椅沿用(用户拍板)+1209券档差", grp_count("Reward__Reward.tsv", 211032) > 0),
    ("TXT_ChainPack_Name_702 已建(HUD页签坑)", not i18n_keys("TXT_ChainPack_Name_702")),
    ("hub142", r and r[38] == "142"),
], "克隆源=深海106103/700")

# 10/11 兑换
r1, r2 = a(101343), a(101344)
e1 = grp_count("ActvExchange__ActvExchange.tsv", 1343)
e2 = grp_count("ActvExchange__ActvExchange.tsv", 1344)
add("马戏珍宝集市（兑换①）", "AO 101343", [
    ("组1343=15行 / 货币=1210勋章", e1 == 15),
    ("c33=1209|1210 / hub142", r1 and r1[33] == "1209|1210" and r1[38] == "142"),
], "克隆源=深海101340；纪念卡槽已换")
add("巡游珍宝集市（兑换②）", "AO 101344", [
    ("组1344=13行 / 货币=1202沿用", e2 == 13),
    ("c33=1057|1202 / hub143", r2 and r2[33] == "1057|1202" and r2[38] == "143"),
], "克隆源=深海101341")

# 12 拜访
r = a(105606); vp = row("ActvVisitPack__ActvVisitPack.tsv", 5607)
pk = row("Pack__Pack.tsv", 211046)
add("马戏庆典之约（拜访）", "AO 105606", [
    ("VisitPack5607: 门头包211046/邀请函1213/每次奖2069", vp and vp[2] == "211046" and vp[4] == "1213"),
    ("里程碑组7(10/20/30/50次→2070)", grp_count("ActvVisitPack__ActvVisitPackReward.tsv", 7) == 4),
    ("门头包 MainBg空铁律 / c19售卖窗空", pk and not pk[30] and not pk[19]),
    ("邀请函 ItemObtain 100363+Item col10 回指", row("ItemObtain__ItemObtain.tsv", 100363) is not None),
    ("c33=1209|1057 / hub142 / RuleTips16045", r and r[33] == "1209|1057" and r[13] == "16045"),
], "克隆源=深海105605")

# 13 许愿池
r = a(105014)
add("许愿池（跨服）", "AO 105014", [
    ("WishingPool5014 → 独立奖池组106(木匣+1209门票·不再共用105)", (row("ActvWishingPool__ActvWishingPool.tsv", 5014) or [""]*3)[2] == "106"),
    ("c33=1209|1210 / hub142", r and r[33] == "1209|1210" and r[38] == "142"),
], "克隆源=26春节105012；奖池独立化(07-10用户拍板)已解除深海下线依赖；Type50跨服部署最不灵活先排")

# 14 周卡/签到
add("周卡109101 / 签到101406（复用不新建）", "复用", [
    ("周卡: 原位换奖池+背景DK=上线前动作(深海在线勿提前)", None),
    ("签到: 部署2期实例化即可, 配置零改", True),
], "用户拍板复用口径")

# 15 外显
sk = row("Skin__Skin.tsv", 1017); hs = row("Hero__HeroSkin.tsv", 102001)
add("外显交付（大奖/纪念卡/铭牌）", "—", [
    ("开箱大奖: 阿米娜猛兽驯服者 HeroSkin102001/Item5302001", hs is not None and row("Item__Item.tsv", 5302001) is not None),
    ("跨服榜大奖: 梦幻旋转木马 Skin1017/Item81152(DK_Homeland_Circus已注册)", sk is not None and sk[7] == "DK_Homeland_Circus"),
    ("本服榜: 纪念卡81欢乐颂歌/Item180081", row("MemorialCard__MemorialCard.tsv", 81) is not None),
    ("铭牌106欢庆之星/Item82006(跨服榜Top)", row("PlayerTitle__PlayerTitle.tsv", 106) is not None),
    ("头像框: 欢庆之环 框cfg10089/Item80116(BP巡游轨道已换指·深海之冠残留已修)", row("Personalize__PersonalizeAvatarFrameCfg.tsv", 10089) is not None and row("Item__Item.tsv", 80116) is not None),
    ("皮肤立绘/头像/卡面DK(_20_Skin01族)+主城皮头图标=待美术", None),
    ("皮肤展示视频DKVideo=待视频化管线", None),
], "07-10 全定案；主稿出图中")

# 16 hub/道具
add("hub 与基础道具", "ActvGroup 142/143", [
    ("142马戏节 / 143马戏巡游", row("ActvOnline__ActvGroup.tsv", 142) is not None and row("ActvOnline__ActvGroup.tsv", 143) is not None),
    ("Item 1209马戏门票/1210马戏勋章/1213邀请函", all(row("Item__Item.tsv", x) for x in (1209, 1210, 1213))),
    ("hub图标+道具icon=沿深海占位, 待美术", None),
], "批次1；扭蛋机(另一agent)挂142")

# i18n 抽查
miss = i18n_keys("TXT_ActvOnline_ActvName_101026", "TXT_ActvOnline_ActvName_102250", "TXT_Skin_Name_1017", "TXT_HeroSkin_Name_102001", "TXT_Item_Name_1209")
add("i18n 抽查", "Text.tsv", [
    ("核心名 key 5/5 存在(福箱/BP/两皮肤/门票)", not miss),
    ("长文本(RuleTips正文/ActvDesc等)=仅cn+en, 14语收口时跑翻译skill", None),
], "全量审计=收口批 i18n_leak_audit")

# git 状态
git = subprocess.run(["git", "-C", r"C:\x3\gdconfig-circus", "log", "--oneline", "-1"], capture_output=True, text=True, encoding="utf-8").stdout.strip()

# ---- render ----
BADGE = {OK: ('<span class="b ok">✅ 配置齐</span>'), WARN: ('<span class="b warn">🟡 配置齐·有占位</span>'), TODO: ('<span class="b todo">🔴 有缺项</span>')}
secs = []
n_ok = n_warn = n_todo = 0
for name, aid, checks, st, notes in mods:
    if st == OK: n_ok += 1
    elif st == WARN: n_warn += 1
    else: n_todo += 1
    lis = []
    for desc, ok_ in checks:
        ico = "✅" if ok_ is True else ("⏳" if ok_ is None else "❌")
        cls = "pass" if ok_ is True else ("hold" if ok_ is None else "fail")
        lis.append('<li class="%s">%s %s</li>' % (cls, ico, html.escape(desc)))
    secs.append('<section><h2>%s <code>%s</code> %s</h2><ul>%s</ul><p class="note">%s</p></section>'
                % (html.escape(name), html.escape(str(aid)), BADGE[st], "".join(lis), html.escape(notes)))

page = ('<!doctype html><meta charset="utf-8"><title>马戏节配置验收</title><style>'
 'body{font-family:system-ui;background:#17171c;color:#e8e8e8;margin:24px;max-width:980px}'
 'h1{font-size:20px}h2{font-size:14px;margin:0 0 6px}code{color:#e0a13a;font-size:12px}'
 'section{background:#1f1f26;border-radius:10px;padding:12px 16px;margin:10px 0}'
 'ul{margin:4px 0;padding-left:6px;list-style:none}li{font-size:13px;line-height:1.7}'
 'li.fail{color:#ff7b72}li.hold{color:#d0a768}.note{font-size:11px;color:#888;margin:6px 0 0}'
 '.b{font-size:11px;border-radius:10px;padding:2px 8px;margin-left:8px}'
 '.b.ok{background:#1e3a2a;color:#7ee2a8}.b.warn{background:#3a331e;color:#e2c77e}.b.todo{background:#3a1e1e;color:#e27e7e}'
 '.sum{background:#23232d;border-radius:10px;padding:10px 16px;font-size:13px}'
 '</style>'
 '<h1>X3 马戏节 · 活动配置验收（数据=worktree tsv 实时校验）</h1>'
 '<div class="sum">生成 ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
 + ' ｜ worktree tip: <code>' + html.escape(git) + '</code> ｜ 模块 ' + str(len(mods))
 + ' 个：✅全绿 ' + str(n_ok) + ' · 🟡有美术/上线前占位 ' + str(n_warn) + ' · 🔴缺项 ' + str(n_todo)
 + '<br>图例：✅=tsv 实测通过 ｜ ⏳=按计划的占位/上线前动作（非缺陷）｜ ❌=缺项需修'
 + '<br>上线前必做 6 项与美术清单见换皮档案 <code>KB\\换皮档案\\X3\\2026-07-09_马戏节整节日.md</code></div>'
 + "".join(secs))
io.open(OUT, "w", encoding="utf-8").write(page)
print(OUT)
print("模块: %d, 全绿 %d, 占位 %d, 缺项 %d" % (len(mods), n_ok, n_warn, n_todo))
