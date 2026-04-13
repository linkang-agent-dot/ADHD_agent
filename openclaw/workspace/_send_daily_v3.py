"""精炼版AI日报 v3 — 含小红书AI热点 + GitHub AI趋势"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.cursor\skills\async-notify\scripts')
import importlib
import feishu_helper
importlib.reload(feishu_helper)

report = """\
🤖 AI 提效日报 | 4月2日

📊 今日概况
后台运行 24h，自动完成 13 个任务，失败 4 个（模型临时故障自动重试）

🔑 重点任务
1. 千川AI接入调研 → 无官方API，走飞书机器人转接最省事
2. 11个高频AI工作流盘点 → 导表/翻译/数据查询提效30-55%
3. Daemon自修复 → 心跳bug+额度爆了自动切备用模型，零人工干预

🔥 小红书AI热点 Top1
「火兔工具箱」综合评分99.2，新手10分钟上手，笔记曝光提升230%。一键采集爆款+智能排版+违禁词检测，覆盖18个赛道。

⭐ GitHub AI趋势 Top1
OpenAI Agents Python SDK（20.5k星）4月1日刚更新v0.13.4，轻量多Agent框架，几行代码跑起Agent协作流水线。

💡 一句话
飞书发一句话，AI后台自动跑完出结果——今天验证了这条链路能稳定跑通。"""

token = feishu_helper.get_token()
resp = feishu_helper.send_text(report, token, verify=True)
print(f'code={resp.get("code")}, garble={resp.get("_garble_detected", False)}')
print(f'字数: {len(report)}')
