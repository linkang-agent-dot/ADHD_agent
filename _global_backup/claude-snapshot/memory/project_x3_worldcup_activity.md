---
name: project-x3-worldcup-activity
description: X3 世界杯活动系列策划案设计定稿（飞轮+三模块）+ 抽奖/BP/竞猜可复用资产盘点
metadata: 
  node_type: memory
  type: project
  originSessionId: 8472eced-268e-4dc5-8a24-08559cc68e5c
---

X3 世界杯活动系列策划案，2026-06-09 立项。侧重**深度付费**。

## 🎁 竞猜奖励包分 8强/4强 改造(2026-07-08·✅已落地 origin/dev·跟上活动必读)
> **★铁律:跟上竞猜活动(QF/SF轮)时,奖励包要分 8强 和 4强 两套配,且 Pack 备注名带「8强」/「4强」区分**(如 `WC竞猜池-8强-FRA-$9.99` / `WC竞猜池-4强-框自选-$9.99`)——agent 扫 Pack 表能一眼分清哪套哪轮,别混。
- **不新增 Pack,改旧 ID**:被淘汰队(R16出局的 CAN/PAR/BRA/MEX/POR/USA/EGY/COL 等)pack ID 闲置→复用当 4强 配置。
- **现役档位结构(2026-07-08追证)**:每队4档共用奖励组——免费→291335 / $4.99→291101 / **$9.99→291330(发道具1148自选头像框宝箱)** / **$19.99→291399(发道具1149自选表情宝箱)**。另 291332/333/334="临时·待换晋级之路框80348/世界之巅框/表情"占位组。
- **① 8强(QF)·按国直给**:改现役8个QF队 $9.99奖励组→直发该国**新荣耀之路框(80348-55)**、$19.99→直发该国**新角色表情道具(表情落地后的154xx id)**。直发本体不套宝箱。
- **② 4强(SF)·复用淘汰队pack**:改成自选宝箱——$9.99→**框自选宝箱(新8框+老48框)**、$19.99→**表情自选宝箱(新8+老48)**。
- **依赖**:QF $19.99挂新表情→**排在表情落地sub-agent之后**(要它出的新表情道具id);都动gdconfig别并发。
- **落地后必补本段**:实改了哪些pack id/奖励组/新建自选宝箱id/commit/build#。荣耀之路框已落(framecfg10081-88/道具80348-55/宝箱1153/奖池291203·build#1624·i18n#1627);表情已全落地(gdconfig commit e7fe3df:Emoticons348-355/解锁道具15468-75/四强表情自选宝箱1154/奖池291204/i18n)。
> **✅✅ 全套已落地 origin/dev(2026-07-08·gdconfig commit链 b1fe20e配置合并→b60adb3 8强→c8bbede合远端X3NEW-1546→1e41a08 4强)**:
> **道具→国家映射(接管必备·别再挖)**:框道具 80348法/80349挪/80350摩/80351英/80352比/80353西/80354阿/80355瑞;表情道具 15468阿/15469比/15470英/15471西/15472法/15473摩/15474挪/15475瑞。8队队号 ARG2/BEL5/ENG18/ESP19/FRA20/MAR30/NOR33/SUI42。
> **① 8强(QF)按国直给**:新建16直给组——框直给291340-347/表情直给291360-367(每组=券+钻+VIP+该国道具·非宝箱)。重指16包c14:894[队号]2→框组、894[队号]3→表情组;c3全加"8强"(WC竞猜池-8强-{国}-{档})。映射见commit b60adb3(如ARG包894022→组291340→框80354)。
> **② 4强(SF)自选宝箱**:新建2自选组——291350框自选(券40+钻5000+VIP50+**1153新8框+1148老48框**双宝箱)/291351表情自选(券80+钻1万+VIP100+**1154+1149**双宝箱)。**复用8个淘汰队闲置包当容器**(ALG/AUS/AUT/BIH/CAN/CIV/COD/CPV=队号1/3/4/6/8/9/10/12)重配成8个QF队4强版:容器包 894012/013→ARG,894032/033→BEL,894042/043→ENG,894062/063→ESP,894082/083→FRA,894092/093→MAR,894102/103→NOR,894122/123→SUI;每包 c14→自选组、c26+c28→该QF队徽章DK(DK_WC_TeamPanel_/DK_WC_Badge_)、c36→队名、c3→"WC竞猜池-4强-{队}-{档}"。**徽章名字一次到位·SF对阵出来直接挑对应队包deploy·无需再改**。脚本 scratchpad/qf_pack_reconfig.py + sf_pack_reconfig.py。
> **★配置搬dev的正确姿势(踩坑总结·接管必读)**:WC框+表情配置原只在dev_festival。选择性搬到dev**别cherry-pick**(tsv driver base=commit^远离dev·静默丢行·实测丢~1item+Reward乱)、也**别全量merge dev_festival→dev**(会带上hero-handbook等11个不该发的commit)。正确=**确定性手工application**:dev各表 + 仅WC的新ID行(纯新ID·不改dev现有行)·脚本 scratchpad/wc_only_merge.py。Reward两边并行append撞seq(dev的X3NEW-1546也在加行)→**重建=远端全量+我的行重编seq**(RewardID不变·seq只是行号·Pack.c14引用RewardID不受影响)。每步跑row-id审计(丢0撞0)。
> **🐛 表情落地3个踩坑修复(2026-07-08·测试暴露·接管必读)**:
> ①**GIF黑底**:`_mp4_to_emote_gif.py` 用 `optimize=True` 存GIF→PIL重映射调色板把透明索引255改成253→`transparency(253)≠background(255)`→游戏按background索引渲染透明区=黑底。**修=optimize=False**(保 transparency==background==255·对齐老WC表情)·8个WC_SF_*.bytes重生成(client MR!683已合dev)·脚本已回写optimize=False。
> ②**表情宝箱缺专属图标**:表情自选宝箱1154之前复用老通用图`DK_WC_EmoteChest`(框宝箱1153有专属`DK_WC_SF_AvatarFrameChest`)。**修=新出`WC_SF_EmoteChest.png`(128·紫金四强款+笑脸表情气泡徽章·x3-media生成)+DK双写`DK_WC_SF_EmoteChest`(client MR!684)+gdconfig item1154 c21改指该DK(dev e4d2638)**。图标列=Item表**c21**。
> ③**买礼包给老宝箱/名字没改=220跑旧配置(非配置bug)**:220服19:27部署·但含我配置的build#1646是19:35才完成→220拉的旧镜像→pack还指老组291330(老宝箱)。**判据=对比服务器LastDeployTime vs 配置build完成时间**(kadmin query_app + Jenkins build api)。修=kadmin `deploy_app(['default_PlayService_220','default_MapService_221'],tag='dev')`重部署拉新镜像(⚠️别带110/111校验服·harness会拦共享服务器操作)。⚠️即使配置刷新,220**客户端包**要重打AB含新DK/新.bytes才显示对(纯git合了但旧客户端包还是旧图)。
> **🐛 表情落地4-5坑续(2026-07-08~09)**:
> ④**i18n表情侧只有cn/en·缺14语言**:e7fe3df落地时只补cn/en,框侧另走172aae6补了16语言、表情侧漏了→非中英语言下表情宝箱/道具/Emoticons名空白。**修**:补表情侧26key(1154宝箱Name/Desc·15468-75道具Name/Desc·348-355 Emoticons)×14语言。⚠️**撞名坑**:落地的en把国家名丢了只留角色(如`[Go Alicia!]`)→同角色不同国队撞名(ARG/SUI都爱莉希雅·FRA/BEL赛米拉·ENG/NOR霍普金斯·ESP/MAR克利欧)→**必须国家·角色都保留**(对齐cn`{国}·{角色}加油`)才能区分。术语:国家加油抄老key `_15420~467`/`_300~347` 全语言,角色名用英雄官方译。全量审计脚本 `x3-translation-automatic/scripts/i18n_leak_audit.py --grep 世界杯`(0 leak/0空/0撞名才过)。commit a49a11f。
> ⑤**新加client资源(png/DK)在游戏里"没生效"·纯AB没重建**:Unity Play/打包客户端读**AB包**,新merge的asset(如表情宝箱`WC_SF_EmoteChest.png`·MR!684)+改的item图标config(1154 c21→新DK)**没烘进旧AB**→显示旧图/回退。**症状=只新加的那个不对、老的(已在AB)都正常**。**判据**:DK桥验解析对(`client.py invoke TFW.DisplayKeyExtension.ToDisplayKeyAssetPath`)+ProtoGen `Item.bytes` grep到新DK字符串→数据全对,就是AB没重建。**修**:①合dev走正式构建出包(AB自动含) ②本地`Tools/Project Builder/AssetBundle/Build Asset Bundles`重打 ③切直读模式(开关没搜到)。**别再翻配置/DK**(那层没问题)。⚠️改ProtoGen `.bytes`文件+Refresh不够,Play模式配置开局载入内存·要stop/play重进才重载·且若读AB还得重打AB。
> **✅ 表情 client 已落地(2026-07-08·commit 1aedacf4822·origin/dev_festival已验)**:每国2个DK——动图`DK_WC_SF_{码}`→`client/Assets/Res/UI/Gif/WC_SF_{码}.bytes`(160透明GIF·非LFS)+静态icon`DK_icon_global_WC_SF_{码}`→`client/Assets/Res/UI/Spirits/Emoticons/Icon/icon_global_WC_SF_{码}.png`(256 sprite·LFS)。Display_Emoticons追加16(去DK_前缀·guid读meta·exportCode0)+Path_Emoticons 140→156(整体str.lower重排防两交替家族DK_WC_SF/DK_icon_global非单调被编辑器静默丢·KB铁律)。落地脚本`scratchpad/land_emote_dk.py`。⚠️提交时只add自己34文件,client仓当时有一大批`RoleF*_mask.png.meta`的guid churn(切分支带出·别提交见KB)。
> **✅ 客户端头像框 DK 已确认完整(2026-07-08 复核·此前误报已澄清)**:8国框 Display_Personalise=1/Path_Personalise=3(key+value.key+objPath)/png在树上——**全部注册正确**。⚠️**教训**:先前"框DK=0条缺口"是**误报**,根因=用 `git show <ref>:file | grep <DK>` 查 .asset **不可靠**(连确定存在的 DK_WC_ARG 都返回0·疑编码/pager),错判成缺。**查client DK真实状态必用 `git grep -c "<DK>" <ref> -- <file>`**(KB `reference_x3_client_resources` line173 四格矩阵法),别用 git show|grep。

## 🏆 16强竞猜准备(2026-07-03·待用户拍档位/排期)
- **清单HTML**=`KB\产出-数值设计\X3_世界杯\世界杯16强竞猜_部署清单.html`(生成器`_gen_16强清单.py`可复跑·队伍/时间变改它重跑)。**ESPN真实R16对阵(8场)**：M1加拿大vs摩洛哥7/4 17:00Z/M2巴拉圭vs法国7/4 21:00Z/M3巴西vs挪威7/5 20:00Z/M4墨西哥vs英格兰7/6 00:00Z/M5葡萄牙vs西班牙7/6 19:00Z/M6美国vs比利时7/7 00:00Z/**M7澳埃胜vs哥加胜(TBD)**7/7 16:00Z/**M8瑞士vs阿佛胜(TBD)**7/7 20:00Z(后2场等R32 seq14-16·7/4打完定队)。
- **✅M1-M6已部署(2026-07-03·prod·24实例单号13942-13965)**：用**新建的 `~\.claude\skills\igame-x3-activity-deploy\deploy_r16.py --go`**(6场硬编码·cfg=102920+(N-1)*4·4档·**start=7/3 10:00 UTC=北京18:00·用户定**·end=各场开球-10min·**83服=老55+新28合一payload**·内置double-check)。单号:M1加摩13942-945/M2巴法13946-949/M3巴挪13950-953/M4墨英13954-957/M5葡西13958-961/M6美比13962-965。**档位=4档**(用户默认没改)。
- **★R16复用R32 cfg 不用先撤回残留(2026-07-03实证)**：R16目标cfg 102920-943上有R32老实例(status5但endTime 6/28-7/1已过)→R16 start 7/3 与它们**时间不重叠**→deploy_r16双check(status2/5+时间重叠)**自动放行**·残留在自己窗口外无害。**省掉"先撤回R32"这步**(memory早前写的撤回非必须)。⚠️deploy_r16**不动wc_dashboard_data.json**(保R32 seq14-16的7/4结算)。
- **✅M7/M8已补(2026-07-04·单号13975-13982·R16全8场齐)**：R32末3场结果=埃及点球胜澳/阿根廷胜佛/哥伦比亚胜加→**ESPN真实R16对阵=M7阿根廷vs埃及(cfg102944-947·13975-978)/M8瑞士vs哥伦比亚(cfg102948-951·13979-982)**。deploy_r16.py已加M7/M8+**`--seq 7,8`过滤**(只发指定场·避免重发M1-6被double-check拦)。
- **🔴★bracket绝不能按占位文字推·必等ESPN出真实对阵(2026-07-04踩坑幸好核了)**：R32没打完时ESPN显示占位"Round of 32 14/15/16 Winner"·我按字面推M7=seq14胜(埃及)vs seq16胜(哥伦比亚)/M8=瑞士vs seq15胜(阿根廷)→**全错**！R32打完后ESPN真实解析=M7阿根廷vs埃及/M8瑞士vs哥伦比亚(占位序号↔实际bracket位不是我想的线性映射)。**教训:淘汰赛下一轮对阵一律等ESPN把占位换成真实队名再配·别自己推晋级树**。

## 🔴🔴 淘汰赛下一轮结算=礼包id跨轮复用·必按下注时间窗隔离(2026-07-06·R16结算踩坑·接管必读)
- **根因**：R16/QF/SF 竞猜的 customParam 礼包=**同一套894xxx(按队·跨轮复用)**。同一队(如摩洛哥894300)在R32和R16都可能被押→`ods_user_asset reason_sub_id`只有礼包id没有轮次/cfg(asset表activity_id列空)→**winners_of按礼包id查会把上一轮老下注也算进来→重复发奖**。
- **解法**：按**下注时间窗起点`settle_from`过滤**(partition_date>=settle_from)隔离本轮。生成器`_gen_发奖详情.py`已改**config驱动**:`SETTLE_FROM=_dash.get("settle_from","2026-06-26")`(4处SQL的partition_date都用它)。**每轮结算前改wc_dashboard_data.json两处**:①`schedule`换成本轮对阵(key/round/a_code/b_code/kickoff_utc/lock_utc·R16 key前缀R16-) ②`settle_from`=本轮竞猜开盘日(R32=2026-06-26/**R16=2026-07-03**/QF=R16打完那天…)。R32 schedule备份在`wc_dashboard_data.R32backup.json`·生成器备份`_gen_发奖详情.R32backup.py`。
- **为何R16用7/3够**:R16的M1-M4队伍(CAN/MAR/PAR/FRA/BRA/NOR/MEX/ENG)其R32场都在≤7/2·R16开盘7/3→partition_date>=7/3干净隔离。⚠️但**QF/SF会更棘手**:EGY/ARG/COL既在R32末(7/4)又在R16 M7/M8(7/7)·跨轮队伍时间窗更近·settle_from要卡到本轮竞猜真实开盘时刻(可能要用created_at时间戳而非partition_date日粒度)。
- **R16对阵(ESPN真实)**:M1加拿大0-3摩洛哥/M2巴拉圭0-1法国/M3巴西1-2挪威(爆冷)/M4墨西哥2-3英格兰=M1-4已打(7/5-6)·M5葡西/M6美比/M7阿埃/M8瑞哥=7/7。
- **✅R16 M1-M4已结算+发邮件(2026-07-06·settle_from=7/3隔离生效·counts正常4065/6965/1467/6061笔)**:mailId **4732041(加摩)/4732043(巴法)/4732044(巴挪)/4732045(墨英)** status2**待放行**;GM加分5块`GM纯命令_合并_part1-5.txt`(18558条)待粘。R16 8场竞猜32实例全live无缺。
- **✅R16 M5/M6已结算+发邮件(2026-07-07)**:M5 **葡萄牙0-1西班牙·西班牙胜**(6865人猜中·mailId **4733593**)/M6 **美国1-4比利时·比利时胜**(4777人·mailId **4733594**)·均status2**待放行**;GM加分合并3块`GM纯命令_合并_part1-3.txt`(11642条·各≤49万字符)待粘。⚠️M2 PARvFRA今天被生成器连带重生成产物但**已在7/6发过(4732043)别重发**——今天只发M5/M6两场。content json今天现转(生成器7/6只出了M1-M4的content json)→**已根治**:content json生成补进生成器(154行旁·`{k:{title,body}}`格式·复用match_mail)·以后每场自动出`content_{key}.json`无需手转。
- **⏳R16 M7/M8待7/7晚打完结算(7/8做)**:M7阿根廷vs埃及(北京7/7 24:00开球)/M8瑞士vs哥伦比亚(北京7/8 04:00)·生成器自动跳未赛·打完重跑`_gen_发奖详情.py`即出M7/M8产物(会连带重生成M1-M6·**只发M7/M8别重发前6场**)。
- **✅R16 M7/M8已结算+发邮件(2026-07-08)**:M7 **阿根廷3-2埃及·阿根廷胜**(ESPN Full Time,9198笔/9148人,命中率93.6%,mailId **4735000** status2待放行)/M8 **瑞士0-0(点球4-3)哥伦比亚·瑞士胜**(ESPN After Penalties,4767笔/4757人,命中率48.4%,mailId **4735001** status2待放行)。M1-M6笔数(4065/6965/1467/6061/6865/4777)与7/6-7/7旧批完全一致=settle_from=7/3隔离生效无翻倍,**未重发M1-M6**。GM加分本轮2场合并**4块**`GM纯命令_合并_part1-4.txt`(13965条=9198+4767·各≤49万字符)待粘。`_verify_发奖发送.py 林康`复核8场全部✅已发全(发件箱receiverCount==奖励csv行数)。**R16全8场结算完毕**,下一轮=QF(8强,见下方⏳QF状态段)。
- **✅QF1已结算+发邮件(2026-07-10)**:**摩洛哥0-2法国·法国胜**(ESPN FT·WebFetch拉)。总竞猜4028人·猜中3362人/3378笔·命中率83.5%(付费档仅16笔=QF昨晚才上窗口短·正常)。**mailId 4737745** receiverCount=3378 status2**待放行**;GM加分`GM纯命令_QF-MARvFRA.txt`(3378条·38万字符单块)待粘。**settle_from已切2026-07-09**(QF开盘日·隔离R16老下注·法摩两队R16都被押过);dashboard `settled`=R16八场。**生成器补了settled跳过**(脚注设计一直没实现·已修:_settled集合内场次直接跳,防错误settle_from重查覆盖存档)。QF2-4(BELvESP 7/10/ENGvNOR 7/11/SUIvARG 7/12)待赛后同流程:ESPN出结果→跑生成器→发邮件+GM;**发完把场key加进dashboard settled**。
- **✅QF2已结算+发邮件(2026-07-11)**:**比利时1-2西班牙·西班牙胜**(ESPN FT)。总竞猜7362人·猜中5926人/5946笔·命中率80.5%。**mailId 4740340** recv=5946 status2**待放行**(登记后outbox延迟~1分钟才可查·QF1也这样·别急着重发);GM加分5946条超49万拆2块=`GM纯命令_合并_part1-2.txt`(用`_chunk_gm_commands.py QF-BELvESP`)待粘。**QF1邮件已确认放行真发**(4737745自动拆分450人/封全status1)。剩QF3 ENGvNOR/QF4 SUIvARG(7/11-12打)。
- **✅QF3/QF4已结算+发邮件(2026-07-13)**:QF3 **英格兰2-1挪威**(8423人·猜中4751人/4766笔·56.4%·**mailId 4743594**)/QF4 **瑞士1-3阿根廷**(8436人·猜中7120人/7144笔·84.4%·**mailId 4743595**)·均status2待放行。GM合并3块`GM纯命令_合并_part1-3.txt`(11910条)待粘。**QF全4场结算完毕**·dashboard settled已含QF全部。
- **✅决赛(FINAL)冠军外显已配置(2026-07-15·dev)**:法国SF淘汰→决赛3候选队ESP/ARG/ENG(冠军会是这三家之一)。**奖励**:$19.99=**大力神冠军框(GOLD)+绿茵之王头衔**(通用·三队一样)/$9.99=**国家冠军框**(西斗牛红金/阿GOAT/英都铎玫瑰·按国直给)/绿茵星辉款弃用。**gdconfig(commit 3724fae2)**:框framecfg10089-92+道具80356-59(图标=框DK自身·防御+100)/头衔PlayerTitle107「绿茵之王」+道具82007(大图DK_WC_title_champion·小图复用DK_icon_global_WCtitle)/奖励组291370-372国框+291373通用(GOLD框+头衔)/重指3队**8强包**(已结算复用:ESP894192/193·ARG894022/023·ENG894182/183)→c14+c3标决赛/i18n cn/en(多语言待补)。**client MR!756**:4框256+头衔横幅752x192(WC_title_champion·MiscIcons注册)+DK双写。脚本 scratchpad/final_config.py+final_client.py。**★头衔配置链keypoint**:PlayerTitle表(9列:名/大图DK/buff/重复补偿/获取/小图DK/品质/排序)+发放道具Item ItemType=18 UseEffectParam={头衔ID}|{秒·-1永久}+头衔大图DK注册在**Path/Display_MiscIcons**(不是Personalise)。**待办**:决赛对阵定后(SF2 ARG vs ENG出结果·决赛7/19)部署决赛竞猜(deploy_wc.py加FINAL排期·或新deploy脚本·3队路由);i18n补14语言;美术终版图在KB决赛外显/(ESP_v2/ENG_v2重做过·法国弃)。
- **✅半决赛(SF)已上线prod(2026-07-13·ark 14094-14101·83服·status2)**:ESPN真实对阵 SF1**西班牙vs法国**(7/14 19:00UTC锁18:50·cfg102968-971)/SF2**阿根廷vs英格兰**(7/15 19:00UTC锁18:50·cfg102972-975)。**★SF包路由(与QF不同·接管keypoint)**:tier0免费/tier1$4.99=原队包base(队)+t(共用组291335/291101没动过·徽章对);tier2$9.99/tier3$19.99=**4强容器包**+t(=淘汰队ID重配的4强版·c14→自选组291350框/291351表情·徽章已设成QF队)。部署脚本`deploy_sf.py`(igame-x3-activity-deploy skill·dry-run默认·83服)。SF结算时settle_from仍=07-09没问题?⚠️**要切07-13**(SF部署日):FRA/ESP/ARG/ENG四队在QF窗口(7/9-12)都被押过·SF结算前必把settle_from改2026-07-13隔离QF老下注(同轮次隔离铁律)。

