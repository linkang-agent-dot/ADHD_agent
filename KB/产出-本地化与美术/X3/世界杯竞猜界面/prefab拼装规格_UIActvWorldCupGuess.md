---
tags: [kind/产出, domain/美术媒体, proj/X3, fest/世界杯, year/2026]
---

# UIActvWorldCupGuess prefab 拼装规格（2026-06-11）

代码侧已全部就位（分支 `dev_festival`），**Unity 里照本规格拼 prefab 即可跑通**。
节点路径必须与 `Auto_UIActvWorldCupGuess.cs` 的 FindByFullPath 严格一致（大小写敏感）。

## 已落仓的东西

| 文件 | 说明 |
|---|---|
| `Assets\Scripts\UI\Actv\UIActvWorldCupGuess.cs` | 业务类（互斥购买/队伍填充/倒计时） |
| `Assets\Scripts\UI\Gen\Auto_UIActvWorldCupGuess.cs` | 手写的绑定文件（后续用 UI 生成器重新生成会覆盖，无碍） |
| `Assets\Scripts\Entity\Player\Activity\ActivityMeta.cs` | GetActivityUIType 加了分流：ActvType=29 且 ContentID∈[2911,2998] → 本界面 |
| `Assets\Res\UI\Spirits\ActvWorldCup\WC_Guess_*.png` | F 固定层 8 张，meta 已设 Sprite + 九宫格 border 初值（短边/3，Sprite Editor 里目视微调） |

## 复用底板

新建 prefab 最快路径：复制 `Assets\Res\UI\Prefab\Activity\UIActvSchedulePack.prefab` 改名
`UIActvWorldCupGuess.prefab`（同目录），保留 Root/Bg、Root/Animation/Top 骨架，重排 Content 区。

## 节点树（路径 = 代码绑定，不能改名）

```
UIActvWorldCupGuess
└── Root
    ├── Bg                       TFWImage   ← WC_Guess_Bg 体育场夜景（已落仓）
    └── Animation
        ├── Top                  （保持模板原样：标题板已砍、倒计时用通用件，本区零新图）
        │   ├── txt_title        TFWText    活动名（SetActivityBaseInfo 自动填）
        │   ├── txt_desc         TFWText    副标题/场次说明
        │   ├── Info             空GO+按钮区 规则按钮（点击=规则弹窗，已绑）
        │   └── Time             GO         模板自带通用件（img_gift_bg_4+img_gift_time），不换图
        │       └── txt          TFWText    倒计时（代码自动驱动）
        ├── Match
        │   ├── Vs               Image      WC_Guess_VS，200×200
        │   ├── TeamL
        │   │   ├── Banner       TFWImage   队伍横幅 480×320 ← 运行时按 Pack.Head DK 填
        │   │   ├── Badge        TFWImage   队徽 256×256 ← Pack.Icon DK
        │   │   └── txt_name     TFWText    队名 ← Pack.Name TextKey
        │   └── TeamR            （与 TeamL 同构）
        └── Packs
            ├── ColumnL                     礼包柱 500×900，底图 WC_Guess_PackPanel 九宫格
            │   ├── RewardList   GO         必得内容物区（结构见下）
            │   ├── BonusTips    TFWText    猜对加送行 ← Pack.Desc
            │   ├── UIBtnPurchase GO        价格按钮（结构见下），380×96
            │   └── txt_state    TFWText    已助威/已锁定 文案（默认隐藏）
            ├── ColumnR          （与 ColumnL 同构）
            └── LockTips         GO         1020×96，底图 WC_Guess_LockBar 九宫格
                └── txt          TFWText    锁定提示文案（代码驱动三态）
```

### RewardList 内部结构（ItemUnitHelper.RefreshLoopReward 的硬要求）

子层级里必须有一个 **LoopScrollRect**（横向 LoopHorizontalScrollRect 即可）+ 其下任意层级一个
**ItemUnitView** 模板（直接拖 `Assets\Res\UI\Prefab\Common\Item\ItemSmall.prefab` 进
Content 当模板，参考 UIActvVisitPack 的 PackRewardList 节点抄结构最快）。

### UIBtnPurchase 节点

直接从 `UIActvSchedulePack.prefab` 里把 UIBtnPurchase 节点整个复制过来（内含价格按钮
prefab 引用），代码 `WidgetContainer.AddSingle<UIBtnPurchase>` 已接好。

## 拼完之后

1. 保存 prefab（如跑 UI 生成器重新生成绑定，会覆盖手写 Auto 文件——生成器分配的 ID 与手写
   不同没关系，以生成器为准）。
2. 编译通过后，配一条测试活动即可在活动中心看到界面（见下）。

## 联调用最小配置（dev 环境）

| 表 | 配法 |
|---|---|
| ActvOnline | ActvType=29，ContentID=2911，TimeController 正常配 |
| ActvPack | ID=2911，PackList 填 2 个礼包 ID，FinalReward 可空 |
| Pack ×2 | BuyCount=1；Name=队名 TextKey；Head=队伍横幅 DK；Icon=队徽 DK；Desc=加送文案 TextKey；Content=必得奖励 RewardID；Price 走 IAP |

⚠️ 服务端 type 29 现状：建包 day=序号（0/1），但**购买路径不校验 day**，所以两个包第一天都
能买；day 锁只是 UI 语义，本界面已绕开（直接查 purchaseNum）。服务端零改动可联调。

## 待办（不阻塞拼 prefab）

- [ ] T 队伍层素材（横幅 32 + 队徽 32）→ DK 注册 → 填进 Pack.Head/Icon
- [ ] B1 背景大图（另批生产）
- [ ] 本地化 key 入表：`Text_WC_Guess_Lock_Tip` / `Text_WC_Guess_Picked`({0}=队名) /
      `Text_WC_Guess_Bought` / `Text_WC_Guess_Locked`（走 x3-translation-automatic）
- [x] ~~焦点战多档扩展~~ 不需要：策划案 v0.25 定稿多档=同场多个独立活动实例（每档一个实例、单档界面），本框架一实例两包正好；高档实例换 B 背景包装即可
- [ ] 服务端后续（可选）：跨包互斥的硬校验；竞猜结算仍走运营 SOP 零后端
