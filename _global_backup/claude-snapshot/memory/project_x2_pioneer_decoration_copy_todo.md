---
name: project-x2-pioneer-decoration-copy-todo
description: 待办——X2拓荒节5个装饰道具的文案(名字+描述)重写，等明天美术给正式资源图后开工
metadata: 
  node_type: memory
  type: project
  originSessionId: e3fce9d2-73c8-4c84-b61e-26b3f0014e65
---

# 待办：X2 拓荒节装饰道具文案重写（等图）

**状态（2026-06-05 二次更新）**：任务从"文案"扩成"先修资源再推文案"。完整方案+缺件清单见 `C:\ADHD_agent\KB\产出-本地化与美术\X2_2026拓荒节_装饰接线方案与缺件清单.md`（权威进度，优先读它）。

三条 track 进度：
1. **预览图(2D)**：6张AI生成已归档；**落地准备已做完**（图+meta+6 Icon DK[1511094086-091]+item表DisplayKey），dev_festival 工作区未push。**待用户**：Unity Ctrl+Shift+E导出→push client→item导表（先导DK再导表）。
2. **主接线(3D模型)**：Furniture表1105拓荒行(110593-110599)J/K/L全空/残留占星DK，21个新prefab DK全未注册。**卡在**用户找美术确认缺件（地板9vs3变体/挂件缺Pendant03/柜台缺游戏机皮3个）。缺件定了才能录21 prefab DK+填1105。
3. **文案(原任务)**：✅**已完成**(2026-06-05)。6件按实物+包装重起名+重写描述，已写回 i18n EVENT 行7462-7475(跳过355的7472/7473)，全18语言，EVENT已备份。新名：350寰宇星盘/351拓土方阶/352垦荒木墙/353荒野花信/354夜归铜灯/356边境货栈。**待i18n导表(fwcli 1011_x2_i18n 全表)生效**。命名调性参考占星(星象仪摆件/夜空墙纸)+P2(流水花庭)。

资产/产线知识：见 memory [[reference-x2-indoor-furniture-assets]]。

## 美术资产（2026-06-05 已定位，详见 [[reference-x2-indoor-furniture-assets]]）
- 位置：`D:\UGit\x2client\client\Assets\x2\Res\Shop\Indoor\`（Building/Decoration/Shelf）
- 全套 8 类：①装饰柱Pillar ②地板Floor ③墙纸Wall ④窗Window ⑤壁灯BracketLight ⑥吊饰Ornaments ⑦墙面挂件Pendant01/02 ⑧柜台Counter01-03(+地毯Carpet×3+摆件Prop)
- **配置只投 5 件(350-354)，没进投放的：窗/壁灯/吊饰/整套柜台区 → 疑似配漏，待用户确认**
- 350 表名"装饰柱"但用户口径"柜台"，美术两者都有 → 必须对图核实 350 到底对哪件
- 给用户看的贴图预览(15张PNG)：`C:\Users\linkang\Pictures\拓荒装饰资源\`（_D漫反射转的，临时给用户认图用）

## 范围：只动 5 个装饰（355墙面3/356舞台 没做，不管）

| 道具ID | item行(1111) | 表里名 | 用户口径 | name LC key | desc LC key |
|--------|------|--------|----------|-------------|-------------|
| 111111350 | 2233 | 装饰柱 | **柜台**(待图核实到底是柱还是柜台) | `labor_2026_wall_decoration_1` | `labor_2026_wall_decoration_1_desc` |
| 111111351 | 2234 | 地板 | 地板 | `labor_2026_floor_1_title` | `labor_2026_floor_1_title_desc` |
| 111111352 | 2235 | 墙纸 | 墙纸 | `labor_2026_wall_1_title` | `labor_2026_wall_1_title_desc` |
| 111111353 | 2236 | 装饰墙面1 | 挂饰1 | `labor_2026_wall_decoration_3` | `labor_2026_wall_decoration_3_desc` |
| 111111354 | 2237 | 装饰墙面2 | 挂饰2 | `labor_2026_wall_decoration_4` | `labor_2026_wall_decoration_4_desc` |

## 关键事实（查证已固化，明天不用重查）
- **本地化没缺口**：14个key在i18n已18语种全译、无占星残留。问题是**中文文案太雷同**（5条desc全是"拓荒节专属XX，装备后可美化主城。"）+ **名字可能跟实物对不上**（350表里写装饰柱、用户叫柜台）→ 要重写。
- **改文案只动 i18n 的 cn 值，不动 key**（key命名是乱的但不影响显示：装饰柱挂在wall_decoration_1、墙面用3/4/5）。
- 三方文案(item Comment / 1187 / i18n)目前语义一致，无错配。

## 表坐标（live GSheet）
- **i18n EVENT**（改文案的落点）：SheetID `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg`，页签 `EVENT`，5个装饰的name+desc共10个key在第 **7462–7471** 行（B=key C=cn D=en…T=cns）。
- 1111 item：SheetID `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs`，页签 `item`，正式批350-356在第2233-2239行。
- 1187 FurnitureBuild：SheetID `1lXRldN7kN_HsEYQ5FfNdawep23TD9J81Vj66yKRdjEk`，页签 `FurnitureBuild`，拓荒家具第71-77行，引用解锁道具350-356。

## 两个遗留问题（文案弄完回头处理）
1. **350 到底是柜台还是装饰柱**——看图定，名字要对上实物。
2. **355墙面3 / 356舞台 没做但1187第76/77行还配着**（解锁道具355/356还在），验收若在装饰列表露出会是空图/占位，需决定是否从1187摘掉这两行。

## 废弃批（不用管，别误删）
1111 还有早期废弃批 111111328-335（第2211-2218行），与正式批350-356共用同一套key。删它不影响翻译，但本轮不动。