## 🎨 半决赛/决赛外显美术生产中(2026-07-06·用户拍板做全)
- **🔴 正名+方向升级(2026-07-07·用户拍板·接管必读)**：①**这套每队框=「荣耀之路头像框」**(游戏内正式名)·**不是**通用里程碑款(晋级之路框80348/世界之巅框80349是另一档·全员共用不分国家)。②**用户否掉"单国旗裹框"公式化路线·要每队走真国家特色**(国家元素长成框结构本身·非贴旗):摩洛哥=zellige几何马赛克+马蹄拱/法国=Art Nouveau锻铁+高卢雄鸡/挪威=维京绳结+极光/英格兰=三狮纹章/西班牙=阿尔罕布拉金饰+弗拉门戈/比利时=霍塔新艺术+红魔。骨架统一(圆框+四强金标+半写实厚涂)·皮=各国纹样。③**6国+待补2国(M7/M8胜者)完整prompt草稿**=`半决赛决赛外显\_SF框_国家特色美需prompt_草稿.md`(⚠️当初4框没留prompt=接手白手起家坑·本文件补上·定稿升决策记录)。④**MAR national打样跑着**(task20260707-173314-9e3d·gemini·输出`WC_SF_Frame_MAR_national.png`不覆盖旧formulaic版·锚=既有FRA框format+MAR国旗配色)·用户认可"国家化"味道后按队铺FRA/NOR/ENG/ESP/BEL。⚠️**旧的4框(FRA/MAR/NOR/ENG是formulaic单旗版)大概率被national版取代**·待用户选定风格再定FINAL/废弃。⚠️x3-media在本会话曾被`media_api_gate`钩子拦·靠往`~\.claude\scripts\media_api_gate_allow.txt`加session_id解(会话级白名单·非全局关钩子)。⑤**✅荣耀之路框六国全定稿(2026-07-07)**:FRA洛可可/NOR圆形维京/MAR zellige/ENG纹章盾/BEL霍塔铁框/ESP巴洛克·各长各的结实框体·中心圆窗·无模板。**FINAL/废弃 + 落地待办见目录说明`荣耀之路头像框_国家特色版\_目录说明.md`；方法论(反模板铁律·结实框体≠松散·圆窗spec·gemini缩窗校准·预览/量窗工具)全在`_SF框_国家特色美需prompt_草稿.md`**。⚠️血泪主线:①同骨架换纹样=模板(首批10框全废)②溶成松散藤蔓=丢框体丑(FRA藤蔓废)→取中=结实框体+各国不同框风格。**待补M7/M8明晚定队后同配方补最后2国**(改`_批量框task生成器.py`JOBS·prompt圆窗顶80%·过verify_transparency)。工具:`_头像预览合成.py`(套头像看游戏内感)/`_量圆窗.py`(卡窗口一致)。
- **产出目录**=`KB\产出-本地化与美术\X3\世界杯竞猜界面\半决赛决赛外显\`。走 **x3-media uiframe类型·gemini·media-worker异步**。设计口径(用户定走A版):
  - **半决赛四强专属框(旧=单国旗裹框·已被上条national方向取代)**=每支进8强队一个·`WC_SF_Frame_{code}.png`·参考锚=`flags_48/{code}.png`(真旗)+`头像框_48_FINAL/Img_Player_AvatarFrame_WC_{code}.png`(现成48队框)+`参考头像框/`概念图。**4已定队(法/摩/挪/英)formulaic版已出**(在半决赛决赛外显/·待选风格);另4队(M5-8胜)7/7后补。
  - **里程碑款待做**:晋级之路框(80348通用)+世界之巅框(80349)+世界之巅表情(15748)·风格锚=`铭牌_世界之巅\WC_Title_PeakOfWorld_FINAL.png`(金+翠绿+奖杯月桂)·**用户要一起做·待4队框审完接着派**。
- 落地待办(图审完):建Item/Frame/Emote行+DK注册(X3 dev DK注册即用不过包·见世界之巅铭牌段)。

## ✅ 8强(QF)已上线 prod(2026-07-09)
- **ESPN真实赛程(WebFetch拉·curl拉不到ESPN被墙但WebFetch走别的通道能拉)**:QF1摩洛哥vs法国(7/9 20:00UTC)/QF2比利时vs西班牙(7/10 19:00)/QF3英格兰vs挪威(7/11 21:00)/QF4瑞士vs阿根廷(7/12 01:00)。锁盘=开球-10min。
- **部署**:dashboard加QF为N=9-12→cfg 102952-967(避R16的102920-951);`deploy_wc.py "9-12" prod --go`→16实例(4场×4档)·**83服**·ark单号14051-14066·status2异步激活(正常,同R32/R16)。customParam=base(队)+档,走master的**8强按国直给**奖励组。
- **🔴🔴服务器坑(2026-07-09踩·血泪)**:`deploy_wc.py` 的 SERVERS 硬编码是**过时55服(1170-1970)**,但WC扩服后现役是**83服(55旧+28新1980-2250)**——首次用deploy_wc.py发QF只上了55服漏28新服,用户当场发现全撤回。**已修deploy_wc.py SERVERS补新服range(1980,2251,10)=83**。**铁律:上竞猜到prod前,必查线上现存WC活动(如R16 cfg 102944)的真实servers[]作ground truth对齐服数**(别信脚本硬编码的旧列表)。查法=iGame prod activity/list 取某cfg的servers。deploy_r16.py的SERVERS(OLD+NEW=83)是对的·deploy_wc.py之前没同步扩服。
- **前置(用户确认已做)**:master+版本已发(WC全套配置8强直给/4强/框表情/i18n 16语言 已在master·gdconfig+client都发版构建过);dev→qa发版也做了。
- **修了deploy_wc.py bug**:活动名硬编码"32强"→改按 m['round'] 映射(R32/R16/QF/SF/3RD/FINAL→32强/16强/8强/半决赛/季军/决赛),以后各轮名字自动对。
- **周卡(109101)**:beta 220已GM开(activityId 7727287086351384576·2027-01窗口);prod按用户"先把比赛上完"暂缓。
- ⚠️**GMPrintServerActivityByCfgId查单服活动不可靠**(周卡/竞猜都报not existed但实际部署成功)→验证查Mongo `ServerActivity`表 或看 deployserveractivity返回。

## ⏳ 8强(QF)状态(2026-07-06·2场已定待上·已被上方取代)
ESPN QF 4场·因R16 M1-4已打→**2场已定对阵未部署**:QF1**法国vs摩洛哥**(7/9·M2胜vs M1胜)/QF3**挪威vs英格兰**(7/11·M3胜vs M4胜);QF2(M5胜vsM6胜)/QF4(M7胜vsM8胜)待7/7 R16打完。部署=做`deploy_qf.py`(复用deploy_r16结构·**cfg基号换102952**避开活跃R16 M5-M8的102936-951·QF1=102952-955/QF3=102960-963)。**待用户确认是否上**。

## 🧰 结算发放两个工具(2026-07-03固化)
- **邮件直发**：奖励券走 `~\.claude\skills\igame-skill\scripts\igame_mail_send.py --csv 奖励_{key}.csv --content content_{key}.json --remark 事由 --send`(content JSON=从生成器`多语言邮件_{key}.csv`转`{lang码:{title,body}}`)。发后status2须iGame后台放行·真实mailId按remark去发件箱查·详见[[reference_x3_igame_mail_import]]。
- **GM纯命令切块(★上限=50万非5M·2026-07-03实测纠正)**：iGame GM输入框**实测只能粘 ≤500,000 字符/次**(5M是错的)。BP加分`GM纯命令_{key}.txt`多场合并/切块走 `KB\产出-数值设计\X3_世界杯\_chunk_gm_commands.py [--limit N] <场key...>`(**默认490,000/块留余量**·按行边界不切断命令·产出`GM纯命令_合并_partN.txt`逐块粘)。今日3场19572条=切**5块**(part1-4各~49万+part5~25万)。

## 🔴 结算工具 bp_snowflakes 只读第1页坑(2026-07-03·扩服后暴露·已修)
- **症状**：`_gen_发奖详情.py` 跑出 `BP live服雪花 28`(只新服)，老服60个BP雪花全漏→GM加分CSV只覆盖28新服、漏60老服(奖励券不受影响·那个按礼包id查不限服)。
- **根因**：`bp_snowflakes()` 原写死 `pageIndex=1&pageSize=200` **只读第1页**。扩服+深海上了一堆新活动后活动总数涨(iGame活动列表349+条)→老服WC-BP实例(13697)被挤到第2页外→只剩最新的新服BP(13912)在第1页。
- **修**：改成**翻页兜底**(`for pi in range(1,12): pageSize=100 直到data空/不满100`)→抓全所有status5的102243实例→新老服雪花全含(修后=83服)。已改入生成器。
- **★通用规律**：任何"读iGame活动列表只取第1页"的工具(bp_snowflakes/发奖验收/查重),活动数一多就漏后页→**凡按活动列表聚合的都要翻页**(deploy_wc.py的double-check读pageSize=300暂够但也是隐患)。扩服/加活动后第一次结算必核`BP live服雪花`数对不对(应≈活跃WC服数·55老+28新=83)。
- **★扩服后结算自动覆盖新服(验证)**：①奖励券=winners_of按礼包id(reason_sub_id·不限server)自动含新服 ②BP雪花=bp_snowflakes翻页后含新服BP(13912 status5) ③今日笔数翻倍(~3500→~6500)=新服玩家已下注入结算。新服无需改WC_SERVERS常量(那只用于paid_reach触达率显示·不影响发奖)。

## 📧 竞猜邮件本地化 + 发奖验收口径（2026-06-30/07-01·结算必读）
- **邮件已带「对阵+最终结果」20语言本地化**：`_gen_发奖详情.py` 每场 `多语言邮件_{key}.csv` = 通用贺词 + 标题加「{A} vs {B}」+ 正文加「{A} {比分} {B}，{胜方}胜」。队名/句式/点球词全 20 语言翻译，源=同目录 `_wc_team_i18n.py`（32 支 R32 队×20 语言 + TMPL 句式 + PEN 点球词；缺队回退三字码，后续轮次是子集已覆盖）。点球场显示如 `德国 1-1 (点球 3-4) 巴拉圭，巴拉圭胜`。**约束**：无 emoji（🏆 会导入失败）、正文不插换行（结果拼同一行）、字节级无尾空行（write_multilang_mail 已处理）。改队名/句式只改 `_wc_team_i18n.py` 重跑。
- **★发奖验收 = 查 iGame 发件箱（权威·首选·2026-07-01 用户定的流程）**：验"邮件发没发/发全没"**不查 asset 表**（asset 有领取延迟对账不准），直接查 iGame 发件箱 `getMailList`：
  - 接口=`email/outbox/getMailList`（POST `/ark/mails`，走 igame-skill CLI `node ~/.claude/skills/igame-skill/scripts/igame-query.js write "email/outbox/getMailList" '{"pageIndex":1,"pageSize":200}'`；auth=`.igame-auth.json` gameId=1090=X3；title 过滤参数无效→拉大页本地按 operator+title 筛）。
  - **筛**：operator=发奖人(如`林康`) + title 含 `World Cup`/`Oracle`（新版标题带对阵`World Cup Oracle Win! - {A} vs {B}`）+ 当天。
  - **★拆分机制(看懂才不误判)**：一场发奖 = **1 封母邮件**(`status=-2`·`sentAt=null`·receiverCount=全量·仅拆分占位不直接发) + 拆成多封 **≤450 收件人的子邮件**(`status=-1` 满450批 + 末批 `status=1`)。**子邮件收件数合计 = 母邮件 receiverCount = 应发笔数** 即算发全。别把 `-2`/`-1` 当"未发/失败"——那是拆分母/子标记，实际已发。
  - **验收判据**：按对阵聚合发件箱 receiverCount，比对生成器 `奖励_{key}.csv` 行数(应发笔数)。一致(差1可忽略)=发全。2026-06-30 4场实测:巴日3952/3953·德巴556/557·荷摩959/960·南加2449/2450 全一致=已发全。
  - **✅一条命令固化**：`python KB\产出-数值设计\X3_世界杯\_verify_发奖发送.py [操作人]` —— 自动拉发件箱→按对阵聚合收件数→比对所有已生成 `奖励_*.csv` 行数→输出每场 ✅已发全/⚠️缺口/❌未发。发完跑一次即验收。⚠️**唯一边界**：靠标题里 `- {A} vs {B}` 对阵后缀匹配→**6/29前老版邮件(无对阵后缀,如首场RSAvCAN)会误报未发**(需手工确认);6/30起本地化邮件都带对阵,不受影响。
  - 其他有用字段:`getMailSendStat`(GET `/ark/mails/mails/{mailId}/condition/stat`)对这类直发邮件返0不可用;`getMailDetail`(GET `/ark/mails/{id}`)可看单封 status/submitAt。
- **发奖到账验收（asset 表·辅助·claim lag 不准）**：加送券到账=`ods_user_asset asset_id='Item_1146' change_type='1' reason_id='igame'`(reason_sub_id=99999·金额列`change_count`=档位5/15/30/60)。**只能证"有人已领"不能证"发全"**（玩家要登录领才进表）→当验收辅证，不当主判据。⚠️当天 igame 1146 里有一批 `change_count=1` 流水与加送券无关(别的邮件)，对账按 amt∈{5,15,30,60} 过滤。

## 💡 免费pack奖励改动=改1行（2026-06-30）
48 个免费竞猜 pack（894010~894480·队号×10+0）**全部共用同一奖励组 `Reward 291335`**（每队付费档才各自分组）→ **改免费档奖励只需改 291335 这一组、不是 48 行**。291335 不被任何付费档/其他活动引用，改它零误伤。组内当前=抽奖券1146×1+钻石1002×1+金币1001×500+通用加速+基础资源袋3101。**通用加速道具系列**：11001=1分/11002=5分/11003=30分/11004=1时/11005=3时/11006=8时。本日已把 291335 内 30分(11003)→1分(11001)（行24793·commit 429feb8 dev_festival）。

## 🔴🔴 扩服上线铁律：皮肤大奖 vs 英雄本体脱节（2026-06-30·扩新服必读）
**背景**：世界杯终极大奖=足球宝贝皮肤 **5304001**（爱莉希雅 Hero1040 的皮肤），考虑往 1970 之后扩几个新服。
- **★核心错配（config 实证）**：世界杯**只发皮肤 5304001，全程从不发本体**。开箱超级大奖组 `Reward 291103` = 仅 `5304001皮肤 + 1146抽奖券x20`；排行榜奖励组 30581-30586 也只给皮肤。本体「英雄-爱莉希雅 **50040**」全游戏只从**招募(DrawCards)/科研/航线/集结**等渠道出，**世界杯任一奖励组都不发 50040**。→ **没本体的玩家中了皮肤=锁着穿不了**（皮肤列表只过滤 IsHide、不要求拥有本体，配置进客户端即显示锁定态，见 [[project_x3_hero_skin_video]]）。
- **★爱莉希雅本体获取窗口（DrawCards__DrawCards.tsv·Hero=1040）**：
  - 首次 UP = **开服第 29-34 天**（DrawCards 行1202，TimeCycle **75004**=TT2 开服相对·28d 触发·+6 天；15 个老服 1170~1460 更宽=第 15-34 天 TC72001）。
  - 之后 = **开服第 132-145 天**，再每 **84 天循环**一次（DrawCards 行12021，TC72021·CycType1·J=84d，全服通用）。
  - 不在常驻池（CardPools 无 1040 的非时间窗条目）→ 传奇限定、**非保底**："经历过 UP" ≠ "人人抽到"。新服只有 D29 这一次窗口（老服有 D132 循环兜底）。
- **★服龄判定线（用户 2026-06-30 定·以 WC 结束日 7/21 为锚）**：到 7/21 已能获取爱莉希雅(=服龄≥29天=首次UP已到)才可上 → **开服日 ≤ 2026-06-23**（=7/21−28d）。可上=同时满足 4 条：①开服≤6/23 ②服务端含 X3NEW-1432(认 ActvType64/71 竞猜) ③客户端含 X3NEW-1441+WC资源包(视频皮肤/框/表情显示) ④该服已部署开箱101516+兑换101339(券/金币有处花·用户已自行确认)。
- **★通用规律（换皮/活动设计可复用）**：**凡活动大奖是「英雄皮肤」，必须核实目标服玩家能否获得该英雄本体**——皮肤无本体=废奖。要么把活动奖励补发本体/碎片(50040)根治，要么用服龄卡线缓解(只缓解不根治：UP没抽中的仍没本体)。同理校验任何"获取了不能用"产出：消耗券→对应消耗活动是否部署；外显道具→客户端资源包是否含 DK；视频皮肤→客户端是否含展示程序。
- **其余产出"获取了不能用"审计表**：皮肤5304001→需本体(🔴)；抽奖券1146→需开箱101516；荣耀金币1147→需兑换101339；助威框80300-347/表情15420-467→需客户端DK资源包；视频皮肤展示→需X3NEW-1441；竞猜customParam→需服务端X3NEW-1432；框/表情宝箱1148/1149→自开即得(291201/291202)可用；纪念卡180079→集卡通用子系统无忧。
- **✅ 扩服=正式部署批次（2026-07-02 用户拍板）**：世界杯要上到新服，口径确认=**开服第30天(D30)落在7/21前 = 开服≤6/22 = 1980–2250 共28服**（D29/D30两口径同批·无服正好6/23开）。每服上6模块=竞猜池(102920-992·deploy_wc.py加servers)+开箱101516+兑换101339+BP102243+累充100597+签到101403(iGame submit)。3道版本门槛=服务端X3NEW-1432(认type64/71)+客户端X3NEW-1441+资源包+本体可招募(D30已保证)。⚠️与深海D35+**重叠4服1980/1990/2000/2010**(两批都开)。**部署清单HTML**=`KB\产出-数值设计\X3_上活动清单_世界杯扩服+深海节_20260702.html`(甘特·两批合一)。
- **✅✅ 已部署上线（2026-07-02·prod·29实例全status2异步激活）**：
  - **⚠️开箱/兑换/签到已重发(2026-07-02晚·单号更新)**：用户取消了原开箱13879+兑换13882+签到13883(现全status7)。①开箱/兑换改**从现在立即开始**→重发 **开箱=13908 / 兑换=13909**(start=now·end仍7/21·payload `wc_kx_dh_now.json`)。②**签到配错**(我配成整段7/3-7/21·被用户纠正)→**签到必须7天一期·多期**(对齐老服周分期)→重发 **签到=13910(7/3-7/9)+13911(7/10-7/16)**(payload `wc_qiandao_periods.json`·各168h)；⚠️老服签到只到7/16(无7/17+期)·新服照办·WC末5天无签到(用户认可)。③BP/累充原批(13880/13881)也被用户取消(status7)→按立即重发 **BP=13912 / 累充=13913**(payload `wc_bp_leichong_now.json`·立即~7/21)。**★最终现行live单号(2026-07-02)**：开箱**13908**/兑换**13909**/BP**13912**/累充**13913**(4个都across按cfg·全**立即~7/21**)/**签到13910(7/3-7/9)+13911(7/10-7/16)**(周分期)/竞猜13884-13907。**原始批13879-13883全废(status7·用户全重来了)**。★iGame **status7=已取消**(不在double-check活跃集2/5·取消的旧实例不挡重发)。★★**教训:签到(ActvType14)是7天循环型·扩服/换服必须按周多期部署·别配成一个长整段**(整段=只签7天后面空·且"结束对齐"规则不适用签到)。
  - **Hub 5模块**（原批单号 13879-13883=开箱/BP/累充/兑换/签到·**开箱13879兑换13882已取消见上条**）：走 `~/.claude/skills/igame-x3-activity-deploy/submit-cross-server.js --env prod --file <payload.json>`；payload=`wc_expand_1980_2250.json`（同skill目录）。**BP/累充/签到窗口 7/3 00:00–7/21 23:59:59 UTC·开箱/兑换已改立即~7/21**；字段照抄线上现有实例（**读回法**=GET `/ark/activity/list` 过滤cfg看startTime/endTime/acrossServer）：**开箱101516=跨服acrossServer=1**(新服自成一个跨服排行组·不并入老55服)、其余4单服；**签到101403配成整段7/3–7/21**(非线上老服的周分期6/26-7/2/7/3-9/7/10-16·因结束对齐)。
  - **竞猜24实例**（单号 **13884-13907**=R32剩余6场 seq11-16 西奥/葡克/瑞阿/澳埃/阿佛/哥加 ×4档 cfg102960-983）：走**新造的 `deploy_wc_newservers.py`**（=deploy_wc.py的复制品·仅SERVERS换成28新服·其余全同含double-check）；命令 `python deploy_wc_newservers.py 11-16 prod --go`。**走A口径=从今天起后续场次·已打完的seq1-10不补**。纯新开独立实例·跟老55服零server重叠→double-check自动通过。**后续轮次(16强等)对阵定了同法 `deploy_wc_newservers.py <场序> prod --go`**。
  - **★发奖/BP自动覆盖新服(无需额外配)**：结算 `_gen_发奖详情.py` 查猜中按礼包id(reason_sub_id·不限server)→自动含新服bettor；BP加分雪花从iGame拉102243各服(13880转live后自动带新服)。所以新服玩家结算/加分自动包含。
  - **下架整批**=`node submit-cross-server.js --env prod --offline --ids 13879,...` / 竞猜同(13884-13907)。
  - **★可复用SOP(扩服上世界杯)**：①读回现有服窗口对齐(GET activity/list) ②hub走submit-cross-server(payload照抄字段·结束对齐) ③竞猜走deploy_wc_newservers(改SERVERS·A口径跳已打完场) ④部后复查 status2=正常异步激活(非失败)。
- **✅ 过线新服名单（2026-06-30 数仓拉出·`dl_server_login_info` MIN(min_register_time) 反推开服日，口径见 [[x3-dau]]）**：WC 现开到 1970；可扩到 **2250**（**1980→2250 共 28 个服全过线**，服号步进 10，开服 5/25~6/22=D29~D57）。**边界干净**：末位可上=**2250**(开服6/22·7/21正好D29·UP 7/20刚开来得及)；首位不可上=**2260**(开服6/24·7/21才D27·UP要7/22才开·WC期内拿不到本体)。⚠️2160~2250(D29~D37)是"UP刚开/进行中"非保底，要稳可只扩到2150(D39+);但本体非保底错配仍在，根治需奖励补发本体50040。

## 🔤 竞猜活动标题去后缀(2026-06-29·dev_festival c1f0366 + dev 7e15e5c) + 删触发礼包测试行(dev_festival 10671a1)
- **标题改名**：73 个竞猜活动实例 `TXT_ActvOnline_ActvName_102920-102992` + 8 个界面内标题(`TXT_WC_Oracle_Title`/`_Free` + `TXT_WC_Guess_Title_R32/R16/QF/SF/3RD/FINAL`)，**16 语言全部**从「胜负预言·{32强/16强/8强/半决赛/季军/决赛/免费预测}」截断为**纯基础名「胜负预言」**(en=Match Oracle/kr=승부 예언/jp=勝敗予言…，去掉 `·`/`・` 后缀)。用户要求：不带免费/决赛/四强等轮次词。**两分支都改了**(dev 走 cherry-pick + tsv 合并驱动)。改法=python 正则 `\s*[·・].*$` 截断 col3-18。
- **删测试行**：`Pack__RecommendPack` row 86(type4/TriggerParams=894390/PackIDs=894391/世界杯竞猜测试，即之前验证「纯配置竞猜引流弹窗」加的测试样例 commit eef2655)已删。引流弹窗机制本身仍成立(见下方 type4 段)，只删那条测试样例。

## 🐛 开箱规则文本换皮漏改(2026-06-27修,commit c055a73 dev_festival·导表#1338 SUCCESS)
- **根因=开箱(101516)蹭了源活动「26元旦-开箱」(101513)的 RuleTips ID 16031**(两活动 ActvOnline col13 都=16031,共用一套规则自动key)。换皮时只回填了 Title/部分正文,**第2条「抽奖券获取途径」照抄源活动**=「集结海兽/完成情报任务/拜访酒馆」(那是糖牌的产出),与世界杯抽奖券真实来源(竞猜/每日免费预测/BP通行证·"强制竞猜"闭环)矛盾→误导玩家。**韩语[10]整段更是没换皮**(천마복상자/캔디카드/카밀라/새해=天马福箱/糖牌/新年)。
- **修法**:改 `tsv\i18n\Text__Text.tsv` 行17371 `TXT_RuleTips_Content_16031`——cn/en/sp/fr/id/de/zh/ru 8语言第2条改为竞猜/免费预测/BP通行证;韩语整段按cn重建(术语对齐 道具名1146=월드컵 챔피언 추첨권/1147=영광의 코인)。脚本 `scratchpad\fix_ruletips_16031.py`(正则 `2\..*?(?=\\n3\.)` 只换第2条段)。
- **★规律(可复用)**:①X3规则文本走自动key `TXT_RuleTips_Title/Content/Tab_{规则ID}`,配置表RuleTips那行单元格只是备注不进客户端(判displayed文本去Text表查key,见[[reference_x3_config_library]]);②**换皮活动若复用源活动的RuleTips/Reward等带文本ID,正文每一条都要逐条核语义**(光换道具名不够,获取途径/玩法描述会留源活动逻辑);③**多语言别只信中英**——本例cn/en已换皮但韩语整段漏译,逐语言扫;④隐患未治本:16031仍被101516+101513共用,i18n已被改成世界杯→元旦开箱若复用会显示世界杯规则,根治需给开箱新建独立RuleTips ID。

## v0.41 兑换商店删折扣券 + 全节日锚点礼包补钻石/VIP(2026-06-24·导表#1245/#1270 SUCCESS·dev_festival)
- **①兑换商店删随机折扣券**：世界杯兑换(ActvExchange ContentID **1339**)删 210038(随机传说折扣券2077)+210039(随机折扣券2079);深海主兑换(**1340「深海馈赠」**)删 134004/134005(同两券)。深海另一兑换 1341(深海珍宝集市/大富翁)本就无折扣券。删法=python按col0(seq)过滤行重写。
- **②锚点礼包(B线)补钻石+VIP——通用口径(可复用)**：
  - **「锚点礼包」=B线纯货币包**=`Pack` PackType=15(col9/0-idx) 名「{节日}抽奖券-道具获取」,4档$4.99/$19.99/$49.99/$99.99,玩家持抽奖券时走 ItemObtain「再获取」入口弹出。区别于A线连锁(ChainPack·PackType11)。
  - **历史BUG=所有老节日B线锚点是纯券没钻/VIP**(元旦210512-515/尼罗210612-615/情人节210712-715/新春210812-815·券分别1124/1128/1134/1138)。**世界杯211012-215**本轮已补→现全部补齐。
  - **★补法口径(对齐A线付费包·券数→钻/VIP固定比例)**：每档 **钻石(item1002)=券×125 · VIP点数(item2022)=券×1.25**。即 券20/80/200/400 → 钻**2500/10000/25000/50000** + VIP**25/100/250/500**。这与同价A线付费包(WC 211002/006/008/010)完全一致。
  - **落地=Reward表**:锚点Pack的 Content(col13)=同号Reward组;组内每加行必守 **同RewardID(col1)内 seq(col0)连续** 铁律([[reference_x3_reward_table_rules]]坑B)→删旧单券行+整组重排到连续空闲seq(本轮WC用40279-290·四老节日用40291-338)。建表脚本 `KB\产出-数值设计\X3_世界杯\build_fest_anchor_diamond_vip.py`(克隆原券行→改item/qty)。
  - **深海/夏日不在此列**:深海A线连锁付费包(211022/024/026/028/030)本就含1200藏宝图+钻+VIP(无B线锚点);夏日恋语当前配置无任何抽奖券锚点礼包(只装饰/拜访)。
- **③⚠️分支事故+非破坏恢复(踩坑)**:提交时工作树被并发agent切到`dev`分支→commit误落dev(dev已偏离dev_festival 70+提交·绝不可推)。**恢复**:`git checkout dev_festival`→重跑可复现脚本在dev_festival重做→push;清dev上误落提交用 **`git update-ref refs/heads/dev origin/dev`**(非破坏·不动工作树·`git reset --hard`被auto-mode classifier拦)。**铁律**:每次commit前`git branch --show-current`(并发agent会切你的分支)。

## 宣传图/splash 换皮出图(2026-06-24,4轮收敛的prompt公式·可复用)
- **产物**：`KB\产出-本地化与美术\X3\世界杯宣传图\`(足球宝贝主稿 `..\足球宝贝爱莉希雅\足球宝贝爱莉希雅_主稿_FINAL.png` + 用户给的splash参考图1竖/2横当格式锚)。**FINAL候选=v4一套**：横版 `WC_splash_horizontal_v4.png` + 竖版 `WC_splash_vertical_v4.png`/`_v4_2.png`(各返2张候选,_2更燃·待用户终选);v1/v2/v3全废弃;宣传文案 `世界杯_足球宝贝_宣传文案.txt`(套拓荒节三段式·套装名"绿茵之星·爱莉希雅"·**应援表情是静态别写"动态"**)。
- **★"抄splash格式"出图prompt公式(死磕4轮才对)**：用户给一张游戏splash当参考时，意图≈**只借格式/质感(画风+星空氛围+play按钮)+构图自由+突出主元素**，不是逐像素复刻构图。三个死路：①严格复刻构图(角色当前景小人物站悬崖远眺远处地标)=用户嫌死板②放开后gemini把角色立绘当**大贴纸摆中间糊背景**(="把背景叠到后面",用户最烦)③真去抄悬崖构图=用户说"误导你了别悬崖"。**终解prompt=**"Match the FORMAT of ref1 (style/colors/starry mood/PLAY button), composition FREE" + "ONE cohesive fully-painted illustration, hero **RE-LIT and integrated INTO the scene** with matching ambient lighting/depth/color grade, **NOT a flat cutout pasted on a background**" + 主元素(足球宝贝重打光融进发光夜景球场+巨型大力神杯+烟花彩带)。模型=gemini(双参考:格式锚+角色主稿)。同根因坑见下方v0.4开箱换皮段(gpt/gemini易把角色画占满屏)。

## v0.40 开箱新增「本服排行榜」占位(2026-06-24,commit 767a651 dev_festival·导表#1236 SUCCESS)
- **背景**：开箱(101516)原只有**跨服**积分榜=`RankCfg 1005`(挂 `ActvOnline.RankCfg`=field[20]);用户要再加一个**本服**榜,投放数值参考跨服÷数量级,核心奖励皮肤→纪念卡。
- **★X3 排行榜配置机制(本次破解,可复用)**：
  - **`Rank__RankCfg.tsv`**=榜定义。关键列(0-idx)：[0]ID(1~9999与程序对死,900段留英雄) [1]备注名 [2]TXT_名称(页签名,自动key) [3]**RankType=榜类型(6=本服/12=跨服/8=跨服分组…)** [4]活动归属id(世界杯=99/深海=97) [5]DK图标 [6]人数上限 [9]是否发奖 [10]结算邮件模板 [12]RuleTips [14]**上榜需求=个人积分≥此值才上榜** [15/17]每日/每周结算SpecialRewardSettlement组 [16/18]日/周结算邮件。
  - **`Rank__RankRewardSlotCfg.tsv`**=名次档→奖励包：[0]档位ID [1]榜ID [2]起始名次 [3]结束名次 [4]Reward组 [5]备注。
  - **`Reward__Reward.tsv`**=奖励内容：[0]RewardID(唯一) [1]掉落包组 [2]掉落类型(1道具) [3]ItemID [4]备注名 [5]数量 [8]权重(10000) [11]备注 [12/13]DropPara(本系列空)。
  - **两个挂载点(并存)**：跨服榜走 `ActvOnline.RankCfg`(field[20],int[]可`a|b`多挂);**开箱本服榜走 `ActvCrafting.本服排行榜`(field[6],表头明写"仅支持配置本服排行榜")**——这是开箱活动原生单本服榜槽,挂它**无需int[]改造**。⚠️但客户端**同时显示跨服+本服两Tab需程序联调**(多榜分Tab非纯配置,见 `C:\Users\linkang\Pictures\X3活动多排行榜配置方式.md` 坑2)。
  - **现成本服榜范本**=深海罗盘 `RankCfg 2000`(RankType=6,可对照建本服榜)。
- **本次落地**：新 `RankCfg 1006`(本服/人数100/**上榜需求1000**[用户定·跨服是2500]/邮件1000018) + 7档 SlotCfg 100424-100430(名次1/2/3/4-5/6-10/11-20/21-50) + Reward组 30591-30597(27行40252-40278) + 挂 ActvCrafting1516 field[6]=1006。奖励=镜像跨服1005:**皮肤5304001→纪念卡180079绿茵之星**(2026-06-24用户定稿数值:名次1/2/3/4-5/6-10发**10/7/5/3/1**张,**11名后不发卡**·commit be96bcd #1240)、速度道具30/25/20/15/10/7/5**÷10→3/3/2/2/1/1/1**(用户认可)、**剔除82004世界之巅头衔**(跨服全球头衔本服语义不符·待用户确认是否加回)。建表脚本 `KB\产出-数值设计\X3_世界杯\build_wc_local_rank.py`(克隆1005+映射,可复跑)。
- **占位性质**：页签名「本服排名」走自动key待补i18n;数值=参考值占位,正式上线前数值评审。

> 📋 **交接/换人先读**：全模块交接总文档 = `C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_世界杯活动_全模块交接总文档.md`（模块状态总表+接力点+关键链路坑+可复用资产+文档指针；本 memory 是其时间线详情版）。

## 🚀 iGame 部署「世界杯非竞猜 5 活动」到测试服（2026-06-25 实操·测试用）
- **非竞猜活动 = 5 个**（73 个竞猜 type71 实例排除在外）：开箱 **101516** / 累充 **100597** / 签到 **101403** / 兑换(荣耀兑换 Glory Exchange) **101339** / 通行证BP **102243**。纪念卡是集卡子系统无独立 ActvOnline，不单独部署。
- **iGame 部署法**（skill `igame-activity-deploy`，走 `ark/activity/submit`）：①`GET ark/activity/query?refresh=true` 返全量活动，**id == ActvOnline 6位ID**，按 cn/en 名("世界杯"/"World Cup")过滤定位 activityConfigId；②`submit_activity.py --activity-config-id <id> --name <名> --server <服> --start-ms --end-ms` 逐个提交，成功返 `{"success":true,"data":["<部署单号>"]}`。鉴权用默认 `.igame-auth.json`（刷新法见 [[reference_igame_gm_send]]）。
- **✅ 纠正假设：iGame 能部署到本地服 3080**（用户 2026-06-25 实测确认）——之前以为本地 `-e local` 服不接 iGame 平台推送，错。本地服也能从 iGame-dev 收活动。
- **🔴 时间窗坑（最关键）：本地服 3080 的服务器时间被 `GMSetServerTimeOffset` 顶到未来**（实操时在 **2026-09-27**，非真实日期 06-25）。iGame 活动窗口必须按**服的 offset 游戏时间**设，否则部署了也不在窗口内不激活。**读 3080 当前游戏时间** = 本地服日志 `server\GameServer\bin\Debug\net8.0\logs\game-3080.<真实日期>.log` 行首格式 `<真实时间> [<游戏时间>]` 的方括号值。本次窗口=`[2026-09-27 16:00, 2026-09-30 16:00] UTC`（取整到整点起=落当前服时间前=立即生效，+3天）。iGame 时间一律按 UTC 直填不做时区换算（skill 铁律）。
- 验证激活：本地服 GM `!gm @<被测uid> GMPrintServerActivityByCfgId <cfgId>` 看 count=1（@uid 用被测号自己避海域坑，见 [[workflow_x3_local_server_gm_telnet]]）；客户端看不见先退登重进刷活动列表。

## 🐛 助威头像框「解锁错框」bug + 道具↔框映射(2026-06-24修,commit dev=51e42e8/dev_festival=57544c7)
- **链路(接管必备)**：助威头像框走**道具使用解锁**。①发放道具 `Item__Item.tsv` **80300–80347**(48队按FIFA字母序,ALG=80300…UZB=80347),道具图标=`DK_Img_Player_AvatarFrame_WC_{码}`(独立字段·正常);②**使用效果=Item col[8](0-idx,值`框cfgID|-1`)→解锁 `Personalize__PersonalizeAvatarFrameCfg.tsv` 对应行**;③框cfg行:col5=ImgRes(`DK_Img_Player_AvatarFrame_WC_{码}`)、col10=Name、col7/8=属性/数值(WC全220000攻击/50)。框图DK注册=Path/Display_Personalise.asset(本次全验:Path+Display+png+meta+guid全对,**问题不在DK图层**)。
- **★bug根因(可复用规律)**：WC框cfg中 BEL–UZB 按字母序占 **10032–10075**,但 **ALG/ARG/AUS/AUT 4个后补在表末尾 10076–10079(不在字母序位)**。做道具表套了线性公式 `框cfg=道具id−70272`(BEL 80304→10032✓),于是字母序最靠前这4队道具(80300–80303)被指到线性位上**已被旧框占用的** 10028–10031(夜颜花骨/酒馆金银铜樽)→玩家用「阿尔及利亚框」道具实际解锁「夜颜花骨」。**道具名/图都对、列表看不出,一使用才错**=隐蔽bug。修=Item col[8] 80300→10076/80301→10077/80302→10078/80303→10079。
- **★通用教训**：cfg行**乱序补在表末尾**(没插字母序位)时,任何「按线性公式/顺序假设」生成的引用方(发放道具/奖励组/映射表)都会对乱序项静默指错。**建表后补行,必回查所有按顺序引用它的下游表**;排查「图对名对、效果错」类隐蔽bug直接核引用ID链,别只看DK层。

## 🛠️ 竞猜对阵生成器工具(2026-06-24,运营配对阵用)
- **产物**：`KB\产出-数值设计\X3_世界杯\世界杯竞猜_对阵生成器.html`(本地start打开)；可复跑生成器 `_gen_对阵生成器.py`(读live Pack表验证192包齐+按FIFA码字母序算队号)+模板 `_tpl_对阵生成器.html`(改UI改模板重跑)。
- **功能**：选A/B队+档位(免费/$4.99/$9.99/$19.99,可多选)→出 customParam `{"packIdA":x,"packIdB":y}`;「加入部署清单」自动从池 **102920–102992(73个type71实例)** 顺次分配**不重复活动ID**;清单可复制TSV(活动ID+对阵+customParam)。含PACK总表(192包/48队×4档,可搜)。
- **数据已验证(live `Pack__Pack.tsv` 894010–894483 共192包齐)**：队号=FIFA三字码字母序1–48(ALG=1…UZB=48);礼包号=894000+队号×10+档位(0免费/1=$4.99/2=$9.99/3=$19.99);助威头像框=80299+队号;应援表情道具=15419+队号(例BRA队7→包894070-073/框80306,GER队21→包894210-213/框80320,ALG队1→框80300/表情15420)。一实例=两包(两队各一同档),多档=多实例。
- ⚠️**file://本地HTML复制坑**：`navigator.clipboard`在file://被禁,必须加`textarea+execCommand('copy')`兜底(本工具已加),否则复制按钮静默失效。

## ★竞猜活动ID池容量 + 跨轮复用铁律（2026-06-28·上活动必读）
- **池=73个**(ActvOnline 102920-102992,实查全在)。**一场×4档=4个id**(免费+4.99+9.99+19.99)。
- **R32全16场×4档=64个**,占 102920-102983,**仅剩9个**(102984-992)。**16强(8场×4=32)/8强起这9个根本不够**。
- 🔴**跨轮必须复用id**:某场打完锁盘→下线那批实例→**用新customParam重部署成下一轮**(customParam驱动天然支持,改对阵=改后台参数零配表)。别给新轮次找新id(池就73个)。或后续轮次减档位省id。
- **R32活动ID分配**:前4场(南非加/巴日/德巴/荷摩)=cfg 102920-935;中4场(科挪/法瑞/墨厄/英刚)=102936-951;后8场(比塞/美波/西奥/葡克/瑞阿/澳埃/阿佛/哥加)=102952-983。全R32对阵+时间见看板数据 `KB\产出-数值设计\X3_世界杯\wc_dashboard_data.json`(16场·已ESPN修正)。
- **部署进度(2026-06-28)**:**前4场(南非加/巴日/德巴/荷摩,cfg102920-935)昨天06-27已上、live且ESPN结盘正确=单号13750-13765(status5,保留)**。⚠️今天我没核实旧的还live就重上→单号13792-13807撞16重复(我的锅),已全`--offline`拦在status8不激活(待审批人/UI终结)。**中4场(科挪/法瑞/墨厄/英刚,102936-951)=早先Wikipedia错时间批已全撤回status19**;**后8场(102952-983)未部署**。→ **R32现仅前4场live;剩12场(102936-983)待用ESPN修正时间部署**。prod竞猜部署=python ascii提交器(`~/.claude/skills/igame-x3-activity-deploy/`+ensure_ascii防中文乱码),customParam=`{"packIdA":队基号+档,"packIdB":...}`。⚠️重上前必查旧实例真status19(见[[reference_x3_kadmin_deploy]])。
- ✅**固化部署器 `~\.claude\skills\igame-x3-activity-deploy\deploy_wc.py`(2026-06-29)**：`python deploy_wc.py <场次> prod [--go]`(场次如`9-16`,默认dry-run只查重预览,--go真发)。读 `wc_dashboard_data.json`(16场ESPN时间)→场序N→cfg=102920+(N-1)*4→4档customParam(队基号+档)→开启立即/结束=该场结盘→**内置double-check(同cfg+server+时间重叠+status2/5=重复拦exit3; status8/11废条目提示)**→ascii提交防乱码→报单号。实测:dry-run跑已上场次正确拦截。**以后上竞猜统一用它,别再inline现写。**
- ✅**R32 全16场部署完成(2026-06-29)**:1-4场cfg102920-935=单13750-765(live);5-8场cfg102936-951=单13816-831;9-16场cfg102952-983=单13832-863。全16场×4档=64实例·55服·ESPN结盘·double-check无重复无乱码。5-16场status2异步激活中(同首批,scheduler tick后转live)。池用 102920-102983=64/73,剩9个(102984-992)。误造的13792-807已驳回成status11废条目(不live·无害)。**下一轮(16强)用 `deploy_wc.py` 复用这些cfg:先下线/撤回打完的R32场→改wc_dashboard_data.json schedule为16强对阵→重跑(double-check会防撞)。**

## ★上线时间锚（2026-06-22 查证·北京时间·上线运营必读）
赛程通用口径=美东ET，运营按**北京时间(ET+12h)**，换算后整体挪到次日凌晨——文档/甘特里6/28-7/19是ET赛程日期,别直接当北京时间用。
- **系列hub上线=6/27(用户定·北京)**:开箱/BP/累充/签到/兑换/纪念卡不依赖赛果,先开;此时还**没有竞猜场次**(对阵未定)。
- **小组赛全打完=32强对阵全锁定**(48队制无单独抽签·由小组排名定):末场J组约旦vs阿根廷6/27 22:00ET开球→约23:50ET打完=**北京6/28约12:00(中午)**对阵全锁。
- **32强淘汰赛首场**=match#73(A组亚军vs B组亚军@SoFi·6/28当天ET仅此1场):6/28 15:00ET=**北京6/29 03:00**。
- **★运营模型(用户定2026-06-22)**:**上活动=该轮对阵一确定就能上(最早=上一轮末场打完那刻),不用等开赛**;**锁盘=各场开赛前10分钟**。⚠️**2026-06-27用户纠正:锁盘没有自动机制!靠手动把 iGame 活动 endTime 设成「开球−10min」实现**(到点活动关闭即停押注);漏设/设晚=开球后还能押。之前记的"自动·不用盯"是错的,每个实例endTime必须逐个核对填对。
- **第一个竞猜礼包**:对阵锁定后(6/28中午北京)→**6/28下午就上**(不用等6/29凌晨开赛),玩家大半天竞猜窗口,6/29 02:50自动锁盘。R32从6/29起每天多场。
- **每轮上活动时点(北京·上一轮打完的当个白天上整轮场次)**:32强=6/28下午 / 16强=7/4白天(R32末场) / 8强=7/8白天(16强末场) / 半决赛=7/12白天(8强末场) / 季军决赛=7/16白天(半决赛末场)。⚠️7/8三撞:8强上活动+晋级之路头像框封包+深海节部署灰度。
- 后续轮次同理ET→+12h换北京;甘特HTML`KB\产出-数值设计\X3_7月排期_世界杯+深海节甘特.html`含三档投放表+逐轮热更窗口+封包硬节点(6/24/7/8/7/15)+与深海节并行撞车标注。
- ⚠️**查开球时间只认 ET 锚,别信web搜出的"当地时间"**(2026-06-27踩坑):资讯站给的local kickoff各场散落不同时区(LA/Houston/Foxborough/Guadalajara…)且常互相矛盾,按local换北京极易错(本次首场误算成北京11:00,实为03:00)。正确=搜"ET kickoff"再 ET+12h=北京。**R32前4确定场(真队伍·北京)**:南非vs加拿大6/29 03:00 / 巴西vs日本6/30 01:00 / 德国vs巴拉圭6/30 04:30 / 荷兰vs摩洛哥6/30 09:00。上线建议=前4场上,南非vs加拿大走免费档(揭幕场星味最弱),其余三场带$4.99/$9.99/$19.99三档付费。
- ⚠️⚠️**开球时间权威源=ESPN/SI,别信Wikipedia(2026-06-28踩坑)**：Wikipedia 的 R32 几场开球时间错(法瑞/葡克/阿佛差4h、英刚/哥加差1h),害第二批结盘配错被撤。**ESPN(`espn.com/soccer/story/_/id/48939282`)+SI 一致版才对**。**R32全16场结盘(=开球-10min·endTime·UTC·ESPN核准)**:南非加6/28 18:50/巴日6/29 16:50/德巴6/29 20:20/荷摩6/30 00:50/科挪6/30 16:50/法瑞6/30 20:50/墨厄7/1 00:50/英刚7/1 15:50/比塞7/1 19:50/美波7/1 23:50/西奥7/2 18:50/葡克7/2 22:50/瑞阿7/3 02:50/澳埃7/3 17:50/阿佛7/3 21:50/哥加7/4 01:20。确认表 `KB\产出-数值设计\X3_世界杯\世界杯竞猜_R32结盘时间确认.html`+看板数据 `wc_dashboard_data.json`(已修正·可复跑)。
- 📋**首批4场部署清单(2026-06-27·手填iGame·1970服)**:`KB\产出-数值设计\X3_世界杯\世界杯竞猜_首批4场部署清单.html`(对阵/活动ID/customParam/开启UTC/锁盘UTC/备注名全表)。**11实例**:南非加拿大=免费(102920)+$4.99(102921);巴西日本/德国巴拉圭/荷兰摩洛哥各三档(102922-930)。packId公式894000+队号×10+档位,队号(本批):RSA39/CAN8/BRA7/JPN27/GER21/PAR36/NED32/MAR30。⚠️**坑:102920-930的ActvOnline备注名是旧mock占位(ENGvsBRA等·全标$4.99)对不上真实对阵**,手填按活动ID认实例+按customParam定对阵,别信备注(真对阵customParam驱动,备注纯编辑器备注)。锁盘endTime(UTC,=开球-10min):南非加拿大6/28 18:50 / 巴西日本6/29 16:50 / 德国巴拉圭6/29 20:20 / 荷兰摩洛哥6/30 00:50。
- 🔑**iGame API 推竞猜实测通(2026-06-27)**:`submit_activity.py`(skill igame-activity-deploy)能推竞猜实例到任意服,实测推102920到**1970服**成功`{"success":true,"data":["3403"]}`(data[]=部署单号)。activityConfigId**直接==ActvOnline 6位ID**(102920,query接口确认在列·cn=世界杯竞猜32强)。auth走`.igame-auth.json`(字段是`clientId`大写I)。⚠️**唯一缺口=脚本payload不带customParam字段→推上去是空对阵壳**(竞猜靠customParam建对阵)。要API连customParam一起推须先拿一条"带customParam的真实竞猜部署Copy as cURL"确认submit payload里customParam确切字段名(server端读arkCustomParam,见[[reference_x3_customparam_activity_pattern]]),再扩展脚本。**本次用户方案=先API推免费空壳→用户手动撤回→再手填正确对阵**(规避customParam,简单不易错)。时间epoch=`calendar.timegm((Y,M,D,h,m,s))*1000`(UTC直填不换算)。
- ✅**首批已落生产基准(2026-06-27·prod webgw-cn·1970服)**：免费场 102920 已上线=部署单号**13732**(创建人1957林康),customParam`{"packIdA":894390,"packIdB":894080}`,**开启统一2026-06-27 06:30 UTC(北京14:30·用户从02:30改的·以此为准)**,结束=各场锁盘(开球-10min)不变,acrossServer=0/Rank=0。我推的空壳13731已被撤回(status19)。其余10实例照此基准部署,清单HTML已同步。**用户(林康)有prod上线权限(实测submit成功)**。⚠️prod网关=`webgw-cn.tap4fun.com`(≠dev的ms-inner-gateway-dev),prod token≠dev token(详见[[reference_igame_gm_send]]环境表+官方skill igame-x3-activity-deploy)。
- 📋**正式部署最终方案(2026-06-27待发)**：4场×4档=16实例(102920-935)→**线上「获取过世界杯道具」的55服**；开启统一北京15:30(07:30 UTC)、结束各场开赛前10min(SA-CAN6/28 18:50/BRA-JPN6/29 16:50/GER-PAR6/29 20:20/NED-MAR6/30 00:50 UTC)。payload+dry-run已备(`~/.claude/skills/igame-x3-activity-deploy/prod_all16_wcservers.json`),待用户最终确认+下线旧13732后 `--env prod --no-aggregate` 发(880服-活动·prod免审批即时可见)。清单HTML=`KB\产出-数值设计\X3_世界杯\世界杯竞猜_首批4场部署清单.html`(生成器`_gen_首批部署清单.py`)。
- 🔑**竞猜可纯配置加触发弹窗(补触达·2026-06-28代码验证·不用程序)**：竞猜建包链=`CreateActivityWorldCupGuess→ResolveWorldCupGuessGiftId→CreateActivityPack→CreateGift(cfgId=894xxx)`(GiftMeta.Activity.cs:140)→`CRecommendPack.GiftPackCreateIds[894xxx]`命中→fire **type4「创建礼包触发」弹窗**。竞猜包在**OnLogin/OnActivityCreate就建**(非开界面才建)→type4弹窗能**主动覆盖没点开竞猜的玩家**(补37%触达缺口)。**配法**=`Pack__RecommendPack`加行:TriggerType=4 / TriggerParams=竞猜礼包cfgId(894xxx,被创建时触发) / PackIDs=推荐包(付费档引流) / Duration / SceneLabel。表字段:ID|IsOn|TriggerType|TriggerParams|Duration|PackIDs|TriggerCD|TriggerRandom|FreeRewardID|SceneLabel(10列,LF,max id 85→新86)。type触发枚举(代码固定):1黑市/2任务/3买礼包/4创建礼包/5买推荐组,加新类型才要程序;现有type4够竞猜用。⚠️弹的是礼包不是跳竞猜界面;要"点击跳竞猜界面"仍需程序。
  - ✅**已验证通过(2026-06-28·本地服3080日志实证·零代码)**：测试行 `Pack__RecommendPack` ID=86(type4/TriggerParams=894390/PackIDs=894391/SceneLabel=世界杯竞猜测试)→ dev_festival commit eef2655 + 导表#1341 SUCCESS。本地服实测抓到 `CreateActivityWorldCupGuess create new packCfgId=894390` → `CreateGift recommend createIndex hit cfgID=894390 createTargets=[86]`(GiftMeta.API.cs:348)。**纯配置竞猜引流弹窗成立**,可批量配(48队免费包894xx0→各自付费档894xx1引流,补37%没碰竞猜的触达,零程序)。
  - 🔑**竞猜包per-player建包触发机制(验证法)**:竞猜包在**玩家活动初始化时per-player建**(OnPostInit→HandleServerActivityInfo→CreateActivityWorldCupGuess),**server级deploy本身不建包**;加载任一离线玩家(任何player GM如 `!gm @<uid> GMPrintServerActivityByCfgId 102920`)即触发建包→弹窗,**无需Unity客户端**。本地服验竞猜建包/弹窗最快=`!gm GMDeployWorldCupGuess <cfgId> <packA> <packB> <时长秒>`(server-scope,errCode0)再 `GMPrintServerActivityByCfgId @uid` 加载玩家触发。
- ✅**发奖详情/结算自动化工具(2026-06-29建)**：`KB\产出-数值设计\X3_世界杯\_gen_发奖详情.py`→产 `世界杯竞猜_发奖详情.html`(看板有按钮链过去)。链路:①**ESPN公开API自动拉赛果**=`site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=YYYYMMDD`(ET日期=kickoff_utc-4h;按队英文名匹配;completed/winner/score)②**猜中玩家=买赢队礼包(含免费)**=数仓`ods_user_asset buy_gift + reason_sub_id IN 赢队4包(base+0..3)`③加送券:免费+5/4.99+15/9.99+30/19.99+60(item1146)④**GM加分BP+600**:iGame拉WC-BP(cfg102243)各服运行时雪花(responses[].activityId)→`server,user,雪花,600`喂 `batch_add_score.py --csv`。产出每场(写`发奖csv\`目录):**①奖励名单csv=X3 6列GBK `服务器,玩家,[1146*券],,,`(直接导iGame bulk-mail,格式见[[reference_x3_igame_mail_import]])②多语言邮件csv=**iGame转置模板格式**(语言做列20种/标题内容超链接做行,走 `~\.claude\skills\bulk-mail-reissue\multilang_mail.py` 的 write_multilang_mail,**别手拼**;坑:无尾空行+无emoji,详见[[reference_x3_igame_mail_import]])③GM加分3变体: **GM_{key}.csv**(`server,user,BP雪花,600`·喂batch_add_score.py脚本批量发) / **GM加分_{key}.txt**(完整文档:表头+；分隔命令+脚本命令) / **GM纯命令_{key}.txt**(纯命令·换行分隔·无；无表头·整列复制)。命令=iGame GM输入框格式 `{"serverIds":"服","cmd":"addactivityscore","playerIds":"玩家","args":["雪花id","600"]}`(；分隔仅GM框整块粘时用,API/脚本不加；);对照样例 `世界杯BP结算_GM命令_样例.txt`,格式权威见[[reference_igame_gm_send]]**。⚠️**发奖前必复查GM雪花仍==live**(GM文件服→雪花 比对 iGame当前102243各服responses[].activityId;若BP中途重部署过雪花会变需重跑生成器;2026-06-29实测55服全一致)。★发放规则(用户2026-06-29定):买多档=多笔=加多次(券+BP**都按笔不去重**,一笔礼包=一次押注=一次发放)。看板「对阵总览」每场带「**发奖时间(北京)=完赛(开球+2h)后那个13:30**·统一每天13:30结算」+「发奖详情▶」按钮(链 `世界杯竞猜_发奖详情.html#{key}` 锚点);**待发奖section已删**(并进总览)。详情页含**竞猜总人数/猜中人数·笔/命中率 + 付费玩家竞猜触达率**(=55服付费玩家∩竞猜buy_gift,口径见[[reference_x3_datain_asset_query]],D0-D1≈87%)。**每天12点看板任务末尾subprocess调它一并刷(自动赛果)**。⚠️名单/命令仅审核不自动发;发完把场key加settled。
- 🔑🔑**竞猜礼包购买/结算查询口径(2026-06-27破解·结算直接复用)**：**订单表 `ods_user_order.iap_id` = Pack ID 894xxx 本身**(不是Pack配置里的PackPrice档105/107/111——那是价格档引用,订单里用不到;我一开始查105/107/111得0是踩这坑)。dim.iap 里894010-894483每档都登记了队名+价格(主数据没错)。**查竞猜购买**=`SELECT iap_id,count(*),count(distinct user_id),sum(收入) FROM v1090.ods_user_order WHERE iap_id LIKE '894%' AND pay_status=1(int) AND partition_date>='<开赛日>' GROUP BY iap_id`。**iap_id是varchar、pay_status是int**(类型别搞反)。**收入口径**=`CASE WHEN currency_type='TOKEN' THEN actual_charge/100.0 WHEN currency_type='usd' THEN actual_charge ELSE pay_price END`(⚠️TOKEN的actual_charge是×100分,不÷100会虚高百倍,见[[feedback_x3_token_actual_charge_unit]])。**解码**:队号=(iap-894000)//10,档=(iap-894000)%10(0免费/1=4.99/2=9.99/3=19.99),队号→FIFA字母序code→队名;一个pack=押某队某档,match=该队所属对阵。**免费档(894xx0)走1钻不进真实订单表**。结算SOP里"查购买名单"即用此(见[[reference_igame_gm_send]])。
- 🔑**WC道具 asset_id(datain查"哪些服有世界杯")**：`Item_1146`世界杯冠军抽奖券(核心货币)/`Item_1147`荣耀金币/`Item_1148`框宝箱/`Item_1149`表情宝箱/`Item_5304001`足球宝贝皮肤/`Item_80300-80347`48队助威框。查WC活跃服=`SELECT TRY_CAST(server_id AS INTEGER) sid,count(distinct user_id) FROM v1090.ods_user_asset WHERE asset_id IN('Item_1146','Item_1147') AND change_type='1' GROUP BY 1`(走ai-to-sql `_datain_api.execute_sql(sql,'TRINO_HF')`)。**2026-06-27线上结果=55服**(1170~1970,1910最高515人;完整列表在 prod_all16_wcservers.json)。
- 🔑**读回校验已部署活动(含customParam/时间)**：`GET webgw-cn.tap4fun.com/ark/activity/list?pageIndex=1&pageSize=50`(prod auth header),返字段含 id/activityConfigId/startTime/endTime/customParam/servers/acrossServer/status/createdBy。**这是核对运营实际填了啥customParam/时间的权威途径**(activity/query只返配置id+名,不返部署实例)。name字段GBK乱码无视,看customParam/时间即可。

