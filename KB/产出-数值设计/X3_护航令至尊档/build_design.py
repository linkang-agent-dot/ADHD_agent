# -*- coding: utf-8 -*-
"""X3《护航令·至尊档（简易战令3档化）改造案》—— GSheet 构建脚本（建表→写内容→套格式）。
复用世界杯 build_design.py 的渲染引擎。可复跑：内容用 update_range 覆盖写。
首次运行自动新建 GSheet 并把 SID 打印出来；之后把 SID 填回 SID 变量即可复跑覆盖。
样式token：T(绿16大标题) H(粗11二级) TH(浅蓝灰表头) S(粗10小计) B(正文10)；
单元格token：[客户端]→粉 [配置]→米黄 [服务端]→橙 [复用]→灰。
"""
import sys, json
sys.path.insert(0, r'C:\ADHD_agent\scripts')
import gsheet_utils as gs

SID = '1BP_qkISn-YfDDsYoBMQLD9-lLRQebYlz1rFjmOmpgLE'  # 留空=新建；新建后把打印的 SID 填这里可复跑覆盖
TITLE = 'X3 护航令·至尊档（简易战令3档化）改造案'

# ---------- 颜色 ----------
GREEN=(0.557,0.878,0.522); THEAD=(0.85,0.9,0.95); PEACH=(0.988,0.922,0.80)
PINK=(1,0.6,1); ORANGE=(1,0.6,0); LBLUE=(0.812,0.886,1.0); GRAY=(0.851,0.851,0.851)
def _c(rgb): return {"red":rgb[0],"green":rgb[1],"blue":rgb[2]}
CELL_TOKENS={'[客户端]':PINK,'[配置]':PEACH,'[服务端]':ORANGE,'[复用]':GRAY}

TABLE_W=[150,130,200,210,300,130,110,110,110,110,110]
TAB_WIDTHS={
 '总览':[180,150,180,160,150,150],
 '改造方案':[80,80,150,90,470,130],
 '配置&服务端':[210,150,360,260,150],
}

def T(*c): return ('T', list(c))
def H(*c): return ('H', list(c))
def TH(*c): return ('TH', list(c))
def S(*c): return ('S', list(c))
def B(*c): return ('B', list(c))

TABS = {}

