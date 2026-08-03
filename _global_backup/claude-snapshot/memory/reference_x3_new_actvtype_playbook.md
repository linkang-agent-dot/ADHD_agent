---
name: reference-x3-new-actvtype-playbook
description: "X3 新增活动类型(ActvType)的权威落地手册——模板commit/文件清单/msgid算法/生成C#惯例/worktree姿势,加新活动先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 74f31af4-2067-4bc8-b0da-37b9c6cad350
  modified: 2026-07-28T08:35:15.236Z
---

# X3 新增 ActvType 权威落地手册（2026-07-24 限时抢购案沉淀）

## 权威模板 = 扭蛋机(ActvType 83)的两个真实 commit（x3-project 仓,dev_festival）
- **代码骨架** `b68261ca862`「服务端+共享注册+proto落地」：**17 文件 1170 行**,比"五件套"多出 6 处——完整清单:ActivityConst(常量+集合)/ErrCode.Activity/SysOpReason/BIUserCommonActivity(枚举)/BIUserActivity(打点方法)/activity.proto/**msgid.def**/两处生成C#(Scripts\Protos\activity.cs + CSSharedHotfix\Common\Protos\activity.cs)/ActivityHotfixUtils/Condition类+.meta/ActivityMeta.cs OnRemove case/ActivityMeta.XXX.cs handler partial/(有榜才要)ServerActivityRankMeta 3处。
- **配置底座** `3ca446c2270`：gdconfig 建表(tsv+def)→TableProtoGen 生成 CfgProtos C#+Res/Config/Proto+ProtoGen bytes 进 client 仓 + ActvOnline 主行 + Item 行。**配置底座先行,代码才有 CActvXxx 可引**。
- 拿清单姿势:`git show --stat <commit>`;整个 diff 导出来当逐文件样板。

## 关键硬知识
- **msgid.def = BKDR-131 哈希**:`h=0; for c in name: h=(h*131+ord(c))&0xFFFFFFFF`。已用 4 个现值验证(DoCircusGachaReq=2108283020 等)。新消息名跑一遍算出来直接填。Req→Ack 差值恒为 292005(只差最后3字符)可当校验。
- **生成 C#(两处 Protos)是"手写照现有生成物样式补齐"的既定实践**(扭蛋机 commit message 原话),Unity Protogen 重跑会覆盖为工具产物。WriteTag:field n 变长=n<<3,长度型=n<<3|2(tag66→530,tag67→538)。Ack 类必带 errCode(WriteTag 8032=field 1004),proto 文件里不写 errCode 只在生成 C# 有。
- **ActvType 权威枚举** `client\Assets\Scripts\CSShared\Common\Const\ActivityConst.cs`;单服活动登记 `SingleServerActivityTypes`(L237附近),跨服榜托管才进 `CenterHostedSingleActivityTypes`。注释提醒:新单服活动**导表工具也要登记**。
- **proto 聚合 message 叫 `ActivityItem`**(不是 ActivityData),在 `client\Assets\TFWConfig\Protobuf\activity.proto`。**分支分叉雷**:dev 与 dev_festival 的 tag 64/65/66 语义已冲突(dev:payGacha/unionIpo/slgMeteorWar vs festival:pioneerCity/bpFund/circusGacha),加新 tag 必须双分支 grep 确认双侧空闲。
- **单服共享状态**(如全服限量库存)落 `ServerActivityMetaBase<TData>`(server\GameServer\Entity\Activity\ServerActivityMetaBase.cs,带 Mongo GetPersistentData 持久化),照 ServerActivityMeta\ 下 20+ 个现成 Meta 的样式建 `ServerActivityXxxMeta`。
- **编译验证口径**:`dotnet build` GameServer.Hotfix / CenterServer.Hotfix / MapServer.Hotfix 三工程 0 error(扭蛋机 commit 原话)。
- **gdconfig 建表 BD_ 前缀坑**(限时抢购案实证):被 `Table.Field` 跨表引用的组列,其 tsv **中文字段名必须带 `BD_` 前缀**(`FieldDef.isBeDepended = comment.find("BD_")`),否则 ExportTable depend_checks 报 `not existed`。扭蛋机表里的「BD_组」就是这来历。string 列(如竖线分隔多 id)无法挂 row3 引用 → def 里逐 id `register_depend_config_and_val`。
- **CfgProtos 生成不碰主仓的姿势**:`Tools/table_exporter/protogen-csharp/win/TableProtoGen.exe --only_gen True --client_path <临时目录>` 生成到假 client 再选择性拷入 worktree(工具默认读 local.json/env.json 指向主仓,别配它);同批生成的 CustomMessage.cs 与仓内既有生成物逐字节比对=验证工具版本一致。
- **sparse-checkout 会截断 cone 外的 tracked 文件**(.githooks 三个 hook 被部分清空的实证):sparse add 新目录后,发现 tracked 文件被截断 → `sparse-checkout add` 该目录 + `git checkout -- <path>` 还原;commit 前查 pre-commit 钩子依赖的 scripts/ 是否在 cone 内。

