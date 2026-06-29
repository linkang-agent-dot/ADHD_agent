#!/usr/bin/env python3
"""X3 Jenkins 构建触发与查询。"""

import argparse
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone

JENKINS_URL = "http://172.20.110.29:8080"
JENKINS_USER = "admin"
JENKINS_PASSWORD = "Adminpwd99"

AUTH = HTTPBasicAuth(JENKINS_USER, JENKINS_PASSWORD)


def _get_crumb(session):
    r = session.get(f"{JENKINS_URL}/crumbIssuer/api/json", timeout=10)
    if r.status_code == 200:
        d = r.json()
        return {d["crumbRequestField"]: d["crumb"]}
    return {}


def trigger_build(job, params=None):
    """触发构建，返回 build_number。"""
    s = requests.Session()
    s.auth = AUTH
    headers = _get_crumb(s)

    if params:
        url = f"{JENKINS_URL}/job/{job}/buildWithParameters"
        r = s.post(url, headers=headers, params=params, timeout=30)
    else:
        url = f"{JENKINS_URL}/job/{job}/build"
        r = s.post(url, headers=headers, timeout=30)

    if r.status_code not in (200, 201):
        print(f"[ERROR] 触发失败 {r.status_code}: {r.text[:300]}")
        sys.exit(1)

    queue_url = r.headers.get("Location", "").rstrip("/")
    if not queue_url:
        print(f"[WARN] 触发成功但未获取队列链接，请到 Jenkins 查看: {JENKINS_URL}/job/{job}/")
        return None

    print(f"已加入队列: {queue_url}")
    deadline = time.time() + 300
    while time.time() < deadline:
        time.sleep(5)
        try:
            data = s.get(f"{queue_url}/api/json", timeout=15).json()
            exe = data.get("executable")
            if exe and exe.get("number"):
                num = exe["number"]
                print(f"构建已启动: #{num}")
                print(f"链接: {JENKINS_URL}/job/{job}/{num}")
                return num
        except Exception:
            pass
    print("[ERROR] 等待超时")
    sys.exit(1)


def check_build(job, build_number):
    """查询构建状态，返回 result 字符串。"""
    url = f"{JENKINS_URL}/job/{job}/{build_number}/api/json"
    data = requests.get(url, auth=AUTH, timeout=10).json()
    result = data.get("result")
    building = data.get("building", False)
    elapsed = (datetime.now(timezone.utc).timestamp() * 1000 - data.get("timestamp", 0)) / 60000
    est = data.get("estimatedDuration", 0) / 60000

    if building:
        print(f"状态: 构建中  已耗时 {elapsed:.0f} 分钟 / 预计 {est:.0f} 分钟")
    elif result == "SUCCESS":
        print(f"状态: 成功  耗时 {data.get('duration', 0) / 60000:.0f} 分钟")
    elif result == "ABORTED":
        print(f"状态: 已中断")
    else:
        print(f"状态: 失败({result})")
        _print_tail(job, build_number)
    return result


def watch_build(job, build_number, interval=60):
    """轮询直到构建结束。"""
    url = f"{JENKINS_URL}/job/{job}/{build_number}/api/json"
    print(f"[WATCH] {job} #{build_number} 轮询中...", flush=True)
    while True:
        time.sleep(interval)
        try:
            data = requests.get(url, auth=AUTH, timeout=15).json()
            result = data.get("result")
            if result:
                duration = data.get("duration", 0) / 60000
                if result == "SUCCESS":
                    print(f"[RESULT] SUCCESS  耗时 {duration:.0f} 分钟")
                else:
                    print(f"[RESULT] {result}  耗时 {duration:.0f} 分钟")
                    _print_tail(job, build_number)
                print(f"链接: {JENKINS_URL}/job/{job}/{build_number}")
                return result
        except Exception as e:
            print(f"[WARN] {e}", flush=True)


def check_all_status():
    """查询打包机当前占用。"""
    tree = "computer[executors[currentExecutable[fullDisplayName,timestamp,estimatedDuration,url]],oneOffExecutors[currentExecutable[fullDisplayName,timestamp,estimatedDuration,url]]]"
    r = requests.get(f"{JENKINS_URL}/computer/api/json?tree={tree}", auth=AUTH, timeout=10)
    busy = False
    for node in r.json().get("computer", []):
        for e in node.get("executors", []) + node.get("oneOffExecutors", []):
            ce = e.get("currentExecutable")
            if ce:
                busy = True
                name = ce.get("fullDisplayName", "")
                elapsed = (datetime.now(timezone.utc).timestamp() * 1000 - ce.get("timestamp", 0)) / 60000
                est = ce.get("estimatedDuration", 0) / 60000
                print(f"  {name}  已耗时 {elapsed:.0f}分钟 / 预计{est:.0f}分钟")
                print(f"    {ce.get('url', '')}")
    if not busy:
        print("  空闲，当前无任务")

    q = requests.get(f"{JENKINS_URL}/queue/api/json?tree=items[task[name],inQueueSince]", auth=AUTH, timeout=10)
    items = q.json().get("items", [])
    if items:
        print("  队列等待:")
        for item in items:
            task = item.get("task", {}).get("name", "")
            wait = (datetime.now(timezone.utc).timestamp() * 1000 - item.get("inQueueSince", 0)) / 60000
            print(f"    - {task} (等待 {wait:.0f}分钟)")


def _print_tail(job, build_number, lines=40):
    url = f"{JENKINS_URL}/job/{job}/{build_number}/consoleText"
    try:
        resp = requests.get(url, auth=AUTH, timeout=30)
        if resp.status_code == 200:
            all_lines = resp.text.splitlines()
            tail = all_lines[-lines:] if len(all_lines) > lines else all_lines
            print("--- 末尾日志 ---")
            print("\n".join(tail))
            print("--- END ---")
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="X3 Jenkins")
    sub = parser.add_subparsers(dest="cmd")

    t = sub.add_parser("trigger", help="触发构建")
    t.add_argument("job")
    t.add_argument("--branch", default="")
    t.add_argument("--publish", default="")
    t.add_argument("--env_build", default="")
    t.add_argument("--codesign", default="")
    t.add_argument("--channel", default="")
    t.add_argument("--sid", default="")
    t.add_argument("--code_branch", default="")
    t.add_argument("--sync_dlc", default="")
    t.add_argument("--BuildMethod", default="")

    c = sub.add_parser("check", help="查询状态")
    c.add_argument("job")
    c.add_argument("--build", type=int, required=True)

    w = sub.add_parser("watch", help="轮询等结果")
    w.add_argument("job")
    w.add_argument("--build", type=int, required=True)
    w.add_argument("--interval", type=int, default=60)

    sub.add_parser("status", help="打包机占用")

    args = parser.parse_args()

    if args.cmd == "trigger":
        params = {}
        if args.branch:
            params["branch"] = args.branch
        if args.publish:
            params["publish"] = args.publish
        if args.env_build:
            params["env_build"] = args.env_build
        if args.codesign:
            params["codesign"] = args.codesign
        if args.channel:
            params["channel"] = args.channel
        if args.sid:
            params["sid"] = args.sid
        if args.code_branch:
            params["code_branch"] = args.code_branch
        if args.sync_dlc:
            params["sync_dlc"] = args.sync_dlc
        if args.BuildMethod:
            params["BuildMethod"] = args.BuildMethod
        trigger_build(args.job, params or None)
    elif args.cmd == "check":
        check_build(args.job, args.build)
    elif args.cmd == "watch":
        watch_build(args.job, args.build, args.interval)
    elif args.cmd == "status":
        check_all_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