# ============ 总览 ============
TABS['总览'] = [
 T('▌X3 护航令·至尊档（简易战令3档化）改造案'),
 H('〇、一句话'),
 B('案子','','给简易战令（ActvType=11，现"免費/至尊"双列2档）加第3档，升级成"免费/进阶/至尊"三列，并把简易战令改成数据驱动可配N档。要改客户端prefab+脚本 & 服务端。'),
 B('本质','','现2档双列形态 → 三列形态。三档UI在积分BP（ActvType=22「世界盃通行證」）里已是现成的，作视觉/交互参照。★砍掉积分BP带的"钻石升级"。'),
 B('目标','','深度付费——现BP付费天花板低（$9.99/$14.99），加更高价"至尊"档（≈2x）抬ARPPU上限；免费/进阶现状不动，对大盘付费率/留存零冲击。'),
 H('一、决策锁定（用户拍板）'),
 B('策划案落点','','独立新 GSheet（本表）'),
 B('至尊档价值模型','','仅"更高价的第3条奖励轨"——不送等级、不双倍免费奖励；superset（买至尊含进阶轨）'),
 B('改造范围','','简易战令 ActvType=11 改成数据驱动可配N档（一劳永逸，老BP零影响）'),
 B('命名','','免费 / 进阶 / 至尊（现"免費"沿用；现付费"至尊"→改名"进阶"；新增顶档=至尊）'),
 B('❌ 排除','','不要"钻石升级"（积分BP BattlePassScore.UpgradePrice 花钻跳级）'),
 T('二、现状：X3 有两套 BattlePass'),
 TH('','简易战令 ActvType=11（本案对象）','积分战令 ActvType=22/33（不动）'),
 B('配置表','ActvBattlePass + BattlePassReward（只有 FreeReward/PackReward 两列=2档）','ActvBattlePassScore（FreeReward/AdvanceReward/SuperReward 三列=3档）+UpgradePrice钻石升级'),
 B('客户端','UIActvBattlePass.BattlePassItem —— prefab 写死2轨','数据驱动；3档UI已实现（世界盃通行證）'),
 B('服务端','ActivityMeta.BattlePass.cs —— 免费/付费两分支硬编码','ActivityMeta.BattlePassScore.cs —— 位标志引擎 Free=1/Advance=2/Super=4，加档≈零代码'),
 B('档位区分','靠不同列（FreeReward列 vs PackReward列）','位标志 purchased & rewardType'),
 T('三、改造对象：现有2档简易BP实例'),
 TH('ActvOnline','名称','主标题','付费包/价格','奖励组','任务'),
 B('101102','BP-新手主线','海盗猎人的赏金','130002 / $14.99','102（34级·带英雄spine）','新手进度412'),
 B('101110','BP-情报循环','猎杀时刻','130003 / $9.99','100','情报410'),
 B('101104','BP-登录循环','登录好礼','130004 / $9.99','101','登录321'),
 B('101120','BP-新手英雄-兔女郎','会员签到好礼','130015 / $3.99','107','登录321'),
 B('注','','老BP不配第2包+不填SuperReward = 保持2档零回归；首期在哪个实例开至尊档由运营按期配置。',''),
 T('四、改动面总览'),
 TH('层','文件','改动','量'),
 B('客户端','UIActvBattlePass.prefab + BattlePassItem/RwdItem/Pop + proto','加第3轨容器+脚本3档分支+购买弹窗进阶/至尊双入口','~200-300行'),
 B('服务端','ActivityMeta.BattlePass.cs','2分支硬编码→位标志引擎（抄 BattlePassScore.cs）','中'),
 B('配置','BattlePass.Pack 管道化 + BattlePassReward 加 SuperReward 列 + 新增至尊礼包/奖励','schema改动','低'),
 T('五、模块目录'),
 B('改造方案','','主模块：包装层/设计目的/玩法/规则说明/界面交互'),
 B('配置&服务端','','配置表schema改动 + 服务端代码改动清单 + proto'),
 B('数值设计','','三档价格/奖励范式'),
 B('本地化','','Text key 清单'),
 B('美术需求','','至尊轨视觉/购买入口'),
 B('验收Checklist','','验收项'),
]

