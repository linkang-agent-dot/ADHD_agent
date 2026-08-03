---
name: project-x3-ticket-ladder-pack
description: 马戏团寻宝(103101)配套门票阶梯礼包活动 103102——ActvType=63 克隆配方+视频链路，已全链闭环(2026-07-27)
metadata: 
  node_type: memory
  type: project
  originSessionId: 205664c6-3f0f-472d-8d32-8b3a77e46e0b
  modified: 2026-07-27T09:12:51.375Z
---

# 马戏节·寻宝门票阶梯礼包活动（AO 103102「寻宝门票特惠」，2026-07-27 闭环）

**唯一入口**：`C:\x3-wt-flashsale\AIDocs\马戏节Gacha\拓荒节Gacha.html` §2.8（配置总览/数值/视频/与链式705分工全在）。母案=马戏团寻宝（ActvType 81，同文档）。

## 状态（全链已闭环）
- gdconfig dev_festival `8d3669aa`，本地 ExportTable 绿 + jolt **#2132 SUCCESS**
- 客户端 dev_festival：DK 双注册 `32cfd1b1513` + 视频 v2 `27133089486`（用户反馈返工：券面缩至~55%画宽+上移上1/3，810×1080/284KB）
- ✅**已绑定主活动（07-27 终版方案）**：`ActvGroupSchedule` 行 **10007**（103101 主→103102 子，StartTime=0/DurationType=2 同窗，照抄 10006 巡游→拼图）——**iGame 只部署 103101，103102 自动同窗开关**（机制=ServerActivityBasicMeta.CreateGroupActivityIds，继承圈服+ArkActivityId；三种绑定机制对比见 [[reference_x3_timecycle]]）。马戏节 TC 全 0，TC 绑定方案作废。
- ⏳ 待办：实机验收——①UITieredPack 三档+头图视频 ②**入口形态确认**：type63 Condition `GetActivityUIType()=null`，入口=商城 UIRecharge 链式页签（同深海装饰 106103），**不在活动列表**；ItemObtain 100510(Type5跳活动) 对无独立界面的 type63 跳转行为待实测，不通就改成 Type7 快捷购买或去掉。③图标/背景暂复用寻宝资产，美术要专属图再换。⚠️BaseActvID 不是绑定机制（服务端零消费，只作新旧版本迁移标记）

## ActvType=63 阶梯礼包克隆配方（新 agent 照抄）
1. **模板**=马戏庆典装饰 106104（谱系：深海 106103→ChainPack 700/706，CustomParameters=**4**=TIERED，UITieredPack 买后解锁下一档）。
2. ActvOnline：ContentID=ChainPackID=同一个 ChainPack id；TC=0；PlayerLv 6,99；ActvRule 15007（通用礼包规则文案，已 16 语）；GroupId=节日组；MailID 可空（63 型无邮件）。
3. ChainPack：PackList=档位 Pack ids；TimeCycle=6001（礼包-永久，生命周期由活动 GiftInfo 控）；**Video 可空=UITieredPack 自动隐藏 VideoRoot**（UITieredPack.cs:306）。**标题=首档 Pack 的 TXT_Pack_Name_<id>**（无 Text 行标题空白）。
4. Pack：PackType=11，BuyCount≥1（0=永久售罄 BUG），Price 填 PackPrice 档 id（111=$19.99）。
5. **收尾必检**：①节日累充白名单（ActvOnline field[49]）加新付费包 ②Item.ObtainID + ItemObtain(Type=5 跳活动) 补获取途径 ③Reward 多行组 DisplayOrder(col14)=行id 组内唯一 ④Text 别名 key 手法：`TXT_ActvOnline_ActvName_X|TXT_ItemObtain_ObtainName_Y` 一行喂两 key。

## 外显加投（07-27 用户三轮拍板·终版）
- **数值终版**：档1=门票×4($20) / 档2=门票×4+**欢庆之环80116(专属)** / 档3=门票×4+史诗书×5+**专属表情[喝彩]**。档2 材料票已删（用户终调）。
- **欢庆之环改为档2 专属（用户拍板"BP 就不投放头像框了"）**：框原位=BP 巡游通行证**至尊轨 Lv2**（组 4037302，⚠️不是满级档）；撤框 `2feacd48` 后该级已按用户拍板**补罗盘×5 对齐邻级**（罗盘×10，`577fb22d`+jolt#2147 绿）。Reward 81321 框行重排 8132102。BP 三轨总量：免费=罗盘20+钻500+杂 / 高级=罗盘35+传奇书10+阅历10万 / 至尊=钻15000+罗盘165。**新做的寻宝之环转备用未投放**：FrameCfg 10094+Item 80360+Text 已在库（jolt #2141 绿）、美术=KB 案子目录 `Img_Player_AvatarFrame_circus_treasure.png`（几何达标 155/246/46），要加专属框直接改 Reward 8132103 指回 80360+客户端补 DK 即可。Reward 换投 commit `8baee56f`。
- **档3 +专属表情[喝彩]✅全落地**：Emoticons 250（ShowType=1）+Item 15476；GIF=视频→切帧正路（seedance 杂耍绿幕 4.79s 天然循环 seam2.3/58帧/644KB，用户选完整版弃 0.8s 循环段）；客户端 `30b9b082270`（gif/.bytes/icon+Path/Display 双DK）。⚠️Gif .bytes 运行时资源，dev 实测需重建 AB。⚠️x3-project 本地 stash `wip-local2` 里有存钱罐案 prefab/cs 的旧 WIP（与已提交版冲突按 HEAD 解，原件在 stash 未丢，存钱罐接手人要用自取）。

## 数值决策（为什么这么配）
- 3 档均 $19.99：券×4 / 券×4+材料票×50 / 券×4+史诗书×5（ROI 100/125/138%）。**券严格 $5/张不打折**→不动 v6「$384.93 稳态拿皮肤」盘子，只加中 R 平价触达位；赠品用寻宝家族词汇（材料票/史诗书），阶梯递增当爬档动力。与链式 705（大 R 主通道、顶档无限购）分工不冲突。

## 视频链路（教训已固化）
- **UI 氛围循环视频=kling fflf**（vidu 首尾差 49.3 淘汰，kling 1.77）；路由+审查流程=`~\.claude\skills\x3-media\references\video-model-routing.md`（SKILL.md 已挂强制条款）。产物目录说明见 KB `产出-本地化与美术\X3\马戏节\寻宝门票阶梯礼包\_目录说明.md`。
- 链路：gpt 首帧合成（icon 直喂会稀疏，先出构图完整首帧）→ kling 同图双喂锁循环 → 工程 compress_video.py 落库（过 video_policy 钩子）→ Display+Path 双注册（锚点平行插入，keys 排序 OrdinalIgnoreCase）。

相关：[[reference_x3_pack_open_mechanisms]]（链式 5 种界面模式）· [[reference_x3_reward_table_rules]]（DisplayOrder 坑）· [[reference_x3_client_resources]]（DK 双注册）
