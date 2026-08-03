# -*- coding: utf-8 -*-
"""马戏团寻宝 103101 (ActvPioneerCity 81001) 玩家全程模拟
机制严格对齐服务端 ActivityMeta.PioneerCity.cs (origin/dev_festival)
"""
import random, io, sys, statistics
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------- 配置 (81001, origin/dev_festival 实配) ----------
RAINBOW_BASE, SOFT_START, HARD_PITY = 200, 8, 12
GRAND_CURVE = [20,20,20,20,20,20,100,300,700,1500,4000,10000]

# 外圈 11 普通格: (名字, 钻值)
OUTER = [
    ("钻石×250", 250), ("钻石×500", 500), ("钻石×1000", 1000),
    ("材料票×15", 750), ("材料票×25", 1250),
    ("5分加速×15", 600), ("30分加速×5", 1000),
    ("祝福银币×10", 500), ("祝福银币×15", 750),
    ("稀有技能书×5", 375), ("史诗技能书×5", 1250),
]
# 内圈 8 档: (名字, 单hit钻值, 抽取上限)
INNER = [
    ("8小时加速×2",   6400, 2),
    ("通用技能碎片×4", 20000, 2),
    ("传奇技能书×25", 12500, 1),
    ("神秘金属×45",   22500, 1),
    ("传奇装备宝箱×1",17500, 1),
    ("诅咒的龙骸×3",  30000, 2),
    ("钻石×15000",    15000, 1),
    ("万能传奇信物×9",45000, 2),
]
# 购买序列: (名字, USD, 门票数, 附带钻石, 附带其他钻值)
PACKS = [
    ("链包-免费档",      0.00,  1,     0, 1540),   # 材料票30+5分加速1
    ("链包 $4.99",       4.99,  1,  2500, 0),
    ("链包 $9.99",       9.99,  2,  5000, 0),
    ("链包 $19.99",     19.99,  4, 10000, 0),
    ("链包 $49.99",     49.99, 10, 25000, 0),
    ("阶梯1 $19.99",    19.99,  4, 10000, 0),
    ("阶梯2 $19.99",    19.99,  4, 10000, 0),      # +头像框(外显不计价)
    ("阶梯3 $19.99",    19.99,  4, 10000, 1250),   # 史诗技能书×5+表情
]
REPEAT = ("链包 $99.99(可复购)", 99.99, 20, 50000, 0)

# 寻宝累充 AO100600: (累充美元门槛, 送门票, 送罗盘) 罗盘250钻/个
RECHARGE_LADDER = [(10,1,5),(40,3,15),(100,6,25),(200,10,35),(400,20,40),
                   (700,30,45),(1000,30,45),(1300,30,45),(1600,30,45),(2000,40,45)]

