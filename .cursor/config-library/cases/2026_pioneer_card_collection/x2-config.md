# X2 2026拓荒节 集卡册 配置记录

**完成日期**: 2026-05-21
**表系统**: X2（1108/1107/1123/1109 ≠ P2的6001-6004）

---

## SheetID 速查

| 表 | 名称 | SheetID | 写入 Tab | GID |
|----|------|---------|----------|-----|
| 1108 | CardGallaryBook | `1yeFJwufv9QZBOHAIifHTfzyYhG0Fy9SQcfDoGLrzir0` | CardGallaryGroup | 65753380 |
| 1107 | CardGallaryGroup | `1w-hmQGDu86TxrHGirvhQoaoniUjJA11t1XxCPDE5ylA` | CardGallaryGroup | 887412445 |
| 1123 | CardGallary | `1Dlg3r30Q7q19NKWcTHP-orYs7UYXs2TmV_V0xHGexMc` | CardGallary | 593941196 |
| 1109 | CardGallaryStore | `1zL0xNJwVQK95r71SDkIWEvZHp8ERFghkIsyyQ92HdZY` | CardGallaryStore | 0 |
| 1111 | item (X2) | `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs` | item | — |

---

## ID 分配

| 表 | 新ID | 行号（写入后）| 操作 |
|----|------|-------------|------|
| 1108 | 11081004（拓荒传奇） | 第10行 | 新增 |
| 1107 | 11074001–11074009（9组）| 第41–49行 | 新增 |
| 1123 | 11235001–11235086（54张，间隔10）| 第259–312行 | 新增 |
| 1109 | 11090031–11090033（3行）| 第17–19行 | 新增 |
| 1111 | 111111339/340/341 | 第2222–2224行 | 覆盖更新 |

---

## 1108 CardGallaryBook（11081004）

| 字段 | 值 |
|------|----|
| GroupID | [11074001–11074009] |
| DisplayKey | 1511094005 |
| DisplayKey1 | 1511094009 |
| DisplayKey2 | 1511094003 |
| DisplayKey3 | 1511094004 |
| FXDisplayKey | 1511020681（复用） |
| LcName | LC_EVENT_item_card_book_title_4 |
| CardPackID | [111111339,111111340,111111341] |
| Rewards | 111111327×1 + 11111082×10 + 11111083×20 |
| OpenReq | actvstart=21127381（拓荒节Gacha活动） |

---

## 1107 CardGallaryGroup（9组）

| ID | 组名 | 卡片ID范围 | DK | DisplayOrder | RewardsFirst |
|----|------|-----------|-----|-------------|--------------|
| 11074001 | 启程准备 | 11235001–006 | 1511094010 | 11071035 | 探测券×5+英雄经验×5 |
| 11074002 | 荒野行军 | 11235011–016 | 1511094011 | 11071036 | 探测券×5+英雄经验×5 |
| 11074003 | 扎营落脚 | 11235021–026 | 1511094012 | 11071037 | 探测券×5+英雄经验×5 |
| 11074004 | 矿脉勘探 | 11235031–036 | 1511094013 | 11071038 | 宝石×2+橙碎片×2 |
| 11074005 | 河谷淘金 | 11235041–046 | 1511094014 | 11071039 | 宝石×2+橙碎片×2 |
| 11074006 | 前哨筑城 | 11235051–056 | 1511094015 | 11071040 | 宝石×2+橙碎片×2 |
| 11074007 | 荒原猎踪 | 11235061–066 | 1511094016 | 11071041 | 宝石×3+橙碎片×3 |
| 11074008 | 地底秘境 | 11235071–076 | 1511094017 | 11071042 | 宝石×3+橙碎片×3 |
| 11074009 | 拓荒盛典 | 11235081–086 | 1511094018 | 11071043 | 橙碎片×3+头像框×1 |

- BG DK（共用）: 1511094019 / 1511094020
- RewardsFollow（全组）: 英雄经验(11116402)×5 + 食物资源(11144003)×30000

---

## 1123 CardGallary（54张）

| G | 星级分布 | 卡片ID范围 | 卡面DK范围 | LC Key范围 |
|---|---------|-----------|-----------|-----------|
| G1 启程准备 | 6×3★ | 11235001–006 | 1511094021–026 | _309–314 |
| G2 荒野行军 | 5×3★+1×4★ | 11235011–016 | 1511094027–032 | _315–320 |
| G3 扎营落脚 | 4×3★+2×4★ | 11235021–026 | 1511094033–038 | _321–326 |
| G4 矿脉勘探 | 3×3★+3×4★ | 11235031–036 | 1511094039–044 | _327–332 |
| G5 河谷淘金 | 2×3★+3×4★+1×5★ | 11235041–046 | 1511094045–050 | _333–338 |
| G6 前哨筑城 | 1×3★+4×4★+1×5★ | 11235051–056 | 1511094051–056 | _339–344 |
| G7 荒原猎踪 | 1×3★+3×4★+2×5★ | 11235061–066 | 1511094057–062 | _345–350 |
| G8 地底秘境 | 3×4★+3×5★ | 11235071–076 | 1511094063–068 | _351–356 |
| G9 拓荒盛典 | 3×4★+3×5★ | 11235081–086 | 1511094069–074 | _357–362 |

