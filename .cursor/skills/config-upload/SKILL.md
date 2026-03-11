# 配置表上传工具

触发词：P2导表、传表、导表、上传配置、用户给数字编号+分支

## 执行顺序（5步）

**S1 确认分支**
```powershell
git -C C:\gdconfig branch --show-current
```
切换：`git -C C:\gdconfig checkout -q <branch>; git -C C:\gdconfig pull -q`

**S2 下载**

多个编号用**空格分隔**，一次性下载：

```powershell
# 单个表
echo "1`n1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"

# 多个表（空格分隔，一次下载）
echo "1`n1168 1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

> 用户输入如 `1168 1111`（空格分隔），直接拼成空格分隔的编号串一次传入。

**S3 读末尾8行确认** → 找 `成功: X, 失败: 0`
- `json error on row` → 报错行号+字段，用 `git diff <file> | Select-Object -First 150` 定位，给出修正建议
- `失败: X>0` → 报告错误

**S4 查看改动**
```powershell
git -C C:\gdconfig diff --stat; git -C C:\gdconfig diff
```
diff 极长时加 `| Select-Object -First 80`。摘要：提取 ID/名称，自然语言描述，不罗列 TSV。

**S5 提交推送**
```powershell
git -C C:\gdconfig add .; git -C C:\gdconfig commit -m "[配置更新]<页签>-<分支>-<五字>"; git -C C:\gdconfig pull -q --rebase; git -C C:\gdconfig push
```

---

## 编号→页签速查

| 编号 | 页签 |
|------|------|
| 1011 | cn（i18n 全语言）|
| 1111 | item |
| 1118 | building |
| 1120 | drop |
| 1168 | get_access_group |
| 1211 | buff |
| 1387 | city_effect |
| 1511 | display_key |
| 1920 | hero_data |
| 2011 | iap_config |
| 2111 | activity_calendar |
| 2112 | activity_config |
| 2115 | activity_task |
| 2116 | activity_item_exchange |
| 2118 | activity_rank_rewards |
| 2119 | activity_ui_template |
| 2120 | activity_ui_module |
| 2121 | activity_special |
| 2122 | activity_rank_rule |
| 2135 | activity_package |
| 2136 | activity_cycle_period |
| 2138 | activity_proto_module |
| 2141 | activity_without_gacha_pool |
| 2142 | activity_without_gacha_reward |
| 2160 | activity_metro_grade |
| 2169 | activity_hud_entry_style |

## 常用 SheetID（需查页签时用）

| 编号 | SheetID |
|------|---------|
| 1111 | 1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws |
| 1168 | 1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA |
| 2112 | 1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E |
| 2118 | 1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M |
| 2120 | 1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0 |
| 2121 | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc |

未知表查索引：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F300"}'
```

## 回复格式
```
✅ <编号>(<页签>) → <分支> 提交成功
commit: [配置更新]<页签>-<分支>-<五字>
📝 +X/-Y行：<摘要>
```