# ============ 改造方案（主模块）============
TABS['改造方案'] = [
 T('▌改造方案 · 多档通行证（简易战令3档化）'),
 H('〇、包装层'),
 B('','','三档（沿用现界面"档位列头"叫法，对齐积分BP模板）：'),
 B('免费','','FreeReward，所有玩家 ← 现界面列头"免費"不变'),
 B('进阶','','AdvanceReward，付费 ← 现界面列头"至尊"改名为"进阶"（现 $9.99/$14.99 付费档落这里）'),
 B('至尊','','SuperReward，新增·更高价顶档 ← 新增列'),
 B('备注','','每个BP实例的主题名/主标题仍按活动自身（猎杀时刻/海盗猎人的赏金…），不强加统一品牌名。'),
 H('一、设计目的'),
 B('1.1 核心目的','','现简易BP只有免费+付费2档，付费天花板低（$9.99–14.99）。加"至尊"档=给愿付更多的玩家一条更高价值轨，抬高BP线 ARPPU 上限。'),
 B('1.2 付费点','','至尊护航礼包（更高价，≈2x）'),
 B('1.3 目标人群','','已买进阶档、愿意继续加价的中大R'),
 B('1.4 因果假设','','现付费档天花板 $14.99 → 加 $19.99–24.99 至尊档 → 已付费用户中部分升档 → BP线 ARPPU 提升'),
 B('1.5 副作用控制','','至尊=纯增量轨；免费/进阶档奖励与解锁逻辑完全不变；老BP不配至尊包即维持2档（零回归）'),
 H('二、玩法说明'),
 B('','','做任务攒积分→升级→每级可领 免费/进阶/至尊 三档奖励。至尊档需购买至尊礼包解锁，解锁后同时享 进阶轨+至尊轨（superset，至尊买家不丢进阶轨）。'),
 H('三、规则说明（核心=数据驱动N档改造）'),
 B('3.1','','基础设定','',''),
 B('','3.1.1','改造对象','[服务端]','简易战令 ActvType=11，由"免费/付费两分支硬编码"→数据驱动多档'),
 B('','3.1.2','位标志引擎','[服务端]','对齐积分BP BattlePassScore：Free=1 / Advance=2 / Super=4（…可扩展）'),
 B('3.2','','档数由配置决定','',''),
 B('','3.2.1','Pack管道化','[配置]','BattlePass.Pack 由单包 → 管道列表 [进阶包 ｜ 至尊包]'),
 B('','3.2.2','index→tier','[服务端]','按 Pack 列表 index 映射档位：index0→Advance(进阶)位、index1→Super(至尊)位、…'),
 B('','3.2.3','档数','[配置]','配1包=2档（老BP行为不变）；配2包=3档；未来加列即N档'),
 B('3.3','','至尊解锁','',''),
 B('','3.3.1','买至尊包','[服务端]','purchased |= (Advance | Super) 双位（superset，至尊买家含进阶轨）'),
 B('','3.3.2','买进阶包','[服务端]','purchased |= Advance 单位'),
 B('3.4','','领奖校验（沿用积分BP三层）','',''),
 B('','3.4.1','档位已购','[服务端]','purchased & rewardType（免费档恒可领）'),
 B('','3.4.2','达成','[服务端]','subItem.finished（任务/等级达成）'),
 B('','3.4.3','未领过','[服务端]','receivedIds & rewardType（位标志去重）'),
 B('3.5','','兼容铁律','[配置]','老BP（101102/101104/101110/101120）不配至尊包+不填 SuperReward = 保持2档，零回归'),
 B('3.6','','❌ 排除','','不含"钻石升级"（BattlePassScore.UpgradePrice 花钻跳级），至尊档纯靠买礼包解锁'),
 H('四、界面交互（据真实截图 Pictures\\X3验收\\BP新增档位\\ 写实）'),
 S('现状界面（简易BP UIActvBattlePass.prefab）'),
 B('','①','顶部活动标题栏「酒館活動」+ 右侧英雄 spine 立绘（大图）','[客户端]',''),
 B('','②','副标题文案 + 价格按钮（$9.99/$14.99/$3.99）+ 右上折扣%徽章','[客户端]',''),
 B('','③','奖励区=双列轨道，列头 免費 ｜ 至尊（右列带锁=未购）','[客户端]',''),
 B('','④','中间纵向等级条（1/2/3…黄线连接），横向滑动翻等级','[客户端]',''),
 B('','⑤','奖励槽 BattlePassRwdItem 三态：锁(mGoLock)/可领(mGoEffect)/已领(mGoReceive)','[客户端]',''),
 S('目标形态参考（积分BP 世界盃通行證 = 现成3列）'),
 B('','','三列轨道并排+列头+等級列在左+顶部「一鍵領取」+「X段/0/3000」进度条。三档UI已实现，作改造参照。','[客户端]',''),
 S('改动逐项（双列→三列：免费/进阶/至尊）'),
 TH('#','文件','改动','标注',''),
 B('1','UIActvBattlePass.prefab','BattlePassItem 内 Free/Pack 两轨 → 加第3轨容器 Super(至尊)，改为按配置档数动态生成轨道；列头 至尊→进阶、新增 至尊 列头+锁态','[客户端]',''),
 B('2','Auto_UIActvBattlePass.BattlePassItem.cs','prefab改后重新生成，新增 mChildGroupSuper 绑定','[客户端]',''),
 B('3','UIActvBattlePass.BattlePassItem.cs','加 mChildGroupSuper/mSuperEndowItems + BindSuperItemData；RefreshView 读 SuperReward 渲染第3轨','[客户端]',''),
 B('4','BattlePassRwdItem.cs','枚举 BattlePassRwdItemType 加 Super；RefreshView(锁/可领/已领)+ClaimBattlePassReward 加 Super 分支(未购→弹购买)','[客户端]',''),
 B('5','UIActvBattlePassPop.cs','FromType 加至尊档；顶部购买区支持 进阶+至尊 两个购买入口(价格/折扣分别读各自Pack)','[客户端]',''),
 B('6','proto activityBattlePass','ActivityBattlePassData.purchased 位标志扩展支持第3档(Super位)','[客户端]',''),
 S('逐元素状态机（第3轨"至尊"）'),
 B('','未购至尊','至尊列整列显 mGoLock，点击任意至尊奖励槽→弹购买弹窗(至尊档)','[客户端]',''),
 B('','已购至尊','superset：进阶+至尊列按"等级达成→mGoEffect可领 / 已领→mGoReceive"','[客户端]',''),
 B('','一键领取','(可选,模板有) 一次领完所有已解锁档已达成未领奖励','[客户端]',''),
 B('','Text key','列头/按钮走自动key管线（见本地化页）','[客户端]',''),
]

