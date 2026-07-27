---
name: reference_x3_actvonline_serverlist_merged_gate
description: X3 ActvOnline 圈服(OpenServerList/CloseServerList)含已合并服→导表 PostProcessData 直接 abort 整个导表;圈服快照必须排除 Server.MergedServers。做"圈服绕行"活动配置前必读
metadata:
  node_type: memory
  type: reference
  originSessionId: 5bcaa8dc-9303-4a6f-9fad-2d5ac7365882
  modified: 2026-07-24T08:22:40.648Z
---

# X3 圈服绕行的隐形雷:OpenServerList/CloseServerList 含已合并服 → 导表整体 abort

2026-07-24 士兵装备活动服龄门(zouhanling/soldier-equip-gate-60d, ActvOnline 105701-06)验证实测。

## 现象
ActvOnline 的 `OpenServerList` / `CloseServerList` 里只要含**一个已被合服的服务器 id**,本地/Jenkins 导表都会在极早期抛:
```
Exception: ActvOnline配置错误：包含已经被合并的服务器 {105701:[1000,1010,...], ...}
```
→ **整个导表 abort,一个 bytes 产物都不生成**(ActvOnline.bytes / i18n bytes / 所有表都没了)。不是只跳过这张表。

## 根因(代码锚点)
`Tools/table_exporter/PostProcessData.py` `deal_actv_online_data()`:
- line 1677: `mergedServers = Utils.getTableRowDataByPrimaryKey("Server","MergedServers").MergedServers` —— 已合并服名单来自 **gdconfig 的 `tsv/Server__Server.tsv`**(入库表),所以**本地和 Jenkins/jolt 读同一份 → 会同样失败**,不是本地环境误报。
- line 1743-1749: `serverIds = item.OpenServerList + item.CloseServerList` **两个列表都查**,任一元素命中 mergedServersSet 就记进 `includeInvalidServerIds`。
- line 1901-1902: 收尾若非空 → `raise`。
- 校验发生在 `process_data()` 早期(ExportTable line 90),**在序列化/生成 bytes 之前**,所以连累后面所有产物。

## 关键点
- **jenkins_tsv_schema_gate / i18n_check PASS ≠ 能导表**。schema gate 是轻量列结构检查,**不跑 PostProcessData 的语义校验**。圈服含已合并服这类错只有完整 ExportTable(robot/jolt 跑的那套)才抓得到。验"导表产物"必须真跑 ExportTable,不能只看静态门。
- **"圈死存量服"用机械区间(如 1000~2570 步10 + 9998)取快照极易踩雷**:老服区段里通常已有一批被合服,机械区间会把死服号也圈进去。正确做法=从**当前存活服**列表取,或对机械快照**扣掉 Server.MergedServers**。本案 159 服快照里就有 43 个已合并服(1000~1520 段)。
- **CloseServerList 含已合并服也报错**(哪怕排除死服在业务上无害,工具照样拒)。
- **"塞一格上百 ID"本身不截断**:工具逐个读了全部 159 个才挑出 43 个非法的;剔掉 43 后重导,ActvOnline.bytes 反序列化出 116 个 int 完整无损(首尾/中段抽查全对)。所以大数组塞一格是安全的,雷只在"含已合并服"这个内容语义上。

## 验证手法(本地导表产物验证通用姿势,不依赖 Unity)
1. `git worktree add --detach <wt> origin/<分支>` 建只读沙箱。
2. `python scripts/sync_xlsx_tsv.py --from-tsv --all`(重建 xlsx 视图,~1min,否则 ExportTable 的 verify_xlsx_tsv orphan abort)。
3. `cd Tools/table_exporter && python ExportTable.py` —— 报错即在此暴露;成功则产物在 `<wt>/temp_dev/ProtoGen/*.bytes` + pb2 在 `<wt>/temp_dev/python_pb/`。
4. 解 bytes: `sys.path.insert(0,"temp_dev/python_pb"); import ActvOnline_pb2; m=ActvOnline_pb2.CActvOnline(); m.ParseFromString(open(".../ActvOnline.bytes","rb").read())`。顶层 `m.Configs` 是 **map<int,CActvOnlineCfg>**(382 项),`m.Configs[105704].OpenServerList/CloseServerList/RequireFunction` 直接读。python protobuf 读 packed/unpacked 都行,数组计数不受 GenProto packed 坑影响。
5. i18n bytes(`temp_dev/ProtoGen/i18n/{cn,en,kr,ru,...}.bytes`):key 是**原文串非哈希**,条目结构 `0x0a<len>key 0x12<vlen>value`;合并键组 `A|B` 会被 gen_i18n 拆成独立条目(gen_i18n.py:143),所以克隆活动补的新键在 bytes 里是独立条目=不裸奔。
- `FunctionType.cs` 由 `PostProcessData` 早期的 `GenNumericCode.gen_function_type` 生成(写 Tools/table_exporter/cwd),**即使 ActvOnline 后续 abort 它也已落地**,可直接 grep 验枚举(`SoldierEquipActvGate = 8004`);出现两次=完整枚举+服务器使用子集两个块,非冲突。

## 相关
[[reference_x3_tsv_export_migration]] [[reference_x3_config]] [[reference_x3_actvtype_enum]] [[reference_x3_unity_mcp]]
