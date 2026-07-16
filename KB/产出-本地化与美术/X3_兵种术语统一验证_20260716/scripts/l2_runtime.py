# -*- coding: utf-8 -*-
"""L2 运行时扫描：通过 DebugUtils 桥逐语言 LocalizationMgr.Update(lang) 强制重载磁盘 bytes，
再 Get(key) 断言任务书全部期望值。结束后恢复原语言 zh。"""
import subprocess, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, r"C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\b1394e45-ee3b-414f-bc83-acdb02f650bd\scratchpad")
from l1_assert import CHECKS, LANG_FILE

CLIENT_DIR = r"C:\x3-project\client"
CLIENT_PY = r"C:\x3-project\.claude\skills\DebugUtils\scripts\client.py"
MGR = "TFW.Localization.LocalizationMgr"

def call(member, arg):
    r = subprocess.run(
        [sys.executable, CLIENT_PY, "invoke", "--type", MGR, "--member", member,
         "--kind", "call", "--args", arg],
        cwd=CLIENT_DIR, capture_output=True, text=True, encoding="utf-8", timeout=30)
    out = r.stdout.strip()
    try:
        j = json.loads(out)
    except Exception:
        return {"ok": False, "raw": out, "err": r.stderr[-300:]}
    return j

# 按语言分组
by_lang = {}
for group, key, lang, mode, exp in CHECKS:
    by_lang.setdefault(LANG_FILE[lang], []).append((group, key, lang, mode, exp))

passed = failed = 0
fails = []
for lf in sorted(by_lang):
    u = call("Update", lf)
    if not u.get("ok"):
        print(f"[!] Update({lf}) failed: {u}")
        for c in by_lang[lf]:
            failed += 1; fails.append(c + (None,))
        continue
    for group, key, lang, mode, exp in by_lang[lf]:
        g = call("Get", key)
        actual = g.get("result") if g.get("ok") else None
        ok = False
        if actual is not None:
            if mode == "eq": ok = actual == exp
            elif mode == "contains": ok = exp in actual
            elif mode == "endswith": ok = actual.endswith(exp)
            elif mode == "not_contains": ok = exp not in actual
        if ok: passed += 1
        else:
            failed += 1
            fails.append((group, key, lang, mode, exp, actual))

# 恢复原语言 zh
r = call("Update", "zh")
print(f"restore zh: ok={r.get('ok')}")
print(f"L2 RUNTIME: PASS {passed} / FAIL {failed} (total {passed+failed})")
for item in fails:
    group, key, lang, mode, exp, actual = item
    print(f"  [X] {group} {key} [{lang}] {mode}")
    print(f"      expect: {exp!r}")
    print(f"      actual: {actual!r}")
