# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
KB="KB/产出-数值设计/X3_深海节/复用参考图/夏日/"
R="client/Assets/Res/"
SP=R+"Spine/Prefabs_Download/"; POR=R+"UI/Spirits/Role/Character Portraits/"
FA=R+"UI/Spirits/Furniture/Actv/"; ICN=R+"UI/Spirits/ItemIcons/"; ACT=R+"UI/Spirits/Activity/"; ADL=R+"UI/Spirits/ActivityImg_Download/"
# 主推皮肤(节日主视觉锚)=热浪尤物·赛米拉(海滨) + 返场海风旅者
SEMIRA="主推皮肤·热浪尤物赛米拉(海滨):"+POR+"Img_C_H_17_Skin01.png + 立绘"+SP+"Role_Spine_17_Skin01.prefab"
HOPKINS="返场·海风旅者霍普金斯:"+POR+"Img_C_H_34_Skin03.png"
def L(*p): return "\n".join(p)
def blk(elem, size, old, new):
    return L(elem, size, "【老图参考·格式结构】"+old, "【新图参考·投放物/主视觉】"+new)
C={
34: blk("转盘外观(DK_Turntable换皮·逐件)：海洋金边框→锚链/珊瑚/贝壳；中心=航海罗盘/舵轮；指针=金锚；8格分区蓝×青绿",
     "【尺寸】与尼罗转盘同尺寸·逐件取原(格子icon=img_turntable_icon1~6/元素=img_ui_turntable_bg*) 【格式】png",
     "包装稿:"+KB+"大转盘.png ；复用源:"+ACT+"img_turntable_icon1~6.png + img_ui_turntable_bg2.png",
     "主视觉锚 "+SEMIRA),
35: blk("转盘活动背景：阳光海域俯瞰+航线+远景小岛/沉船宝藏/珊瑚礁+光斑+气泡(海洋阳光调,呼应海滨投放物)",
     "【尺寸】=尼罗大转盘背景 1080×1344(img_queen_bg_3) 【格式】png",
     "包装稿:"+KB+"大转盘.png ；复用源:"+ADL+"img_queen_bg_3.png",
     SEMIRA),
36: blk("背景角色立绘=直接用主推皮肤赛米拉(海滨)立绘，现成无需新画 ✅(克利奥佩特拉位→换赛米拉)",
     "【尺寸】=尼罗立绘位同尺寸 【格式】spine(现成)",
     "复用源:尼罗大转盘界面立绘槽位",
     SEMIRA+" ；备选返场 "+HOPKINS),
37: blk("传说铭牌图：锚+罗盘+浪花徽章(传说品质·金+蓝) —— 深海版无现成,需新出",
     "【尺寸】~752×192(title标准) 【格式】png",
     "复用源:现有title铭牌资源("+R+"UI/Spirits/.../title)",
     "🔧无现成投放物,需新出；主题锚 "+SEMIRA+" ；另HUD icon 124×136"),
61: blk("BP主界面背景：航海日志/海图桌——海图卷轴+罗盘/望远镜/船舵/羽毛笔,暖光船舱(海洋探险调)",
     "【尺寸】=夏日BP背景同尺寸(取原) 【格式】png",
     "包装稿:"+KB+"02_为誓言而战_BP_102236.png ；复用源:夏日BP界面背景("+R+"UI/Spirits/ActivityImg)",
     "主视觉锚 "+SEMIRA),
62: blk("史诗铭牌图：船舵+海浪徽章(史诗品质) —— 深海版无现成,需新出",
     "【尺寸】~752×192(title) 【格式】png",
     "复用源:现有title铭牌资源",
     "🔧无现成投放物,需新出；主题锚 "+SEMIRA),
84: blk("每日礼包背景/弹窗：海洋每日来信——漂流瓶里的信+珍珠/贝壳,浅蓝水面+光斑",
     "【尺寸】=夏日每日礼包弹窗同尺寸 【格式】png",
     "包装稿:"+KB+"怦然心动.png",
     "主视觉锚 "+SEMIRA),
85: L("礼包展示视频（海洋版·重制，非简单换皮）",
     "【时长】~15s 【格式】mp4 【风格】卡通奇幻·海蓝青绿+金光",
     "【分镜脚本】",
     "镜1(0-3s)：阳光海面，镜头由海面下潜入水；一只漂流瓶随波漂入画面中央",
     "镜2(3-7s)：瓶塞弹开，飘出卷着丝带的来信/卷轴，珍珠贝壳环绕、气泡光斑上浮",
     "镜3(7-12s)：信展开化作礼包，道具逐个飞出特写(养成材料/代币/抽奖券)，金光迸发",
     "镜4(12-15s)：道具收束为礼包icon + 标题『怦然心动·深海』 + 『每日可领』角标，定格",
     "【老图参考·格式结构】包装稿:"+KB+"怦然心动.png ；节奏:"+KB+"录制_2026_05_27_17_46_46_144.mp4",
     "【新图参考·投放物/主视觉】"+SEMIRA),
108: blk("通用礼包banner：海洋主题(贝壳/珊瑚/锚边框,预留$9.99价格位)",
     "【尺寸】=礼包墙banner槽位(待程序定) 【格式】png",
     "同礼包墙现有banner",
     "主视觉锚 "+SEMIRA),
109: blk("深海头像框图：贝壳/珊瑚/锚链环绕框+珍珠,蓝金边 —— 无现成,需新出",
     "【尺寸】256×256(AvatarFrame) 【格式】png",
     "复用源:现有玩家头像框资源(AvatarFrame)",
     "🔧无现成投放物,需新出；主题锚 "+SEMIRA),
133: blk("累充活动背景：海底宝藏窟——沉船金币堆+宝箱金光+鱼群,金黄×蓝",
     "【尺寸】=夏日累充背景同尺寸 【格式】png",
     "包装稿:"+KB+"07_花瓣与恩典_累充_100595.png ；复用源:夏日累充界面背景("+R+"UI/Spirits/ActivityImg)",
     "顶档投放物·深海猎手潜艇船皮肤(15065):"+ICN+"icon_global_ship_skin_submarine.png"),
134: L("顶档外显=深海猎手·潜艇船皮肤(永久 Item15065，现成) ✅ 无需新出 (注:是船皮肤,非行军皮肤)",
     "【新图参考·投放物】"+ICN+"icon_global_ship_skin_submarine.png"),
158: blk("礼包banner：海滨沙滩度假——椰树+遮阳伞+沙滩+海浪+泳圈,暖橘×浅蓝",
     "【尺寸】=装饰阶梯礼包banner同尺寸 【格式】png",
     "包装稿:"+KB+"08_夏日装饰礼包_装饰阶梯_106101.png",
     "投放物·椰风遮阳椅(151043):"+FA+"icon_jiaju_summer_3.png"),
159: L("装饰物=椰风遮阳椅(海滨假日 Item151043，现成) ✅ 无需新出",
     "【新图参考·投放物】"+FA+"icon_jiaju_summer_3.png"),
187: blk("拜访活动背景：海滨酒馆门面——海风+门楣+棕榈+海平面,暖橘×浅蓝",
     "【尺寸】=夏日拜访背景同尺寸 【格式】png",
     "包装稿:"+KB+"03_夏日柔情海湾_拜访礼包_105603.png + "+KB+"门头拜访礼包.png ；复用源:夏日拜访界面背景("+R+"UI/Spirits/ActivityImg)",
     "投放物·海滨门头(1001009)door:"+R+"Furniture/Model/Furniture_Door_Wall_Column_Skin08/Texter/Furniture_Door_Skin08.png + icon "+FA+"icon_jiaju_summer_4.png ；海滨地板(2001013):"+R+"Furniture/Prefabs/Floor/FurnitureFloor_Actv_Summer.prefab + icon "+FA+"icon_jiaju_summer_2.png ；主推 "+SEMIRA),
188: L("投放物三件套=海滨假日(门头1001009/地板2001013/墙纸3001010，现成) ✅ 无需新出",
     "【新图参考·投放物】门头door:"+R+"Furniture/Model/Furniture_Door_Wall_Column_Skin08/Texter/Furniture_Door_Skin08.png + icon "+FA+"icon_jiaju_summer_4.png",
     "地板floor:"+R+"Furniture/Prefabs/Floor/FurnitureFloor_Actv_Summer.prefab + icon "+FA+"icon_jiaju_summer_2.png"),
189: blk("礼包图/icon：海滨门头礼包($99.99)",
     "【尺寸】=拜访礼包图同尺寸 【格式】png",
     "包装稿:"+KB+"门头拜访礼包.png",
     "投放物·海滨门头door:"+R+"Furniture/Model/Furniture_Door_Wall_Column_Skin08/Texter/Furniture_Door_Skin08.png"),
211: blk("活动背景(仅换图，名字/玩法不变)：海洋许愿池——水底光柱+漂浮许愿币/贝壳/珍珠,青绿幽蓝",
     "【尺寸】=许愿池原活动背景同尺寸(取原替换) 【格式】png",
     "复用源:许愿池界面现有背景资源",
     "无独立投放物,沿用节日主视觉锚 "+SEMIRA),
234: blk("活动背景(仅换图，名字/玩法不变)：远航酒馆——海图+酒桶+船舵+舷窗外海洋,暖光",
     "【尺寸】=最佳酒馆原活动背景同尺寸(取原替换) 【格式】png",
     "包装稿:"+KB+"05_为爱干杯_最佳酒馆_10071702.png ；复用源:最佳酒馆界面现有背景资源",
     "无独立投放物,沿用节日主视觉锚 "+SEMIRA),
}
data=[{"range":f"'{TAB}'!C{r}","values":[[C[r]]]} for r in sorted(C)]
o=gws(['sheets','spreadsheets','values','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"valueInputOption":"RAW","data":data})
print("update:", 'OK cells='+str(json.loads(o).get('totalUpdatedCells')) if 'totalUpdatedCells' in o else o[:160])
