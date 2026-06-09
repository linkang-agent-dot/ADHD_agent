# -*- coding: utf-8 -*-
"""X3 世界杯活动系列策划案 —— GSheet 构建脚本（建表→写内容→套格式）。
可复跑：内容用 update_range 覆盖写。SID 已建好传入。
样式token：行级 T(绿18大标题) H(粗11二级) TH(浅蓝灰表头) S(粗10小计) B(正文10)；
单元格token：[客户端处理]→粉 [配置说明]→米黄 需程序→橙 换美术→蓝 纯复用→灰。
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\scripts')
import gsheet_utils as gs

SID = '1eAG8w9y4f_hJMc1l_pMVglzdWf9M4sLTOlKcIKq_BEc'

# ---------- 颜色 ----------
GREEN=(0.557,0.878,0.522); THEAD=(0.85,0.9,0.95); PEACH=(0.988,0.922,0.80)
PINK=(1,0.6,1); ORANGE=(1,0.6,0); LBLUE=(0.812,0.886,1.0); GRAY=(0.851,0.851,0.851)
def _c(rgb): return {"red":rgb[0],"green":rgb[1],"blue":rgb[2]}

CELL_TOKENS={'[客户端处理]':PINK,'[配置说明]':PEACH,'需程序':ORANGE,'换美术':LBLUE,'纯复用':GRAY}

# 列宽（按页签类型：模块页列阶梯正文在E要宽 / 甘特页均匀 / 表格页均衡 / 总览专用）
MODULE_W=[110,70,215,95,330,150,120,120,120,120]
TABLE_W=[160,140,190,215,270,130,110,110,110,110]
TAB_WIDTHS={
 '总览·排期':[175,95,310,120,250,110,95,95,95,95],
 '排期甘特图':[200,84,84,84,84,84,84,84],
}

# ---------- 每页签内容：(style, [A,B,...]) ----------
def T(*c): return ('T', list(c))
def H(*c): return ('H', list(c))
def TH(*c): return ('TH', list(c))
def S(*c): return ('S', list(c))
def B(*c): return ('B', list(c))

TABS = {}

# ============ 总览·排期 ============
TABS['总览·排期'] = [
 T('▌X3 世界杯活动系列 · 总览'),
 H('〇、活动主题与基调'),
 B('主题','','2026 国际足球世界杯（真实赛事联动）'),
 B('活动名','','「绿茵狂热 · 世界杯」 / World Cup Frenzy'),
 B('周期','','32强小组赛 → 决赛，约 6/11–7/6（~26天，节日级长活动）'),
 B('核心目标','','深度付费；修「宽口浅底」，补 $9.99/$19.99 中段付费断层'),
 B('设计基调','','真实赛事代入 + 合规规避（竞猜=买礼包，花钱必有回报，预测对只是额外bonus）'),
 B('★零新后端','','整个系列复用现有系统(转盘/BP/礼包)，结算走运营SOP+现有bulk-mail，无程序新开发'),
 T('一、付费深度提升思路'),
 H('1、核心飞轮（世界杯金券=唯一闭环货币）'),
 B('','','竞猜 + BP 产「世界杯金券」 → 主抽奖转盘消耗 → 英雄 + 足球拉拉队皮肤(限定)大奖。'),
 B('','','金券只从 竞猜礼包 / 免费预测 / BP 三条线产出，只在转盘消耗 —— 三条付费线全部汇流到大奖拉力。'),
 H('2、深度结构（套用 P2「宽口浅底」教训）'),
 B('1）','','竞猜礼包价格阶梯 $4.99 / $9.99 / $19.99，补中段断层；高档礼包猜对加送更多金券 = pay-to-predict-more 深度杠杆'),
 B('2）','','转盘中段 GACHA 拉复购，顶端足球拉拉队皮肤套装做情感向高价外显（P2 实证高R最吃情感款）'),
 B('3）','','BP 三轨(免费/高级/至尊)做抗衰退订阅形态，覆盖全周期'),
 B('4）','','投放四阶段错开付费点：小组赛引流(免费/低价) → 16强付费深化($9.99) → 8/4强高价($19.99)+皮肤 → 决赛多实例高潮'),
 T('二、历史付费表现参考（数仓实测·全服全期·不预估增量）'),
 TH('历史对标节日','付费人数','收入(USD)','ARPPU','口径/说明'),
 B('尼罗之辉','832','$47,785','$57.43','近期最强节日，世界杯目标对标'),
 B('情人节','511','$30,010','$58.73','情感向节日(ARPPU 最高)'),
 B('春节','315','$14,984','$47.57',''),
 B('★世界杯目标基准','—','—','≈ $57','对标历史最强节日尼罗；不预估增量，实际看飞轮+深度结构落地'),
 B('口径','','数仓 v1090.ods_user_order；pay_status=1；收入=usd取actual_charge其余pay_price；按节日Pack前缀(2106/2107/2108)聚合，2026-06-09查'),
 T('三、活动排期'),
 B('','','▶ 甘特图见「排期甘特图」页签；下表为各阶段动作明细'),
 TH('阶段','时间窗','上线模块 / 动作','开发量','复用/新增'),
 B('阶段1 引流','D1-3 小组赛','主转盘开启 + BP开启 + 每日免费竞猜 + 低价$4.99竞猜礼包','纯复用','复用 ActvLuckyWheel / ActvBattlePassScore / Pack'),
 B('阶段2 深化','D4-14 小组赛后程','付费竞猜转 $9.99 为主 + 转盘累抽阶梯推进 + BP冲刺','纯复用','逐场配竞猜礼包'),
 B('阶段3 高价','D15-22 16强/8强','$19.99 竞猜礼包 + 皮肤套装预热 + 转盘保底冲刺','换美术','足球拉拉队皮肤'),
 B('阶段4 高潮','D23-26 4强/决赛','决赛多实例竞猜(免费+多档付费同场) + 转盘超级大奖保底冲刺','纯复用','决赛多Pack实例'),
 T('四、各模块解锁条件'),
 TH('模块','ActvType','解锁/开启条件','TimeCycle','配置表'),
 B('主转盘','10','活动期绝对时间开启','新增TC行','ActvLuckyWheel 族'),
 B('比赛竞猜','Pack礼包(无独立ActvType)','逐场上限时礼包(付费)/$0领取(免费)','各场TC/绝对时间','Pack / ActvOnline'),
 B('付费BP','22','活动期开启','新增TC行','ActvBattlePassScore 族'),
 B('⚠️ 跨服注意','','若 ActvOnline.CrossServerRank=1，绑定 TimeCycle 必须 TriggerType=1 绝对时间','','见 reference_x3_timecycle'),
]

# ============ 排期甘特图（独立页·列宽均匀）============
TABS['排期甘特图'] = [
 T('▌活动排期甘特图'),
 B('','','■ = 活动开启窗口；列为赛程阶段，日期按 FIFA 真实赛程对齐(待定)'),
 ('GH',['模块 \\ 赛程','小组赛D1-3','小组赛D4-9','小组赛D10-17','16强D18-21','8强D22-23','4强D24-25','决赛D26']),
 ('G',['主转盘(冠军之轮)','■','■','■','■','■','■','■']),
 ('G',['付费BP(冠军通行证)','■','■','■','■','■','■','■']),
 ('G',['免费竞猜(每日预测)','■','■','■','■','■','■','■']),
 ('G',['付费竞猜 $4.99(引流)','■','■','','','','','']),
 ('G',['付费竞猜 $9.99(深化)','','■','■','■','','','']),
 ('G',['付费竞猜 $19.99(高价)','','','','■','■','■','■']),
 ('G',['皮肤套装预热','','','','■','■','','']),
 ('G',['决赛多实例','','','','','','','■']),
]

# ============ 模块1-世界杯转盘 ============
TABS['模块1-世界杯转盘'] = [
 T('▌模块1 · 世界杯幸运转盘（主抽奖）'),
 H('〇、包装层'),
 B('活动名','「冠军之轮」 / Champion\'s Spin'),
 B('界面主标题','旋转冠军之轮，赢取世界杯传奇！'),
 B('副标题','用世界杯金券抽取，限定英雄与足球拉拉队皮肤等你来夺！'),
 B('按钮文案','单抽 / 十连抽 / 每日免费抽'),
 B('主题视觉关键词','奖杯金光、草绿球场、世界杯旗帜、拉拉队彩带、纸屑庆典'),
 H('一、设计目的'),
 B('1.1 核心目的','作为飞轮终点，承接竞猜/BP产出的金券，用限定外显大奖拉动持续抽取与深度付费'),
 B('1.2 付费点','金券不足时引导补充(竞猜礼包/BP)；累抽阶梯+超级大奖保底驱动大R冲刺'),
 B('1.3 目标人群','中R~超R(情感向皮肤套装)；全R(每日免费抽+累抽阶梯引流)'),
 B('1.4 最终大奖','足球宝贝皮肤·爱莉希雅(Hero 1040·传奇·白毛大胸·D29-34招募可得,D35内) + 限定英雄'),
 H('二、玩法说明'),
 B('','复用现有幸运大转盘(ActvLuckyWheel)。玩家用世界杯金券单抽/十连抽，奖池分 超级大奖/稀有/普通 三层；'),
 B('','每日有免费抽次数；累计抽数触发阶梯宝箱礼包；累计抽数达保底必出超级大奖。换皮世界杯主题，玩法规则不变。'),
 H('三、规则说明'),
 B('3.1','','基础设定','',''),
 B('','3.1.1','活动类型','[配置说明]','复用 ActvType=10 (ActvLuckyWheel)，新增 ContentID 一行'),
 B('','3.1.2','活动开启','[配置说明]','新增 TimeCycle 行 + ActvOnline.TimeController 指向；ActvOnline.MailID 必填(101109)'),
 B('','3.1.3','功能入口','[客户端处理]','世界杯活动主页 → 冠军之轮 页签'),
 B('3.2','','抽奖机制(复用·配置要点)','',''),
 B('','3.2.1','消耗道具','[配置说明]','抽奖消耗道具=世界杯金券(Item 1140)；单抽消耗数量=10；10连抽消耗数量=100（草案）'),
 B('','3.2.2','每日免费抽','[配置说明]','关闭每日免费=0(开启)；保留每日免费抽引流(沿用历史值)'),
 B('','3.2.3','奖池分层','[配置说明]','奖励池→ActvLuckyWheelReward：是否为超级大奖=1(皮肤/英雄)；稀有(养成+钻石)；普通(资源)；权重控制概率'),
 B('','3.2.4','超级大奖保底','[配置说明]','超级大奖次数=累计N抽必出(草案累计200)；超级大奖次数(每天)=每日上限；本服排行榜按抽数'),
 B('','3.2.5','累抽阶梯礼包','[配置说明]','额外奖励组→ActvLuckyWheelOtherReward：需要次数 5/20/40/70/120/200 各发对应奖励id'),
 B('','3.2.6','单日上限','[配置说明]','单日抽奖次数上限(沿用历史，防刷)'),
 B('3.3','','外围','',''),
 B('','3.3.1','红点提示','[客户端处理]','入口:有免费抽/金券≥十连可抽；阶梯宝箱可领；超级大奖未领'),
 B('','3.3.2','大奖跑马灯','[配置说明]','超级大奖产出全服跑马灯(MarqueeRuntips)'),
 B('','3.3.3','金券回收','[配置说明]','活动结束剩余金券按比例回收发邮件(MailID)'),
 H('四、配置表（复用·本期要配字段）'),
 S('ActvLuckyWheel__ActvLuckyWheel（主表）'),
 TH('字段','编号','抽奖消耗道具','单抽消耗数量','10连抽消耗数量','额外奖励组','奖励池','超级大奖次数','累计抽卡次数','触发礼包'),
 B('本期值','新ContentID','1140(金券)','10','100','OtherReward组','Reward组','200(保底)','阶梯触发','可空/链礼包'),
 B('DK字段','','DK_转盘图片 / DK_转盘指针图标 / DK_底部背景图 → 换世界杯皮(见美术页签)','','','','','','',''),
 S('ActvLuckyWheelReward（奖池）'),
 TH('字段','编号','BD_组','道具id','道具数量','权重','是否为超级大奖','界面排序'),
 B('说明','行号','同主表奖励池','奖励道具/皮肤/英雄','数量','概率权重','1=超级大奖','UI顺序'),
 S('ActvLuckyWheelOtherReward（累抽阶梯）'),
 TH('字段','编号','BD_组','奖励id','DK_宝箱icon','需要次数'),
 B('说明','行号','同主表额外奖励组','阶梯Reward','宝箱图标DK','5/20/40/70/120/200'),
 H('五、界面交互'),
 B('UILuckyWheel.prefab','','复用，仅换皮；逐元素读上述配置；Text key 见本地化页签','[客户端处理]','转盘盘面/指针/抽奖按钮/奖池预览/累抽进度条/超级大奖展示 均沿用'),
 H('六、美术需求（占位·待定皮肤来源）'),
 B('🔧 转盘盘面','DK_转盘图片 世界杯主题','待美术','占位','待定皮肤来源/具体美需'),
 B('足球宝贝皮肤·爱莉希雅','超级大奖立绘+模型(FBX)+Spine+卡片+头像','基础英雄=爱莉希雅 Hero1040','待美术出图','客户端零现成资产，需新出；字段 Hero__HeroSkin DK_Prefab/Head/Fullbody/Spine/HeroCard；详见「足球宝贝设计稿」'),
 H('七、本地化'),
 B('','见「活动本地化」页签 转盘段',' ',' ',' '),
]

# ============ 模块2-比赛竞猜 ============
TABS['模块2-比赛竞猜'] = [
 T('▌模块2 · 每日比赛竞猜（飞轮入口）'),
 H('〇、包装层'),
 B('活动名','「胜负预言」 / Match Oracle'),
 B('界面主标题','预言绿茵胜负，赢取冠军金券！'),
 B('副标题','选择你看好的一方，预测正确额外赢取世界杯金券！'),
 B('按钮文案','免费预测 / 购买助威礼包'),
 H('一、设计目的'),
 B('1.1 核心目的','飞轮入口产金券；用真实赛事代入感驱动每日参与与付费；价格阶梯做中段深度'),
 B('1.2 付费点','付费助威礼包(每个结果一个礼包)，买哪个=押哪个；高档礼包猜对加送更多金券'),
 B('1.3 合规规避','★竞猜=买礼包：花钱必得金券(有回报，非赌博)；预测正确只是额外bonus'),
 B('1.4 目标人群','全R(免费预测引流) + 中高R(付费助威礼包深度)'),
 H('二、玩法说明'),
 B('','每场真实比赛 = 一个竞猜活动实例(统一模板)。运营按场逐配「免费 / 付费 + 价格档」。'),
 B('','玩家对一场比赛只能竞猜一次、锁定一个结果(主胜/平/客胜)，不可改、不可对冲。'),
 B('','比赛结束→运营拿真实赛果→查日志命中买对/猜对玩家→bulk-mail批量发bonus金券+结算邮件(兼做赛果通知)。'),
 H('三、规则说明'),
 B('3.1','','基础设定','',''),
 B('','3.1.1','活动载体','[配置说明]','付费=限时礼包(Pack)；免费=$0领取礼包(Pack价格0)。无独立ActvType'),
 B('','3.1.2','一场一实例','[配置说明]','每场比赛建一组礼包(每结果一个)；运营按场选 免费/付费 及价格档；常规一场一个，决赛可多上'),
 B('','3.1.3','活动开启','[配置说明]','逐场按赛程绝对时间开/关(赛前开售→开赛锁盘)'),
 B('','3.1.4','功能入口','[客户端处理]','世界杯活动主页 → 胜负预言 页签 → 当日比赛列表'),
 B('3.2','','竞猜机制','',''),
 B('','3.2.1','结果模板','[配置说明]','每场 N 个结果礼包：主胜/平/客胜(淘汰赛可简化2项)。免费/付费共用同一套结果模板'),
 B('','3.2.2','★防对冲(锁定)','[客户端处理]','每人每场只能选一个结果：买了一个结果礼包/领了免费预测后，本场其余结果置灰锁定，不可再买/改'),
 B('','3.2.3','付费竞猜','[配置说明]','买某结果礼包=押该结果。礼包必得金券(保底价值)；价格档 $4.99/$9.99/$19.99 运营按场选'),
 B('','3.2.4','免费竞猜','[配置说明]','每日1场免费预测额度=$0领取该结果"竞猜票"礼包(借领取日志记录所选结果)'),
 B('','3.2.5','结算发券','[配置说明]','赛果=所押结果→额外加送bonus金券(付费按档:$4.99/$9.99/$19.99=+20/+50/+120草案；免费猜对+5)'),
 B('','3.2.6','开赛锁盘','[客户端处理]','开赛时间到→该场所有礼包下架，不可再竞猜'),
 B('3.3','','外围','',''),
 B('','3.3.1','红点提示','[客户端处理]','今日有可免费预测的场次；有未结算/待领的金券'),
 B('','3.3.2','结算邮件','[配置说明]','每场结束发结算邮件：写明赛果+你的预测+发放bonus金券(兼做赛果通知，游戏内不做赛果展示界面)'),
 H('四、配置表（复用 Pack）'),
 S('Pack__Pack（每场每结果一行；免费场价格=0）'),
 TH('字段','PackID','PackType','价格档($)','礼包内容(必得金券+资源)','OpenActv/开启','结果标记(运营记录)'),
 B('示例·付费','新PackID','限时礼包','4.99/9.99/19.99','金券30/70/160 + 养成资源(ROI落档)','逐场绝对时间','主胜/平/客胜(运营登记表)'),
 B('示例·免费','新PackID','$0领取','0','金券0(仅记录预测)','逐场','同上'),
 B('注','金券加送(bonus)不在Pack里配，走结算邮件由运营按赛果发(见运营SOP页签)','','','','',''),
 H('五、界面交互'),
 B('UI比赛列表','','当日比赛卡片列表(队伍/开赛时间/状态)','[客户端处理]','复用礼包列表/活动页样式；队徽=美术'),
 B('UI单场竞猜','','三结果礼包并列 + 选一个锁定其余','[客户端处理]','★防对冲置灰逻辑；显示礼包内容+猜对加送金券文案'),
 B('UI我的预测','','已选结果展示(只读)','[客户端处理]','显示本场已押结果，等待赛果'),
 B('注','★交互含状态机(可竞猜→已锁定→已开赛→已结算)，落地前走《X3交互模块工作流》出活原型确认','[客户端处理]','',''),
 H('六、运营SOP'),
 B('','结算流程/漏发补偿 见「运营SOP·结算」页签',' ',' ',' '),
 H('七、美术需求（占位）'),
 B('🔧 竞猜界面','比赛卡片/队徽/结果礼包图/胜负预言主视觉','待美术','占位','待定来源'),
 H('八、本地化'),
 B('','见「活动本地化」页签 竞猜段',' ',' ',' '),
]

# ============ 模块3-付费BP ============
TABS['模块3-付费BP'] = [
 T('▌模块3 · 世界杯通行证（付费BP）'),
 H('〇、包装层'),
 B('活动名','「冠军通行证」 / Champion Pass'),
 B('界面主标题','解锁冠军通行证，赛季奖励全收！'),
 B('副标题','完成世界杯任务累积积分，免费/高级/至尊三轨豪礼等你领！'),
 B('按钮文案','解锁高级 / 解锁至尊 / 一键升级'),
 H('一、设计目的'),
 B('1.1 核心目的','独立付费深度线(不绑竞猜)；订阅形态抗衰退，覆盖全周期'),
 B('1.2 付费点','高级/至尊礼包解锁付费轨；钻石买等级(冲刺款)'),
 B('1.3 目标人群','中R(高级轨) + 大R/超R(至尊轨+钻石买级)'),
 B('1.4 奖励','金券 + 足球拉拉队皮肤碎片 + 世界杯主题外显 + 养成资源'),
 H('二、玩法说明'),
 B('','复用 ActvBattlePassScore(ActvType=22)。完成世界杯主题任务获积分→升BP等级→三轨(免费/高级/至尊)领奖。'),
 B('','高级轨/至尊轨需购买对应礼包解锁；支持用钻石直接购买等级冲刺。换皮世界杯主题，玩法不变。'),
 H('三、规则说明'),
 B('3.1','','基础设定','',''),
 B('','3.1.1','活动类型','[配置说明]','复用 ActvType=22 (ActvBattlePassScore)，新增 ContentID'),
 B('','3.1.2','活动开启','[配置说明]','新增 TimeCycle + ActvOnline.TimeController；MailID 必填'),
 B('','3.1.3','功能入口','[客户端处理]','世界杯活动主页 → 冠军通行证 页签'),
 B('3.2','','BP机制(复用·配置要点)','',''),
 B('','3.2.1','积分获取','[配置说明]','积分获取方式→ActvScoreTask：每日登录/参与竞猜/抽转盘/活动任务(草案)'),
 B('','3.2.2','三轨奖励','[配置说明]','奖励组→BattlePassScoreReward：每级配 免费奖励/高级奖励/至尊奖励'),
 B('','3.2.3','付费解锁','[配置说明]','购买礼包→Pack：高级礼包($14.99草案)/至尊礼包($29.99草案)，解锁对应轨道'),
 B('','3.2.4','钻石买等级','[配置说明]','可以购买等级=1；BattlePassScoreReward.升级钻石价格 配每级跳级价'),
 B('','3.2.5','等级与积分','[配置说明]','BattlePassScoreReward：等级 + 积分需求(每级阈值) 配满全周期(草案30级)'),
 B('3.3','','外围','',''),
 B('','3.3.1','红点提示','[客户端处理]','有可领奖励档；积分可升级；至尊轨未解锁提示'),
 B('','3.3.2','到期补领','[配置说明]','活动结束未领奖励发邮件(MailID)'),
 H('四、配置表（复用·本期要配字段）'),
 S('ActvBattlePassScore__BattlePassScore（主表）'),
 TH('字段','活动内容ID','是否开启','积分获取方式','购买礼包','奖励组','可以购买等级'),
 B('引用','ContentID','1=开启','ActvScoreTask.id','Pack(高级/至尊)','BattlePassScoreReward.Group','1=可钻石买级'),
 B('本期值','新ContentID','1','世界杯任务组','高级$14.99/至尊$29.99','奖励组号','1'),
 S('ActvBattlePassScore__BattlePassScoreReward（每级三轨奖励）'),
 TH('字段','编号','BD_组','等级','积分需求','免费奖励','高级奖励','至尊奖励','升级钻石价格'),
 B('说明','行号','奖励组','1~30','每级阈值','RewardID','RewardID','RewardID','跳级钻石价'),
 H('五、界面交互'),
 B('UIBattlePass.prefab','','复用，仅换皮；三轨进度条+领取+解锁购买入口','[客户端处理]','读上述配置；Text key 见本地化'),
 H('六、美术需求（占位）'),
 B('🔧 BP界面','世界杯主题进度条/三轨背景/解锁按钮','待美术','占位','待定来源'),
 B('🔧 BP外显奖励','世界杯主题航迹/头像框/拉拉队皮肤碎片图标','待美术','占位','待定'),
 H('七、本地化'),
 B('','见「活动本地化」页签 BP段',' ',' ',' '),
]

# ============ 开发配置需求 ============
TABS['开发配置需求'] = [
 T('▌开发配置需求'),
 TH('模块','ActvType','复用源ContentID','新ContentID','新ActvOnline ID','TimeController','备注'),
 B('主转盘','10','🔧 待选历史实例(1001-1023)','🔧 待分配','🔧 待分配','🔧 新TC行','三层保底现成'),
 B('比赛竞猜(逐场)','Pack(无ActvType)','—','每场一组PackID','逐场ActvOnline','逐场绝对时间','按赛程逐场建,决赛可多组'),
 B('付费BP','22','🔧 待选历史实例','🔧 待分配','🔧 待分配','🔧 新TC行','三轨BP'),
 H('全局变量 / 道具'),
 TH('类型','名称/ID','用途','值/说明'),
 B('道具','世界杯金券 Item 1140(预留)','唯一闭环货币','UseActivityID 绑转盘ContentID；ID 待最终确认(114x段)'),
 B('道具','竞猜票(免费记录用)','免费预测记录载体','$0礼包发放,借领取日志记录所选结果(也可直接用金券Item做0元礼包)'),
 B('必检','ActvOnline.MailID','除ActvType=8外必填','101109(漏配服务端静默吞奖励)'),
 B('必检','跨服 TimeCycle','CrossServerRank=1 必 TT=1','见 reference_x3_timecycle'),
]

# ============ 数值设计·道具价值 ============
TABS['数值设计·道具价值'] = [
 T('▌数值设计 · 金券经济 & 礼包价值（草案·待评审）'),
 H('一、世界杯金券 经济闭环'),
 TH('环节','口径','金券量(草案)','说明'),
 B('产出·免费预测','每日1场猜对','+5 /场','全程约可猜~26场,猜对率假设50%→约65金券≈6.5抽'),
 B('产出·付费$4.99','礼包必得+猜对加送','30必得 +20猜对','猜对共50≈5抽'),
 B('产出·付费$9.99','礼包必得+猜对加送','70必得 +50猜对','猜对共120≈12抽'),
 B('产出·付费$19.99','礼包必得+猜对加送','160必得 +120猜对','猜对共280≈28抽'),
 B('产出·BP','三轨奖励累计','🔧 待配','全周期产出,付费轨显著高于免费'),
 B('消耗·转盘单抽','单抽消耗','-10','每日另有免费抽次数'),
 B('消耗·转盘十连','10连消耗','-100','保底至少1稀有'),
 H('二、礼包价值(ROI 落档·待数值核)'),
 TH('档位','售价$','金券必得','搭配养成资源','目标ROI'),
 B('助威礼包·低','4.99','30','少量资源','落历史$4.99档ROI区间'),
 B('助威礼包·中','9.99','70','中量资源+少量钻石','落$9.99档'),
 B('助威礼包·高','19.99','160','大量资源+钻石','落$19.99档'),
 B('BP高级','14.99','—','三轨高级奖励解锁','订阅价值'),
 B('BP至尊','29.99','—','三轨至尊+皮肤碎片','深度款'),
 B('注','ROI公式=礼包总钻石价值÷(售价×500)；落模板同档区间(见 reference_x3_config_library)','','',''),
 H('三、转盘奖池结构(草案)'),
 TH('层级','内容','权重思路','保底'),
 B('超级大奖','足球宝贝皮肤·爱莉希雅(Hero1040限定)+限定英雄','极低权重','累计200抽必出'),
 B('稀有','养成资源+钻石','中权重','十连至少1'),
 B('普通','活动资源/少量金券','高权重','—'),
 B('累抽阶梯','5/20/40/70/120/200抽宝箱','—','额外固定奖励'),
]

# ============ 运营SOP·结算 ============
TABS['运营SOP·结算'] = [
 T('▌运营 SOP · 竞猜结算（每日例行 · 零后端）'),
 H('一、为什么是运营动作而非后端功能'),
 B('','付费竞猜=买礼包,订单日志天然记录玩家所押结果;免费竞猜=$0领取,领取日志记录所选结果。'),
 B('','两者都有日志,结算只需:拿赛果→查日志命中买对/猜对玩家→批量发bonus金券。无需服务端单独存预测,零程序开发。'),
 H('二、每日结算流程'),
 B('1','赛后获取真实赛果','[运营]','运营自行从资讯网站获取(游戏内不做赛果展示)'),
 B('2','查命中玩家','[运营]','按 server+场次PackID(=押注结果) 查购买/领取日志,筛出押中赛果的玩家'),
 B('3','计算bonus金券','[运营]','按礼包档位($4.99/$9.99/$19.99/免费)对应加送量(见数值页签)'),
 B('4','批量发券+结算邮件','[运营]','用现成 bulk-mail 工具(reference_x3_igame_mail_import)发金券+结算邮件,邮件写明赛果+你的预测+发放量'),
 B('5','未中玩家','[运营]','礼包内容已即时到账(保底),无需额外处理'),
 H('三、风险与兜底'),
 B('漏发/延迟','凌晨场次次日结算','[运营]','结算邮件文案说明"赛果次日到账";建立每日结算checklist防漏场'),
 B('录错赛果','人工核对双源','[运营]','两个资讯源交叉确认后再发;错发用GM/邮件追回或补发'),
 B('争议','以官方赛果为准','[运营]','文案声明以FIFA官方最终结果为准(含点球/加时)'),
 H('四、待固化'),
 B('🔧','结算查询SQL模板','','上线前用ai-to-sql写好"按server+PackID查购买/领取玩家"的模板,沉淀进KB复用'),
]

# ============ 活动本地化 ============
TABS['活动本地化'] = [
 T('▌活动本地化（Text Key 清单）'),
 TH('Text_Key','模块','中文','英文','说明'),
 B('TXT_WC_Main_Title','通用','绿茵狂热·世界杯','World Cup Frenzy','活动主标题'),
 B('TXT_WC_Wheel_Title','转盘','冠军之轮','Champion\'s Spin','转盘活动名'),
 B('TXT_WC_Wheel_Main','转盘','旋转冠军之轮，赢取世界杯传奇！','Spin for World Cup legends!','主标题'),
 B('TXT_WC_Wheel_Btn1','转盘','单抽','Draw x1','按钮'),
 B('TXT_WC_Wheel_Btn10','转盘','十连抽','Draw x10','按钮'),
 B('TXT_WC_Oracle_Title','竞猜','胜负预言','Match Oracle','竞猜活动名'),
 B('TXT_WC_Oracle_Main','竞猜','预言绿茵胜负，赢取冠军金券！','Predict the match, win gold tickets!','主标题'),
 B('TXT_WC_Oracle_Free','竞猜','免费预测','Free Pick','按钮'),
 B('TXT_WC_Oracle_Buy','竞猜','购买助威礼包','Buy Cheer Pack','按钮'),
 B('TXT_WC_Oracle_Locked','竞猜','本场已锁定预测','Pick locked for this match','防对冲提示'),
 B('TXT_WC_Pass_Title','BP','冠军通行证','Champion Pass','BP活动名'),
 B('TXT_WC_Pass_Main','BP','解锁冠军通行证，赛季奖励全收！','Unlock the Champion Pass!','主标题'),
 B('TXT_WC_Ticket_Name','道具','世界杯金券','World Cup Gold Ticket','金券道具名'),
 B('TXT_WC_Settle_Mail','邮件','胜负预言结算','Match Oracle Settlement','结算邮件标题'),
 B('注','其余 key 落地时按 TXT_{Table}_{Field}_{ID} 规则补全;走 x3-translation-automatic 扩10语','','',''),
]

# ============ 活动美术需求 ============
TABS['活动美术需求'] = [
 T('▌活动美术需求（皮肤来源/具体美需待定）'),
 TH('类型','内容','参考/规格','状态','备注'),
 B('🔥英雄皮肤','足球宝贝皮肤·爱莉希雅(转盘超级大奖)','基础英雄爱莉希雅Hero1040;FBX模型+Spine+立绘+卡片+头像;Hero__HeroSkin DK_字段','待美术出图','基础英雄已定爱莉希雅(性感World Cup babe);详见「足球宝贝设计稿」'),
 B('转盘','DK_转盘图片/指针/底部背景 世界杯主题','沿用转盘UI尺寸','待定',''),
 B('竞猜','比赛卡片/队徽/结果礼包图/胜负预言主视觉','沿用礼包/活动页','待定',''),
 B('BP','三轨进度条/背景/解锁按钮/世界杯外显(航迹/头像框)','沿用BP UI','待定',''),
 B('通用','活动主页banner/世界杯主视觉','活动banner尺寸','待定',''),
 B('图标','世界杯金券图标 DK','道具icon规格','待定',''),
 B('注','换皮必双参考(老图=格式锚+新图=元素锚);投放物优先搜现成资源,搜不到才新出;路径必验存在(reference_x3_art_resource_spec)','','',''),
]

# ============ 活动事件打点 ============
TABS['活动事件打点'] = [
 T('▌活动事件打点'),
 TH('事件ID','名称','触发条件','参数','说明'),
 B('🔧 evt_wc_wheel_draw','转盘抽奖','单抽/十连','次数/消耗金券/产出','转盘付费漏斗'),
 B('🔧 evt_wc_oracle_free','免费预测','领取免费竞猜票','场次/所选结果','免费参与率'),
 B('🔧 evt_wc_oracle_buy','购买助威礼包','买竞猜礼包','场次/结果/档位/金额','竞猜付费核心'),
 B('🔧 evt_wc_oracle_hit','竞猜命中','结算命中','场次/档位/发放金券','结算/猜中率'),
 B('🔧 evt_wc_pass_unlock','BP解锁','买高级/至尊','档位/金额','BP付费'),
 B('🔧 evt_wc_pass_levelup','BP升级','升级/钻石买级','等级/方式','BP深度'),
 B('注','打点用于复盘:竞猜参与率/付费转化/各档位ROI/转盘飞轮回收;字段待与数据对齐','','','',''),
]

# ============ 日志需求 ============
TABS['日志需求'] = [
 T('▌日志需求（结算依赖·必须可查）'),
 TH('日志类型','内容','频率','说明'),
 B('★竞猜购买日志','server+user+场次PackID(=押注结果)+金额+时间','实时','结算命中查询的核心依据,必须含PackID可反推所押结果'),
 B('★免费领取日志','server+user+场次+所选结果+时间','实时','免费预测记录,$0领取需落日志'),
 B('转盘抽奖日志','user+消耗金券+产出道具','实时','复盘飞轮/概率'),
 B('金券流水','user+产出/消耗来源+量','实时','金券经济健康度'),
 B('BP日志','user+升级/解锁/领取','实时','BP付费深度'),
 B('注','结算SOP直接吃 竞猜购买日志+免费领取日志,这两类是硬需求(无则无法结算)','','',''),
]

# ============ 验收Checklist ============
TABS['验收Checklist'] = [
 T('▌验收 Checklist'),
 TH('模块','编号','验收项','通过','不通过','备注'),
 B('转盘','W1','金券消耗/单抽十连数量正确','','',''),
 B('转盘','W2','超级大奖保底次数触发','','',''),
 B('转盘','W3','累抽阶梯5/20/40/70/120/200发奖','','',''),
 B('转盘','W4','每日免费抽生效','','',''),
 B('转盘','W5','超级大奖跑马灯','','',''),
 B('竞猜','O1','★防对冲:每场只能选一个结果,锁定其余','','','核心'),
 B('竞猜','O2','付费礼包必得金券(保底价值)','','',''),
 B('竞猜','O3','免费$0领取记录所选结果(日志可查)','','',''),
 B('竞猜','O4','开赛时间到锁盘下架','','',''),
 B('竞猜','O5','结算邮件含赛果+预测+发放金券','','',''),
 B('竞猜','O6','购买/领取日志含PackID可反推结果','','','结算硬依赖'),
 B('BP','P1','三轨(免费/高级/至尊)奖励正确','','',''),
 B('BP','P2','高级/至尊礼包解锁对应轨','','',''),
 B('BP','P3','钻石买等级生效','','',''),
 B('通用','G1','ActvOnline.MailID 已填(101109)','','','漏配吞奖励'),
 B('通用','G2','跨服活动TimeCycle TT=1','','',''),
 B('通用','G3','金券UseActivityID绑转盘ContentID','','',''),
 B('通用','G4','活动结束金券/未领奖回收邮件','','',''),
]

# ============ 变更记录 ============
TABS['变更记录'] = [
 T('▌变更记录'),
 TH('日期','版本','变更内容','作者'),
 B('2026-06-09','v0.1','初稿:飞轮+三模块(转盘/竞猜/BP)+零后端结算SOP+配套页签','Claude'),
 B('2026-06-09','v0.2','增量预估→历史ARPU实测值(尼罗$57.43/情人节$58.73/春节$47.57,不预估增量);新增排期甘特图','Claude'),
 B('2026-06-09','v0.3','格式重构:甘特图独立成页(列宽均匀)/总览正文归C列+列宽按表格重配/模块页正文列E加宽/全表格式重置防残留','Claude'),
 B('2026-06-09','v0.4','足球宝贝皮肤基础英雄定为爱莉希雅(Hero1040,传奇,D29-34招募可得);模块页正文归C列防窄挤','Claude'),
 B('','待办','足球宝贝具体美需出图(见设计稿) / ContentID·ActvOnline ID分配(建配置时定) / 结算SQL模板 / 打点字段对齐 / 草案数值待数值评审',''),
]

# ============ 足球宝贝设计稿 ============
TABS['足球宝贝设计稿'] = [
 T('▌足球宝贝皮肤设计稿 · 爱莉希雅'),
 H('一、基础信息'),
 B('基础英雄','','爱莉希雅 / Elysia（Hero 1040，品质4传奇）'),
 B('原型人设','','白毛大胸·吸血鬼猎人；银白长发、白皙肤、丰满身形、性感黑色高开衩长裙、持匕首'),
 B('D35可得','','招募UP池 开服D29-34 可抽（D35内，符合约束）'),
 B('皮肤主题','','世界杯·足球宝贝（性感拉拉队 / World Cup babe）'),
 B('获取途径','','世界杯幸运转盘「冠军之轮」超级大奖（限定）'),
 B('皮肤名(暂定)','','绿茵宝贝·爱莉希雅 / Pitch Diva Elysia'),
 H('二、原型资产（X3客户端·换皮参考源）'),
 TH('资产','客户端路径','用途'),
 B('立绘(FullLength)','Assets/Res/UI/Spirits/Role/FullLength/Role_F_40.png','★换装主参考(脸/发/身形锚)'),
 B('卡片(HeroCard)','Assets/Res/UI/Spirits/Role/HeroCard/Role_C_40.png','卡片图换皮参考'),
 B('头像(Portrait)','Assets/Res/UI/Spirits/Role/Character Portraits/Img_C_H_40.png','头像换皮参考'),
 B('Spine动画','Assets/Res/Spine/Role_Spine_40/（Role_F_40 atlas/skel/png）','动作骨骼换皮参考'),
 H('三、皮肤视觉概念（保留她本人 + 只换造型）'),
 B('★保留(身份锚)','','同脸、同银白长发、同白皙肤、同丰满身形、同卡通3D渲染风——必须一眼是爱莉希雅本人'),
 B('★替换(造型)','','黑长裙→性感拉拉队球衣：露脐无袖球衣(红白金队色+号码)+百褶啦啦裙+过膝条纹袜+运动鞋'),
 B('道具替换','','匕首→足球(夹在臂下)+彩色花球(pom-poms)；脸颊小国旗彩绘'),
 B('姿态','','活力自信的拉拉队应援姿势，全身站立'),
 B('视觉关键词','','绿茵球场、世界杯彩旗、纸屑庆典、阳光、青春性感、应援'),
 H('四、概念稿（GRFal 基于本人立绘换装生成）'),
 B('概念图','','C:\\ADHD_agent\\KB\\产出-本地化与美术\\X3\\足球宝贝爱莉希雅\\（GPT/gemini 各2张候选，选定后回填文件名）'),
 B('生成方式','','call_grfal generate_image + reference=Role_F_40.png(本人立绘)，保身份换造型；脚本 gen_soccer_baby.py'),
 B('说明','','此为方向概念稿，供美术外包对齐；最终交付需美术按下方清单出正式资产'),
 H('五、美术交付清单（按 Hero__HeroSkin DK 字段）'),
 TH('DK字段','资产类型','对标原型尺寸/规格','参考(老图格式锚)'),
 B('DK_Fullbody','立绘 PNG','对齐 Role_F_40.png 尺寸','Role_F_40.png'),
 B('DK_HeroCard','卡片图 PNG','对齐 Role_C_40.png','Role_C_40.png'),
 B('DK_Head','头像 PNG','对齐 Img_C_H_40.png','Img_C_H_40.png'),
 B('DK_Spine','Spine动画(atlas+skel+png)','对齐 Role_Spine_40 骨骼','Role_Spine_40/'),
 B('DK_Prefab','3D模型 FBX(如需)','对齐英雄外包模型','OutsourcingRes 对应族'),
 B('★换皮铁律','','双参考：老图(Role_F_40 等=格式/尺寸/结构锚) + 新概念图(=足球宝贝元素锚)；路径必验存在(reference_x3_art_resource_spec)'),
 H('六、配置落地（Hero__HeroSkin 表新增行）'),
 B('','','新增一行皮肤：HeroID=1040；皮肤名Text key；DK_Fullbody/HeroCard/Head/Spine/Prefab 指向新出资产；Regained 转钻补偿字段沿用同类皮肤(重复获得转钻，见 reference_x3_monetization_mechanics)'),
 H('七、本地化'),
 TH('Text_Key','中文','英文','说明'),
 B('TXT_HeroSkin_Name_1040WC','绿茵宝贝·爱莉希雅','Pitch Diva Elysia','皮肤名(暂定)'),
 B('TXT_HeroSkin_Desc_1040WC','绿茵场上最耀眼的应援宝贝，为冠军而欢呼！','The dazzling diva cheering for the champions!','皮肤描述(暂定)'),
]

# ---------- 写入 + 格式 ----------
def colspan(rows):
    return max((len(r[1]) for r in rows), default=1)

def build_format_reqs(gid, rows, ncol, tab=''):
    reqs=[]
    nrow=len(rows)
    # 先把整片区域格式重置为白底/常规(清旧版残留的标题绿/染色)
    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":0,"endRowIndex":80,"startColumnIndex":0,"endColumnIndex":26},
        "cell":{"userEnteredFormat":{"backgroundColor":{"red":1,"green":1,"blue":1},"textFormat":{"bold":False,"fontSize":10,"foregroundColor":{"red":0,"green":0,"blue":0}},"wrapStrategy":"OVERFLOW_CELL","horizontalAlignment":"LEFT"}},
        "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.wrapStrategy,userEnteredFormat.horizontalAlignment"}})
    # 全表默认字号10
    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":0,"endRowIndex":nrow,"startColumnIndex":0,"endColumnIndex":ncol},
        "cell":{"userEnteredFormat":{"textFormat":{"fontSize":10},"verticalAlignment":"TOP"}},
        "fields":"userEnteredFormat.textFormat.fontSize,userEnteredFormat.verticalAlignment"}})
    # C列起自动换行
    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":0,"endRowIndex":nrow,"startColumnIndex":2,"endColumnIndex":ncol},
        "cell":{"userEnteredFormat":{"wrapStrategy":"WRAP"}},"fields":"userEnteredFormat.wrapStrategy"}})
    for i,(st,cells) in enumerate(rows):
        rng={"sheetId":gid,"startRowIndex":i,"endRowIndex":i+1,"startColumnIndex":0,"endColumnIndex":ncol}
        if st=='T':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"backgroundColor":_c(GREEN),"textFormat":{"bold":True,"fontSize":16}}},
                "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})
            reqs.append({"updateDimensionProperties":{"range":{"sheetId":gid,"dimension":"ROWS","startIndex":i,"endIndex":i+1},
                "properties":{"pixelSize":40},"fields":"pixelSize"}})
        elif st=='H':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"textFormat":{"bold":True,"fontSize":11}}},
                "fields":"userEnteredFormat.textFormat"}})
        elif st=='TH':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"backgroundColor":_c(THEAD),"textFormat":{"bold":True,"fontSize":10}}},
                "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})
        elif st=='S':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"textFormat":{"bold":True,"fontSize":10}}},
                "fields":"userEnteredFormat.textFormat"}})
        elif st=='GH':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"backgroundColor":_c(THEAD),"textFormat":{"bold":True,"fontSize":9},"horizontalAlignment":"CENTER"}},
                "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.horizontalAlignment"}})
        elif st=='G':
            # 首列模块名加粗；■格染甘特条色
            reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":i,"endRowIndex":i+1,"startColumnIndex":0,"endColumnIndex":1},
                "cell":{"userEnteredFormat":{"textFormat":{"bold":True,"fontSize":9}}},"fields":"userEnteredFormat.textFormat"}})
            BAR=(0.36,0.65,0.92)
            for j,val in enumerate(cells):
                if j>=1 and str(val).strip()=='■':
                    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":i,"endRowIndex":i+1,"startColumnIndex":j,"endColumnIndex":j+1},
                        "cell":{"userEnteredFormat":{"backgroundColor":_c(BAR),"horizontalAlignment":"CENTER","textFormat":{"foregroundColor":_c(BAR)}}},
                        "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.horizontalAlignment,userEnteredFormat.textFormat.foregroundColor"}})
            continue
        # 单元格token着色
        for j,val in enumerate(cells):
            v=str(val).strip()
            for tok,col in CELL_TOKENS.items():
                if v==tok or (tok in v and tok in ('需程序','换美术','纯复用')):
                    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":i,"endRowIndex":i+1,"startColumnIndex":j,"endColumnIndex":j+1},
                        "cell":{"userEnteredFormat":{"backgroundColor":_c(col)}},"fields":"userEnteredFormat.backgroundColor"}})
                    break
    # 列宽（按页签类型选）
    if tab in TAB_WIDTHS:
        widths=TAB_WIDTHS[tab]
    elif tab.startswith('模块'):
        widths=MODULE_W
    else:
        widths=TABLE_W
    for ci,w in enumerate(widths[:max(ncol,len(widths))]):
        reqs.append({"updateDimensionProperties":{"range":{"sheetId":gid,"dimension":"COLUMNS","startIndex":ci,"endIndex":ci+1},
            "properties":{"pixelSize":w},"fields":"pixelSize"}})
    return reqs

def main():
    gidmap={t:g for g,t,*_ in gs.list_tabs(SID)}
    for tab,rows in TABS.items():
        # 模块页:把"标签+正文"两列行的正文移到C列(防B列窄挤),保持与列阶梯正文(E)分层
        if tab.startswith('模块'):
            rows=[(st,([c[0],'',c[1]] if st=='B' and len(c)==2 else c)) for st,c in rows]
        gid=gidmap.get(tab)
        if gid is None:
            # 自动建缺失页签(如新增甘特图页),插在第2位
            gs._call(['sheets','spreadsheets','batchUpdate','--params',json.dumps({'spreadsheetId':SID})],
                jb={"requests":[{"addSheet":{"properties":{"title":tab,"index":1}}}]})
            gidmap={t:g for g,t,*_ in gs.list_tabs(SID)}
            gid=gidmap.get(tab)
        cs=colspan(rows)
        vals=[list(cells)+['']*(cs-len(cells)) for st,cells in rows]
        gs.ensure_grid(SID,tab,rows=max(len(vals)+5,30),cols=14)
        # 清旧内容(防版本变短残留)
        gs.update_range(SID,tab,'A1:Z80',[['']*26 for _ in range(80)])
        ok=gs.update_range(SID,tab,'A1',vals)
        reqs=build_format_reqs(gid,rows,cs,tab)
        rc,text,err=gs._call(['sheets','spreadsheets','batchUpdate','--params',json.dumps({'spreadsheetId':SID})],jb={"requests":reqs})
        print(f'{tab}: rows={len(vals)} write={ok} fmt_rc={rc} {"ERR" if chr(34)+"error"+chr(34) in text else "ok"}')

if __name__=='__main__':
    main()
