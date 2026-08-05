# 把 ActvOnline.ContentID 误当成 ChainPackID 造成假警报

- 日期：2026-08-04
- 场景：X3 马戏节总体扫描，检查 AO106104 装饰阶梯礼包。
- 现象：看到 AO106104 `ContentID=702`，又看到 `ChainPack 702` 已属于相片墙，便初步判断马戏礼包被串包。
- 根因：没有先按 AO 表头区分字段角色。AO106104 真正的连锁礼包引用在 col31 `ChainPackID=706`，而 706 正确指向 `211032|211033|211034`；ContentID=702 是该 ActvType 的内容/样式配置编号，不等同于 ChainPack 主键。
- 纠正：沿完整字段链核对 `AO106104.col31 → ChainPack706 → Pack211032-211034 → Reward同组`，不把同号 702 当引用。
- 后续规则：扫 ActvOnline 时必须用表头/列索引语义追引用，禁止看到相同数字就按表名猜 FK；至少追到“引用字段 → 目标表 → 子配置”两层后再报异常。

## 同轮追加：通用 FK/i18n 扫描的两类假 block

- 首版临时审计把 `RequireFunction=0` 当成缺失引用；X3 标量 FK 的 `0` 与空值都可能表示未绑定，应跳过。
- 首版文本索引只拿整格 key，没有按 `|` 拆 alias，因而把 `TXT_ActvOnline_ActvName_100599` 等共享文本行误报为缺 key。
- 修正后：所有 `|` alias 分键建索引，标量 `0/空` 跳过；22 个马戏节 AO 的通用 FK、嵌套 ChainPack→Pack→Reward、AO 名称/描述 16 语检查均无 block。
