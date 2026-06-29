#!/usr/bin/env python3
"""批量给玩家加活动/BP积分 (GMAddActivityScore) via iGame gm-operate/add。

2026-06-25 实测定型的格式：
  gmCommand 内层 = {"serverIds":"<服,字符串>","cmd":"addactivityscore",
                    "playerIds":"<玩家,字符串>","args":["<活动雪花id>","<分值>"]}
  - serverIds / playerIds 都是字符串(不是数组)；不要尾随 ；
  - 加分的活动 id 必须是【运行时雪花号】(不是配置号102243)。世界杯BP=7655210947394404352。
    雪花号查法见 memory reference_x3_score_activity「GMPrintServerActivityByCfgId」。
  逐条发送 → 自动用 /gm-operate/detail 读 returnInfo 核 errCode=0。

输入(三选一)：
  1. --csv 文件，每行: serverId,playerId,activityId,score  (# 开头/空行忽略，可含表头 serverId)
  2. --rows "3080,27877,7655210947394404352,500;3080,27878,7655210947394404352,500"  (分号隔行)
  3. 单条: --server 3080 --player 27877 --activity 7655210947394404352 --score 500

用法:
  python batch_add_score.py --csv scores.csv
  python batch_add_score.py --rows "3080,27877,7655210947394404352,500"
  python batch_add_score.py --server 3080 --player 27877 --activity 7655210947394404352 --score 500
  可选: --cmd addactivityscore(默认) / --env dev|beta / --auth-file <path> / --dry-run
"""
from __future__ import annotations
import argparse, json, sys, time, pathlib, urllib.request, urllib.error

ENDPOINTS = {
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate",
    "dev":  "https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate",
}


def load_auth(p):
    a = json.load(open(p, "r", encoding="utf-8"))
    t, c = (a.get("token") or "").strip(), (a.get("clientId") or "").strip()
    if not t or not c:
        raise ValueError("auth file 需含 token + clientId")
    return t, c


def headers(token, client_id, env):
    origin = "https://igame-qa.tap4fun.com" if env == "beta" else "https://igame-dev.tap4fun.com"
    return {
        "accept": "*/*", "authorization": f"Bearer {token}", "clientid": client_id,
        "content-type": "application/json", "gameid": "1090", "regionid": "201",
        "origin": origin, "referer": origin + "/",
    }


def parse_rows(args):
    rows = []
    if args.csv:
        for ln in pathlib.Path(args.csv).read_text(encoding="utf-8-sig").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = [x.strip() for x in ln.split(",")]
            if len(parts) < 4 or not parts[0].lstrip("-").isdigit():
                continue  # 跳过表头/坏行
            rows.append(parts[:4])
    elif args.rows:
        for seg in args.rows.split(";"):
            seg = seg.strip()
            if not seg:
                continue
            parts = [x.strip() for x in seg.split(",")]
            if len(parts) >= 4:
                rows.append(parts[:4])
    elif args.server and args.player and args.activity and args.score:
        rows.append([str(args.server), str(args.player), str(args.activity), str(args.score)])
    return rows


def send_one(base, hdr, server, player, activity, score, cmd):
    gm_line = json.dumps({"serverIds": str(server), "cmd": cmd,
                          "playerIds": str(player), "args": [str(activity), str(score)]},
                         ensure_ascii=False)
    payload = {"operateType": 3, "gmCommand": [gm_line]}
    req = urllib.request.Request(base + "/add", data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode("utf-8", "replace"))
    return resp


def verify(base, hdr, op_id):
    try:
        req = urllib.request.Request(base + f"/detail?id={op_id}", headers=hdr, method="GET")
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))["data"]
        for c in d.get("contents", []):
            ri = c.get("returnInfo")
            if ri:
                arr = json.loads(ri)
                return all(x.get("errCode") == 0 for x in arr), ri
        return False, "(returnInfo 空=玩家没绑/没找到)"
    except Exception as e:
        return None, f"detail查询失败: {e}"


def main():
    ap = argparse.ArgumentParser(description="批量 GMAddActivityScore via iGame")
    ap.add_argument("--csv"); ap.add_argument("--rows")
    ap.add_argument("--server"); ap.add_argument("--player")
    ap.add_argument("--activity"); ap.add_argument("--score")
    ap.add_argument("--cmd", default="addactivityscore")
    ap.add_argument("--env", choices=("dev", "beta"), default="dev")
    ap.add_argument("--auth-file", default="C:/Users/linkang/.igame-auth.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-verify", action="store_true", help="不查 detail 核验(更快)")
    a = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    rows = parse_rows(a)
    if not rows:
        print("没有有效输入行。用 --csv / --rows / 单条参数。", file=sys.stderr)
        return 2
    base = ENDPOINTS[a.env]
    token, client_id = load_auth(a.auth_file)
    hdr = headers(token, client_id, a.env)

    print(f"共 {len(rows)} 条，env={a.env}，cmd={a.cmd}{'  [DRY-RUN]' if a.dry_run else ''}")
    ok = fail = 0
    for i, (srv, pid, act, sc) in enumerate(rows, 1):
        if a.dry_run:
            print(f"  [{i}] DRY srv={srv} player={pid} activity={act} score={sc}")
            continue
        try:
            resp = send_one(base, hdr, srv, pid, act, sc, a.cmd)
            oid = resp.get("data", {}).get("id")
            if not resp.get("success"):
                print(f"  [{i}] FAIL 网关拒绝 srv={srv} p={pid}: {json.dumps(resp,ensure_ascii=False)[:120]}")
                fail += 1; continue
            if a.no_verify:
                print(f"  [{i}] 已提交 op={oid} srv={srv} p={pid} +{sc}")
                ok += 1; continue
            time.sleep(2)
            good, info = verify(base, hdr, oid)
            if good:
                print(f"  [{i}] OK op={oid} srv={srv} p={pid} activity={act} +{sc}  errCode=0")
                ok += 1
            else:
                print(f"  [{i}] FAIL op={oid} srv={srv} p={pid} 执行未成功: {info}")
                fail += 1
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:120]
            print(f"  [{i}] FAIL HTTP{e.code} srv={srv} p={pid}: {body}")
            fail += 1
        except Exception as e:
            print(f"  [{i}] FAIL srv={srv} p={pid}: {e}")
            fail += 1
    if not a.dry_run:
        print(f"\n完成: 成功 {ok} / 失败 {fail} / 共 {len(rows)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
