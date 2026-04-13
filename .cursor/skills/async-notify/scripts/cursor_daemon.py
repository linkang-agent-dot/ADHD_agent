"""
cursor_daemon.py — Cursor 后台任务守护脚本

两种模式：
  A. 传统模式（默认）：发现任务 → 打印到 stdout → 等待 Cursor Agent 手动读取
  B. 自动执行模式（--auto-execute）：发现任务 → 调用 Cursor Agent CLI 执行 → 写结果 → 飞书通知 → 循环

自动执行模式要求预先安装 Cursor Agent CLI：
  irm 'https://cursor.com/install?win32=true' | iex
  agent login
"""
import argparse
import shutil
import subprocess
import sys
import os
import json
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

INBOX_DIR  = r'C:\ADHD_agent\openclaw\workspace\cursor_inbox'
OUTBOX_DIR = r'C:\ADHD_agent\openclaw\workspace\cursor_outbox'
RESTART_FLAG = r'C:\ADHD_agent\openclaw\workspace\cursor_daemon_restart.flag'
WORKSPACE  = r'C:\ADHD_agent'
NOTIFY_DONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notify_done.py')
POLL_INTERVAL = 5   # 秒
TASK_TIMEOUT  = 1800  # 单个任务最长执行时间（秒）
AGENT_CMD = None      # 运行时解析：优先 node.exe 直接调用，跳过 .CMD/.ps1 包装层
AGENT_NODE = None     # node.exe 路径
AGENT_INDEX = None    # index.js 路径
DEFAULT_MODEL = None  # 全局默认模型（可被任务级 model 覆盖）
LOG_FILE = os.path.join(os.path.dirname(INBOX_DIR), 'daemon_autoexec.log')


