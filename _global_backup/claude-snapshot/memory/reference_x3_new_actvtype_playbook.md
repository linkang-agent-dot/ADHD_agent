---
name: reference-x3-new-actvtype-playbook
description: "X3 新增活动类型(ActvType)的权威落地手册——模板commit/文件清单/msgid算法/生成C#惯例/worktree姿势,加新活动先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 74f31af4-2067-4bc8-b0da-37b9c6cad350
  modified: 2026-07-27T03:51:17.960Z
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

## worktree 姿势(大仓必用)
- x3-project 全量检出会超时(Unity 资产巨大)。正确姿势:`git worktree add --no-checkout <path> -b <branch> origin/dev_festival` → `git sparse-checkout set server client/Assets/Scripts client/Assets/TFWConfig/Protobuf` → checkout。几秒完成。
- 动仓前先 `git branch --show-current`——主工作区可能挂在别人分支(本案撞到 zouhanling 分支),绝不切别人现场,一律 worktree。
- 超时的半成品 worktree:`git worktree remove <path> -f -f` + `git branch -D` + `git worktree prune`。
- **新 worktree 编译服务端必先建 client→server 链接层**:直接 build 报几百个 MsgHandler/IRequest 找不到 = 缺链接。`python MakeLink.py` 在无符号链接特权的 Windows 报 WinError 1314 → 改用 `mklink /J` junction 按 link_config 全量建(≈20 条)即过;junction 在 server/.gitignore 内不会混进提交。一次性环境成本。
- **sparse 依赖路径实测全清单(存钱罐案复证)**:server 编译除 `server client/Assets/Scripts client/Assets/TFWConfig/Protobuf` 外还需补铺 **5** 条:`client/Assets/TFWCore/Script/Common`、`client/Packages/com.tfw.protobuf@1.0.1`、`client/Assets/TFWConfig/FrameworkProtos`、`client/Assets/Res/Config/ProtoGen`、`client/Assets/Res/MapCommon`(缺哪条=对应 junction 目标不存在,建链前 Test-Path 一遍就知道);另 commit 前 `sparse-checkout add scripts .githooks`(pre-commit 报"[视频校验] 未找到 scripts/check_video_assets.py"=scripts 不在 cone;.githooks 被截断则 `git checkout -- .githooks` 还原)。

## 关联
[[project_x3_flashsale_reskin]](本手册出处案) · [[workflow_x3_multiagent_worktree]](并发纪律) · [[reference_x3_actvtype_enum]](枚举权威源)
