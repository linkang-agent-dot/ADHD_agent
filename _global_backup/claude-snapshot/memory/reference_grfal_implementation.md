---
name: reference_grfal_implementation
description: GRFal 怎么实现的 + 内部 prompt 在哪一层；问 grfal/Morphix 实现、内部提示词、换皮 prompt 先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 34a4cf7b-da6b-468b-b275-af988c306362
---

公司 **GRFal** = 内网自建 **AI 媒体能力网关**，三层架构：
- **① 客户端层**（你机器上）：`~/.claude/skills/grfal-api/scripts/call_grfal.py`，纯 urllib HTTP 壳子，**无任何 prompt/AI 逻辑**，只做文件→base64 转发 + token 管理(device flow,access 12h/refresh 30d) + 域名故障回退(切内网 IP 172.20.90.45:6018)。
- **② 服务端层**：内网 `grfal.tap4fun.com`→代理→后端 6018，gradio.Server 注册 ~78 个 `@tool`(对外约53,真值=`GET /api/tools`)。**自己不造模型**，转发外部商业后端(FAL gpt-image-2/阿里百炼/即梦豆包seadance/happyhorse/ElevenLabs/MiniMax/Tripo/Hunyuan)+本地后处理(ffmpeg/PIL/色键/SBS)。
- **③ 外部模型后端**：真正出活的模型。

**内部 prompt 在哪 = 全在服务端工具内部**(客户端没有)，三类：① 工具自带写死 prompt(如 `face_swap` 缺省换头模板,全文在文档)；② LLM 驱动中间步骤(`aspect_ratio=auto`推比例 / `video_inpainting`+`video_remove_watermark` LLM 找物体 / `seedance_prompt_reverse` 两遍LLM反推 / `describe_media` / `screenshot_localization` / `pdf_enhancement`)；③ `creative_workflow` 多步管线(sprite_sheet/storyboard_expand/p2_*_design 等,每个 tool_id 一整套精调 prompt;admin 不暴露的更重:comic_/drama_/cf_*)。

**Morphix**(`demo.tap4fun.com/morphix-demo_0e8f`)=GRFal 的**应用层**换皮网页,无独有能力,只调 generate_image/describe_media/remove_background 3 个工具,价值=精调 prompt+多步编排。

**唯一入口文档**(架构+内部prompt清单+prompt设计7模式+Morphix 8段build*Prompt全文已整段内嵌)：
`C:\ADHD_agent\KB\方法论\GRFal工具实现与内部Prompt逻辑总览.html`（分7页签,本地打开）。
逆向源(更细 app.js 流程图)：同目录 `Morphix换皮工具逆向_prompt库.html` + `Morphix_prompt中文注释版.html`。

