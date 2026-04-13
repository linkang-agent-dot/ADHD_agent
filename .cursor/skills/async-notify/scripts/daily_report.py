"""
daily_report.py — AI 提效日报自动生成

用法：
  python daily_report.py                  # 生成今天的日报
  python daily_report.py --date 20260401  # 指定日期

流程：
  1. 从本地 inbox/outbox 采集当日任务统计
  2. 从 daemon 日志提取运行时长
  3. 调用 GitHub API 获取 AI 趋势 Top1（带链接）
  4. 构造 agent 任务提交给 daemon，让 agent 用 WebSearch 查小红书 AI 热点
  5. daemon 执行后把结果发飞书

也可以直接 --send-now 模式：跳过 daemon，直接发飞书（需要 agent CLI 在线）
"""
import argparse
import json
import os
import re
import sys
import uuid
import requests
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

INBOX_DIR = r'C:\ADHD_agent\openclaw\workspace\cursor_inbox'
OUTBOX_DIR = r'C:\ADHD_agent\openclaw\workspace\cursor_outbox'
LOG_FILE = r'C:\ADHD_agent\openclaw\workspace\daemon_autoexec.log'
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, SCRIPTS_DIR)


def collect_task_stats(date_str: str) -> dict:
    """从 inbox/outbox 采集指定日期的任务统计"""
    prefix = f'task_{date_str}'
    total = 0
    done = 0
    error = 0
    done_titles = []

    for f in sorted(os.listdir(INBOX_DIR)):
        if f.startswith(prefix) and f.endswith('.json') and not f.startswith('_'):
            total += 1
            try:
                with open(os.path.join(INBOX_DIR, f), 'r', encoding='utf-8') as fp:
                    d = json.load(fp)
                st = d.get('status', '')
                title = d.get('title', f)
                if st == 'done':
                    done += 1
                    done_titles.append(title)
                elif st == 'error':
                    error += 1
            except Exception:
                pass

    return {
        'total': total,
        'done': done,
        'error': error,
        'done_titles': done_titles,
    }


def collect_daemon_hours(date_str: str) -> str:
    """从 daemon 日志提取当日运行区间"""
    date_fmt = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}'
    try:
        lines = open(LOG_FILE, 'r', encoding='utf-8', errors='replace').readlines()
        today = [l for l in lines if date_fmt in l]
        if not today:
            return '无日志'
        first = re.search(r'(\d{2}:\d{2})', today[0])
        last = re.search(r'(\d{2}:\d{2})', today[-1])
        if first and last:
            return f'{first.group(1)} ~ {last.group(1)}'
    except Exception:
        pass
    return '未知'


def fetch_github_trending() -> str:
    """调用 GitHub API 获取最近一周 AI 热门仓库 Top1，返回带链接的文本"""
    try:
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = 'https://api.github.com/search/repositories'
        params = {
            'q': f'AI agent OR LLM tool pushed:>{week_ago} stars:>1000',
            'sort': 'updated',
            'order': 'desc',
            'per_page': 5
        }
        r = requests.get(url, params=params, timeout=15,
                         headers={'Accept': 'application/vnd.github.v3+json'})
        items = r.json().get('items', [])
        if not items:
            return '暂无数据'

        # 取第一个非"awesome-list"类的仓库
        for item in items:
            name = item['full_name']
            if 'awesome' in name.lower():
                continue
            stars = item['stargazers_count']
            desc = (item.get('description') or '')[:60]
            link = item['html_url']
            updated = item.get('pushed_at', '')[:10]
            stars_k = f'{stars/1000:.1f}k' if stars >= 1000 else str(stars)
            return f'{name}（{stars_k}⭐，{updated}更新）\n{desc}\n{link}'

        item = items[0]
        return f'{item["full_name"]}（{item["stargazers_count"]}⭐）\n{item["html_url"]}'
    except Exception as e:
        return f'GitHub API 异常: {e}'


