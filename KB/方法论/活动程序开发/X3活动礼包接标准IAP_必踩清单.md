# X3 活动礼包接标准 IAP（gift 系统）必踩清单

> 来源：2026-08-04 马戏节限时抢购（ActvType=84）IAP 从「点了报『礼包不存在』」到全链跑通的实战。
> 适用：任何**活动内的礼包要走真金内购**（`GiftMeta.ReqBuyGift`）的场合 —— 活动货架、活动窗内档位、
> 阶梯档、活动直购包。**开工先按本清单逐条核，能省掉一整天的来回。**

---

## 0. 一句话结论

活动里的 IAP 包，**代码只是一半，另一半全在 `Pack` 表的四个字段上**：
`Price`（价格点）/ `PackType`（决定走哪条校验分支）/ `BuyCount`（限购）/ `Content`（内容 Reward）。
这四个任意一个空或配错，表现**都是同一句「礼包不存在」**，而且**请求根本不会发到服务端**
（客户端本地就拒了）⇒ 服务端日志里查不到任何 `BuyGiftReq`，极易误判成"协议没通/服务端没实现"。

**判据**：客户端日志 `FloatMsg=禮包不存在` 的调用栈里，回调直接来自 `GiftMeta.ReqBuyGift`（同步返回）
＝ 本地校验拒的，不是服务端拒的。错误码 `1010001 = ErrCodeGiftCfgNotFound`。

---

## 1. `Pack.PackType` 必须选"没有额外校验分支"的类型（本次头号坑）

`GiftMeta.CheckCanBuyGift` 尾部有个 `switch (cfg.PackType)`，**只有部分类型有 case**：

| 有 case（会加校验） | 无 case（走 default，直接放行） |
|---|---|
| `WEEKLY(4)` `RECOMMEND(1)` `VIP(2)` `DAILY(7)` `BATTLE_PASS(13)` **`CHAIN(11)`** `SELF_SELECT(19)` `PIGGY(21)` `GROWTH(6)` | **`ACTIVITY(16)`** `ACTV_WINDOW(30)` 等 |

- 🔴 **`PackType=11`（`PACK_TYPE_CHAIN` 链式/阶梯礼包）是最容易误配的**：chain 分支要求
  `giftInfo.ChainCfgID != 0 && giftInfo.extraInfo?.chainInfo != null`，而由
  `CreateActivityPack` 直建的 gift 这两项**都是空** ⇒ 直接 `ErrCodeGiftCfgNotFound`。
- ✅ **走 `CreateActivityPack` 建的包，标准取值是 `PackType = 16`（`PACK_TYPE_ACTIVITY`）**。
  实证依据：`ActvPack → CreateActivityProgressPack → CreateActivityPack` 这条同路径的包，
  **93 个全是 16**（只有 4 个三选一是 3）。
- `ACTV_WINDOW(30)` 也无 case，但它的语义是"靠 Trigger 链 + `TimeCycleID` 跟随活动窗口创建"
  （见 `GiftConst.TriggerPackTypes` 上方注释），**不是** `CreateActivityPack` 直建 ⇒ 别乱选。

**查法**：`grep -n "case GiftConst.PACK_TYPE" client/Assets/Scripts/Entity/Player/Gift/GiftMeta.cs`
→ 你的 PackType 在里面 = 要满足那条分支的全部前提；不在里面 = 放行。

## 2. `Pack.Price` 是 IAP 价格点，**活动自己表里的 Price 不算**

- 标准 gift 下单读的是 `CPack.I(packId).Price`（string，指向 `Pack__PackPrice.tsv` 的 `Id`）。
- 🪤 **换皮/搬运最容易漏**：活动自己的表（如 `ActvFlashSalePack.Price`）里配了价格点，
  看着"IAP 档位已配"，但**gift 系统压根不读它** ⇒ `CPack.Price` 空 ⇒ 下单失败。
  本次原始配置就是这样，从第一天起 IAP 就是断的、也从没测过。
- 价格点速查（`Pack__PackPrice.tsv`）：`105=$4.99 / 107=$9.99 / 111=$19.99 / 116=$49.99 / 115=$99.99`
  （⚠️ id 不随价格递增，别按 id 大小推金额）。
