v2「对齐 X3 现成 prefab」老模块静态图 —— 出图源（可重跑）

跑法（在本目录，按序）：
  1) python prefab_parse.py <prefab绝对路径>       # 解析任意 X3 prefab：节点树 + RectTransform 四要素 + sprite/切片
     python digest.py       <prefab绝对路径> [深度] # 同上，折叠重复兄弟 + 只留有视觉意义的节点（读这个更快）
     首次跑会建 _guid_index.json（扫 Assets/Res 的 *.meta + 各目录 *.cs.meta，约 24s / 33310 条），之后直接命中缓存
  2) python fetch_sprites.py     # 从 x3-project 只读拷 119 张官方 sprite → assets/x3/，并导出 borders.json（Unity LBRT + CSS TRBL）
  3) python gen2.py              # 生成 9 个 1080×1920 静态 HTML
  4) powershell -ExecutionPolicy Bypass -File shot2.ps1   # headless Chrome 1:1 截图 → png/
  5) python contact_v2.py        # 拷 png/ 到上一级交付目录 + 出 _全屏对照_v2.png

已解析并留档的 prefab dump：
  dump/*.txt  全量（含所有节点、组件、覆盖值）
  dig/*.txt   摘要（折叠重复兄弟，深度可控）
  覆盖：UIActvExchange / UIExchangeUnit / UiActivityCommonRules / UIActvPreview / UIActvSchedulePack /
        UIActvDailyRank / UIActvVisitPack / UIActvCumRecharge / UIActvBattlePassScore / UIActvBattlePassFund /
        UIPiggyBankContent / UICoinPiggyBankTips / UIPackCommonPop
  另外临时解析过（未落 dump，需要时重跑 digest.py）：
        Recharge/UIMultiTierPack、Package/UIStepChainPack、Idle/UIIdleIncome、Public/UIRankTemplate、
        Public/UIItemTemplate、Public/UITitle、Button/UIBtnPurchase、Button/UIBtnGift、
        Activity/DailyGift、Activity/GotoDetails、Activity/StageTabs、Activity/ActvRank、
        Common/PanelNew/BottomPublicBtnEmpty

注意：
- 九宫格：Unity spriteBorder{x左,y下,z右,w上} → CSS border-image-slice「上 右 下 左」。borders.json 里两种顺序都给了。
- assets/ 里 P2 玩法图素与宝物 DK 图是从 03_横转竖demo（只读）抽的；assets/x3/ 是从 x3-project 的 Spirits/ 只读拷的（未碰 NewSprite/）。
- 全程只读 03_横转竖demo\ 与 x3-project\，不写不改。
- 交付结论文档 = 上一级 _X3参照映射表.md。
