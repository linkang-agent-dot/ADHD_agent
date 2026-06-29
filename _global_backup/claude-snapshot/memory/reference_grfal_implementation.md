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

相关 [[morphix-prompt]] [[reference_x3_media_skill_location]] [[workflow_x3_grfal_generate_image]]。
