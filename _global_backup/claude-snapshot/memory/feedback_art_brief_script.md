---
name: 美需动画脚本写法
description: 特效美需的动画脚本只写定性描述，不写具体参数
type: feedback
originSessionId: a1c29c47-f955-4979-8cb2-95b357b51283
---
动画脚本的"元素"一节，只写每个元素"做什么动作"，不写具体数值参数（不写透明度%、px、s/圈等）。

**Why:** 参数抠太细了，美术不需要这层信息，脚本的作用是传达意图和节奏感，不是技术规格书。

**How to apply:** 元素描述格式：`元素名 | 动作描述（定性）`，例如"礼帽 | 轻微上下浮动，像悬浮在空中"，不写"幅度5px/周期4s"。

---

## 追加：多语言游戏 UI 切图别烧中文文字（2026-07-01 养成手册 ×2 徽章实证）
出徽章/角标/标签这类 UI 切图，**别把中文文字烧进图**——游戏多语言，中文烧死会在其他语种界面出错/违和。规则：① 纯装饰(丝带/标签底) = **无字空底**，文字由客户端 TFWText 叠(走 i18n)；② 必须带字的标识(徽章/角标) = 只烧**语言中性**内容——数字(×2/-17%)或**英文**(BONUS/SALE)，绝不烧中文。派 x3-media 时 prompt 明确写 "ABSOLUTELY NO Chinese characters, English and numerals only"。**Why:** 中文烧图=锁死单语言，翻不了。

## 追加：X3项目出带数字的图，gpt会把X2画成X3（2026-07-01养成手册实证）
给 X3 项目出"X2倍/双倍"这类**带数字**的徽章/文案图时，gpt 被满屏"X3"游戏名带偏，**常把 X2 画成 X3**（勋章"X3 BONUS"、丝带"每日奖励X3！"都翻过车）。prompt 必须显式锁死：`the multiplier is 'X2' (double), NOT 'X3' — X3 is only the game name, do not write X3 anywhere`。**Why:** 上下文里游戏名 X3 出现太多，模型默认往 X3 靠。出完必核数字。

## 追加：出效果图默认核对横竖屏（2026-07-01）
X3 是**竖屏手机**游戏，出整界面效果图默认要 portrait 竖版；gpt 常默认出横版。prompt 写 "VERTICAL PORTRAIT phone layout (tall 9:16, NOT landscape)"，并给竖版真实截图当参考锁方向。x3-media ui_reskin 有横竖转换 variant。