# ============ 配置&服务端 ============
TABS['配置&服务端'] = [
 T('▌配置表 schema 改动 + 服务端代码改动'),
 H('一、配置表 schema 改动'),
 TH('表','改动','说明','标注'),
 B('ActvBattlePass__BattlePass.tsv','Pack 列：int → 管道串 进阶包｜至尊包','第8列。空第2段=无至尊档=2档','[配置]'),
 B('ActvBattlePass__BattlePassReward.tsv','新增 SuperReward 列（cs/int，引用 Reward）','现有 ID/Group/Count/FreeReward/PackReward 之后追加','[配置]'),
 B('Pack__Pack.tsv','新增至尊礼包行','礼包类型13(BP专用UI)沿用；价格≈2×进阶档','[配置]'),
 B('Reward__*.tsv','新增至尊轨 RewardID 系列','具体ID建配置时扫tsv分配防撞','[配置]'),
 B('注','','X3导入只认tsv(改tsv不碰xlsx)；2026-06-04起xlsx-tsv-gate强制两边一致，落地时xlsx+tsv同改成一致再commit',''),
 H('二、BattlePassReward 表头 4 行 schema（程序对接）'),
 TH('','ID','Group','Count','FreeReward','PackReward','SuperReward(新增)'),
 B('类型(cs)','int','int','int','int','int','int'),
 B('引用','','关联BattlePass','任务计数','Reward.id','Reward.id','Reward.id'),
 B('中文','编号','BD_组','任务计数','免费奖励','进阶奖励','至尊奖励'),
 B('英文','ID','Group','Count','FreeReward','PackReward','SuperReward'),
 H('三、服务端代码改动'),
 TH('文件','改动',''),
 B('ActivityMeta.BattlePass.cs','2分支硬编码→位标志引擎（抄 ActivityMeta.BattlePassScore.cs 现成范式）：Pack列表 index→tier位；至尊包置 Advance|Super 双位；领奖/解锁/校验数据驱动','[服务端]'),
 B('proto activityBattlePass（client Assets\\Scripts\\Protos\\activityBattlePass.cs）','ActivityBattlePassData.purchased 支持多位；rewardType 枚举加第3档','[服务端]'),
 B('GiftMeta.cs（礼包购买回调）','至尊礼包→ReceiveActivityBattlePassReward(..., Super)；已支持任意档位，基本零改','[复用]'),
 B('范式来源','BattlePassScore.cs 已有完整可抄：位标志 purchased / 三层领奖校验 / ReceiveAll foreach 遍历 realRewardTypes',''),
]

# ============ 数值设计 ============
TABS['数值设计'] = [
 T('▌数值设计'),
 H('一、三档价格与奖励范式'),
 TH('档','价格','奖励轨'),
 B('免费','$0','现 FreeReward 不变'),
 B('进阶','沿用现价 $9.99 / $14.99','现 PackReward 不变（现界面"至尊"列改名"进阶"）'),
 B('至尊','≈2× → $19.99 / $24.99','至尊买家=进阶轨+至尊轨(superset)；至尊轨与进阶轨同槽位结构，品质/数量上提（蓝→紫，量×1.5–2）'),
 H('二、约束'),
 B('superset','','买至尊=解锁进阶+至尊两轨（不丢进阶）'),
 B('❌ 钻石升级','','不引入（不要 UpgradePrice 花钻跳级）'),
 B('不送等级/不双倍','','至尊档=纯第3条更高价奖励轨'),
 H('三、待建配置时定'),
 B('至尊包 IAP id','','按价格档分配（建配置时查 PackPrice 表）'),
 B('至尊轨 RewardID','','扫 tsv 分配防撞；与进阶轨同结构、量级上提'),
]