## ⚠️竞猜礼包ID段已从892改到894(2026-06-23核实·全文旧记的892/893段作废)
- **现行真源**(dev + feature/x3-deepsea-art 工作区都已合并·实查一致)：竞猜礼包=**Pack 894段(894010-894483,共192个)**；活动壳 ActvOnline **102920-102992(共73个实例,v2)**。
- ⚠️**2026-06-23 纠正运行时挂载法**：上面"挂载走 ActvPack PackList 列"是**误判**(只看了配表存在,没核代码路径)。**实证**(代码 `ActivityWorldCupGuessCondition.cs` + commit a3e648decd6 X3NEW-1432 已在 origin/dev_festival)：竞猜 ActvType=64 已于 **2026-06-18 切 customParam 驱动**——iGame 部署填 `{"packIdA":894xx,"packIdB":894xx}` 两礼包号建本场对阵，**运行时不读 ActvPack.PackList**(ActvPack 2920-2992 配表行仍在但绕开)。**换对阵=改 iGame customParam 重部署,零配表/零热更**。**礼包号公式=894000+队号×10+档位**(队号=国家英文名字母序01-48=助威头像框道具号−80299;档位0免费/1=$4.99/2=$9.99/3=$19.99),例 巴西(队07)vs德国(队21)$4.99=`{"packIdA":894071,"packIdB":894211}`。⚠️**一个实例只出两个包(两队各一·同档),多档=部署该场多个实例**(CreateActivityWorldCupGuess 只建2包不派生4档)。抽查测试=挑几个102920-992实例上iGame填customParam看对阵/购买/锁定。本地 GM `GMAddServerActivityByCfgId` 不带 customParam→开不出对阵,竞猜本体只能走 iGame 部署测。详见 [[reference_x3_customparam_activity_pattern]] + 交接总文档 §3 纠正横幅。
- **外显道具 GM 发放速查**(`!gm @<uid> GMAddItem <号> <数>`)：足球宝贝皮肤 **5304001** / 助威头像框 48队 **80300–80347**(80306=巴西/80320=德国) / 应援表情解锁道具 48队 **15420–15467**(param→Emoticons 300–347,15420=阿尔及利亚) / 抽奖券 **1146** / 荣耀金币 **1147**。
- **★查世界杯礼包的正确姿势**：Pack 表**备注列无"世界杯/WC/竞猜"字样**(克隆来的没回填)→按文字搜 Pack 表搜不到!必须**顺 ActvPack 引用链找**(ContentID→PackList)或按 894xxx ID段过滤。下方 v0.30/v0.32 等段落写的 892001-112/893xxx 全是旧ID,只按ID段定位会扑空。
- BP竞猜加分途径(2026-06-23复核仍在)：ActvScoreTask **1910"竞猜命中1场比赛"Score=600**(空TaskType=GM手动结算),挂进世界杯BP `ActvBattlePassScore` row **2242**(备注"世界杯-BP",途径串`...|601|602|1910`)。⚠️ContentID是**2242不是旧记的2240**(2240现被"推币机BP-单服"占用)。

