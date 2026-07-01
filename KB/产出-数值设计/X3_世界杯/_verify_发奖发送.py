# -*- coding: utf-8 -*-
"""世界杯发奖「发没发/发全没」验收 —— 查 iGame 发件箱 vs 生成器应发数(权威·比 asset 表准,无领取延迟)。
用法: python _verify_发奖发送.py            # 默认核对所有已生成 奖励_*.csv 的场次
      python _verify_发奖发送.py 林康        # 指定发奖操作人过滤(默认全部WC邮件都算)
链路: igame getMailList(email/outbox) → 按对阵聚合收件数 → 比对 发奖csv/奖励_{key}.csv 行数(应发笔数)。
判据: 母邮件(status=-2·全量)或子邮件合计 == 应发笔数(差1可忽略)=已发全。status -2=拆分母邮件/-1,1=子邮件,都算已发。
"""
import json, io, sys, subprocess, csv, glob, collections, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯")
CSVDIR = ROOT / "发奖csv"
IGAME_CLI = r"C:\Users\linkang\.claude\skills\igame-skill\scripts\igame-query.js"
sys.path.insert(0, str(ROOT))
import _wc_team_i18n as TI

OPERATOR = sys.argv[1] if len(sys.argv) > 1 else None  # None=不按操作人过滤

def igame_mails(pages=4, page_size=200):
    """拉发件箱前 pages 页(按 sentAt desc),返回全部记录。"""
    out = []
    for pi in range(1, pages + 1):
        params = json.dumps({"pageIndex": pi, "pageSize": page_size}, ensure_ascii=False)
        r = subprocess.run(["node", IGAME_CLI, "write", "email/outbox/getMailList", params],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        try:
            d = json.loads(r.stdout)
        except Exception:
            print("解析失败 page", pi, r.stdout[:200]); break
        data = d.get('data', [])
        out += data
        if len(data) < page_size:
            break
    return out

def match_title(a, b):
    return f"{TI.team_name(a,'en')} vs {TI.team_name(b,'en')}"

def expected_counts():
    """读 schedule + 奖励csv,返回 {对阵英文标题: (key, 应发笔数)}。"""
    sched = json.loads((ROOT / "wc_dashboard_data.json").read_text(encoding='utf-8'))["schedule"]
    exp = {}
    for m in sched:
        key = m["key"]; f = CSVDIR / f"奖励_{key}.csv"
        if not f.exists():
            continue
        n = sum(1 for _ in csv.reader(open(f, encoding='gbk')))
        exp[match_title(m["a_code"], m["b_code"])] = (key, n)
    return exp

def main():
    exp = expected_counts()
    if not exp:
        print("没有已生成的 奖励_*.csv,先跑 _gen_发奖详情.py"); return
    mails = igame_mails()
    # 按对阵聚合(标题 'World Cup Oracle Win! - {A} vs {B}';老版无对阵后缀跳过)
    agg = collections.defaultdict(lambda: {"parent": 0, "child": 0})
    for m in mails:
        t = m.get('title') or ''
        if 'World Cup' not in t and 'Oracle' not in t:
            continue
        if OPERATOR and OPERATOR not in (m.get('operator') or ''):
            continue
        vs = t.split(' - ', 1)[1].strip() if ' - ' in t else '(无对阵)'
        rc = m.get('receiverCount') or 0
        if m.get('status') == -2:
            agg[vs]["parent"] += rc
        else:
            agg[vs]["child"] += rc
    print(f"{'对阵':<28}{'发件箱':>8}{'应发笔数':>10}  判定")
    allok = True
    for title, (key, need) in exp.items():
        got = agg.get(title, {"parent": 0, "child": 0})
        sent = got["parent"] or got["child"]  # 母邮件优先,无则子邮件合计
        ok = abs(sent - need) <= 1 and sent > 0
        allok = allok and ok
        flag = "✅已发全" if ok else ("⚠️缺口" if sent > 0 else "❌未发/没找到")
        print(f"{title:<28}{sent:>8}{need:>10}  {flag}")
    print("\n结论:", "全部已发全 ✅" if allok else "有场次缺口/未发,人工复查 ⚠️")

if __name__ == "__main__":
    main()
