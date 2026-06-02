# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-活动美术需求"; GID=1651551353
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
KB="KB/产出-数值设计/X3_深海节/复用参考图/夏日/"; RES="client/Assets/Res/UI/Spirits/"
R=[]
R.append(["深海节 · 活动美术需求 CHECKLIST（美术对接清单·与各活动模块美需同源）"])
R.append(["规范 reference_x3_art_resource_spec.md。尺寸原则：复用类=与复用源同尺寸(美术取原资源)；新出类=查到px。详细场景/元素见「深海节-各活动模块」。状态:待制作/✅复用现成/🔧待策划。"])
R.append([""])
R.append(["【视觉调性】","主色深蓝/浅蓝/青绿+金黄(宝藏)+珍珠白(贝壳)+暗绿紫(海怪)；卡通奇幻；表现水波/气泡/光斑/鱼群/航线/沉船剪影；避坑:卡通非克苏鲁·与航海之路/夏日海滨区分·沙滩底加水"])
R.append([""])
R.append(["#","模块","美术类型","要求(场景+元素)","尺寸/格式","参考(全路径)","状态","完成✓"])
i=[0]
def row(*a):
    a=list(a)
    if len(a)==7: a=[a[0]]+a[2:]  # 去掉误加的空列
    m,t,req,sz,ref,st=a
    i[0]+=1; R.append([str(i[0]),m,t,req,sz,ref,st,""])
row("①深海罗盘","转盘外观(逐件换皮)","金边框→锚链/珊瑚/贝壳；中心罗盘/舵轮；指针金锚；8格深蓝×青绿","与尼罗转盘同尺寸·逐件取原 /png","包装:"+KB+"大转盘.png；源:"+RES+"Activity/img_turntable_icon1~6.png+img_ui_turntable_bg2.png","待制作")
row("","","转盘活动背景","海域俯瞰+航线+远景沉船宝藏/珊瑚礁+光斑+气泡","1080×1344(=尼罗img_queen_bg_3) /png","包装:"+KB+"大转盘.png；源:"+RES+"ActivityImg_Download/img_queen_bg_3.png","待制作")
row("","","背景角色立绘","克利奥佩特拉→深海皮肤","=尼罗立绘同尺寸 /spine或png","源:尼罗大转盘界面立绘资源(同槽位)","🔧待策划定方向")
row("","","传说铭牌图","锚+罗盘+浪花徽章(传说·金+深蓝)","~752×192(title) /png","源:现有title铭牌资源","待制作")
row("","","活动HUD icon","深海罗盘入口图标","124×136 /png","同HUD活动icon规格","待制作")
row("②远航日志(BP)","BP主界面背景","海图桌:海图卷轴+罗盘/望远镜/船舵/羽毛笔,暖光船舱","=夏日BP背景同尺寸 /png","包装:"+KB+"02_为誓言而战_BP_102236.png；源:夏日BP界面背景(ActivityImg)","待制作")
row("","","史诗铭牌图","船舵+海浪徽章(史诗)","~752×192(title) /png","源:现有title铭牌资源","待制作")
row("③怦然心动·深海","每日礼包背景/弹窗","漂流瓶里的信+珍珠/贝壳,浅蓝水面+光斑","=夏日每日礼包弹窗同尺寸 /png","包装:"+KB+"怦然心动.png","待制作")
row("","","礼包展示视频(分镜见模块)","深海版重制·4镜分镜(下潜→开瓶→礼包道具飞出→定格)","~15s /mp4","包装:"+KB+"怦然心动.png；节奏:"+KB+"录制_2026_05_27_17_46_46_144.mp4","待制作")
row("④深海印记","通用礼包banner","贝壳/珊瑚/锚边框+$9.99价格位","=礼包墙banner槽位(待程序定) /png","同礼包墙现有banner","待制作")
row("","","深海头像框图","贝壳/珊瑚/锚链环绕框+珍珠,深蓝金边","256×256(AvatarFrame) /png","源:现有玩家头像框资源","待制作")
row("⑤深海馈赠(累充)","累充活动背景","沉船金币堆+宝箱金光+鱼群,金黄×深蓝","=夏日累充背景同尺寸 /png","包装:"+KB+"07_花瓣与恩典_累充_100595.png；源:夏日累充界面背景(ActivityImg)","待制作")
row("","","行军皮肤","深海猎手(永久15065)","现成","现成资源·配置直接投放(美术0产出)","✅复用现成")
row("⑥深海居所(装饰)","礼包banner","椰树+遮阳伞+沙滩+海浪+泳圈,暖橘×浅蓝(底部加水)","=装饰阶梯礼包banner同尺寸 /png","包装:"+KB+"08_夏日装饰礼包_装饰阶梯_106101.png","待制作")
row("","","装饰物(椰风遮阳椅)","椰风遮阳椅(海滨假日151043)","现成 DK_icon_jiaju_summer_3","现成:"+RES+"Furniture/Actv/icon_jiaju_summer_3.png","✅复用现成")
row("⑦海滨之约(拜访)","拜访活动背景","海滨酒馆门面:海风+门楣+棕榈+海平面,暖橘×浅蓝","=夏日拜访背景同尺寸 /png","包装:"+KB+"03_夏日柔情海湾_拜访礼包_105603.png+门头拜访礼包.png；源:夏日拜访界面背景(ActivityImg)","待制作")
row("","","门头三件套","海滨假日门头(横梁1001009/地板2001013/墙纸3001010)","现成","现成:client/Assets/Res/Furniture/Prefabs/Door/Skin08/Furniture_Door_Skin08.prefab","✅复用现成")
row("","","礼包图/icon","海滨门头礼包$99.99","=拜访礼包图同尺寸 /png","包装:"+KB+"门头拜访礼包.png","待制作")
row("⑧许愿池","活动背景(仅换图)","深海许愿池:水底光柱+漂浮许愿币/贝壳/珍珠,青绿幽蓝","=许愿池原活动背景同尺寸(取原替换) /png","源:许愿池界面现有背景资源","待制作(只背景)")
row("⑨最佳酒馆","活动背景(仅换图)","远航酒馆:海图+酒桶+船舵+舷窗外深海,暖光","=最佳酒馆原活动背景同尺寸(取原替换) /png","包装:"+KB+"05_为爱干杯_最佳酒馆_10071702.png；源:最佳酒馆界面现有背景资源","待制作(只背景)")
R.append([""])
R.append(["合计需新出: "+str(sum(1 for r in R if len(r)>6 and r[6].startswith('待')))+" 项；✅复用现成 3 项(深海猎手/椰风遮阳椅/门头三件套)；🔧待策划 1 项(立绘方向)"])
R.append(["★完成列美术自行打✓；状态变更回填本表。详细场景元素+模块上下文见「深海节-各活动模块」对应模块【美术需求】。"])

gws(['sheets','spreadsheets','values','clear','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:H40"})])
o=gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1","valueInputOption":"RAW"})],{"values":R,"majorDimension":"ROWS"})
print("write:", 'OK rows='+str(len(R)) if 'updatedCells' in o else o[:160])