## 客户端阶段补充(限时抢购阶段2考古)
- **UI 类注册无需手补**:Editor/PC 走 `WndMgrEx.InitUITypes` 反射扫描 `[GameCommon.Identifier]` 自动注册;`UITypeAutoRegisterGen.cs` 仅真机打包时重新生成(扭蛋机也不在里面)。Identifier ID 只要求全局唯一(重复会在 ScanUITypes throw),新 UI 用 BKDR-131(类名) 再 grep 确认无碰撞即可。
- 客户端镜像 partial 模板:`client/Assets/Scripts/Entity/Player/Activity/ActivityMeta.CircusGacha.cs`(Req 前置校验+Ack 更新 data+FireEvent);UI 结构模板=UIBase<UIActivityData> 生命周期+Auto_ partial 绑定文件(FindByFullPath 按 prefab 真节点路径预绑)。
- 客户端 C# 由 Unity 编译,dotnet 三工程绿≠客户端能编(_CLIENTLOGIC_ 段 dotnet 不碰)——诚实标注,Editor 验证单列。
- **⚠️ 命令行热塞 client bytes 对运行中的 Editor 无效**(限时抢购反复踩):客户端读的是 **Unity 导入过的 TextAsset**,不是磁盘 .bytes;命令行 cp 新 bytes 后,运行中的 Play 仍读旧导入资产(实证:cp 进 Price=107、文件里验证有、客户端运行时仍读 0)。**改客户端 bytes/代码后必须让用户完全关 Editor 重开**(强制 AssetDatabase 重导 + 脚本重编),退 Play/大退账号都不够。另:client ProtoGen .bytes 是 git-tracked,手动 cp 的会被任何 git 操作还原(测试期别对 client 仓 pull/checkout)。
- **⚠️ 客户端是繁体(zh 列)时,只填 cn/en 会满屏空白**(限时抢购实证):Text 表语言列 = cn/en/sp/fr/id/de/kr/**zh(繁)**/ru/ua/jp/it;繁中客户端读 zh 列,只填简体(cn)→繁中界面所有自定义文案空白。新 ActvType 的 i18n 至少 cn+en+zh 三列(zh 可先拷 cn 值应急),完整 14 语走 x3-translation-automatic。

