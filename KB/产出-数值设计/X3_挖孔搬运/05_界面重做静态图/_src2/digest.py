# -*- coding: utf-8 -*-
"""prefab 布局摘要：折叠重复兄弟（DayTab(1..4) 只留 1 个）+ 深度限制 + 只留有视觉意义的节点"""
import os, sys, re, json
import prefab_parse as pp

SKIP_SCRIPTS = {"CanvasRenderer", "BetterOutline", "ExOutline", "UIAudio", "ButtonScale",
                "EventTriggerListener", "DOTweenAnimation", "ButtonState", "Canvas",
                "RectTransformScaleParent", "RectTransformScaler", "EffectDisplay"}


def base_name(n):
    return re.sub(r"\s*\(\d+\)$", "", n)


def digest(node, out, maxdepth):
    ind = "  " * node["depth"]
    line = ind + node["name"]
    if not node["active"]:
        line += " [OFF]"
    bits = []
    if node.get("sizeDelta"):
        bits.append("sz%s" % node["sizeDelta"])
    if node.get("anchoredPosition"):
        bits.append("p%s" % node["anchoredPosition"])
    am, aM = node.get("anchorMin"), node.get("anchorMax")
    if am and aM:
        if am == [0, 0] and aM == [1, 1]:
            bits.append("STRETCH")
        else:
            bits.append("a%s%s" % (am, aM))
    if node.get("pivot") and node["pivot"] != [0.5, 0.5]:
        bits.append("piv%s" % node["pivot"])
    if node.get("scale"):
        bits.append("scl%s" % node["scale"])
    if bits:
        line += "  " + " ".join(bits)
    out.append(line)
    if node.get("nestedPrefab"):
        out.append(ind + "  >> " + str(node["nestedPrefab"]).replace("Assets/Res/UI/Prefab/", ""))
        mm = node.get("instMods") or {}
        sd = [mm.get("m_SizeDelta.x"), mm.get("m_SizeDelta.y")]
        ap = [mm.get("m_AnchoredPosition.x"), mm.get("m_AnchoredPosition.y")]
        if any(x is not None for x in sd + ap):
            out.append(ind + "  >> 覆盖 sz=%s pos=%s" % (sd, ap))
    for c in node.get("comps", []):
        s = []
        sc = c.get("script")
        if sc in SKIP_SCRIPTS and not c.get("sprite") and c.get("text") is None:
            continue
        if c.get("sprite") and c["sprite"] != "(none)":
            s.append("IMG " + c["sprite"])
            if c.get("imgType") and c["imgType"] != "Simple":
                s.append(c["imgType"])
            b = c.get("border_LBRT")
            if b and any(b):
                s.append("border(L,B,R,T)=%s" % [int(x) for x in b])
            if c.get("color") and c["color"] != "#FFFFFF":
                s.append(c["color"])
            if c.get("spritePath"):
                s.append(c["spritePath"].replace("Assets/Res/UI/", ""))
        elif c.get("text") is not None:
            t = c["text"]
            s.append("TXT %r fs=%s %s" % (t[:48], int(c.get("fontSize") or 0), c.get("color") or ""))
        elif sc and sc not in SKIP_SCRIPTS:
            s.append(sc)
            for k in ("spacing", "cellSize", "padding_LRTB", "scroll"):
                if c.get(k):
                    s.append("%s=%s" % (k, c[k]))
        if s:
            out.append(ind + "  · " + " ".join(str(x) for x in s))
    if node["depth"] >= maxdepth:
        if node.get("childCount"):
            out.append(ind + "  ...(%d 子节点省略)" % node["childCount"])
        return
    seen = {}
    for k in node.get("children", []):
        b = base_name(k["name"])
        seen[b] = seen.get(b, 0) + 1
        if seen[b] > 1:
            continue
        digest(k, out, maxdepth)
    reps = {k: v for k, v in seen.items() if v > 1}
    if reps:
        out.append(ind + "  [重复兄弟已折叠] " + ", ".join("%s ×%d" % (k, v) for k, v in reps.items()))


if __name__ == "__main__":
    p = sys.argv[1]
    md = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    r = pp.analyze(p)
    out = ["=== %s (GO=%d) ===" % (os.path.basename(p), r["nodeCount"])]
    for n in r["nodes"]:
        digest(n, out, md)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))
