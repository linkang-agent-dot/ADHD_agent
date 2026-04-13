# 节日卡册道具配置 Skill

## 触发条件
当用户提到"卡册配置"、"卡包道具"、"item_card_asset"、"节日卡包"、"保底卡包"、"主题卡包"时使用。

---

## 使用方法（标准流程）

### S1 注册 gws 别名（首次使用时执行一次）
```bash
python gsheet_query.py alias set card_6001 1T-8EtaenFTybZzKqeRtLGWNRWlaxcPIMQScvUCTY1Dc
python gsheet_query.py alias set card_6002 1H1Epc0EccCDrxGpgZoIyGlpDh4WaDviOQX-r41rSvhE
python gsheet_query.py alias set card_6003 1TiKSm3Z6AnbclrxDS4w9O4b-Vmz6MPhQU4ll7A42z2Y
```

### S2 读取目标节日的 book（6001）
```bash
python gsheet_query.py row card_6001 {BOOK_ID}
# → 拿到 group_id 列表（通常8个）
```

### S3 读取所有 group（6002）
```bash
python gsheet_query.py idrange card_6002 {group_id_start} {group_id_end}
# → 拿到每组的 display_order、card_id 列表，以及 A_ARR_rewards
```

### S3.5 ⚠️ 核查 6002 每组 rewards 里的道具 ID（容易漏、曾经误判）
对 `A_ARR_rewards` 里**每一个** `id` 逐个执行：
```bash
python gsheet_query.py row 1111_P2 {item_id}
# → 看 S_STR_comment 和 A_MAP_lc_name，判断是否含上一个节日的名称
```
同时查 **6001 book 的 `A_ARR_rewards`**，做同样验证。
节日专属道具（皮肤、专属宝箱、专属头像框）**必须替换**；通用道具（加速、资源宝箱、增产特权）可保留。

### S4 ⚠️ 查 6003 确认每组的最高星级（不可跳过）
```bash
python gsheet_query.py idrange card_6003 {card_id_start} {card_id_end}
# → 看 col[2] A_INT_star，最大值决定 drop JSON 是否加5★ entry
```
**严禁**用 6002 rewards 字段推断5★——此方法已被验证不可靠（见 gotchas.md）。

### S5 读取 1111 表核验现有道具
```bash
python gsheet_query.py idrange 1111_P2 {id_start} {id_end}
# → 核验 drop JSON 的星级 entry 与 S4 结论是否一致
```

### S5.5 ⚠️ 检查 6004 集卡商店（容易漏）
```bash
python gsheet_query.py tail card_6004 10
# → 看 rows 60040026–60040030 的 goods_id 是否已指向本节日的保底卡包 ID
# → 每次换节日都要更新这5行，不更新会导致商店卖的还是上一个节日的卡包
```

### S6 理解 book 的8组结构，区分两类 group
每个节日的 book 固定包含 **8 个 group**：
- **低星组（3个）**：卡星级 1★–2★ 或 1★–3★，**不做专属主题卡包**，玩家通过全册保底自然获取
- **高星组（5个）**：卡星级含 3★+，其中 4 或 5 个有专属主题卡包

判断依据：看 6003 卡的 display_order，低星组范围 12x1–12x9（如 1201–1209），高星组从 12x4（1204）开始有主题卡包。

### S7 生成/修正配置行
参照 `references/cases/easter_fest_card_pack.md` 里的完整模板和 ID 映射生成 TSV 行。

---

## 节日对照速查

| 节日 | Book ID | 主题卡包起始 ID | 保底卡包段 | 自选卡包 |
|------|---------|--------------|----------|---------|
| 科技节 | 60011004 | 11119996–111110000 | 111110002–006 | 111110007 |
| 复活节 | 60011005 | 111110301–111110304 | 111110305–309 | 111111023 |

---

## 参考案例
- `references/cases/easter_fest_card_pack.md` — 复活节卡册道具配置（2026），含完整 ID 映射、8组结构、drop 模板、坑点
- `references/cases/easter_fest_localization.md` — 复活节卡册本地化配置（2026），含 Google Sheet 结构、Key 命名规则、整理版格式
- `references/gotchas.md` — 通用坑点汇总，持续追加
