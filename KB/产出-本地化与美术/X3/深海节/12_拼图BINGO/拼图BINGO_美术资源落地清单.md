---
tags: [kind/产出, domain/美术媒体, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 拼图(BINGO) 美术资源落地清单

> 2026-06-23 建。X3 的 **BINGO = 拼图 ActvPuzzle**（5×5 格子，奖励分 `Type1=行 / 2=列 / 3=最终`，连成行列给奖＝连线 BINGO）。**ActvType=18，纯换皮，无需程序**（节日已换 27 版 1801-1827）。
> 深海版**之前没配过**（最新到 1827 春节）。本清单 = 深海拼图换皮所需美术资源 + 落地链路，参考春节 1827 / 尼罗 1825 范式。

## 玩法落地 = 4 配置表 + DK 美术
| 表 | 作用 | 深海新 ID(待建) | 克隆源(1827春节) |
|---|---|---|---|
| `ActvPuzzle__ActvPuzzle` | 主表(拼图图/格子数/各 DK) | **1828** | 1827 |
| `ActvPuzzle__ActvPuzzleReward` | 阶段奖(行/列/最终) | 组**1028**(11行) | 组1027 |
| `Reward__Reward` | 最终奖内容 | 新组(发纪念卡) | 603935(春节最终=纪念卡180078+信物+钻) |
| `ActvOnline__ActvOnline` | 活动壳(icon/bg/入口) | **101828** / CID1828 / 组**140**(深海入口) | 101827 |
| `Reward__Reward` 行列奖 | 行/列连线奖 | 复用 **603934**(万能信物×5) 或克隆 | 603934 |
| `ActvPuzzleTask` | 格子任务 | **复用组109**(通用，1810-1827 都用它) | 109 |

★**最终奖励 = 纪念卡**（这是拼图的招牌：尼罗拼图→尼罗回响卡 / 情人节→我对你的誓言 / 春节→新春特辑180078）。**深海拼图最终奖 = 纪念卡 180080「远航之歌」**（本轮已配，正好闭环）。

## 美术资源清单（深海拼图换皮所需）
> 全部落到 `client/Assets/Res/UI/Spirits/ActivityImg/`，命名 `img_Activity_deepsea_*.png`，注册 `client/Assets/Res/Config/DisplayKey/Path_Activity.asset`（双列表：m_Keys + key/objPath 对，插同类后）。**尺寸对齐复用源春节 1827 同名图**（换皮跟源对齐，见 [[reference_x3_art_resource_spec]]）。

| # | 用途 | 配置字段 | 春节1827 复用源 DK | 建议深海 DK 名 | 状态 |
|---|---|---|---|---|---|
| 1 | **拼图封面**(被拼合的整图·切5×5) | ActvPuzzle.col3 PuzzleImg | DK_img_Activity_CNY_bg_7 / 航海navigation_bg_9 | DK_img_Activity_deepsea_puzzle | ⬜待出·**800×800方形RGB不透明·角色场景插画**(春节=双角色+灯笼/航海=美人鱼+贝壳+宝藏)·深海建议=霍普金斯或美人鱼+深海珊瑚宝藏·可restyle航海这张(海主题最近)。航海封面在`Spirits/ActvVoyage/`·节日封面在`Spirits/ActivityImg/` |
| 2 | 格子图标(单格底) | ActvPuzzle.col7 DK_bg1 | DK_img_Activity_CNY_bg_9 | DK_img_Activity_deepsea_puzzle_grid | ⬜待出 |
| 3 | 背景框 | ActvPuzzle.col8 DK_bg2 | DK_img_Activity_CNY_bg_8 | DK_img_Activity_deepsea_puzzle_frame | ⬜待出 |
| 4 | 活动背景图 | ActvOnline.col22 ActvImg | DK_img_Activity_CNY_bg_6 | DK_img_Activity_deepsea_puzzle_bg | ⬜待出(可复用深海大富翁/转盘 bg) |
| 5 | 活动 HUD 图标 | ActvOnline.col21 ActvIcon | DK_img_Activity_CNY_icon_4 | DK_img_Activity_deepsea_puzzle_icon | ⬜待出(124×136) |

> 注：col9 拼图名底图 / col10 奖励底图 春节1827 为空（不填则隐藏），深海可同样留空。

## 入库链路（参考之前·跟纪念卡/头像框 DK 同法）
1. 美术出图(透明/对齐源尺寸) → 落 KB `KB\产出-本地化与美术\X3\深海节\12_拼图BINGO\`。
2. 拷 png → `client/Assets/Res/UI/Spirits/ActivityImg/img_Activity_deepsea_puzzle*.png` + .meta(克隆同类改 guid)。
3. 注册 `Path_Activity.asset`：m_Keys 列表 + key/objPath 对，**两处都加**（插 DK_img_Activity_CNY_* 同类后）。Path-only(活动图走 Path_Activity)。
4. 配置侧 4 表填上这些 DK 名 → 本地 ExportTable 验证 → push。

## ★封面已出候选(2026-06-23·GRFal gpt·待用户挑定)
- **深海拼图封面 4 候选**(本目录 `深海拼图封面_puzzle_cover_{A|B}_cand{0|1}.png`):用霍普金斯纪念卡 big(A)/big_v2(B)当参考·800×800方形满幅·深海宝藏场景(珊瑚/珍珠/巨贝/沉船/金币/海豚)·保霍普金斯身份。推荐 B_cand0(居中均衡)或 A_cand1。
- **世界杯拼图封面 2 候选**(备用·`KB\产出-本地化与美术\X3\世界杯拼图BINGO\世界杯拼图封面_绿茵之星_cand{0|1}.png`):绿茵之星·球场+大力神杯+足球。推荐 cand0(满幅)。
- **英雄源图(霍普金斯=Role 34 skin01 海风旅者)**:`client\Assets\Res\UI\Spirits\Role\FullLength\FullLength_IOS\Role_F_ios_34_skin.png`(全身)·头像`Character Portraits\Img_C_H_34_Skin01.png`。
- **生成 prompt 范式(拼图封面·可复用)**:"deep sea themed SQUARE key visual for jigsaw puzzle, feature character from reference (preserve face/hair/outfit/3D-cartoon look), deep-sea treasure scene(coral/pearls/clam/sunken gold/light rays), FULL-FRAME square edge-to-edge (cut into 5×5 grid), NO transparency/UI/text, 1:1"。★拼图封面=**不透明满幅**(≠banner的透明渐隐)·gpt+参考图·脚本 `scratchpad/gen_puzzle_cover.py`(submit-only+轮询·GRFal见[[workflow_x3_grfal_generate_image]])。
- HUD icon(124×136 RGBA)=**拼图块+节日纹饰**(春节=金拼图块+中国结)→深海版=拼图块+珊瑚/浪花/贝壳·待出(封面定后)。

## 落地顺序
确认 Bingo=拼图 + 最终奖=纪念卡180080 → 美术出 5 图(封面/格子/背景框/活动bg/icon·或复用深海现有bg) → DK 入库 Path_Activity → 配置 1828/1028/最终Reward/101828(组140) + i18n(拼图名/描述) → 本地导表 → push。

## 关键决策记录(为什么)
- **BINGO=拼图 ActvPuzzle**：X3 无独立 Bingo 表，拼图的 Reward Type 行/列/最终 = 连线 BINGO 机制；ActvType18 标准可换皮，无需程序。
- **最终奖=纪念卡180080**：拼图招牌玩法=拼满得节日纪念卡，深海接本轮已配的 180080 远航之歌。
- **任务组复用 109**：1810-1827 拼图都共用 TaskGroup 109(通用填格任务)，深海复用，不新建。
- **行列奖复用 603934**：万能信物×5，跨节日通用，深海可直接复用(只最终奖需克隆专属发纪念卡)。
