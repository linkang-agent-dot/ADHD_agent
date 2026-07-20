---
name: project-x3-frame-removal-gm
description: CS-296963 道具更换案：已用掉的永久头像框扣除 GM 已加进 dev_festival 待版本上线，含上线后执行步骤与头像框系统代码锚点
metadata: 
  node_type: memory
  type: project
  originSessionId: c3ed2a1c-8113-4e56-bb30-dbfed37a57c8
---

# CS-296963 头像框更换：移除头像框 GM（等版本上线后执行）

## 案情
- 玩家 1890192（2090服）要求：扣「滑稽舞台（永久）」道具80091 → 换发「爱意缠绕（永久）」道具80061。
- 卡点：玩家道具**已使用**，转成永久头像框，客服资产修改只能扣道具形态，扣不了已解锁外显。
- 道具→头像框映射（Item 表 use 参数）：80091→框 **10015**（永久-1）；80061→框 10012。

## 已做（2026-07-10）
- x3-project `dev_festival` 新增 GM `[角色_信息]移除指定头像框(含永久,参数=头像框配置ID)`，commit `b6bef0961f4`；**进正式线 MR !723**(feature/cs296963-remove-frame-gm→dev, 2026-07-13开, 基于origin/dev干净cherry-pick)（单文件 +28 行，`server\GameServer.Hotfix\PlayerMeta\BasicMeta.Personal.cs`，在「加速头像框过期」GM 后面）。
- 逻辑对齐过期删除路径：`unlockFrameTimes.Remove` + `UpdateFrameNumeric`（回收词缀属性+战力上限）+ 佩戴中则重置默认框并 ntf；**不发过期邮件**（客服自己发补偿邮件）；**不把被移除框塞进 ntf.unlockFrameCfgIds**（客户端会当新解锁弹"获得头像框"UI，见 client `BasicMeta.Personal.cs OnUnlockHeadFrameNtf`）；未佩戴时客户端缓存等重登对齐。

## 待办（版本上线后）
1. 测试环境先验：GM 面板搜「移除指定头像框」，参数填框ID（如 10015），确认移除+战力回落+佩戴重置。
2. 线上对玩家 1890192@2090 执行 GM 参数 `10015`（走 iGame GM，见 [[reference_igame_gm_send]]）。
3. 回工单让客服邮件补发 80061，闭环 CS-296963。

## 头像框系统代码锚点（服务端 GameServer.Hotfix\PlayerMeta\BasicMeta.Personal.cs）
- 数据：`Data.unlockFrameTimes`（框ID→过期ts，-1=永久）、`Data.usedFrameCfgId`（佩戴中）。
- 现有 GM：解锁所有头像框 / 加速头像框过期（**跳过永久框-1**，这是本案根因）。
- 属性：框带 AffixInfos+Power，增删必走 `UpdateFrameNumeric`（NumericChangeSourceType.Frame）。
