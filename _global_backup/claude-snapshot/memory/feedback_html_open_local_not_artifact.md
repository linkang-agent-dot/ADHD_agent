---
name: feedback-html-open-local-not-artifact
description: "HTML 产物(验收清单/报告/原型/甘特)一律直接 start 本地打开,永远不发 Artifact/不开 claude.ai 界面"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a91692dc-7cc0-45e6-bf6b-ae69a3977fb7
---

用户要求：**做好的 HTML（验收清单 / 报告 / 交互原型 / 甘特 / 任何 .html 产物）一律用 `start "" "<路径>"` 直接在本机默认浏览器打开，永远不要发 Artifact、不要让用户开 claude.ai 的界面。**

**Why**：用户在本机工作，本地浏览器打开即看即用；Artifact 要跳 claude.ai 网页，多一道、还要登录，用户嫌烦。2026-06-23 深海节验收清单明确提出「直接打开 html，后面永远不开 claude 的界面」。

**How to apply**：
- HTML 写完/更新后，直接 `start "" "<绝对路径>"`（Git Bash 里 `start` 可用）打开。
- **不再调 Artifact 工具**渲染 HTML 给用户（除非用户明确要分享链接给teammate）。
- 仍正常把 HTML 归档到 KB 固定路径（产物归档不变，见 [[reference_output_paths]]），只是「给用户看」的方式改成本地打开。
