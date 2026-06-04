---
name: reference-reskin-workflow
description: X2 节日换皮完整工作流——脚本用法、必检表、踩坑速查、行军表情AI生成链路
metadata: 
  node_type: memory
  type: reference
  originSessionId: 03f54909-5392-432f-954e-d30d028b3fc8
---

# X2 节日换皮工作流

## 一、脚本位置

| 文件 | 用途 |
|------|------|
| `C:\ADHD_agent\.cursor\skills\gsheet-config-replace\scripts\activity_reskin.py` | 单活动换皮（读源→追踪→克隆→输出TSV） |
| 同目录 `run_all.py` | 批量跑多个活动，累积 next_id 防碰撞 |
| 同目录 `write_activity.py` | 把 TSV 写入 GSheet（insertDimension + values.update） |

## 二、JSON 配置模板

```json
{
  "project": "X2",
  "source_activity_id": "211200208",
  "target_activity_id": "21127375",
  "target_comment": "拓荒节-2026-BP",
  "target_constant": "labor_2026_labor_festival_bp",
  "item_mapping": {
    "旧道具ID": "新道具ID"
  },
  "activity_mapping": {
    "旧活动ID": "新活动ID"
  },
  "text_replacements": {
    "占星": "拓荒"
  },
  "preserve_ids": [21127224, 21191335],
  "reuse_types": ["drop", "retake"]
}
```

- `preserve_ids`：共用底座 ID，不做替换（如 base_activity_id、ui_template）
- `reuse_types`：复用旧组件不新建的 typ 列表

## 三、涉及的表（必检清单）

### 核心表（脚本自动追踪）

| 表 | 说明 | id_col |
|----|------|--------|
| 2112 | 活动主表 | 1 |
| 2135 | 活动礼包 | 1 |
| 2011 | IAP 配置 | 1 |
| 2013 | IAP 模板 | 1 |
| 2121 | 活动特殊组件 | 1 |
| 2115 | 活动任务 | 2 |
| 2116 | 兑换 | 2 |
| 2124 | 掉落 | 1 |
| 2137 | 资源回收 | 1 |
| 2122 | 排行规则 | 2 |
| 2118 | 排行奖励 | 3 |

### 间接引用表（脚本不追踪，手动检查）

| 表 | 说明 | 何时需要 |
|----|------|---------|
| 2141 | 无底 Gacha 奖池 | 有 Gacha 抽奖 |
| 2142 | 无底 Gacha 奖励 | 同上，注意页签名可能带后缀 |
| 2024 | 自选礼包坑位 | 有周卡/自选礼包 |
| 2151 | 大富翁地图 | 有大富翁活动 |
| 2130/2131 | BP 战令 | 有 BP 活动 |
| 1111 | 道具表 category_param | 金蛋/周卡解锁引用 2124/2013 |
| 1365 | 行军特效 | 有行军皮肤 |
| 1187 | 装饰家具 | 有装饰品 |
| 1312 | 主城皮肤 | 有主城换皮 |
| 1168 | 访问跳转 | 行军表情等入口 |
| 1180 | 地图表情 | 行军表情 |

### 二级引用必查点

- 2121 JSON 字段（expr/status/array）内的 2124 drop ID、2115 任务 ID、2011 IAP ID
- 2011 iap_status 内的 drop ID（随机礼包奖池）
- 1111 category_param 内的 2124/2013 引用
- 每新增一个 2011 ID 都要加到累充 2122 的 score_rule

## 四、写入安全规范

1. **写前备份**：duplicateSheet 备份目标页签，命名 `_bak_` 前缀
2. **禁用 append**：INSERT_ROWS 会插到表头。用 insertDimension + values.update
3. **定位末行**：遍历 ID 列找真正最后非空行，禁止用 `len(values)`
4. **写后验证**：读回写入行确认列数、ID、位置
5. **列数对齐**：克隆行必须补全到表头列数，INT 空列补 0

## 五、行军表情 AI 生成链路

### 工具

- GRFal API（`C:\ADHD_agent\.cursor\skills\x2-media\call_grfal.py`）
- 模型：gemini（静态图）、wan（视频，duration=4）
- 背景去除：scipy flood-fill（threshold=235），不用 rembg（会挂）

### 流程

1. **生成静态参考图**：gemini 模型，传入旧表情作参考图
2. **生成视频**：wan 模型，传参考图 + prompt，duration=4
3. **选片段**：cv2 抽帧做 contact sheet，确认动画段落
4. **调速度**：调整输出 fps 控制播放速度
5. **抽 16 帧**：从确认片段等距采样 16 帧
6. **去白底**：scipy flood-fill 从四角扩散，生成 RGBA
7. **输出**：
   - 精灵图 4×4（1024×1024 RGBA）
   - 16 张单帧（256×256 RGBA）
   - 静态首帧（256×256 RGBA）

### 注意事项

- cv2 不支持中文路径，必须先复制到 ASCII 临时目录处理
- PIL/Pillow 支持中文路径，最终写回用 PIL
- GRFal remove_background 需要有效 session，过期时用本地方案
- prompt 里加 "fixed camera angle no zoom no pan" 防止 wan 模型自动推拉

## 六、2026拓荒节换皮案例索引

| 内容 | 位置 |
|------|------|
| 完整 ID 映射 | activity_reskin.py 输出的 mapping.json |
| 踩坑第一轮（脚本/写入/知识库） | [[2026拓荒节换皮踩坑总结与优化项]] |
| 踩坑第二轮（引用链遗漏/写入BUG） | [[拓荒节换皮第二轮踩坑（测试阶段）]] |
| 行军表情产出 | `KB\产出-本地化与美术\X2\行军表情\` |

## 七、下次换皮 Checklist

- [ ] 读本文档 + 两份踩坑记录
- [ ] 确认 item_mapping（哪些道具需要新建）
- [ ] 确认 activity_mapping（哪些活动 ID 已分配）
- [ ] 确认 reuse_types（哪些组件复用不新建）
- [ ] 跑 activity_reskin.py dry-run，检查 TSV
- [ ] 写入前 duplicateSheet 备份
- [ ] 写入后全链路验证（含间接引用表）
- [ ] LC key 确认 + 18 语言翻译写入
- [ ] 行军表情/主城皮肤等美术资源确认
