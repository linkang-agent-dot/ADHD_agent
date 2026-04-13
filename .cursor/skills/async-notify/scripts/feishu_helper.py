"""飞书消息发送工具 — async-notify skill 共用模块"""
import re
import requests
import json
import os
import sys
import mimetypes
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

APP_ID = 'cli_a934245330789ccf'
OPEN_ID = 'ou_e48f6c4c0395f45b74b51525f348678b'
SEND_URL = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
TOKEN_URL = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
OPENCLAW_CONFIG = r'C:\Users\linkang\.openclaw\openclaw.json'


def get_app_secret() -> str:
    """从环境变量或 OpenClaw 配置文件读取飞书 App Secret"""
    # 优先读环境变量
    secret = os.environ.get('FEISHU_APP_SECRET', '')
    if secret:
        return secret
    # 回退：从 openclaw.json 的 env 节点读取
    try:
        with open(OPENCLAW_CONFIG, 'r', encoding='utf-8') as f:
            import json as _json
            cfg = _json.load(f)
        secret = cfg.get('env', {}).get('FEISHU_APP_SECRET', '')
        if secret:
            return secret
    except Exception as e:
        pass
    raise ValueError("FEISHU_APP_SECRET 未找到（环境变量 / openclaw.json 均无）")


def get_token() -> str:
    app_secret = get_app_secret()
    r = requests.post(TOKEN_URL, json={'app_id': APP_ID, 'app_secret': app_secret}, timeout=10)
    token = r.json().get('tenant_access_token', '')
    if not token:
        raise ValueError(f"获取飞书 token 失败: {r.text}")
    return token


def _verify_message(msg_id: str, original_text: str, token: str) -> bool:
    """发送后读回消息，检查是否有乱码（双重编码特征字符）。"""
    try:
        url = f'https://open.feishu.cn/open-apis/im/v1/messages/{msg_id}'
        r = requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=10)
        data = r.json()
        items = data.get('data', {}).get('items', [])
        if not items:
            return True  # 读不到就跳过检查
        body = items[0].get('body', {}).get('content', '')
        content = json.loads(body)
        actual = content.get('text', '') or ''
        # 检测常见双重编码乱码特征（GBK↔UTF-8 交叉）
        garble_chars = ['鎻', '馃', '鍛', '鏃', '鎸', '涓', '鍒', '妯', '鐪', '璇']
        for c in garble_chars:
            if c in actual and c not in original_text:
                print(f'[feishu_helper] ❌ 检测到乱码字符「{c}」，消息可能双重编码', file=sys.stderr)
                return False
        return True
    except Exception:
        return True  # 验证失败不阻塞


def send_text(text: str, token: str = None, verify: bool = True) -> dict:
    """发送纯文本消息，默认发后自动验证内容"""
    if token is None:
        token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        'receive_id': OPEN_ID,
        'msg_type': 'text',
        'content': json.dumps({'text': text}, ensure_ascii=False)
    }
    r = requests.post(SEND_URL, headers=headers, json=payload, timeout=15)
    resp = r.json()
    if verify and resp.get('code') == 0:
        msg_id = resp.get('data', {}).get('message_id', '')
        if msg_id:
            ok = _verify_message(msg_id, text, token)
            if not ok:
                resp['_garble_detected'] = True
    return resp


