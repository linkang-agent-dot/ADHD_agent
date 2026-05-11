# 机甲主题皮肤配置运维文档

**案例**：巨象蒸汽霸主  
**完成日期**：2026-04-17  
**配套工具**：`config-output.html`（同目录）

---

## 一、涉及表总览

| 表号 | tab 名 | SheetID | 新增行数 |
|------|--------|---------|---------|
| 1111 | item | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` | 1 |
| 4010 | mecha_skin | `1KWNZXyhUlI4UyREfENWe7yZvHSxWgpEtMv5T10G2X7w` | 1 |
| 4011 | mache_colour（注意拼写）| `1nl7w3Vfm1Wgv2ih5xKcPdLaIwfxv-ArWztVUSBlPnKY` | 1 |

> ⚠️ 4011 的 tab 名是 **`mache_colour`**（mache 非 mecha），查表时注意。

---

## 二、ID 编排规则

| 类型 | ID 格式 | 巨象（mech 6）示例 |
|------|--------|-----------------|
| 4010 皮肤 ID | `401 0 [mech_num] [group] 01` | 原始=40106001，第1套=40106101，**第2套=40106201** |
| 4011 颜色 ID | `401 1 [mech_num] [group] 01` | 原始=40116001，第1套=40116101，**第2套=40116201** |
| 1111 道具 ID | 递增，当前最大 11119972 | 本案例：**11118915**（策划手动指定） |

各机甲编号：巨犀=1, 金刚=2, 野豹=3, 毒蝎=4, 天鹰=5, **巨象=6**, 雄狮=7, 螳螂=8, 战龟=9, 蜘蛛=10, 鳄鱼=11

---

## 三、本案例最终 ID

| 项 | ID |
|----|----|
| 1111 道具 ID | `11118915` |
| 4010 皮肤 ID | `40106201` |
| 4011 颜色 ID | `40116201` |
| 皮肤代号（LC 后缀）| `zhenqibazhu` |

---

## 四、DK 对应关系（⚠ 容易填错）

| DK 名称 | 填入位置 |
|---------|---------|
| 皮肤模型 DK（display_skin_key）| 4010 col[3]、4010 col[5]、4011 col[5] 三处**相同** |
| 皮肤图标 DK（方形头像）| 4010 col[11]、4011 col[14]、**1111 col[6]** 三处**相同** |
| Mask Color DK | 4011 col[12]，单独提供 |

本案例美术 DK：
- 模型：`151105079`（大象新皮肤模型）
- 图标：`151105080`（大象新皮肤方形头像）

---

## 五、4011 三个 URL 字段（gacha 界面用）

| 字段 | col | 说明 |
|------|-----|------|
| `A_STR_gacha_banner_url` | [21] | gacha 界面 banner 图 |
| `A_STR_gacha_reward_url` | [22] | 奖励展示图 |
| `A_STR_gacha_select_url` | [23] | 皮肤选择界面全身立绘 |

路径规律（参考祥和之象）：
```
banner/reward: assets/operation/P2dlcimg/activityImg/EventBanner_Obj_XXX.png
select:        assets/operation/P2dlcimg/llustration/llustrationFullXXX.png
```

本案例切图来源：`D:\CD_UI_NEW_2\2_UI_CUT\H_活动\J_节日机甲抽奖迭代爬塔_87\切图\`

---

## 六、固定值速查（新皮肤抄这里，不用每次查表）

### 1111 item 固定字段

| 字段 | 值 |
|------|-----|
| class | `mecha_skin` |
| quest_class | `31` |
| display_order | `0` |
| display_quality | `15112564` |
| lc_upper_show | `{}` |
| value | `500` |
| max_own | `5` |
| max_get / max_use | `1` / `1` |
| display_labels | `["bag_other"]` |
| fixed_use | `-1` |
| use_now | `0` |
| drop_display | `[]` |
| source | `11740000` |
| effect 第2条 | `{"typ":"item","id":11111034,"val":10}`（固定给碎片） |

### 4010 mecha_skin 固定字段

| 字段 | 值 |
|------|-----|
| skin_level | `0` |
| preview | `1` |
| showcond | `{}` |

### 4011 mache_colour 固定字段（主题皮肤 class=1）

| 字段 | 值 |
|------|-----|
| class | `1` |
| status_active | `[{"typ":"buff","id":121141050,"arg1":800}]` |
| innate_effect | `[{"typ":"buff","id":121136004,"arg1":300}]` |
| display_order | `10001` |
| preview | `1` |
| showcond | `{}` |
| activity_select | `0` |
| area | `600` |
| camera_angle | `180` |
| mecha_actv_place | `{"x":-10000,"y":60,"z":300}` |
| icon_display_key_type | `0` |
| display_tag | `0` |

---

## 七、LC Key 命名规范

| 用途 | 格式 | 示例 |
|------|------|------|
| 4010/4011 皮肤名 | `LC_HERO_mecha_name_{code}` | `LC_HERO_mecha_name_zhenqibazhu` |
| 4010/4011 皮肤描述 | `LC_HERO_mecha_skin_src_{code}` | `LC_HERO_mecha_skin_src_zhenqibazhu` |
| 1111 道具名 | `LC_HERO_mecha_name_{code}_item` | `LC_HERO_mecha_name_zhenqibazhu_item` |
| 1111 道具描述 | `LC_HERO_mecha_skin_src_{code}_item` | |
| 1111 使用提示 | `LC_HERO_mecha_skin_src_{code}_tips` | |

---

## 八、配置工具已知 BUG 及修复

### HTML 生成器：复制 TSV 缺右引号

**现象**：粘贴到 Sheet 后，JSON 字段（如 lc_name）内容被截断，缺少后半部分引号。

**根因**：`escHtml()` 函数未转义双引号 `"`，导致 JSON 值中的 `"` 被浏览器解析为 HTML 属性结束符，`title` 属性值被截断。

**修复**：
```javascript
// 错误
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
// 正确：加上 &quot; 转义
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
```

> 📌 所有后续 HTML 生成器模板复用时必须确认 `escHtml` 包含 `&quot;` 转义。

---

## 九、参考行（可作下次换皮模板）

祥和之象（当前最接近的参考）：
- 1111: `11118871`
- 4010: `40106101`  
- 4011: `40116101`