prompt 设计模式提炼(做图像换皮/编辑直接套)：①双参考图职责切分(图#1布局/图#2视觉) ②ERASE铁律逐项点名要擦的视觉特征 ③先describe文本化风格再批量generate ④灰底#B8B8B8非白底防白边 ⑤线框中文标注翻译成实渲 ⑥节日换皮抄"主题转换"段(唯一放飞,文字逐字保留) ⑦参考图能说明的别在prompt里说。黑名单:X3 "painterly/笔触"永久BAN。

**Morphix 模版库决策(2026-06-25,别再追)**：Morphix 预置模版系统=分类参考图库+stylePrompt,逆向只拿到 stylePrompt 文本,**那套分类参考图库在 Morphix 服务器上、本地没有、决策不去拿**(走自建)。原因:① X16/X17 不是我方项目抄了没用 ② 模版库本就该按自己项目建。自建料=X3 Spirits 6353张PNG(`C:\x3-project\client\Assets\Res\UI\Spirits`)+6034交互库,按7元素槽(character/scene/screen/panel/widget/icon/frame)挑代表图配stylePrompt,真要模版化再建。**当前换皮无需任何图库**:单次换皮直接喂 reference_images=[图#1布局,图#2手头风格图] 走 buildReskinPrompt 即可。注:Morphix 是网页前端明文JS(prompt 就这么读出的,非反编译),后端就是 GRFal 无独有逻辑——反编译服务器拿不到新东西。

相关 [[morphix-prompt]] [[reference_x3_media_skill_location]] [[workflow_x3_grfal_generate_image]] [[project_x3_hero_skin_video]]。

## 🎬 视频工具矩阵 + 特殊能力(2026-07-08 补,总览HTML已加「🎬视频工具矩阵」页签)
GRFal **无时间轴剪辑器**,视频=AI工具(外部模型)+本地ffmpeg。**杀手锏(别处没有/极省事)**:
- **seadance 视频编辑**(generate_video ref_types=参考视频+元素参考):**只换物体、运镜全保留**,prompt「把视频1的X换成图片1的Y运镜不变」——传统剪辑做不到。
- **seadance 视频延展/拼接**(ref_types=参考视频×N):多段clip+转场描述→**AI生成过渡帧缝成连续视频**(非硬切)。
- **seadance 音频参考克隆**(ref_types含参考音频,仅seadance):克隆音色/旋律/对白,单请求混最多9图+3视频+3音频。
- **video_inpainting / video_remove_watermark**:**免画mask**——LLM看首帧定位物体/水印→Bria eraser逐帧擦。
- **seedance_prompt_reverse**:喂现成视频两遍分析反推带时间戳prompt`[0-2s]…`回喂重生成。
- **export_sbs_video**⭐:导左右分屏透明视频给Unity(彩色半+alpha半),皮肤视频链路关键,**本地ffmpeg不走模型**。
- **数字人三件套**:video_avatar(音频驱动图说话)/video_lipsync(对口型latentsync高质/lipsync快)/video_portrait(视频驱动动作迁移)。
- generate_video 6模式:文生/首帧i2v/首尾帧fflf/元素参考/fflf+元素(Kling)/参考视频v2v/参考音频。模型:seadance最全能·happyhorse阿里百炼·kling·vidu/grok/veo3/sora/wan/runway/hailuo。

## 🏠 脱离GRFal「走A直连商业API」= 要重建哪些内置逻辑(2026-07-08)
**核心认知:GRFal不是纯代理,模型外裹4层胶水**。裸API=裸模型,这4层要么自建要么结果打折:
1. **①前处理Prompt工程**(face_swap换头/Morphix 8段build*Prompt/creative_workflow各管线)→🟢已全逆向,总览HTML复制即用。裸prompt结果明显更糙(串味/白边/不换轴)。
2. **②LLM中间步骤(agentic)**(aspect_ratio=auto推画幅/擦除去水印LLM首帧定位/prompt_reverse/describe_media)→🟡要自己在流程里加一次GPT/Gemini调用补前置判断。
3. **③本地后处理(确定性)**(ffmpeg SBS拼接/H.264压缩/抽帧·PIL resize色键·rembg抠图·LaMa擦除·base64·URL下载·异步轮询)→🟢基本白送,本来就是本地活,家里照搬零损失。
4. **④多步编排管线**(图标=describe榨风格→批量generate·元素拆分=灰底雪碧图→去底→连通域切→分类→打包·creative_workflow)→🟡步骤已逆向(总览HTML E/C段有流程图),照着chain。
**走A真实工作量≈写个薄本地编排层(~200行Python)**:调Kling/fal封装+复制build*Prompt+ffmpeg/PIL/rembg后处理+补1-2处LLM前置判断+串流水。裸模型出活,这层把结果做「对」。
**家用平替栈(A2000 4-12G+32G RAM现实版)**:本地能跑=出图(ComfyUI+Flux/SDXL量化)/抠图(rembg已有.u2net)/超分(Real-ESRGAN)/擦除(ProPainter平替Bria)/口型(LatentSync/Wav2Lip)/图片说话(LivePortrait)/SBS+拼接+压缩+抽帧(纯ffmpeg零损失)/VLM(Ollama+Qwen2-VL)/TTS克隆(GPT-SoVITS/F5-TTS);**跑不动认命买API**=重型视频生成(Wan/Hunyuan本地跑不动)+seadance视频编辑延展→Kling/即梦/Runway/fal开放平台(GRFal背后也是这些,脱不脱离都掏这钱)。

## 🎬 video_compression 压视频到目标大小（2026-07-01 实操踩坑）
用 GRFal 把视频压到指定 KB 区间时，两个坑先知道，省得从头试：
- **⚠️参数名坑**：skill 文档写 `--file video_file=path`（单数）会报「缺少必需参数 video_files」——**服务端真实参数是 `video_files`（复数）**。用 `--file video_files=<path>`。（文档待修）
- **CRF 不能直接定大小**（H.265/HEVC，crf 0-51 越高越小），要**试 2-3 版收敛**。经验换算：**crf 每 +6 ≈ 码率 ×0.5**；`max_height` 降一档（1080→720）≈ 像素 ×0.44。两者叠乘估目标。
- **实测锚点**（源 12.5MB / 2160×1920 SBS / 24fps / 15s）：crf30@1080p=2.25MB → crf36@720p=690K → **crf38@720p=555K**（命中 300-600K）。要压到 300-600K 这种 ~20-40× 比，基本要 720p + crf 36-40。
- **命令**：`python "~/.claude/skills/grfal-api/scripts/call_grfal.py" --tool video_compression --file video_files=<in> --params '{"crf":38,"preset":"slow","max_height":720,"audio_bitrate":"32k"}'`（视频类走后台异步，返 task_id，轮询 `--check-task <id>`；轮询循环要 `while grep -q '"status": "\(running\|pending\)"'` 别用 grep -qv，多行 JSON 会误退）。结果是 URL，`curl -sk` 下载。
- **⚠️SBS 皮肤视频专属风险**：SBS=左右半（彩色半+alpha遮罩半），激进压缩块效应会让 alpha 边缘渗色/黑边→进游戏抠图不干净。质量吃紧时回退 crf36（略超但稳）或只对 alpha 半区保质量。视频皮肤资源链见 [[project_x3_hero_skin_video]]。
- **进包替换姿势**（压完换回 Unity 仓，2026-07-01）：Unity 资源替换=**只覆盖文件内容(mp4/png)、绝不动同名 `.meta`**（.meta 存 GUID，动了引用全断；git status 应只有资源那一行 M、无 .meta）。资源是 git-tracked 就自带兜底（`git checkout -- <path>` 还原），仍另存一份原文件备份防 reset。⚠️**先 `git branch --show-current`**：世界杯资源只该落 dev_festival，别 commit 进当时 checkout 的无关在途分支（本次仓在 `dev-guide-academy-fallback`+22 脏文件→只改工作树不 commit，提交待用户定分支）。

## 🔴 纠错：X3 仓库视频压缩用官方脚本，别用 grfal(2026-07-01)
上面 grfal `video_compression` 段**只适用于「一次性/非进仓」视频**。**要压缩后 commit 进 X3 client 仓的视频，必须用官方脚本**，否则过不了 pre-commit 视频 gate：
- **gate**：`C:\x3-project\.githooks\video_policy.json` 强制 `.mp4/.m4v/.mov`=**H.264**、≤1080p(竖版≤2160×1920)、≤30fps、`yuv420p`、音频 aac/opus、码率≤6000kbps(软约束)。**grfal 出的是 H.265/HEVC → 直接被 gate 拒**。
- **官方脚本**：`C:\x3-project\client\Tools\VideoTools\compress_video.py`(自带 `ffmpeg/`)。用法 `python compress_video.py -i <文件或目录> [--crf 28] [--height 1080] [--fps 30] [--preset slower] [--audio-bitrate 64k]`。默认参数就对齐 video_policy(H.264/1080p/30fps/yuv420p/aac)→压完即可过 gate。
- **默认自动备份**原片到 `~/video_compress_backup/<名>_<时间戳>.mp4` 再 in-place 覆盖原路径(`--no-backup` 关)；目录输入=批量压 mp4/mov/m4v/webm。webm 走 VP9。
- **🔴双重压缩坑(2026-07-01 踩)**：脚本 in-place 覆盖→**若对已压过的文件再跑=二次有损**(画质更差、体积可能反增)。**必须始终从真原片压**；重压前先确认 `stat -c%s` 是原始大小，不是则从 `~/video_compress_backup` 或 git 还原真原片再压。多次试 crf 用 scratchpad 拷贝(`--no-backup`)非破坏性试，别在仓库文件上反复 in-place。
- **实测(足球宝贝 SBS 2160×1920/24fps/15s/12.5MB)**：默认 crf28→**1.96MB/1216×1080/H.264/1040kbps**(合规,~6.4×)；要更小 720p+高crf：`--height 720 --crf 34`=600K / `--crf 40`=347K(H.264 比 grfal H.265 同 crf 大,想进 300-600K 用 720p+crf34~40)。视频皮肤链见 [[project_x3_hero_skin_video]]。
- **🔴共享 checkout 工作树不稳踩坑(2026-07-01)**：在有并发 agent 的共享仓(如 `dev-guide-academy-fallback`)上,in-place 压好的文件**会在回合之间被别的进程 `git checkout`/还原掉**。据「上回合已压好」的记忆直接 `cp` 去存档→把还原后的**原片当压缩版存错、还覆盖了正确标签**。**铁律=每次 cp/存档/进仓前必 `stat -c%s` 核实是不是你要的那版**(压缩版 vs 原片字节数),别信"上回合的状态还在"。且**压缩定稿要立刻落到 KB durable 存档**(别只留在共享仓工作树,回合间会丢);进仓统一在最终分支从 KB 存档 cp。足球宝贝定稿=`KB\产出-本地化与美术\X3\世界杯宣传图\足球宝贝爱莉希雅\足球宝贝皮肤视频_官方压缩_H264_1080p_FINAL_待进包.mp4`(1.96M H.264)。