## 🔴 2026-06-24 重大ID纠正：真·世界杯BP是 ActvOnline **102243**，不是 102240（commit c3416be dev_festival·导表#1214 SUCCESS）
**全文旧记的"BP102240"全错**。三个 ActvType=22 BP 行别再认混：
- **102243** = 真·世界杯BP（c3="世界杯通行证"·ContentID=**2242**→BattlePassScore"世界杯-BP"含竞猜加分1910·DK_WC_Pass_Icon/Bg）。**它的 TC 一直是 2240（=TimeCycle"世界杯-BP(测试)"绝对窗6/11-7/19）没被清0** → 本次清成 0（与开箱/累充/签到/兑换4模块对齐，全走 iGame 部署控时）。type22 在 SKIP_TIMECYCLE_CHECK，TC=0 导表不报错。
- **102240** = 废弃克隆（当初从推币机102242克隆来做WC BP，备注改成"世界杯-BP"但 ContentID/DK 还是推币机的没换完，TC 从克隆起就是0）→ **本次已物理删除**（无任何外部FK引用，验证过）。06-23 的"清BP102240 TC"其实清的是这个废弃克隆，真BP 102243 没动到，所以才有此 bug。
- **102242** = 真·推币机单服BP-循环期（ContentID=2240→"推币机BP-单服"·TC=160004 TT=2开服15天+3天循环）**完好从没被动过**，无需"改回去"。另 102241=推币机BP-跨服、102244=深海BP，别混。
- 判后续每个WC活动TC是否对：除102243外，开箱101516/累充100597/签到101403/兑换101339 + 73个竞猜(type71·102920-992) 全已 TC=0（2026-06-24全量扫过）。

## 2026-06-23 debug 三修 + 合并修复（已commit 0a0d1fc + 合origin/dev e1a075c，**已ff-push到origin/dev**=dev现cefc2e8→e1a075c，含4个深海WIP一并上dev）
- ⚠️**下面②③写的"BP102240"是错的**，真BP=102243，见上方 2026-06-24 纠正块。
- **①猜中即得不显示根因**：客户端 `UIActvWorldCupGuess.cs:132 bonusTips.text=packCfg.Desc`，而 `CfgProtoTextEx.cs:4347` 把 Desc 硬拼成 **per-pack 自动key `TXT_Pack_Desc_{packID}`**——**完全不读** Pack 表 c37 里配的共享key `TXT_WC_Oracle_Bonus_T1/T2/T3/Free`。修=给192个894礼包各建 `TXT_Pack_Desc_{id}`（按c37档位:Free+5/T1$4.99+15/T2$9.99+30/T3$19.99+60，从全对的T1模板`+15`替换派生，**绕开T2/T3共享key的en等10语言误填+15的预存bug**）。⚠️共享key塞c37是白配，铁律见[[reference_x3_config_library]]自动key机制。
- **②TC=0 导表硬伤**：世界杯系列非竞猜模块(开箱101516/累充100597/签到101403/兑换101339/BP102240)TC清0后，**开箱(ActvType15)/签到(ActvType14补签)不在 `PostProcessData.py` 的 SKIP_TIMECYCLE_CHECK** → 导表报 `时间控制器ID:0不能是0`。深海节(d2eb3dd)只加了累充5/酒馆7/转盘10/兑换13/BP22/许愿池50/拜访56。修=SKIP 集补 `ACTV_TYPE_CRAFTING=15`+`ACTV_TYPE_RESIGN=14`（竞猜是71=WC_GUESS已在）。累充5/兑换13/BP22本就在SKIP。
- **③页签group**：Pack表无group字段，礼包跟随**活动级 ActvOnline col38(0-idx)=ActvGroup**(世界杯=139)；BP(102240)漏配补139。
- **删测试**：102911/912/913+链(ActvPack 2911-13/TimeCycle 2911-13/Pack 891101-106/i18n 6key)；Reward组291101/291102共享live**不删**。
- **合并后遗症(line-merge未装tsv3way driver打散)**：Reward整表col1乱序(273断点/331 RewardID劈断,导表硬伤)→**按col1升序重排**恢复(基准e763d7c=24999行0断点);AvatarFrame同理(2→0);7个ActvOnline备注被空值覆盖(102241/102242/102902/106501/106502/106503/109002,全是dev侧推币机/一掷千金/霍普金斯非节日活动)→从合并前dev侧(ac2e54f^2)取回。详见[[workflow_x3_merge_conflict_audit]]。
- ⚠️**列号现查纠正**(memory旧值多处错)：ActvOnline TimeCycle=col8(1-idx)/ActvGroup=col39；Reward RewardID=**col2**(col1是唯一行号seq)；Pack奖励组=col14(字段名Reward)/档位标记c37。tsv_edit用0-idx(TC=7/Group=38/备注=1)。

## 落地状态（v0.2 · 2026-06-09）
- **策划案 GSheet**：`1eAG8w9y4f_hJMc1l_pMVglzdWf9M4sLTOlKcIKq_BEc`（13页签，已写实+格式+task-checker验收10/11过）。构建脚本：`C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\build_design.py`（可复跑覆盖，改内容改脚本再跑）。
- **历史付费参考(数仓实测·全服全期·收入口径usd取actual_charge其余pay_price)**：尼罗 832人/$47785/ARPPU**$57.43**；情人节 511人/$30010/**$58.73**；春节 315人/$14984/$47.57。世界杯目标对标尼罗~$57，不预估增量。(查询:v1090.ods_user_order 按iap_id前缀2106/2107/2108聚合;user_id列名是user_id非uid)
- **v0.2改动**：增量预估→历史ARPU实测值；排期加甘特图(■染蓝条,按赛程阶段)。
- **剩余待办(建配置时定)**：ContentID·ActvOnline ID分配 / 结算SQL模板 / 打点字段对齐 / 草案数值待数值评审。

## ⚠️构建脚本管理的Sheet：真源=脚本,手改必被覆盖(2026-06-10踩坑)
本案 Sheet 由 build_design.py 全量覆盖式重跑——**任何直接在 Sheet 上的手改(如足球宝贝主稿FINAL回填)都会被下次重跑冲掉**。铁律：凡脚本管理的表,改内容只改脚本再重跑,绝不直接改表;若临时手改了,当场把改动固化回脚本。v0.7.1 已把皮肤主稿FINAL/配色手改固化进脚本。

## v0.7 全案review+重验(2026-06-10,方法论)
大改(v0.2→v0.7)后重派 task-checker 重验,抓到自查漏掉的**删除链残留3处**(数值页"每日免费开"悬空/红点引用已删机制/免费Pack"抽奖券0"与必发1券矛盾——照配会断结算链)。教训:①自己改+自己扫(grep关键词)不够,删一个机制要把"以它为前提的下游表述"(红点条件/数值行/示例行)全链清掉 ②review发现的事实错误(周期6/11-7/6 vs 真实赛程6/28-7/19)源于早期假设没对真实日历,涉及真实世界日程的案子先查日历再写。

## v0.3-v0.4 迭代(2026-06-09)
- **格式重构(v0.3)**：教训=异构表格+甘特图共用一套列宽必打架，正文塞窄列=「烂」。解法：①甘特图独立成页(列宽均匀84px) ②每页正文统一归一列(总览/模块页正文归C列,模块列阶梯正文在E) ③列宽按页签类型分(模块MODULE_W正文E宽/表格TABLE_W/甘特均匀/总览专用) ④build_format_reqs开头加全区域格式重置防旧版残留。构建脚本 build_design.py 代码层自动把模块页"标签+正文"两列行正文移C(不逐行改)。
- **足球宝贝英雄选定(v0.4)=爱莉希雅(Hero1040)**：性感派World Cup babe。

## X3 英雄换皮选角链路(可复用·2026-06-09)
- **英雄花名册**：`Hero__Hero.tsv` col4=名(全女性:格蕾丝/莉莉/斯嘉丽/鲁比/茉莉/海泽尔/赛米拉/阿米娜/克利欧佩特拉/爱莉希雅…) col7=品质(1普通/2稀有/3史诗/4传奇)。基础英雄id 4位(1001+),5位是升星变体。
- **判"D35内可获得"**：看 `DrawCards__DrawCards.tsv` col5=开服时间窗(如"开服1-21天"/"22-34天"/"35-59天")+col9=Hero。D35内招募UP池(全传奇):凌霜1043(D1-21)/夜玫瑰1042(D1-21)/艾琳娜1047(D22-34)/爱莉希雅1040(D29-34);星璃1044/露娜1045(D35-59)/佐伊1051(D60-89)超出。早期主线/常驻起手英雄(1001-1007低id品质2-3)全员D35必有。
- **⚠️坑**：平时出节日皮肤的脸(海泽尔1015/赛米拉1017/阿米娜1020/克利欧佩特拉1023)**不在常驻招募池**(活动限定获取)→D35内不保证可得,换皮选角避开。
- **英雄2D/Spine资产路径**(以Hero1040为例,换皮参考源)：立绘 `client/Assets/Res/UI/Spirits/Role/FullLength/Role_F_{id末2位}.png`、卡片 `Role/HeroCard/Role_C_40.png`、头像 `Role/Character Portraits/Img_C_H_40.png`、Spine `Res/Spine/Role_Spine_40/`。HeroSkin DK字段:DK_Fullbody/HeroCard/Head/Spine/Prefab。
- **足球宝贝概念图**：GRFal以本人立绘Role_F_40为reference换装(保身份换造型),脚本+图归 `KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\`。最终主稿=`足球宝贝爱莉希雅_主稿_FINAL.png`(=_FINAL_白金高质量_v2,白金10号+胸/裙金奖杯徽章+纯黑白足球+花球,零国家元素,高质量渲染)。**关键迭代经验**:用户认可某张"质量好但带违规元素(国徽/国旗/红队色)"的高质量图→以它当**质量/姿势锚**reference,prompt里逐条改设计(红→白金/国徽→奖杯/去脸颊国旗/去球袜商标字),既得质量又合规。
- **开箱活动UI换皮效果图**(`KB\产出-本地化与美术\X3\世界杯礼盒\`)：底=X3"天马藏宝阁"开箱活动UI截图`orig_ui.png`(非转盘);素材=世界杯足球礼盒(透明`WorldCup_box1_pick2_trans.png`)+足球宝贝主稿。**多图参考法**:call_grfal `--file reference_images=` 可重复传多张(append),三参考=原UI(布局/人物尺寸位置锚)+角色+礼盒,gemini保布局更稳。**踩坑**:GPT/gemini易把角色画成占满屏的大图→顶到/遮挡顶部UI文字+比例不协调;解法=用原UI当人物尺寸位置锚+prompt明确"角色中等场景插画、置于顶栏+标题文字带下方、不overlap任何UI文字、不oversize"。迭代:含奖杯足球版→去奖杯足球人物当主体→修遮挡照原布局(v5)→偏侧(v6人物缩太小)→**V7定稿**(人物按V5比例+礼盒缩小下移到脚前+小奖杯填空)=`开箱活动效果图_FINAL.png`(V7-V2小奖杯在礼盒右)。**全程工作流+14条踩坑见 `KB\方法论\X3_AI出图工作流_角色皮肤换装+活动UI换皮_世界杯案.md`**。
- **英雄换装概念图多轮迭代法(可复用)**：①首版用英雄本人立绘当reference→保身份换造型；②后续每轮用"上一版选中图"当reference,逐轮只调一处(R1初版含徽章→R2白金配色+去国家元素→R3胸口加风格化金奖杯印花),锁姿势+身份不漂;③call_grfal generate_image是long_running必submit-only+轮询,poll里print要套 `sys.stdout=io.TextIOWrapper(...,encoding='utf-8',errors='replace')` 否则GBK控制台崩。**IP注意**:赛事符号(大力神杯)用原创风格化(奖杯+月桂)不精确复刻FIFA商标;"去国家元素"指国旗/国徽,赛事奖杯印花不算。最终主稿待用户定(R3-v1简洁/v2华丽)。

## 设计定稿（4 轮问答确认）
- **主题**：2026 真实世界杯（6/11–7/6），周期 32 强→决赛 ~1 个月，节日级长活动。
- **核心飞轮**：竞猜 + BP 产「世界杯抽奖券」(唯一闭环货币) → 主抽奖消耗 → 英雄 + 足球拉拉队皮肤(限定)大奖。抽奖券只从竞猜/免费预测/BP 产出，只在转盘消耗。
- **三模块**：
  1. **主抽奖=世界杯开箱**(非转盘,2026-06-10改)：复用 `ActvCrafting`(ActvType=15,即"天马福箱"开箱,复用源 ActvOnline 101513)，提交抽奖券开箱+累抽阶梯+保底；表族 ActvCrafting/Reward(超级大奖标记)/OtherReward(累抽阶梯);字段 制作消耗道具/单次消耗数量/奖励池/阶段奖励组/本服排行榜/DK_箱子关闭图·开启图·底部遮罩图。
  2. **每日竞猜=独立Actv活动**(2026-06-10改:不是裸Pack,是独立ActvOnline+ActvType+TimeController的活动壳,每场竞猜礼包Pack挂在活动下)：一场比赛=一个竞猜活动实例（统一模板），运营按场逐配「免费/付费+价格档」；常规一场一个，决赛可多上。**实例内防对冲：玩家只能选一个结果、锁定不可改**（堵死买全部结果必赢漏洞）。付费=每个结果一个礼包(必得抽奖券)，买一个=押一个，猜对加送抽奖券；免费=每日1场免费预测，猜对小额抽奖券。
  3. **付费 BP**：独立、不绑竞猜，双轨进度，复用 `ActvScore`/`BattlePassScore`(7/22)。
- **合规规避**（最关键）：竞猜=买礼包，花钱必得抽奖券(有回报，非赌博)，预测正确只是额外 bonus。
- **★货币/积分决策(2026-06-10定·v0.6)**：①**不要单独积分概念**，抽奖券=唯一闭环货币(积分vs券本质=只增不减可做榜/里程碑 vs 消耗品) ②竞猜=**方案A(买礼包=竞猜)**，**不引入竞猜币**(竞猜币需服务端记押注=破坏零后端;它最大好处"强制竞猜"用③即可零成本达成) ③★**抽奖券不单独出售**(无"直接买N张券"的包,只从竞猜礼包/免费/BP产出)→想开箱必走竞猜=**强制竞猜**且仍零后端 ④**BP积分=原活跃来源砍50% + 竞猜途径加分**(竞猜BP用**GM命令**随每日结算一起发,不需BP-task原生集成);数值:活跃砍半后免费轨需竞猜补足才打满,付费竞猜档BP积分递增=付费加速。
- **★零新后端开发（2026-06-09 简化定稿）**：
  - **游戏内赛果展示界面 = 砍**（竞品都不做；玩家看资讯网站+结算邮件兼做赛果通知）。
  - **付费竞猜** = 买礼包，订单自带记录；**免费竞猜** = $0 领取"竞猜票"，领取日志记录所选结果。两者都有日志，无需服务端单独存预测。
  - **结算 = 纯运营动作，不做成后台功能**：运营看资讯网站拿赛果 → 查日志(付费订单+免费领取)命中买对/猜对玩家 → 用现成 bulk-mail 批量发 bonus 抽奖券+结算邮件。整个活动退化成「配置+美术+运营SOP」，零程序新开发。
  - **风险**：依赖运营每日手动结算，策划案需写 SOP + 漏发/错发补偿。
- **深度付费**（套 [[p2-x3]] 教训）：竞猜礼包 $4.99/$9.99/$19.99 阶梯(补中段断层,高档加送更多券) + 转盘中段 GACHA 拉复购 + 顶端足球拉拉队皮肤套装做情感向高价外显 + BP 抗衰退。投放节奏套 P2 四阶段：小组赛引流(免费/低价)→淘汰赛付费深化→决赛多实例高潮。

## X3 可复用资产盘点（2026-06-09 Explore，跨案可复用）
- **抽奖**：`ActvLuckyWheel`(10) 自带三层保底——超级大奖 `SRewardNum`/`SReward=1`、累抽档位 `ActvLuckyWheelOtherReward`、累抽次数触发礼包；20+ 历史实例(1001-1023)；消耗活动专用券。另有机甲双层转盘 `ActvMechaWheel`(6, 翻倍保底 MultiplierPityCount)、许愿池 `ActvWishingPool`(50, 阶段保底, 仅 TT=1)。
- **BP**：原生 `ActvBattlePass`(11) 过简陋(无双轨/无进度条字段)；**付费通行证走 `ActvScore`/`BattlePassScore`(7/22)**(积分阈值=等级+免费/付费礼包白名单)，落地时验字段。
- **竞猜**：X3 **无任何竞猜/赛事预测框架**；最接近=猜谜 `ActvUnderpants`(31)但仅是非题。→ 竞猜必走"礼包+后台结算"轻量路线，不新建框架。
- **足球/拉拉队皮肤**：客户端**零现成资产**，需美术新出英雄皮肤 FBX。英雄皮肤目录 `client\Assets\Res\Unit\Role\OutsourcingRes\{英雄名}\`，配置 `Hero__HeroSkin` 字段 DK_Prefab/DK_Head/DK_Fullbody/DK_Spine/DK_HeroCard。
- **奖券道具**：Item `114x` 段可预留(1140-1150)，绑 `UseActivityID`→抽奖 ContentID；现有券命名"XX券/凭证/币"(1026-1143)。

相关：[[x3]](策划案模板) · [[p2-x3]](深度付费教训) · [[x3]](付费机制速查 monetization) · [[reference_x3_config_library]]
- ⚠️红线变更(2026-06-10):竞猜界面队徽可直接用真实国家队的(用户放开);无国旗国徽仅保留在皮肤/开箱场景。

## 决赛助威动态表情(2026-06-16立项,区别于小组赛48静态)
- **决赛专属·真动效**:动作=**双拳振臂过顶+仰头大喊GO**(决赛级助威,不夹气不庆祝/不举杯——还没夺冠);覆盖=**决赛2队各1个**(队伍出来再套队色+脸彩,现先出中性模板验链路)。
- **技术链路=动态行军表情(dynamic_march_emoji,非图生视频)**:x3-media一张图出**4×4逐帧sprite sheet**(透明1024,每格256,首尾可循环)→切16帧→合成循环GIF→.bytes进Emoticons(Res字段指动图,跟现有22个动图机制一致)。比图生视频可控省钱。
- 角色锚=Q版爱莉希雅啦啦队(沿用小组赛FINAL形象);模板产出存`KB\产出-本地化与美术\X3\世界杯竞猜界面\决赛助威表情\`。
- 落地同小组赛:Emoticons表(新ID,接348+)+Item表情包道具+DK+i18n;决赛队定后套色。
- ✅**链路验通(2026-06-16)**:dynamic_march_emoji出4×4 sprite sheet(2048,gpt,2候选)→切帧(切16格+alpha阈值二值透明+合成循环GIF)→`决赛助威表情\_preview_v1/v2.gif`循环动画。模板=`WC_Final_Cheer_template_4x4_v1/v2.png`中性白底。**待用户选候选+决赛2队定后套队色**。注:AI 4×4逐帧角色一致性可能飘,正式版盯帧间脸型/裁切一致。
- 📋**生产模板已固化(决赛队定了照此跑)**:`决赛助威表情\_生产模板_prompt+流程.md`=prompt全文+三步流程(**S1先出该队球衣定妆图→S2用它出4×4逐帧→S3切帧成循环GIF/.bytes**);切帧脚本`_slice_4x4_to_gif.py`可复跑。

## v0.27 ActvType64+测试配置落地(2026-06-12)
- **路由终版=新 ActvType 64**(用户先说62但62=链式礼包已占,拍板新开;64=首空号)：ActivityWorldCupGuessCondition(CSSharedHotfix,标准[ActivityTriggerCondition]映射,server块照抄进度礼包建包流程复用progressPackData)+ActivityConst.TRIGGER_TYPE_WORLD_CUP_GUESS=64；**已删除 type29 按 ContentID 分流 hack**(ActivityMeta/UI类的IsWorldCupGuess全清)。⚠️dev服务端需带此代码构建才认识64。
- **测试配置已推 gdconfig dev_festival(041b125)**：双实例同时在线验多实例形态——102911付费场($4.99,Pack 891101/02,奖励组291101=20券[1134一封情书占位]+500钻+100K金) + 102912免费场(GemPrice=1钻占位,Pack 891103/04,291102=1券留资产记录)；TC 2911/12(部署起算30天)；MailID=101109；ActvPack.FinalReward=291102(防依赖校验,钻空上限1券)。
- 决策：免费包1钻占位(零钻无先例/UseGem推导不明,上线前问程序)；加送值=Pack.Desc中文直填"猜对加送 +15/+5"(i18n后置)。
- 配表新知识已沉淀进 x3-config-export SKILL.md(新增整行流程/PackPrice档位id/gate实操)。
- 剩余：导表验证(jolt跑着)→igame部署dev→用户登号验收→生成器收口+DK注册+入场动画(跟客户端)。

## v0.28 demo验收通过+48队铺量启动(2026-06-13)
- **demo 全链路跑通**：真机界面+互斥状态机(Cheered/Locked)+文本(走自动key管线修复)全验证。免费包 1 钻定版(用户拍板,零价确认砍掉)。
- **★配置表文本=自动key管线**(返工2次学费)：单元格内容不进客户端,proto写死拼 TXT_{表}_{字段}_{行ID} 查i18n bytes;新行文本必须把自动key写进Text表;详见 x3-config-export SKILL.md。
- **48队铺量**(2026=48队制,非32强!名单已抽签定):①队伍板48张=程序绘制完成(`scripts/draw_wc_team_panels.py`含48队队服主色表,KB\...\队伍板48\) ②队徽=AI合体徽(用户定不拆框),巴西徽风格锚+国旗盾面+双底差分,试点4队(德日法英)→过审后42队分5批 ③队名key 48×10语种待配置时入Text表。
- 剩余待办：试点质检→批量42徽→DK注册→生成器收口/入场动画(客户端四件套对齐,零价已砍)→真券道具→比赛列表入口界面。

## v0.32 竞猜v2全量落地+界面文本全空根因(2026-06-17,commit 7d4e5f1/46dd299/e6b25d1/83bc5d4)
- **v2结构(替换v1)**：56付费+17免费=73实例;对阵=模拟32队晋级树(全唯一,修掉v1跨轮重复bug);外显按轮次(头像框/聊天表情**不重复投**)=16强该队框/8强框宝箱+该队表情/半决赛晋级之路框+表情宝箱/季军双宝箱/决赛世界之巅框+表情;免费=每比赛日1场(GemPrice col8=1=1钻购买,非price0领取);$4.99去金币。生成器`gen_wc_backup_v2.py`+替换`_apply_v2_to_live.py`。备份`_stage_v2\README_备份说明.md`。
- **★★最大坑(反复踩4轮)：X3配置文本=自动key管线,配置表单元格字面值客户端完全不读!** 源头`client\Assets\Scripts\CSShared\Common\Cfg\CfgProtoTextEx.cs`(每个文本字段getter拼死key)。界面文本全空=没建对应自动key:
  - 活动标题/描述 = `TXT_ActvOnline_ActvName_{活动ID}` / `TXT_ActvOnline_ActvDesc_{活动ID}` (不是col2/col3,那俩只是编辑器备注)
  - 礼包队名/猜对加送 = `TXT_Pack_Name_{礼包ID}` / `TXT_Pack_Desc_{礼包ID}` (不是col35/col36)
  - 规则弹窗 = `TXT_RuleTips_Tab/Title/Content_{规则ID}` (不是RuleTips行的Tab/Title/Content列)
  - **判定法**:界面文本空→去CfgProtoTextEx.cs搜该字段getter看拼的key名→Text表建该key。**新增任何带文本配置行,必须把自动key写进Text表**。猜对加送想"共享一个key"做不到(代码`bonusTips.text=packCfg.Desc`强制per-pack),要共享须改客户端那1行读shared key。
- **竞猜活动字段映射(全破解)**:ActvOnline: **col13=ActvRule(规则RuleTips ID,如1190)** / **col38=GroupId(活动组,世界杯=139,ActvGroup表已存在)** / col4=TC/col5=type64/col7=ContentID/col21=DK_WC_ActvIcon。Pack: col6=Price(USD)/col7=PackPrice(IAP id)/**col8=GemPrice(钻石价,免费场填1)**/col13=Content(Reward组)/col25=Head(队伍板DK)/col27=Icon(队徽DK)/col40=UnionGiftCfg(商会赠礼)。客户端读逻辑见`UIActvWorldCupGuess.cs` RefreshSide。
- **xlsx-tsv gate 实操坑(沉淀)**:①`sync_xlsx_tsv`留`.tsv.bak.*`→pre-commit hook当未暂存tsv拒,commit前`rm`掉 ②tsv行数减少(shrink)→`--from-tsv`留空尾行→openpyxl删尾行trim ③`git checkout`还原xlsx刷新mtime>tsv→gate判断不了源方向(refuse),`touch` tsv或两边改一致 ④RuleTips.xlsx有合并单元格→`--from-tsv`清表重写炸(MergedCell read-only)→openpyxl直接append行 ⑤**正确姿势=tsv+xlsx都改到`--check`mismatch=0/crlf=0,再`git add`两边一起(hook识别两边一致放行"auto action staged")**;只stage单边或两边不一致都被拒。
- 验证:导表#998(v2)/#1002(规则)/e6b25d1/83bc5d4均SUCCESS分支dev_festival。剩:3里程碑款美术(晋级之路框80348/世界之巅框80349/世界之巅表情15748,现临时宝箱占位)+客户端拼prefab。