- 顺带：客户端展示价也读它（`CPack.Price` → `UIHelper.GetGiftFormattedPriceByPrice`），
  空则退化成「敬请期待」——**看到界面价格是「敬请期待」就是这一条没配**。

## 3. `Pack.BuyCount` = 限购次数；**每场重置要靠"换场重发 gift"**

- 限购闸：`GiftEx.GetLimitBuyCount() => CPack.I(cfgID)?.BuyCount ?? 0`，
  服务端在 `GiftMeta.cs` 用它拦 `purchaseNum`；超限报 `1010005「超過禮包購買次數限制」`。
- 空 = **无限购**（实测同一 giftId 可以连续买到爆）。
- 🔴 **`BuyCount` 是"该 gift 实例生命周期内"的次数，不是"每天/每场"**。
  要做「每场限购 N 次」只有一条路：**换场时移除旧 gift、以新 giftId 重建**，
  `purchaseNum` 自然归零（这就是 X2 `giftLimitNum` 的"每场重发"语义）。
  ```csharp
  // 换场判定处
  if (windowChanged) { /* 先收集再删，RemoveGift 会改索引 */ RemoveOldGifts(); }
  // 然后照常 CreateActivityPack(新 giftId, ...)
  ```
- ⚠️ **推论：giftId 每场都会变，客户端不能缓存 giftId**，必须每次从服务端下发数据里取。

## 4. 🔴 服务端在 `OnLogin`/`OnPostInit`/`OnReconnected` 里建 gift ⇒ 通知会被**静默吞掉**

`GiftMeta.CreateGift`（`GiftMeta.API.cs`）推 `NewGiftInfoNtf` 前有闸门：

```csharp
if (Player.CanSendMsgToClient()) { SendMsgToClient(new NewGiftInfoNtf { giftInfo = giftInfo }); }
```

登录回调期这个闸门是 **false** ⇒ Ntf 丢弃、**此后再无补推时机** ⇒ 客户端礼包列表里没有这批 gift
⇒ 点下去 `GetGiftCfg(giftId)` 返回 null ⇒ 「礼包不存在」。

- **X3 自己早记了这个坑**：`GiftMeta.cs` 里有注释「该方法在 meta 的 OnReconnected/OnLogin 回调里
  直发会被守卫挡下，故统一经 `ScheduleFlushPendingOfflineGiftEndows` **延后一帧**触发」。
- ✅ **两件事都要做**：
  1. 登录期的刷新**延后一帧**：`Timer.AddFrameTimer(1, cb)`（照抄上面那个范式）
  2. 再补一个**幂等全量补推**：把该活动名下现有 gift 全推一遍
     —— 只改时序不补推的话，**库里已有 gift 但历史上没送达的老号仍然是坏的**。
- **判据**：服务端日志 `grep -c "SendToClient\[<uid>\]->NewGiftInfoNtf"` ＝ 0 就是中招了。
  ⚠️ 别用 `'"ID":[0-9]*,"cfgID":<packId>'` 这种锚定 grep 找——JSON 里 `cfgID` 不紧跟 `ID`
  （中间有 startTime/endTime/purchaseNum），会误判成"没推"。

## 5. 🔴 反复出现的病：**逻辑写了但没接线**（本案一个搬运里踩了 3 次）

| # | 写好的东西 | 漏接的地方 | 表现 |
|---|---|---|---|
| 1 | `RefreshAllFlashSaleWindows` | 没挂进登录生命周期 | 登录打开界面＝**空货架**，零报错 |
| 2 | `CreateGift` 的 `NewGiftInfoNtf` | 时序不对被闸门吞 | IAP 点了报**「礼包不存在」** |
| 3 | `FlashSaleOnBuyGift`（买后活动侧记账） | **没挂进 `OnBuyGiftForGiftId` 派发器** | IAP 买完 `personalBought`/`globalRemain` 永不变 ⇒ 格子**不进售罄态、按钮不置灰**、单服限量不扣 |

