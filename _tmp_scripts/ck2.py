# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-活动美术需求"; GID=1651551353
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
KB="KB/产出-数值设计/X3_深海节/复用参考图/夏日/"; R="client/Assets/Res/"
POR=R+"UI/Spirits/Role/Character Portraits/"; SP=R+"Spine/Prefabs_Download/"; FA=R+"UI/Spirits/Furniture/Actv/"; ICN=R+"UI/Spirits/ItemIcons/"
SEM="主视觉锚·赛米拉(海滨):"+POR+"Img_C_H_17_Skin01.png + spine "+SP+"Role_Spine_17_Skin01.prefab"
NEED="🔧无现成投放物·需新出"
rows=[]
rows.append(["深海节 · 活动美术需求 CHECKLIST（老图参考=格式结构 / 新图参考=实际投放物元素）"])
rows.append(["规范 reference_x3_art_resource_spec.md。尺寸:复用类=与复用源同尺寸/新出类=查到px。明亮潜水海洋风·非深渊·偏亮不阴暗。详细见「深海节-各活动模块」。状态:待制作/✅复用现成/🔧待策划。"])
rows.append([""])
rows.append(["【视觉调性】","主色海蓝/浅蓝/青绿+金黄(宝藏)+珍珠白(贝壳)+暖橘(阳光)；明亮潜水海洋风(非深渊·偏亮不阴暗·潜水与泳装/海滨不冲突)；卡通奇幻；水波/气泡/光斑/鱼群/航线/珊瑚；避坑:不阴暗·不克苏鲁·与航海之路区分"])
rows.append([""])
rows.append(["#","模块","美术类型","要求(场景+元素)","尺寸/格式","老图参考·格式结构","新图参考·投放物元素","状态","完成✓"])
i=[0]
def row(*a):
    a=list(a)
    if len(a)==8: a=[a[0]]+a[2:]
    m,t,req,sz,old,new,st=a
    i[0]+=1; rows.append([str(i[0]),m,t,req,sz,old,new,st,""])
