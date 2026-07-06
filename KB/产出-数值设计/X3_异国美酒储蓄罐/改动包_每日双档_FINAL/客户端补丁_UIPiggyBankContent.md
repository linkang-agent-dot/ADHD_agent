---
tags: [kind/产出, domain/配置换皮, proj/X3, year/2026-07]
---

# 客户端改动 · UIPiggyBankContent 选档逻辑（每日双档 · 买完自动切下一档）

**文件**：`C:\x3-project\client\Assets\Scripts\UI\ItemObtain\UIPiggyBankContent.cs`
**目的**：储蓄罐卡显示「**第一个不在 CD 里的档**」，并在购买后自动重选 →「砸完档1(进CD) 自动切到档2，砸完档2(都进CD) 显示倒计时，次日 CD 到期自动回档1」。
**原理**：每档有自己的 24h CD（档1 Group 8 / 档2 Group 11），**CD 状态 = 该档本周期已砸过**，所以不用单独记购买次数，选档只看 CD 是否在走。
**服务端零改动**。仅改 2 处：

---

## 改动 1：购买后重新选档（让它自动切下一档）

`OnRefreshPackGiftUI`（约 line 63-66）

```csharp
// BEFORE
private void OnRefreshPackGiftUI(long packID)
{
    RefreshContent();
}

// AFTER
private void OnRefreshPackGiftUI(long packID)
{
    PrefixData();   // 重新选档：买完当前档进CD后，自动切到下一个不在CD的档
    RefreshContent();
}
```

## 改动 2：选档逻辑改成「第一个不在 CD 的档」

`PrefixData()` 内，替换原来「按 needCount 选档」那段（约 line 89-106）：

```csharp
// BEFORE（按"还差多少量"选档——本案不需要）
var haveCount = G.Player.GetMeta<StorageMeta>().GetItemNum(itemCfgID);
var needCount = Data.needCount - haveCount;
var index = -1;
for (var i = 0; i < mBankInfos.Count; i++)
{
    if (mBankInfos[i].num >= needCount)
    {
        index = i;
        break;
    }
}
if (index == -1)
{
    index = mBankInfos.Count - 1;
}
mIndex = index;

// AFTER（选第一个不在CD里的档；全在CD则停在第0档显示倒计时）
var giftMetaSel = G.Player.GetMeta<GiftMeta>();
var index = 0;
for (var i = 0; i < mBankInfos.Count; i++)
{
    var packID = CPiggyBank.I(mBankInfos[i].cfgID).PackID;
    var bt = giftMetaSel.GetGiftBuyingTime(packID);   // ColdTime==0 返回0；否则返回组/包的上次购买时间
    var ct = CPack.I(packID).ColdTime;
    var inCd = bt > 0 && bt + ct > GameTime.Time;
    if (!inCd) { index = i; break; }                  // 命中第一个可买(不在CD)的档
}
mIndex = index;
```

> `mBankInfos` 顺序 = PiggyBank 表内该 item 的档顺序（档1 行46 → 档2 行51），故 index 0=档1($9.99)、1=档2($19.99)，"第一个不在CD"天然先档1后档2。

---

## 行为验证（自测点）
| 状态 | 显示 | 可买 |
|---|---|---|
| 新的一天，两档都没砸 | 档1 $9.99 | ✅ |
| 砸完档1 | 自动切→档2 $19.99 | ✅ |
| 砸完档2 | 档1（显 24h CD 倒计时） | ❌(CD中) |
| 次日 CD 到期 | 自动回档1 $9.99 | ✅ |

> 左右箭头(mBtnLeft/Right)仍在(Count>1)，玩家也可手动滑看另一档——可保留；若产品要求"完全不出现下一档"，再隐藏箭头（另议，非必须）。

## ⚠️ 防刷说明
两档各自 24h CD（独立 Group），服务端原生 ColdTime 校验即拦，**无 ColdTime=0 穿透漏洞**，无需额外防刷逻辑。
