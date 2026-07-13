# 冒烟清单（首次真实 key 验证）

代码已全部完成（30 tests passed），API 契约已按官方文档核对（2026-07-13，见文末）。
本清单 = 你拿到火山账号后，第一次跑通真素材要做的事 + 要盯的坑。

---

## 1. 火山引擎开通与防刷爆（先做这个）

1. 开通 [火山方舟](https://console.volcengine.com/ark)（控制台 → 方舟大模型服务平台）。
2. 开通两个模型（模型广场 → 开通管理）：
   - 视觉理解：`doubao-seed-1-6-vision-250815`（打轴用）
   - 视频生成：`doubao-seedance-2-0-mini-260615`（冒烟先用最便宜的 mini；效果不够再换标准版 `doubao-seedance-2-0-260128`）
   - 可直接用 Model ID 调用，也可各建一个「推理接入点」（在线推理 → 创建接入点），接入点 ID 形如 `ep-xxx`，填进 config 同样生效。接入点便于单独限流/监控。
3. API Key：**不要用主账号 key**。IAM 建子账号 → 只授予方舟推理权限（`ArkFullAccess` 以下最小化）→ 在方舟控制台「API Key 管理」创建 key。
4. **⚠️ 必做：控制台设消费限额 + 预警。费用中心 → 资金管理 → 设置消费限额/余额预警（建议先充小额、设日预警阈值，例如 50 元）。视频生成按 token 计费（≈ 宽×高×帧率×时长/1024），一条 720p/15s 段约几毛到几块钱，但管线一次 run 会串行生成多段——没有限额就是裸奔。**

## 2. 本地配置

```bash
cd C:\ADHD_agent\avatar-replace
cp config.example.yaml config.yaml   # 按需改模型 ID / 接入点 ep-xxx
# API key 走环境变量（或写 .env 后自行 source）：
set ARK_API_KEY=你的key        # PowerShell: $env:ARK_API_KEY="你的key"
pip install -r requirements.txt      # 另需 ffmpeg 在 PATH
```

数字人形象：`avatars/<形象名>/` 下放 1~9 张参考图（多角度更稳，见 §5）。

## 3. 冒烟步骤

拿一条 **≤60 秒** 的真实素材（含要替换的人物）：

```bash
python -m core.cli annotate 素材.mp4        # 打轴：VLM 找人，输出 job_id + timeline
# 人工看 timeline（jobs/<job>/job.json）：时段和 person_desc 对不对
python -m core.cli confirm <job_id> --all   # 或 --spans 0,2 只确认部分
python -m core.cli run <job_id> --avatar <形象目录名>   # 切段→逐段替换→拼回
python -m core.cli status <job_id>
```

先只 confirm **一个最短的时段**跑通全链路，再放开 `--all`（省钱 + 快速暴露契约问题）。

## 4. 验收四点

| # | 验收项 | 怎么看 |
|---|--------|--------|
| 1 | 打轴准确率 | timeline 的 start/end 与人物实际出现区间偏差 ≤1s；person_desc 描述能唯一定位到目标人物 |
| 2 | 数字人形象跨段一致性 | 多个替换段里的数字人长相/服装/体型是否同一个人（跨段一致性是生成模型弱项，重点盯） |
| 3 | 非替换区保真 | 替换段内其余人物、背景、运镜、光线不被改动；keep 段逐帧无损 |
| 4 | 音画同步 | 全片音轨来自原片整条铺回，看替换段口型/动作与音频是否对得上（时长漂移超 2% 会自动变速校正） |

## 5. 效果不行时的调参抓手

- **提示词**：`core/replace.py` 的 `PROMPT_TMPL`——素材以"视频1/图片1"按 content 顺序指代；描述不够就在模板里加"人物锁定"约束语。
- **参考图**：加张数（最多 9 张）、加角度（正/侧/背+全身/半身）；图片要求 300-6000px、宽高比 0.4-2.5、单张 <30MB。
- **段长**：config `pipeline.segment_max` 调小（如 10s）——段越短模型越稳，但段数变多、成本上升、跨段一致性压力变大。
- **打轴密度**：`pipeline.frame_interval` 调密（如 0.5s）——短暂露脸不漏检。
- **模型档位**：mini → 标准版 `doubao-seedance-2-0-260128`；分辨率 720p → 1080p（仅标准版）。

## 6. 已知待验证项（文档核对遗留，第一次冒烟逐条打钩）

- [ ] **①（头号）参考视频 base64**：官方文档标注参考视频"仅支持公网 URL（mp4/mov，单段 2-15s，≤50MB，≤3 段），不支持 base64"；图片 base64 明确支持。当前 `volc.py` 视频仍用 data URL 传（本地管线无上传基建）。**若创建任务报 InvalidParameter → 需先把段视频传到可公网访问的地方（TOS / 图床），或试方舟素材上传 API `POST {base}/files`（multipart，purpose=user_data，返回 file id——但 file id 能否在视频生成 content 里引用，各方文档说法不一，需实测）。**
- [ ] ② 请求体总大小 ≤64MB：720p/15s 段 base64 后一般 <30MB，超了就必须走 ①的 URL 方案。
- [ ] ③ 段长下限 2s：`cut.py` 未做最短段约束，命中时段极短（<1s）时可能切出 <2s 的替换段被 API 拒——遇到就把该时段外扩 buffer 调大或手动合并。
- [ ] ④ **真人人脸限制**：有文档标注参考图"不允许真实人脸"（Real human faces are not allowed）。数字人形象图应该没事，但若形象图偏写实被风控拒绝，需换更卡通/风格化的形象图。源视频含真人（未成年人）是否触发内容审核也要实测。
- [ ] ⑤ `duration: -1`（模型自适应）在"参考视频编辑"场景的实际输出时长是否≈输入段长；漂移大就改成显式整数秒（4-15）。
- [ ] ⑥ VLM 单请求图片张数上限：官方未明示（受上下文 token 限制）。`annotate.py` 已按 8 帧/批分批发送（BATCH=8），正常不会超限；若仍报超限就调小 BATCH。
- [ ] ⑨ 拼接处画质/无跳变：替换段已内置归一化（重编码回源片分辨率/fps，见 `core/stitch.py`），冒烟时肉眼检查替换段与原段拼接处是否有画质突变/跳帧。
- [ ] ⑦ 并发/QPS：官方未公布具体数值（429=限流）。当前管线串行逐段生成，冒烟不会踩；将来并行化再实测。
- [ ] ⑧ 模型 ID 时效：`doubao-seedance-2-0-mini-260615` / `doubao-seed-1-6-vision-250815` 以控制台"模型广场"当日展示的 Model ID 为准（方舟模型 ID 带版本日期，会更新）。

## 7. P1 未做、设计文档里提过的能力（别当成已有）

- 段级**并发**生成与自动**重试**：当前串行、失败即停（断点续跑可从失败段继续）。P2 做。
- confirm 前**成本预估展示**（段数×单价）：P2 Web 确认页做；CLI 阶段自己数 timeline 段数估。

## 附：契约核对结论（2026-07-13）

来源：官方 volcengine-python-sdk（arkruntime 源码，权威）+ Seedance 2.0 多家镜像文档交叉验证（官方文档站 JS 渲染无法直读）。

| 项 | 原假设 | 官方实际 | 处理 |
|----|--------|----------|------|
| VLM 端点/传参 | POST /chat/completions，image_url data URL | ✅ 一致，图片 base64 支持 | 不改 |
| VLM 模型 ID | `doubao-1-5-vision-pro-32k`（无版本） | 方舟 Model ID 带版本日期 | config 改为 `doubao-seed-1-6-vision-250815` |
| 视频端点 | POST/GET /contents/generations/tasks | ✅ 一致（SDK 源码确认） | 不改 |
| content 素材元素 | 无 role | 需 `role: reference_video / reference_image` | 已加 |
| 时长/分辨率 | 未传 | body 顶层字段 duration/resolution/ratio/generate_audio/watermark | 已加，进 config |
| status 枚举 | running/succeeded/failed/cancelled | + queued + **expired** | expired 已入失败分支 |
| 结果字段 | content.video_url | ✅ 一致（另有 last_frame_url） | 不改 |
| 视频模型 ID | `doubao-seedance-pro` | 仅 2.0 系列支持参考视频；`doubao-seedance-2-0[-fast/-mini]-xxxxxx` | config 改 mini 版 |
| 视频 base64 | 假设支持 | 文档标注不支持（仅 URL） | 保持 data URL + 注释，冒烟验证（§6①） |
