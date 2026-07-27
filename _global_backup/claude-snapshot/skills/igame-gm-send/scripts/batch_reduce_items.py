#!/usr/bin/env python3
"""批量给玩家扣道具/资源(GMReduceItems)——prod/dev/beta。
读 reclaim batch json [{"server","uid","args":"cfgid,num;cfgid,num"}], 逐条发 gm-operate/add。
args 作为单个字符串参数传给 GMReduceItems(itemInfoStr)，内含逗号+分号，绝不能被拆散。
默认 dry-run；--send 才真发；--limit N 只发前 N 条(金丝雀)；发后存 op id 到 --opout 供 detail 复查。
GMReduceItems 内部 Math.Min(num,余额) → floor 到 0，扣不到负数(缺口写掉)。
"""
from __future__ import annotations
import argparse, json, sys, pathlib, time, urllib.error, urllib.request

ENDPOINTS = {
    "prod": "https://webgw-cn.tap4fun.com/ark/gm-operate/add",
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate/add",
    "dev":  "https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate/add",
}
ORIGINS = {
    "prod": "https://igame.tap4fun.com",
    "beta": "https://igame-qa.tap4fun.com",
    "dev":  "https://igame-dev.tap4fun.com",
}

def load_auth(p):
    a = json.load(open(p, "r", encoding="utf-8"))
    tok = (a.get("token") or "").strip(); cid = (a.get("clientId") or "").strip()
    if not tok or not cid: raise ValueError("auth 缺 token/clientId")
    return tok, cid

def send_one(endpoint, origin, tok, cid, gameid, regionid, server, uid, cmd, argstr):
    inner = {"serverIds": str(server).strip(), "cmd": cmd.strip(),
             "playerIds": str(uid).strip(), "args": [argstr]}   # args 单元素，保留逗号/分号
    payload = {"operateType": 3, "gmCommand": [json.dumps(inner, ensure_ascii=False)]}
    req = urllib.request.Request(endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"accept": "*/*", "authorization": f"Bearer {tok}", "clientid": cid,
                 "content-type": "application/json", "gameid": str(gameid), "regionid": str(regionid),
                 "origin": origin, "referer": origin + "/"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True, help="reclaim batch json")
    ap.add_argument("--env", choices=("prod","beta","dev"), default="prod")
    ap.add_argument("--cmd", default="reduceitems", help="GM名(无需gm前缀)")
    ap.add_argument("--auth-file", default="C:/Users/linkang/.igame-auth.json")
    ap.add_argument("--gameid", default="1090"); ap.add_argument("--regionid", default="201")
    ap.add_argument("--limit", type=int, default=0, help="只发前N条(0=全部)")
    ap.add_argument("--send", action="store_true", help="真发(否则 dry-run)")
    ap.add_argument("--opout", default="", help="发后把 [{uid,server,opid,resp}] 写这")
    ap.add_argument("--sleep", type=float, default=0.15)
    a = ap.parse_args()

    batch = json.load(open(a.batch, "r", encoding="utf-8"))
    if a.limit > 0: batch = batch[:a.limit]
    endpoint, origin = ENDPOINTS[a.env], ORIGINS[a.env]

    if not a.send:
        print(f"[DRY-RUN] env={a.env} endpoint={endpoint} cmd={a.cmd} 共 {len(batch)} 条")
        for b in batch[:3]:
            inner = {"serverIds": b["server"], "cmd": a.cmd, "playerIds": b["uid"], "args": [b["args"]]}
            print("  样例:", json.dumps(inner, ensure_ascii=False))
        print("加 --send 真发；--limit 1 先金丝雀")
        return 0

    tok, cid = load_auth(a.auth_file)
    results = []
    for i, b in enumerate(batch, 1):
        try:
            resp = send_one(endpoint, origin, tok, cid, a.gameid, a.regionid,
                            b["server"], b["uid"], a.cmd, b["args"])
            ok = '"success":true' in resp.replace(" ", "").lower()
            opid = ""
            try: opid = str(json.loads(resp).get("data", ""))
            except Exception: pass
            print(f"[{i}/{len(batch)}] {b['server']}/{b['uid']} {'OK' if ok else 'FAIL'} op={opid} {resp[:120]}")
            results.append({"uid": b["uid"], "server": b["server"], "opid": opid, "ok": ok, "resp": resp})
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", errors="replace")
            print(f"[{i}/{len(batch)}] {b['server']}/{b['uid']} HTTPERR {txt[:160]}")
            results.append({"uid": b["uid"], "server": b["server"], "opid": "", "ok": False, "resp": txt})
        except Exception as e:
            print(f"[{i}/{len(batch)}] {b['server']}/{b['uid']} ERR {e}")
            results.append({"uid": b["uid"], "server": b["server"], "opid": "", "ok": False, "resp": str(e)})
        time.sleep(a.sleep)
    if a.opout:
        open(a.opout, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=1))
        print("op记录已存", a.opout)
    okn = sum(1 for r in results if r["ok"])
    print(f"\n完成: {okn}/{len(results)} success")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
