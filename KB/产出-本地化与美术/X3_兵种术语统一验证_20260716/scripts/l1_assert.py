# -*- coding: utf-8 -*-
"""L1 断言：解析 i18n .bytes（protobuf KV）并校验任务书四/五节全部期望值。
用法: python l1_assert.py <i18n_bytes_dir>
"""
import os, sys

def read_varint(b, pos):
    result = 0; shift = 0
    while True:
        byte = b[pos]; pos += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return result, pos
        shift += 7

def parse_i18n(path):
    with open(path, "rb") as f:
        b = f.read()
    d = {}; pos = 0; n = len(b)
    while pos < n:
        tag = b[pos]; pos += 1
        assert tag == 0x0A, f"unexpected tag {tag} at {pos}"
        ln, pos = read_varint(b, pos)
        entry = b[pos:pos+ln]; pos += ln
        # entry: 0x0A len key 0x12 len value
        ep = 0; key = ""; val = ""
        while ep < len(entry):
            etag = entry[ep]; ep += 1
            eln, ep = read_varint(entry, ep)
            payload = entry[ep:ep+eln]; ep += eln
            if etag == 0x0A: key = payload.decode("utf-8")
            elif etag == 0x12: val = payload.decode("utf-8")
        d[key] = val
    return d

# 任务书语言码 -> 文件名
LANG_FILE = {"en":"en","sp":"sp","fr":"fr","de":"de","kr":"kr","tw":"zh","ru":"ru",
             "ua":"ua","jp":"jp","it":"it","pt":"po","th":"th","id":"id","tr":"tr",
             "pl":"pl","cn":"cn"}

# (key, lang, mode, expected)  mode: eq / contains / endswith / not_contains
CHECKS = []
K1 = "TXT_HeroSkillInfo_NewDescUp_9037"
for lang, exp in {
    "en":"Warrior Atk/Def: +{0}", "sp":"Atk/Def Guerrero: +{0}",
    "fr":"Atk/Déf Guerrier : +{0}", "de":"Krieger Angriff/Verteidigung: +{0}",
    "kr":"투사 공/방: +{0}", "tw":"鬥士攻防：{0}", "ru":"Атк/Защ Воина: +{0}",
    "ua":"Атк/Зах Воїна: +{0}", "jp":"ウォリアー攻防: +{0}",
    "it":"Atk/Dif Guerriero: +{0}", "pt":"Atk/Def Guerreiro: +{0}",
    "th":"นักรบ โจ/ป้อ: +{0}", "id":"Atk/Def Petarung: +{0}",
    "tr":"Savaşçı Sld/Sav: +{0}", "pl":"Atk/Obr Wojownika: +{0}",
}.items():
    CHECKS.append(("Key1", K1, lang, "eq", exp))

for lang, exp in {"en":"Commander Route—Warrior","it":"Rotta del Comandante—Guerriero",
    "jp":"指揮官航路-ウォリアー","kr":"지휘관 항로-투사","id":"Jalur Komandan-Petarung"}.items():
    CHECKS.append(("Key2a", "TXT_Route_Name_5000", lang, "eq", exp))
CHECKS.append(("Key2b", "TXT_Route_Name_6000", "en", "contains", "Wavebreaker"))
CHECKS.append(("Key2b", "TXT_Route_Name_6000", "en", "endswith", "—Warrior"))
CHECKS.append(("Key2b", "TXT_Route_Name_6000", "kr", "eq", "파도타기 항로-투사"))
CHECKS.append(("Key2b", "TXT_Route_Name_6000", "jp", "eq", "波砕き航路-ウォリアー"))

K3 = "TXT_HeroSkillInfo_NewDesc_1043"
CHECKS.append(("Key3", K3, "en", "contains", "Every other turn, Warriors deal an extra"))
CHECKS.append(("Key3", K3, "sp", "contains", "Cada 2 turnos, los guerreros"))
CHECKS.append(("Key3", K3, "ru", "contains", "Каждые 2 хода воины"))
CHECKS.append(("Key3", K3, "de", "contains", "die Krieger"))

CHECKS.append(("Key4", "TXT_BuffTemplate_AffixName_220613", "fr", "endswith", "tous les marins sont des guerriers"))

CHECKS.append(("Key5", "TXT_ActvOnline_ActvName_100546", "ru", "eq", "Великий Разгром — Командир Воинов"))
CHECKS.append(("Key5", "TXT_ActvOnline_ActvName_100546", "ua", "eq", "Великий Розгром—Командир Воїнів"))

CHECKS.append(("Key6", "TXT_MemorialCard_GetTips_60", "tw", "eq", "鬥士營地達到14級可獲取"))

# 五、回归检查
for key, m in [("Text_Soldier_fighter", {"en":"Warrior","kr":"투사","jp":"ウォリアー","id":"Petarung"}),
               ("Text_Soldier_hunter",  {"en":"Hunter","kr":"사냥꾼","jp":"ハンター","id":"Pemburu"}),
               ("Text_Soldier_shooter", {"en":"Archer","kr":"소총수","jp":"アーチャー","id":"Penembak"})]:
    for lang, exp in m.items():
        CHECKS.append(("Reg1", key, lang, "eq", exp))
CHECKS.append(("Reg2", "TXT_HeroSkillInfo_NewDesc_1046", "kr", "contains", "광전사"))
CHECKS.append(("Reg2", "TXT_HeroSkillInfo_NewDesc_1046", "kr", "not_contains", "광투사"))
CHECKS.append(("Reg3", "TXT_BuffTemplate_AffixName_120023", "id", "eq", "Serangan prajurit petarung tunggal"))

def main(d):
    langs_needed = sorted({LANG_FILE[c[2]] for c in CHECKS})
    dicts = {}
    for lf in langs_needed:
        p = os.path.join(d, lf + ".bytes")
        dicts[lf] = parse_i18n(p)
    passed = failed = 0
    fails = []
    for group, key, lang, mode, exp in CHECKS:
        lf = LANG_FILE[lang]
        actual = dicts[lf].get(key)
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
    print(f"DIR: {d}")
    print(f"PASS {passed} / FAIL {failed} (total {passed+failed})")
    for g, k, l, m, e, a in fails:
        print(f"  [X] {g} {k} [{l}] {m}")
        print(f"      expect: {e!r}")
        print(f"      actual: {a!r}")
    return failed

if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1]) else 0)