# ============ 本地化 ============
TABS['本地化'] = [
 T('▌本地化（Text keys）'),
 B('说明','','X3配置文本走自动key管线：单元格字面值客户端不读，proto拼 TXT_{表}_{字段}_{行ID}；新增文本必须同commit把自动key写进Text表，补全16语种，否则非中文客户端显空/中文母版。'),
 TH('Key','中文','英文(占位)','说明'),
 B('TXT_…_FreePass','免费','Free','列头（现"免費"沿用）'),
 B('TXT_…_AdvancePass','进阶','Advanced','列头（现"至尊"改名"进阶"）'),
 B('TXT_…_SuperPass','至尊','Ultimate','列头（新增）'),
 B('TXT_Pack_Name_{至尊包ID}','（按活动主题）至尊礼包名','','新增至尊礼包'),
 B('TXT_Pack_Desc_{至尊包ID}','至尊礼包描述','','新增至尊礼包'),
]

# ============ 美术需求 ============
TABS['美术需求'] = [
 T('▌美术需求'),
 TH('类型','内容','参考','状态'),
 B('至尊轨视觉','轨道底/锁态/已领态/特效','复用现有 免费/进阶 槽样式，配至尊金/紫色调','待美术'),
 B('至尊购买按钮','主界面"至尊"档购买入口','复用现购买按钮','待美术'),
 B('至尊礼包banner','购买弹窗至尊档展示','复用现弹窗布局','待美术'),
 B('列头图标','至尊列头标签+锁图标','复用现"至尊"列头样式换文案','待美术'),
]

# ============ 组件&节点改造 ============
TABS['组件&节点改造'] = [
 T('▌UI 组件素材 + 节点改造方案（拆UI做组件依据）'),
 B('说明','','简易战令奖励板=九宫格sprite程序拼,无整块底图。加第3档=在行模板里复制Pack单元→Super单元、Title里复制标签,三列重分x/宽。下表=战令界面真实UI素材(已透明,client\\Assets\\Res\\UI\\Spirits\\)。'),
 H('一、战令专属真实素材（可换皮）'),
 TH('节点','真实PNG(Spirits\\ 下)','尺寸','说明'),
 B('列头标签底·免費','Activity\\ui_battlepass_bg_1.png','36×84','九宫格,横向拉伸'),
 B('列头标签底·至尊','Activity\\ui_battlepass_bg_2.png','36×84','复制做"进阶/至尊"列头底'),
 B('列头装饰副本','Activity\\ui_battlepass_bg_3/bg_4.png','248×168','至尊标签装饰/翻转'),
 B('等级菱形·已达成','Activity\\ui_battlepass_point_1.png','88×88','金菱形'),
 B('等级菱形·未达成','Activity\\ui_battlepass_point_2.png','76×76','灰菱形'),
 B('行级锁','Activity\\img_battlepass_icon_lock.png','28×36',''),
 B('活动大背景','ActivityImg_Download\\img_battlepass_bg_1.png','1080×944','船/海场景(非奖励板)'),
 H('二、通用复用图（九宫格/跨界面，换皮慎动）'),
 TH('节点','真实PNG','说明'),
 B('奖励格底框','HeroFavor\\img_hgd_bg6.png','40×44九宫格,全格通用(借英雄好感)'),
 B('折扣徽章/×2角标','Pack\\img_gift_bg_Discount.png','156×156,礼包系统通用'),
 B('进度竖轴 底/填充','WorldTend\\img_TXDS_pd_5.png / pd_1.png','九宫格(借世界趋势)'),
 B('已领勾✓','WorldTend\\img_TXDS_icon_gou.png','跨界面通用'),
 B('格内锁','Memory\\img_remember_icon_lock.png','借纪念册'),
 B('购买按钮','prefab UIBtnPurchase(通用)','非裸sprite,按钮底图在该通用prefab'),
 H('三、节点改造方案（prefab 层·保持节点不变·改位置+新增）'),
 B('行模板结构','','每行=UIItemTemplate(1012×167)：Free单元(x=-309,宽394) + Pack单元(x=+197,宽618,HorizontalLayoutGroup) + Level菱形 + SliderShort进度轴'),
 B('改法·奖励轨','[客户端]','行模板里复制 Pack单元→Super单元(同挂 BattlePassRwdItem),三单元 x/宽重分：免费(压窄1格)/进阶(1格)/至尊(2格);Pack是HorizontalLayoutGroup加格自动排版'),
 B('改法·列头','[客户端]','Title 下复制 Pack标签→进阶/至尊标签(换底图ui_battlepass_bg_2+换文案+锁),调三标签x'),
 B('改法·购买','[客户端]','顶部加第2个 UIBtnPurchase(进阶+至尊各一),折扣徽章各自一个'),
 B('奖励格三态','','BattlePassRwdItem: Lock(隐藏切换)/Receive(✓)/Effect(DK粒子DK_Select_FX_9无PNG)/Double(×2角标);槽底img_hgd_bg6常驻'),
]