def _log(msg: str):
    """同时写 stdout 和文件日志，避免 PowerShell 重定向吞输出。"""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    try:
        print(line, flush=True)
    except Exception:
        pass
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def _auto_repair(task: dict, fname: str, path: str) -> bool:
    """修复缺 task_id / status 的畸形入队 JSON，返回是否做了修改。"""
    changed = False
    if 'task_id' not in task or not task['task_id']:
        task['task_id'] = fname.removesuffix('.json')
        changed = True
    if 'status' not in task or not task['status']:
        task['status'] = 'pending'
        changed = True
    if 'submitted_at' not in task or not task['submitted_at']:
        task['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        changed = True
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        _log(f'🔧 自动修复畸形任务 {fname} → task_id={task["task_id"]}, status={task["status"]}')
    return changed


def scan_inbox() -> dict | None:
    """扫描 inbox 目录，返回最早的 pending 任务，没有则返回 None。
    遇到缺 task_id / status 的 JSON 会自动补全后标为 pending。"""
    if not os.path.exists(INBOX_DIR):
        return None
    files = sorted([
        f for f in os.listdir(INBOX_DIR)
        if f.endswith('.json') and not f.startswith('_')
    ])
    for fname in files:
        path = os.path.join(INBOX_DIR, fname)
        try:
            # 尝试 utf-8，失败则 fallback 到 gbk（OpenClaw Windows 侧可能用 GBK 写入）
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    task = json.load(f)
            except (UnicodeDecodeError, json.JSONDecodeError):
                with open(path, 'r', encoding='gbk', errors='replace') as f:
                    task = json.load(f)
        except Exception:
            continue
        if not task.get('title') and not task.get('instructions'):
            continue
        _auto_repair(task, fname, path)
        if task.get('status') == 'pending':
            return task
    return None


def mark_processing(task: dict):
    """将任务标记为 processing，防止重复领取"""
    path = os.path.join(INBOX_DIR, f'{task["task_id"]}.json')
    task['status'] = 'processing'
    task['picked_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)


def _build_prompt(task: dict) -> str:
    """将 inbox JSON 拼装成给 Agent CLI 的 prompt 字符串。"""
    parts = []
    if task.get('title'):
        parts.append(f'任务：{task["title"]}')
    if task.get('instructions'):
        parts.append(f'\n{task["instructions"]}')
    if task.get('context'):
        parts.append(f'\n背景信息：{task["context"]}')
    return '\n'.join(parts) or task.get('title', '执行任务')


def _write_result(task: dict, status: str, result_text: str):
    """写 outbox 结果 + 更新 inbox 状态。"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    outbox_data = {
        'task_id': task['task_id'],
        'title': task.get('title', ''),
        'status': status,
        'result': result_text[:2000],
        'completed_at': now,
    }
    outbox_path = os.path.join(OUTBOX_DIR, f'{task["task_id"]}.json')
    with open(outbox_path, 'w', encoding='utf-8') as f:
        json.dump(outbox_data, f, ensure_ascii=False, indent=2)

    inbox_path = os.path.join(INBOX_DIR, f'{task["task_id"]}.json')
    task['status'] = status
    task['completed_at'] = now
    with open(inbox_path, 'w', encoding='utf-8') as f:
        json.dump(task, f, ensure_ascii=False, indent=2)


def _send_feishu(task_title: str, result_summary: str, is_error: bool = False):
    """调用 notify_done.py 发飞书通知。"""
    try:
        subprocess.run(
            [sys.executable, NOTIFY_DONE,
             '--task', task_title,
             '--result', result_summary[:2000],
             '--agent', 'Cursor-AutoExec'],
            timeout=30, capture_output=True,
        )
    except Exception as e:
        _log(f'⚠️ 飞书通知失败: {e}')


def _resolve_agent_cli():
    """找到 agent CLI 的 node.exe + index.js，跳过 .CMD/.ps1 包装层。"""
    global AGENT_CMD, AGENT_NODE, AGENT_INDEX
    base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'cursor-agent')
    versions_dir = os.path.join(base, 'versions')
    if os.path.isdir(versions_dir):
        versions = sorted(os.listdir(versions_dir), reverse=True)
        for v in versions:
            node = os.path.join(versions_dir, v, 'node.exe')
            idx = os.path.join(versions_dir, v, 'index.js')
            if os.path.isfile(node) and os.path.isfile(idx):
                AGENT_NODE = node
                AGENT_INDEX = idx
                AGENT_CMD = f'{node} {idx}'
                return
    AGENT_CMD = shutil.which('agent') or shutil.which('cursor-agent')


def execute_task(task: dict) -> None:
    """用 Cursor Agent CLI 执行一个任务，写结果到 outbox 并发飞书通知。"""
    task_id = task['task_id']
    title = task.get('title', task_id)
    prompt = _build_prompt(task)

    _log(f'🚀 自动执行: {title}')
    _log(f'prompt 长度: {len(prompt)} 字符')

    prompt_file = None
    try:
        # 直接调用 node.exe + index.js，完全绕过 .CMD/.ps1 的编码问题
        env = os.environ.copy()
        env['CURSOR_INVOKED_AS'] = 'agent'

        if AGENT_NODE and AGENT_INDEX:
            cmd = [AGENT_NODE, AGENT_INDEX]
        elif AGENT_CMD and AGENT_CMD.lower().endswith(('.cmd', '.bat')):
            cmd = ['cmd', '/c', AGENT_CMD]
        else:
            cmd = [AGENT_CMD]

        cmd += ['--print', '--force', '--approve-mcps', '--trust',
                '--workspace', WORKSPACE,
                '--output-format', 'text']

        # 任务级 model > 全局 DEFAULT_MODEL > CLI 默认
        model = task.get('model') or DEFAULT_MODEL
        if model:
            cmd += ['--model', model]

        # 任务级 mode: plan / ask（不设则为完整 agent 模式）
        mode = task.get('mode')
        if mode in ('plan', 'ask'):
            cmd += ['--mode', mode]

        # 任务级 sandbox 开关
        sandbox = task.get('sandbox')
        if sandbox in ('enabled', 'disabled'):
            cmd += ['--sandbox', sandbox]

        cmd.append(prompt)

        model_info = model or '(CLI默认)'
        mode_info = mode or 'agent'
        _log(f'模型: {model_info} | 模式: {mode_info}')
        _log(f'执行命令: {os.path.basename(cmd[0])} ... (共 {len(cmd)} 个参数)')

        proc = subprocess.run(
            cmd, capture_output=True, timeout=TASK_TIMEOUT,
            encoding='utf-8', errors='replace', env=env,
        )
        stdout = proc.stdout or ''
        stderr = proc.stderr or ''

        _log(f'CLI 返回码: {proc.returncode}, stdout: {len(stdout)} 字符, stderr: {len(stderr)} 字符')

        if proc.returncode == 0:
            summary = stdout.strip()
            if not summary:
                summary = '(Agent 无文本输出，任务可能已通过工具完成)'
            _write_result(task, 'done', summary)
            # 飞书显示取前1500字，完整结果保存在 outbox
            _send_feishu(title, f'✅ 已完成\n{summary[:1500]}')
            _log(f'✅ 任务完成: {task_id}')
        else:
            err_msg = stderr.strip()[:500] or stdout.strip()[:500] or f'exit code {proc.returncode}'
            # 模型服务临时故障 / 额度超限时，自动 fallback 到 auto 模型重试一次
            is_provider_error = (
                'Provider Error' in err_msg
                or 'trouble connecting' in err_msg
                or 'usage limit' in err_msg
                or 'hit your usage' in err_msg
                or 'Spend Limit' in err_msg
            )
            if is_provider_error and model != 'auto':
                _log(f'⚠️ 模型服务故障，fallback 到 auto 模型重试...')
                fallback_cmd = cmd[:-1]  # 去掉 prompt
                # 移除原来的 --model 参数
                clean_cmd = []
                skip_next = False
                for part in fallback_cmd:
                    if skip_next:
                        skip_next = False
                        continue
                    if part == '--model':
                        skip_next = True
                        continue
                    clean_cmd.append(part)
                clean_cmd += ['--model', 'auto', prompt]
                proc2 = subprocess.run(
                    clean_cmd, capture_output=True, timeout=TASK_TIMEOUT,
                    encoding='utf-8', errors='replace', env=env,
                )
                if proc2.returncode == 0:
                    summary = (proc2.stdout or '').strip()
                    if not summary:
                        summary = '(Agent 无文本输出)'
                    _write_result(task, 'done', summary)
                    _send_feishu(title, f'✅ 已完成（fallback auto）\n{summary[:1500]}')
                    _log(f'✅ 任务完成(fallback): {task_id}')
                    return
                err_msg = (proc2.stderr or '').strip()[:500] or err_msg
            _write_result(task, 'error', f'CLI 返回非零: {err_msg}')
            _send_feishu(title, f'❌ 执行失败\n{err_msg[:200]}', is_error=True)
            _log(f'❌ 任务失败: {task_id} — {err_msg[:200]}')

    except subprocess.TimeoutExpired:
        _write_result(task, 'error', f'执行超时（{TASK_TIMEOUT}s）')
        _send_feishu(title, f'⏰ 执行超时（{TASK_TIMEOUT}s），已中断', is_error=True)
        _log(f'⏰ 任务超时: {task_id}')
    except FileNotFoundError:
        _write_result(task, 'error', 'agent CLI 未安装，无法自动执行')
        _send_feishu(title, '❌ agent CLI 未找到，请先运行 agent login', is_error=True)
        _log('❌ agent CLI 未安装!')
    except Exception as e:
        _write_result(task, 'error', f'未知异常: {e}')
        _send_feishu(title, f'❌ 未知异常: {e}', is_error=True)
        _log(f'❌ 异常: {e}')
        import traceback
        _log(traceback.format_exc())
    except BaseException as e:
        _log(f'💀 致命异常（BaseException）: {e}')
        import traceback
        _log(traceback.format_exc())


def main():
    parser = argparse.ArgumentParser(description='Cursor 后台任务守护 — 等待队列任务')
    parser.add_argument('--timeout', type=int, default=3600, help='最长等待秒数（默认 3600 = 1小时）')
    parser.add_argument(
        '--stay-alive',
        action='store_true',
        help='收到任务后不退出进程，继续轮询',
    )
    parser.add_argument(
        '--auto-execute',
        action='store_true',
        help='检测到任务后自动调用 Cursor Agent CLI 执行（需预先安装 agent CLI 并 login）',
    )
    parser.add_argument(
        '--default-model',
        type=str, default=None,
        help='全局默认模型（可被任务 JSON 中的 model 字段覆盖）。例: claude-4.6-opus-high-thinking',
    )
    args = parser.parse_args()

    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    global AGENT_CMD, AGENT_NODE, AGENT_INDEX, DEFAULT_MODEL
    DEFAULT_MODEL = args.default_model
    if args.auto_execute:
        _resolve_agent_cli()
        if not AGENT_NODE:
            _log('❌ --auto-execute 需要 Cursor Agent CLI，但未找到')
            _log('请先运行: irm "https://cursor.com/install?win32=true" | iex && agent login')
            _log('退回传统模式（仅打印任务）')
            args.auto_execute = False
        else:
            _log(f'agent 直调: {AGENT_NODE} {AGENT_INDEX}')

    start = time.time()
    last_heartbeat = start
    mode_label = 'auto-execute' if args.auto_execute else ('stay-alive' if args.stay_alive else 'interactive')
    _log(f'🟢 启动，监听任务队列...')
    _log(f'📂 inbox: {INBOX_DIR}')
    model_label = DEFAULT_MODEL or '(CLI默认)'
    _log(f'⏱ 最长等待: {args.timeout}s | 模式: {mode_label} | 默认模型: {model_label}')

    while True:
        now_ts = time.time()
        elapsed = int(now_ts - start)

        if os.path.exists(RESTART_FLAG):
            try:
                os.remove(RESTART_FLAG)
            except OSError:
                pass
            _log('🔄 检测到 restart flag，优雅退出')
            sys.exit(0)

        task = scan_inbox()
        if task:
            try:
                mark_processing(task)
                task_id = task['task_id']
                title = task.get('title', task_id)
                _log(f'📬 收到新任务: {title}')
                _log(f'task_id: {task_id} | 来源: {task.get("submitted_by", "unknown")}')

                current_task_path = os.path.join(OUTBOX_DIR, '_current_task.json')
                with open(current_task_path, 'w', encoding='utf-8') as f:
                    json.dump(task, f, ensure_ascii=False, indent=2)

                if args.auto_execute:
                    execute_task(task)
                    time.sleep(POLL_INTERVAL)
                    continue

                # --- 传统模式：打印任务内容到 stdout ---
                print('\n' + '='*60, flush=True)
                print('CURSOR_TASK_START', flush=True)
                print(json.dumps(task, ensure_ascii=False, indent=2), flush=True)
                print('CURSOR_TASK_END', flush=True)
                print('='*60, flush=True)
                try:
                    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                    import feishu_helper
                    instructions_preview = task.get('instructions', '')[:80].replace('\n', ' ')
                    feishu_helper.send_text(
                        f'📬 Cursor 后台收到新任务\n'
                        f'任务：{title}\n'
                        f'内容：{instructions_preview}...\n'
                        f'⚠️ 请到 Cursor 对话框告知执行此任务'
                    )
                except Exception as e:
                    _log(f'⚠️ 飞书通知失败: {e}')
                if args.stay_alive:
                    time.sleep(POLL_INTERVAL)
                    continue
                sys.exit(0)
            except Exception as exc:
                _log(f'💥 任务处理异常: {exc}')
                import traceback
                _log(traceback.format_exc())

        if elapsed >= args.timeout:
            _log(f'⏰ 等待超时 ({args.timeout}s)，无任务到达')
            sys.exit(0)

        if now_ts - last_heartbeat >= 60:
            _log(f'💤 等待中... 已等 {elapsed}s，剩余 {args.timeout - elapsed}s')
            last_heartbeat = now_ts

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
