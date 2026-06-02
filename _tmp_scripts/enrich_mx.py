# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
KB="KB/产出-数值设计/X3_深海节/复用参考图/夏日/"
RES="client/Assets/Res/UI/Spirits/"
def L(*p): return "\n".join(p)
C={
34: L("转盘外观(DK_Turntable换皮·逐件)：金色埃及边框→锚链/珊瑚/贝壳质感；中心=航海罗盘/舵轮；指针=金锚；8格分区深蓝×青绿",
     "【尺寸】与尼罗大转盘同尺寸·逐件取原：格子icon=img_turntable_icon1~6 / 元素bg=img_ui_turntable_bg* 【格式】png",
     "【参考】包装稿:"+KB+"大转盘.png ；复用源资源:"+RES+"Activity/img_turntable_icon1~6.png + img_ui_turntable_bg2.png"),
35: L("转盘活动背景：海域俯瞰+航线虚线+远景沉船宝藏/珊瑚礁剪影+阳光光斑+气泡",
     "【尺寸】=尼罗大转盘背景 1080×1344(img_queen_bg_3) 【格式】png",
     "【参考】包装稿:"+KB+"大转盘.png ；复用源资源:"+RES+"ActivityImg_Download/img_queen_bg_3.png"),
36: L("🔧背景角色立绘：克利奥佩特拉→深海皮肤【待策划定:女海盗船长/美人鱼/深海女神】",
     "【尺寸】=尼罗立绘同尺寸(美术取原) 【格式】spine或png",
     "【参考】复用源:尼罗大转盘界面克利奥佩特拉立绘资源(同槽位)"),
37: L("传说铭牌图：锚+罗盘+浪花徽章(传说品质·金+深蓝)",
     "【尺寸】~752×192(头衔title标准) 【格式】png 【参考】复用源:现有title铭牌资源",
     "另:活动HUD icon —【尺寸】124×136 【格式】png"),
61: L("BP主界面背景：航海日志/海图桌——摊开海图卷轴+罗盘/望远镜/船舵/羽毛笔，暖光木质船舱",
     "【尺寸】=夏日BP背景同尺寸(美术取原资源) 【格式】png",
     "【参考】包装稿:"+KB+"02_为誓言而战_BP_102236.png ；复用源:夏日BP界面背景资源(ActivityImg)"),
62: L("史诗铭牌图：船舵+海浪徽章(史诗品质)",
     "【尺寸】~752×192(title标准) 【格式】png 【参考】复用源:现有title铭牌资源"),
84: L("每日礼包背景/弹窗：深海每日来信——漂流瓶里的信+珍珠/贝壳，浅蓝水面+光斑",
     "【尺寸】=夏日每日礼包弹窗同尺寸 【格式】png 【参考】包装稿:"+KB+"怦然心动.png"),
85: L("礼包展示视频（深海版·重制，非简单换皮）",
     "【时长】~15s(参考夏日录制节奏) 【格式】mp4 【风格】卡通奇幻·深蓝青绿+金光",
     "【分镜脚本】",
     "镜1(0-3s)：深海海面晨光，镜头由海面下潜入水；一只漂流瓶随波漂入画面中央",
     "镜2(3-7s)：瓶塞弹开，飘出卷着丝带的深海来信/卷轴，珍珠贝壳环绕、气泡光斑上浮",
     "镜3(7-12s)：信展开化作礼包，道具逐个飞出特写(养成材料/代币/抽奖券图标)，金光迸发",
     "镜4(12-15s)：道具收束为礼包icon + 标题『怦然心动·深海』浮现 + 『每日可领』角标，定格",
     "【参考】包装稿:"+KB+"怦然心动.png ；夏日原视频(节奏参考):"+KB+"录制_2026_05_27_17_46_46_144.mp4"),
108: L("通用礼包banner：深海主题(贝壳/珊瑚/锚边框装点，预留$9.99价格位)",
     "【尺寸】=礼包墙banner槽位(目标UI待程序定;同类礼包banner) 【格式】png 【参考】同礼包墙现有banner尺寸"),
109: L("深海头像框图：贝壳/珊瑚/锚链环绕框+珍珠点缀，深蓝金边",
     "【尺寸】256×256(AvatarFrame标准) 【格式】png 【参考】复用源:现有玩家头像框资源(AvatarFrame)"),
133: L("累充活动背景：海底宝藏窟——沉船金币堆+宝箱开启金光+鱼群环绕，金黄×深蓝",
     "【尺寸】=夏日累充背景同尺寸 【格式】png",
     "【参考】包装稿:"+KB+"07_花瓣与恩典_累充_100595.png ；复用源:夏日累充界面背景资源(ActivityImg)"),
134: L("行军皮肤=深海猎手(永久 Item15065，现成『暂无获取』) ✅ 无需新出",
     "【参考】现成资源(配置直接投放，美术0产出)"),
158: L("礼包banner：海滨沙滩度假——椰树+遮阳伞+沙滩+海浪+泳圈，暖橘×浅蓝(底部加水避免沙滩感)",
     "【尺寸】=装饰阶梯礼包banner同尺寸 【格式】png 【参考】包装稿:"+KB+"08_夏日装饰礼包_装饰阶梯_106101.png"),
159: L("装饰物=椰风遮阳椅(海滨假日 Item151043，现成) ✅ 无需新出",
     "【参考】现成 icon:"+RES+"Furniture/Actv/icon_jiaju_summer_3.png (DK_icon_jiaju_summer_3)"),
187: L("拜访活动背景：海滨酒馆门面——海风+门楣装饰+棕榈+海平面，暖橘×浅蓝",
     "【尺寸】=夏日拜访背景同尺寸 【格式】png",
     "【参考】包装稿:"+KB+"03_夏日柔情海湾_拜访礼包_105603.png + "+KB+"门头拜访礼包.png ；复用源:夏日拜访界面背景(ActivityImg)"),
188: L("门头三件套=复用海滨假日(横梁1001009/地板2001013/墙纸3001010，现成) ✅ 无需新出",
     "【参考】现成:client/Assets/Res/Furniture/Prefabs/Door/Skin08/Furniture_Door_Skin08.prefab"),
189: L("礼包图/icon：海滨门头礼包($99.99)",
     "【尺寸】=拜访礼包图同尺寸 【格式】png 【参考】"+KB+"门头拜访礼包.png"),
211: L("活动背景(仅换图，名字/玩法不变)：深海许愿池——水底光柱+漂浮许愿币/贝壳/珍珠，青绿幽蓝",
     "【尺寸】=许愿池原活动背景同尺寸(美术取原资源替换) 【格式】png 【参考】复用源:许愿池界面现有背景资源"),
234: L("活动背景(仅换图，名字/玩法不变)：远航酒馆——海图+酒桶+船舵+舷窗外深海，暖光",
     "【尺寸】=最佳酒馆原活动背景同尺寸(美术取原资源替换) 【格式】png",
     "【参考】包装稿:"+KB+"05_为爱干杯_最佳酒馆_10071702.png ；复用源:最佳酒馆界面现有背景资源"),
}
data=[{"range":f"'{TAB}'!C{r}","values":[[C[r]]]} for r in sorted(C)]
o=gws(['sheets','spreadsheets','values','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"valueInputOption":"RAW","data":data})
print("update:", 'OK cells='+str(json.loads(o).get('totalUpdatedCells')) if 'totalUpdatedCells' in o else o[:160])
