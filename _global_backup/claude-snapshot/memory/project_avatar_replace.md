---
name: project_avatar_replace
description: 个人侧项目：视频未成年人→数字人替换平台（自建直连火山引擎，严禁走公司GRFal）；设计+P1计划已落盘，待选执行方式开工
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3b3ccf-262a-424d-ad12-d49316bd5204
---

# avatar-replace：视频未成年人→数字人替换平台

**性质（红线）**：个人侧项目，服务合作方的投放/宣传素材合规。**全程严禁调用公司 GRFal / 公司资源**（用户 2026-07-13 明令）；后端自建直连火山引擎（Seedance 视频替换 + 豆包 VLM 打轴 + 即梦文生图建形象库，同一账号）。

**唯一入口**：`C:\ADHD_agent\avatar-replace\docs\plans\`
- `2026-07-13-avatar-replace-design.md` — 设计文档（含「被否决的方案」决策记录：否决走GRFal/一步到位公网平台/纯CLI/整片送Seedance）
- `2026-07-13-avatar-replace-p1-plan.md` — P1 管线核心实施计划（12 任务 TDD，测试全 mock 零真实调用）

**核心链路**：上传(≤60s) → VLM 1fps 抽帧两遍打轴（粗定位含未成年人时段→细化外观描述）→ 人工确认（兼作误判兜底+成本预告）→ 切段（镜头切点只向外吸附、±0.5s缓冲、>15s二分，非命中段原样保留）→ 每段 Seedance 替换（参考视频+形象库2-3张参考图，prompt 锁运镜）→ 拼回（时长漂移>2%变速对齐；**音轨整条用原片铺回**，Seedance 音频丢弃）。

**关键技术锚点**：Seedance 参考视频单次上限 15s（一切分段策略的根因）；GRFal 的 ref_types 是 GRFal 自己的抽象，方舟原生 API 契约待 P1 Task 11 对官方文档核对（volc.py 是唯一改动点）。

**阶段**：P1 管线核心(CLI) → P2 Web薄壳 → P3 形象库（即梦生成明显成年形象，跨视频一致）→ P4 部署形态后置（公网加鉴权配额限流 vs 做成交付包让合作方自建各用各key——后者安全问题自动消解）。**最大不确定性=Seedance 人物替换实际效果**，P1 跑通即真素材验效，不行早止损。

**安全要点（公网化才启用）**：key 只在服务端环境变量+火山子账号最小权限+控制台消费限额硬顶；登录白名单/每日配额/IP限流中间件预埋本地关。用户特别强调防被入侵无限刷 API。

**GRFal 硬拦 hook（2026-07-13 已装并实测生效）**：`~/.claude/hooks/block_grfal.py`（PreToolUse，注册在用户 settings.json），双开关=会话ID在 `~/.claude/hooks/grfal_ban_sessions.txt` 名单 OR cwd 含 avatar-replace 才生效，其他日常会话用 grfal 不受影响。拦 call_grfal/grfal域名/内网IP/Skill grfal-api与x3-media*/Agent media-worker。**新开 avatar-replace 平行会话**：从 `C:\ADHD_agent\avatar-replace\` 目录启动即自动带防护；否则把新会话ID加进名单。

**当前状态（2026-07-13 晚）**：✅ **P1 管线核心已完成**（子代理驱动 10 组任务全过，33 tests passed，全程零 GRFal/零真实调用）。代码在 `C:\ADHD_agent\avatar-replace\`（core 8 模块 + CLI + 30+ 测试），~25 个 commit 全在 ADHD 仓 main、只含本目录。
- **API 契约已按官方 SDK 源码核对并修正**（role 字段/顶层生成参数/expired 状态/仅 Seedance 2.0 支持参考视频）；`generate_audio:false` 省钱（音轨走原片铺回）。
- **终审最大收获=C1**：Seedance 产出段与本地切段参数不同，concat -c copy 必出坏片，FakeProvider 测试掩盖了这条接缝——已内置归一化（`stitch.py` 对所有 replace 段重编码回源片分辨率/fps）。教训：**mock 测试的结构性盲区要靠"异质输入"回归测试补**（test_stitch_normalizes_foreign_replace_segment）。
- **下一步**：①用户开通火山方舟拿 ARK_API_KEY → 按 `docs/SMOKE.md` 冒烟（头号验证项=参考视频 base64 可能不支持、仅公网 URL；②真人人脸风控）②效果过关后再排 P2 Web壳 / P3 形象库 / P4 部署形态。

相关 [[reference_grfal_implementation]]（架构参考来源，仅借鉴设计不调用）
