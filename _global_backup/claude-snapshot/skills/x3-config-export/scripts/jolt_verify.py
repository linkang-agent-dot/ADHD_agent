# -*- coding: utf-8 -*-
"""触发 Jenkins X3导配置 并自动验证构建结果。

用法: python jolt_verify.py <branch>

流程: jolt.exe 触发 -> 解析队列URL -> 轮询队列拿 build 号 -> 轮询构建到结束
     -> 打印 SUCCESS/FAILURE + 分支 + console 末尾关键行。

退出码: 0=SUCCESS, 2=FAILURE, 3=超时/无法判定, 1=触发异常。
"""
from __future__ import annotations
import sys, re, time, json, ssl, subprocess
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

JOLT = r"C:\x3-project\Tools\Jolt\jolt.exe"
JOB = "http://172.20.110.29:8080/job/X3%E5%AF%BC%E9%85%8D%E7%BD%AE/"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get_json(url: str):
    with urllib.request.urlopen(url, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def get_text(url: str) -> str:
    with urllib.request.urlopen(url, context=CTX, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def trigger(branch: str, extra=None) -> str:
    """跑 jolt，返回原始输出(GBK 解码)。

    extra: 额外透传给 Jenkins buildWithParameters 的 kv 列表，如 ['skip_check=true']。
    用于列变化确认重导（CheckColumn.py 的 skip_check 开关）等需带外参数的场景。
    """
    extra_str = (" " + " ".join(extra)) if extra else ""
    p = subprocess.Popen([JOLT], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = p.communicate(f"excel branch={branch} code_branch={branch}{extra_str}\nexit\n".encode("utf-8"), timeout=600)
    try:
        return out.decode("gbk")
    except UnicodeDecodeError:
        return out.decode("utf-8", "replace")


def main():
    branch = sys.argv[1] if len(sys.argv) > 1 else "dev-summer-love-song"
    extra = sys.argv[2:]  # 形如 skip_check=true，透传给 jolt excel 命令
    print(f"[1/3] 触发导表 branch={branch} extra={extra or '-'} ...")
    text = trigger(branch, extra)
    print(text.strip())

    m = re.search(r"/queue/item/(\d+)/", text)
    if not m:
        # 触发失败(已在队列/执行中) —— 退回看 lastBuild
        print("[!] 未拿到新队列项（可能已有构建在跑）。查 lastBuild 状态...")
        try:
            lb = get_json(JOB + "lastBuild/api/json?tree=number,result,building")
            print(f"    lastBuild #{lb.get('number')} building={lb.get('building')} result={lb.get('result')}")
        except Exception as e:
            print(f"    查询失败: {e}")
        return 3

    qid = m.group(1)
    print(f"[2/3] 队列项 {qid}，等待分配 build 号 ...")
    build_url = None
    for _ in range(40):  # 最多 ~10min 排队
        try:
            q = get_json(f"http://172.20.110.29:8080/queue/item/{qid}/api/json")
        except Exception:
            time.sleep(15); continue
        if q.get("cancelled"):
            print("[x] 队列项被取消"); return 3
        ex = q.get("executable")
        if ex and ex.get("number"):
            build_url = ex["url"]
            print(f"    -> build #{ex['number']}  {build_url}")
            break
        time.sleep(15)
    if not build_url:
        print("[!] 等待 build 号超时"); return 3

    print("[3/3] 轮询构建 ...")
    result = None
    for _ in range(40):  # 最多 ~10min 构建
        try:
            b = get_json(build_url + "api/json?tree=number,result,building,duration")
        except Exception:
            time.sleep(15); continue
        if not b.get("building") and b.get("result"):
            result = b["result"]; break
        time.sleep(15)
    if result is None:
        print("[!] 构建轮询超时，去 Jenkins 看："+build_url); return 3

    # 取 console 末尾关键行 + 分支确认
    branch_line = finish_line = ""
    try:
        lines = get_text(build_url + "consoleText").splitlines()
        for l in lines:
            if "branch=" in l: branch_line = l.strip()
            if re.search(r"Finished|FAILURE|marked build", l): finish_line = l.strip()
    except Exception:
        pass

    print("\n" + "=" * 48)
    print(f"构建结果: {result}")
    if branch_line: print(f"分支: {branch_line}")
    if finish_line: print(f"结尾: {finish_line}")
    print("构建URL: " + build_url)
    print("=" * 48)
    return 0 if result == "SUCCESS" else 2


if __name__ == "__main__":
    sys.exit(main())