row("①深海罗盘","转盘外观(逐件换皮)","金边框→锚链/珊瑚/贝壳;中心罗盘/舵轮;指针金锚;8格蓝×青绿","与尼罗转盘同尺寸逐件取原 /png","包装:"+KB+"大转盘.png;源:"+R+"UI/Spirits/Activity/img_turntable_icon1~6.png",SEM,"待制作")
row("","","转盘活动背景","明亮浅海俯瞰+航线+小岛/沉船宝藏/珊瑚+光斑+气泡","1080×1344(=尼罗img_queen_bg_3) /png","包装:"+KB+"大转盘.png;源:"+R+"UI/Spirits/ActivityImg_Download/img_queen_bg_3.png",SEM,"待制作")
row("","","背景立绘","直接用主推赛米拉(海滨)立绘,现成无需新画","=尼罗立绘位 /spine","源:尼罗大转盘立绘槽位",SEM+" ✅现成","✅复用现成")
row("","","传说铭牌图","锚+罗盘+浪花徽章(传说·金+蓝)","~752×192 /png","源:现有title铭牌资源",NEED,"待制作(新出)")
row("","","活动HUD icon","深海罗盘入口","124×136 /png","同HUD活动icon规格",SEM,"待制作")
row("②远航日志(BP)","BP主界面背景","海图桌:海图卷轴+罗盘/望远镜/船舵,暖光船舱","=夏日BP背景同尺寸 /png","包装:"+KB+"02_为誓言而战_BP_102236.png;源:夏日BP背景(ActivityImg)",SEM,"待制作")
row("","","史诗铭牌图","船舵+海浪徽章(史诗)","~752×192 /png","源:现有title铭牌资源",NEED,"待制作(新出)")
row("③怦然心动·深海","每日礼包背景/弹窗","漂流瓶里的信+珍珠/贝壳,浅蓝水面+光斑","=夏日每日礼包弹窗同尺寸 /png","包装:"+KB+"怦然心动.png",SEM,"待制作")
row("","","礼包展示视频(分镜见模块)","深海版重制·4镜(下潜→开瓶→礼包道具飞出→定格)","~15s /mp4","包装:"+KB+"怦然心动.png;节奏:"+KB+"录制_2026_05_27_17_46_46_144.mp4",SEM,"待制作")
row("④深海印记","通用礼包banner","贝壳/珊瑚/锚边框+$9.99价格位","=礼包墙banner槽位(待程序定) /png","同礼包墙现有banner",SEM,"待制作")
row("","","深海头像框图","贝壳/珊瑚/锚链环绕框+珍珠,蓝金边","256×256(AvatarFrame) /png","源:现有玩家头像框资源",NEED,"待制作(新出)")
row("⑤深海馈赠(累充)","累充活动背景","沉船金币堆+宝箱金光+鱼群,金黄×亮蓝","=夏日累充背景同尺寸 /png","包装:"+KB+"07_花瓣与恩典_累充_100595.png;源:夏日累充背景(ActivityImg)","顶档投放物·深海猎手潜艇船皮肤(15065):"+ICN+"icon_global_ship_skin_submarine.png","待制作")
row("","","顶档外显(船皮肤)","深海猎手潜艇(永久15065,现成)","现成","-","投放物:"+ICN+"icon_global_ship_skin_submarine.png","✅复用现成")
row("⑥深海居所(装饰)","礼包banner","椰树+遮阳伞+沙滩+海浪+泳圈,暖橘×浅蓝","=装饰阶梯礼包banner同尺寸 /png","包装:"+KB+"08_夏日装饰礼包_装饰阶梯_106101.png","投放物·椰风遮阳椅(151043):"+FA+"icon_jiaju_summer_3.png","待制作")
row("","","装饰物(椰风遮阳椅)","椰风遮阳椅(海滨假日151043,现成)","现成 DK_icon_jiaju_summer_3","-","投放物:"+FA+"icon_jiaju_summer_3.png","✅复用现成")
row("⑦海滨之约(拜访)","拜访活动背景","海滨酒馆门面:海风+门楣+棕榈+海平面,暖橘×浅蓝","=夏日拜访背景同尺寸 /png","包装:"+KB+"03_夏日柔情海湾_拜访礼包_105603.png+门头拜访礼包.png","门头door:"+R+"Furniture/Model/Furniture_Door_Wall_Column_Skin08/Texter/Furniture_Door_Skin08.png;地板:"+R+"Furniture/Prefabs/Floor/FurnitureFloor_Actv_Summer.prefab;"+SEM,"待制作")
row("","","门头+地板(投放物)","海滨假日门头1001009/地板2001013(现成)","现成","-","门头icon "+FA+"icon_jiaju_summer_4.png;地板icon "+FA+"icon_jiaju_summer_2.png","✅复用现成")
row("","","礼包图/icon","海滨门头礼包$99.99","=拜访礼包图同尺寸 /png","包装:"+KB+"门头拜访礼包.png","门头door:"+R+"Furniture/Model/Furniture_Door_Wall_Column_Skin08/Texter/Furniture_Door_Skin08.png","待制作")
row("⑧许愿池","活动背景(仅换图)","深海许愿池:水底光柱+漂浮许愿币/贝壳/珍珠,明亮青绿","=许愿池原背景同尺寸(取原替换) /png","源:许愿池界面现有背景资源","无独立投放物·沿用 "+SEM,"待制作(只背景)")
row("⑨最佳酒馆","活动背景(仅换图)","远航酒馆:海图+酒桶+船舵+舷窗外深海,暖光","=最佳酒馆原背景同尺寸(取原替换) /png","包装:"+KB+"05_为爱干杯_最佳酒馆_10071702.png;源:酒馆界面现有背景","无独立投放物·沿用 "+SEM,"待制作(只背景)")
rows.append([""])
rows.append(["合计需新出背景/banner/视频约13项；🔧需新出美术(无投放物)3项:传说铭牌/史诗铭牌/深海头像框；✅复用现成5项:立绘(赛米拉)/船皮肤(潜艇)/椅子/门头/地板"])
rows.append(["★完成列美术自行打✓。老图=照格式/尺寸；新图=照投放物元素配色,使背景与所售内容一致。详细见「深海节-各活动模块」。"])
gws(['sheets','spreadsheets','values','clear','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:I40"})])
o=gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1","valueInputOption":"RAW"})],{"values":rows,"majorDimension":"ROWS"})
print("write:", 'OK rows='+str(len(rows)) if 'updatedCells' in o else o[:160])
