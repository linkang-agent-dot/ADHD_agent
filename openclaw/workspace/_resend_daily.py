"""直接用 Python 写日报并发飞书，绕过 PowerShell 管道编码问题"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.cursor\skills\async-notify\scripts')
import importlib
import feishu_helper
importlib.reload(feishu_helper)

report = """\
🤖 AI 提效日报 | 4月2日（周四）

▌ 今日 AI 帮你干了这些事

  #  |  场景  |  省了多少  |  亮点
  1  |  Daemon 心跳 bug 修复  |  省30分钟手动排查  |  从「挂了自己改代码重启」→「10分钟定位修好」
  2  |  模型额度/故障双重fallback  |  省15分钟人工重试  |  触发usage limit也会自动换auto模型重试
  3  |  飞书通知格式升级  |  省每次阅读混乱感  |  markdown自动清洗、截断200→1500字
  4  |  千川AI接入路径调研  |  省1小时搜索翻文档  |  3分钟得出：无官方API，走低代码平台或飞书机器人最稳
  5  |  OpenClaw外部系统接入方案  |  省半天方案讨论  |  结论：统一走飞书机器人触发虾哥，最省事
  6  |  游戏内高频AI工作流盘点  |  省人工整理  |  P2导表/X2下载/GSheet替换/本地化 提效30-55%

▌ Top3 最值得复用的场景

▷ 1. 模型故障自动fallback
一句话：主模型挂了或额度爆，自动切到auto重试，不需要你手动管
怎么用：在飞书给虾哥发任务时加 model:gpt-4o 可以直接指定非Sonnet模型
适用：所有通过daemon跑的AI任务

▷ 2. 千川无API → 低代码平台代替
一句话：千川没有官方开放API，但数环通/集简云支持无代码连接千川数据流
怎么用：去数环通配置「千川→飞书/钉钉」触发，不需要写代码
适用：想监控千川广告数据、自动发报的同学

▷ 3. 飞书机器人作为外部系统统一入口
一句话：任何外部系统（千川/竞品工具/定时任务）只要能发飞书消息，就能触发AI执行
怎么用：配置飞书机器人webhook，把信息发进来，虾哥自动路由给Cursor执行
适用：想接更多数据源但不想写接口的场景

▌ 今日小心得
  • 「挂了」不一定是进程死了，可能只是日志不打了——elapsed%60 这种整除判断在5s步长下会跳过，改成计时器方式稳多了
  • 飞书消息里的粗体和标题直接发出来都是符号，要做一次markdown清洗才好看
  • Sonnet额度是按月算的，月底容易爆，提前备好fallback模型很必要
"""

token = feishu_helper.get_token()
resp = feishu_helper.send_text(report, token)
print(f'飞书响应: code={resp.get("code")}, msg={resp.get("msg","")}')
msg_id = resp.get('data', {}).get('message_id', '')
print(f'message_id: {msg_id}')

if resp.get('code') == 0 and msg_id:
    import requests, json
    verify_url = f'https://open.feishu.cn/open-apis/im/v1/messages/{msg_id}'
    r = requests.get(verify_url, headers={'Authorization': f'Bearer {token}'}, timeout=10)
    vdata = r.json()
    body = vdata.get('data', {}).get('items', [{}])[0].get('body', {}).get('content', '')
    text = json.loads(body).get('text', '')
    print('\n=== 飞书端实际内容（前300字）===')
    print(text[:300])
    if '鎻' in text or '馃' in text:
        print('\n❌ 仍然存在乱码！')
    else:
        print('\n✅ 内容正常，无乱码')
