# -*- coding: utf-8 -*-
"""轮询 GRFal 异步任务直到出结果并下载。

为什么要有这个脚本：media-worker 的 Bash 工具禁用前台 sleep，没法自己等；
主 agent 可以起后台命令，所以轮询这活归主 agent。
判完成一律看 JSON 的 status 字段，别 grep "success"——响应体里恒有 "success": true（那是HTTP层成功），会假阳性。
"""
import json, re, subprocess, sys, time, os, urllib.request

GRFAL = r'C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py'


def check(task_id):
    r = subprocess.run([sys.executable, GRFAL, '--check-task', task_id],
                       capture_output=True)
    txt = r.stdout.decode('utf-8', errors='replace')
    m = re.search(r'\{.*\}', txt, re.S)
    return json.loads(m.group(0)) if m else {'status': 'unparsed', '_raw': txt[:400]}


BASES = ('https://grfal.tap4fun.com', 'http://172.20.90.45:6018')


def urls_of(d):
    """从完成响应里把所有结果 URL 抠出来（结构随工具变，做通用递归）。

    ⚠️后端返回的常是**相对路径** `/api/output/...`（gradio.Server 改版后如此），
    必须补 host 才能下载——只认 http 开头会把完成的任务当成"没结果"。
    """
    out = []
    def walk(v):
        if isinstance(v, str) and re.search(r'\.(mp4|png|jpg|jpeg|webm|webp)$', v.split('?')[0], re.I):
            out.append(v if v.startswith('http') else BASES[0] + v)
        elif isinstance(v, dict):
            for x in v.values(): walk(x)
        elif isinstance(v, list):
            for x in v: walk(x)
    walk(d)
    return list(dict.fromkeys(out))


def is_done(d):
    """判完成。

    🪤后端对「运行中」和「已完成」返回**两种不同结构**：
      运行中: {"success":true, "status":"running", "progress":..., "elapsed_seconds":...}
      已完成: {"success":true, "result":"/api/output/xxx.mp4"}        <- 压根没有 status 字段!
    所以只看 status 会让完成的任务一直判成 '?' 直到假超时（2026-07-29 实测踩到）。
    正确判据 = status 命中完成词 **或** 已经能抠出结果文件。
    """
    st = str(d.get('status', '')).lower()
    return st in ('completed', 'success', 'succeeded', 'finished') or bool(urls_of(d))


def main():
    task_id, outdir, fname = sys.argv[1], sys.argv[2], sys.argv[3]
    tries = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    os.makedirs(outdir, exist_ok=True)
    for i in range(1, tries + 1):
        d = check(task_id)
        st = str(d.get('status', '(无status=多半已完成)')).lower()
        print(f'[{i}/{tries}] status={st} elapsed={d.get("elapsed_seconds")}', flush=True)
        if is_done(d):
            us = urls_of(d)
            print(f'  结果 URL {len(us)} 个', flush=True)
            if not us:
                print('  !! 完成但没抠到 URL，原始响应：', flush=True)
                print(json.dumps(d, ensure_ascii=False)[:1500], flush=True)
                return 2
            for n, u in enumerate(us):
                ext = os.path.splitext(u.split('?')[0])[1] or '.mp4'
                base, e0 = os.path.splitext(fname)
                dst = os.path.join(outdir, fname if n == 0 else f'{base}_alt{n}{e0 or ext}')
                urllib.request.urlretrieve(u, dst)
                print(f'  ✔ {dst}  ({os.path.getsize(dst)} bytes)', flush=True)
            return 0
        if st in ('failed', 'error'):
            print('  !! 生成失败：' + json.dumps(d, ensure_ascii=False)[:800], flush=True)
            return 1
        if i < tries:
            time.sleep(60)
    print('!! 超时，任务仍未完成（未重新提交，可继续用同一 task_id 查）', flush=True)
    return 3


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main())
