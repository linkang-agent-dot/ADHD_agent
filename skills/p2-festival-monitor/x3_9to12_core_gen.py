# -*- coding: utf-8 -*-
"""9–12 月规划 · 核心版（给 leader）：一张图 + 四个月做什么 + 目标账 + 开发需求。
详细版＝9-10月模块规划_周占比.html；本页只保留最核心的图表与需求。
依赖 scratchpad 里的 json（先跑过详细版的查询）。
"""
import json, os

SCR = r"C:/Users/linkang/AppData/Local/Temp/claude/C--Users-linkang/549921cb-db7d-4567-bdb3-e36bd4b4e0c7/scratchpad"
OUT = r"C:\ADHD_agent\KB\产出-数值设计\X3_8-10月节日需求\_9-12月规划_核心版.html"

TS = json.load(open(f"{SCR}/target_split.json", encoding="utf-8"))
DP, DX = TS["p2"], TS["x3"]


def series(fn):
    o = []
    for x in json.load(open(f"{SCR}/{fn}", encoding="utf-8")):
        fe, b, t, p = float(x["fest"]), x["fb"] or 0, float(x["total"]), x["payers"]
        if not p:
            continue
        o.append({"d": x["d"], "payrate": round(b / p * 100, 2),
                  "arppu": round(fe / b, 2) if b else 0, "fest": fe,
                  "share": round(fe / t * 100, 2)})
    return sorted(o, key=lambda r: r["d"])


def segments(rows, thr=10, tol=1, mn=4):
    out, cur, miss = [], [], 0
    for r in rows:
        if r["payrate"] >= thr:
            cur.append(r); miss = 0
        elif cur:
            miss += 1
            if miss > tol:
                out.append(cur); cur, miss = [], 0
            else:
                cur.append(r)
    if cur:
        out.append(cur)
    return [s for s in out if len(s) >= mn]


NAME = {"2026-05-12": ("P2 拓荒节", "#c084fc", 2.6, ""),
        "2026-06-10": ("P2 深海节", "#a78bfa", 1.8, "6 4"),
        "2026-06-26": ("X3 世界杯+深海", "#5ad1ff", 2.8, ""),
        "2026-05-29": ("X3 夏日恋语", "#38bdf8", 2.0, "6 4")}
