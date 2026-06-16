# 世界杯竞猜活动配置 — 备份/待同步

> 2026-06-16 预生成。**未写入 live gdconfig**（等另一个 agent 干完 + 对阵抽签后再同步）。
> 生成器：`..\gen_wc_guess_activities.py`（改 PLAN/TIER 重跑覆盖）。

## 包含（6 个 _add.tsv 片段，追加用）
| 文件 | 内容 | ID 段 |
|---|---|---|
| ActvOnline_add.tsv | 56 竞猜活动(type64) | 102920-102975 |
| ActvPack_add.tsv | 56 活动礼包组 | 2920-2975 (=ContentID) |
| TimeCycle_add.tsv | 56 时间周期 | 2920-2975 |
| Pack_add.tsv | 112 礼包(每实例两队各一包) | 892001-892112 |
| Reward_add.tsv | 8 行=2 新奖励组 | 组291302($9.99)/291303($19.99)，行24700-24707 |
| Text_add.tsv | 6 标题 i18n key | TXT_WC_Guess_Title_{轮次} |

56 实例分布(对齐甘特图)：32强16×$4.99 / 16强8×($4.99+$9.99) / 8强4×三档 / 半决赛2×三档 / 季军1×三档 / 决赛1×三档。
奖励组：$4.99=**291101**(已存在live) / $9.99=291302 / $19.99=291303。

## ⚠️ 同步前必须填的占位
1. **队伍**（每个 Pack 的 Head/Icon/Name）：现为空（走 prefab 兜底）。对阵定后填：
   - Head(proto字段18)=队伍板 `DK_WC_TeamPanel_{三字码}`、Icon(20)=队徽 `DK_WC_Badge_{三字码}`、Name=队名 TextKey。
   - ⚠️ proto字段↔tsv列映射要现验(仿 DKVideo 坑)：填前对一个 Pack 实测确认 Head/Icon 落哪列。
2. **开球时间**：TC 现为相对窗口(TriggerType5,部署起算)；实际按比赛日由 **igame 部署时定**(不必改 TC)。
3. **球队款直发 vs 自选宝箱**（草案统一用了宝箱，按设计可细化）：
   - 设计原意：16强$9.99=球队款头像框直发 / 8强$19.99=球队款表情直发 / 半决赛$9.99=四强专属国旗框。
   - 草案为简化**全用自选宝箱(1148/1149)**。若要还原"球队款直发"，对阵定后把对应实例的奖励组换成"券+钻+VIP+该队框/表情道具(80300+/15700+段)"。

## 同步步骤（另一个 agent 完事 + 对阵出来后）
1. `git -C C:\x3\gdconfig fetch && reset --hard origin/dev_festival`，确认 ID 段(102920+/2920+/892001+/291302-303/24700+)仍空闲。
2. 填队伍(上面占位1) + 按需细化奖励组(占位3)。
3. 逐表 append _add.tsv 到 live tsv → `sync_xlsx_tsv.py --from-tsv --files <表>` → 全仓 `sync_xlsx_tsv.py` 验 mismatch=0/crlf=0。
4. commit(X3NEW-前缀) → push → `jolt_verify.py dev_festival` → **核对 build 是 dev_festival 分支**(别认 dev 别人的)。
5. igame 按赛程逐场部署(竞猜活动走部署,不占客户端封包)。

## 依赖(已就绪)
- 自选宝箱道具 1148/1149 + 池 291201/291202 + 48框道具80300-80347 + 48表情道具15700-15747 已在 live(导表#945 SUCCESS)。
- 入口图 DK_WC_ActvIcon / 真券1146 / 界面 ActvType64 已 live。