## v0.30 竞猜56实例填真队伍落 live(2026-06-16,commit 4783e4d dev_festival)
- **56实例全配齐**(随机48队22-24对·种子2026验证美术,作模板对阵定后改`pairs`重跑覆盖)：ActvOnline 102920-975/ActvPack&TC 2920-975/Pack 892001-112(每实例两队各一包)/Reward组291401-448(48队组·行24800-25039)/Text 231行。分布对齐甘特图(32强16×$4.99/16强8×双档/8强4×三档/半决赛2/季军1/决赛1)。生成器=`KB\产出-数值设计\X3_世界杯\gen_wc_guess_filled.py`+落地`_apply_to_live.py`，**完整字段映射/落地步骤复盘见同目录`_stage_activities\README_同步说明.md`**。
- **★Pack队伍展示字段(本次破解,proto字段#≠tsv列#)**：Head=**col25**=队伍板`DK_WC_TeamPanel_{码}` / HeadShowTime=col26(int) / Icon=**col27**=队徽`DK_WC_Badge_{码}`；队名/加送文案走**i18n自动key**`TXT_Pack_Name_{packID}`/`TXT_Pack_Desc_{packID}`(非Pack列)；奖励组=Content=col13。
- **商会赠礼=Pack col40=UnionGiftCfg随IAP价格档**：$4.99→202/$9.99→203/$19.99→204(201=0.99~2.99/202=3.99~7.99/203=9.99~14.99/204=17.99~29.99)。克隆模板891101会带残留 col35="巴西"(改按队队名)+col36="猜对加送 +15"(清空)。
- **落地踩坑**：①Text表27列(克隆模板易按17列手搓→列数不匹配)②`sync_xlsx_tsv.py --from-tsv --files` 要传**tsv**路径不是xlsx(传xlsx静默不写,openpyxl保存175表慢必走后台)③行号被别人占(行24710被RewardID30585占)→现查max另选24800段④只git add自己6tsv+6xlsx,别碰他人在途`_staging_weeklycard`。
- 奖励组按档：$9.99=券40/钻5000/VIP50+该队框道具(80300+idx)+1148自选框宝箱；$19.99=券80/钻10000/VIP100+该队表情(15700+idx)+1149自选表情宝箱；$4.99=共享291101。队码↔道具idx对齐(PersonalizeAvatarFrameCfg按cfgID升序,已验ECU=80315/15715)。

## v0.29 48队美术批量收官(2026-06-13)
- **48队全齐**(2026美加墨48队制,官方分组名单已查证)：队伍板`队伍板48\WC_TeamPanel_{三字码}.png`(程序绘制,draw_wc_team_panels.py含48队队服主色表) + 队徽`队徽48\WC_Badge_{三字码}.png`(AI双底差分,巴西徽风格锚,alpha全员合格零次品256透明,BRA/ARG已归拢)。三字码=FIFA标准。
- **⚠️队徽抠图返工(2026-06-16,双底差分埋的雷)**：上面"alpha全员合格"是**误判**——当初只看四角净/没量中段半透明。实测`队徽48\`**42/48张半透明15-35%**(中段alpha散布=毛边/虚影/重影,NZL/SWE肉眼可见重影只是最极端表现),仅ARG/BRA/GER/JPN/ENG/FRA 6张达标(<13%)。**根因=双底差分**(生白底+黑底两次gpt生图有漂移,反推alpha对不齐→错位重影+半透明,同[[reference_x3_cosmetic_resource_paths]]里march-emoji"双底差分重影79.6%"同坑)。**★抠图质量真判据=中段半透明占比`(30<a<225)`**,标杆ARG/BRA≈1%,>13%即不干净;不能只看四角或硬化后数字(硬化把噪点归0/255会假性达标但RGB重影还在)。**正解=单次生成白底图→GRFal `remove_background`→256**(NED/KOR/COL/POR试点验证0.7-2.2%达标,复杂图案如太极/国徽也清晰,无重影)。试点目录`队徽48_重出试点4\`+`队徽48_重出NZL_SWE\`,锚=`.cache_wc_anchor\BRA_badge.png`。**待用户定重出范围**(全42张/只❌严重>25%的21张)后批量。⚠️remove_bg worker偶发存错路径`C:\Users\linkang\ADHD_agent\...`需挪回。
- **★队徽设计=足球+国旗盾合体勋章(2026-06-17定稿,大返工)**：①**纯抠图救不了**——纯盾徽(无足球)用户全否,标杆ARG/BRA本就是**足球+国旗盾合体的圆形勋章**,纯盾/硬化/双底差分全是歧路。②**prompt演进**(踩4轮):纯盾❌→"replace Brazil crest"❌(模型抠着巴西盾形/黄菱/星星不放,串味)→"放宽自由画"半对→**终稿✅**=`Reference images are Brazil and Japan World Cup team medals/emblems. Following the same style and format, generate another World Cup team emblem for {国}: a soccer ball combined with {国} flag shield. The shield is purely {国} own flag ({国旗描述}). Centered, ~80% of frame, white background.`③**双锚=BRA+JPN**(单BRA锚易串巴西元素,加JPN后模型理解"同系列勋章"更稳;锚图`.cache_wc_anchor\BRA_badge.png`+`JPN_badge.png`)④后处理remove_background→256。⑤**验证**:FRA/JPN/CRO格子/AUS米字星/MEX鹰徽 全过(盾内纯净无串巴西/复杂旗清晰/0.7-2.2%透明),试点`队徽48_勋章试点2\`。待开48队全量。**旧的纯盾返工目录(重出FINAL/重出试点4/重抠试点等)全作废**。
- **✅48队徽全完成(2026-06-17)**：足球+国旗盾合体勋章版48张齐,在`队徽48_勋章FINAL\WC_Badge_{三字码}.png`(256/透明<5%/占画面~82%统一)。总览`_总览48_FINAL.html`(生成器`_gen_badge_overview_final.py`)。**国旗逐张核对**:NZL/RSA/UZB/QAT/ESP 5个小众旗初版画错(Y字形/9齿锯齿/新月星等),按"prompt写全旗细节+强调must be X flag exactly"重出修正。占比标准化工具`_normalize_badge.py`(AUS/PAN/IRN偏大已修)。**落地待办**:降客户端尺寸→Pack.Icon配DK引用。其余试点目录(带球版/放宽/精简/整盾替换/勋章试点)可清理。
- **★小众旗终极解=真实国旗图当参考锚(2026-06-17,RSA/QAT二次返工验证)**:RSA南非Y字形6色旗/QAT卡塔尔9齿锯齿,纯文字描述写多详细gpt还是画不准。**终解=把真实国旗png加进reference_images当第3张锚**(`flags_48\{FIFA码}.png`已有48国真实旗),prompt写`reference image 3 is actual {国} flag — copy its exact pattern`,照临摹就准。小众/复杂旗(格子/Y字/锯齿/徽章)都该带真实旗锚。锚拷`.cache_wc_anchor\{码}_flag.png`。
- **⚠️remove_bg偶尔没抠净留白底(2026-06-17,AUS)**:worker remove_background偶尔主体外圈留片254白没抠(四角透明但盾/球间残白),目视才发现(alpha统计四角=0会漏判)。修=本地洪水抠白,种子取"四边白+邻接已透明区的白像素"(纯四边种子会被已透明四角卡住)。**收尾全48目视扫残留白底**,别只信alpha统计。
- **✅队徽资源替换并push(2026-06-18,7daffdef5da)**:48定稿覆盖client`Assets/Res/UI/Spirits/ActvWorldCup/WC_Badge_{码}.png`(同名覆盖,.meta未动→DK引用不变,无需重注册)。**⚠️在途仓库有别人WIP时安全push套路**(x3-project仓根=`C:/x3-project`非client子目录,ProtoGen/*.bytes是别人未提交WIP):①只`git add`自己48png ②别人的改动若已混进暂存,从**仓根**`git restore --staged <仓根相对路径如client/...>`撤出(在client/子目录里撤路径基准不符无效) ③push被拒(远端有新提交)→`git stash push -u`暂存别人WIP→`pull --rebase`→push→`git stash pop`还原。**⚠️但若别人WIP含导表生成物(ProtoGen/*.bytes等)且rebase拉进了同文件新版,`stash pop`会撞出UU冲突(2026-06-18踩坑)**——这类生成物本就不该stash保护(随最新导表重生成)。**冲突收拾=`git checkout HEAD -- <冲突路径>`恢复到远端最新版+`git stash drop`弃旧,生成物以最新为准**。④rebase后`M gdconfig`子模块指针=别人推进子模块的在途状态(子模块checkout在新commit但父仓指针记旧),**非自己改动,绝不`checkout HEAD -- gdconfig`**(会把别人的新子模块退回旧版),原样留给改子模块的人。先`git ls-tree HEAD gdconfig`vs`cd gdconfig;git rev-parse HEAD`确认方向再判。
- **⚠️小众国旗gpt易画错(2026-06-17,NZL头像框踩坑)**：新西兰头像框国旗球画成了非新西兰旗。**根因**=prompt只写国名/简略描述时,gpt对**小众/复杂国旗**(新西兰深蓝+米字+南十字红星、刚果、佛得角、乌兹别克等)易凭印象画错。**修=prompt里把国旗细节写全+强调"必须是X国旗、不是纯旗"**(NZL改`dark navy blue with Union Jack top-left + four red stars white-border Southern Cross — NOT a plain flag, must be NZ flag exactly`,重出即对)。**铁律=48国出完必逐张核对国旗准确性**(尤其小众旗),别只验透明度/构图。头像框+队徽两个模块都适用。**⚠️NZL队徽manifest里写的是"silver fern银蕨"非国旗**——派NZL队徽前确认用国旗还是银蕨。
- **⚠️AI出图主体占比不一,需套版标准化(2026-06-17,队徽勋章版)**：gpt出的勋章主体占画面比例飘(实测IRN/AUS顶满100%,标杆BRA/FRA~82%),换队替换会大小漂移。**标准化工具`KB\...\世界杯竞猜界面\_normalize_badge.py`**(trim真实主体bbox→等比缩至长边=画布*0.82→居中贴256透明画布;alpha>40阈值避抗锯齿噪点)。收尾对全48队跑一遍统一占比(IRN已标准化82%,AUS待处理)。同[[reference_x3_cosmetic_resource_paths]]里48队徽老版"占比82~100%套版"同坑同解。
- **⚠️批量生成清单漏队踩坑(2026-06-17)**：勋章版重出脚本`_gen_badge_final42.py`的国家字典**漏了ESP西班牙**(48队只生成41个待跑,减已OK6应是42),收尾对账`set(ALL48)-set(done)`才发现缺ESP+JPN汇入路径写错。**铁律=批量脚本生成后立即`len()`核对数量对不对**(41≠预期42就该查),收尾必用全48集合做差集对账,别只数"跑了多少"。ESP已补派。
- **★批量worker model坑(已进x3-media SKILL.md)**：派media-worker不指定model会继承主agent session model;撞claude-fable-5(子agent不可用)→整批"model may not exist"全挂,已提交生成白费。修=Agent调用显式 model:"sonnet5"(工具型worker够用快省)/"opus"。第一批8个全挂后切sonnet5/opus重派救回。
- **批量流水线打法**：每队1 task json(_wc_badge_batch_manifest.json台账)+逐队国旗英文描述;分批8个并行派(并发上限~16);完成通知驱动滚动派下批;以"目录有无合格png"为真相源对账,worker假death/残留轮询不影响已落地图。
- **★48徽尺寸规范化(2026-06-14修)**：批量AI徽章在画布里占比不一(82%~100%顶满),换队替换会大小漂移。修法=以巴西/阿根廷模板占比(主体84%居中)为基准,全员统一缩放对齐→1:1套版(叠版验证盾/球轮廓重合)。**两个坑**：①`getbbox`被alpha噪点(边角抗锯齿淡像素alpha1~3)骗成满画布256→必须先alpha阈值化(p>=30)再取真实主体bbox ②规范化=trim真实bbox→等比缩至max边=215px(84%)→居中贴256透明画布。脚本含备份(_raw_备份/)。
- 剩余落地待办：①48板+48徽落仓客户端Spirits\ActvWorldCup\ ②注册96个DK ③48队名key入Text表(国家名10语种) ④Pack配置填DK字段。需用户Unity配合DK导出一次。

## v0.30 48队支持表情立项(2026-06-15)
- **走可售卖聊天表情系统 Emoticons**(非快捷回复/非custom_emoji1/非HeroStickers羁绊册)：主表`Emoticons__Emoticons.tsv`(ID/Res/Pack/Name/ShowType/备注)+图`Spirits/Emoticons/Icon/icon_global_*.png`**256×256**+气泡底ui_chat_memebg_*+Path_Emoticons.asset注册；解锁=Item 154xx表情包道具(ItemType24,param=Emoticons.ID)。完整链路见 KB `X3_外显生产链路…md` §1.2。
- **决策(2026-06-15)**：①美术=**队徽+加油元素**(在已完成的48队徽`队徽48/WC_Badge_{三字码}.png`256×256基础上加欢呼拳头/挥旗/彩带/呐喊文字,**复用队徽省成本**,256尺寸与Emoticon icon一致) ②发放=**竞猜礼包附赠**(押某队的竞猜礼包附带该队支持表情,强化"支持本队"情感)。
- **落地量(48队)**：48行Emoticons表 + 48个256×256 icon(队徽加工) + 48个154xx解锁道具 + 48×10语种队名key + ~96 DK(icon+道具icon)；ID开世界杯专属新段。
- 建议先试点4队(德日法英,跟队徽试点同批)验"队徽+加油元素"处理→过审再批42。
- 剩余:试点出图→批量→DK注册→Emoticons表+154xx道具配置→挂进竞猜礼包奖励。

### v0.31 应援表情走向定稿(2026-06-15)
- **画风路线推翻"队徽+彩带"** → 改 **Q版英雄穿球衣应援**(对齐现有Emoticons都是Q版角色半身,非盾徽)。**模型=单角色固定动作+48队球衣轮换**(像队徽套版,主体换成角色)。
- **主体角色锁定=爱莉希雅(足球宝贝1040)**,世界杯官方IP。母版动作=双手举金色花球+张嘴欢呼,纯白金描边球衣(留白便于换队色),透明底Q版半身。母版=`KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情_Q版\WC_CheerMaster_Aerisia.png`(gpt生,march_emoji类型,x3-media派media-worker)。
- **48队球衣参考表**=`同目录\48队球衣参考表.md`(全48队主色/辅色/图案,合规口径取配色版式不复刻品牌logo,来源Footy Headlines)。换衣建议球衣+花球一起染队色(半身像球衣占比小,识别要靠队色整体)。
- **流水线**: 母版(已出待审)→换48队球衣(以母版为锚img2img只改躯干区)→DK注册→Emoticons表+154xx道具→挂竞猜礼包附赠。
- ⚠️**应援表情格式终版(2026-06-15 多轮迭代后定)**：Q版爱莉希雅穿**真实足球球衣球裤**(白色中性)+**双手高举一面真实国旗过头呐喊**(国旗=队伍识别主元素)。母版基于**候选2**(`WC_CheerMaster_Jersey_hires_2`)改成举空白浅灰矩形旗=`WC_CheerMaster_Flag`(生成中)。
  - **演进史(别走回头路)**：啦啦队装+花球❌→真实球衣+举围巾❌(围巾换色弱标识)→**真实球衣+举真实国旗✅**(用户拍板,国旗最准最清晰)。旧母版`Aerisia_v2_1`(啦啦队)+`Jersey_1/2`(围巾)+4张啦啦队试点(德英日法)**全作废**。
  - **48队国旗合成流水线**(零AI逐张、纯合成保证准确一致): 48面真实国旗已从 flagcdn 下载存`flags_48\{FIFA码}.png`(FIFA三字码→ISO2映射在`_gen_flag_emote_48.py`,ENG=gb-eng/SCO=gb-sct);合成脚本`_gen_flag_emote_48.py`=母版举空白旗→真实国旗透视贴旗面四角QUAD+乘算保留布料褶皱阴影+缩256;母版出图后量QUAD填入即跑48,输出`应援表情48_举旗\`。
  - **白球衣决策**:球衣留白中性,队伍识别全靠国旗;团队若要球衣也染队色=后续追加。
  - ⚠️**举旗合成两坑(2026-06-15实测,第一版糊脸作废)**：①旗必须举在**头顶正上方、整面不与头脸身体重叠**,否则国旗**中心图案(日本红圆/巴西球徽)被脑袋挡**没法看→母版`WC_CheerMaster_Flag`(旗在头后)废,重出`WC_CheerMaster_FlagTop`(旗在头顶上方)。②合成旗面遮罩**不能只按浅灰**:角色白金发+白球衣也是低饱和浅色会撞色被误贴国旗→遮罩收紧=低饱和(sat<16)+亮度190~232(排亮白球衣)+非暖色(R-B<10,排白金发/肤色)+quad内。脚本`_gen_flag_emote_48.py`已含修正。
  - ~~举旗48版~~(`应援表情48_举旗\`,母版FlagTop_1)**用户否决**:举旗版body不如啦啦队、贴真旗显糙。流水线/脚本`_gen_flag_emote_48.py`+48国旗`flags_48\`留档可复用(未来要"贴国旗"类合成可直接用)。
  - 🎯**应援表情终极方向(2026-06-15用户定·已试点验证)=「脸彩国旗+队色队服」啦啦队版**：以最初啦啦队 Image#1(`应援表情48\WC_CheerEmote_ENG_raw2.png`,双花球+队服上衣短裙)为角色/姿势/画风锚,AI逐队画三处:①队服(上衣+短裙)换队色 ②双花球换队色 ③**脸颊画小国旗face paint**。透明底256。
    - **核心规律(验证得出)**:**队服配色/图案=主识别,脸彩国旗=补充**;两者叠加→简单旗(日蓝+红圆)和复杂旗(墨竖三色+鹰徽/克红白格)都能认出国家。有特色队服的队(克罗地亚格子/英格兰十字/巴西黄绿)靠队服就够,脸彩锦上添花。
    - 试点4队全过(`应援表情48_脸彩试点\WC_FaceEmote_{JPN,BRA,MEX,CRO}.png`+对比页`_试点4队对比.html`),特意含墨/克复杂旗。
    - **生产方式**:AI逐队gpt生成(以Image#1为reference锚同角色同动作),每队kit描述查`48队球衣参考表.md`+脸彩国旗;分批并发media-worker。
    - ✅**48队全部完成(2026-06-15)**:成品`应援表情48_FINAL\WC_FaceEmote_{FIFA码}.png`(每队1张规范名256透明)+`_总览48.html`+`_QC接触表48.png`+`_README.md`。一致性质检通过。
    - ⚠️**落地前发现关键链路(2026-06-15)**:Emoticons系统现有22个**清一色动图GIF零静态**——配表`Res`字段指`DK_{名}`→`Res/UI/Gif/{名}.bytes`(发到聊天会动的GIF),`icon_global`静态PNG只是面板缩略图(双DK,详见[[reference_x3_cosmetic_resource_paths]])。**我们48张只是静态(=icon那半),缺动图GIF那半**。配表卡在此:Res无动图可指。**待用户定**:A先上静态(PNG→单帧gif.bytes,能用但不动,这套里唯一不动略突兀)/B给48加循环动效(花球摇摆轻跳,程序可批量非逐个AI)/C静态先上动图后补。定了再→48 DK注册(双DK)+Emoticons表48行(世界杯新ID段)+154xx道具→挂竞猜礼包附赠。
    - ✅**结案=A静态先上(2026-06-17用户定)**:48张PNG→单帧gif.bytes已落仓Emoticons表(ID300-347/Res=`DK_WC_{码}`/`Res/UI/Gif/WC_{码}.bytes`)。**踩坑+修复**:聊天里显灰底/白框=GIF背景色索引(0)≠透明色索引(255)触发`UniGifDecoder`第0帧填充bug(详见[[reference_x3_cosmetic_resource_paths]]表情段"GIF .bytes透明铁律")。已批量修48张(`background=transparency`+透明调色板设白),client `dev_festival` commit 9458fd4753d 已push。**生效待重建client资源包+更新dev服**(同line238)。
    - 演进总史:啦啦队白装❌→真实球衣举围巾❌→举国旗(头顶)❌→啦啦队脸彩+队色✅(留住爱的啦啦队+脸彩解决认不出国家)。
    - **44队批量经验(2026-06-15)**:分4批(12+12+12+8)滚动派media-worker;偶发失败两类——①单worker socket断(error="socket closed",task卡running)②GRFal gpt跑满3次>1200s超时(error step=generate);均非真错误,reset task为pending+同task_id重派即解。以"目录有无该队256 png"为完成真相源对账,manifest=`应援表情48_脸彩\_manifest.json`。③**worker出图命名不统一**:有的存规范名`WC_FaceEmote_{码}.png`,有的出2候选存`_256_1/_2`/`_1_256`/`_2_256`变体→按规范名glob会漏数;对账/归一化要用正则`WC_FaceEmote_([A-Z]{3}).*256`匹配任意候选,最后**归一化**(每队挑1候选→规范名)再拼总览。④**第三类假成功(2026-06-15头像框国旗化试点实测)**:worker报`TASK_DONE success`且task.result.saved_to有路径,但文件**实际没下载落地**(目录里没有)→必须`os.path.exists(saved_to)`实查兜底,reset+重派补;**铁律=task状态/通知都不可信,唯一真相源=目录里有无该文件**。⑤**needs_auth常是误判**(2026-06-15头像框全量批):单worker报needs_auth别急让用户刷Cookie——GRFal已迁token device flow(config里grfal_cookie/GRFAL_COOKIE env都空是正常),先跑`grfal-api/scripts/call_grfal.py --list-tools`探活,通=认证活着=误判→直接reset+同task_id重派。⑦**worker对中文路径reference偶发误判(2026-06-16晋级档模板)**:reference_images指向含中文路径(如`头像框_48_FINAL\..FRA.png`)时,个别worker报`reference image not found`(failed)或`needs_auth`,但文件实存+认证活着。解法=锚图拷一份到**纯ASCII路径**(如`C:\ADHD_agent\.cache_wc_anchor\FRA_base.png`),task的reference_images改指ASCII副本再重派。偶发非必现(同批其他中文路径worker也能成),失败的重派必换ASCII。
  - 确认48齐后→DK注册+Emoticons表48行(世界杯新ID段)+154xx表情包道具→挂竞猜礼包附赠。
- ~~母版v2定版~~(已被上面服装修正推翻)=`WC_CheerMaster_Aerisia_v2_1`(全身Q版啦啦队装)。**踩坑(已进x3-media type-march-emoji.md)**: Q版角色AI图生图**禁双底差分transparify**(两次生图漂移→重影79.6%)，改单次生成+普通去背(降到4.3%)。试点4队(德日法英)走 march_emoji+gpt以母版为锚换队色,德/英已验证同人同动作只换球衣成功(`应援表情48\WC_CheerEmote_{码}.png`+_hires)。换衣描述源=`48队球衣参考表.md`。
- ⚠️ X3表情系统认知(详见 [[reference_x3_cosmetic_resource_paths]] + KB`X3_外显生产链路…md`§1.2): 可售卖聊天表情=**Emoticons**(256×256,Emoticons表+154xx表情包道具ItemType24),节日通行证卖的就是这套;现有22个全是Q版英雄半身(贝拉/猫神/舞者…)。

## ⚠️v0.12 重大设计变更(2026-06-10 用户Sheet手改固化)
- **推翻v0.6③「抽奖券不单卖」**：改为**有单独出售但ROI低**(低于同价竞猜礼包)——硬强制竞猜→**软引导**(竞猜礼包=获券最优解;直购券包=大R跳过通道,多一条付费线,GACHA复购引擎回归,深度上限打开)。
- **价格档改**：.99(普通场,**全程覆盖**每场有)/9.99(16强起**焦点战**)/9.99(8强起焦点战,新增)——删.99;删皮肤套装预热排期行。
- 🔧待定:焦点战与一场一档的关系(高档替换低档or焦点场同场多档)/直购券包与9.99档数值。
- **总览v0.11重构**(给制作人,一眼框架):飞轮改「核心循环」+图位(用户手动贴图)/深度付费一句话/模块目录(HYPERLINK跳转,build脚本post-step用USER_ENTERED写公式,RAW会变文本)/甘特并回总览(总览页不wrap靠OVERFLOW溢出,列宽均匀150)/「活动说明」表(模块|形式|开发量|复用新增)。
- **签到模块4(v0.10)**：纯复用换背景,ActvType=14补签登录/ActvLogin表/复用源101402;7日一期发少量抽奖券(补免费盘)+补签钻石;背景复用竞猜B背景层零美术增量。

## v0.13 数值锚定(2026-06-10·完全对齐夏日开箱)
夏日参考表: GSheet 1mUTq8_8OsPVbGfISOSdGav-1K2p_PiQwqj8vpUIfF3M 「2）活动策划案」(gid=1228951972,开箱段A40-198/礼包累充段A199-310)。
- **券面价/usr/bin/bash.25/张**(=夏日一封情书)·开箱1次10券=$2.5·**保底200→100次**(坑深$250=夏日赛米拉皮肤门槛)·阶梯5/20/40/70/100(终点=超级大奖)
- **传统礼包带券(锚点/连锁/累充)**: 按**$0.50/张**投放(面价×2计价=ROI折半=偏低;夏日gacha道具按锚点50%投放口径);P2X2实证累充加gacha道具→超大R ARPU+20%;直购券包≥$0.50(ROI最低,🔧待定)
- **焦点战=多档并存**(定稿): 焦点场同场$4.99+$19.99/$49.99;防对冲锁【方向】,同方向各档限购1可叠买,反方向全锁
- 奖池: 万分比总权重10000,高价值低权重(夏日11301-11308模式);调ROI=砍高价值权重移低价值,总权重不变;开箱线ROI目标~50%

## v0.14 尼罗道具循环白皮书校准(2026-06-10)
白皮书位置: KB/产出-数据分析/26尼罗河活动道具循环.html(★X3开箱/转盘活动数值真锚,比夏日表更细)。核心口径:
- **尼罗券双线**: 连锁A线(ChainPack482,pack_type=11)=券+宝石+VIP经验,免费档穿插(1/5/10/20/50/100),全通$184.95→926券; 锚点B线(pack_type=15)=纯券同价同量无资源($4.99=20/$19.99=80/$49.99=200/$99.99=400=**$0.25/张**),全买$174.96→700券=A线后的追加
- **世界杯校准**: 竞猜礼包必得=尼罗同价档(20/80/200),bonus=必得50%(10/40/100);传统礼包=尼罗A/B线模板;直购券=B线锚点本身(ROI偏低);累充附赠$0.50/张(夏日口径)
- 尼罗另有二级循环(券→兑换积分→兑换商店+纪念卡Lv30无限消耗端,全通需378张),世界杯本期简化不做
- 券面价 $0.25/张 三案一致(尼罗B线=夏日一封情书=世界杯)

## v0.15 兑换商店+累充加入(2026-06-10,推翻v0.14简化)
- **模块5兑换商店**(跟夏日):开箱奖池产出「世界杯纪念币」($0.01/个=夏日玫瑰花瓣)→ActvExchange兑换 历史皮肤(1500币级)/养成(1200)/外显小件(200),SKU分层照尼罗。
- **模块6累充**(跟夏日):10档$10~$2000;券按档位差值×2配($0.50/张,合计4000张照夏日H列);世界杯航迹→$50-100档/头像框→$200档(外显进累充,美术+2件:航迹重3D/头像框轻2D);累充隔离三表协同(reference_x3_recharge_isolation)。
- **A线vs竞猜对比账**(数值页新表):竞猜猜对$0.167/券(全场最优)>A线全通摊销=竞猜EV $0.20/券(持平!)>猜错=B线$0.25——竞猜=A线的博弈版(上行最优/下行=B线/无资源附加),A线综合ROI最高(主投放线),B线=追加纯券(=直购券)。三线自洽。
- 全案现6模块:开箱/竞猜/BP/签到/兑换商店/累充 + 皮肤。

## v0.16-v0.17 竞猜激励定稿(2026-06-10)
- **v0.16 猜对bonus 50%→75%**(+15/+60/+150,用户定标猜对单券≈$0.15→实际$0.143);EV(50%)=$0.18/券**正式优于A线全通$0.20**→竞猜=获券最优解坐实(A线靠宝石+VIP+确定性保综合ROI第一)。
- **v0.17 焦点战模板+爆冷加成**:押弱势方且爆冷胜→常规bonus外额外+必得50%($19.99:+40/$49.99:+100,爆冷单券$0.111,🔧待评审);强弱由运营逐场标定+**我司最终解释权**写入规则与界面声明;本地化3模板key(Focal_Tag/Upset_Tip/Disclaimer);设计目的=防全员押强队保悬念(合规版赔率思想,文案禁出现赔率字样)。
- **券效率全谱系**: 爆冷$0.111 > 猜对$0.143 > EV$0.18 > A线$0.20 > B线/猜错$0.25 > 累充附赠$0.50——激励梯度指向参与竞猜+敢押弱队。

## ★v0.19 机制纠错(2026-06-10):皮肤=排行榜独占,非保底
- **足球宝贝皮肤+限定英雄=开箱次数排行榜独占**(Top20草案,分层🔧待定如Top1-3加发英雄)——这才是尼罗/夏日的真实模式(白皮书:英雄皮肤=排行榜独占只有冲榜可得;26年榜扩Top20后大R付费率8%→24-47%=关键杠杆)。
- **我此前把夏日$250误读为保底坑深——实际$250=排行榜上榜门槛**。开箱无保底,奖池=资源/养成/纪念币(皮肤不进池);累计阶梯5/20/40/70/100=纯资源。
- 加「距离上榜还有{0}次」提示(TXT_WC_Chest_RankGap,夏日2.3节临门一脚转化实证)。
- **核心循环图v2**=HTML+Chrome headless截图(core_loop.html→核心循环图_v2.png,1760×920,KB/产出-数值设计/X3_世界杯/);PIL版弃用。HTML出图法:chrome --headless --screenshot --window-size,比PIL好看,emoji正常,改字编辑HTML重截。

## v0.22 价格档定稿(2026-06-10)
- 竞猜三档回调:**$4.99(普通场全程)/$9.99(16强起焦点战)/$19.99(8强起焦点战)**,砍$49.99竞猜档(传统A/B线$49.99礼包档保留)。必得=尼罗同价档20/40/80,bonus75%=+15/+30/+60,爆冷+50%=+20/+40(单券$0.111/猜对$0.143/EV$0.18比例制不变)。
- ★构建脚本永久移除WRAP——**用户偏好:全表溢出不换行**(之前每次rebuild把他手动改的溢出冲回换行)。
- v0.21全量重验闭环:checker抓6block(旧版尾巴:设计稿超级大奖/BP皮肤碎片线/主胜平客胜/32场x3/一场一档/bonus50%)+复核又抓2漏网→教训「修复残留必须grep全表同概念,不能只改报告坐标」已进checklist进化日志。排行榜Top20定稿(不分层,皮肤+限定英雄)。

## v0.23 足球宝贝全部走视频(2026-06-11,制作人拍板)
- 对齐「英雄皮肤视频化方案」(GSheet 15Iacryl-uRDzaFUsErqvTvppnqMG0MuA3U1yKLKHuTU,见 project_x3_hero_skin_video):交付从 FBX+Spine 全套外包 → **2D套件(立绘/卡片/头像)+DKVideo透明循环视频,全程AI五步产链**(主稿FINAL=原画→generate_video首帧驱动→export_sbs_video→VideoRes/+BubbleVideoPlayer)。
- 配置:HeroSkin 新行 DKSpine留空+DKVideo指视频prefab。
- **★跨案依赖**:视频化客户端改造(UIHelper.CreateSpine加视频分支,改1处覆盖5界面+HeroSkin.DKVideo字段)需在足球宝贝上线前先落地;视频化案待确认事项(播放组件/SBS shader/性能预算)同步跟进。

## v0.24 竞猜界面出图规格定稿(2026-06-11)
- 最终效果图=「竞猜界面_最终效果图_FINAL.png」(=FINAL_v2_矩形VS_1):VS区改**规则长方形+两矩形独立留缝**——用户定稿理由:多比例手机适配安全(伸缩裁切不破坏槽位边界);拼缝版(v2_2)弃。
- **槽位尺寸规格表**已进策划案模块2五-2(1080×1920基准,落地以prefab实测回校):B1背景1080×1920×3张/F1横幅1080×200九宫格/T1队伍横幅480×320(2x出图960×640)×32一图翻转/T2队徽256×256×32/F3 VS 200×200/F4柱面板500×900九宫格/F5按钮380×96/F6条1020×96/道具icon128(新出仅抽奖券+纪念币2张);九宫格件无文字。
- 教训沉淀:效果图主题槽必须规则矩形+交美术必配规格表(方法论§9-S6已记)。

## v0.26 竞猜界面客户端框架已拼(2026-06-11,本地commit a92064dd997 @dev_festival 未push)
- **路线定稿：复用进度礼包 ActvType=29 服务端语义，零新后端**——客户端 `ActivityMeta.GetActivityUIType` 按 ContentID∈[2911,2998] 分流到新界面 `UIActvWorldCupGuess`（ActvPack ContentID 段位=ActvType×100，29xx 仅 2901 已用）。一实例=一档两包，与 v0.25 多档=多实例完全契合。
- **队伍信息零新表**：装进 Pack 自身字段——Name=队名TextKey / Head=队伍横幅DK / Icon=队徽DK / Desc=加送文案 / Content=必得奖励。每场每档=1条ActvOnline+1条ActvPack+2条Pack。
- **互斥(买A锁B)=纯客户端表现**：直查 gift purchaseNum，服务端只靠 BuyCount=1 限购；双买科学家由运营结算查订单剔除（写进SOP）。⚠️type29 的 day 锁（服务端建包 day=PackList序号）购买路径不校验、仅 UI 语义，新界面已绕开 → 两包首日均可买。
- **已落仓**：业务类+手写Auto绑定（Gen 的 [Identifier]=任意唯一int即可，UI生成器重生成会覆盖、无碍）+ F固定层8张切图入 `Spirits\ActvWorldCup\`（手写meta: textureType8+九宫格border=短边/3初值）。**prefab 待 Unity 里拼**，图纸=`KB\产出-本地化与美术\X3\世界杯竞猜界面\prefab拼装规格_UIActvWorldCupGuess.md`（含节点树/RewardList结构硬要求/最小联调配置）。
- 4个本地化key待入表：Text_WC_Guess_{Lock_Tip,Picked,Bought,Locked}。
- **素材补遗(2026-06-12,commit 6e89aa80791)**：+通用队名条 WC_Guess_NamePlate(墨绿九宫格,32队共用一条·用户定)、加送柔光条 WC_Guess_BonusGlow(双底差分,**2026-06-12用户弃用**——嫌丑,加送遮罩定版=Unity空Image纯色块EBBE5A/A70,图留仓备用)、券icon/礼盒已早入。队伍区结构定版=三层叠:竖板容器(TeamPanel绿/蓝)→盾徽→队名条嵌底，单贴零件无容器感(踩坑)。
- **界面美术全齐(2026-06-11下午,commit 0bb47c45527)**：F固定层8张(其中TimeBar/Hourglass/SlotFrame/PriceBtn 4张经复用审计弃用——倒计时/格子框/价格按钮全用游戏原生通用件) + T层(WC_Guess_TeamPlate空板九宫格+Badge_Brazil/Argentina真透明) + B背景(WC_Guess_Bg体育场夜景) 均在 `Spirits\ActvWorldCup\`。主题感集中3处:礼包柱/VS/背景（标题板2026-06-11砍——txt_title文字够用,代码未绑底板节点,F1切图作废）。剩余30队徽等界面跑通后批量产。配置阶段待办：WC_Guess_Bg/TeamPanel/队徽/NamePlate注册DK + 淘汰赛·决赛两套背景出图（背景按实例换=ActvOnline.ActvImg填DK，prefab图只是兜底）。铺量32队时再决策：队徽拆「通用盾框1张+旗芯32张」（风格统一+芯便宜量产；用户2026-06-12定=demo阶段不动，要改连结构一起改）。HTML拼装指南=`KB\...\世界杯竞猜界面\prefab拼装指南.html`(带进度勾选)。

## ★v0.25 多档机制纠正(2026-06-11,用户纠错)
- **焦点战多档=同场上【多个独立活动实例】**(每档一个实例,各自单档界面),实例间靠**背景/包装区分档次**(高档=夜场金辉)——**不是单界面堆多档**(我曾画三档堆叠被纠,废稿)。比赛列表同场显示多实例入口(档位角标/背景色区分)。
- 防对冲=实例内锁方向;跨实例方向不强锁,靠bonus EV中性兜底(对冲无利可图)。
- 配置=每实例独立 ActvOnline+Pack 组;B背景层+焦点战高档氛围图(🔧专属1张或复用决赛庆典)。
- 焦点战版效果图=单档$19.99+夜场背景+焦点之战角标+弱方爆冷标签+解释权小字(竞猜界面_焦点战版v2)。

## v0.26-v0.27 焦点战机制终稿(2026-06-11)
- **爆冷→Win Bonus胜利加赠**(v0.26),再纠正为**指定方固定**(v0.27):运营每场焦点战在场次表配「加赠方=左/右」,押指定方且其获胜→常规bonus(75%)外额外加赠+必得50%;**标签固定挂指定方横幅侧**(明示无争议,删最终解释权声明/强弱标定/SOP爆冷判定);运营通常指定冷门方=原爆冷杠杆回归但无强弱话术。本地化只剩 TXT_WC_Focal_Tag/WinBonus 两key。
- 焦点战效果图定稿=竞猜界面_焦点战效果图_FINAL.png(v4_2:夜场+焦点之战角标+左队侧加赠标签+单档$19.99)。拆解示意图已加焦点战增量槽(F7角标/T3加赠标签/B1+夜场背景)。
- **gws token过期处理实战**:后台管道跑 gws auth login 无tty会卡死(0输出);正确=PowerShell Start-Process 新窗口跑(有tty弹浏览器),用户点授权即恢复。

## 活动入口图标落地(2026-06-15)
- 入口图从占位(DK_img_Activity_icon_schedule"赛程"图)换成**正式 DK_WC_ActvIcon**:金色世界杯奖杯+经典黑白足球+绿草基座,透明底自由形状(系统列表自动套圆框)。
- 资产=client `Assets/Res/UI/Spirits/ActvWorldCup/WC_ActvIcon.png`,注册进 Path_Activity.asset(keys段+key/objPath对段同序追加,objPath直写路径不用GUID),与48队徽同套路。
- ActvOnline 102911/102912 col22(0索引col21)→DK_WC_ActvIcon。client(655f35f)+gdconfig(333e1cc)均push dev_festival,导表验证中。
- 出图踩坑全记入 memory `reference_x3_client_resources.md`(入口图真规格124×136透明自由形状+worker不做透明化+玻璃白主体洋红幕色键根治法)。工作件在 `KB\产出-本地化与美术\X3\世界杯竞猜界面\活动图标\`。

## 世界杯头像框设计方向(2026-06-15 立项·试点中)
- **拓展自 v0.16 累充$200档的单件头像框** → 改做**按国家×两档晋级**的头像框系列(参考他项目55张世界杯框=40国,KB`...\世界杯竞猜界面\参考头像框\`,gemini厚涂半写实风,阿根廷8版=风格试错)。
- **★两档晋级机制(用户2026-06-15定)**：①**基础版(小组赛档)**=框体偏素+通用、**国家自身颜色主导**环体、**金色大幅减量只当描边点缀**(否决早期"史诗金华丽"试点);②**晋级版(进半决赛/决赛触发)**=基础版上叠加该国**文化符号**(法国高卢雄鸡/巴西桑巴…),做越走越荣耀的情绪。
- **骨架vs皮(批量生产法,子agent分析参考图得出)**：骨架锁死=圆环+顶部国旗(右上飘)+底部正中足球+能量粒子+左侧9点钟宝石卡扣+环臂交叉收口;每国只换4变量=①环臂主色(队服色优先,荷兰用橙不用蓝)②顶部国旗③足球配色④国家符号(可选)。
- **画风**：向X3原生cel-shaded平涂收敛(加描边/提饱和/精简纹理),双参考法(X3原生框=画风锚`...外显图库...\头像框\`如kvk/Egypt + 本批参考图=构图国旗锚)。
- **首批国家建议**：一梯队8国(阿根廷/巴西/法国/西班牙/德国/英格兰/葡萄牙/荷兰),参考里**缺意大利**(强队大市场)建议补;长尾按运营市场排。
- **试点产出**(全在`KB\...\世界杯竞猜界面\头像框_X3风格试点\`,x3-media uiframe类型/gpt/600输出待降256):法国跑了**三档浓淡**供选骨架——①**强**=`..._WorldCup_France_pilot*`(大金翼+大宝石史诗感,用户嫌强)②**素**=`..._base_v2_alt1`(纯国色环+金菱钻,用户嫌素)③**中**=`..._mid_v2`/`_mid_v2_alt1`(国色环+细金边+顶小蓝宝石冠+侧宝石夹+底足球金托/金翼)=**当前推荐骨架**(不素不强,顶部冠位天然留给晋级版文化符号)。
- **★骨架定稿(2026-06-15用户拍板)=`头像框_X3风格试点\Img_Player_AvatarFrame_WC_France_mid_v2_alt1.png`**(中间档:单三色带细金边+顶蓝宝石冠+侧菱钻+底足球小金翼)。法国此图即成品。
- **★48队铺量规则(用户拍板)**:范围=**世界杯48队(不含意大利,意没进2026)**;配色源=`世界杯竞猜界面\48队球衣参考表.md`(FIFA三字码对齐队徽/应援表情);①环体配色=**球队传统色优先**(荷兰橙/澳洲黄绿等标志队色用队色,其余用国旗色)②足球=**跟该国主色变**(跟模板一致)③骨架/金饰/宝石/翼形状/构图**只换色不动**。
- **生产打法**:x3-media uiframe/gpt,法国定稿图当骨架锚reference,prompt锁"reskin只recolor"。输出`头像框_48\Img_Player_AvatarFrame_WC_{三字码}.png`(600待降256),台账`头像框_48\_manifest.json`。**试点4队全过**(NED荷兰橙/BRA巴西黄绿蓝/ARG阿根廷浅蓝白/GER德国黑红金,2026-06-15:骨架零漂移+队色准+深色OK,在`头像框_48\`)。**⚠️但用户后续否决"纯配色"=认不出国家**→改方向**国旗化提识别**(2026-06-15晚):试点2国×2方向(`头像框_国旗化试点\`)。**★评审定稿(子agent+用户)=「足球国旗化」**:环=队色,底部足球贴国旗图案(像国旗裹球)。边框国旗化被否(环是弧/无中心→日本红圆这类中心图案旗无处安放、复杂旗糊、金属环高光冲淡旗色)。范式锚=`头像框_国旗化试点\WC_frame_JPN_ballflag.png`(白底红圆球一眼识别)。
- **★国旗球最终模板规则(2026-06-15定)**:①环=**队色单主色带**(不堆三色,否则与国旗球撞色冗余,法国是反例)②底部足球=**国旗球**(中心图案旗/条纹旗都贴球面,cel-shaded高光叠旗上保球感不拍平2D)③骨架金饰(顶冠+侧菱钻+底金翼)不变。
- **48队国旗球批量注意**(评审给):中心徽章旗(日/韩/墨/巴/葡/沙)最省心摆球正面;复杂米字/格子旗(英/澳/新/克罗地亚)球小直印会糊→简化主元素+实显尺寸验可读;队色=旗色条纹旗(法/德)环收单色让球跳出。
- **验证中(2026-06-15)**:按国旗球规则重铺4队压测全难点(`头像框_国旗球_试点\`):JPN中心圆标杆/FRA撞色修正/CRO最难格子旗/BRA球徽旗。过审→剩44队按`48队球衣参考表`分批滚动铺(套队徽滚动派media-worker法,sonnet5)。**纯配色版`头像框_48\`4队作废**(被国旗球取代)。
- **★环体终修(2026-06-15用户定)**:纯单色环"占比太大太闷"被否→环=队色但加**明暗渐变+金属光泽+雕纹**(金属珐琅感,非平涂纯色),球不动。4队验证过(`头像框_国旗球_环纹理试点\`:JPN/FRA/CRO/BRA)用户认可=**48队最终模板**。范式锚=`头像框_国旗球_环纹理试点\Img_Player_AvatarFrame_WC_JPN.png`+骨架锚=法国mid_v2_alt1。
- **全量开铺(2026-06-15)**:剩44队(48减已做JPN/FRA/CRO/BRA)按`48队球衣参考表`环色+各队国旗球,输出`头像框_48_FINAL\Img_Player_AvatarFrame_WC_{三字码}.png`,台账`_manifest.json`,分批滚动派media-worker(sonnet5),目录实查对账。复杂旗(英/澳/新米字·克格子已验)简化主元素验小尺寸可读。
- **✅48队全齐(2026-06-15)**:三批滚动派完成,`头像框_48_FINAL\`48张+总览`_总览48.html`(生成器`_gen_frame48_overview.py`,含三字码→中文名)。**⑥新踩坑(worker路径bug)**:个别worker(QAT)把文件存到**错误路径`C:\Users\linkang\ADHD_agent\...`(多Users\linkang\前缀,正确=C:\ADHD_agent\...)**,task报success但正确目录无文件→排查"假成功"时**全盘find該队png**,可能在错路径,挪回即可不用重生成。
- **✅落地完成(2026-06-16,三步全推送)**：
  - **A.DK注册**(client `47a226c36b6`):48图降256(原2048)拷`client\Assets\Res\UI\Spirits\Personalise\AvatarFrame\`+48 meta(抄kvk模板换guid/spriteID)+注册`Path_Personalise.asset`(keys/values两段同序追加,平行一致)。脚本`_register_dk_48.py`。⚠️只add自己97文件(Path_asset+48png+48meta),避开别人WIP(Button4/ClickToClose prefab/gdconfig submodule)。
  - **配置**(gdconfig `458da5e`):`Personalize__PersonalizeAvatarFrameCfg.tsv`新增48行**ID 10028-10075**,字段=DK_Img_Player_AvatarFrame_WC_{码}/属性220000攻击万分比50(0.5%)/Power20000/来源"竞猜礼包获取"/Name世界杯队名(桑巴军团/高卢雄鸡/三狮之环…)。脚本`_gen_avatarframe_cfg.py`。
  - **C.i18n**(同commit):`tsv/i18n/Text__Text.tsv`追加48个`TXT_PersonalizeAvatarFrameCfg_Name_{ID}`×**15语言**(列序col4=cn,col5-18=en/sp/fr/id/de/kr/zh/ru/ua/jp/it/pl/po/tr/th,状态col1=AI)。脚本`_gen_i18n_48.py`(内置完整翻译表)。**直接改tsv不跑CompositeI18n**(新行不在xlsx,扫不到;pre-commit hook自动tsv→xlsx同步)。
  - **⚠️名字改版(2026-06-16,gdconfig `e8bb064`)**:基础版(小组赛档)名字从包装名(桑巴军团/高卢雄鸡)**改为朴素「世界杯·{国家}」**(如世界杯·德国/World Cup Germany);中文+繁中用中点·,其他语言空格分隔。配置Name+Text i18n 48×15语同步。**包装名留给后续淘汰赛档(第二档晋级版)头像框**用包装+文化符号。脚本`_rename_to_worldcup_country.py`(内置48国名×15语+世界杯15语,可复用)。
  - **client commit msg强制`X3NEW-`/`X3-`前缀**(无前缀被hook拒)。
- **⚠️导表受阻(2026-06-16,非本案问题)**:jolt #921 FAILURE,但blocker=**别人的`ActvOnline DKVideo→DK_Video`列改名(commit 8842d7d 世界杯开箱视频案)**撞tsv-schema-gate"列序不能变"。我的两表`PersonalizeAvatarFrameCfg`+`Text`均`blocked=False reason=unchanged`全过,**数据没问题**。头像框要等ActvOnline列序gate被解决才能跟着导出生效。
- **剩余**:导表解阻后生效 → 头像框可挂进竞猜礼包奖励/活动发放(新commit)。
- **⚠️3张漏透明化修复(2026-06-16,client 1733bf8)**:TUR/QAT/CPV 三个worker漏做透明化→吐**整张灰底(213-252)不透明RGB图**(其余45张正常RGBA)。全盘扫alpha揪出(`alpha范围(255,255)`或四角!=0)。修法=洪水填充抠灰底(mask=三通道≥195且极差≤22的中性浅灰),**关键:种子要四边+图像中心点双向灌**——头像框是闭环,中心镂空区的灰底被框环隔断、与外部背景不连通,只灌四边中心仍255不透明,补中心种子才抠掉。框主体彩色/金/深色不在灰mask内不会被吃穿。脚本`KB\...\世界杯竞猜界面\_fix_alpha_3.py`,原图备份`头像框_48_FINAL\_opaque_raw_备份\`。改完FINAL 2048版+client 256版都更新。(套队徽/应援表情的滚动派media-worker法,sonnet5 model)。
- **晋级版(第二档)**:进半决赛/决赛触发,基础版顶部冠位换该国文化符号(法高卢雄鸡/巴桑巴…),待基础版48齐+球队晋级再做。
- **✅晋级档模板定稿(2026-06-16,法国样板)**:在`头像框_晋级档模板\`出两档各2变体——**四强档**`WC_frame_FRA_semifinal_v1/v2`(基础版骨架+金桂冠环抱+星章/4星点缀+金量加码,隆重但克制)+**决赛冠军档**`WC_frame_FRA_final_v1/v2`(最华丽:顶部风格化金奖杯[原创非FIFA商标]+金桂冠+金光放射)。三档浓淡递进=小组赛(基础质感)→四强(桂冠+星)→决赛(奖杯+光芒)。**只定模板,等真实四强/决赛队伍出来(赛程到淘汰赛)再套确定国家批量出**(像基础版那样按队铺,骨架锚=各队基础版/或法国晋级档,只换队色+国旗球)。脚本逻辑见会话,锚图ASCII副本`C:\ADHD_agent\.cache_wc_anchor\FRA_base.png`。
- **落地**:48框→降256→DK注册+AvatarFrame配置表(待美术齐)。
- **🔍应援表情"DK not found"诊断(2026-06-16,根因=client包未重构非配置)**:48队应援表情(Emoticons表ID300-347,Res=`DK_WC_{码}`,gif走`Assets/Res/UI/Gif/WC_{码}.bytes`)游戏报not found。**全链路查证仓库层全齐**:配置/DK注册(Path_Emoticons.asset远端也在)/48个.bytes+.meta/i18n 都对。**关键诊断法=找同表能正常显示的对照**(DK_Bella01与DK_WC_KSA同在Path_Emoticons、注册格式同;Bella能显=DK系统正常),唯一差别=Bella01.bytes是4月老文件已打进现役client包,WC_*.bytes是6/15 22:15新提交→**dev服跑的client资源包是6/15前构建的,没含新.bytes**→DK配置查得到但运行时`ResourceMgr.LoadTextBytesAsync`从包里加载.bytes失败报not found。修=**重新构建client资源包/AssetBundle并更新dev服**(非改配置)。报错抛点`DisplayKeyExtension.cs:259`。
  - **⚠️踩坑(我犯的)**:`git show <commit>:<path>`查x3-project时路径前缀必须带`client/`(如`client/Assets/...`),漏了会grep=0误判成"DK被覆盖删除"假警报。x3-project仓根在client上层,client/是子目录。

## 真券落地 + 奖励格漂移修复(2026-06-15)
- **真券 item 1146 世界杯冠军抽奖券**:克隆1134建,图标 DK_WC_TicketIcon(券图WC_Guess_TicketIcon.png早先已做+在Path_Item注册,只是没提交/item没建),Reward 24457(付费20)/24460(免费1)换1134→1146,Name/Desc文本(zh+en兜底)。client 33ff721/gdconfig 4c22b8c。
- **奖励道具格漂移**:两列 RewardList(ScrollRect) anchoredPosition.x=405,而列锚点居中→把道具推到列心右405px(左列偏右/右列漂出面板)。修=x 405→0。prefab 34069ab(走客户端构建)。
- 入口图 DK_WC_ActvIcon 导表 SUCCESS #850。

## v0.32 竞猜「皮肤场」实例 102913 + 开箱Spine背景机制查证(2026-06-15)
- **新增竞猜皮肤场 102913**(用户要:走B克隆竞猜实例+背景播V8透明视频+皮肤奖励爱莉希雅+券1146;视频背景客户端做,配置侧我建):克隆 102911,押巴西/阿根廷两包 **Pack 891105/891106**($4.99)→奖励组 **291103=皮肤道具 5304001×1 + 券1146×20**;ActvPack 2913(FinalReward 291102)/TC 2913/i18n 6 key(克隆译文)。gdconfig dev_festival 72a92c2,**导表 SUCCESS #861**。背景列 ActvImg 留空给客户端。建表脚本临时 /tmp/build_wc_skin_instance.py(克隆模板行→改列→断言空→LF追加,无 append 子命令时的范式)。
- **★皮肤已就位**:HeroSkin **104001 足球宝贝·爱莉希雅**已建(DK_Spine空/DK_Video=DK_video_zuqiubaobei_sbs/ObtainItemID=5304001);**发英雄皮肤=Reward 行 ItemType=1+ItemID=ObtainItemID(5304001)+num=1**(同战斧女王5302201等所有皮肤)。item 5304001 文本 TXT_Item_Name/Desc_5304001 已有。
- **★V8 透明视频版本厘清**:用户说"V8才对"=**入场片单条直出 v8**(15s,入场→颠球→idle),透明 SBS=`视频\入场\入场v8_SBS_q19_1.mp4`(12513754字节,2160×1920),**与客户端 `VideoRes\HeroSkin\zuqiubaobei_sbs.mp4` 字节完全一致=早已落客户端**。KB 里 `足球宝贝_v8_无缝循环.mp4`(4.29s)是不透明普通循环、`足球宝贝_v7_SBS透明`系列(5s)是旧 v7——都不是要用的那个。
- **★开箱(ActvType15)Spine 背景怎么配进去的**(用户问):=`ActvOnline.ActvPrefab`列(col23/0-idx[23],proto 注释「DK_主题spine」)填 Spine DK→界面 Root/Role 的 EffectDisplay.DisplayKey→Path_Spine.asset→Res/Spine/Role_Spine_XX/。天马福箱 101513 [23]=DK_Role_Spine_39_Skin01(卡蜜拉);底图 ActvImg[22] 在后、Role Spine 在前两层叠。EffectDisplay 同时有 VideoDisplayKey 分支(与Spine互斥),视频化皮肤走它。竞猜界面无 Role 节点→客户端要加才能放视频背景。透明视频 UI 链(现成)+皮肤视频化改造已合 dev_festival,全沉淀进 [[reference_x3_client_new_ui_workflow]] §可复用组件 + 交接文档 §4.9。

## v0.33 ★主抽奖=开箱(ActvType15)首个实例真落地(2026-06-15,导表SUCCESS)
- **纠正**:v0.32 我把用户"世界杯竞猜开箱"误读成竞猜建了 102913;用户澄清**要的是开箱模块(ActvType15)**。102913 竞猜实例**保留不清**(用户定)。
- **开箱实例 101516**(克隆天马福箱1513):`ActvOnline 101516`(ContentID1516/type15/复用TC1513/ActvImg=DK_WC_Crafting_Bg/ActvPrefab清空/显示列[33]=1146|5304001) + `ActvCrafting 1516`(消耗**券1146×1**=测试值[设计10券/次]/产物5304001/奖池115/阶梯复用1012/box DK 关开底) + 奖池`ActvCraftingReward 组115`(8行,克隆元旦池112,**首行超级大奖=皮肤5304001 权重50**,余7资源照搬) + i18n 2key。gdconfig **056e7e9 导表SUCCESS**。建表脚本 `C:\Users\linkang\build_wc_crafting.py`。
- **★开/关箱动画机制**(用户问):非逐帧——box_1关/box_2开两图常驻 FlyItem 节点,开箱时 prefab DOTween 序列 AnimaOpen 做 box_1淡出+box_2淡入+放大;配套金光粒子=EffectDisplay 读 `DK_Fx_baoxiang_open_{绿蓝紫橙}`(按奖励品质选色,+_short跳过版),**全游戏硬编码通用、与节日无关、不读配置**→**世界杯开箱零代码,只换 box_1/box_2 两张图**。
- **开箱美术**(client `Spirits\ActvWorldCup\`,已注册3 DK):WC_Crafting_Bg(540×960,竞猜体育场缩) + BoxClose(720,WorldCup_box1_pick2_trans切) + **BoxOpen(720,AI生开盖版**=照元旦box_2开盖构图,洋红幕→色键扣,源`世界杯礼盒\WorldCup_box_open_magenta_v1.png`)。底遮罩仍元旦占位。
- **本地验收**:`!gm @<uid> GMAddServerActivityByCfgId 101516 0`(TC1513绝对日期窗口能算,与竞猜TC2913部署起算算不出窗口不同);开箱在活动中心列表正常显示(type15已注册分类)。
- **协作踩坑**:①开箱配置一度被别人 `reset --hard` 冲掉(未提交)→重做;②stash 护别人Pack/Reward WIP 时 data/Reward.xlsx 被WPS锁 Permission denied→stash半失败→关WPS+reset取消暂存救回;③多页签 ActvCrafting.xlsx 同步必须3子页签全传否则gate divergent。均沉淀进 [[x3-tsv-export-migration]] + 交接文档§3.5/§4.11-13。

## 竞猜礼包正式数值对齐(2026-06-15)
- **付费礼包=5个道具ICON**(用户定):券+钻石+VIP点数+[第5物]+金币。档位数量套尼罗/夏日A线:$4.99=券20/钻2500/VIP点数25(item2022)/金币10万;$9.99=券40/钻5000/VIP50/金币20万;$19.99=券80/钻10000/VIP100/金币40万。bonus+15/+30/+60,焦点额外+20/+40。**券经济按纯券算**(资源是附加填充不动EV)。
- **免费礼包=5个ICON(全便宜填充约等于免费)**:券1+钻石1+金币500+30分钟加速(11003)×1+基础资源袋(3101)×1。
- ⚠️**商会赠礼是假道具,发不了**:用户本想第5物放"商会赠礼",查明=公会赠礼购买特权(UnionGift系统按价格档自动挂,假道具12101-12105不可投放Reward)→详见 [[reference_x3_reward_table_rules]] 坑C。**第5物现用神秘宝箱(1130)占位,正式用啥待用户定**。
- 测试配置 291101(付费$4.99,5物)/291102(免费,5物)已落 gdconfig(ddacb0f);$9.99/$19.99档策划案已写,测试服暂只配$4.99场。build_design.py 两档构成已补全。

## v0.34 累充/BP/签到换皮 + 世界杯单独入口落地(2026-06-16)
- **三模块换皮全落地(gdconfig c441937,client c12ddd80f62,均dev_festival)**：累充**100597**(克隆尼罗100594,10档道具1128→世界杯券1146,ActvTask+Reward 59801-810;**白名单col50@2026-06-18定稿=156包**:核心12[特惠5档211002/004/006/008/010+抽奖券4档211012~015+BP130020/021+通用1002001]+竞猜全部付费包144[894XX1/2/3×48国,免费档不计];原占位测试包891101/02/05/06已替掉;commit a758dd6;★白名单是col50不是col51+apply_xlsx_patch列名填RechargePointPackWhitelist不是Pack,见[[reference_x3_recharge_isolation]]) / 签到**101403**(克隆101402,day1-6发券x1·末日x3,Reward59811/59812,ActvLogin448-454) / BP**102240**(克隆元旦BP2233,BattlePassScoreReward组140)。**★BP积分设计定稿(2026-06-16用户改):门槛不变(积分需求=元旦原值3000),竞猜只作额外加分途径——不抬门槛逼竞猜,活跃照旧能打+竞猜锦上添花。曾误做积分需求×2=6000(=砍活跃50%),用户否决已改回3000(commit 3a3b387)。竞猜加分走GM随结算发,不入配置。**
- **★BP奖励换WC专属块(2026-06-16,commit d2014ce)**:糖牌1124→世界杯券1146(保数量)/烟花表情15416→券×5/其他不变。⚠️**关键坑=组140奖励组与元旦BP组132共享同批RewardID(4028xxx),直接改会连元旦一起改**→必须克隆新块:60组(20级×3轨)→4099xxx(+71000),改糖牌/烟花、其余照抄,组140指针(BattlePassScoreReward idx4/5/6)重指;元旦组132不动。脚本build_wc_bp_rewards.py。等级奖励表 `KB\产出-数值设计\X3_世界杯\世界杯BP_等级积分奖励.html`(gen_bp_html.py)。
- **★世界杯单独入口=`ActvOnline__ActvGroup`新建组139**(用户要"不走普通活动入口/不放酒馆")：图标DK_WC_ActvIcon/排序98/chrome复用组101通用cm。三活动 col38=139 即从普通列表移进世界杯入口。节日入口纯靠 col38 归类,ActvGroupSchedule只给航海/入侵/KVK用。
- 客户端6 DK(DK_WC_{Fund,Pass,Checkin}_{Bg,Icon}):背景竖960/方500/横568+HUD124×136落仓Path_Activity注册,需客户端构建。i18n 7key cn+en兜底(全语种待x3-translation-automatic)。
- ✅**导表 #942 SUCCESS(2026-06-16,commit af36d74)**:两blocker均清→①**DKVideo(真因纠正:非proto!)**——导表`FieldDef.py:60`按**注释行row5有无"DK_"**定isRes;col51(DK_Video)row5注释历史漏写DK_→isRes=False,而值`DK_video_zuqiubaobei_sbs`以DK_开头→`RowObjTransform.py:66-68`报错(文案"not startswith DK_"误导,真意=值是DK_资源但列没声明为资源)。修=ActvOnline col51 row5注释补"DK_视频"(照col48 MainEffect="DK_界面特效"),另一边补的。我先前误判"等客户端补proto"已纠正。②**TC TriggerType**——我建累充/签到/BP TC套了竞猜式5(导表要求TriggerType=5活动必须是触发式玩家活动item.TriggerType≠0),非触发式活动改回1绝对(WC档期6/11~7/18)。三活动+入口139全部导表生效。
- ★工具坑(进x3-config-export SKILL.md):ActvBattlePassScore.xlsx=16384列病态宽表+Table1 ref写坏成`6:42`→openpyxl写崩,修=zip改ref`A6:G42`。全程+脚本见换皮档案 `KB\换皮档案\X3\20260616_世界杯累充BP签到.md`。

## v0.39 用户试玩反馈修复(2026-06-17)
用户跑下来报4问题,逐一处理：
- **①连锁礼包名"还叫尼罗"**：根因=clone i18n 时 swap 只改了 cn/en,**其余14语言(含繁中"尼羅之輝禮包")各有自己的尼罗译法没换**→残留。修=5个付费包名(TXT_Pack_Name_211002/4/6/8/10)14语言全重译为"世界杯礼包N"。⚠️换皮 clone i18n 通用坑,见 [[reference_x3_i18n_workflow]]。
- **②锚点礼包不显示**：根因=锚点(PackType15道具获取)靠 **ItemObtain 表**挂"获取途径"触发,WC只clone了Pack行、漏了ItemObtain注册+券ObtainID。修=新建 **ItemObtain 100357**(clone尼罗100310,ObtainType7,Value=211012-015,名世界杯券) + **券1146 ObtainID=100357**。机制详见 [[reference_x3_pack_open_mechanisms]]。
- **③开箱加0.001%直接抽皮肤**(用户新需求)：奖池115加皮肤行 **11509**(5304001×1,SReward1全服喊话),原8项权重×10(相对概率不变,总10000→100000),皮肤权重1→**1/100001=0.001%**。奖池权重非强制10000(组100=9970),相对权重制可缩放表达更细概率。
- **④顺修损坏的 data/ItemObtain.xlsx**：HEAD里就坏(invalid XML,openpyxl normal/sync挂、只read_only能读),卡所有人改ItemObtain。从4页签tsv重建干净xlsx。见 [[x3-tsv-export-migration]]。
- commit 392e010(①②④)/739b468(③)。
- **未决(非配置)**：最后一档"剩余领取次数不对"=Pack行+ChainPack与尼罗字节级一致、无配置差异(疑客户端进度/缓存或尼罗本身);兑换ICON白底=双底差分真透明(疑客户端缓存,reimport即可)。

## v0.38 纪念卡+开箱礼包落地，兑换商店待配(2026-06-17,接前一agent崩溃残局)
- **背景**：前一 agent 配纪念卡时崩溃，用户让我接管 + 继续配兑换商店/开箱礼包(KB有知识)。
- **★模块7 世界杯纪念卡 = 完成(jolt SUCCESS)**：前 agent 其实配完了核心、只是 gdconfig 没 commit(client已提交)。我验证+补提交。MemorialCard **79 绿茵之星**(clone尼罗回响76,PropertyGroup1011复用) + Item **180079**(Type9纪念卡/UseEffect15→卡79) + i18n 7key + 卡图 client(icon_card_image_79/img_card_image_79+DK)。recipe在 `KB\产出-数值设计\X3_世界杯\_系列卡_配置落地清单.md`。commit fa613d6。**获取途径=兑换商店(下条)**。
- **★模块1 开箱礼包 = 完成(jolt中)**：**clone 尼罗连锁ChainPack482(Pack210601-611)+锚点(210612-615) → WC 211001-211015(+400偏移)，券1128→1146**。①连锁A线11包(6免费穿插+5付费,付费=券+钻+VIP点数,$4.99~) ②锚点B线4档纯券(PackType15,券20/80/200/400@$4.99/19.99/49.99/99.99=$0.25/张,TC6001"礼包-永久"通用复用) ③新 **ChainPack676**(PackList 211001-211011) 挂 ActvOnline101516.ChainPackID(col31 481→676)。脚本 `C:\Users\linkang\build_wc_crafting_packs.py`。commit d169412。
- **★X3 Pack奖励内容机制(接管keypoint,查/clone礼包必懂)**：Pack 行 **col13 Content = Reward 表 col1=同值的掉落包ID**(如 Pack210602→Reward包210602=券×20+钻+VIP)。col11 ContentID 另有用途。clone 礼包必须**同时 clone Reward 表对应掉落包**(换券道具)，否则礼包空。详见 [[reference_x3_config]]。
- **★模块5 兑换商店「荣耀兑换所」= 完成(本地导表过,push+jolt)**：clone 情人节 ActvExchange1337(15SKU)→**WC ContentID 1339**(ActvOnline **101339**/TC1339绝对6/11~7/18/挂入口组139/图DK_WC_Exchange_Bg+Icon[前agent美术]),币 1135玫瑰花瓣→**荣耀金币1147**,纪念卡SKU 180077→**180079绿茵之星**,其余13养成/外显SKU照搬(用户定用情人节不用尼罗)。i18n ActvName荣耀兑换所/Desc。脚本=前agent写的`C:\Users\linkang\build_wc_exchange.py`(我补:纪念卡换180079+修多行单元格坑)。commit 4b38051。**⚠️坑见下**。
- **⚠️ActvExchange多行单元格坑(2026-06-17,卡很久)**：情人节首个SKU(万能传奇信物)Label=`"50%\n每日刷新"`是引号多行单元格,前agent脚本split/join克隆把它截断→tsv坏→xlsx永远mismatch同步不掉。修=raw补回续行+改用csv.reader验。**教训已进[[x3-tsv-export-migration]]:改含多行单元格的表禁split/join,用csv**。
- **★世界杯活动全模块至此配齐**(开箱主体+累抽+排行+礼包[连锁/锚点]+兑换商店+纪念卡+竞猜+BP+累充+签到+入口139)。四次导表全SUCCESS(纪念卡/礼包#994/兑换商店#995/翻译#996)。
- **全语种翻译(2026-06-17,commit ec072a5,#996 SUCCESS)**：本批**13个WC key**(荣耀金币1147 name/desc、纪念卡79绿茵之星 name/desc/获取提示×3、兑换商店101339 name/desc、开箱101516 name/desc)cn+en兜底→**16语言真译**(脚本 build_wc_i18n_translate.py)。⚠️**x3-translation-automatic skill 假设过时**(E:盘/10语言/xlsx),少量已知key直接翻tsv col5-18更稳,详见 [[reference_x3_i18n_workflow]]。**注:竞猜/BP/累充/签到等其他WC模块的i18n是否全16语言未核**,后续全表翻译可跑skill扫描补。
- 剩余=数值评审(开箱消耗10券/Value/SKU定价)/美术替换占位(底遮罩)/客户端(皮肤视频化/竞猜入场动画/96队徽DK/应援表情静态vs动图)/结算SOP文档。
- **协作**：前 agent 还顺手改了 data/Item.xlsx 等(冗余,tsv是真源)；提交纪念卡时遇 HEAD xlsx 比 tsv 旧1257格的历史漂移→`sync_xlsx_tsv --from-tsv` 重生成对齐(多页签MemorialCard喂全2子页签)。

## v0.37 开箱排行榜+资源栏/HUD图标收口(2026-06-16)
- **★换皮开箱必查的"克隆继承坑"(接管keypoint)**：开箱101516克隆元旦1513,把元旦这几列也带过来,逐个要改：①**ActvCrafting产物Product**(v0.36已修:皮肤→1147荣耀金币) ②**ActvOnline col21 ActvIcon(HUD图标)**=元旦`DK_img_Activity_NewYear_icon_2`→`DK_WC_Crafting_Icon` ③**col33 TopResource(右上角资源栏)**=元旦`1124|1125`(糖牌马蹄)→`1146|1147`(券+荣耀金币) ④**col20 RankID**=元旦本服167→克隆情人节跨服。BP102240同样从元旦BP继承col33=`1124|1125`已修`1146|1147`(用户截图发现的马蹄bug)。
- **排行榜=克隆情人节1514跨服排行(用户:参考情人节,皮肤换WC)**：`RankCfg 1004`(克隆172"跨服世界排名"Top100) + `RankRewardSlotCfg 100401-08`(克隆17201-08,RankType=1004,8档1/2/3/4-5/6-10/11-20/21-50/51-100) + 奖励包`Reward col1=30581-88`(克隆30511-18,**皮肤5301702→5304001足球宝贝**,加速照抄)。**Top20(30581-86)发皮肤+加速,21-100(30587-88)纯加速**。`ActvOnline 101516`:col20 RankID 167→1004 + **col18 CrossServerRank→1(跨服)**。皮肤=排行独占(已移出奖池)。脚本`build_wc_crafting_rank.py`。
- **活动入口组**:101516 col38 131→139(世界杯单独入口,对齐累充/签到/BP)。
- **★图标DK双命名空间坑(接管keypoint)**：**HUD图标(ActvIcon col21)读`Path_Activity.asset`;道具图标(item col20)读`Path_Item.asset`——两套独立namespace**。"累充HUD用券图"不能直接把col21填道具DK(跨namespace不显示),解=把累充现用`DK_WC_Fund_Icon`(Path_Activity)的**objPath重指**到券图`WC_Guess_TicketIcon.png`(client改,col21不动)。
- **金币图标定稿=v2**(用户发图定,金奖牌+奖杯+足球+月桂):client`WC_GloryCoin.png`(从KB`荣耀金币/WC_GloryCoin_v2.png`)+meta+`DK_WC_GloryCoin`(Path_Item双段),item1147 col20占位券图→`DK_WC_GloryCoin`。
- **开箱HUD=世界杯箱子**(用户:KB箱子切HUD):client`WC_Crafting_Icon.png`(KB`WorldCup_box1_pick2_trans.png`缩124×136居中透明)+meta+`DK_WC_Crafting_Icon`(Path_Activity双段),101516 col21指过去。
- **★DK注册脚本法(无Unity,静态图,可复用)`build_wc_icons_client.py`**:Path_*.asset=**keys段(`    - DK_x`)+values对段(`    - key: DK_x`/`      objPath:路径`)双段平行,两段都加**;meta=clone同类现有图meta换guid(顶部)+spriteID(uuid4().hex);objPath直写png路径不用GUID。沿用avatarframe`_register_dk_48`法。
- **commit**:gdconfig 数值dbd93ea/排行cfe8253/group8da46ab/BP91cf3fc/图标指向3b55a12;client 累充HUD ca711ca85d5/图标37cd2549634。jolt 数值#968+排行#969 SUCCESS,图标指向jolt中。**生效=jolt SUCCESS→robot回写client→本地pull client+重启(见[[workflow-x3-local-server-gm-telnet]])**。

## v0.38 跨服排行榜前五铭牌「世界之巅」(2026-06-18,新增外显)
- **背景**:此前世界杯**无铭牌(PlayerTitle)资产**——开箱跨服排行(RankCfg1004,见v0.37)前名次想加专属头衔板,本次新出。⚠️X3「铭牌」=PlayerTitle头衔(无独立铭牌系统,见[[reference_x3_cosmetic_resource_paths]]),title板尺寸**752×192**。
- **设计定稿(用户拍板)**:**统一一款**(非金银铜三款)+主题**世界之巅**(文案=世界之巅/Peak of the World,沿用决赛框/表情同名)+发放范围=**跨服排行榜前5名**(改自最初前3),对应`RankRewardSlotCfg`前4档100401(r1)/100402(r2)/100403(r3)/100404(r4-5)。
- **★PlayerTitle发放机制(本次追代码确认·接管keypoint)**:头衔**不直接发,要包成可用Item**——服务端`StorageMeta.Item.cs:362` `case ItemUseEffect.EffectTypeTitle: UnlockTitle(UseParameter[0]=头衔cfgId,UseParameter[1]=过期s(-1永久),num)`(同头像框80xxx包一层套路)。排行榜奖励发的是**这个title-Item**(进Reward奖励包),不是activity挂PlayerTitleID。现有3头衔(101风暴领主/102海皇/103魔海之主,Quality=3橙)走ActvKvk.PlayerTitleID直发,**title-Item用法本案首例**。PlayerTitle表字段:ID/Name(TXT_)/DK_Icon(752板)/PositionBuff(int[]战力词缀)/Reimburse(重复获取钻补偿`单日|最高`,见[[reference_x3_monetization_mechanics]]Regained)/DK_SmallIcon(ItemIcons小图)/Quality(0蓝1紫2橙3)/Order。
- **美术产出**:`KB\产出-本地化与美术\X3\世界杯竞猜界面\铭牌_世界之巅\WC_Title_PeakOfWorld_v{1,2}.png`(752×192成品+`_full.png`高清)。**生成法**=x3-media uiframe类型,gpt图生图,**双锚=①现有铭牌「风暴领主」金翼款(`外显图库_表情头像框铭牌\铭牌\101_风暴领主_kvk_icon_title.png`)定结构/格式 + ②世界杯荣耀金币`世界杯礼盒\荣耀金币\WC_GloryCoin_FINAL.png`定中央奖杯+月桂+足球元素**(合规风格化奖杯,非FIFA标);金+翠绿配色,内板留空给文字。**定稿=v2→`WC_Title_PeakOfWorld_FINAL.png`**(废稿v1)。
- **★落地spec(全追代码核实·冷启动可直接执行,2026-06-18;用户已批"全走完",待执行)**:
  - **小图标**=铭牌缩版(板缩到256宽居中贴256透明,对齐现有nesticon小图标做法,非圆徽)→`铭牌_世界之巅\WC_Title_SmallIcon_FINAL.png`已出。
  - **★title-Item非首例**:现有`Item__Item.tsv` 82001风暴领主/82002海皇/82003魔海之主就是头衔的Item包装(Type9/**UseType1/UseEffect18=头衔**/UseParameter=`titleID|过期秒`,如82001=`101|2592000`30天)。**直接镜像82001→新82004**。Item字段顺序:ID/Name/(shoptitans原名)/Desc/Type/SubType/UseType/UseEffect/UseParameter/...DK_Icon(col21=小图标)/.../DK_Background/Subtitle/.../Order。
  - **PlayerTitle表+行104**:DK_Icon=`DK_WC_title_PeakOfWorld`/PositionBuff**留空(用户定无Buff)**/Reimburse=`100|1000`/DK_SmallIcon=`DK_icon_global_WCtitle`/Quality=3橙/Order=4。
  - **Item表+行82004**:镜像82001,Type9/UseType1/UseEffect18/UseParameter=`104|-1`(永久,UnlockTitle支持-1;现有是限时,本案选永久=赛季荣誉)/DK_Icon=`DK_icon_global_WCtitle`/DK_Background=`DK_Bg_CM_Item4`。
  - **Reward表**:排行榜前5名=奖励包`30581`(r1)/`30582`(r2)/`30583`(r3)/`30584`(r4-5)各+1行发`82004`×1(镜像同包的加速行:col2=包ID/col3=1道具/col4=82004/col6=1/col8=1/col9=10000)。RankRewardSlotCfg 100401-04已映射这4包(见v0.37)。
  - **DK注册**(client仓,无Unity静态图法`build_wc_icons_client.py`):752板→`Spirits/Activity/WC_title_PeakOfWorld.png`注册`DK_WC_title_PeakOfWorld`;小图→`Spirits/ItemIcons/icon_global_WCtitle.png`注册`DK_icon_global_WCtitle`;**两DK都进`Path_Item.asset`**(实测DK_kvk_icon_title板+DK_icon_global_nesticon小图都在此namespace,非Path_Activity)。
  - **i18n auto-key**(CfgProtoTextEx确认,配置表单元格字面值客户端不读):`TXT_PlayerTitle_Name_104`/`TXT_PlayerTitle_ObtainDesc_104`/`TXT_Item_Name_82004`/`TXT_Item_Desc_82004`/`TXT_Item_ObtainTips_82004`/`TXT_Item_Subtitle_82004`→入Text表cn+en+多语种。头衔名=世界之巅/Peak of the World。
  - 执行注意:xlsx-tsv gate(两边改一致再git add)、client在途仓push套路(见line345 v0.30尾)、改完jolt_verify验证。
- **✅已落地(2026-06-18)**:gdconfig commit `3407e8a`@dev_festival(PlayerTitle104+Item82004+Reward 30581-84+Text 6 key) + client commit `1303632312d`(2 PNG+2 meta+Path_MiscIcons/Path_Item DK)。**导表jolt #1071 SUCCESS**(#1066=我Reward ID不连续bug已修;#1070=他人tooling driver修复mid-flight非我)。
- **✅DK流程闭环(2026-06-22)**:切回dev_festival→Unity自动导入两图(GUID解析正常)→**DisplayKey API实测两DK都解析到正确路径**(`DK_WC_title_PeakOfWorld`→ActvWorldCup板png/`DK_icon_global_WCtitle`→ItemIcons小图)。**★用户确认:X3 dev「DK注册即用,不过包」**——Editor/dev走LocalAsset直读AssetDatabase,无需AssetBundle重建;重建仅对打出来的独立/移动客户端。上条"剩客户端资源包重建"作废。至此世界之巅铭牌全链路落地完成。
- **★Reward表加行铁律(本次#1066踩坑·接管keypoint)**:`reward_def.py:116-124` 校验**同一RewardID内所有行的「行ID(col1)」必须连续整数**(sorted后 max==min+n-1),否则导表FAILURE `rewardID:X ID不连续`。奖励包行ID紧挨打包(如30581-88占24692-24721无空隙)→**直接append到文件尾(全局max+1)必破坏目标包连续性**。正解=目标包**整包行ID重排到fresh连续块**(全局max往上,size=原行数+新增),col1是内部行id(外部只引RewardID=col2,renumber安全)。⚠️另:`git checkout origin -- .` 类全量checkout会让openpyxl碰过的xlsx(如ActvOnline)冒3字节diff,非自己改的用`git checkout HEAD -- <file>`恢复,别误提交。

## v0.36 开箱数值改抄情人节(1514)+兑换货币定名(2026-06-16,纠正v0.35)
- **★纠正 v0.35 的两个数值错(用户指出"数值不对")**：①基准从**元旦1513改成情人节1514**(用户定);②**最关键错=主表Product(每次开箱必产物)上轮被我设成皮肤5304001**→等于每开一次送皮肤,大错。情人节开箱模式=**Product=兑换货币(玫瑰花瓣1135)×1/次 + 随机奖池1项**;奖池**超级大奖也是货币大堆**(玫瑰花瓣×500权重50),皮肤**不进池**(走排行榜独占)。
- **落地(commit dbd93ea @ dev_festival,xlsx同步mismatch=0)**：①1516 Product 5304001→**1147** ②奖池组115整组重置=情人节113(权重50/400/500/700/700/1500/2500/3650,超级大奖=**荣耀金币1147×500**,7项资源同情人节;皮肤5304001移出池) ③累抽组1015已是发1147、数量50/100/200/400/800/1600/3000(=情人节1013,不动) ④**兑换货币1147改名「世界杯纪念币」→「荣耀金币」**+新描述(参考尼罗兑换货币**猫眼石币1129**文风:评价物+币,desc尾"可用于活动商店兑换珍贵道具")。脚本 `C:\Users\linkang\build_wc_crafting_fix_valentine.py`。
- **★尼罗对照模板(接管参考)**：尼罗 1128女王恩典卷=抽奖券(消耗) / 1129猫眼石币=兑换货币(产出·DK_icon_global_Egypt02·进ActvExchange兑换)。WC 完全对照:**1146抽奖券=开箱消耗 / 1147荣耀金币=开箱产出+累抽+后续兑换商店货币**。两者是独立道具,别混。
- **⏳进行中**：①1147 专属图标 sub-agent 生成中(参考猫眼石币货币图标风格+世界杯金币主题,出图存`KB\产出-本地化与美术\X3\世界杯礼盒\荣耀金币\`)——**现图标仍占位借用券图DK_WC_TicketIcon,待换**;②本地导表自测验证中→过了 push+jolt。
- **皮肤5304001分发**:已移出开箱奖池,设计=排行榜Top20独占(情人节1514本身无rank,WC排行榜模块单独配,未落地TODO)。

## v0.35 开箱累抽阶梯换皮落地(2026-06-16,本地导表验证)
> ⚠️本节奖池/产物数值已被 v0.36 推翻(改抄情人节);v0.35 的"克隆元旦112/首行皮肤"仅留作沿革,以 v0.36 为准。累抽阶梯部分(组1015/包31601-31607)仍有效。
- **背景**:开箱实例 101516(ActvCrafting 1516)的**累抽阶梯整条线之前还是元旦的**——奖池组115已换好(随机池,首行皮肤),但 OtherRewardGroup 仍=元旦组1012、阶梯各档发的奖励包=元旦31301-31307(发幸运马蹄)。**用户要求:照抄元旦阶梯结构,只把道具换成新建的世界杯兑换道具。**
- **★开箱两条奖励线(接管必懂,我一开始没分清)**:①**奖池 RewardGroup**(主表col4)→`ActvCraftingReward`表(每次开箱随机池,SReward=1标超级大奖) ②**累抽阶梯 OtherRewardGroup**(主表col5)→`ActvCraftingOtherReward`表(各档 NeedTime=累计开箱次数门槛,达标领里程碑)。阶梯发奖路径=`ActivityCraftingCondition.GetReward`返回`OtherReward.RewardID`→`EndowReward`→`EndowHelper.CReward`。⚠️**Reward 表 col0=行唯一ID(仅保证不重复)、col1 才是 RewardID 外键**,查阶梯发什么/改阶梯奖励按 col1 查(我一开始按col0查误判成"悬空引用",其实都在col1)。
- **落地(commit 5aebf37 @ dev_festival)**:①新道具 **1147 世界杯纪念币**(克隆幸运马蹄1125;图标暂占位`DK_WC_TicketIcon`;Value=5按设计$0.01)+i18n TXT_Item_Name/Desc_1147(cn+en) ②新奖励包 **Reward col1=31601-31607**(克隆31301-31307,道具1125→1147,数量50/100/200/400/800/1600/3000照抄元旦) ③新阶梯组 **1015**(克隆1012,NeedTime 50/150/300/500/750/1000/1500照抄) ④`ActvCrafting 1516.OtherRewardGroup` 1012→1015。建表脚本 `C:\Users\linkang\build_wc_crafting_ladder.py`(copy-and-swap范式,可复跑dry-run)。
- **本地导表自测验证通过**(我的31601-31607+道具1147转换无错);本地导表方法+depend坑沉淀进 [[x3-tsv-export-migration]]。
- **⚠️遗留待用户拍**:①纪念币 1147 图标暂用券图占位,要不要出专属 ②Value=5 是否OK。
- **协作踩坑(并发agent同享工作区)**:提交时共享 tsv 捎带了另一agent的签到奖励包59812未提交行→导表先后卡两次(都是它的数据,非我的):①59812行ID不连续(按用户授权机械重编24670-24672解掉,仅改col0不动内容) ②59812 ItemType误填序号1/2/3(加速11003/资源袋3101应都=1,depend报`3101 not existed`)→**交还该agent修**。我的开箱阶梯本地导表已干净,等它修完59812 ItemType,整条dev_festival导表转绿即生效。

## 竞猜礼包投放排期 + 外显线定稿(2026-06-16)
- **真实赛程对齐**(FIFA/Wiki核实):淘汰赛32场,32强6/28(1场)→6/29~7/3(各3场);16强7/4-7(各2);8强7/9-11(1/1/2);半决赛7/14-15;季军7/18;决赛7/19。休息日7/8,7/12-13,7/16-17。
- **甘特图**=`KB\产出-数值设计\X3_世界杯\世界杯_竞猜礼包投放甘特图.html`(脚本`gen_deploy_gantt.py`,改RULE重跑)。含每日各档实例数+主题+**每日付费总坑**(全程总坑$449.46)。
- **三档外显映射**(用户定):$4.99=纯竞猜 / $9.99=头像框 / $19.99=聊天表情。一场比赛=一个竞猜活动实例。
- **$9.99头像框线**:32强不投(腻) → 16强球队款直发(现成48) → 8强**自选头像框宝箱** → **半决赛=四强专属头像框(单国旗裹框,QF阶段预产8支晋级队,库`参考头像框/`56概念图打底)** → 季军/决赛 自选框宝箱。
- **$19.99聊天表情线**:8强球队款直发(现成48) → 半/季/决 **自选表情宝箱**。
- **★自选宝箱机制解决"队伍晋级重复"**:开箱自选,从现成48资源池收集,不重复。
- **新美术=2个宝箱图标(已完成)**:`自选宝箱\WC_AvatarFrameChest.png`(金箱+银色人像头像框徽记+足球)/`WC_EmoteChest.png`(金箱+表情气泡+足球)。**配对款**:同金箱体只换徽记;中性无国旗;游戏宝箱风格(对齐icon_Chest,区别于世界杯开箱礼盒)。+四强国旗框待QF预产。
- 现成外显:48头像框`头像框_48_FINAL\Img_Player_AvatarFrame_WC_{码}.png` + 48聊天表情`应援表情48_脸彩\`。
- ⚠️**AI出宝箱图标踩坑**:worker常把"透明"画成假棋盘格(alpha全255)→洪水扣灰格;或带参考图队色→需"团队中性"硬约束;最稳=洋红幕重出+chroma_key_remove.py扣。

## 自选宝箱底层道具落地(2026-06-16, 导表#945 dev_festival SUCCESS)
- **自选宝箱机制**: 自选礼包道具=ItemType20,col8=Reward组ID(自选池),玩家开箱从池中选1。框/表情道具=ItemType9(col8=cfgID,col20=图标DK)。
- **已建(gdconfig dev_festival)**: 48框道具`80300-80347`(ItemType9,col8=`{框cfgID 10028-10075}|-1`,col20=DK_Img_Player_AvatarFrame_WC_*) + 48表情道具`15700-15747`(col8=表情ID300-347,col20=DK_icon_global_WC_*) + 2自选池(Reward组`291201`框48/`291202`表情48,行号24565-24660连续) + 2宝箱道具(`1148`自选头像框宝箱/`1149`自选表情宝箱,ItemType20挂池+宝箱DK) + i18n 196行(各语言先填中文待x3-translation翻)。
- **client**: 2宝箱图标128落仓`Spirits/ActvWorldCup/WC_AvatarFrameChest.png|WC_EmoteChest.png`+注册DK(Path_Item)。生成器`KB\产出-数值设计\X3_世界杯\gen_wc_cosmetic_items.py`(读cfg表批量产→暂存`_stage_cosmetic\`→分批落)。
- **DK现状(仓库核实)**: 48头像框(Path_Personalise)/48表情+48气泡(Path_Emoticons)/48队徽+48队伍板+入口(Path_Activity)/券图全已注册+png落仓。框可穿戴cfg=PersonalizeAvatarFrameCfg(48)、表情cfg=Emoticons表(48)均已存在。
- ⚠️**导表核对build必须认分支**: lastBuild可能是`dev`分支别人的(会SUCCESS误导);必须查console `branch=dev_festival`+我们的commit号确认是我们的build再下结论。jolt_verify超时拿不到build号时尤其要手动核对。

## ⚠️BP配置铁律(2026-06-16踩坑·点升级没反应根因)
- **BattlePassScoreReward 行ID必须 = RewardGroup×100 + Level**(代码`ActivityUtils.NewBattlePassScoreRewardCfgID=group*100+level`硬拼ID查行)。组140→Lv1必须14001..Lv20=14020;春节组137=13701..13720为正例。
- 世界杯BP曾配成14201-14220(142xx段)→代码按14001查`CBattlePassScoreReward.I()`取null→**升级/买级点了无响应**(但奖励正常显示,因奖励走GroupIds遍历不依赖精确ID→症状=奖励对/升级失效,极易误判为"升级积分要求错")。修=改回140xx,commit ae37f9d。
- 配新BP奖励组前先验:行ID=组号×100+等级。

## ★竞猜结算「玩家支持哪个队」查日志链路(2026-06-17 代码层已验证,补零后端结算SOP)
**口径=玩家支持的队 = 他买的哪个 Pack**(防对冲锁定→一场只能选一队,买的Pack=立场)。竞猜Pack `892001-892112`(每场两队各一包),Pack→队伍映射真源=`_stage_activities\_manifest.txt` / `Pack__Pack.tsv`第36列(国名) / i18n `TXT_Pack_Name_{packID}`。⚠️现随机对阵占位,真对阵重跑生成器后映射会变,查时以最新manifest为准。
- **统一口径(免费1钻+付费都覆盖·推荐)**: `v1090.ods_user_asset` WHERE `reason_id='buy_gift'` AND `reason_sub_id` = Pack ID(892xxx)。`reason_sub_id`就是Pack配置ID=队伍。去重用每个竞猜包都发的券`asset_id='Item_1146'`(一次购买只算一行)。
- **仅付费(带金额)**: `v1090.ods_user_order` WHERE `iap_id`=Pack ID。★**已验证 X3 的 ods_user_order.iap_id 直接=Pack ID**(尼罗包210601-210611与Pack ID 1:1对齐,dim_iap可查名)。免费1钻不是IAP订单→此表查不到。
- **代码层证据(=最硬的上线前验证,不依赖数据)**: ①`client\...\CSShared\Common\SysOpReason.cs:14` `ItemOPBuyGift="buy_gift"`(注释"已用于BI,不可更改") ②`GetNewReason(reason,subId)=reason+分隔符+subId`→数仓拆成reason_id/reason_sub_id ③`GiftMeta.cs` 发奖统一`GetNewReason(ItemOPBuyGift, cfgID)`,cfgID=Pack配置ID ④`OnBuyGiftReq`(钻石/现金/金砖入口)+真实IAP走`NotifyDeliveryGift`,**两条入口共用`HandleGiftReward`**→免费钻包和付费都打`buy_gift+PackID`。竞猜包就是普通Pack行,走全游戏同一段礼包记账码,出错概率≈0。
- **⚠️GM验证不了**: 礼包模块**无"模拟购买"GM**(只有重置购买次数/触发链式/触发推荐),购买是客户端消息`OnBuyGiftReq`[MsgHandler],GM调不到;GMAddItem塞道具走gm reason不打buy_gift→测了等于没测。真要端到端只能客户端真买一笔。
- **⚠️dev服不进数仓**: `v1090`只有生产服(1800-2190区间),dev/测试服(如3080)+892xxx流水不在数仓。dev端到端验证只能走:iGame订单`/order/query_by_user_id`(按玩家查·**仅付费**·dev沙盒付费可能0单不写订单系统,正常)或服务端BI日志(env=dev落`BI.RollingLogFileAppender`文件+UDP127.0.0.1:39999,文件在服务器主机非本机)。iGame dev网关=`https://ms-inner-gateway-dev.tap4fun.com/ark`,dev token在`~/.igame-auth-dev.json`(约10天过期;但订单/资产可直连dev网关+dev token,绕开igame-query.js那条写死生产网关的死路)。
- **★免费包打buy_gift=线上实证(2026-06-17)**: 直接证明"免费(0元/钻)礼包也落buy_gift+PackID"——线上找"在buy_gift但不在订单"的pack=非付费包(如`210601`尼罗之辉-礼包免费1,price列空,今日数千条`reason_id='buy_gift' reason_sub_id='210601'`发Item_1128券,零付费订单)。同理世界杯免费1钻包必落`buy_gift|892xxx`→队伍可查。**至此口径三重验证完毕:代码层(共用记账码)+付费(尼罗包iap_id=PackID)+免费(210601线上buy_gift实跑)。**

## ★竞猜对阵换队/改对阵 配置链(2026-06-17 热更测试 JORvsIRN→ENGvsBRA 实证)
竞猜=**ActvType=64**。一场比赛(fixture) = 一个付费 ActvOnline(`1029xx`,备注`WC竞猜-{轮次}-{T1}vs{T2}-${价}`) + 一个免费变体(`1029xx`,备注`WC免费竞猜-{日期}-{T1}vs{T2}`,如102920付费/102976免费同为JORvsIRN)。**ActvName/Desc走共享cn(胜负预言·32强/16强..)按cn复用,不区分对阵**。
- **每场2个助威礼包(每队1个)**: 付费`892xxx`+免费`893xxx`。**队伍编码在 Pack__Pack.tsv 行**(0-idx列): `[25]DK_WC_TeamPanel_{CODE}`(队伍面板图) `[27]DK_WC_Badge_{CODE}`(队标/旗) `[35]队名`(中文备注·表头空·客户端不读) + bonus列`TXT_WC_Oracle_Bonus_T1/Free`。
- **玩家可见队名 = `TXT_Pack_Name_{packID}`**(不是col35备注,也不是TXT_WC_Team_*——后者只有ARG/BRA两个、非通用源)。竞猜面板显示的队名读这个。`TXT_Pack_Desc_{packID}`=猜对加送+X(bonus文案)。⚠️这批 TXT_Pack_Name 历史上 en=cn=中文未翻(我的WC i18n批量补译没覆盖8920xx段,正则只到2110段)。
- **改一场对阵 = 改该fixture全部礼包(付费+免费各队,如JORvsIRN=892001/892002/893001/893002)的**: ①col25 TeamPanel ②col27 Badge ③col35备注队名 ④`TXT_Pack_Name`(用 `wc_country_table.json` 16语正确本地化) + ⑤ActvOnline付费/免费两行的备注(col1)。用 `tsv_edit.py set --col <0idx> --old/--new` 逐格断言改。
- **★队标资源位置**: 48国全部 `DK_WC_TeamPanel_/DK_WC_Badge_{CODE}` 注册在 client `Assets\Res\Config\DisplayKey\Path_Activity.asset`(含BRA/GER/JPN等非32强参赛队也有)。**但 `Assets\Editor\Config\tableResInfo.txt` 只列32强参赛的32队**(BRA等没列)——换非参赛队时别被 tableResInfo 误导以为没资源,**真源是 Path_Activity.asset**(且 tableResInfo 可能过期,见[[reference_x3_client_resources]])。
- **落地**: 改 Pack/ActvOnline tsv + Text tsv(TXT_Pack_Name) → sync_xlsx_tsv --auto(Pack/ActvOnline/Text三xlsx) → ExportTable自测 → commit+push+jolt。Pack col3(`WC-32强-JOR-$4.99`内部备注)不影响显示可不改。

## ★★决策记录+已落地：让竞猜对阵「热更服务端就能换」(2026-06-17, 客户端改动已push dev_festival commit 4bd6029717a)
**问题**：上面那套换对阵全改客户端配置(ActvPack/Pack/i18n),但热更只热服务端、够不到客户端(见 [[workflow_x3_auto_jolt_export]] 热更边界) → 世界杯淘汰赛赛程会变却动不了。**根因**：竞猜零后端,客户端**显示**直读客户端配置 `CActvPack.I(ContentID).PackList`。
**方案(已落地)**：客户端改读**服务端下发的 progressPackData**,不读 CActvPack。**proto零改、服务端零改**——服务端 `ActivityWorldCupGuessCondition.OnAddActivity`(`client\...\CSSharedHotfix\Game\Activity\ActivityTriggerConditions\ActivityWorldCupGuessCondition.cs`, `#if _SERVERLOGIC_`, **hotfix可热更**)**早已**用 `CreateActivityProgressPack(GetContentId,...)` 从**服务端自己(可热更)的 ActvPack.PackList** 建两队礼包塞进 `progressPackData` 下发(dayItem 带 day(0左/1右)+giftId+**packCfgId**)。客户端只是显示侧错读了客户端配置。
- **已改的唯一一处**：`client\...\UI\Actv\UIActvWorldCupGuess.cs` `RefreshView()`,`mPackList` 来源由 `CActvPack.I(mContentID).PackList` 改为循环 `activityMeta.GetProgressPackPackDayItemByDay(mActivityId, day)`(day=0,1..遇null停)取 `.packCfgId`(属性确认在 activity.cs:3016)。`mContentID` 在 RefreshView 里变成未使用(无害,未清)。
- **生效闭环**：换对阵 = 改服务端 ActvPack.PackList + 热更服务端 → OnAddActivity 重建 progressPackData 下发新 packCfgId → 客户端显示新队。**客户端零重打包**(48队队标 Path_Activity.asset 全量预置、队名走各队 Pack 的 TXT_Pack_Name 预置)。
- **★运营注意**：OnAddActivity 在**活动开窗时**读 ActvPack 建包;换某轮对阵必须**在那场活动开窗前**改好 ActvPack + 热服务端,已开实例不回溯重建(淘汰赛按轮提前配正好)。
- **分支策略**：x3-project 受保护的是 `dev`;`dev_festival` 等是工作分支,**直接 push 不用 MR**(测试客户端从工作分支出包);只有合进 `dev` 正式线才走 MR(见 [[workflow_x3_protected_branch_mr]])。
- **状态**：客户端读改完+已push dev_festival;待测试客户端从 dev_festival 出包验证「改 ActvPack.PackList+热服务端→对阵变」闭环。**已验证服务端侧生效**(改ActvPack.PackList+热服务端→下发变,用户实测过)。

## ★竞猜礼包池重构(2026-06-17, Phase A已push 34909e9; B/C在途)
**目标**:把旧"每场两个专属礼包"(146个,per-轮次)换成 **48国×4档=192 的 per-country 礼包池**,PackList 只去池里指两国→服务端自由换队。奖励走档(身份只靠 name+DK)。
- **ID段**: `894CCT`(CC=国01-48按code字母序, T=0免/1=4.99/2=9.99/3=19.99) = 894010~894483。
- **奖励口径**: 免费=291335 / 4.99=291101 / 9.99=291330(通用自选头像框宝箱) / 19.99=**新建291399**(克隆291317把JOR表情15725→自选表情宝箱1149,通用)。per-country外显奖励(押注队的头像框/表情)被砍成通用自选宝箱;若产品要"得所押队外显",才需per-country奖励(暂不做,跟客户端出包补)。
- **★可复用脚本(C:\Users\linkang\)**: `gen_wc_pack_pool.py`(生成器,内含48国code↔cn表+4档模板克隆+TXT16语,preview/apply双模式) / `preview_wc_rewire.py`(Phase B 旧包→池映射预演,按备注code+价位)。48国code↔cn映射在 gen 脚本里(32强32队从包抽+16队FIFA)。
- **三阶段(全部✅完成,jolt SUCCESS)**:A建池(192包+192TXT+291399奖励,commit 34909e9)/ B重指73行ActvPack旧包→池/ C删146旧包+292条TXT_Pack(Name+Desc)(B+C commit dca02f1)。**旧146包已全删,竞猜活动全指向894新池**。⚠️xlsx删行同步极坑,见 [[reference_x3_tsv_export_migration]] 「批量删行同步xlsx大坑」(必须openpyxl remove+recreate sheet+csv.reader解析+全字符串写)。备份 `C:\Users\linkang\wc_old_packs_backup_20260617.tsv`(146包)+`wc_old_packs_txt_backup_20260617.tsv`(292TXT)。
- **⚠️遗留**:① 2920(付费JORvsIRN场)被测试改成ESP|FRA,其免费场2976仍JOR|IRN→不一致,执行B前定2920真实队;② 9.99/19.99 仅口径通用,"测试该国表情"的4包未单独配。
- 模板列位(Pack tsv,1-idx): col3备注/col7价/col8 PackPrice/col14奖励Content/col26 DK_TeamPanel/col28 DK_Badge/col36队名(Name源→TXT_Pack_Name)/col37 bonus(TXT_WC_Oracle_Bonus_T1/2/3/Free)。
- **⚠️价格坑(2026-06-17 用户抓出,真金白银)**: 礼包**真实IAP价走 col8 PackPrice→`Pack__PackPrice.tsv`(GiftPriceCfg)的 Dollar 字段**,**不是 col7 显示价**。且 PackPrice id↔金额**非顺序**: `105=$4.99 / 106=$7.99 / 107=$9.99 / 111=$19.99 / 109=$14.99 / 112=$29.99...`。旧竞猜模板把9.99档配成106($7.99)、19.99档配107($9.99)→**显示9.99/19.99实收7.99/9.99**,克隆建池时继承,已修(48+48包: 9.99→107, 19.99→111, 4.99=105本对)。**克隆礼包模板务必核 col8 PackPrice 对不对得上 col7 显示价**(查 Pack__PackPrice.tsv 的 Dollar)。
- **✅已完成(2026-06-18)**: 「全部竞猜活动(ActvType64,76个)ActvOnline.TimeCycle(col8)→0(不配,改走iGame/外部控时)」**已提交 dev_festival commit 4291166 + push + jolt**;导表验证 TimeCycle=0 不报FK错(**导表脚本不用改**)。备份留底 `C:\Users\linkang\wc_actvonline_timecycle0_backup_20260618\`。(过程曾被并发agent的 protect-WIP stash 卷走一次,重做时立即commit锁住——见下条并发坑)
- **⚠️并发agent踩坑(2026-06-18)**: gdconfig 是**多agent共用一个工作目录**。我的未提交改动被另一个agent的 `git stash`("protect-others-wip-pack-reward")**连同它的Reward WIP一起卷走过一次**。教训:**共用仓里配置改完别久留未提交→尽快commit或文件级备份**;`stash@{0}`含别人WIP**勿pop**;切分支会动共用工作区(未跟踪文件如`_staging_weeklycard/`会带过去)。

## ★操作流程：配/换一场竞猜对阵 + 热更(2026-06-17 实测,团队反复用这套)
配任意一场(小组赛/淘汰赛)对阵 = **只改 ActvPack.PackList 指向两队的池包**,不动礼包不动客户端:
1. **算两队池包ID** = `894`+`CC`+`T`。CC=队code在48队**字母序**序号(01-48), T=档(0免/1=$4.99/2=$9.99/3=$19.99)。懒得算就 `grep "WC竞猜池-{CODE}-{档}" tsv/Pack__Pack.tsv` 拿ID。48队code见 [[reference_x3_tsv_export_migration]]段或 `gen_wc_pack_pool.py`。例:BRA-4.99=894071, GER-4.99=894211。
2. **选/建活动(ActvType64)**:ContentID=活动的col5。`tsv_edit.py set --file tsv/ActvPack__ActvPack.tsv --id <ContentID> --col2(0idx) --old <旧> --new "<左队池包>|<右队池包>"`(PackList[0]左/[1]右)。
3. **部署**:`sync_xlsx_tsv --auto`→`--check` mismatch=0→本地 `ExportTable.py` 过→commit+push dev_festival→`jolt_verify` 构建SUCCESS。(jolt 多发会 ABORTED/超时=被在跑build顶,查 Jenkins lastBuild result 定论)
4. **热更服务端** + **重开该活动**(GM重触发/调时间;OnAddActivity 开窗时才读ActvPack建progressPackData,已开实例不回溯)。
5. **验证**:服务端抓下发 progressPackData 两 dayItem.packCfgId==两队池包(不依赖客户端);客户端(带4bd6029 build)进竞猜看队名/队标变。
- **⚠️小组赛活动还没建**:现仅3测试活动(102911付费/102912免费/102913皮肤)+淘汰赛(32强~决赛,1029xx)。小组赛要**新建一批 ActvOnline(type64)+ActvPack+TimeCycle**(TimeCycle定开窗,服务端调度)。测试流程已用 102911 配 BRAvsGER 实跑通(commit 3b95002,build #1054 SUCCESS)。

## v0.39 美术注册完整性审计(2026-06-22,只读)
- **结论**:dev_festival 上 WC 配置引用的 **163 个 DK 全部已注册+文件在位**(缺注册0/文件缺0/无LFS未拉)——48队徽`DK_WC_Badge_*`+48队伍板`DK_WC_TeamPanel_*`+48应援表情`DK_WC_*`(→`Res/UI/Gif/WC_*.bytes`)+各模块Bg/Icon+荣耀金币/抽奖券/两宝箱/铭牌。**WC美术齐**。
- **唯一缺口=3款里程碑专属外显「从没做」(非没注册)**:晋级之路框/世界之巅框/世界之巅表情(规划ID 80348/80349/15748,**全表0命中=配置里就没建行**);里程碑奖励现发**通用宝箱占位**(`DK_WC_AvatarFrameChest`自选框 / `DK_WC_EmoteChest`自选表情)。补不补是产品决策,补=出图→建Item/Frame/Emote行→DK注册。
- **★审计法(可复用)**:`grep -rhoE "DK_WC[A-Za-z0-9_]*" tsv/`收集配置引用DK → diff `client/.../DisplayKey/Path_*.asset` 里 `- key: DK_` 注册项 → 缺集=未注册;再对注册项的objPath查文件存在(⚠️objPath相对**client/工程根**不是repo根,查存在要拼`client/`前缀,否则全报缺=假阳性)。<2KB=LFS指针(图没拉)。

## ★决赛外显收尾(2026-07-15,全部✅进dev)
决赛外显=4冠军框(ESP/ARG/ENG/GOLD大力神)。~~+1冠军头衔「绿茵之王」~~**头衔已撤下不投**(2026-07-15用户拍板:头衔道具ICON做不大,跟深海节头衔/世界杯排行榜头衔尺寸冲突)→从$19.99奖励组291373摘除头衔道具82007(dev commit,build验证)。**当前奖励:$19.99=纯金GOLD框+券80+钻万+VIP100 / $9.99=国家框+券40+钻5000+VIP50**。
- **⚠️头衔休眠遗留(未清,无害,以后要复用/清理看这里)**:PlayerTitle 107、item 82007、i18n(107/82007的中英+14语言)、客户端banner`WC_title_champion.png`+图标`icon_global_WC_champion.png`+两DK(`DK_WC_title_champion`/`DK_icon_global_WC_champion`)全部已建但**无任何grant入口=永不发放**。要彻底清=删291373已无关联的item/title/DK/asset/i18n(多个MR,不值当);要复活=重加reward行即可。配置主体见 scratchpad `final_config.py`(framecfg 10089-92/item 80356-59+82007/PlayerTitle 107/reward 291370-373/重指3队8强包)+`final_client.py`(4框256→Personalise+头衔横幅752×192→MiscIcons),已 commit dev 3724fae2/client MR!756。**本轮补的两个尾巴**:
- **① 头衔专属道具ICON**(之前借用老头衔图`DK_icon_global_WCtitle`,用户要专属):GRFal出图=金色大力神杯+绿底桂冠皇冠徽章,`WC_title_champion_icon.png`。客户端`icon_global_WC_champion.png`(256)→`Res/UI/Spirits/ItemIcons/`,DK`DK_icon_global_WC_champion`注册Path/Display_Item(**道具小图ICON走Item表不是MiscIcons**),client commit 63015ee1ab6→**MR!768**→dev。配置item 82007 col21(0idx20)从`DK_icon_global_WCtitle`改`DK_icon_global_WC_champion`,dev commit(build#1816 SUCCESS)。
- **② i18n补全14语言**:决赛16个key(4框名`TXT_PersonalizeAvatarFrameCfg_Name_10089-92`+4道具名`TXT_Item_Name_80356-59`+4描述`TXT_Item_Desc`+头衔`TXT_PlayerTitle_Name/ObtainDesc_107`+头衔道具`TXT_Item_Name/Desc_82007`)原只中英,补sp/fr/id/de/kr/繁中/ru/ua/jp/it/pl/pt/tr/th。**i18n表列布局(1idx)**:col1 key/col2-3 optional空/col4 cn/col5 en/col6 sp/7 fr/8 id/9 de/10 kr/11 zh(繁体)/12 ru/13 ua/14 jp/15 it/16 pl/17 po(葡)/18 tr/19 th(全填=nz17,总列宽28)。翻译子agent写脚本精确填col6-19,已push dev导表SUCCESS(钉钉为准,jolt_verify本地轮询偶发不回写别慌)。
- **⚠️实机显示前提**:330/220服客户端要**重打包含MR!768**(+MR!756决赛框资源),头衔图标/框才实机显示;服务端配置刷新≠客户端build刷新(新client资产不在AB就显示占位/旧图)。
- **顺带**:券DK错位修复MR!766早已merged进dev(Path_Item孤儿key`DK_Img_Icon_59`只加key漏value顶偏26图标,补value+重排单调)。全量Path_*.asset平行审计=仅Path_Item曾错位,hehaofei其他DK commit均平行OK。

## ★半决赛结算(2026-07-17) + settle_from踩坑复盘 + 决赛对阵
- **SF结算已发**:SF-ESPvFRA **西班牙2-0法国·ESP胜**(3233笔·**mailId 4750902**)/SF-ARGvENG **阿根廷2-1英格兰·ARG胜**(5219笔·**mailId 4750903**)·均status2待iGame后台放行。GM加分合并2块`发奖csv\GM纯命令_合并_part1.txt`(4342条)+`part2.txt`(4110条·共8452)待粘。dashboard settled已含SF两场。
- **⚠️踩坑1·settle_from没随轮次前移=重复发钱(本次差点发错)**:7/16有人生成过SF文件但settle_from还停在7/9(QF的)→把QF窗口(7/09-11)的下注全算进SF。**发前用本地CSV交叉验证抓出**:SF-ESPvFRA(押ESP)错版7084人里,QF-BELvESP的5926押ESP玩家100%全在(QF独有=0)=铁证泄漏。datain查ESP池(894190-193)按日下注证实:QF群7/09-11 → **7/12断档** → SF群7/13起,SF开盘=**7/13**。改settle_from=7/13重跑→ESP降7084→3233(剔除3831 QF-only)、ARG 5217(剔除2914)。**教训:每轮结算前必改wc_dashboard_data.json的settle_from=本轮开盘日,发前用「新SF赢家∩上轮同队QF赢家/QF独有」验隔离(QF独有应远大于0)**。错版备份`发奖csv\_WRONG_settlefrom79_backup_20260717\`。
- **⚠️踩坑2·datain静默返0=打错集群**:X3(1090)在**TRINO_HF**,`_datain_api.execute_sql(sql)`默认TRINO_AWS→静默返空/max分区显2026-01-08(假象)。生成器内部已`execute_sql(sql,'TRINO_HF')`正确,但手动查必带集群:`query_trino.py --datasource TRINO_HF`。见[[reference_ai_to_sql]]。
- **★决赛对阵=西班牙vs阿根廷(不是英格兰!)**:SF赛果ESP淘汰FRA、**ARG淘汰ENG**→决赛ESP vs ARG。英格兰出局。之前上330测试的「决赛ENG vs ESP」是错的(330测试服用户说不用管)。决赛外显ESP/ARG框现成(ENG框废弃)。**季军赛(ENG vs FRA)不上竞猜**(用户2026-07-17定)。决赛竞猜上prod时按ESP vs ARG。

## ★决赛竞猜已上prod(2026-07-17)
- **对阵=西班牙(ESP) vs 阿根廷(ARG)**(ESPN确认Argentina at Spain 7/19 19:00Z)。已上prod **83服**·cfg **102976-979**·ark单号**14241-14244**·status2待激活·锁盘**2026-07-19 18:50 UTC**。部署脚本=`igame-x3-activity-deploy\deploy_final.py`(新建)。
- **★决赛包路由(与SF不同·接管keypoint)**:四档全走`base(队)+t`(不是SF的4强容器)。ESP池894190-193/ARG池894020-023。**tier2($9.99)/tier3($19.99)=8强包已重指决赛外显奖励**:894192→291370(西班牙冠军框80356)·894022→291371(阿根廷框80357)·894193/894023→291373(GOLD大力神框80359·**无头衔**)。免费/4.99=原8强券档(291335/291101)。**已核master(prod)上291370-373+Pack c14重指全在位**,奖励链prod侧完整。
- **cfg标题无所谓**:TXT_WC_Guess_Title_{R32..FINAL}全是同一句「胜负预言/Match Oracle」,任意cfg显示都对(SF2当年就用了FINAL标题的cfg)。
- **⚠️季军赛(ENG vs FRA·7/18)不上竞猜**(用户定)。
- **⏳决赛结算(7/19锁盘后做)**:①`wc_dashboard_data.json`已加`FINAL-ESPvARG`(schedule第15项→生成器cfg102976对齐)②**settle_from必须改2026-07-17**(决赛开盘日·隔离SF的7/13老下注,ESP/ARG在SF窗口都被押过)③ESPN出结果→跑`_gen_发奖详情.py`→发邮件+GM→settled加FINAL。
- **⚠️遗留·决赛框i18n**:决赛4框名+描述的**14语言在dev没同步master**(master只cn/en)。框在**购买$9.99/$19.99时即发**(非结算时)→非中英玩家买框看英文兜底名。不阻塞下注,但决赛窗口内最好把dev的决赛i18n(TXT_Item_Name/Desc_80356-59+framecfg名)同步master。

## ★决赛结算已发(2026-07-20) — 世界杯竞猜收官
- **决赛=西班牙1-0阿根廷·西班牙夺冠**(ESPN)。总竞猜6697人·猜中**3749笔/3738人**·命中率55.8%·**mailId 4756774**(status2待放行)。GM加分`发奖csv\GM纯命令_FINAL-ESPvARG.txt`(426KB单块<490K无需切)待粘。settled已含FINAL-ESPvARG。
- **settle_from=2026-07-17(决赛开盘日)隔离生效**:决赛ESP赢家3738 vs SF-ESPvFRA的ESP赢家3233·SF独有1861被正确剔除(没重复发)·交集1372(两轮都押ESP)。**再次验证每轮结算必改settle_from=本轮开盘日**。
- **世界杯竞猜全流程收官**:R32→R16→QF→SF→FINAL全部结算发奖完毕(季军赛不上竞猜)。决赛外显ESP/ARG框已随$9.99/$19.99礼包在下注时发放。
