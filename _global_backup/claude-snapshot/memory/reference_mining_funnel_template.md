---
name: 挖矿回归漏斗表格模板
description: 分R级关卡/任务漏斗可视化模板，用于挖矿小游戏等活动的通关回归分析
type: reference
originSessionId: 01fae4ed-878e-4fa8-b10b-cc598258a401
---
## 模板文件

`C:\Users\linkang\mining_funnel_template.html`

Demo 预览：https://demo.tap4fun.com/mining_rlevel_funnel_c616/

## 用途

挖矿回归（及类似活动）中，用于可视化**分R级关卡/任务漏斗**：
- 每行 = 一个关卡/任务节点
- 列 = 各R级（非R/小R/中R/大R/超R）的人数、步骤转化率、留存率
- Tab 切换多个周期（如三期活动）
- 支持奖励类型标注（白包/绿包/道具/无奖励）

## 复用方法

只需修改 HTML 中的 `CONFIG` 对象：

```js
const CONFIG = {
  periods: [
    { label: '第一期 x.xx-x.xx' },  // Tab 名称
    ...
  ],
  data: [
    // 每期一个对象
    {
      entry: { 1:非R入口, 2:小R入口, 3:中R入口, 4:大R入口, 5:超R入口 },
      rows: [
        {
          id: '关卡名称',           // 显示名
          reward: '+白包×2',        // 奖励文字（自定义）
          rewardType: 'white',      // 'white'|'green'|'item'|'none'
          sectionStart: true,       // 可选，true=该行上方加粗分割线
          d: { 1:非R人数, 2:小R, 3:中R, 4:大R, 5:超R }
        },
        ...
      ]
    },
    ...
  ]
};
```

## 奖励类型颜色

| rewardType | 显示颜色 | 用途 |
|---|---|---|
| `white` | 蓝色（白包色） | 白色/绿色等卡包奖励 |
| `green` | 绿色 | 绿包/高级奖励 |
| `item` | 黄色 | 其他道具（骰子/积分/BP等） |
| `none` | 灰色 | 无奖励节点 |

## 步转颜色规则

| 转化率 | 颜色 |
|---|---|
| ≥90% | 绿色（正常） |
| ≥80% | 浅绿 |
| ≥70% | 黄色（注意） |
| ≥60% | 橙色（偏低） |
| <60% | 红色（问题点） |

## 适用场景

- 挖矿小游戏循环关卡回归
- BINGO 分层任务完成率
- 大富翁阶段转化
- 任何「多节点顺序推进」类活动的分R级漏斗分析