def build_agent_task(date_str: str, stats: dict, daemon_hours: str, github_info: str) -> dict:
    """构造提交给 daemon 的 agent 任务 JSON"""
    date_fmt = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}'
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    try:
        dt = datetime.strptime(date_str, '%Y%m%d')
        weekday = weekdays[dt.weekday()]
    except Exception:
        weekday = ''

    top_tasks = stats['done_titles']
    top_tasks_text = '\n'.join(f'  - {t}' for t in top_tasks) if top_tasks else '  （无）'

    # 算月日
    month = int(date_str[4:6])
    day = int(date_str[6:])
    date_display = f'{month}月{day}日'

    instructions = f"""你是 AI 提效日报编辑。根据下面的数据 + WebSearch 搜索结果，输出一份精炼日报。

【本地数据（直接使用，不要修改数字）】
日期: {date_display}（{weekday}）
后台运行区间: {daemon_hours}
任务: 共{stats['total']}个，完成{stats['done']}，失败{stats['error']}
完成的任务:
{top_tasks_text}

GitHub AI 趋势 Top1（已查好，直接用）:
{github_info}

【需要你搜索的——小红书 AI 热点】
用 WebSearch 搜索「小红书 AI提效工具 2026」，找 1 条最火的内容。
要求：标题 + 一句话 + 链接（优先 xiaohongshu.com，搜不到就写「搜索"小红书 AI工具"」，禁止编URL）

【输出规则】
1. 直接输出下面的格式，第一个字必须是🤖，禁止任何前言/解释/附言
2. 从完成的任务中挑 3 个最有实际产出的（优先选调研报告、配置生成、bug修复、方案输出，跳过纯查询类）
3. 每个任务一句话总结它的价值，不超过20字
4. 一句话总结不超过30字
5. 全文300字以内

🤖 AI 提效日报 | {date_display}（{weekday}）

📊 后台运行 {daemon_hours}，完成 {stats['done']} 个任务，失败 {stats['error']} 个

🔑 重点任务
1. 任务名 → 价值
2. 任务名 → 价值
3. 任务名 → 价值

🔥 小红书 AI 热点
标题 + 说明 + 链接

⭐ GitHub AI 趋势
{github_info}

💡 一句话总结"""

    now = datetime.now()
    task_id = f'task_{now.strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:6]}'
    return {
        'task_id': task_id,
        'title': f'AI提效日报-{date_fmt}',
        'instructions': instructions,
        'submitted_by': 'DailyReport',
        'submitted_at': now.strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending',
        'priority': 'normal',
    }


def submit_to_daemon(task: dict):
    """写入 inbox 目录，等待 daemon 自动执行"""
    path = os.path.join(INBOX_DIR, f'{task["task_id"]}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    print(f'[daily_report] 任务已提交: {task["task_id"]}')
    print(f'[daily_report] 等待 daemon 自动执行并发飞书')


def send_now(stats: dict, daemon_hours: str, github_info: str, date_str: str):
    """跳过 daemon，直接用已有数据生成并发飞书（无小红书搜索）"""
    import feishu_helper
    date_fmt = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}'
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    try:
        dt = datetime.strptime(date_str, '%Y%m%d')
        weekday = weekdays[dt.weekday()]
    except Exception:
        weekday = ''

    top3 = stats['done_titles'][:3]
    tasks_block = ''
    for i, t in enumerate(top3, 1):
        tasks_block += f'  {i}. {t}\n'

    report = f"""🤖 AI 提效日报 | {date_fmt}（{weekday}）

📊 后台运行 {daemon_hours}，完成 {stats['done']} 个任务，失败 {stats['error']} 个

🔑 重点任务
{tasks_block}
⭐ GitHub AI 趋势
  {github_info}

💡 （小红书热点需通过 daemon 模式生成，当前为快速模式）"""

    token = feishu_helper.get_token()
    resp = feishu_helper.send_text(report, token, verify=True)
    ok = resp.get('code') == 0
    garble = resp.get('_garble_detected', False)
    print(f'[daily_report] 飞书发送: {"成功" if ok else "失败"}, 乱码检测: {garble}')


def main():
    parser = argparse.ArgumentParser(description='AI 提效日报自动生成')
    parser.add_argument('--date', type=str, default=None,
                        help='日期 YYYYMMDD，默认今天')
    parser.add_argument('--send-now', action='store_true',
                        help='跳过 daemon 直接发飞书（无小红书搜索）')
    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime('%Y%m%d')
    print(f'[daily_report] 生成日期: {date_str}')

    stats = collect_task_stats(date_str)
    print(f'[daily_report] 任务统计: 总{stats["total"]} 完成{stats["done"]} 失败{stats["error"]}')

    daemon_hours = collect_daemon_hours(date_str)
    print(f'[daily_report] daemon运行: {daemon_hours}')

    github_info = fetch_github_trending()
    print(f'[daily_report] GitHub: {github_info[:80]}...')

    if args.send_now:
        send_now(stats, daemon_hours, github_info, date_str)
    else:
        task = build_agent_task(date_str, stats, daemon_hours, github_info)
        submit_to_daemon(task)


if __name__ == '__main__':
    main()