## X2→X3 UI prefab 搬运(限时抢购 2026-07-27 实证,照扭蛋机迁移 commit 8e11ea9c73f 先例)
- **🔑 X2/X3 是同源工程,公共资源大量同 guid**——字体(OPlusSans/思源宋)、常用公共件 prefab(ItemMid/ButtonBlueBig/ClickToClose 等)、TFW 框架/uGUI 脚本 guid 在 X3 **原地解析,不用拷不用换**。搬运前把 bundle 的"未解析 guid"清单先在 X3 全仓 grep 一遍,实测 48 图剩 24、13 公共件剩 2、字体零改——**断链量≈预估的一半,别按全断链报工作量**。
- **搬运套路**:①专属图连原 .meta 拷入 `Res/UI/Sprite/UIActvXxx/Images/`(保 X2 guid,prefab 引用不断)②prefab 拷入 `Res/UI/Prefab/Activity/`,主件名=代码加载路径写死的名 ③**剥 X2 专属脚本组件**(特效 Graphic/Spine SkeletonGraphic/LoopScrollRect 之类 X3 没有的),装饰性的直接剥、功能性的换 X3 等价 ④缺源嵌套 FX 实例整块移除、缺失 Animation clip 置空 ⑤**文字浮雕特效 missing script 可照扭蛋机先例保留**(Editor 警告无害,已有上线先例)⑥DK 注册=`Editor/Config/DisplayKey/Display_Activity.asset` 追加(key=图名/type/guid)+`Res/Config/DisplayKey/Path_Activity.asset` keys/values 双段追加。
- 剥了什么在哪个节点要列清单留档(用户 Editor 按需补 X3 组件/美术补动效)。
- **⚠️ 分阶段开发的 TODO 扫尾纪律**(限时抢购实证):早阶段因依赖未就绪留的 `TODO(阶段N)`(如阶段2 UI 因 CfgProtos 未生成跳过 icon/价格渲染),**依赖就绪后没人自动回头补**——验收时"界面空图/没文案"就是它。收口前全仓 `grep "TODO(阶段"` 逐条销账,别当注释留着。
- **⚠️ 新增 ErrCode 必须配套录 `Text_ErrCode<常量名>` i18n key**(限时抢购实证:点抽奖弹出裸 key `Text_ErrCodeActivityFlashSaleRaffleNoCount`)——X3 错误码 toast 按此命名约定查文案,加 N 个错误码=加 N 个 Text_ErrCode key(cn/en 起步),别漏。列进新 ActvType 的 i18n 清单。
- **⚠️ 带时间窗/场次/阶段的活动,服务端必须在边界时刻主动推送数据**(限时抢购实证:场次开抢瞬间在线玩家界面不会自己变,点按钮靠 Ack 捎数据才刷——"要点了按钮才出来")。X2 同类语义=换场服务端重发。落法=ServerActivityMeta 定时任务到点遍历在线玩家 Refresh+推 UpdateActivityDatasNtf;客户端倒计时归零拉取做兜底。与下一条(登录填充)配套成对:**登录填一次+边界推一次,缺一个都会"看不到"**。
- **⚠️ 下发数据必须在登录钩子填充,不能只靠请求触发**(限时抢购空货架实证):OnAddActivity 只建空壳数据;若 packs/场次等填充只写在 [MsgHandler] 里→玩家登录打开界面=空数据(没人发过请求)。**新 ActvType 必在 `ActivityMeta.OnPostInit`(完整登录钩子,链式 gift 补建同位置)对该类型活动跑一次数据刷新**;OnReconnected 也要考虑(重连不走 OnPostInit 的已知坑)。
- **⚠️ 界面出现 555/9999 类占位数字 = 有未接管的节点,常见是"嵌套 prefab 实例"**(限时抢购购买钮实证):X2 prefab 里价格钮/通用件常是嵌套 prefab(PrefabInstance),其内部文本(如 Layout/txt=9999)和自带 Button 组件**不会被外层按路径绑定覆盖**——表现=占位数字上屏+点击被无 handler 的 Button 吞掉(服务端 Req 计数 0)。搬运清点时嵌套实例要单独过一遍:文本接管+点击接管或禁用其 Button。定位法=prefab YAML 搜占位文本值,父链解析不出(?)=嵌套实例。
- **⚠️ X2 prefab 静态文本 = LC_ key 字面量**(搬运后满屏裸 key 实证):X2 的 Text 组件里直接写 LC_xxx,靠 X2 本地化脚本运行时替换;剥脚本后原样裸露。搬运清点:prefab YAML grep `LC_` 列全静态文本节点→逐个"接管(代码绑 TXT key)或隐藏(X2 特有模块如累计大奖进度)",别留裸 key 上界面。
- **UI 渲染现成 API 惯例**(补渲染别发明):道具图标=`UIHelper.GetPackFirstAndEndowItems`(取包首道具,周特惠同款)+`UIHelper.SetItemBasicInfo(itemID, image)`(走 DK,扭蛋机同款);价签=钻石 `UIHelper.ThreeDigitsCommaSeparated` / IAP `GetGiftFormattedPriceByPrice`;文案 `LocalizationMgr.Format`。**Pack 名 i18n key 走导表自动惯例 `TXT_Pack_Name_<PackId>`**(211006 世界杯实证)。

## worktree 姿势(大仓必用)
- x3-project 全量检出会超时(Unity 资产巨大)。正确姿势:`git worktree add --no-checkout <path> -b <branch> origin/dev_festival` → `git sparse-checkout set server client/Assets/Scripts client/Assets/TFWConfig/Protobuf` → checkout。几秒完成。
- 动仓前先 `git branch --show-current`——主工作区可能挂在别人分支(本案撞到 zouhanling 分支),绝不切别人现场,一律 worktree。
- 超时的半成品 worktree:`git worktree remove <path> -f -f` + `git branch -D` + `git worktree prune`。
- **新 worktree 编译服务端必先建 client→server 链接层**:直接 build 报几百个 MsgHandler/IRequest 找不到 = 缺链接。`python MakeLink.py` 在无符号链接特权的 Windows 报 WinError 1314 → 改用 `mklink /J` junction 按 link_config 全量建(≈20 条)即过;junction 在 server/.gitignore 内不会混进提交。一次性环境成本。
- **sparse 依赖路径实测全清单(存钱罐案复证)**:server 编译除 `server client/Assets/Scripts client/Assets/TFWConfig/Protobuf` 外还需补铺 **5** 条:`client/Assets/TFWCore/Script/Common`、`client/Packages/com.tfw.protobuf@1.0.1`、`client/Assets/TFWConfig/FrameworkProtos`、`client/Assets/Res/Config/ProtoGen`、`client/Assets/Res/MapCommon`(缺哪条=对应 junction 目标不存在,建链前 Test-Path 一遍就知道);另 commit 前 `sparse-checkout add scripts .githooks`(pre-commit 报"[视频校验] 未找到 scripts/check_video_assets.py"=scripts 不在 cone;.githooks 被截断则 `git checkout -- .githooks` 还原)。

## 关联
[[project_x3_flashsale_reskin]](本手册出处案) · [[workflow_x3_multiagent_worktree]](并发纪律) · [[reference_x3_actvtype_enum]](枚举权威源)