def clean_markdown(text: str) -> str:
    """把常见 markdown 语法转成飞书友好的纯文本，提升可读性。"""
    lines = text.splitlines()
    out = []
    in_code_block = False
    for line in lines:
        # 代码块切换
        if re.match(r'^```', line):
            in_code_block = not in_code_block
            if in_code_block:
                out.append('――― 代码 ―――')
            else:
                out.append('――――――――――')
            continue
        if in_code_block:
            out.append('  ' + line)
            continue

        # 表格分隔行 |---|---| → 跳过
        stripped = line.strip()
        if re.match(r'^\|[\s|:\-]+\|$', stripped):
            continue
        # 表格数据行 | col1 | col2 | → 取出单元格，空格分隔
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped[1:-1].split('|')]
            cells = [c for c in cells if c]  # 过滤空单元格
            if cells:
                out.append('  ' + '  |  '.join(cells))
            continue

        # 标题：# ## ### → ▌标题
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            prefix = '▌' if level <= 2 else '▷'
            title_text = m.group(2).strip()
            # 清洗标题里的行内格式
            title_text = re.sub(r'\*\*(.+?)\*\*', r'\1', title_text)
            title_text = re.sub(r'\*(.+?)\*', r'\1', title_text)
            out.append(f'{prefix} {title_text}')
            continue
        # 有序列表：1. 2. → 数字.
        m = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)
        if m:
            indent = '  ' * (len(m.group(1)) // 2 + 1)
            out.append(f'{indent}{m.group(2)}. {m.group(3)}')
            continue
        # 无序列表：- * + → •
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            indent = '  ' * (len(m.group(1)) // 2 + 1)
            out.append(f'{indent}• {m.group(2)}')
            continue
        # 引用 > → ｜
        m = re.match(r'^>\s*(.*)', line)
        if m:
            out.append(f'  ｜{m.group(1)}')
            continue
        # 分隔线 --- === *** → 细线
        if re.match(r'^[-=*]{3,}\s*$', line):
            out.append('──────────')
            continue

        # 行内格式：**bold** *italic* `code` ~~strike~~
        line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        line = re.sub(r'\*(.+?)\*', r'\1', line)
        line = re.sub(r'`(.+?)`', r'「\1」', line)
        line = re.sub(r'~~(.+?)~~', r'\1', line)
        # 链接 [text](url) → text
        line = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', line)
        out.append(line)

    # 去掉连续空行（只保留一个）
    result = []
    prev_blank = False
    for l in out:
        is_blank = (l.strip() == '')
        if is_blank and prev_blank:
            continue
        result.append(l)
        prev_blank = is_blank
    return '\n'.join(result).strip()


def audit_result(result: str) -> tuple[bool, str]:
    """检查结果是否看起来完整，返回 (is_ok, hint)。"""
    cleaned = result.strip()
    if len(cleaned) < 30:
        return False, '⚠️ 结果内容过短，可能不完整'
    vague_keywords = ['好的', '完成了', 'done', 'ok', '已处理']
    if cleaned.lower() in [k.lower() for k in vague_keywords]:
        return False, '⚠️ 结果仅含模糊确认词，缺少实质内容'
    return True, ''


def send_card(title: str, body_lines: list[str], token: str = None) -> dict:
    """发送富文本卡片消息（飞书 post 格式）"""
    if token is None:
        token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    content_rows = [[{'tag': 'text', 'text': line}] for line in body_lines]
    payload = {
        'receive_id': OPEN_ID,
        'msg_type': 'post',
        'content': json.dumps({
            'zh_cn': {
                'title': title,
                'content': content_rows
            }
        })
    }
    r = requests.post(SEND_URL, headers=headers, json=payload, timeout=15)
    return r.json()


def send_done_notification(task: str, result: str, agent: str, timestamp: str) -> bool:
    """发送任务完成通知（send_text 纯文本，含 markdown 清洗 + 完整性审核 + 发后验证）"""
    try:
        token = get_token()
        cleaned = clean_markdown(result)
        ok, hint = audit_result(cleaned)
        parts = [f'✅ [{agent}] {task}', '']
        parts.append(cleaned)
        if not ok:
            parts += ['', hint]
        parts += ['', f'⏱ {timestamp}']
        full_text = '\n'.join(parts)
        resp = send_text(full_text, token, verify=True)
        if resp.get('_garble_detected'):
            print('[feishu_helper] ⚠️ 发后验证检测到乱码，跳过重发（源数据可能已损坏）', file=sys.stderr)
        return resp.get('code') == 0
    except Exception as e:
        print(f'[feishu_helper] 发送完成通知失败: {e}', file=sys.stderr)
        return False


def upload_image(image_path: str, token: str = None) -> str:
    """上传图片到飞书，返回 image_key"""
    if token is None:
        token = get_token()
    upload_url = 'https://open.feishu.cn/open-apis/im/v1/images'
    headers = {'Authorization': f'Bearer {token}'}
    ctype, _ = mimetypes.guess_type(image_path)
    if not ctype or not ctype.startswith('image/'):
        ctype = 'image/png'
    with open(image_path, 'rb') as f:
        files = {'image': (Path(image_path).name, f, ctype)}
        data = {'image_type': 'message'}
        r = requests.post(upload_url, headers=headers, files=files, data=data, timeout=30)
    resp = r.json()
    if resp.get('code') != 0:
        raise ValueError(f"飞书图片上传失败: {resp}")
    return resp['data']['image_key']


def send_image(image_path: str, token: str = None) -> dict:
    """上传并发送一张图片消息"""
    if token is None:
        token = get_token()
    image_key = upload_image(image_path, token)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        'receive_id': OPEN_ID,
        'msg_type': 'image',
        'content': json.dumps({'image_key': image_key})
    }
    r = requests.post(SEND_URL, headers=headers, json=payload, timeout=15)
    return r.json()


def send_images(image_paths: list, caption: str = None, token: str = None) -> list:
    """批量发送多张图片，可附带文字说明"""
    if token is None:
        token = get_token()
    results = []
    if caption:
        send_text(caption, token)
    for path in image_paths:
        try:
            resp = send_image(path, token)
            results.append({'path': path, 'ok': resp.get('code') == 0, 'resp': resp})
        except Exception as e:
            results.append({'path': path, 'ok': False, 'error': str(e)})
    return results


def send_confirm_notification(task: str, question: str, agent: str, task_id: str, timestamp: str) -> bool:
    """发送需确认通知"""
    try:
        token = get_token()
        title = f'🔔 [{agent}] {task} — 需要确认'
        body = [
            f'问题：{question}',
            '',
            f'task_id：{task_id}',
            '',
            '💬 回复方式（告诉虾哥）：',
            '• 同意/是/yes/继续 → 确认执行',
            '• 拒绝/否/no/取消 → 取消操作',
            '• 或直接说明你的想法',
            '',
            f'⏰ 请求时间：{timestamp}',
            '（虾哥会把你的回复转达给 Cursor）',
        ]
        resp = send_card(title, body, token)
        return resp.get('code') == 0
    except Exception as e:
        print(f'[feishu_helper] 发送确认通知失败: {e}', file=sys.stderr)
        return False
