---
name: x3
description: X3 配置自动key文本(礼包名/邮件标题等)显示空白的根因排查——服务端CheckAndConvertCfgTxtToEmpty在key缺失时返空
metadata: 
  node_type: memory
  type: reference
  originSessionId: 33fe5727-08d6-48d3-80a0-91952eddfd74
---

## 现象
界面/邮件里某个"自动读取的名字"显示空白（如买礼包后邮件正文"恭喜您已购买【】"礼包名空）。

## 机制（X3 自动key文本管线 + 服务端取值）
- 配置表文本字段(Pack.Name/MailTemplate.Title等)客户端**不读单元格**，读自动key(`CfgProtoTextEx.cs` getter拼)：
  - 礼包名 `TXT_Pack_Name_{packId}`、邮件标题 `TXT_MailTemplate_Title_{id}`、邮件正文 `TXT_MailTemplate_Content_{id}`、发件人 `TXT_MailTemplate_FromName_{id}`、简述 `TXT_MailTemplate_BriefDesc_{id}`。
- getter 走 `CfgHelper.CheckAndConvertCfgTxtToEmpty(key)`(`CfgHelper.cs:90`)：
  ```
  #if _SERVERLOGIC_   return LocalizationMgr.ContainsKey(key) ? key : string.Empty;   // 服务端
  #else               return IsNullOrEmpty(LocalizationMgr.Get(key)) ? string.Empty : key;  // 客户端
  ```
- **关键坑**：买礼包邮件正文 {0}=`cfg.Name`(=`TXT_Pack_Name_{packId}`)由**服务端**填进 contentArgs。**服务端加载的本地化没这个key → cfg.Name 返回空串 → 邮件名字空白**(不是显示key字面、是真空)。买礼包发的是邮件模板 **MAIL_BUY_GIFT=3000000**(`TableConst.cs`)，路径 GiftMeta.cs:2046 `detailInfo.contentArgs.Add(cfg.Name)`。

## 排查顺序
1. **配置在不在**：grep `tsv/i18n/Text__Text.tsv` 找该自动key。**注意合并行**——key 可能在 `col0=TXT_A|TXT_B|TXT_C` 的管道合并行里(精确 `$1==key` 会漏，用 `grep -F`)。导表 `gen_i18n.py:127/143` 会 `split('|')` 给每个 key 都注册值，所以合并行里的副 key 也有效。
2. **配置齐了还空 → 服务端跑旧导出**(最常见，同 [[reference_x3_rank_config_chain]] 的结论模式)：key 在 dev tsv 但服务端加载的 localization bytes 是该 key 加入之前的旧版 → ContainsKey=false → 返空。修=`!gm ReloadGameServer` 热更最新 ProtoGen(含 localization bytes)，或确认服加载导出版本≥该 key commit 日期。
3. **真缺配置**：客户端/iGame 用的 ID 不在已配 key 范围(如 customParam 填了名字 key 不存在的礼包号)→ 补 Text 表(走 x3-translation-automatic 或手补，记得独立行/合并行机制)。

## 实例(2026-06-24 世界杯竞猜买礼包邮件名空)
192个竞猜礼包名 `TXT_Pack_Name_894010~894483` 全在(独立行/10+语言齐, commit 34909e9 2026-06-17 已合dev)，邮件标题3000000 key也在(合并行)→配置无缺。空=测试服跑6/17前旧导出。

## 实例(2026-06-29~30 深海居所装饰底部入口标签空白·已结案)
HUD底部活动入口(沙滩椅图标)无文字=活动页签标签`TXT_ActvOnline_ActvName_106103`(深海居所装饰)空。该key 16语齐(繁中"深海居所裝飾")且commit `dfba14d` 进dev_festival→空=运行中的客户端/服务端读的是更新前的旧localization,没重载。
- **★坑1(差点误判):繁中译文≠简体母版用词,不能当"旧导出"证据**。本例副标题`TXT_Pack_Desc_211016`游戏显繁中"深海瞬間…"而config简体母版是"深海馈赠…"——繁中翻译本就用了不同词,正常,**不是旧导出**。判旧导出真证据=「key在dev但客户端查不到」(尤其近期新加commit),不是「显示文案≠简体母版」。
- **★坑2(本次结案关键):bytes 可能其实早导对了,真因是「没重载」+「manifest stale」**。本地重导后发现 client `i18n/zh.bytes` 的 md5 跟新导出**完全相同**(数据早就在盘上)→根因不是没导,是①运行中的Editor客户端/3080服在bytes更新前已把旧localization读进内存没重载 ②client manifest 的 **16个 i18n 语言行集体 stale**(某次导出更新了bytes却没更新manifest,md5对不上文件)。
- **修(本地服→Editor链路·实测全过2026-06-30)**:① jolt导表失败时走本地 `cd Tools/table_exporter && python ExportTable.py`(产物在 `C:\x3\gdconfig\temp_dev\ProtoGen\`,含 `i18n/*.bytes`+`ActvOnline.bytes`+`AllTableDataMd5.txt`) ② cp 改的 bytes(尤其 `i18n/*.bytes`)→ `client/Assets/Res/Config/ProtoGen/` ③ **同步 manifest**=`python ~/.claude/skills/x3-config-export/scripts/sync_client_manifest.py i18n ActvOnline.bytes`(只更新这几张表的md5行·别整份覆盖;temp_dev用反斜杠path、client用正斜杠,脚本已归一) ④ `python ~/x3_gm.py "!gm ReloadGameServer"`→日志 `ReloadAllLoadedCfgByFilenames: i18n/cn..zh` + `16 tables reloaded`(没同步manifest会是 `0 tables reloaded`) ⑤ **标签是客户端i18n,服务端reload不影响运行中的Editor客户端**→最后必在Unity Editor对 `i18n/*.bytes` Reimport + 重进Play,客户端启动时重载localization才显示。
- **★口径:页签/HUD入口标签=活动名 `TXT_ActvOnline_ActvName_{AO}`;大礼包标题=礼包名 `TXT_Pack_Name_{packId}`,两者不同源**(本例标签"深海居所裝飾"≠大标题"深海居所特惠",正确)。详见 [[workflow-x3-local-server-gm-telnet]] 本地导表→热更段。

**How to apply:** 见到"自动文案空白"别急着判缺配置——先 grep(含合并行)确认 key 在不在 dev；在就转查服务端是否重载了最新导出。详见 [[reference_x3_i18n_workflow]] + [[reference_x3_config_library]] 自动key机制。