# ============ 打点&日志 ============
TABS['打点&日志'] = [
 T('▌打点 & 日志'),
 B('结论','','本案=系统档位改造（简易BP 2档→3档），★复用现有简易BP既有链路，无新增埋点/日志需求。'),
 H('一、打点（事件）'),
 TH('事件','是否新增','说明'),
 B('至尊档购买','否（复用）','至尊档=IAP订单，走现有 BP 礼包购买回调 GiftMeta.cs，订单自带记录；沿用现简易BP购买打点'),
 B('至尊轨领奖','否（复用）','复用现 BP 领奖打点（领奖走同一 ReceiveActivityBattlePassReward，按 rewardType 区分档位）'),
 B('档位曝光/点击','否（复用）','沿用现 BP 界面打点；如需单独看至尊档点击率，可后续在客户端加，非本期必需'),
 H('二、日志'),
 TH('日志','是否新增','说明'),
 B('购买/发奖日志','否（复用）','至尊包 IAP 订单 + 发奖走现有 BP 日志链路，无新增'),
 H('三、数据分析口径（无需新埋点）'),
 B('升档转化/收入','','新增「至尊包 IAP id」即可从现有订单数据（ods_user_order 按 iap_id 聚合）算至尊档付费人数/收入/对比进阶档升档率，验证 ARPPU 抬升假设；不需新埋点。'),
]

# ============ 验收Checklist ============
TABS['验收Checklist'] = [
 T('▌验收 Checklist'),
 TH('模块','编号','验收项','通过','备注'),
 B('配置','1','BattlePass.Pack 支持管道串[进阶包｜至尊包]，配2包正确出3档','',''),
 B('配置','2','BattlePassReward 新增 SuperReward 列，老行不填=2档不回归','',''),
 B('服务端','3','买至尊包后 purchased 置 Advance|Super 双位（superset）','',''),
 B('服务端','4','领奖三层校验：未购档不可领/未达成不可领/已领不可重复','',''),
 B('服务端','5','老BP(101102等)行为完全不变（零回归）','',''),
 B('客户端','6','界面正确显示3列：免费/进阶/至尊；列头"至尊"已改"进阶"','',''),
 B('客户端','7','至尊列未购显锁、点击弹购买；已购按达成态正确渲染','',''),
 B('客户端','8','购买弹窗 进阶+至尊 两个购买入口，价格/折扣各自正确','',''),
 B('客户端','9','一键领取（若做）只领已解锁档','',''),
 B('数值','10','至尊档价格≈2x；至尊轨奖励品质/数量上提','',''),
 B('本地化','11','免费/进阶/至尊 列头 + 至尊礼包名/描述 自动key已入Text表，16语种补全','',''),
 B('排除','12','确认无"钻石升级"入口（不要 UpgradePrice）','',''),
]

# ---------- 写入 + 格式（复用世界杯引擎）----------
def colspan(rows):
    return max((len(r[1]) for r in rows), default=1)

