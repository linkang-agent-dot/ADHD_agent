---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海 · 怦然心动（进度礼包 ActvType29）— 配置备份表 / staging

> 2026-06-24 建。**方向 A**：克隆一个深海专属进度礼包活动（不动旧的新手/兔女郎包 102901）。
> worktree：`C:\x3\gdconfig-pengran`，分支 `X3NEW-deepsea-pengran`（基于 dev_festival）。**待用户验收后合 dev_festival**。

## 一、最终数值（用户拍板 2026-06-24）

- **价格**：5 档**全 $4.99**（价格档 105），**每档内容完全相同**。
- **ROI = 10**（口径：产出钻 ÷ 实付钻，对齐航海/尼罗/春节）。实付 $4.99 = 2,495 钻（500钻=$1）。
- **价值口径**：深海罗盘=2,000钻/个（抽奖产出值）· 深海藏宝图=125钻（$0.25/张·尼罗=世界杯券价）· 钻石=1钻 · **VIP点数=固定 bonus 不计入 ROI**。

| 内容 | item | 数量/档 | 计ROI钻值 |
|---|---|---|---|
| 深海罗盘（探索券·复用旧道具） | **1057** 航海罗盘 | 10 | 20,000 |
| 深海藏宝图（转盘券） | **1200** | 20 | 2,500 |
| 钻石（固定·不动） | **1002** | 2,500 | 2,500 |
| VIP点数（固定 bonus·不计ROI·不动） | **2022** | 25（=2,500 VIP点数） | — |
| **计** | | | **25,000钻 → ROI 10.0** |

- **买全部送**：深海藏宝图(1200) × **100**（=5×每档20）。

## 二、配置改动（已落 worktree tsv·6 张表）

| 表 | 新增 | 说明 |
|---|---|---|
| `ActvOnline__ActvOnline` | **102993** | 克隆 102901；ContentID=3002；ActvType=29；**TimeController=160006**（⚠️TC=0 被 ExportTable 拒：ActvType29 不在 SKIP_TIMECYCLE 豁免名单，只有竞猜64豁免 → 必须给真 TimeCycle）；ActvImg=`DK_img_Activity_deepsea_schedule_bg`（藏宝图弹窗背景·**待客户端DK入库**）；ActvPrefab 清空（深海无角色）；ActvIcon 暂沿用通用 `DK_img_Activity_icon_schedule`（HUD图标待出） |
| `ActvPack__ActvPack` | ContentID **3002** | packs=800005\|...\|800009；最终奖励组(col2)=**40600** |
| `Pack__Pack` | **800005–800009** | 克隆 800000；Price档=105($4.99)；Content(col14)=**40500**（5档共用·引用Reward的col2组号）；名=深海进度礼包-dayN |
| `Reward__Reward` | 内容组(col2)**40500**(4行) + 最终组(col2)**40600**(1行) | 40500={1057×10,1200×20,1002×2500,2022×25}；40600={1200×100} |

> ⚠️**Reward表结构铁律（本次踩坑）**：**col1=唯一行id（"仅保证不重复"）、col2=掉落包/组id（"相同ID为同一个掉落包"）**。Pack.Content / ActvPack.最终奖励 **引用的是 col2(组号)**，不是 col1！多道具=多行同col2、各行col1唯一。导表 RewardData 的 DictWriter 按 col1 查重，col1 重复即报 `重复主键 ID`。本次 col1 用 15904033–037（唯一行id），col2 用 40500/40600（组号·查 col2 空位非 col1）。
| `TimeCycle` | **160100** | 克隆 2901（TriggerType=5 触发式·Duration 7天）；深海怦然心动。⚠️**原用160006与dev分支撞车→改160100(dev/dev_festival两边都空)**。⚠️**TC不能=0**：ActvType29在GIFT_TRIGGER_ACTIVITY_TYPES={29}里,导表强制要求有TimeCycle且TriggerType=5(PostProcessData.py:1742),TC=0直接FAILURE |
| `i18n/Text__Text` | TXT_ActvOnline_ActvName/Desc_102993 + TXT_Pack_Name_800005–009 | zh+en 已填，**其余语言待 i18n**（跑 x3-translation-automatic） |

## 三、验证状态

- ✅ **本地 ExportTable 通过（2026-06-24）**：`protoc 编译成功 + generate localization bytes success + MD5`，零 Exception。配置合法（depend_checks / ActvType29 TimeCycle / Reward 主键 全过）。
- ⏳ worktree `X3NEW-deepsea-pengran` 改动**未提交、未合 dev_festival**——等用户验收。

### 踩坑记录（3 个导表坑，已解）
1. **TC=0 不行**：ActvType29 进度礼包不在 SKIP_TIMECYCLE 豁免（只竞猜64豁免）→ 必须真 TimeCycle（建 160006·触发式7天）。
2. **Reward col0/col1 写反**：col0=seq唯一行号、col1=RewardID组号，Pack/ActvPack 引用 col1(组)。多道具=多行同col1、col0各唯一连续。详见 [[reference_x3_reward_table_rules]]（早有记载·建表前该先读）。
3. **组号查空要查 col1(RewardID) 维度**：16317/40501 在 RewardID 维度已占用 → 用真空段 40500(内容)/40600(最终)。

## 四、落地状态（2026-06-24 已验收·全干）

- ✅ **gdconfig 合 dev_festival + push**（commit 8909c63，含配置 0eb2d27 + i18n）。
- ✅ **i18n 16 语言补全**（ActvName/Desc/5档Pack名；名克隆102901/800000-004，desc新译；脚本 `scratchpad/fill_i18n_pengran.py`）。
- ✅ **客户端藏宝图背景 DK 入库**（commit 9cdf76f）：`img_Activity_deepsea_schedule_bg`（**540×960**·从 3:4 藏宝图_选定 居中裁切适配 schedule 槽位）+ Display_Activity/Path_Activity 双补。
- ✅ **jolt 导表 SUCCESS**（构建 #1233·dev_festival·Finished: SUCCESS）。worktree 已清理。
- ⚠️ **HUD 图标**（ActvIcon）仍沿用通用 `DK_img_Activity_icon_schedule`（深海专属 HUD 图待出）。
- 注：bg 原 3:4 藏宝图艺术图居中裁成 540×960（槽位尺寸），左右房间边缘略裁、爱心窗+藏宝图+珊瑚珍珠保留。若要更贴合可后续出 9:16 原生版。

## 四、构建脚本

`scratchpad/build_pengran.py`（克隆源行 + 改 6 表；TC fixup 见对话）。