通用字段：
- Category: 11071001（固定，deprecated）
- DisplayKey1（卡背）: 1511094002（所有卡共用）
- LcDesc: LC_ASSET_card_gallary_desc
- FirstGotRewards: [{"typ":"vm","id":11151001,"val":5}]
- Honor/Recycle: 3★=100/1, 4★=200/2, 5★=400/10

---

## 1109 CardGallaryStore（3行）

| ID | 商品 | 价格(星尘) | 月限 | DO | RequirementPurchase |
|----|------|---------|------|-----|---------------------|
| 11090031 | 111111339 | 15 | 20 | 1011 | actvend+actvopencnt=21127381 |
| 11090032 | 111111340 | 30 | 15 | 1012 | 同上 |
| 11090033 | 111111341 | 150 | 10 | 1013 | 同上 |

---

## 1111 覆盖更新（3行）

| ID | 名称 | DK（更新） | LcName（更新） | category_param |
|----|------|-----------|--------------|----------------|
| 111111339 | 拓荒节2026-1-2星卡包 | 1511094006 | LC_EVENT_item_card_pack_name_15 | 3★:9000, 4★:1000; random_add=11081004 |
| 111111340 | 拓荒节2026-1-3星卡包 | 1511094007 | LC_EVENT_item_card_pack_name_16 | 3★:8000,4★:1300,5★:200; random_add=11081004 |
| 111111341 | 拓荒节2026-2-3星卡包 | 1511094008 | LC_EVENT_item_card_pack_name_17 | 4★:9500,5★:500; random_add=11081004 |

---

## 踩坑记录

### 1123 appendDimension vs insertDimension
- **问题**: insertDimension startIndex=258 失败（"must be less than grid size 258"）
- **原因**: grid size=258时，startIndex=258超出范围（0-indexed，末尾插入=等于gridsize）
- **修复**: 改用 appendDimension（length=54）追加行，再写入数据
- **结论**: 追加到表末尾时用 appendDimension，中间插入用 insertDimension

### 1108 tab 名误导
- 1108 书表的 tab 名是 "CardGallaryGroup"（非 Book），容易混淆
- 实际 SheetID 和数据内容正确，tab 名称是历史遗留命名问题

---

### 1011 gws.cmd 角括号传参失败

- **问题**: 传包含 `<color=#...>` 的 JSON body 给 gws.cmd 时，rc=1，报"系统找不到指定的文件"
- **原因**: gws.cmd 通过 CMD.EXE 执行，CMD 把 `<` 解析为 stdin 重定向符号，破坏 JSON 参数
- **修复**: 直接调用 Node.js 可执行文件绕过 CMD.EXE：
  ```python
  NODE = 'node'
  GWS_JS = r'C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js'
  cmd = [NODE, GWS_JS, 'sheets', 'spreadsheets', 'values', 'batchUpdate', '--params', params_str, '--json', body_str]
  ```
- **结论**: 凡是 JSON body 含 `<` 或 `>` 的写入（如 color tag、HTML），必须用 node+GWS_JS 代替 gws.cmd

---

## 1011 EVENT LC 写入记录

| 字段 | 值 |
|------|----|
| SheetID | `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg` |
| Tab | EVENT (GID: 550403607) |
| 写入行范围 | 7401–7470（70行）|
| ID_int 范围 | 1011087586–1011087655 |

| LC Key | ID_int | 内容 |
|--------|--------|------|
| item_card_book_title_4 | 1011087586 | 拓荒传奇 / Pioneer's Legend |
| item_card_collection_title_35–43 | 1011087587–595 | 启程准备…拓荒盛典 |
| item_card_name_309–362 | 1011087596–649 | 54张卡名 |
| item_card_pack_name_15–17 | 1011087650–652 | 卓越-史诗/卓越-传说/史诗-传说 卡包（拓荒）|
| item_card_pack_desc_15–17 | 1011087653–655 | 含 `<color=#...>` 色彩标签 |

备份 tab: `EVENT_backup_labor_lc`

---

## 待办

- [x] 1011 LC 翻译文案（54卡名 + 9组名 + 1册名 + 6卡包名/描述）✅ 2026-05-21
- [ ] DK 实际图片路径填入（美术上传CDN后）