def build_format_reqs(gid, rows, ncol, tab=''):
    reqs=[]; nrow=len(rows)
    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":0,"endRowIndex":120,"startColumnIndex":0,"endColumnIndex":26},
        "cell":{"userEnteredFormat":{"backgroundColor":{"red":1,"green":1,"blue":1},"textFormat":{"bold":False,"fontSize":10,"foregroundColor":{"red":0,"green":0,"blue":0}},"wrapStrategy":"OVERFLOW_CELL","horizontalAlignment":"LEFT"}},
        "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat,userEnteredFormat.wrapStrategy,userEnteredFormat.horizontalAlignment"}})
    reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":0,"endRowIndex":nrow,"startColumnIndex":0,"endColumnIndex":ncol},
        "cell":{"userEnteredFormat":{"textFormat":{"fontSize":10},"verticalAlignment":"TOP"}},
        "fields":"userEnteredFormat.textFormat.fontSize,userEnteredFormat.verticalAlignment"}})
    for i,(st,cells) in enumerate(rows):
        rng={"sheetId":gid,"startRowIndex":i,"endRowIndex":i+1,"startColumnIndex":0,"endColumnIndex":ncol}
        if st=='T':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"backgroundColor":_c(GREEN),"textFormat":{"bold":True,"fontSize":16}}},
                "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})
            reqs.append({"updateDimensionProperties":{"range":{"sheetId":gid,"dimension":"ROWS","startIndex":i,"endIndex":i+1},
                "properties":{"pixelSize":38},"fields":"pixelSize"}})
        elif st=='H':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"textFormat":{"bold":True,"fontSize":11}}},"fields":"userEnteredFormat.textFormat"}})
        elif st=='TH':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"backgroundColor":_c(THEAD),"textFormat":{"bold":True,"fontSize":10}}},
                "fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})
        elif st=='S':
            reqs.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":{"textFormat":{"bold":True,"fontSize":10}}},"fields":"userEnteredFormat.textFormat"}})
        for j,val in enumerate(cells):
            v=str(val).strip()
            if v in CELL_TOKENS:
                reqs.append({"repeatCell":{"range":{"sheetId":gid,"startRowIndex":i,"endRowIndex":i+1,"startColumnIndex":j,"endColumnIndex":j+1},
                    "cell":{"userEnteredFormat":{"backgroundColor":_c(CELL_TOKENS[v])}},"fields":"userEnteredFormat.backgroundColor"}})
    widths=TAB_WIDTHS.get(tab, TABLE_W)
    for ci,w in enumerate(widths[:max(ncol,len(widths))]):
        reqs.append({"updateDimensionProperties":{"range":{"sheetId":gid,"dimension":"COLUMNS","startIndex":ci,"endIndex":ci+1},
            "properties":{"pixelSize":w},"fields":"pixelSize"}})
    return reqs

def main():
    global SID
    tab_order=list(TABS.keys())
    if not SID:
        SID,url=gs.create_spreadsheet(TITLE, tabs=tab_order)
        print('NEW SID =', SID)
        print('URL =', url)
        if not SID:
            print('!! 新建失败'); return
    gidmap={t:g for g,t,*_ in gs.list_tabs(SID)}
    for tab,rows in TABS.items():
        gid=gidmap.get(tab)
        if gid is None:
            gs._call(['sheets','spreadsheets','batchUpdate','--params',json.dumps({'spreadsheetId':SID})],
                jb={"requests":[{"addSheet":{"properties":{"title":tab}}}]})
            gidmap={t:g for g,t,*_ in gs.list_tabs(SID)}; gid=gidmap.get(tab)
        cs=colspan(rows)
        vals=[list(cells)+['']*(cs-len(cells)) for st,cells in rows]
        gs.ensure_grid(SID,tab,rows=max(len(vals)+5,30),cols=14)
        gs.update_range(SID,tab,'A1:Z120',[['']*26 for _ in range(120)])
        ok=gs.update_range(SID,tab,'A1',vals)
        reqs=build_format_reqs(gid,rows,cs,tab)
        rc,text,err=gs._call(['sheets','spreadsheets','batchUpdate','--params',json.dumps({'spreadsheetId':SID})],jb={"requests":reqs})
        print(f'{tab}: rows={len(vals)} write={ok} fmt_rc={rc} {"ERR" if chr(34)+"error"+chr(34) in text else "ok"}')
    print('DONE SID =', SID)

if __name__=='__main__':
    main()