def rainbow_rate(pity):
    if pity >= HARD_PITY: return 10000
    if pity < SOFT_START: return RAINBOW_BASE
    span = HARD_PITY - SOFT_START + 1
    return min(10000, RAINBOW_BASE + (10000-RAINBOW_BASE)*(pity-SOFT_START+1)//span)

class Player:
    def __init__(s, rng):
        s.rng=rng; s.tickets=0; s.usd=0.0; s.gems_from_packs=0; s.extra_val=0
        s.outer_val=0; s.inner_val=0; s.outer_draws=0; s.stars=0
        s.pack_i=0; s.outer_avail=list(range(11)); s.outer_pity=0
        s.inner_counts=[0]*len(INNER); s.inner_total=0
        s.grand=False; s.exhausted=False; s.free_outer_used=False
        s.outer_loot={}; s.inner_loot={}
        s.ladder_i=0; s.ladder_tickets=0; s.ladder_val=0
    def buy_next(s):
        if s.pack_i < len(PACKS): p=PACKS[s.pack_i]; s.pack_i+=1
        else: p=REPEAT
        s.usd+=p[1]; s.tickets+=p[2]; s.gems_from_packs+=p[3]; s.extra_val+=p[4]
        got=[]
        while s.ladder_i < len(RECHARGE_LADDER) and s.usd >= RECHARGE_LADDER[s.ladder_i][0]:
            _,tk,cp = RECHARGE_LADDER[s.ladder_i]; s.ladder_i+=1
            s.tickets+=tk; s.ladder_tickets+=tk; s.ladder_val+=cp*250
            got.append((tk,cp))
        return p, got
    def draw_outer_once(s, free=False):
        """返回 (中彩虹星?, 格子名)"""
        s.outer_draws+=1
        pity = s.outer_pity+1
        hit = (len(s.outer_avail)==0) or (s.rng.randrange(10000) < rainbow_rate(pity))
        if not free and not hit is None: pass
        if hit:
            s.stars+=1; s.outer_pity=0; s.outer_avail=list(range(11))
            return True, "彩虹星"
        idx = s.rng.choice(s.outer_avail); s.outer_avail.remove(idx); s.outer_pity+=1
        name,val = OUTER[idx]; s.outer_val+=val
        s.outer_loot[name]=s.outer_loot.get(name,0)+1
        return False, name
    def draw_inner_once(s):
        """返回 (中大奖?, 档名或None)"""
        s.inner_total+=1
        avail=[i for i,(n,v,lim) in enumerate(INNER) if s.inner_counts[i]<lim]
        if not avail:
            s.exhausted=True
            if not s.grand: s.grand=True
            return True, None
        idx_c = s.inner_total-1
        rate = GRAND_CURVE[idx_c] if idx_c < len(GRAND_CURVE) else 0
        if not s.grand and s.rng.randrange(10000) < rate:
            s.grand=True; return True, None
        i = s.rng.choice(avail); s.inner_counts[i]+=1
        name,val,lim = INNER[i]; s.inner_val+=val
        s.inner_loot[name]=s.inner_loot.get(name,0)+1
        if s.grand and all(s.inner_counts[j]>=INNER[j][2] for j in range(len(INNER))):
            s.exhausted=True
        return False, name

def run_full(rng, narrate=False, goal="clear"):
    """goal: clear=抽空内圈 / grand=拿到皮肤即停"""
    P=Player(rng); log=[]
    # 免费资源
    (p,_)=P.buy_next()
    if narrate: log.append(f"领{p[0]}: 门票×1 + 材料票30/加速(≈1540钻)")
    hit,name=P.draw_outer_once(free=True)  # 活动免费单抽,不耗票
    if narrate: log.append(f"免费单抽 → {name}")
    if not hit: pass
    while not (P.exhausted if goal=="clear" else P.grand):
        # 有星先抽内圈
        if P.stars>0:
            P.stars-=1
            g,name=P.draw_inner_once()
            if narrate:
                if g and P.grand and name is None:
                    log.append(f"  ★内圈第{P.inner_total}抽 → 🎪直中大奖【狂欢剧场·永久岛皮】(本抽概率{GRAND_CURVE[min(P.inner_total,12)-1]/100:.1f}%)")
                else:
                    log.append(f"  ●内圈第{P.inner_total}抽 → {name}")
            continue
        # 没星: 没票先买包
        if P.tickets<=0:
            p,got=P.buy_next()
            if narrate:
                line=f"💰买{p[0]} → 门票+{p[2]} (随包返钻{p[3]}) | 累计消费${P.usd:.2f}"
                for tk,cp in got: line+=f"\n   🎁触发寻宝累充档 → 再送门票×{tk}+罗盘×{cp}"
                log.append(line)
        # 连抽到中星或票尽
        cycle=[]
        while P.tickets>0:
            P.tickets-=1
            hit,name=P.draw_outer_once()
            cycle.append(name)
            if hit: break
        if narrate and cycle:
            n=len(cycle)
            got = "、".join(cycle[:-1]) if cycle[-1]=="彩虹星" else "、".join(cycle)
            star = f" → 第{n}抽中彩虹星✨" if cycle[-1]=="彩虹星" else "(票尽未中星)"
            log.append(f"外圈连抽{n}次{star}  途中: {got if got else '—'}")
    return P, log

def main():
    seed=20260731
    # ---------- 理论值 ----------
    # 外圈每星期望票数
    surv=1.0; e_cycle=0.0
    for n in range(1,13):
        p=rainbow_rate(n)/10000
        e_cycle += n*surv*p; surv*=(1-p)
    # 内圈拿大奖期望抽数
    surv=1.0; e_grand=0.0
    for k,r in enumerate(GRAND_CURVE,1):
        p=r/10000; e_grand += k*surv*p; surv*=(1-p)
    print(f"◆ 理论: 每颗彩虹星期望 {e_cycle:.2f} 张门票 | 大奖期望第 {e_grand:.2f} 次内圈抽命中 | 全清恒定需 13 颗星")
    print(f"◆ 全清期望门票 ≈ {13*e_cycle:.0f} 张")

    # ---------- 单人叙事跑 ----------
    print("\n"+"="*78+"\n【模拟实录】一名玩家从零跑到全清 (seed=%d)\n"%seed+"="*78)
    P,log = run_full(random.Random(seed), narrate=True)
    for l in log: print(l)
    tot_val = P.gems_from_packs + P.extra_val + P.outer_val + P.inner_val + P.ladder_val
    print("-"*78)
    print(f"总消费 ${P.usd:.2f} (={P.usd*500:.0f}钻)  门票消耗{P.outer_draws-1}张(其中累充白送{P.ladder_tickets})  彩虹星{P.inner_total}颗")
    print(f"到手: 礼包返钻 {P.gems_from_packs}  外圈产出 {P.outer_val}钻  内圈产出 {P.inner_val}钻  累充罗盘 {P.ladder_val}钻  其他 {P.extra_val}钻")
    print(f"     + 永久岛屿皮肤【狂欢剧场】(非卖品,不计钻)")
    print(f"综合ROI(含返钻) = {tot_val/(P.usd*500)*100:.0f}%   纯活动增量ROI = {(P.outer_val+P.inner_val)/(P.usd*500)*100:.0f}%")
    print("\n外圈战利品:", ", ".join(f"{k}×{v}" for k,v in sorted(P.outer_loot.items())))
    print("内圈战利品:", ", ".join(f"{k}×{v}" for k,v in sorted(P.inner_loot.items())))

    # ---------- Monte Carlo ----------
    N=50000; rng=random.Random(1)
    usd_c=[]; tick_c=[]; roi_c=[]; act_c=[]
    usd_g=[]; grand_at=[]
    for _ in range(N):
        P,_=run_full(rng); usd_c.append(P.usd); tick_c.append(P.outer_draws-1)
        tv=P.gems_from_packs+P.extra_val+P.outer_val+P.inner_val+P.ladder_val
        roi_c.append(tv/(P.usd*500)); act_c.append((P.outer_val+P.inner_val+P.ladder_val)/(P.usd*500))
    for _ in range(N):
        P,_=run_full(rng, goal="grand"); usd_g.append(P.usd); grand_at.append(P.inner_total)
    def q(a,p): return sorted(a)[int(len(a)*p)]
    print("\n"+"="*78+f"\n【蒙特卡洛 ×{N}】\n"+"="*78)
    print(f"◇ 全清(拿满内圈+皮肤): 花费 中位数 ${statistics.median(usd_c):.2f} | P10 ${q(usd_c,.10):.2f} ~ P90 ${q(usd_c,.90):.2f} | 均值 ${statistics.mean(usd_c):.2f}")
    print(f"   门票消耗 中位数 {statistics.median(tick_c):.0f} 张 (P10 {q(tick_c,.10)} ~ P90 {q(tick_c,.90)})")
    print(f"   综合ROI(含返钻) 中位 {statistics.median(roi_c)*100:.0f}% | 纯活动增量ROI 中位 {statistics.median(act_c)*100:.0f}%")
    print(f"◇ 只为皮肤(中大奖即停): 花费 中位数 ${statistics.median(usd_g):.2f} | P10 ${q(usd_g,.10):.2f} ~ P90 ${q(usd_g,.90):.2f}")
    print(f"   大奖命中在内圈第 {statistics.mean(grand_at):.1f} 抽(均值); 分布: " +
          " ".join(f"[{k}抽]{grand_at.count(k)/N*100:.0f}%" for k in range(7,14) if grand_at.count(k)>0))
    lo6=sum(1 for g in grand_at if g<=6)/N*100
    print(f"   前6抽直中大奖的幸运儿: {lo6:.1f}%")

if __name__=="__main__":
    main()
