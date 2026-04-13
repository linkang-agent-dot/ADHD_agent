"""精炼版AI日报 — 300字以内，面向小白"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.cursor\skills\async-notify\scripts')
import importlib
import feishu_helper
importlib.reload(feishu_helper)

report = """\
🤖 AI 提效日报 | 4月2日

📊 今日概况
  后台运行 24h，自动完成 13 个任务，失败 4 个（模型服务临时故障）

🔑 重点任务
  1. 千川AI接入调研 → 结论：无官方API，走飞书机器人转接最省事
  2. 高频AI工作流盘点 → 梳理出11个可复用场景，导表/翻译/数据查询提效30-55%
  3. 外部系统接入方案 → 统一走飞书触发，不用写接口
  4. Daemon自动修复 → 心跳bug+模型额度爆了自动切备用模型

💡 一句话总结
  飞书发一句话，AI后台自动跑完出结果——今天验证了这条链路能稳定跑通。"""

token = feishu_helper.get_token()
resp = feishu_helper.send_text(report, token, verify=True)
print(f'code={resp.get("code")}, garble={resp.get("_garble_detected", False)}')
print(f'字数: {len(report)}')
