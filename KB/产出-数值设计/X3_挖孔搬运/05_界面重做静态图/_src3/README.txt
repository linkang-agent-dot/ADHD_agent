v3「X3 标准弹窗形态」老模块静态图 —— 出图源（可重跑）

跑法（在本目录，按序）：
  1) python gen3.py       # 生成 10 个 1080×1920 静态 HTML（内容沿用 v2，只换外壳）
  2) powershell -ExecutionPolicy Bypass -File shot3.ps1   # headless Chrome 1:1 截图 → png/
  3) python contact_v3.py # 拷 png/ 到上一级交付目录 + 出 _全屏对照_v3.png

辅助（沿用 v2 的解析工具，已随包拷进来）：
  python prefab_parse.py <prefab绝对路径>        # 全量节点树 + RectTransform 四要素 + sprite/切片
  python digest.py       <prefab绝对路径> [深度]  # 摘要（折叠重复兄弟，读这个更快）
  _guid_index.json 是 GUID→资源 缓存（扫 Assets/Res，约 24s / 33310 条）

v3 相对 v2 只改一件事：**界面外壳**。
  v2 把 9 个 panel 子面板画成了「独立整屏页」（自带标题+倒计时+规则钮的页头）——方向错。
  v3 = 挖孔活动主界面（透出） + 全屏 mask + X3 标准弹窗壳。

弹窗壳规格（本轮新解析的两个真弹窗，逐节点实测）：
  Activity/UIActvIdleReward.prefab   30 GO   Animation 1025.93×1213.01
  Activity/UIActvLuckyWheelProb.prefab 12 GO Animation 1025.93×1216.81
  两者结构完全一致：
    Mask(全屏 TFWImage)
    └ Animation 1025×1213
       ├ BG(stretch)  img_dz_bg_3  spriteBorder L240 B108 R240 T112（浅米不透明 rgb 249,233,193）
       │  └ BG 660×88 pos(0,-21) anchor 顶部居中  img_cm_biaoti
       ├ Title  h85  pos(0,-63.5)  fs46 #F7E497
       ├ btn_close 104×104 pos(-69,-67.4) anchor 右上  img_cm_zhizuo_guanbianniu
       └ Content 920.74×949.5 pos(0.74,-43.52)  bg img_cm_bg_ditu5 border 44
          （= 距壳顶 175 / 壳底留 88 给 CTA；壳内滚动用 LoopVerticalScrollRect）
  出图统一用用户量定的 img_cm_bg_tanchu（1022×458，border L240 B120 R240 T120，
  浅米不透明 rgb 247,228,187）当底板，与 img_dz_bg_3 视觉等价、九宫格可拉到任意高度。

注意：
- 九宫格：Unity spriteBorder{x左,y下,z右,w上} → CSS border-image-slice「上 右 下 左」。borders.json 里两种顺序都给了。
- assets/ = 从 _src2 整包拷来（P2 玩法图素来自 03_横转竖demo 只读；assets/x3/ 来自 x3-project 的 Spirits/ 只读拷贝，未碰 NewSprite/）。
  本轮新拷 1 个：img_dz_bg_3.png（真弹窗底板，留作对照）。
- 全程只读 03_横转竖demo\ 与 x3-project\，不写不改。
- 交付结论文档 = 上一级 _X3参照映射表.md（新增「零、界面类型裁决」一节）。
