# -*- coding: utf-8 -*-
"""
X3 Unity prefab 布局解析器（只读）
用途：dump 节点树 + 每节点 RectTransform 四要素 + Image sprite(guid反查名/路径/spriteBorder) + Text 内容/字号
输出：JSON + 人读 txt
用法：python prefab_parse.py <prefab绝对路径> [--depth N]
"""
import os, sys, re, json, io

ASSETS = r"C:\x3-project\client\Assets"
UIROOT = os.path.join(ASSETS, "Res", "UI")
IDX_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_guid_index.json")


# ---------- guid 索引 ----------
def build_guid_index():
    if os.path.isfile(IDX_CACHE):
        with open(IDX_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    idx = {}
    walks = [os.path.join(ASSETS, "Res")]
    for d in os.listdir(ASSETS):
        p = os.path.join(ASSETS, d)
        if os.path.isdir(p) and d != "Res":
            walks.append(p)
    for wroot in walks:
      only_cs = (os.path.basename(wroot) != "Res")
      for root, dirs, files in os.walk(wroot):
        for fn in files:
            if not fn.endswith(".meta"):
                continue
            if only_cs and not fn.endswith(".cs.meta"):
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    head = f.read(4000)
            except Exception:
                continue
            m = re.search(r"^guid:\s*([0-9a-f]{32})", head, re.M)
            if not m:
                continue
            guid = m.group(1)
            asset = p[:-5]
            rel = os.path.relpath(asset, ASSETS).replace("\\", "/")
            border = None
            bm = re.search(r"spriteBorder:\s*\{x:\s*([-\d.]+),\s*y:\s*([-\d.]+),\s*z:\s*([-\d.]+),\s*w:\s*([-\d.]+)\}", head)
            if bm:
                border = [float(bm.group(i)) for i in (1, 2, 3, 4)]
            pm = re.search(r"spritePivot:\s*\{x:\s*([-\d.]+),\s*y:\s*([-\d.]+)\}", head)
            rec = {"path": "Assets/" + rel, "name": os.path.splitext(os.path.basename(asset))[0]}
            if border:
                rec["border"] = border  # unity: x=left y=bottom z=right w=top
            idx[guid] = rec
            # sub-sprite (sprite sheet) name table
            for sm in re.finditer(r"- name:\s*(\S+)\s*\n\s*internalID:\s*(-?\d+)", head):
                pass
    with open(IDX_CACHE, "w", encoding="utf-8") as f:
        json.dump(idx, f)
    return idx


# ---------- prefab YAML 极简解析 ----------
def parse_docs(path):
    """返回 {fileID: {'cls':int, 'body':str}}"""
    docs = {}
    cur_id = None
    cur_cls = None
    buf = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.match(r"^---\s*!u!(\d+)\s*&(-?\d+)", line)
            if m:
                if cur_id is not None:
                    docs[cur_id] = {"cls": cur_cls, "body": "".join(buf)}
                cur_cls = int(m.group(1))
                cur_id = int(m.group(2))
                buf = []
            else:
                if cur_id is not None:
                    buf.append(line)
    if cur_id is not None:
        docs[cur_id] = {"cls": cur_cls, "body": "".join(buf)}
    return docs


def g_num(body, key):
    m = re.search(r"^\s*%s:\s*(-?[\d.eE+]+)\s*$" % re.escape(key), body, re.M)
    return float(m.group(1)) if m else None


def g_vec2(body, key):
    m = re.search(r"^\s*%s:\s*\{x:\s*(-?[\d.eE+]+),\s*y:\s*(-?[\d.eE+]+)" % re.escape(key), body, re.M)
    return [round(float(m.group(1)), 2), round(float(m.group(2)), 2)] if m else None


def g_guid(body, key):
    m = re.search(r"^\s*%s:\s*\{fileID:\s*(-?\d+)(?:,\s*guid:\s*([0-9a-f]{32}))?" % re.escape(key), body, re.M)
    if not m:
        return None, None
    return int(m.group(1)), m.group(2)


def g_str(body, key):
    m = re.search(r"^\s*%s:\s*(.*)$" % re.escape(key), body, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v.startswith("'") and v.endswith("'"):
        v = v[1:-1]
    if "\\u" in v:
        try:
            v = v.encode("ascii", "backslashreplace").decode("unicode_escape")
        except Exception:
            pass
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return v


def g_children(body):
    m = re.search(r"m_Children:\s*\n((?:\s*-\s*\{fileID:\s*-?\d+\}\s*\n)*)", body)
    if not m:
        return []
    return [int(x) for x in re.findall(r"fileID:\s*(-?\d+)", m.group(1))]


def g_color(body):
    m = re.search(r"m_Color:\s*\{r:\s*([\d.]+),\s*g:\s*([\d.]+),\s*b:\s*([\d.]+),\s*a:\s*([\d.]+)\}", body)
    if not m:
        return None
    r, g, b, a = [float(m.group(i)) for i in (1, 2, 3, 4)]
    return "#%02X%02X%02X" % (int(r * 255), int(g * 255), int(b * 255)) + ("" if a > 0.99 else " a=%.2f" % a)


IMG_TYPE = {0: "Simple", 1: "Sliced", 2: "Tiled", 3: "Filled"}


def analyze(path, max_depth=99, guid_idx=None):
    docs = parse_docs(path)
    if guid_idx is None:
        guid_idx = build_guid_index()

    # GameObjects & transforms
    go = {}       # goID -> {name, active, comps:[fileID]}
    tr = {}       # transformID -> {go, parent, children, rt...}
    comp_owner = {}  # compID -> goID

    for fid, d in docs.items():
        b = d["body"]
        if d["cls"] == 1:  # GameObject
            name = g_str(b, "m_Name") or ""
            act = g_num(b, "m_IsActive")
            comps = [int(x) for x in re.findall(r"component:\s*\{fileID:\s*(-?\d+)\}", b)]
            go[fid] = {"name": name, "active": (act is None or act == 1), "comps": comps}
        elif d["cls"] in (4, 224):  # Transform / RectTransform
            goid, _ = g_guid(b, "m_GameObject")
            pid, _ = g_guid(b, "m_Father")
            rec = {
                "go": goid, "parent": pid, "children": g_children(b),
                "is_rect": d["cls"] == 224,
            }
            if d["cls"] == 224:
                rec["anchorMin"] = g_vec2(b, "m_AnchorMin")
                rec["anchorMax"] = g_vec2(b, "m_AnchorMax")
                rec["anchoredPosition"] = g_vec2(b, "m_AnchoredPosition")
                rec["sizeDelta"] = g_vec2(b, "m_SizeDelta")
                rec["pivot"] = g_vec2(b, "m_Pivot")
                sc = re.search(r"m_LocalScale:\s*\{x:\s*([\d.-]+),\s*y:\s*([\d.-]+)", b)
                if sc and (abs(float(sc.group(1)) - 1) > 0.001 or abs(float(sc.group(2)) - 1) > 0.001):
                    rec["scale"] = [round(float(sc.group(1)), 3), round(float(sc.group(2)), 3)]
            tr[fid] = rec

    for goid, gg in go.items():
        for c in gg["comps"]:
            comp_owner[c] = goid

    # ---- 嵌套 PrefabInstance（1001）：把 stripped transform 还原成「源 prefab 名」 ----
    inst = {}
    for fid, d in docs.items():
        if d["cls"] == 1001:
            b = d["body"]
            _, sguid = g_guid(b, "m_SourcePrefab")
            si = guid_idx.get(sguid, {})
            nm_ = si.get("name") or ("prefab:" + str(sguid))
            # 取 modification 里的 m_Name / m_SizeDelta / m_AnchoredPosition / m_Text
            mods = {}
            for mm in re.finditer(r"propertyPath:\s*(\S+)\s*\n\s*value:\s*(.*)\n", b):
                k, v = mm.group(1), mm.group(2).strip()
                if v != "":
                    mods[k] = v
            inst[fid] = {"src": nm_, "srcPath": si.get("path"), "mods": mods}
    # stripped transform -> 所属 PrefabInstance
    strip_owner = {}
    for fid, d in docs.items():
        if d["cls"] in (4, 224):
            m = re.search(r"m_PrefabInstance:\s*\{fileID:\s*(-?\d+)\}", d["body"])
            if m:
                strip_owner[fid] = int(m.group(1))

    # component info per GameObject
    def comp_info(goid):
        out = []
        for cid in go[goid]["comps"]:
            d = docs.get(cid)
            if not d:
                continue
            cls = d["cls"]
            b = d["body"]
            if cls in (4, 224):
                continue
            if cls == 114:  # MonoBehaviour
                sfid, sguid = g_guid(b, "m_Script")
                sname = None
                if sguid and sguid in guid_idx:
                    sname = guid_idx[sguid]["name"]
                # 常见脚本字段
                extra = {}
                if sname in ("Text", "TextMeshProUGUI") or "Text" in (sname or ""):
                    pass
                # Text (Unity UI Text 是 114 + script guid)
                txt = g_str(b, "m_Text") if re.search(r"^\s*m_Text:", b, re.M) else None
                fs = g_num(b, "m_FontSize")
                sprite_fid, sprite_guid = g_guid(b, "m_Sprite")
                item = {"cls": 114, "script": sname or ("guid:" + str(sguid))}
                if txt is not None:
                    item["text"] = txt
                if fs:
                    item["fontSize"] = fs
                if sprite_guid:
                    si = guid_idx.get(sprite_guid, {})
                    item["sprite"] = si.get("name", sprite_guid)
                    item["spritePath"] = si.get("path")
                    if "border" in si:
                        item["border_LBRT"] = si["border"]
                    t = g_num(b, "m_Type")
                    if t is not None:
                        item["imgType"] = IMG_TYPE.get(int(t), int(t))
                    c = g_color(b)
                    if c:
                        item["color"] = c
                elif sprite_fid == 0 and re.search(r"m_Sprite:", b):
                    c = g_color(b)
                    item["sprite"] = "(none)"
                    if c:
                        item["color"] = c
                # ScrollRect / Layout 关键字段
                for k in ("m_Spacing", "m_ChildAlignment", "m_CellSize", "spacing", "m_Padding"):
                    pass
                sp = g_num(b, "m_Spacing")
                if sp is not None:
                    item["spacing"] = sp
                cs = g_vec2(b, "m_CellSize")
                if cs:
                    item["cellSize"] = cs
                sp2 = g_vec2(b, "m_Spacing")
                if sp2:
                    item["spacing"] = sp2
                pad = re.search(r"m_Padding:\s*\n\s*m_Left:\s*(-?\d+)\s*\n\s*m_Right:\s*(-?\d+)\s*\n\s*m_Top:\s*(-?\d+)\s*\n\s*m_Bottom:\s*(-?\d+)", b)
                if pad:
                    item["padding_LRTB"] = [int(pad.group(i)) for i in (1, 2, 3, 4)]
                if re.search(r"m_Horizontal:\s*0", b) and re.search(r"m_Vertical:\s*1", b):
                    item["scroll"] = "vertical"
                elif re.search(r"m_Horizontal:\s*1", b) and re.search(r"m_Vertical:\s*0", b):
                    item["scroll"] = "horizontal"
                al = g_num(b, "m_Alignment")
                if al is not None and (txt is not None):
                    item["align"] = int(al)
                col = g_color(b)
                if col and "color" not in item:
                    item["color"] = col
                out.append(item)
            elif cls == 222:
                out.append({"cls": 222, "script": "CanvasRenderer"})
            elif cls == 223:
                out.append({"cls": 223, "script": "Canvas"})
            elif cls == 225:
                a = g_num(b, "m_Alpha")
                out.append({"cls": 225, "script": "CanvasGroup", "alpha": a})
        return out

    # find root
    roots = [fid for fid, t in tr.items() if t["parent"] == 0]
    result = {"prefab": path, "nodes": []}

    def walk(tid, depth, path_str):
        t = tr.get(tid)
        if not t:
            return None
        goid = t["go"]
        gg = go.get(goid)
        instref = None
        if gg is None:
            ii = inst.get(strip_owner.get(tid, -1))
            if ii:
                gg = {"name": "<嵌套prefab:%s>" % ii["src"], "active": True, "comps": []}
                instref = ii
            else:
                gg = {"name": "?", "active": True, "comps": []}
        node = {
            "depth": depth, "name": gg["name"], "active": gg["active"],
            "path": path_str,
        }
        if instref:
            node["nestedPrefab"] = instref.get("srcPath") or instref["src"]
            keep = {k: v for k, v in instref["mods"].items()
                    if any(s in k for s in ("m_Name", "m_SizeDelta", "m_AnchoredPosition", "m_AnchorM",
                                            "m_Pivot", "m_Text", "m_IsActive", "m_LocalScale"))}
            if keep:
                node["instMods"] = keep
        if t.get("is_rect"):
            for k in ("anchorMin", "anchorMax", "anchoredPosition", "sizeDelta", "pivot", "scale"):
                if t.get(k):
                    node[k] = t[k]
        ci = comp_info(goid) if goid in go else []
        if ci:
            node["comps"] = ci
        kids = []
        if depth < max_depth:
            for c in t["children"]:
                k = walk(c, depth + 1, path_str + "/" + gg["name"])
                if k:
                    kids.append(k)
        node["childCount"] = len(t["children"])
        if kids:
            node["children"] = kids
        return node

    for r in roots:
        n = walk(r, 0, "")
        if n:
            result["nodes"].append(n)
    result["nodeCount"] = len(go)
    return result


def fmt(node, out, only_visual=True):
    ind = "  " * node["depth"]
    line = ind + node["name"]
    if not node["active"]:
        line += " [INACTIVE]"
    bits = []
    if node.get("sizeDelta"):
        bits.append("size%s" % node["sizeDelta"])
    if node.get("anchoredPosition"):
        bits.append("pos%s" % node["anchoredPosition"])
    if node.get("anchorMin") and node.get("anchorMax"):
        bits.append("anc%s-%s" % (node["anchorMin"], node["anchorMax"]))
    if node.get("pivot"):
        bits.append("piv%s" % node["pivot"])
    if node.get("scale"):
        bits.append("scale%s" % node["scale"])
    if bits:
        line += "  " + " ".join(bits)
    out.append(line)
    if node.get("nestedPrefab"):
        out.append(ind + "    ↳ 源: " + str(node["nestedPrefab"]).replace("Assets/Res/UI/Prefab/", ""))
    if node.get("instMods"):
        mm = node["instMods"]
        out.append(ind + "    ↳ 覆盖: " + ", ".join("%s=%s" % (k.replace("m_", ""), v) for k, v in list(mm.items())[:10]))
    for c in node.get("comps", []):
        s = []
        if c.get("script"):
            s.append(c["script"])
        if c.get("sprite"):
            s.append("sprite=" + str(c["sprite"]))
        if c.get("imgType"):
            s.append(str(c["imgType"]))
        if c.get("border_LBRT"):
            s.append("border(L,B,R,T)=%s" % c["border_LBRT"])
        if c.get("color"):
            s.append("col=" + c["color"])
        if c.get("text") is not None:
            s.append("TEXT=%r" % c["text"][:60])
        if c.get("fontSize"):
            s.append("fs=%s" % int(c["fontSize"]))
        if c.get("spacing"):
            s.append("spacing=%s" % c["spacing"])
        if c.get("cellSize"):
            s.append("cell=%s" % c["cellSize"])
        if c.get("padding_LRTB"):
            s.append("pad(L,R,T,B)=%s" % c["padding_LRTB"])
        if c.get("scroll"):
            s.append("scroll=" + c["scroll"])
        if c.get("spritePath"):
            s.append("[" + c["spritePath"].replace("Assets/Res/UI/", "") + "]")
        if s:
            out.append(ind + "    · " + " | ".join(s))
    for k in node.get("children", []):
        fmt(k, out, only_visual)


if __name__ == "__main__":
    p = sys.argv[1]
    depth = 99
    for i, a in enumerate(sys.argv):
        if a == "--depth":
            depth = int(sys.argv[i + 1])
    r = analyze(p, depth)
    out = []
    out.append("=== %s  (GameObject 数=%d) ===" % (os.path.basename(p), r["nodeCount"]))
    for n in r["nodes"]:
        fmt(n, out)
    txt = "\n".join(out)
    sys.stdout.reconfigure(encoding="utf-8")
    print(txt)