✅ **收工前必做的机械审计**（30 秒，能挡掉整类问题）：
```bash
# 列出该功能 partial 里所有 public 方法 → 数全仓调用点，==0 就是孤立入口
grep -oE "public (void|ErrorCode|int|long|bool|[A-Za-z]+) ([A-Za-z]+)\(" <你的文件>.cs \
  | grep -oE "[A-Za-z]+\($" | tr -d '(' | sort -u | while read m; do
      n=$(grep -rho "\b$m\s*(" --include=*.cs <搜索根>/ | wc -l)
      echo "$m  调用点 $((n-1))"
  done
```
新增"买成功回调"这类东西时，**先去找该品类的集中派发器**（X3 是
`ActivityMeta.OnBuyGiftForGiftId`，由 `TEventType.OnBuyGiftForGiftId` 驱动），挂进去再写实现。

## 6. 配置源被删、导出产物还在 = 定时炸弹

本案实况：3 张活动表 + Pack/Reward/Item/AO/RuleTips 的相关行**在 tsv 源里全没了**，
client/server 一直靠**撤除前导出的旧 `.bytes`** 活着 —— 谁重新导一次表，活动整体消失。

- **判据**：本地 `Tools/table_exporter/ExportTable.py` 跑完，`temp_dev/ProtoGen/` 里**有没有该表的 bytes**。
  没有 = 源已经没了，现在能跑纯属产物残留。
- **同步 bytes 到本地服/客户端时只拷自己改的那张表**：客户端产物往往是旧日期的，
  整目录覆盖会把别人的 schema 变更一起怼进来（`InvalidProtocolBufferException`），
  更糟的是**会把只存在于旧产物里的行删掉**。
- 恢复要**手术式**：文件级 `git checkout <好版本> -- <不存在的新文件>`；行级从好版本
  **按字段名映射**后 append（⚠️ 表可能在**中间插过列**——本次 `ActvOnline` 插了
  `BaseActvID` 等 4 列把 `ExcludeActvIDs` 从 idx52 挤到 idx56，按列位置搬会整行串列）。
- **补引用要以 `ExportTable.py` 的 `depend_checks` 为准，不能靠扫表头的"引用表"行**：
  本次 `ActvFlashSale.AssistRewardIds` 那列 row2「引用表」是**空的**，扫表头会漏，
  只有 def schema 知道它引用 Reward ⇒ 导表报 `depend_keys: {8202101..04} not existed` 才暴露。
  做法＝跑导表 → 按它报的缺口补 → 再跑，直到 `EXIT=0`（本次迭代 3 轮）。

## 7. 自测 IAP：给个 `#if UNITY_EDITOR` static 入口，别靠人工点屏幕

DebugUtils 桥的 `invoke`/`eval` **不支持泛型方法**，而 IAP 必须
`G.Player.GetMeta<GiftMeta>().ReqBuyGift(...)` ⇒ 没有 static 入口就只能求人点。

```csharp
#if UNITY_EDITOR
    public static void EditorBuyFlashSaleGift(long giftId)
    {
        G.Player.GetMeta<GiftMeta>().ReqBuyGift(giftId, null, (e, m) =>
            D.I?.Error($"[FlashSaleEditorTest] buy giftId={giftId} errCode={e} msg='{m}'"));
    }
#endif
```
```bash
client.py invoke --type "UI.UIActvFlashSale" --member "EditorBuyFlashSaleGift" --kind call --args <giftId>
```
配合「进 Play → 自动登录 → 开界面 → 读 Editor.log」（见 [[X3客户端功能实机验证_DebugUtils桥]]），
**整个 IAP 回归可以无人值守跑**。⚠️ giftId 每场变，测前先从服务端日志取当前值。

---

## 验收判据（跑通的样子）

| 项 | 判据 |
|---|---|
| IAP 可买 | 客户端回调 `errCode=0`；服务端 `OnBuyGiftReq` → `BuyGiftAck errCode=0` |
| 活动侧记账 | 下发数据里 `globalRemain` 减 1、`personalBought` 加 1 |
| 限购 | 再买报 `1010005「超過禮包購買次數限制」` |
| 每场重置 | 换场日志出现"移除旧 gift 重建"，`giftId` 变新、`purchaseNum=0`，又能买一次 |
| 售罄表现 | `personalBought >= 限购数` ⇒ 购买钮置灰 + 「已售罄」（置灰用 `UIHelper.SetGray`，不用换 prefab 件）|