SEGS = []
for fn, side in (("p2_daily.json", "P2"), ("x3_daily.json", "X3")):
    for s in segments(series(fn)):
        if s[0]["d"] not in NAME:
            continue
        nm, c, w, dash = NAME[s[0]["d"]]
        pr = sorted(x["payrate"] for x in s)
        ap = sorted(x["arppu"] for x in s)
        SEGS.append({"name": nm, "side": side, "color": c, "w": w, "dash": dash,
                     "n": len(s), "rev": round(sum(x["fest"] for x in s)),
                     "pr": round(pr[len(pr) // 2], 1), "ap": round(ap[len(ap) // 2], 1),
                     "pts": [{"i": i, "d": r["d"], "payrate": r["payrate"],
                              "arppu": r["arppu"], "fest": r["fest"]} for i, r in enumerate(s)]})
SEGS.sort(key=lambda z: (z["side"], -z["rev"]))

# ---- 节日收入月占比：P2 基准 vs X3 现状 ----
MO = json.load(open(f"{SCR}/monthly.json", encoding="utf-8"))
P2M = [{"m": x["m"], "fest": float(x["fest"]), "total": float(x["total"]),
        "sh": float(x["fest"]) / float(x["total"]) * 100} for x in MO["p2"]]
X3M = [{"m": x["m"], "fest": float(x["fest"]), "total": float(x["total"]),
        "sh": float(x["fest"]) / float(x["total"]) * 100} for x in MO["x3"]]
_full = sorted(r["sh"] for r in P2M if r["m"] < "2026-07")
P2M_MED, P2M_LO, P2M_HI = _full[len(_full) // 2], _full[0], _full[-1]
P2M_LO_M = [r["m"] for r in P2M if abs(r["sh"] - P2M_LO) < .05][0]
P2M_HI_M = [r["m"] for r in P2M if abs(r["sh"] - P2M_HI) < .05][0]

MONTHS = [
 {"mo":"9 月","theme":"周年狂欢","c":"#4ade80","act":"先把<b>节日收入月占比</b>拉起来",
  "kn":"节日收入月占比","kv":"15% → <b>20–25%</b>","cap":16,
  "dev":[("挖孔 v1（P2 最强单品搬运）",10,"力"),("<b>新海妖皮肤系统</b>（新建）",5,"力"),("弹珠",5,"力"),
         ("<b>开箱活动 · 周年限定宝箱版本</b>（独立单）",3,"我"),("<b>复用活动全部包装及配置</b>（约 16 个沿用活动换皮）",6,"我"),
         ("<b>周年行军特效搬运</b>（对接 + FxID 绑定 + DK 注册）",3,"我"),("<b>全部内容的美术资源进包</b>（P2→X3 规格/材质/DK）",5,"我"),("挖孔 v1 · <b>数值与奖池配置</b>",3,"我"),("海妖皮肤 · <b>数据与投放配置</b>",1,"我")],
  "art":[(1,0,"普通主城皮肤","二周年限定 · <b>普通档</b>","P2 海盗船 · 搬运",
          "W1 内外圈<b>外圈</b>＝随机走量（$19.99 档）"),
         (1,1,"高级主城皮肤","二周年限定 · <b>高级档</b>","P2 海盗船 · 搬运 ＋<b>新增品质档</b>",
          "W1 内外圈<b>内圈</b>＝固定收鲸（$99.99 档）"),
         (1,0,"英雄皮肤","周年 · <b>史诗（$49.99）</b>","新做","W2 挖孔 · <b>前 50 刀阶段奖励＝转化钩子</b>"),
         (1,0,"英雄皮肤","周年 · <b>限定</b>","新做","W2 挖孔<b>顶奖</b>"),
         (1,1,"海妖皮肤","新海妖皮肤","新做（<b>新系统</b>）","W3 弹珠<b>大奖</b>"),
         (0,0,"航行特效","周年行军特效","P2 周年庆 · 搬运","W3 配套外显"),
         (0,0,"航行特效","X3-1 周年行军装扮<b>返场</b>","返场（美术成本已付）","W3 开箱返场批次"),
         (0,0,"门头三件套","周年门头套装（建议）","新款（系统已在投 44 款）","随版本"),
         (0,0,"头衔 / 聊天表情","周年款（建议）","2D 轻量","全程常驻")],
  "weeks":[("W1 · D0–D6","<span style='color:var(--dim2)'>内外圈抽奖</span><span class='rz rz-old'>8月首投·复用</span>","<span class='nc'><b>主城皮肤 · 二周年限定（普通+高级）</b></span>　—— 外圈随机走量、内圈固定收鲸"),
           ("W2 · D7–D13","<span style='color:#f87171'>挖孔 v1</span><span class='rz rz-new'>新建</span>","<span class='nc'><b>英雄皮肤 · 史诗（$49.99 钩子）＋ 周年限定</b></span>　—— 钩子把人推过前 50 刀"),
           ("W3 · D14–D20","<span style='color:#f87171'>弹珠</span><span class='rz rz-new'>新建</span> ＋ <span style='color:var(--dim2)'>开箱</span><span class='rz rz-old'>复用</span>","<span class='nc'><b>海妖皮肤</b></span>（弹珠大奖）＋ <span class='nc'><b>一批皮肤返场</b></span>（开箱）")],
  "why":"9 月做的是<b>「填内容 + 拉长度」</b>，直接作用在总量上 ⇒ 本月只考核<b>月占比</b>一个数，不拆因子。节日期<b>满 21 天不断档</b>是硬前提"},
 {"mo":"10 月","theme":"万圣节","c":"#5ad1ff","act":"<b>付费率与付费深度同步拉</b>",
  "kn":"付费率 ＋ 节日 ARPPU","kv":f"{DX['payrate']:.1f}%→40%+　${DX['arppu']:.1f}→$30.5+","cap":16,
  "dev":[("主城皮肤套装<b>系统功能开发</b>",7,"力"),("装饰物升级系统",3,"力"),("<b>团购礼包</b>（P2 搬运）",3,"力"),
         ("<b>复用活动包装及配置</b>（克隆脚本可复用）",4,"力"),
         ("<b>红色英雄皮肤 + 互动系统</b>（走 feature/skin-moment）",5,"我"),("<b>节日卡册</b> <span style='color:var(--dim2)'>或</span> <b>联盟总动员 · 节日版</b>（<span style='color:var(--warn)'>二选一</span>）",5,"我"),
         ("<b>预购连锁礼包</b>（P2 搬运）",3,"我"),("<b>主城套装 · 美术资源搬运沟通</b>（P2→X3 规格对齐）",3,"我")],
  "art":[(1,1,"主城皮肤套装","<b>主城皮肤套装（首期）</b>","<b>新系统</b> ＋ 内容",
          "<b>万圣节不出独立主城皮肤，只做套装</b>＝把「买一件」变「集一套」"),
         (1,1,"英雄皮肤","<b>红色英雄皮肤 · 带互动系统</b>","新做 · <b>新品质顶档</b>","与 9 月史诗档形成分层：<b>史诗＝静态+$49.99 钩子走量 · 红色＝带互动+顶格定价收鲸</b>"),
         (1,0,"英雄皮肤","万圣节英雄皮肤","新做","开箱<b>大奖</b>"),
         (0,1,"卡册","节日卡册","<b>新增收集线</b>","坑深决定深度"),
         (0,0,"装饰","装饰升级（已售出续费口）","系统（载体已有 146 款）","不出新美术"),
         (0,0,"头像","补头像位（建议）","2D 轻量","15 款 vs 头像框 96 款")],
  "weeks":[("W1 · D0–D6","<span style='color:var(--dim2)'>内外圈抽奖</span><span class='rz rz-old'>复用</span>",
            "★ <span class='nc'><b>主城皮肤套装 · 首期</b></span>（套装系统上线）——把「买一件」变「集一套」"),
           ("W2 · D7–D13","<span style='color:var(--dim2)'>挖孔</span><span class='rz rz-old'>9月建成·复用</span>",
            "★ <span class='nc'><b>红色英雄皮肤 + 互动系统</b></span>（顶格新品质档，靠互动而非数值做差异）"),
           ("W3 · D14–D20","<span style='color:var(--dim2)'>开箱 ＋ 弹珠</span><span class='rz rz-old'>复用</span>",
            "★ <span class='nc'><b>万圣节英雄皮肤</b></span>（开箱大奖）· <span class='nc'><b>节日卡册</b></span>开启（新收集线）"),
           ("全程 · D0–D20","<span style='color:#f87171'>预购连锁 ＋ 团购</span><span class='rz rz-new'>新搬运</span>",
            "<span class='nc'><b>预购连锁礼包</b></span>（收鲸·人均$167.7）＋ <span class='nc'><b>团购礼包</b></span>（宽入口·4,941 买家）· <span class='nc'>装饰升级系统</span>")],
  "why":"前四方向拉<b>深度</b>、方向 5 <b>双拉</b>；两个因子必须同时抬——占比＝付费率×ARPU。"
        "🔑<b>英雄皮肤的分层由此定死</b>：史诗＝静态动画 + $49.99 + 挂玩法前 50 刀钩子（<b>走量</b>）· "
        "红色＝<b>带互动系统</b> + 顶格定价（<b>收鲸</b>）——两档差异不在属性数值而在<b>有没有互动</b>。"
        "这点很关键：现有四档梯度（至尊+150%/传说+100%/史诗+50%/限定+30%）<b>全靠数值区分，结果至尊档只有 11 人持有</b>，"
        "证明光加档位没用；互动系统已有在途分支 <code>feature/skin-moment</code>（代码就绪，差拼 prefab + 实机验证）"},
 {"mo":"11 月","theme":"黑五","c":"#fbbf24","act":"黑五 ＋ 钓鱼 ＋ 查漏补缺",
  "kn":"两项一起结账","kv":"补 9/10 月未达成项","cap":16,
  "dev":[("钓鱼形式搬运（P2）",5),("<b>累充改造为联盟累充</b>",3),("<b>新增主城特效系统</b>（系统+搬运+接入）",5),("黑五双轨礼包（纯配置）",2),("<b>复用活动全部包装及配置</b>",4),("9/10 月欠账回补（预留）",8)],
  "art":[(1,0,"高级主城皮肤","<b>钓鱼主城皮肤</b>","新做（沿用 9 月新增的高级档）",
          "<b>钓鱼的大奖载体</b>（新形式配新皮）　<span style=\"color:var(--warn)\">档位待你确认</span>"),
         (1,0,"英雄皮肤","<span class='nc'><b>黑五英雄皮肤（限定 + 史诗）</b></span>","新做 · 双档","史诗＝$49.99 钩子档 / 限定＝顶奖"),
         (1,0,"海妖皮肤","<b>海妖皮肤 · 第二期</b>","新做（系统已在 9 月建成）","系统只摊一次 ⇒ 二期纯内容"),
         (1,0,"—","<b>黑五小额宽入口</b>（$0.99–4.99）","P2 搬运 · 纯配置","<b>拉付费率的最快杠杆</b>：P2 单品 5,822 买家 / 人均 $10.5"),
         (1,0,"—","<b>黑五大额收鲸档</b>","P2 搬运 · 纯配置","终极连锁人均 $174 / 折扣 $124 / 大额 $99"),
         (0,0,"头衔 / 表情 / 航迹","轻量 2D（建议带）","低成本","填投放日历")],
  "weeks":[("W1 · D0–D6","<span style='color:#f87171'>黑五双轨</span><span class='rz rz-new'>新·纯配置</span>",
            "★ <b>黑五英雄皮肤（限定 + 史诗）</b>｜小额宽入口拉付费率（P2 单品 5,822 买家）＋ 大额收鲸（人均 $174）"),
           ("W2 · D7–D13","<span style='color:#f87171'>钓鱼</span><span class='rz rz-new'>新形式搬运</span>",
            "★ <span class='nc'><b>钓鱼主城皮肤</b></span>（新形式配新皮）——钓鱼周占比中位 12.5%、人均 4.8 单靠复购稳收入"),
           ("W3 · D14–D20","<span style='color:var(--dim2)'>内外圈 ／ 开箱</span><span class='rz rz-old'>复用</span>",
            "★ <span class='nc'><b>海妖皮肤 · 第二期</b></span>（系统 9 月已建成，纯内容）· <span class='nc'><b>主城特效首发</b></span>（X3 新外显位）"),
           ("全程 · D0–D20","<span style='color:#f87171'>累充改联盟累充</span><span class='rz rz-new'>改造</span>",
            "全程在线的深度改造：P2 联盟版人均 $75.6 / 4.7 单 vs 普通版 $38.5 / 3.0 单（<b>人均 1.96×</b>）")],
  "why":"黑五是<b>价格驱动</b>不靠新外显、内容压力最小 ⇒ 同时承担「补短板 + 稳收入 + 结账」三件事"},
 {"mo":"12 月","theme":"圣诞","c":"#c084fc",
  "act":"冲流水（年度收官）","kn":"月度节日占比","kv":"全年最高点","cap":16,
  "dev":[("<b>猜酒杯形式搬运（P2）</b>",5),("套装 2 期（美术 + 配置）",3),("弹珠 · 挖孔 复用（换皮配置）",2),("圣诞行军特效搬运",2),("<b>复用活动全部包装及配置</b>",4)],
  "art":[(1,0,"主城皮肤套装","<b>主城套装 2 期</b>","系统已摊完 · 只出美术+配置","<b>半年性价比最高的一次投放</b>"),
         (1,0,"普通主城皮肤","<b>普通圣诞皮肤 · 直售</b>","新做","<b>不走抽奖、直接卖</b>＝补一个确定性购买入口"),
         (1,0,"英雄皮肤","<span class='nc'><b>圣诞英雄皮肤（限定 + 史诗）</b></span>","新做 · 双档","史诗＝$49.99 钩子 / 限定＝顶奖"),
         (1,0,"海妖皮肤","<b>圣诞海妖皮肤</b>","新做（系统已建成）","系统第三次复用，纯内容"),
         (1,0,"航行特效","<b>圣诞行军特效</b>","新做 / 搬运","成熟位，随节日出"),
         (0,0,"门头三件套 / 头像 / 头衔 / 表情","圣诞款（建议）","低成本","填投放日历")],
  "weeks":[("W1 · D0–D6","<span style='color:#f87171'>猜酒杯</span><span class='rz rz-new'>新形式搬运</span>",
            "★ <span class='nc'><b>圣诞海妖皮肤</b></span>（系统第三次复用）｜猜酒杯周占比中位 16.0%、人均 6.2 单、顶档仅 $99.99"),
           ("W2 · D7–D13","<span style='color:var(--dim2)'>挖孔</span><span class='rz rz-old'>复用·只换皮</span>",
            "★ <b>圣诞英雄皮肤（限定 + 史诗）</b>——史诗当 $49.99 钩子、限定当顶奖"),
           ("W3 · D14–D20","<span style='color:var(--dim2)'>弹珠</span><span class='rz rz-old'>复用·只换皮</span>",
            "★ <span class='nc'><b>主城套装 2 期</b></span>（系统已摊完）＋ <span class='nc'><b>普通圣诞皮 · 直售</b></span>（不走抽奖的确定性入口）"),
           ("全程 · D0–D20","<span style='color:#f87171'>圣诞行军特效</span><span class='rz rz-new'>新做</span> ＋ <span style='color:var(--dim2)'>常驻货架</span><span class='rz rz-old'>复用</span>",
            "<span class='nc'><b>五类外显同月铺开</b></span>；形式全是<span class='oc'>复用</span> ⇒ 开发仅 16d 却铺满全月")],
  "why":"<b>形式＝两个复用（弹珠+挖孔）＋ 猜酒杯，外显铺五类</b>——用已建成的形式承载大量新内容，开发最省产出最大。"
        "猜酒杯还补上了<b>P2 vs X3 的最大单项差距</b>：它对位 X3 转盘，单项付费玩家 ARPU 差 <b>$14.7＝总差 $24.9 的 59%</b>（充值直接参与+排行强循环 vs 礼包送券弱循环）。"
        "P2 12 月节日月占比 <b>39.0%</b>，<b>年底是该冲的月份不是收摊的</b>"},
]

# ---- 现有外显载体全集（配置表实查 2026-07-29）+ 可挖掘点 ----
CARRIERS = [
    ("英雄皮肤", "Hero__HeroSkin", 106, "48 款可获取 · <b>仅 25 款有专属英雄卡</b>",
     "已在投", "10 月加红色新品质档；<b>23 款无专属卡的要先定死美术规格</b>"),
    ("头像框", "PersonalizeAvatarFrameCfg", 96, "深海款<b>零成交</b>", "死货架",
     "并进套装卖或砍掉腾货架位，别再单独铺"),
    ("纪念卡", "MemorialCard", 86, "9 月已迭代＝拆分投放定位", "已在投",
     "系统级优化待找竞品（三类对标：SLG集卡/二游收集/P2集卡册）"),
    ("装饰（单个）", "FurnitureDecorate", 146, "含大量功能性家具，节日位远少于 146",
     "偏弱", "10 月<b>升级系统</b>＝给已售出装饰开续费口，不出新美术"),
    ("门头三件套", "FurnitureSkin", 44, "横梁 12 / 墙纸 13 / 地板 17", "在投",
     "9 月周年可出一套；三件套是现成分层结构"),
    ("头衔", "PlayerTitle", 31, "在装扮界面佩戴", "在投", "低成本随节日出，无需单独排期"),
    ("主城皮肤", "Skin (Type=1)", 20,
     "<b>品质全封顶在 3（紫）</b>：品质3×15 / 2×2 / 1×1 / 默认×1，连 8 月马戏节新皮（ID1017）也是品质3。"
     "战力只有 50000 / 100000 两档。<b>单件售卖，无套装概念</b>",
     "已在投",
     "拆三类：<b>普通</b>（＝现有 20 款这一档）· <b style='color:var(--bad)'>高级＝新增品质档（品质4）</b>，"
     "9 月周年双档里的高级档就是它，跟英雄皮肤加红色顶档同性质 · "
     "<b style='color:var(--bad)'>套装＝新系统</b>，10 月建成 → 12 月出 2 期（系统只摊一次）"),
    ("头像", "PersonalizeAvatarCfg", 15, "<b>与头像框 96 款严重不对称</b>", "可挖",
     "头像框有 96 款、头像只有 15 款 ⇒ <b>头像位是低成本可挖空间</b>"),
    ("航行特效（航迹）", "Skin (Type=2)", 14, "几乎每节日一款，成熟投放位", "已在投",
     "9 月出周年行军特效（搬 P2）+ X3-1 周年装扮返场"),
    ("家具皮肤", "FurnitureDecorateSkin", 12, "青铜/白银/黄金三档<b>带不同属性</b>", "在投",
     "🔑<b>X3 内部已跑通的「同外显分品质」先例</b>，直接给 10 月英雄皮肤分品质当依据"),
    ("聊天表情", "ChatEmojyReply", 11, "2D 轻量", "在投", "随节日低成本出"),
    ("船只装扮", "已有系统", None, "系统已存在（不在 Skin 表，另有归属）", "在投",
     "与航行特效成套投放；<b>本轮不新增需求</b>"),
]

DIG = [
    ("皮肤返场机制", "机制",
     "48 款里 <b>3 款零持有</b>；红绸剑姬·阿米娜（至尊+150%）仅 11 人持有而阿米娜有 <b>599,305 人</b>解锁 ⇒ 潜在受众近 60 万，<b>美术成本早已付过</b>",
     "3 d", "<b>9 月 W3 已排</b>"),
    ("头像位扩充", "内容",
     "头像框 96 款 vs 头像 15 款，同一界面两个位严重不对称；头像是 2D 轻资产", "2 d", "10 或 12 月随节日带"),
    ("死货架止损", "清理",
     "头像框（深海款）与家具礼包<b>连续零成交</b>；先并进套装或砍掉，别再排美术", "1 d", "9 月随版本"),
    ("拜访礼包提曝光", "优化",
     "ARPPU <b>$100</b> 却只有 <b>24 人</b>购买（1.4%）＝定价没错、曝光/门槛错。<b>提曝光近乎零开发成本</b>", "1 d", "9 月随版本"),
]

# ---- 9/10 月外显投放（用户 2026-07-30 给定）----
ART9 = [
    ("主城皮肤", "周年皮肤（P2 海盗船）", "P2 搬运", "W1 内外圈抽奖大奖", "#5ad1ff"),
    ("英雄皮肤", "周年英雄皮肤（<b>限定</b>）", "新做", "W2 挖孔", "#4ade80"),
    ("英雄皮肤", "周年英雄皮肤（<b>史诗</b>）", "新做", "W2 挖孔 · <b>$49.99 钩子档</b>（前 50 刀阶段奖励）", "#4ade80"),
    ("海妖皮肤", "新海妖皮肤", "新做（新系统）", "W3 弹珠", "#c084fc"),
    ("航行特效", "周年行军特效（P2 周年庆）", "P2 搬运", "W3 弹珠", "#c084fc"),
    ("航行特效", "X3-1 周年行军装扮<b>返场</b>", "返场", "W3 开箱（返场批次）", "#fbbf24"),
]
ART10 = [
    ("主城皮肤", "万圣节皮肤（P2 万圣节）", "P2 搬运", "内外圈 / 榜奖", "#5ad1ff"),
    ("英雄皮肤", "万圣节英雄皮肤", "新做", "开箱大奖", "#4ade80"),
    ("英雄皮肤", "<b>红色英雄皮肤 · 带互动系统</b>", "新做 · <b>新品质顶档</b>", "史诗静态走量 / 红色带互动收鲸", "#f87171"),
    ("主城皮肤", "<b>主城皮肤套装</b>", "系统 + 内容", "套装系统首期（12 月出 2 期）", "#5ad1ff"),
]

OWN = {"力": "zhangli（程序）", "我": "linkang（配置/美术）"}
OWC = {"力": "#c084fc", "我": "#5ad1ff"}
OWS = {"力": "zhangli", "我": "linkang"}
OWB = lambda o: (f"<span style='color:{OWC[o]};border:1px solid {OWC[o]}55;"
                 f"background:{OWC[o]}14;border-radius:3px;padding:1px 6px;font-size:10px;white-space:nowrap'>{OWS[o]}</span>"
                 if o else "<span style='color:#3a4653'>—</span>")

# ---- 月卡 HTML（三层：预期开发 → 外显规划 → 核心付费点）----
# 在模板外先拼好，避免 f-string 多层嵌套引号打架
_mc = []
for M in MONTHS:
    dev_sum = sum(r[1] for r in M["dev"])
    gap = dev_sum - M["cap"]
    _has_owner = any(len(r) == 3 and r[2] for r in M["dev"])
    gap_html = ('<span style="color:var(--dim2)">分两条线 ↓</span>' if _has_owner
                else (f'<span style="color:var(--bad)">超 {gap}d</span>' if gap > 0
                      else f'<span style="color:var(--ok)">余 {-gap}d</span>'))
    _dv = [(r if len(r) == 3 else (*r, "")) for r in M["dev"]]
    dev_rows = "".join(f'<tr><td>{n}</td>'
                       f'<td style="text-align:center">{OWB(o)}</td>'
                       f'<td class="n">{d}</td></tr>' for n, d, o in _dv)
    _by = {}
    for n, d, o in _dv:
        if o: _by[o] = _by.get(o, 0) + d
    split_rows = "".join(
        f'<tr class="sp"><td style="color:var(--dim2)">└ {OWN[o]} 这条线</td><td></td>'
        f'<td class="n">{v}/{M["cap"]} '
        + (f'<span style="color:var(--bad)">超 {v-M["cap"]}d</span>' if v > M["cap"]
           else f'<span style="color:var(--ok)">余 {M["cap"]-v}d</span>') + '</td></tr>'
        for o, v in _by.items())
    art_rows = ""
    for k, new, cat, item, src, use in M["art"]:
        cls = ' class="star"' if k else ''
        star = f'<span style="color:{M["c"]}">★</span>' if k else ''
        # new=1 ⇒ 本次新做的外显类型/品质档（此前 X3 没有这个类型）→ 载体标红 + 「新」角标
        cat_html = (f'<span style="color:var(--bad);font-weight:700">{cat}</span>'
                    f'<span class="nw">新</span>' if new
                    else f'<span style="color:var(--dim2)">{cat}</span>')
        art_rows += (f'<tr{cls}><td style="text-align:center">{star}</td>'
                     f'<td>{cat_html}</td><td><b>{item}</b></td>'
                     f'<td style="font-size:11.5px">{src}</td>'
                     f'<td style="color:var(--dim);font-size:11.5px">{use}</td></tr>')
    wk_rows = "".join(f'<div class="row"><div class="w">{w}</div><div class="mod">{m}</div>'
                      f'<div class="dsc">{d}</div></div>' for w, m, d in M["weeks"])
    _mc.append(f'''<div class="mo">
<div class="hd"><span class="m" style="color:{M["c"]}">{M["mo"]}</span><span class="th">{M["theme"]}</span>
<span class="act" style="color:{M["c"]}">{M["act"]}</span>
<span class="kpi">{M["kn"]}<b>{M["kv"]}</b></span></div>
<div class="sec"><div class="st">预期开发内容</div>
<table class="tin"><tr><th>项目</th><th style="width:72px;text-align:center">归属</th><th class="n" style="width:78px">人天</th></tr>
{dev_rows}
<tr class="sum"><td><b>合计</b></td><td></td><td class="n"><b>{dev_sum}</b>{"" if _has_owner else "/" + str(M["cap"])} {gap_html}</td></tr>
{split_rows}</table></div>
<div class="sec"><div class="st">外显规划　<span class="hint2">★＝核心付费点　·　<span style="color:var(--bad)">红色载体＋「新」＝本次新做（此前 X3 无此类型/品质档）</span></span></div>
<table class="tin"><tr><th style="width:22px"></th><th style="width:118px">载体</th><th>投放物</th>
<th style="width:158px">来源</th><th>作用</th></tr>
{art_rows}</table></div>
<div class="sec"><div class="st">核心付费点　<span class="hint2"><span style="color:#f87171">红＝新做</span> · <span style="color:var(--dim2)">灰＝复用</span></span></div>{wk_rows}</div>
<div class="why"><b>为什么这么排：</b>{M["why"]}</div></div>''')
# 9 月单独一段；10–12 月一段。中间插「一张图看两个动作」——它解释的正是 10 月要抬的两个因子
MONTH_HTML_9 = _mc[0]
MONTH_HTML_REST = "\n".join(_mc[1:])

# ---- 外显类型 × 月份 投放矩阵（■已定 / ○建议 / △待定 / — 无）----
# cell = (标记, 文案)；标记决定底色
MATRIX = [
    ("普通主城皮肤", "🔴 3D · 现有 20 款", [
        ("■", "二周年限定 · <b>普通档</b><br>（P2 海盗船 · 搬运）<br><span style='color:#8fa3b8'>内外圈<b>外圈</b>＝随机走量</span>"),
        ("—", ""),
        ("—", ""),
        ("■", "<b>普通圣诞皮 · 直售</b><br><span style='color:#8fa3b8'>不走抽奖的确定性入口</span>")], 0),
    ("高级主城皮肤", "🔴 3D · <b>新增品质档</b>", [
        ("■", "二周年限定 · <b>高级档</b><br>（P2 海盗船 · 搬运）<br><span style='color:#8fa3b8'>内外圈<b>内圈</b>＝固定收鲸</span>"),
        ("—", ""),
        ("■", "<b>钓鱼主城皮肤</b><br>（钓鱼的大奖载体）<br><span style='color:#fbbf24'>档位待确认</span>"),
        ("—", "")], 1),
    ("主城皮肤套装", "🔴 3D · <b>新系统</b>", [
        ("—", ""),
        ("■", "<b>套装系统首期</b><br><span style='color:#f87171'>万圣不出独立主城皮肤</span><br><span style='color:#8fa3b8'>「买一件」→「集一套」</span>"),
        ("—", ""),
        ("■", "<b>套装 2 期</b><br><span style='color:#8fa3b8'>系统已摊完 · 只出美术+配置</span>")], 1),
    ("英雄皮肤", "🔴 视频/Spine", [
        ("■", "周年限定<br>＋周年<b>史诗（$49.99 钩子）</b>"),
        ("■", "万圣节英雄皮肤<br>＋<b>红色新品质档</b>"),
        ("■", "<b>黑五英雄皮肤</b><br>（限定 + 史诗双档）"),
        ("■", "<b>圣诞英雄皮肤</b><br>（限定 + 史诗双档）")]),
    ("海妖皮肤", "🔴 <b>新系统</b> · 9 月建成", [
        ("■", "<b>新海妖皮肤</b><br>（挂 W3 弹珠）"), ("—", ""),
        ("■", "<b>第二期</b><br>（系统复用，纯内容）"),
        ("■", "<b>圣诞海妖皮肤</b><br>（系统第三次复用）")], 1),
    ("航行特效（航迹）", "🟡 特效", [
        ("■", "周年行军特效（P2 搬运）<br>＋<b>X3-1 周年装扮返场</b>"),
        ("○", "成熟位，建议带一款"), ("○", "建议带一款"),
        ("■", "<b>圣诞行军特效</b>")]),
    ("主城特效", "🟡 特效 · <b>新类型</b>", [
        ("—", ""), ("—", ""),
        ("■", "<b>新增主城特效</b><br><span style='color:#8fa3b8'>X3 此前无此位</span>"),
        ("○", "圣诞款（建议）")], 1),
    ("船只装扮", "已有系统", [
        ("○", "与航迹成套投放"), ("○", "同左"), ("○", "同左"), ("○", "同左")]),
    ("纪念卡", "🟢 2D", [
        ("■", "9 月已迭代<br>＝拆分投放定位"), ("—", ""), ("—", ""), ("○", "圣诞款（建议）")]),
    ("卡册（节日版）", "🟢 2D · <b>新增收集线</b>", [
        ("—", ""), ("■", "<b>新增节日卡册</b>"), ("—", ""), ("—", "")], 1),
    ("门头三件套", "🟡 3D", [
        ("○", "周年可出一套<br>（横梁/墙纸/地板）"), ("—", ""), ("—", ""), ("○", "圣诞款（建议）")]),
    ("装饰（单个）", "🟡 3D", [
        ("—", ""), ("■", "<b>升级系统</b><br>给已售出装饰开续费口"), ("—", ""), ("—", "")]),
    ("家具皮肤", "🟡 3D", [
        ("—", ""), ("○", "青铜/白银/黄金三档<br>可作分品质样板"), ("—", ""), ("—", "")]),
    ("头衔", "🟢 2D", [("○", "低成本随节日带"), ("○", "同左"), ("○", "同左"), ("○", "同左")]),
    ("头像框", "🟢 2D", [
        ("⚠", "<b>零成交 → 先止损</b><br>停单独铺"), ("○", "并进套装卖"), ("—", ""), ("—", "")]),
    ("头像", "🟢 2D", [
        ("—", ""), ("○", "<b>建议补</b><br>（15 款 vs 框 96 款）"), ("—", ""), ("○", "建议补")]),
    ("聊天表情", "🟢 2D", [("○", "低成本随节日带"), ("○", "同左"), ("○", "同左"), ("○", "同左")]),
]
# 第 4 位＝new 标记（1＝本次新做的外显类型/品质档）；只写了 3 位的行补 0
MATRIX = [r if len(r) == 4 else (*r, 0) for r in MATRIX]
MO_N = ["9 月", "10 月", "11 月", "12 月"]
MO_T = ["周年", "万圣", "黑五", "圣诞"]
MO_C = ["#4ade80", "#5ad1ff", "#fbbf24", "#c084fc"]
MK = {"■": ("#4ade80", "已定"), "○": ("#5ad1ff", "建议"), "△": ("#fbbf24", "待定"),
      "⚠": ("#f87171", "止损"), "—": ("#3a4653", "无")}


# ---- 9–10 月工作流：分工 / 负载 / 排期倒推 ----
# 每条线按顺序串行排；单人满负荷 5d/周
GANTT = [
 ("9 月 · 周年", 20, {
   "力": [("挖孔 v1", 10, "P2 最强单品·预留返工"), ("海妖皮肤系统", 5, "新建"), ("弹珠", 5, "")],
   "我": [("美术资源进包", 5, "★ 别人的前置输入"), ("周年行军特效搬运对接", 3, ""),
          ("挖孔数值与奖池配置", 3, "★跟挖孔双单"), ("海妖数据与投放配置", 1, ""),
          ("开箱 · 周年宝箱版", 3, "独立单"), ("复用活动包装及配置", 6, "约 16 个换皮")]}),
 ("10 月 · 万圣", 20, {
   "力": [("主城套装系统功能", 7, "新系统·12 月复用"), ("装饰物升级系统", 3, ""),
          ("团购礼包", 3, "P2 搬运"), ("复用活动包装及配置", 4, "")],
   "我": [("主城套装美术资源沟通", 3, "★ 套装系统的前置"), ("红色英雄皮肤+互动", 5, "feature/skin-moment"),
          ("卡册／联盟总动员 二选一", 5, "两者择一，不叠加"), ("预购连锁礼包", 3, "P2 搬运")]}),
]
BUF = ("<div style='position:absolute;left:80%;right:0;top:0;bottom:0;"
       "background:repeating-linear-gradient(45deg,rgba(248,113,113,.07) 0 6px,transparent 6px 12px);"
       "border-left:2px dashed #f8717188' title='改 BUG 保留 4d'></div>")
_gt = []
for gname, span, lanes in GANTT:
    _lines = ""
    for who, tasks in lanes.items():
        c = OWC[who]; x = 0.0; bars = ""
        for k, (tn, td, note) in enumerate(tasks):
            w = td / span * 100
            op = 0.30 if k % 2 == 0 else 0.18
            bars += (f"<div class='bar' style='left:{x:.1f}%;width:{w-0.5:.1f}%;"
                     f"background:rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},{op});"
                     f"border:1px solid {c}66;color:{c}' title='{tn} · {td}d {note}'>{tn} <span style='opacity:.7'>{td}d</span></div>")
            x += w
        used = sum(t[1] for t in tasks)
        _lines += (f"<div class='ln'><div class='who' style='color:{c}'>{OWN[who]}"
                   f"<div style='font-weight:400;font-size:10.5px;color:var(--dim2)'>{used}d / {span}d 档期</div></div>"
                   f"<div class='tr'>{BUF}{bars}</div></div>")
    weeks = "".join(f"<span>第 {i+1} 周</span>" for i in range(span // 5))
    _gt.append(f"<div class='gt'><div style='font-size:12.5px;font-weight:700;margin-bottom:9px'>{gname} · 开发排期倒推"
               f"<span style='font-weight:400;color:var(--dim2);font-size:11px'>（横轴＝上线前第几周；<span style='color:var(--bad)'>右侧斜纹＝改 BUG 保留 4d，块压进去或越界＝超载</span>）</span></div>"
               f"<div class='ax' >{weeks}</div>{_lines}"
               f"<div class='lg'>档期 {span}d ＝ <b>可开发 16d</b> + <b style='color:var(--bad)'>改 BUG 4d</b>。"
               f"关键路径＝较长那条线 <b>{max(sum(t[1] for t in v) for v in lanes.values())}d</b>"
               f"{f' ⇒ <b style=&quot;color:var(--bad)&quot;>越过 16d 线 {max(sum(t[1] for t in v) for v in lanes.values())-16}d，会吃掉改 BUG 的时间</b>' if max(sum(t[1] for t in v) for v in lanes.values())>16 else ' ⇒ 装得下'}。</div></div>")
GANTT_HTML = chr(10).join(_gt)

# 负载条（按人 × 月）
_ld = []
for gname, span, lanes in GANTT:
    for who, tasks in lanes.items():
        used = sum(t[1] for t in tasks); c = OWC[who]
        over = used > 16
        _ld.append(f"<div class='ld'><div class='nm' style='color:{c}'>{gname[:4]}　{OWN[who][:2]}</div>"
                   f"<div class='br'><div class='fl' style='width:{min(used/25*100,100):.0f}%;background:{c}'></div>"
                   f"<div class='rl' style='left:64%' title='可开发 16d（20d 档期 − 4d 改 BUG）'></div></div>"
                   f"<div style='width:118px;text-align:right;font-size:11.5px'>"
                   f"<b style='color:{'var(--bad)' if over else 'var(--ok)'}'>{used}d</b>"
                   f"<span style='color:var(--dim2)'> / 16d 可开发　{'超 '+str(used-16)+'d' if over else '余 '+str(16-used)+'d'}</span></div></div>")
LOAD_HTML = chr(10).join(_ld)


# ---- 工单清单（开发 / 配置 / 美术；有分工的拆双单）----
# 行 = (类型, 单名, 归属, 人天, 依赖/备注)   类型: 程 / 配 / 美
TK_C = {"程": "#c084fc", "配": "#5ad1ff", "美": "#fbbf24"}
TK_N = {"程": "程序", "配": "策划配置", "美": "美术"}
WY_C = {"AI": "#4ade80", "人工": "#fbbf24", "": "#3a4653"}
# 行 = (类型, 单名, 归属, 人天, 处理方式, 依赖/备注)
TICKETS = [
 ("9 月 · 周年", [
  ("程", "挖孔 v1 · <b>功能开发</b>", "zhangli", "10d", "", "P2 搬运；<b style='color:#f87171'>明确还得改，10d 含返工待确认</b>"),
  ("配", "挖孔 v1 · <b>数值与奖池配置</b>", "linkang", "3d", "", "★与上单是<b>同一功能的两个单</b>，一起验收"),
  ("程", "海妖皮肤系统 · <b>功能开发</b>", "zhangli", "5d", "", "新建系统，11/12 月复用两次"),
  ("配", "海妖皮肤系统 · <b>皮肤数据与投放配置</b>", "linkang", "1d", "", "★同上，双单"),
  ("程", "弹珠 · 开发", "zhangli", "5d", "", "<b style='color:#fbbf24'>缺口解法＝这单推到 11 月</b>"),
  ("配", "开箱活动 · 周年限定宝箱版本", "linkang", "3d", "", "独立单（用户明确）"),
  ("配", "周年行军特效搬运对接", "linkang", "3d", "", "FxID 绑定 + DK 注册"),
  ("配", "复用活动包装及配置", "linkang", "6d", "", "约 16 个沿用活动换皮"),
  ("配", "全部内容的<b>美术资源进包</b>", "linkang", "5d", "", "规格 / 材质 / DK 三关；<b>是zhangli系统线的前置</b>"),
  ("美", "主城皮肤 · 二周年<b>普通档</b>", "linkang", "—", "AI", "P2 海盗船搬运 ⇒ 3D 模型+贴图进包"),
  ("美", "主城皮肤 · 二周年<b>高级档</b>", "linkang", "—", "人工", "同源但<b>要做出档位区分度</b>（$19.99 vs $99.99）"),
  ("美", "英雄皮肤 · 周年<b>史诗</b>", "linkang", "—", "AI", "静态为主（立绘+图标），对应 $49.99 钩子"),
  ("美", "英雄皮肤 · 周年<b>限定</b>", "linkang", "—", "AI", "顶奖 ⇒ 走 AI 视频化链路"),
  ("美", "海妖皮肤 · 新款", "linkang", "—", "AI", "新系统首款，<b>规格由此单定基线</b>（后续两期照抄）"),
  ("美", "行军特效 · 周年款", "linkang", "—", "人工", "P2 周年庆搬运 ⇒ 特效资源迁移"),
  ("美", "门头三件套 · 周年款（建议）", "linkang", "—", "人工", "横梁/墙纸/地板 <b>三件一起出</b>，缺一不成套"),
  ("美", "头衔 / 聊天表情 · 周年款", "linkang", "—", "AI", "2D 轻量，填投放日历最便宜的料"),
  ("美", "活动包装 · 挖孔", "linkang", "—", "AI", "背景 + 玩法 UI 逐部件 + HUD icon"),
  ("美", "活动包装 · 弹珠", "linkang", "—", "AI", "同上"),
  ("美", "活动包装 · 开箱（周年宝箱版）", "linkang", "—", "AI", "同上 + 宝箱本体"),
  ("美", "活动包装 · 内外圈（换主题）", "linkang", "—", "AI", "8 月首投已有骨架，只换主题元素"),
  ("美", "礼包 banner / 头图批次", "linkang", "—", "AI", "按档位数量出，预留文案+价格位"),
  ("美", "道具图标批次", "linkang", "—", "AI", "新增货币 / 门票 / 碎片"),
 ]),
 ("10 月 · 万圣", [
  ("程", "主城皮肤套装 · <b>系统功能开发</b>", "zhangli", "7d", "", "新系统，12 月出 2 期复用"),
  ("程", "装饰物升级系统", "zhangli", "3d", "", "给已售出 146 款装饰开续费口"),
  ("程", "团购礼包（P2 搬运）", "zhangli", "3d", "", "宽入口·4,941 买家"),
  ("配", "复用活动包装及配置", "zhangli", "4d", "", "克隆脚本可复用"),
  ("配", "红色英雄皮肤 + 互动系统", "linkang", "5d", "", "走 feature/skin-moment"),
  ("配", "节日卡册 <span style='color:var(--dim2)'>或</span> 联盟总动员节日版", "linkang", "5d", "", "<b style='color:#fbbf24'>二选一，不叠加</b>"),
  ("配", "预购连锁礼包（P2 搬运）", "linkang", "3d", "", "收鲸·人均 $167.7"),
  ("配", "主城套装 · 美术资源搬运沟通", "linkang", "3d", "", "<b>是套装系统的前置</b>"),
  ("美", "主城皮肤套装 · 首期", "linkang", "—", "人工", "<b style='color:#f87171'>件数未定 ⇒ 开单前先定几件成一套</b>，直接决定工作量"),
  ("美", "英雄皮肤 · <b>红色（带互动）</b>", "linkang", "—", "人工", "新品质顶档，<b>含互动动画</b>，不是静态"),
  ("美", "英雄皮肤 · 万圣节", "linkang", "—", "AI", "开箱大奖"),
  ("美", "节日卡册 · 卡面批次", "linkang", "—", "AI", "按坑数出；<b>选联盟总动员则此单不开</b>"),
  ("美", "头像补位（建议）", "linkang", "—", "AI", "15 款 vs 头像框 96 款，明显缺口"),
  ("美", "活动包装 · 万圣三活动换皮", "linkang", "—", "AI", "挖孔 / 开箱 / 内外圈各一套"),
 ]),
]
import re as _re
_strip = lambda x: _re.sub(r"<[^>]+>", "", x).replace("★", "").strip()
_tk = []; _copy = {}
for gi, (gname, rows) in enumerate(TICKETS):
    n_p = sum(1 for r in rows if r[0] == "程"); n_c = sum(1 for r in rows if r[0] == "配")
    n_a = sum(1 for r in rows if r[0] == "美")
    n_ai = sum(1 for r in rows if r[4] == "AI"); n_mn = sum(1 for r in rows if r[4] == "人工")
    trs = ""
    for t, nm, ow, md, wy, dep in rows:
        pre = (f"<span style=\"color:{WY_C[wy]};font-weight:700\">[{wy}]</span> " if wy else "")
        trs += (f"<tr><td style='text-align:center'><span style=\"color:{TK_C[t]};border:1px solid {TK_C[t]}55;"
                f"background:{TK_C[t]}14;border-radius:3px;padding:1px 6px;font-size:10.5px;white-space:nowrap\">{TK_N[t]}</span></td>"
                f"<td>{pre}{nm}</td><td style='text-align:center;font-size:11.5px'>{ow}</td>"
                f"<td class='n' style='font-size:11.5px'>{md}</td>"
                f"<td style='color:var(--dim);font-size:11.5px'>{dep}</td></tr>")
    key = f"g{gi}"
    _nmx = lambda nm, wy: (f"[{wy}] " if wy else "") + _strip(nm)
    _copy[key] = ("类型	单名	归属	人天	依赖备注" + chr(10)
                  + chr(10).join("	".join([TK_N[t], _nmx(nm, wy), ow, _strip(md), _strip(dep)])
                                 for t, nm, ow, md, wy, dep in rows))
    _copy[key + "a"] = ("单名	备注" + chr(10)
                        + chr(10).join("	".join([_nmx(nm, wy), _strip(dep)])
                                       for t, nm, ow, md, wy, dep in rows if t == "美"))
    _tk.append(f"<h3>{gname} · 共 <b>{len(rows)}</b> 单"
               f"<span style='font-size:12px;font-weight:400;color:var(--dim2)'>"
               f"（程序 {n_p} · 配置 {n_c} · 美术 {n_a}　美术里 "
               f"<b style='color:#4ade80'>AI {n_ai}</b> / <b style='color:#fbbf24'>人工 {n_mn}</b>）</span>"
               f"<button class='cp' data-k='{key}'>⧉ 复制全部</button>"
               f"<button class='cp' data-k='{key}a'>⧉ 只复制美术单</button></h3>"
               f"<table><tr><th style='width:64px'>类型</th><th>单名</th><th style='width:52px'>归属</th>"
               f"<th class='n' style='width:56px'>人天</th>"
               f"<th style='width:38%'>依赖 / 备注</th></tr>{trs}</table>")
TICKET_HTML = chr(10).join(_tk)
import json as _json
COPY_JSON = _json.dumps(_copy, ensure_ascii=False)

# ---- P2 黑五活动全清单 + 抽取建议 ----
BF = [
    ("2023 感恩节黑五小额", 5822, 10.5, 61148, "✅ 必抽", "宽入口天花板：全场最广，人均仅 $10.5，纯配置", "#4ade80"),
    ("25 感恩节每日补给升级礼包", 3868, 12.7, 49083, "✅ 必抽", "第二宽入口，且是「每日」结构＝天天触达", "#4ade80"),
    ("黑五省省卡礼包", 1815, 22.1, 40174, "✅ 必抽", "中额档补 $10→$99 之间的空白", "#4ade80"),
    ("感恩节终极连锁礼包", 947, 174.3, 165060, "✅ 必抽", "收鲸主力：单品 $16.5 万，人均 $174", "#4ade80"),
    ("黑五折扣 2024", 439, 123.6, 54277, "⭕ 可选", "同为收鲸档，与终极连锁重叠，二选一即可", "#fbbf24"),
    ("黑五英雄专属礼包", 888, 44.5, 39544, "⭕ 可选", "定向英雄，需绑当期英雄；X3 可绑周年/万圣皮肤英雄", "#fbbf24"),
    ("2023 感恩节黑五大额", 596, 99.3, 59189, "⭕ 可选", "$99 档，与终极连锁价位接近", "#fbbf24"),
    ("2024 感恩节随机 GACHA", 1277, 119.1, 152055, "❌ 不抽", "X3 已有内外墙 + 开箱两套抽奖，再加会互相蚕食", "#f87171"),
    ("2023 / 2024 感恩节 GACHA", 1685, 77.1, 129932, "❌ 不抽", "同上，抽奖位已满", "#f87171"),
    ("2024 感恩节 BP 礼包", 1792, 25.8, 46172, "❌ 不抽", "X3 已有双 BP；结论早已明确「别再堆 BP」", "#f87171"),
]

# ---- 9/10 月反馈与验收节奏 ----
FB = [
    ("9 月末", "① <b>节日收入月占比是否到 20–25%</b>（本月唯一主考核）<br>"
     "② 节日期是否<b>满 21 天且中间无空档</b>（逐日付费率不掉到 10% 以下）<br>③ 三个 W 的主力模块是否<b>各达周占比 15%</b>",
     "现成脚本：`x3_cumulative_monitor.py`（每日 09:10 自动跑）+ 本页生成器重跑",
     "任一项未达 → 记入 11 月结账清单"),
    ("10 月末", "① <b>付费玩家付费率是否到 40%+</b>（活跃日中位，从 32.1% 起）<br>"
     "② <b>节日日均 ARPPU 是否到 $30.5+</b>（从 $25.3 起）<br>"
     "③ 方向 5 单独看：<b>宽入口带来的新增买家数</b>（对标 P2 黑五小额 5,822 人的量级感）",
     "同上 + `x3_l1_metrics.py`（模块级付费率/ARPU/ARPPU/复购）",
     "<b>两个因子哪个没达就补哪个</b>：付费率没达 → 11 月黑五小额宽入口；深度没达 → 黑五大额/折扣档"),
    ("11 月末", "黑五双轨是否两头都成：<b>小额买家数</b>（对标 P2 5,822 的量级感）＋ <b>大额人均</b>",
     "同上", "作为 12 月冲量前的最后一次校准"),
]

DEV = [(M["mo"], [(r[0], r[1]) for r in M["dev"]], M["cap"]) for M in MONTHS]

ASK = [
    ("11 月主题确认为<b>黑五</b>（原按感恩节占位）", "已按你的标注改；感恩节与黑五在 P2 是同一批礼包（感恩节黑五小额/大额）"),
    ("9 月节日期<b>拉到 21 天</b>是硬目标还是弹性目标", "建议硬目标——它是 40% 的前置条件，且零开发成本"),
    ("对外承诺的占比口径与数值", "建议讲「半年到 35%」，40–50% 作为上限空间；口径统一用成熟服 1000–1870"),
]

html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3 9–12 月规划 · 核心版</title><style>
:root{{--bg:#0d1117;--panel:#141b24;--panel2:#1a232e;--line:#243040;--fg:#e8f0f8;
--dim:#8fa3b8;--dim2:#6b7f95;--acc:#5ad1ff;--ok:#4ade80;--warn:#fbbf24;--bad:#f87171;--new:#c084fc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);line-height:1.7;
font-family:"Microsoft YaHei","PingFang SC",sans-serif;font-size:14px}}
main{{max-width:1060px;margin:0 auto;padding:36px 30px 80px}}
h1{{margin:0;font-size:28px;letter-spacing:.01em}}
.sub{{color:var(--warn);font-size:17px;font-weight:700;margin:7px 0 10px}}
.meta{{color:var(--dim2);font-size:12.5px;border-bottom:1px solid var(--line);padding-bottom:16px}}
.meta b{{color:var(--acc)}}
.v{{background:linear-gradient(180deg,#16202b,#131a23);border:1px solid var(--line);
border-left:3px solid var(--warn);border-radius:6px;padding:16px 20px;margin:22px 0}}
.v .t{{font-size:10.5px;letter-spacing:.22em;color:var(--warn);font-weight:700}}
.v p{{margin:9px 0 0}}.v b{{color:#fff}}
h2{{font-size:19px;margin:42px 0 6px}}
h2 .no{{display:inline-block;background:var(--acc);color:#06202b;font-size:12px;font-weight:700;
border-radius:4px;padding:1px 9px;margin-right:9px;vertical-align:2px}}
h2+.lead{{color:var(--dim);margin:0 0 14px;font-size:13px}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:12.5px;background:var(--panel)}}
th,td{{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}}
th{{background:var(--panel2);color:var(--dim);font-size:11.5px;white-space:nowrap}}
td.n{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.note{{background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--dim2);
border-radius:5px;padding:11px 15px;font-size:12.5px;color:var(--dim);margin:14px 0}}
.note b{{color:var(--fg)}}.note.ok{{border-left-color:var(--ok)}}.note.bad{{border-left-color:var(--bad)}}
.note.warn{{border-left-color:var(--warn)}}
svg{{background:var(--panel);border:1px solid var(--line);border-radius:6px;margin-top:8px}}
.tabs{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0 0}}
.tabs button{{background:transparent;color:var(--dim);border:1px solid var(--line);border-radius:4px;
padding:5px 14px;font-size:12.5px;cursor:pointer;font-family:inherit;transition:.15s}}
.tabs button.on{{background:var(--acc);border-color:var(--acc);color:#06202b;font-weight:700}}
.lg{{display:flex;gap:14px;flex-wrap:wrap;font-size:11.5px;color:var(--dim);margin:9px 0}}
.lg i{{display:inline-block;width:11px;height:3px;margin-right:5px;vertical-align:3px}}
/* 月卡 */
.mo{{border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:16px 0;background:var(--panel)}}
.mo .hd{{display:flex;align-items:baseline;gap:12px;padding:12px 18px;border-bottom:1px solid var(--line);
flex-wrap:wrap}}
.mo .m{{font-size:21px;font-weight:700}}
.mo .th{{font-size:13px;color:var(--dim)}}
.mo .act{{font-size:15px;font-weight:700}}
.mo .kpi{{margin-left:auto;font-size:12px;color:var(--dim);text-align:right}}
.mo .kpi b{{display:block;font-size:16px;color:var(--warn)}}
.mo .bd{{padding:6px 18px 14px}}
.mo .row{{display:flex;gap:12px;padding:7px 0;border-bottom:1px dashed rgba(143,163,184,.14);font-size:12.5px}}
.mo .row:last-child{{border-bottom:0}}
.mo .w{{width:96px;flex:none;color:var(--dim2);font-size:11.5px;padding-top:1px}}
.mo .mod{{width:210px;flex:none;font-weight:700}}
.rz{{font-size:10px;font-weight:400;border-radius:3px;padding:0 5px;margin-left:6px;white-space:nowrap}}
.rz-new{{color:#f87171;border:1px solid #f8717155;background:rgba(248,113,113,.10)}}
.rz-old{{color:var(--dim2);border:1px solid var(--line);background:rgba(143,163,184,.06)}}
.nc{{color:#f87171}}
.oc{{color:var(--dim2)}}
.mo .dsc{{flex:1;color:var(--dim)}}
.mo .why{{margin:8px 18px 14px;padding:9px 13px;background:var(--panel2);border-radius:5px;
font-size:12px;color:var(--dim2);border-left:2px solid var(--line)}}
.mo .why b{{color:var(--dim)}}
.mo .sec{{padding:9px 18px 2px;border-top:1px solid rgba(36,48,64,.75)}}
.mo .st{{font-size:11px;letter-spacing:.16em;color:var(--dim2);font-weight:700;margin-bottom:4px}}
.mo .hint2{{letter-spacing:0;font-weight:400;color:var(--dim2)}}
.cp{{margin-left:8px;font:inherit;font-size:11px;font-weight:400;cursor:pointer;
  background:var(--panel2);color:var(--acc);border:1px solid var(--line);border-radius:4px;padding:3px 9px}}
.cp:hover{{border-color:var(--acc);background:rgba(90,209,255,.10)}}
.cp.ok{{color:var(--ok);border-color:var(--ok)}}
.gt{{border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:14px 16px;margin:14px 0}}
.gt .ax{{display:flex;margin-left:104px;border-bottom:1px solid var(--line);padding-bottom:5px;margin-bottom:10px}}
.gt .ax span{{flex:1;font-size:11px;color:var(--dim2);text-align:center}}
.gt .ln{{display:flex;align-items:center;margin:9px 0}}
.gt .who{{width:104px;flex:none;font-size:12px;font-weight:700}}
.gt .tr{{flex:1;position:relative;height:30px;background:linear-gradient(90deg,var(--line) 1px,transparent 1px) 0 0/20% 100%}}
.gt .bar{{position:absolute;top:2px;height:26px;border-radius:4px;font-size:11px;line-height:26px;
  padding:0 8px;white-space:nowrap;overflow:hidden;font-weight:600}}
.gt .lg{{font-size:11px;color:var(--dim2);margin-top:12px;padding-top:9px;border-top:1px solid var(--line)}}
.ld{{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:12px}}
.ld .nm{{width:132px;flex:none}}
.ld .br{{flex:1;height:19px;background:var(--panel2);border-radius:3px;position:relative;overflow:visible}}
.ld .fl{{height:100%;border-radius:3px}}
.ld .rl{{position:absolute;top:-3px;bottom:-3px;width:2px;background:var(--bad)}}
.tin tr.sp td{{background:transparent;font-size:11.5px;padding-top:2px;padding-bottom:2px;border-top:0}}
.mxwrap{{overflow-x:auto;border:1px solid var(--line);border-radius:8px;margin:14px 0}}
.mxT{{margin:0!important;border:0!important;min-width:2560px;table-layout:fixed}}
.mxT th{{width:148px;vertical-align:bottom;font-size:12px;line-height:1.35}}
.mxT td{{width:148px;vertical-align:top;font-size:11.5px;line-height:1.45}}
.mxT .mhd{{position:sticky;left:0;z-index:2;width:96px;min-width:96px;background:var(--panel2);box-shadow:2px 0 6px rgba(0,0,0,.35)}}
.mxT .wt{{color:var(--dim2);font-size:10.5px;font-weight:400;margin-top:3px}}
.nw{{display:inline-block;margin-left:4px;padding:0 4px;border-radius:3px;font-size:9.5px;
font-weight:700;color:#1a232e;background:var(--bad);vertical-align:1px;letter-spacing:.04em}}
table.tin{{margin:3px 0 8px;font-size:12px;background:transparent}}
table.tin th{{background:rgba(26,35,46,.55);font-size:11px;padding:4px 8px}}
table.tin td{{padding:4px 8px;border-color:rgba(36,48,64,.75)}}
table.tin tr.sum td{{background:rgba(90,209,255,.05)}}
table.tin tr.star td{{background:rgba(255,255,255,.03)}}
.mo .row{{padding:6px 0}}
.tabbar{{display:flex;gap:6px;flex-wrap:wrap;margin:20px 0 6px;border-bottom:1px solid var(--line);padding-bottom:0}}
.tb{{background:transparent;color:var(--dim);border:1px solid var(--line);border-bottom:none;
border-radius:6px 6px 0 0;padding:8px 16px;font-size:13px;cursor:pointer;font-family:inherit;transition:.15s}}
.tb:hover{{color:var(--fg)}}
.tb.on{{background:var(--panel);color:var(--acc);font-weight:700;border-color:var(--line);
box-shadow:inset 0 2px 0 var(--acc)}}
.pane{{display:none}}.pane.on{{display:block}}
.lead0{{font-size:15px;line-height:1.85;background:var(--panel);border:1px solid var(--line);
border-radius:8px;padding:15px 19px;margin:18px 0 6px}}
.story{{display:grid;gap:14px;margin:16px 0 8px}}
.sc{{margin:14px 0 24px;border:1px solid var(--line);border-left:4px solid;border-radius:0 8px 8px 0;background:var(--panel);padding:13px 18px}}
.sh{{display:flex;align-items:baseline;gap:11px;flex-wrap:wrap}}
.sm{{font-size:21px;font-weight:700}}.sn{{font-size:13px;color:var(--dim)}}
.sg{{margin-left:auto;font-size:12.5px;color:var(--dim)}}.sg b{{font-size:16px;color:var(--warn);margin-left:6px}}
.sb{{font-size:13px;margin-top:7px}}
.se{{font-size:12px;color:var(--dim2);margin-top:6px;padding:8px 12px;background:var(--panel2);
border-radius:5px;border-left:2px solid var(--line)}}
.se b{{color:var(--dim)}}
table.mx td{{font-size:11.5px;line-height:1.5;vertical-align:top}}
table.mx th{{text-align:center}}
table.mx th:first-child,table.mx th:nth-child(2){{text-align:left}}
</style></head><body><main>

<h1>X3 9–12 月规划 · 核心版</h1>
<div class="sub">四个月两个动作：<span style="color:var(--ok)">把线拉长</span>（9 月）→ <span style="color:var(--acc)">把线抬高</span>（10 月）→ 结账（11 月）→ 冲量（12 月）</div>
<div class="meta">口径＝X3 <b>成熟服 1000–1870</b>、P2 全服，均为<b>节日活跃日中位</b>（付费率≥10% 的日子）·
数仓实查 2026-07-30 · 详细论证见同目录《9-10月模块规划_周占比.html》</div>

<div class="v"><div class="t">最核心的三句话</div>
<p>① <b>差距不在玩家钱包</b>：大盘日 ARPU X3 ${DX['arpu']:.1f} vs P2 ${DP['arpu']:.1f}（差 8%）。
差在<b>付费率 {DX['payrate']:.1f}% vs {DP['payrate']:.1f}%</b> 和 <b>ARPPU ${DX['arppu']:.1f} vs ${DP['arppu']:.1f}</b>。</p>
<p>② <b>两步走，考核指标不同</b>：<b>9 月先拉总量</b>——把节日期从 12 天拉到 <b>21 天</b>、每周一个主力模块，只考核<b>节日收入月占比（15% → 20–25%）</b>；
<b>10 月再同步拉付费率与付费深度</b>（含新增的方向 5＝P2 礼包形式搬运）。9 月不拆因子，10 月才拆。</p>
<p>③ <b>40% 是够得着的</b>：只要付费率提到 46.8%（<b>仍低于 P2 的 {DP['payrate']:.1f}%</b>）、ARPPU 一动不动，活跃日占比就到 40%。
但<b>累计</b>占比还要把空窗率从 <b>{DX['gap_ratio']:.0f}%</b> 压到 15% 以内。</p>
</div>

<div class="tabbar">
  <button class="tb on" data-p="p1">四个月怎么走</button>
  <button class="tb" data-p="p2">月度明细</button>
  <button class="tb" data-p="p6">9–10 月工作流</button>
  <button class="tb" data-p="p3">外显投放</button>
  <button class="tb" data-p="p4">弹药与礼包</button>
  <button class="tb" data-p="p7">工单清单</button>
  <button class="tb" data-p="p5">目标 · 产能 · 验收</button>
</div>
<div class="pane on" id="p1">

<div class="lead0">这四个月只做四件事——<b style="color:var(--ok)">9 月把占比拉到 30%</b> →
<b style="color:var(--acc)">10 月把付费率和 ARPU 拉到 P2 水平</b> →
<b style="color:var(--warn)">11 月回归迭代 + 黑五 + 钓鱼，稳中有升</b> →
<b style="color:var(--new)">12 月汇总上半年效果，配合圣诞拉满一次</b>。</div>

<h2><span class="no">9 月</span>目标图 · 节日收入月占比 — 要站上 30%</h2>
<p class="lead">柱＝该月节日收入 ÷ 该月大盘收入。P2 近 12 个月（全服）· X3 成熟服 1000–1870。</p>
{(lambda: (lambda W,H,PL,PB,rows,mx: f'''<svg viewBox="0 0 {W} {H}" width="100%">
{"".join(f'<line x1="{PL}" y1="{H-PB-g/mx*(H-PB-26):.0f}" x2="{W-16}" y2="{H-PB-g/mx*(H-PB-26):.0f}" stroke="#243040"/><text x="{PL-7}" y="{H-PB-g/mx*(H-PB-26)+4:.0f}" font-size="10" fill="#6b7f95" text-anchor="end">{g}%</text>' for g in (0,10,20,30,40,50))}
<line x1="{PL}" y1="{H-PB-P2M_MED/mx*(H-PB-26):.1f}" x2="{W-16}" y2="{H-PB-P2M_MED/mx*(H-PB-26):.1f}" stroke="#c084fc" stroke-dasharray="7 4" stroke-width="1.4"/>
<text x="{W-20}" y="{H-PB-P2M_MED/mx*(H-PB-26)-6:.0f}" font-size="10.5" fill="#c084fc" text-anchor="end">P2 月占比中位 {P2M_MED:.1f}%</text>
<rect x="{PL}" y="{H-PB-25/mx*(H-PB-26):.0f}" width="{W-16-PL}" height="{(25-20)/mx*(H-PB-26):.0f}" fill="#4ade80" fill-opacity=".10"/>
<text x="{PL+6}" y="{H-PB-25/mx*(H-PB-26)-5:.0f}" font-size="10.5" fill="#4ade80">9 月目标带 20–25%</text>
{"".join(f"""<rect x="{PL+8+i*((W-PL-26)/len(rows)):.1f}" y="{H-PB-r['sh']/mx*(H-PB-26):.1f}" width="{(W-PL-26)/len(rows)*0.66:.1f}" height="{r['sh']/mx*(H-PB-26):.1f}" fill="{r['c']}" rx="2"><title>{r['m']} · {r['sh']:.1f}%（节日 ${r['fest']:,.0f} / 大盘 ${r['total']:,.0f}）</title></rect>
<text x="{PL+8+i*((W-PL-26)/len(rows))+(W-PL-26)/len(rows)*0.33:.1f}" y="{H-PB-r['sh']/mx*(H-PB-26)-5:.0f}" font-size="9.5" fill="{r['c']}" text-anchor="middle">{r['sh']:.0f}</text>
<text x="{PL+8+i*((W-PL-26)/len(rows))+(W-PL-26)/len(rows)*0.33:.1f}" y="{H-PB+15}" font-size="9" fill="#6b7f95" text-anchor="middle">{r['m'][2:].replace('-','/')}</text>""" for i, r in enumerate(rows))}
<text x="{W//2}" y="{H-6}" font-size="11" fill="#8fa3b8" text-anchor="middle">月份（左＝P2 近 12 月 · 右＝X3 成熟服）→</text></svg>''')(1000,270,52,42,
  [dict(r, c="#c084fc") for r in P2M] + [dict(r, c="#5ad1ff") for r in X3M], 50))()}
<div class="note"><b>P2 近 12 个月：中位 {P2M_MED:.1f}% · 最低 {P2M_LO:.1f}%（{P2M_LO_M}）· 最高 {P2M_HI:.1f}%（{P2M_HI_M}）</b>　｜
<b>X3：6 月 9.7% → 7 月 19.2%</b>（7 月是两个节日叠加）。<b>9 月要用单个节日站上 30% ——落在 P2 中位与最差月之间。</b></div>


<div class="sc" style="border-left-color:#4ade80">
  <div class="sh"><span class="sm" style="color:#4ade80">9 月</span><span class="sn">周年狂欢</span>
    <span class="sg">节日收入月占比<b>15% → 30%</b></span></div>
  <div class="sb"><b>做法</b>：节日期从 <b>12 天拉到 21 天不断档</b>（D0–D20）＋ 三个 W 各一个主力模块（内外圈 / 挖孔 / 弹珠+开箱堆叠）。</div>
  <div class="se"><b>够到 30% 需要两件事同时成立</b>：节日期 ≥21 天（空窗率降到 30% 以内）<b>且</b>活跃日占比从 27.4% 提到 <b>40%+</b>。
  参照系：X3 7 月已做到 19.2%（但那是世界杯＋深海<b>两个节日叠加</b>）；P2 月占比中位 35.5%、最差月 24.8%
  ——<b>30% 意味着一个节日就要打到 P2 中位附近，是激进目标</b>。</div>
</div>

<h2><span class="no">10 月</span>目标图 · 付费率与 ARPU — 要够到 P2 水平</h2>
<p class="lead">横轴＝节日第 N 天（各节日按自己开场日 D0 对齐），只截节日期。
<span style="color:var(--ok)">绿箭头＝9 月要做的（把线拉长到 D20）</span>；
<span style="color:var(--warn)">切换按钮看 10 月要抬的两个因子</span>。</p>
<div class="tabs">
  <button class="on" data-k="payrate">付费玩家付费率（10 月 KPI 之一）</button>
  <button data-k="arppu">节日日均 ARPPU（10 月 KPI 之二）</button>
</div>
<div class="lg" id="lg"></div>
<div id="ch"></div>
<div class="note bad" id="nt"></div>

<table>
<tr><th>节日期</th><th class="n">天数</th><th class="n">节日收入</th><th class="n">付费率中位</th><th class="n">ARPPU 中位</th></tr>
{"".join(f'''<tr{' style="background:rgba(90,209,255,.06)"' if s["side"]=="X3" else ''}>
<td><b style="color:{s["color"]}">{s["name"]}</b></td><td class="n">{s["n"]}</td>
<td class="n">${s["rev"]:,}</td><td class="n">{s["pr"]}%</td><td class="n">${s["ap"]}</td></tr>''' for s in SEGS)}
</table>
<div class="note"><b>一行对比：</b>P2 拓荒节 <b>23 天做了 $103 万</b>；X3 世界杯+深海两个节日叠一起、拉了 <b>27 天只做了 $4.56 万</b>。
<b>X3 的节日期更长，但付费率只有一半、ARPPU 七成</b>——时间拉长不等于收得多，关键是每周有没有主力模块顶着。</div>




<div class="sc" style="border-left-color:#5ad1ff">
  <div class="sh"><span class="sm" style="color:#5ad1ff">10 月</span><span class="sn">万圣节</span>
    <span class="sg">付费率 ＋ ARPU <b>拉到 P2 水平</b></span></div>
  <div class="sb"><b>做法</b>：四个深度方向（主城套装系统 / 英雄皮肤分品质＋红色新档 / 装饰升级 / 节日卡册）
  ＋ 两个 P2 礼包单子（<b>预购连锁 · 团购</b>）。</div>
  <div class="se"><b>「P2 水平」＝两个具体数</b>：付费玩家付费率 <b>32.1% → 51.5%</b>（1.60×）·
  节日 ARPU <b>$8.8 → $16.1</b>（1.82×）。两者相乘 ⇒ 活跃日占大盘 <b>27.4% → 47.0%</b>。
  而大盘日 ARPU 两边只差 8%（$33.4 vs $36.0）——<b>钱包一样，差的是节日运营</b>。</div>
</div>

<div class="sc" style="border-left-color:#fbbf24">
  <div class="sh"><span class="sm" style="color:#fbbf24">11 月</span><span class="sn">黑五</span>
    <span class="sg">目标<b>稳中有升</b></span></div>
  <div class="sb"><b>做法</b>：① <b>9/10 月内容回归迭代</b>（把两个月跑出来的数据回头修一轮）
  ② <b>黑五内容</b>（小额宽入口 + 大额收鲸双轨）③ <b>钓鱼小游戏</b>（P2 搬运）。
  另含累充改联盟累充、新增主城特效。</div>
  <div class="se"><b>为什么这三件能「稳」</b>：钓鱼周占比中位 <b>12.5%</b>、人均 <b>4.8 单</b>——靠复购稳住而非开场爆发；
  黑五小额单品 <b>5,822 买家 / 人均 $10.5</b>，是补付费率最快且零开发的杠杆；
  而 11 月<b>原本是唯一有回补余量的窗口</b>——但主城特效系统（5d）落进来后，11 月自身也到 <b>27/20</b>，<b>回补预留的 8d 已经被挤占，这点需要一并拍</b>。</div>
</div>

<div class="sc" style="border-left-color:#c084fc">
  <div class="sh"><span class="sm" style="color:#c084fc">12 月</span><span class="sn">圣诞</span>
    <span class="sg"><b>上半年汇总效果 ＋ 拉满一次</b></span></div>
  <div class="sb"><b>做法</b>：形式＝<b>弹珠 + 挖孔（复用只换皮）+ 猜酒杯（新形式）</b>；
  外显五类同月铺开＝套装 2 期 / 普通圣诞皮直售 / 圣诞英雄皮（限定+史诗）/ 圣诞海妖皮 / 圣诞行军特效。</div>
  <div class="se"><b>为什么 12 月能「拉满」</b>：前三个月建成的<b>四件弹药全部就绪可同月轮转</b>，
  系统成本已在 9/10 月摊完 ⇒ <b>12 月开发只需 10 人天，却铺五类外显</b>。
  P2 12 月节日月占比 <b>39.0%</b>（全年最高之一）——年底本身就是付费高点。</div>
</div>

<div class="sc" style="border-left-color:#f87171;background:rgba(248,113,113,.05)">
  <div class="sh"><span class="sm" style="color:#f87171">⚠ 产能红线</span>
    <span class="sn">补齐「海妖系统」与「复用活动配置」后暴露</span>
    <span class="sg">四个月合计<b style="color:#f87171">104 / 80 人天</b></span></div>
  <div class="sb">
  <table class="tin" style="margin:6px 0 8px"><tr><th style="width:66px">月</th><th class="n" style="width:78px">需求/容量</th><th>主要构成</th></tr>
  <tr><td><b>9 月</b></td><td class="n" style="color:#f87171"><b>31/20</b> 超 11d</td>
    <td><b>三个新东西就吃掉 17d</b>：挖孔 7 ＋ 海妖系统 7 ＋ 周年行军特效搬运 3；<br>
    再加弹珠 5 ／ <b>开箱周年限定宝箱版 3</b>（独立单·含 $500 档自选宝箱与返场配置）／ <b>复用活动配置 6</b></td></tr>
  <tr><td><b>10 月</b></td><td class="n" style="color:#f87171"><b>30/20</b> 超 10d</td>
    <td>套装系统 7 ／ 分品质 5 ／ 装饰升级 3 ／ 卡册 5 ／ 预购连锁 3 ／ 团购 3 ／ 复用配置 4</td></tr>
  <tr><td><b>11 月</b></td><td class="n" style="color:var(--warn)"><b>27/20</b> 超 7d</td>
    <td>钓鱼 5 ／ 联盟累充 3 ／ <b>主城特效系统 5</b>（系统+搬运+接入）／ 黑五礼包 2 ／ 复用配置 4 ／ <b>回补预留 8</b></td></tr>
  <tr><td><b>12 月</b></td><td class="n" style="color:var(--ok)"><b>16/20</b> 余 4d</td>
    <td>猜酒杯 5 ／ 套装 2 期 3 ／ 弹珠挖孔换皮 2 ／ 圣诞行军特效 2 ／ 复用配置 4</td></tr>
  </table>
  <b>刚性项（建议不动）</b>：挖孔＝9 月 W2 主力；<b>海妖系统＝9 月 W3 的大奖载体，系统不上则 W3 没外显</b>；
  主城套装系统＝10 月核心且 12 月要复用（系统只摊一次）。</div>
  <div class="se"><b>三个选项，需要拍一个：</b>
  ① <b>加人</b>——9 月需 +11d、10 月 +10d、11 月 +7d；
  ② <b>开发前置</b>——节日期不变，把 9/10 月的系统开发提前到 8 月底/9 月底起做（用 12 月的 4d 余量和 11 月回补预留对冲）；
  ③ <b>砍内容</b>——可砍候选：节日卡册（5d·10 月）、团购礼包（3d·挪 11 月与黑五小额同源）、开箱周年限定宝箱版（3d·但它是 W3 开箱本体，砍了 W3 就没主力）。<br>
  💡<b>另一条能省时间的</b>：复用活动配置首月记 6d、后三月记 4d，是因为<b>马戏节已经沉淀了配置克隆脚本</b>，
  再脚本化一轮有望压到 2–3d/月，四个月共省 4~6d。</div>
</div>

<div class="note ok"><b>两张图连起来看就是这四个月的全部</b>：
图 1 的柱子要从 19.2% 长到 <b>30%</b>（9 月）；图 2 的线要<b>先横向拉长到 D20</b>（9 月）、<b>再纵向抬到 P2 中位线</b>（10 月）；
11 月把两个月的欠账补齐并靠钓鱼稳住；12 月用已建成的四件弹药 + 五类外显<b>拉满一次</b>。</div>

</div>
<div class="pane" id="p2"><h2><span class="no">2·1</span>9 月 · 先把月占比拉起来</h2>
<p class="lead">三层看：<b>预期开发内容</b>（人天）→ <b>外显规划</b>（★＝核心付费点）→ <b>核心付费点</b>（按周）。</p>
{MONTH_HTML_9}

<h2><span class="no">2·2</span>10 – 12 月做什么</h2>
<p class="lead">同样三层看。<b>10 月＝抬高（付费率＋深度双拉）· 11 月＝黑五＋钓鱼＋结账 · 12 月＝复用形式承载五类外显、冲流水。</b></p>
{MONTH_HTML_REST}

<div class="note ok"><b>四件弹药的达标线（P2 同口径实测，周占大盘）</b>——9–12 月建成后 X3 手里就有这四张牌：
<table style="margin:8px 0 0"><tr><th>弹药</th><th class="n">周占比中位</th><th class="n">人均</th><th class="n">人均单数</th><th>特点</th></tr>
<tr><td><b>猜酒杯</b>（12 月）</td><td class="n"><b>16.0%</b></td><td class="n"><b>$162.2</b></td><td class="n"><b>6.2 单</b></td><td>顶档仅 $99.99，<b>靠复购不靠高价</b></td></tr>
<tr><td><b>挖孔</b>（9 月）</td><td class="n">15.9%</td><td class="n">—</td><td class="n">—</td><td>P2 最强单品，渗透 44%</td></tr>
<tr><td><b>钓鱼</b>（11 月）</td><td class="n">12.5%</td><td class="n">$76.0</td><td class="n">4.8 单</td><td>稳定型，靠复购不靠爆发</td></tr>
<tr><td><b>弹珠</b>（9 月 W3）</td><td class="n">9.7%</td><td class="n">—</td><td class="n">—</td><td>带榜 $222k vs 无榜 $167k</td></tr>
</table>
<b>判据＝主力模块单周占大盘 ≥15% 算达标</b>。猜酒杯与挖孔都在这条线上，钓鱼和弹珠是中档补位——
<b>四件轮转就能让每周都有一个够线的模块顶着</b>，这正是 P2 月占比常年 35%+ 的做法。</div>

</div>
<div class="pane" id="p3"><h2><span class="no">3·1</span>外显全景 · 类型 × 月份</h2>
<h3>外显类型 × 月份 · 投放矩阵</h3>
<p class="lead"><b>横向读＝该月要出的全部外显</b>（一行＝一个月的投放清单）；<b>纵向读＝该类型四个月怎么排</b>。表格可左右拖动。
<span style="color:var(--ok)">■ 已定</span> ·
<span style="color:var(--acc)">○ 建议（低成本可带）</span> ·
<span style="color:var(--warn)">△ 待定</span> ·
<span style="color:var(--bad)">⚠ 止损</span><br>
<b style="color:var(--bad)">红色类型名＋「新」＝本次新做</b>（此前 X3 没有这个外显类型/品质档，要连系统或档位一起建）。
主城皮肤已按<b>普通 / 高级 / 套装</b>三类拆开——三者定价位、投放位、开发成本都不同，混成一行会看不出 10 月「不出独立皮只做套装」这个决定。</p>
<div class="mxwrap"><table class="mx mxT">
<tr><th class="mhd">月份</th>
{"".join(f'''<th>{f'<b style="color:var(--bad)">{t}</b><span class="nw">新</span>' if nw else t}
<div class="wt">{wt}</div></th>''' for t, wt, cells, nw in MATRIX)}</tr>
{"".join(f'''<tr><td class="mhd" style="border-left:3px solid {MO_C[i]}"><b style="color:{MO_C[i]}">{MO_N[i]}</b><div class="wt">{MO_T[i]}</div></td>
{"".join((f'<td style="background:{MK[row[2][i][0]][0]}14;border-left:2px solid {MK[row[2][i][0]][0]}55">'
          f'<span style="color:{MK[row[2][i][0]][0]};font-weight:700">{row[2][i][0]}</span> {row[2][i][1]}</td>')
         if row[2][i][1] else '<td style="color:#3a4653;text-align:center">—</td>' for row in MATRIX)}</tr>''' for i in range(4))}
</table></div>
<div class="note"><b>矩阵读出来的三件事</b>：
① <b>四个月外显都不空</b>——原以为 11 月靠价格驱动不用外显，实际 11 月有<b>钓鱼主城皮肤 + 黑五英雄皮双档 + 海妖二期</b>三件核心；
<b>12 月最重（五类同月铺开）</b>，但它的形式全是复用，开发压力反而最小。<br>
② <b>「系统摊一次、内容复用多次」是这半年的主线</b>：海妖皮肤系统 9 月建成 → 11 月二期 → 12 月圣诞款（<b>复用三次</b>）；
主城套装系统 10 月建成 → 12 月 2 期。<b>系统成本只付一次，后面全是纯内容产出。</b><br>
②' <b style="color:var(--bad)">本次要新建的只有四样</b>（红色标记）：<b>高级主城皮肤（新增品质档）· 主城皮肤套装（新系统）· 海妖皮肤（新系统）· 节日卡册（新增收集线）</b>，
外加英雄皮肤的<b>红色新品质顶档</b>。<b>其余全是已有类型出新款或搬运</b>——所以外显这一块的真实新建成本集中在 9/10 月，11/12 月基本是复用。
配置实查佐证：主城皮肤 20 款<b>品质全封顶在 3（紫）</b>，8 月马戏节新皮也是品质3 ⇒ 想要「高级档」必须新开品质位，不是换套美术就行。<br>
③ <b>英雄皮肤四个月都出「限定＋史诗」双档</b>——史诗固定当 $49.99 转化钩子、限定当顶奖，这个结构一旦定死，
后面每月只换美术不改设计。<b>轻量 2D（头衔/表情）四月都能带，是填满投放日历最便宜的料；头像框先止损、头像该补。</b></div>

<h2><span class="no">3·2</span>现有外显投放规划 · 全模块盘点与可挖掘点</h2>
<p class="lead">配置表实查（2026-07-29）。<b>"状态"列＝这个位现在是否在有效投放</b>，右侧＝可挖掘方向。</p>
<table>
<tr><th style="width:110px">载体</th><th class="n">现有</th><th>现状</th><th style="width:62px">状态</th><th>可挖掘 / 处理</th></tr>
{"".join(f'''<tr><td><b>{n}</b><br><span style="color:var(--dim2);font-size:11px">{tb}</span></td>
<td class="n">{cnt if cnt is not None else "—"}</td><td style="color:var(--dim)">{cur}</td>
<td><span class="pill" style="color:{'#f87171' if '空缺' in st or '死货架' in st else ('#fbbf24' if '可挖' in st or '偏弱' in st else '#4ade80')}">{st}</span></td>
<td>{dig}</td></tr>''' for n, tb, cnt, cur, st, dig in CARRIERS)}
</table>

<h3>可挖掘点 → 建议提单</h3>
<table>
<tr><th style="width:180px">提单项</th><th style="width:70px">类型</th><th>依据（都是已实查的数）</th><th class="n">估工</th><th style="width:130px">建议排期</th></tr>
{"".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td style="color:var(--dim)">{c}</td><td class="n">{d}</td><td>{e}</td></tr>' for a, b, c, d, e in DIG)}
</table>

</div>
<div class="pane" id="p4"><h2><span class="no">4·1</span>11 月 · P2 黑五活动清单与抽取建议</h2>
<p class="lead">P2 历年黑五/感恩节礼包实查（同一批礼包命名即「感恩节黑五小额/大额」）。<b>我们抽一部分做，不全抄。</b></p>
<table>
<tr><th>P2 礼包</th><th class="n">买家</th><th class="n">人均</th><th class="n">单品收入</th><th style="width:78px">建议</th><th>理由</th></tr>
{"".join(f'''<tr><td>{n}</td><td class="n"><b>{b:,}</b></td><td class="n">${a}</td><td class="n">${r:,}</td>
<td><span class="pill" style="color:{c};border:1px solid {c}55;background:{c}18">{v}</span></td>
<td style="color:var(--dim)">{why}</td></tr>''' for n, b, a, r, v, why, c in BF)}
</table>
<div class="note ok"><b>抽取原则＝只抽 X3 缺的，不抽已有的</b>：
<b>抽 4 个</b>——小额宽入口（补 X3「没有 $0.99–4.99 入口」这个已知短板）、每日补给（天天触达）、省省卡（中额补空白）、终极连锁（收鲸）；
<b>不抽 3 类</b>——GACHA 类（X3 已有内外墙+开箱两套抽奖，再加互相蚕食）、BP 礼包（已有双 BP，结论早就是"别再堆 BP"）。
<b>四个抽取项全是纯配置礼包，开发成本约 2 天。</b></div>

</div>
<div class="pane" id="p6"><h2><span class="no">6·1</span>能力边界 — 两条线怎么分</h2>
<p class="lead">与zhangli对齐后的分工。<b>分线的意义不是排班，是把「一个月超 10 天」变成「两条线各自有没有超」</b>——
而红线是 <b>16d</b>（20d 档期扣掉 4d 改 BUG）——不是 20d。</p>
<table>
<tr><th style="width:132px">谁</th><th>负责什么</th><th>为什么归他</th></tr>
<tr><td><b style="color:#c084fc">zhangli（程序）</b></td>
<td>挖孔 · 海妖皮肤系统 · 弹珠<br><span style="color:var(--dim2)">主城套装系统功能 · 装饰物升级系统 · 团购礼包 · 复用活动包装配置（10 月）</span></td>
<td><b>要写新代码的系统</b>——新玩法、新外显系统、新协议。这些改动都落在服务端 + 客户端功能层，只能由程序开。</td></tr>
<tr><td><b style="color:#5ad1ff">linkang（配置 / 美术）</b></td>
<td>开箱开发 · 复用活动配置 · 行军特效搬运对接 · <b>全部内容的<b>美术资源进包</b></b><br>
<span style="color:var(--dim2)">红色英雄皮肤+互动 · 节日卡册 · 预购连锁礼包 · 主城套装美术资源沟通（10 月）</span></td>
<td><b>复用 + 搬运 + 对接</b>——已有框架内配置、P2 资源迁 X3 的规格/材质/DK 对齐、跨端沟通。不需要动系统层。</td></tr>
</table>
<div class="note"><b>边界判据一句话</b>：<b style="color:#c084fc">改系统的归zhangli</b>，<b style="color:#5ad1ff">改内容和资源的归 linkang</b>。
按这条切，9/10 两个月的活能干净地分成两条几乎不互相阻塞的线。</div>

<h2><span class="no">6·2</span>两条线的负载 — 对着 20d 红线看</h2>
{LOAD_HTML}
<div class="note"><b style="color:var(--bad)">配置人天填进来之后，主要缺口换了一条线</b>：
9 月<b style="color:var(--bad)">linkang 21d（超 5d）</b>· zhangli 20d（超 4d）；10 月zhangli 17d（超 1d）· <b style="color:var(--ok)">linkang 16d（正好）</b>。
<b>缺口合计 10d，其中 9 月占 9d。</b><br>
之前挖孔和海妖的配置量没估（10d / 5d 全按纯开发记在zhangli名下），一填进来（<b>挖孔数值 3d + 海妖数据 1d</b>）
<b>linkang 这条线就从 17d 跳到 21d，超过zhangli成了最紧的一条</b>——这也说明双单拆分不只是流程规范，它会直接改产能账。<br>
<b>两条线要分别解</b>：<br>
· <b style="color:#c084fc">zhangli超 4d</b> → <b>弹珠 5d 推到 11 月</b>，一步到位（20→15d，反而余 1d）。<br>
· <b style="color:#5ad1ff">我超 5d</b> → 挪不动的有三块：<b>美术资源进包 5d</b>（zhangli系统线的前置）、
<b>挖孔数值 3d + 海妖数据 1d</b>（跟着对应开发单走，不能错开）。
能动的只有<b>复用活动包装配置 6d</b>（无依赖）和<b>行军特效搬运 3d / 开箱 3d</b>（都是 W3 的活）——
但这三块都是 9 月节日本体必须的，砍了就没内容。<b style="color:var(--warn)">⇒ 实际解法只有「人工美术单分出去」或「复用活动配置找人分担」，靠挪单解决不了。</b></div>

<h2><span class="no">6·3</span>排期倒推 — 最晚什么时候开工</h2>
{GANTT_HTML}
<div class="note"><b>两条线不是对称的，有一个硬顺序</b>：
<b style="color:#5ad1ff">linkang 的「美术资源进包」（9 月 5d）和「主城套装美术资源沟通」（10 月 3d）都排在最前</b>——
因为它们是<b style="color:#c084fc">zhangli那条线的前置输入</b>：海妖皮肤系统要先有资源规格才能定数据结构，套装系统同理。
<b>这两块一拖，zhangli那条线就空转。</b><br>
其余部分两条线互不阻塞，可以完全并行；linkang 的「复用活动包装配置」（6d / 4d）是<b>最没有依赖的一块，天然当缓冲</b>——
哪条线出意外就先压它。</div>

<h2><span class="no">6·4</span>这套分工暴露出的两个待办</h2>
<table>
<tr><th style="width:150px">事项</th><th>状态</th><th>要谁拍</th></tr>
<tr><td><b style="color:var(--bad)">9 月两条线都超</b></td>
<td>zhangli 20d（超 4d）→ <b>弹珠推 11 月即解</b>；linkang 21d（超 5d）→ <b>挪不动，只能分担</b>：
不能挪的是美术资源进包 5d（zhangli前置）＋ 挖孔数值 3d ＋ 海妖数据 1d（跟开发单走），
能挪的三块又都是 9 月节日本体。</td>
<td><b>linkang，决定把哪些人工美术单 / 复用活动配置分出去</b></td></tr>
<tr><td>10 月「卡册 / 联盟总动员」二选一</td>
<td>两者<b>不叠加</b>，只做一个（记 5d）。定成二选一后linkang 这条线正好 16d 打平 ⇒ <b>10 月不能再往我这边加任何东西</b>。</td>
<td>linkang，随 10 月方案定</td></tr>
<tr><td><b style="color:var(--bad)">美术资源进包 5d 是新识别项</b></td>
<td>之前四个月的产能表里<b>完全没算这块</b>——P2 资源迁 X3 要过规格 / 材质 / DK 三关。
9 月估 5d、10 月估 3d 都是<b>拍的，没有实测</b>。第一批资源过完后要回头校准。</td>
<td>linkang，9 月首批资源过完后回填</td></tr>
</table>
</div>

<div class="pane" id="p7"><h2><span class="no">7·1</span>开单规则 — 一个功能什么时候拆成两单</h2>
<table>
<tr><th style="width:150px">情况</th><th>怎么开</th><th>本轮实例</th></tr>
<tr><td><b style="color:#f87171">有分工</b></td>
<td><b>拆成两个单</b>：一个「功能开发」给程序，一个「数值 / 内容配置」给策划。
两单同名前缀、互相挂关联，<b>验收时一起验</b>——只验开发单会漏掉奖池配错。</td>
<td><b>挖孔 v1 · 海妖皮肤系统</b>（各拆 2 单）</td></tr>
<tr><td>无分工</td><td>一个单到底，归属写清是程序还是配置。</td>
<td>弹珠 / 开箱 / 复用活动配置 / 各礼包搬运</td></tr>
<tr><td><b style="color:#fbbf24">美术</b></td>
<td><b>按资源类型拆，不按月或按活动打包。</b>一类资源一个单，因为交付物、参考图、验收标准都不同——
「9 月美术」这种单没法验收，「主城皮肤二周年高级档」才能。</td>
<td>9 月 14 个美术单 · 10 月 6 个</td></tr>
</table>

<h2><span class="no">7·2</span>工单清单</h2>
<p class="lead">人天列＝已排进产能表的数字；<b style="color:#f87171">「待拆」＝这块工作量还没从主单里拆出来，会额外压到linkang 这条线上</b>。
美术单不占程序/配置人天，单独走美术排期。</p>
{TICKET_HTML}

<h2><span class="no">7·3</span>美术单必带的三件事</h2>
<p class="lead">照 <b>X3 美术资源规范</b>（知识库既有沉淀）开单，缺任一项美术都会返工。</p>
<table>
<tr><th style="width:132px">必带项</th><th>为什么</th></tr>
<tr><td><b>尺寸 ＝ 与复用源同尺寸</b></td>
<td>X3 <b>同类资源跨活动尺寸完全不统一</b>（活动背景实测有 1080×1344 / 540×960 / 800×800 / 1080×140 等）。
所以不能写"按标准出"，只能写"与复用源 XX 的对应资源同尺寸"或写实查到的 px。</td></tr>
<tr><td><b style="color:#f87171">双参考（缺一不出图）</b></td>
<td><b>老图</b>＝复用源旧界面 → 定版式/尺寸/结构；<b>新图</b>＝本期实际投放物的资源图 → 定新主题元素长什么样。
只给老图美术画不出换皮后的新东西。<b>关键</b>：投放物多数是游戏里已有的现成资源，要去配置表+客户端里搜出来给美术，不是重画。</td></tr>
<tr><td><b>出图后四项核验</b></td>
<td>尺寸 / 格式与真透明 / 四边边距 / 主体占比，逐项对参考。
<b>透明必须验真</b>——AI 出的"透明底"常是画了浅灰或棋盘格的假透明，没有 alpha 通道。</td></tr>
</table>

<h2><span class="no">7·4</span>开单前要拍的三件事</h2>
<table>
<tr><th style="width:170px">待拍</th><th>影响</th><th>谁拍</th></tr>
<tr><td>挖孔 / 海妖的配置人天 <span style="color:var(--ok)">✓ 已估</span></td>
<td><b>挖孔数值与奖池 3d · 海妖数据与投放 1d</b>，已计入linkang 这条线（17d → <b style="color:var(--bad)">21d</b>）。
预警成立：这 4d 一进来，最紧的线就从zhangli换成了我。</td>
<td>—</td></tr>
<tr><td><b>主城套装几件成一套</b></td>
<td>直接决定 10 月最大那个美术单的工作量，件数没定这单开不出来。</td>
<td>linkang，10 月方案定稿时</td></tr>
<tr><td>卡册 / 联盟总动员二选一</td>
<td>选联盟总动员则「卡册卡面批次」美术单<b>不开</b>；两条路的美术量差很多。</td>
<td>linkang，随 10 月方案定</td></tr>
</table>
</div>

<div class="pane" id="p5"><h2><span class="no">5·1</span>目标账 — 40% 怎么来</h2>
<div class="note ok"><b>恒等式（两边实测都对得上）</b><br>
<span style="color:var(--fg);font-size:14.5px">累计节日占比 ＝ <b style="color:var(--bad)">(1−空窗率)</b> × <b style="color:var(--warn)">付费玩家付费率</b> × <b style="color:var(--acc)">节日 ARPPU</b> ÷ 大盘 ARPU</span><br>
X3：(1−{DX['gap_ratio']/100:.3f}) × {DX['payrate']:.1f}% × ${DX['arppu']:.1f} ÷ ${DX['arpu']:.1f} ＝ <b>{(1-DX['gap_ratio']/100)*DX['payrate']*DX['arppu']/DX['arpu']:.1f}%</b>（实测 15.0%）　｜
P2 同式 ＝ <b>{(1-DP['gap_ratio']/100)*DP['payrate']*DP['arppu']/DP['arpu']:.1f}%</b>（实测 37.7%）</div>

<table>
<tr><th>动作</th><th>攻哪个因子</th><th class="n">从</th><th class="n">到</th><th>谁负责</th><th class="n">开发成本</th></tr>
<tr><td><b>排满日历 + 每周一个主力</b></td><td style="color:var(--ok)">总量（空窗率↓）</td>
<td class="n">月占比 15%</td><td class="n"><b>20–25%</b></td><td><b>9 月</b>（三个 W · 21 天）</td><td class="n">15 天</td></tr>
<tr><td><b>深度付费优化</b>（方向 1–4）</td><td style="color:var(--acc)">节日 ARPPU</td>
<td class="n">${DX['arppu']:.1f}</td><td class="n"><b>$30.5+</b></td><td><b>10 月</b></td><td class="n">20 天</td></tr>
<tr><td><b>P2 礼包形式搬运</b>（方向 5）</td><td style="color:var(--warn)">付费率 ＋ 深度<b>双拉</b></td>
<td class="n">{DX['payrate']:.1f}%</td><td class="n"><b>40%+</b></td><td><b>10 月</b>（拆封顶/双轨/宽入口/榜）</td><td class="n">5 天</td></tr>
<tr style="background:rgba(74,222,128,.06)"><td colspan="2"><b>三件全做 ⇒ 累计节日占比</b></td>
<td class="n">15.0%</td><td class="n"><b style="color:var(--ok)">40%</b></td><td>11 月结账 · 12 月冲量</td><td class="n"><b>35 天</b></td></tr>
</table>
<div class="note warn"><b>两个诚实说明</b>：① 三段之间有重叠，表中已按下沿取值；
② <b>50% 必须两条腿一起走且 ARPPU 要摸到 P2 的 103%</b>——所以对外承诺建议讲 <b>35%</b>，40–50% 留作上限空间。</div>

<h2><span class="no">5·2</span>开发需求与产能</h2>
<p class="lead">版本容量口径＝一个周期约 <b>20 人天</b>（开发 70% ≈ 14 天 + 测试 30% ≈ 6 天）。</p>
<table>
<tr><th style="width:70px">月份</th><th>需求项</th><th class="n">人天</th><th class="n">容量</th><th class="n">余量</th></tr>
{"".join(f'''<tr><td><b>{mo}</b></td>
<td>{" · ".join(f"{n}<span style='color:var(--dim2)'>({d}d)</span>" for n, d in items)}</td>
<td class="n"><b>{sum(d for _, d in items)}</b></td><td class="n">{cap}</td>
<td class="n" style="color:{'var(--ok)' if cap-sum(d for _,d in items)>=0 else 'var(--bad)'}">
{cap-sum(d for _, d in items):+d}</td></tr>''' for mo, items, cap in DEV)}
<tr style="background:rgba(90,209,255,.05)"><td><b>合计</b></td><td>—</td>
<td class="n"><b>{sum(sum(d for _, d in it) for _, it, _ in DEV)}</b></td>
<td class="n"><b>{sum(c for _, _, c in DEV)}</b></td>
<td class="n" style="color:var(--ok)"><b>+{sum(c for _, _, c in DEV)-sum(sum(d for _, d in it) for _, it, _ in DEV)}</b></td></tr>
</table>
<div class="note bad"><b>产能不够，必须做取舍</b>：四个月合计 <b>104 人天 / 容量 80</b>，9 月超 <b>11d</b>、10 月超 10d、11 月超 7d，只有 12 月余 4d。<b>根因＝补齐了四项此前漏算的：新海妖皮肤系统（7d）、周年行军特效搬运（3d）、开箱周年限定宝箱版（3d·独立单）、每月的复用活动全部包装及配置（4–6d）。</b><br>三条路（加人 / 开发前置 / 砍内容）见「四个月怎么走」页签末尾的产能红线卡；<b>刚性不可砍＝挖孔、海妖系统、主城套装系统</b>。</div>

<h2><span class="no">5·3</span>9 / 10 月的反馈与验收节奏</h2>
<p class="lead">每月末按固定三项验收，<b>不达标就进 11 月结账清单</b>——这是这套规划的闭环，也是 11 月被设成轻开发月的原因。</p>
<table>
<tr><th style="width:76px">时点</th><th>验收什么</th><th style="width:230px">数据怎么来</th><th style="width:210px">不达标怎么办</th></tr>
{"".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td style="color:var(--dim2)">{c}</td><td>{d}</td></tr>' for a, b, c, d in FB)}
</table>
<div class="note ok"><b>三条验收原则</b>：
① <b>9 月只考核总量、10 月才拆因子</b>——9 月做的是填内容+拉长度，直接看<b>月占比</b>；10 月做深度优化，才拆成<b>付费率与 ARPPU 两个因子</b>分别看；
② <b>10 月两个因子要同时抬</b>，因为占比 ＝ 付费率 × ARPPU，只抬一个另一个跌回去就白做；
③ <b>口径必须锁死</b>：X3 成熟服 1000–1870 · 节日活跃日（付费率≥10%）· 中位数 · <b>日粒度</b>（周粒度数值天然更高，别混用）。</div>

<h2><span class="no">5·4</span>待拍板</h2>
<table>
<tr><th style="width:34px">#</th><th>事项</th><th>我的建议</th></tr>
{"".join(f'<tr><td class="n">{i+1}</td><td>{a}</td><td>{b}</td></tr>' for i, (a, b) in enumerate(ASK))}
</table>

<div class="note" style="margin-top:26px"><b>数据来源</b>　X3＝<code>v1090.ods_user_order</code>（成熟服 1000–1870，USD 口径）·
P2＝<code>v1041.dl_user_order</code> × <code>dim_iap</code>（节日＝<code>iap_type='混合-节日活动'</code>）·
节日期＝付费率≥10% 的连续日自动切段 · 生成器 <code>skills\\p2-festival-monitor\\x3_9to12_core_gen.py</code></div>

<script>
const SEGS={json.dumps(SEGS, ensure_ascii=False)};
const META={{
 payrate:{{lb:"付费玩家付费率",f:v=>v.toFixed(0)+"%",p2:{DP['payrate']:.2f},x3:{DX['payrate']:.2f},
  nt:"<b>9 月的 KPI。</b>X3 夏日只撑到 <b>D11</b> 就断（图上蓝虚线），P2 深海／拓荒能走满 <b>21–23 天</b>且中途反复起波。9 月要做的就是把这条线<b>横向拉到 D20</b>，靠三个 W 各一个主力模块顶住。"}},
 arppu:{{lb:"节日日均 ARPPU",f:v=>"$"+v.toFixed(0),p2:{DP['arppu']:.2f},x3:{DX['arppu']:.2f},
  nt:"<b>10 月的 KPI。</b>X3 活跃日中位 <b>${DX['arppu']:.1f}</b>、P2 <b>${DP['arppu']:.1f}</b>（拓荒节达 $38.5）。10 月要做的是把这条线<b>纵向抬到 $30.5–34.1</b>，四个方向全部作用在「已经在花钱的人」身上。"}}
}};
const W=1000,H=360,PL=54,PR=22,PT=24,PB=46;
const maxD=Math.max(...SEGS.map(s=>s.pts.length))-1;
// 默认只开「P2 拓荒节」（P2 最强样本）与「X3 夏日恋语」（X3 单节日样本，只到 D11）
// 其余曲线点图例可开：P2 深海节做第二参照，X3 世界杯+深海是双节叠加不算单节日
const DEF=["P2 拓荒节","X3 夏日恋语"];
const on={{}}; SEGS.forEach(s=>on[s.name]=DEF.includes(s.name));
const X=i=>PL+i/maxD*(W-PL-PR);
let K="payrate";
function lg(){{
 document.getElementById("lg").innerHTML=SEGS.map(s=>
  `<span style="cursor:pointer;opacity:${{on[s.name]?1:.34}}" data-n="${{s.name}}">
   <i style="background:${{s.color}}"></i>${{s.name}} <span style='color:var(--dim2)'>${{s.n}}天</span></span>`).join("");
 document.querySelectorAll("#lg span[data-n]").forEach(e=>e.onclick=()=>{{on[e.dataset.n]=!on[e.dataset.n];lg();draw();}});
}}
function draw(){{
 const m=META[K], vis=SEGS.filter(s=>on[s.name]);
 const top=Math.max(...vis.flatMap(s=>s.pts.map(p=>p[K])),m.p2,1)*1.14;
 const Y=v=>H-PB-(v/top)*(H-PB-PT);
 let s=`<svg viewBox="0 0 ${{W}} ${{H}}" width="100%"><defs>
  <marker id="a1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#4ade80"/></marker>
  <marker id="a2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fbbf24"/></marker></defs>`;
 for(let i=0;i<=5;i++){{const v=top*i/5,y=Y(v);
  s+=`<line x1="${{PL}}" y1="${{y.toFixed(0)}}" x2="${{W-PR}}" y2="${{y.toFixed(0)}}" stroke="#243040"/>
      <text x="${{PL-7}}" y="${{(y+4).toFixed(0)}}" font-size="10" fill="#6b7f95" text-anchor="end">${{m.f(v)}}</text>`;}}
 for(let i=0;i<=maxD;i+=3){{const x=X(i);
  s+=`<line x1="${{x.toFixed(0)}}" y1="${{PT}}" x2="${{x.toFixed(0)}}" y2="${{H-PB}}" stroke="#1c2733"/>
      <text x="${{x.toFixed(0)}}" y="${{H-PB+16}}" font-size="10" fill="#6b7f95" text-anchor="middle">D${{i}}</text>`;}}
 [["p2","#c084fc","P2 中位"],["x3","#5ad1ff","X3 中位"]].forEach(([k,c,lb])=>{{
  const y=Y(m[k]);
  s+=`<line x1="${{PL}}" y1="${{y.toFixed(1)}}" x2="${{W-PR}}" y2="${{y.toFixed(1)}}" stroke="${{c}}" stroke-dasharray="7 4" stroke-width="1.3" opacity=".7"/>
      <text x="${{W-PR-4}}" y="${{(y-6).toFixed(0)}}" font-size="10.5" fill="${{c}}" text-anchor="end">${{lb}} ${{m.f(m[k])}}</text>`;}});
 // 9月：横向拉长
 const x20=X(20),x11=X(11),ya=H-PB-14;
 s+=`<line x1="${{x20.toFixed(0)}}" y1="${{PT}}" x2="${{x20.toFixed(0)}}" y2="${{H-PB}}" stroke="#4ade80" stroke-dasharray="5 4" stroke-width="1.5"/>
     <text x="${{(x20-4).toFixed(0)}}" y="${{PT+12}}" font-size="10.5" fill="#4ade80" text-anchor="end">9月目标 D20（21天）</text>
     <line x1="${{x11.toFixed(0)}}" y1="${{ya}}" x2="${{(x20-6).toFixed(0)}}" y2="${{ya}}" stroke="#4ade80" stroke-width="1.6" marker-end="url(#a1)"/>
     <text x="${{((x11+x20)/2).toFixed(0)}}" y="${{ya-6}}" font-size="10.5" fill="#4ade80" text-anchor="middle">9月：拉长（夏日只到 D11）</text>`;
 // 10月：纵向抬高
 if(K==="arppu"){{const xa=W-PR-160,y1=Y(m.x3),y2=Y(m.p2);
  s+=`<line x1="${{xa}}" y1="${{y1.toFixed(1)}}" x2="${{xa}}" y2="${{(y2+7).toFixed(1)}}" stroke="#fbbf24" stroke-width="2" marker-end="url(#a2)"/>
      <text x="${{xa+8}}" y="${{((y1+y2)/2).toFixed(0)}}" font-size="11" fill="#fbbf24">10月：抬高 ARPPU</text>
      <text x="${{xa+8}}" y="${{((y1+y2)/2+14).toFixed(0)}}" font-size="10.5" fill="#fbbf24">${{m.f(m.x3)}} → ${{m.f(m.p2)}}</text>`;}}
 vis.forEach(g=>{{
  s+=`<path d="${{g.pts.map((p,i)=>(i?"L":"M")+X(p.i).toFixed(1)+" "+Y(p[K]).toFixed(1)).join(" ")}}" fill="none" stroke="${{g.color}}" stroke-width="${{g.w}}"`+(g.dash?` stroke-dasharray="${{g.dash}}"`:"")+`/>`;
  g.pts.forEach(p=>{{s+=`<circle cx="${{X(p.i).toFixed(1)}}" cy="${{Y(p[K]).toFixed(1)}}" r="${{g.side==='X3'?3:2.3}}" fill="${{g.color}}"><title>${{g.name}} D${{p.i}}（${{p.d}}）\\n${{m.lb}} ${{m.f(p[K])}}\\n节日收入 $${{p.fest.toLocaleString()}}</title></circle>`;}});
 }});
 s+=`<text x="${{W/2}}" y="${{H-5}}" font-size="11" fill="#8fa3b8" text-anchor="middle">节日第 N 天（D0 ＝ 各节日自己的开场日）→</text></svg>`;
 document.getElementById("ch").innerHTML=s;
 document.getElementById("nt").innerHTML=m.nt;
}}
document.querySelectorAll(".tabs button").forEach(b=>b.onclick=()=>{{
 document.querySelectorAll(".tabs button").forEach(o=>o.classList.toggle("on",o===b));
 K=b.dataset.k; draw();}});
lg(); draw();
document.querySelectorAll(".tb").forEach(b=>b.onclick=()=>{{
  document.querySelectorAll(".tb").forEach(o=>o.classList.toggle("on",o===b));
  document.querySelectorAll(".pane").forEach(p=>p.classList.toggle("on",p.id===b.dataset.p));
  window.scrollTo({{top:0}});
}});

var TKCOPY = {COPY_JSON};
document.querySelectorAll(".cp").forEach(function(btn){{
  btn.addEventListener("click", function(){{
    var txt = TKCOPY[btn.dataset.k] || "";
    var done = function(){{
      var old = btn.textContent;
      btn.textContent = "✓ 已复制"; btn.classList.add("ok");
      setTimeout(function(){{ btn.textContent = old; btn.classList.remove("ok"); }}, 1600);
    }};
    if (navigator.clipboard && window.isSecureContext) {{
      navigator.clipboard.writeText(txt).then(done, function(){{ fallback(txt, done); }});
    }} else {{ fallback(txt, done); }}
  }});
}});
function fallback(txt, cb){{
  var ta = document.createElement("textarea");
  ta.value = txt; ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select();
  try {{ document.execCommand("copy"); cb(); }} catch(e) {{ alert("复制失败"); }}
  document.body.removeChild(ta);
}}
</script>
</div>
</main></body></html>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
tmp = OUT + ".tmp"
open(tmp, "w", encoding="utf-8", newline="").write(html)
os.replace(tmp, OUT)
print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
