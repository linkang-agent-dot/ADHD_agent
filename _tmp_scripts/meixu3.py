# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-活动美术需求"
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
R=[]
R.append(["深海节 · 活动美术需求（美术对接清单：场景元素 + 尺寸/格式）"])
R.append(["规范：reference_x3_art_resource_spec.md。尺寸原则：复用类=与复用源同尺寸(美术取原资源)；新出类=查到px。视觉调性见下。"])
R.append([""])
R.append(["【视觉调性】","主色:深蓝/浅蓝/青绿+金黄(宝藏)+珍珠白(贝壳)+暗绿紫(幽灵海怪)；卡通奇幻；表现:水波/气泡/光斑/鱼群/航线/沉船剪影；避坑:卡通非克苏鲁、与航海之路/夏日海滨区分、沙滩底加水"])
R.append([""])
R.append(["模块","美术类型","深海版要求(场景+元素)","尺寸/格式","参考图","状态"])
def row(m,t,req,sz,ref,st): R.append([m,t,req,sz,ref,st])
row("①深海罗盘","转盘外观(DK_Turntable)","金边框→锚链/珊瑚/贝壳质感；中心航海罗盘/舵轮；指针金锚；8格分区深蓝×青绿","=尼罗黄金卷轴转盘同尺寸/png(转盘元素约112×188等,逐件取原)","大转盘.png","待制作")
row("","转盘活动背景","海域俯瞰+航线+远景沉船宝藏/珊瑚礁剪影+光斑+气泡","=尼罗大转盘背景同尺寸(queen_bg_3=1080×1344)/png","大转盘.png","待制作")
row("","背景角色立绘","克利奥佩特拉→深海角色【A女海盗船长/B美人鱼/C深海女神】","=尼罗立绘同尺寸/spine或png","大转盘.png","🔧待策划定方向")
row("","传说铭牌图","锚+罗盘+浪花徽章,传说品质金+深蓝","~752×192/png(头衔标准)","-","待制作")
row("②远航日志","BP主界面背景","海图桌:海图卷轴+罗盘/望远镜/船舵/羽毛笔,暖光船舱","=夏日BP背景同尺寸/png","02_BP_102236.png","待制作")
row("","史诗铭牌图","船舵+海浪徽章,史诗品质","~752×192/png","-","待制作")
row("③怦然心动·深海","每日礼包背景/弹窗","漂流瓶来信+珍珠/贝壳,浅蓝水面光斑","=每日礼包原尺寸/png","怦然心动.png","待制作")
row("","礼包展示视频","深海版","=夏日视频同时长/mp4","录制_..mp4","待制作")
row("④深海印记","通用礼包banner","贝壳/珊瑚/锚边框装点(9.99礼包)","=礼包墙banner(目标UI待程序定)/png","-","待制作")
row("","深海头像框图","贝壳/珊瑚/锚链环绕框+珍珠,深蓝金边","256×256/png(AvatarFrame标准)","-","待制作")
row("⑤深海馈赠","累充活动背景","海底宝藏窟:沉船金币堆+宝箱金光+鱼群,金黄×深蓝","=夏日累充背景同尺寸/png","07_累充_100595.png","待制作")
row("","行军皮肤","深海猎手(永久15065,现成'暂无获取')","(现成)","-","✅复用现有")
row("⑥深海居所","礼包banner","海滨沙滩度假:椰树+遮阳伞+沙滩+海浪+泳圈,暖橘×浅蓝(底部加水)","=装饰礼包banner同尺寸/png","08_装饰阶梯_106101.png","待制作")
row("","装饰物(椰风遮阳椅)","椰风遮阳椅(海滨假日151043,现成)","(现成 DK_icon_jiaju_summer_3)","门头拜访礼包.png","✅复用现有")
row("⑦海滨之约","拜访活动背景","海滨酒馆门面:海风+门楣+棕榈+海平面,暖橘×浅蓝","=夏日拜访背景同尺寸/png","03_拜访_105603.png","待制作")
row("","门头三件套","复用海滨假日门头","(现成 1001009/2001013/3001010)","门头拜访礼包.png","✅复用现有")
row("","礼包图/icon","海滨门头礼包$99.99","=礼包图同尺寸/png","门头拜访礼包.png","待制作")
row("⑧许愿池","活动背景(仅换)","深海许愿池:水底光柱+漂浮许愿币/贝壳/珍珠,青绿幽蓝","=许愿池原背景同尺寸/png","-(许愿池界面)","待制作(只背景)")
row("⑨最佳酒馆","活动背景(仅换)","远航酒馆:海图+酒桶+船舵+舷窗外深海,暖光","=最佳酒馆原背景同尺寸/png","05_最佳酒馆_10071702.png","待制作(只背景)")
R.append([""])
R.append(["★待策划:①背景角色立绘方向(A女海盗/B美人鱼/C深海女神)；⑤累充档位数值(夏日复盘)。尺寸:复用类美术直接取原资源同尺寸；新出类已标px。"])

gws(['sheets','spreadsheets','values','clear','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:H45"})])
out=gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1","valueInputOption":"RAW"})],{"values":R,"majorDimension":"ROWS"})
print("write:", 'OK' if 'updatedCells' in out else out[:140], "rows:",len(R))
