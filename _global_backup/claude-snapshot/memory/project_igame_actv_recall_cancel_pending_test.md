---
name: igame-actv-recall-cancel-x2
description: 2026-06-11 X2 拓荒节试发撤回实测完成——X2 提交即直发无审批态，recall 空操作、cancel(逗号字符串ids) 才生效；P2 审批流场景仍未验证。
metadata: 
  node_type: memory
  type: project
  originSessionId: ff6264eb-1436-4bff-92cf-2ed3438db9ec
---

**2026-06-11 X2 实测结果**（id 13541/13542，拓荒节试发后撤回）：
- X2 活动提交后**直发游戏服、无审批态**（detail status 直接 20=已部署），不存在"部署申请状态"，所以 **recall 是空操作**（返回 success 但 updatedAt 不动、部署还在——别被 success 骗）。
- 生效的是 `activity/operation/cancel`，**ids 必须逗号字符串** `"13541,13542"`（数组 400）；成功后 status 20→7。
- 原"部署申请→recall / 上线中→cancel"规则在 X2 上简化为：**一律 cancel**（除非未来遇到真有审批态的提交）。细节已沉淀 [[workflow-x2-festival-launch-table]]。

**遗留**：P2（有审批流？）场景的 recall 路径仍未实测——下次 P2 下活动时再验一次，验完这条可删。
