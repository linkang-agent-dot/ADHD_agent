# 防晒衣素材雷达 POC｜运行手册

## 当前结论

本目录是可复跑的抖音单平台技术 POC。当前主榜是 10 条真人商品短口播，实测时长 20.6～44.4 秒，均已取得完整本地视频，并完成全片定频抽帧、本地转写、人工复核和时间轴。主榜数据真源为 `_references/selected_10.json`；旧 5 条与后续落选候选均保留作研究证据，不混入主榜。

主榜入选门槛同时满足：真人出镜；围绕商品持续讲解；优先 15～60 秒。纯穿搭蒙太奇、产品空镜、AI 数字人和 90 秒以上长测评只进研究池。天镜消耗尚未接入，当前页面不根据点赞伪装跑量结论。

当前产品化只推进“选品引擎”：先确认候选来源、商品与视频的对象关系、天镜/罗盘字段及最小入选规则，再把入选商品交给素材雷达深拆。唯一入口是 `08A_选品引擎_范围与验证清单.md`；更大的“选品与投放判断台”仅保留为 BACKLOG，暂不推进。

下游“参考视频换商品并制作成片”已独立为正式 Skill：`C:\ADHD_agent\.agents\skills\ecommerce-video-reskin\SKILL.md`；当前机器的可调用安装位为 `C:\Users\linkang\.agents\skills\ecommerce-video-reskin\`。素材雷达只交付候选原片、完整视频证据和结构拆解；新 Skill 负责完整痛点分段、骨皮映射、关键帧、分段生成、原声后期、QC与成本。旧 `remake_attempt*` 只作为实证和反例，不再复制其时间线式流程。

## 新 Agent 最短运行路径

在项目根目录执行：

    python scripts\build_dashboard.py
    python scripts\check_structure.py

`check_structure.py` 必须通过：它验证 10 条唯一 URL、15～60 秒时长门槛、本地视频、转写、时间轴、图片内嵌和天镜“待接入”口径。

## 获取与深拆链路

1. 从公开抖音详情/分享页记录稳定 URL、账号、标题、时间、指标与截图。
2. `douyin_public_share_fetch.py <视频ID> --provider bugpk --download-route proxy --output <元数据JSON> --download <本地MP4>` 解析公开详情并下载到 `_references/media_authorized`；不读取或导出浏览器 Cookie。
3. `build_local_video_evidence.py --media-dir <媒体目录> --output-dir <证据目录> --mode all --model small --ids <素材ID>` 用本机 PyAV / faster-whisper 生成全片定频帧、联系表和转写，全部留在本机。
4. 人工交叉核对画面、烧录字幕与转写，只有同时满足真人、商品持续讲解和短时长门槛的样本写入 `_references/selected_10.json`。
5. 重跑 `build_dashboard.py` 和 `check_structure.py`，生成并验证自包含 HTML。

## 数据与风控边界

- 个人内容及本项目素材不得上传或提交到公司网络、公司 GRFal、公司 worker 或任何公司媒体接口。
- 可以在本机只读学习已安装公司工具的 Prompt、参数设计和实现逻辑，但不得发送内容或创建远程任务。
- 不绕过登录、验证码、频控、付费权限或平台安全策略；不导出 Cookie，不去水印，不批量转载。
- 第三方公开解析回退不是稳定 SLA；失败时记录状态并停止，不切公司服务兜底。

## 排序与扩品

- `ranking_rules.json` 是候选排序真源；点赞只作为外部内容信号，不解释为销量、GMV、ROI 或利润。
- 可直接复用：稳定 ID、去重、本地证据生成、JSONL、规则排序、报告和看板。
- 扩到第二个服装品时必须重校准：搜索词、内容标签、证明动作、功效风险、深拆规则和排序权重。
