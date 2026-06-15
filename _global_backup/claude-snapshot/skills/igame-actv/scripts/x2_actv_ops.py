# -*- coding: utf-8 -*-
"""X2 活动运维三件套：提交 / 取消 / 验证（2026-06-11 拓荒节部署沉淀，全部实测过）

用法：
  python x2_actv_ops.py submit acts.json        # 批量提交，acts.json 见下方格式
  python x2_actv_ops.py cancel 13544,13545 "原因"  # 批量取消（ids 逗号字符串）
  python x2_actv_ops.py verify 13568-13588      # 验证部署回执（区间或逗号列表）

acts.json 格式（数组）：
  [{"configId":"211110593","name":"拓荒节-2026-节日累充","across":1,"rank":1,
    "start":"2026-06-12","end":"2026-06-26","servers":[1003702,...]}]

硬知识（详见 memory workflow_x2_festival_launch_table）：
  - 时间：startTime=开始日 UTC00:00；endTime=最后活跃日的**次日** UTC00:00
  - servers 必须是活跃服（schema dump 里的服）；iGame serverMgr 名单含合服死 id
  - X2 提交即直发游戏服无审批态；recall 是空操作，撤就用 cancel
  - cancel 的 ids 必须逗号字符串；成功后 status=7
  - 提交成功 data=["13544"] 是 id 字符串数组
  - 单服活动 rank 必须 0；跨服排行 across=1 rank=1
"""
import io, sys, json, subprocess, os
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
IGAME = os.path.expanduser(r'~\.claude\skills\igame-skill\scripts\igame-query.js')


def call(kind, path, body):
    r = subprocess.run(["node", IGAME, kind, path, body], capture_output=True, text=True, encoding='utf-8')
    out = (r.stdout or "").strip()
    try:
        return json.loads(out)
    except Exception:
        return {"success": False, "message": f"非JSON响应: {out[:200]}"}


def date_ms(s):
    y, mo, d = map(int, s.split("-"))
    return int(datetime(y, mo, d, tzinfo=timezone.utc).timestamp() * 1000)


def expand_ids(s):
    out = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = map(int, part.split("-"))
            out += [str(i) for i in range(a, b + 1)]
        else:
            out.append(part)
    return out


def cmd_submit(path):
    acts = json.load(open(path, encoding='utf-8'))
    ok = 0
    for a in acts:
        if a.get("across", 0) == 0 and a.get("rank", 0) == 1:
            print(f"✗ {a['name']}: 单服活动不能 rank=1，跳过"); continue
        p = {"activityConfigId": str(a["configId"]), "name": a["name"],
             "startTime": date_ms(a["start"]), "endTime": date_ms(a["end"]),
             "previewTime": 0, "endShowTime": 0,
             "acrossServer": a.get("across", 0), "acrossServerRank": a.get("rank", 0),
             "servers": [a["servers"]]}
        resp = call("write", "activity/add_activity/submitActivity", json.dumps([p], ensure_ascii=False))
        if resp.get("success"):
            gid = (resp.get("data") or ["?"])[0]
            print(f"✓ {a['name']} -> {gid}（{a['start']} ~ {a['end']}，{len(a['servers'])}服）"); ok += 1
        else:
            print(f"✗ {a['name']}: {json.dumps(resp, ensure_ascii=False)[:200]}")
    print(f"提交 {ok}/{len(acts)}。记得 verify + 回写上线表 N/O/P 列。")


def cmd_cancel(ids_str, reason):
    ids = expand_ids(ids_str)
    resp = call("write", "activity/operation/cancel",
                json.dumps({"ids": ",".join(ids), "reason": reason}, ensure_ascii=False))
    print("cancel success:", resp.get("success"))
    for i in ids:
        d = call("read", "activity/operation/getData", json.dumps({"id": i}))
        st = d.get("data", {}).get("status")
        print(f"  {i} status={st} {'✓已取消' if st == 7 else '⚠️未变成7，检查！'}")


def cmd_verify(ids_str, expect_servers=None):
    for i in expand_ids(ids_str):
        d = call("read", "activity/operation/getData", json.dumps({"id": i}))
        data = d.get("data", {})
        blob = json.dumps(d)
        nf = blob.count("server not found")
        succ = blob.count('deploy')
        flag = "✓" if nf == 0 and (expect_servers is None or succ >= expect_servers) else "⚠️"
        print(f"{flag} {i} {data.get('name','?')} status={data.get('status')} "
              f"across={data.get('acrossServer')}/{data.get('acrossServerRank')} "
              f"deploy_success={succ} server_not_found={nf}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "submit":
        cmd_submit(sys.argv[2])
    elif cmd == "cancel":
        cmd_cancel(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "运营撤回")
    elif cmd == "verify":
        cmd_verify(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
    else:
        print(__doc__)
