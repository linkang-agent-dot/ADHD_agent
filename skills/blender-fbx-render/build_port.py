# -*- coding: utf-8 -*-
"""Port P2 anniversary2024 Lv2 city skin -> X3 Homeland_Circus (dev_festival).
All P2 assets keep their original GUIDs so internal references hold.
"""
import os, re, shutil, uuid, random, io
from PIL import Image

SRC = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew\anniversary2024"
ANIM_SRC = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuilding\CityHall\Common\Animations\CityEffectAnim_SkinMesh.anim"
WT = r"C:\x3\client-circus\client\Assets"
HOMELAND = os.path.join(WT, r"Res\Unit\WorldMap\Homeland")
CIRCUS = os.path.join(HOMELAND, "Homeland_Circus")

P2_PREFAB_GUID = "c3be252249d23be489a48b1cdb84037e"
P2_ROOT_T = "4414977561818611856"
P2_MAT_GUID = "1919c42f1c451934bb1271f083d38ef4"
X3_TEX_GUID = "db1a23416004cc148bc23d8d56b1ad94"  # Homeland_Anniversary_Celebration.png
UPGRADE_INST = "2218148105800070125"
UPGRADE_STRIPPED = "497922850942355807"

BAKED_GUID = uuid.uuid4().hex
CIRCUS_PREFAB_GUID = uuid.uuid4().hex
INST_ID = str(random.getrandbits(62) | (1 << 62))
STRIP_ID = str(random.getrandbits(62) | (1 << 62))

def folder_meta(path):
    meta = path + ".meta"
    if os.path.exists(meta):
        return
    open(meta, "w", newline="\n").write(
        "fileFormatVersion: 2\nguid: %s\nfolderAsset: yes\nDefaultImporter:\n"
        "  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
        % uuid.uuid4().hex)

# ---------- 1. dirs ----------
for sub in ["", "Fbx", "Material", "Texture", "Prefab", "Anim"]:
    d = os.path.join(CIRCUS, sub)
    os.makedirs(d, exist_ok=True)
    folder_meta(d)

# ---------- 2. copy assets (original guids) ----------
copies = [
    (os.path.join(SRC, r"Common\Fbx\Anniversary2024.fbx"), os.path.join(CIRCUS, r"Fbx\Anniversary2024.fbx")),
    (os.path.join(SRC, r"Common\Fbx\Anniversary2024.controller"), os.path.join(CIRCUS, r"Fbx\Anniversary2024.controller")),
    (ANIM_SRC, os.path.join(CIRCUS, r"Anim\CityEffectAnim_SkinMesh.anim")),
]
for s, d in copies:
    shutil.copy2(s, d)
    shutil.copy2(s + ".meta", d + ".meta")

# ---------- 3. baked texture (diffuse TGA -> 1024 PNG) ----------
img = Image.open(os.path.join(SRC, r"High\Texture\P2_Anniversary2024_Diffuse_High.tga")).convert("RGB")
img = img.resize((1024, 1024), Image.LANCZOS)
img.save(os.path.join(CIRCUS, r"Texture\Anniversary2024_Diffuse.png"), optimize=True)
tex_meta = open(os.path.join(HOMELAND, r"Homeland_Anniversary\Texutre\Homeland_Anniversary_Celebration.png.meta"), encoding="utf-8").read()
tex_meta = tex_meta.replace(X3_TEX_GUID, BAKED_GUID)
open(os.path.join(CIRCUS, r"Texture\Anniversary2024_Diffuse.png.meta"), "w", newline="\n").write(tex_meta)

# ---------- 4. material: X3 homeland shader, our texture, P2 mat guid ----------
mat = open(os.path.join(HOMELAND, r"Homeland_Anniversary\Material\homeland.mat"), encoding="utf-8").read()
mat = mat.replace(X3_TEX_GUID, BAKED_GUID)
mat = mat.replace("m_Name: homeland", "m_Name: anniversary2024Pbr")
open(os.path.join(CIRCUS, r"Material\anniversary2024Pbr.mat"), "w", newline="\n").write(mat)
mat_meta = open(os.path.join(SRC, r"High\Material\anniversary2024Pbr.mat.meta"), encoding="utf-8").read()
open(os.path.join(CIRCUS, r"Material\anniversary2024Pbr.mat.meta"), "w", newline="\n").write(mat_meta)

# ---------- 5. P2 prefab copy, strip UpgradeIcon nested instance ----------
ptxt = open(os.path.join(SRC, r"High\Anniversary2024Lv2.prefab"), encoding="utf-8").read()
header, _, body = ptxt.partition("--- !u!")
blocks = ["--- !u!" + b for b in ("\n" + "--- !u!").join([body]).split("--- !u!") if b.strip()]
# simpler robust split:
parts = re.split(r"(?m)^(?=--- !u!)", ptxt)
head = parts[0]
blocks = parts[1:]
kept = []
removed = 0
for b in blocks:
    first = b.splitlines()[0]
    if ("&" + UPGRADE_INST) in first or ("&" + UPGRADE_STRIPPED) in first:
        removed += 1
        continue
    kept.append(b)
new_p = head + "".join(kept)
new_p = new_p.replace("  - {fileID: %s}\n" % UPGRADE_STRIPPED, "")
assert "eb1db9c56d7e4ac4a928090a685c967d" not in new_p, "UpgradeIcon refs remain"
assert removed == 2, "expected to remove 2 blocks, removed %d" % removed
open(os.path.join(CIRCUS, r"Prefab\Anniversary2024Lv2.prefab"), "w", newline="\n").write(new_p)
shutil.copy2(os.path.join(SRC, r"High\Anniversary2024Lv2.prefab.meta"),
             os.path.join(CIRCUS, r"Prefab\Anniversary2024Lv2.prefab.meta"))

# ---------- 6. Homeland_Circus.prefab (clone X3 skeleton) ----------
sk = open(os.path.join(HOMELAND, "Homeland_Anniversary.prefab"), encoding="utf-8").read()
parts = re.split(r"(?m)^(?=--- !u!)", sk)
head, blocks = parts[0], parts[1:]
REMOVE_IDS = {"1805895003110536268", "4475408423230332897", "3177427837962797075", "5588738071872860589"}
kept = []
for b in blocks:
    first = b.splitlines()[0]
    m = re.search(r"&(\d+)", first)
    if m and m.group(1) in REMOVE_IDS:
        continue
    kept.append(b)
assert len(blocks) - len(kept) == 4, "expected removing 4 blocks, removed %d" % (len(blocks) - len(kept))
sk2 = head + "".join(kept)
# swap island child ref -> stripped nested-instance transform
assert "  - {fileID: 4475408423230332897}\n" in sk2
sk2 = sk2.replace("  - {fileID: 4475408423230332897}\n", "  - {fileID: %s}\n" % STRIP_ID)
sk2 = sk2.replace("m_Name: Homeland_Anniversary", "m_Name: Homeland_Circus")

def mod(prop, val):
    return ("    - target: {fileID: %s, guid: %s,\n        type: 3}\n"
            "      propertyPath: %s\n      value: %s\n"
            "      objectReference: {fileID: 0}\n" % (P2_ROOT_T, P2_PREFAB_GUID, prop, val))

mods = "".join([
    mod("m_RootOrder", "0"),
    mod("m_LocalScale.x", "0.9"), mod("m_LocalScale.y", "0.9"), mod("m_LocalScale.z", "0.9"),
    mod("m_LocalPosition.x", "0"), mod("m_LocalPosition.y", "-2.06"), mod("m_LocalPosition.z", "0"),
    mod("m_LocalRotation.w", "1"), mod("m_LocalRotation.x", "0"),
    mod("m_LocalRotation.y", "0"), mod("m_LocalRotation.z", "0"),
    mod("m_LocalEulerAnglesHint.x", "0"), mod("m_LocalEulerAnglesHint.y", "0"),
    mod("m_LocalEulerAnglesHint.z", "0"),
])
inst = ("--- !u!1001 &%s\nPrefabInstance:\n  m_ObjectHideFlags: 0\n  serializedVersion: 2\n"
        "  m_Modification:\n    serializedVersion: 3\n"
        "    m_TransformParent: {fileID: 8450762641144410508}\n"
        "    m_Modifications:\n%s"
        "    m_RemovedComponents: []\n    m_RemovedGameObjects: []\n"
        "    m_AddedGameObjects: []\n    m_AddedComponents: []\n"
        "  m_SourcePrefab: {fileID: 100100000, guid: %s, type: 3}\n"
        % (INST_ID, mods, P2_PREFAB_GUID))
stripped = ("--- !u!4 &%s stripped\nTransform:\n"
            "  m_CorrespondingSourceObject: {fileID: %s, guid: %s,\n    type: 3}\n"
            "  m_PrefabInstance: {fileID: %s}\n  m_PrefabAsset: {fileID: 0}\n"
            % (STRIP_ID, P2_ROOT_T, P2_PREFAB_GUID, INST_ID))
if not sk2.endswith("\n"):
    sk2 += "\n"
sk2 += inst + stripped
circus_prefab = os.path.join(HOMELAND, "Homeland_Circus.prefab")
open(circus_prefab, "w", newline="\n").write(sk2)
pm = open(os.path.join(HOMELAND, "Homeland_Anniversary.prefab.meta"), encoding="utf-8").read()
pm = re.sub(r"guid: [0-9a-f]{32}", "guid: " + CIRCUS_PREFAB_GUID, pm, count=1)
open(circus_prefab + ".meta", "w", newline="\n").write(pm)

# ---------- 7. DK registration ----------
disp_path = os.path.join(WT, r"Editor\Config\DisplayKey\Display_Model.asset")
disp = open(disp_path, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in disp[:2000] else "\n"
entry = ("  - key: Homeland_Circus" + nl + "    type: Model" + nl + "    desc: " + nl +
         "    guid: " + CIRCUS_PREFAB_GUID + nl + "    exportCode: 0" + nl)
if not disp.endswith(nl):
    disp += nl
disp += entry
open(disp_path, "w", newline="").write(disp)

path_path = os.path.join(WT, r"Res\Config\DisplayKey\Path_Model.asset")
pth = open(path_path, encoding="utf-8", newline="").read()
nl2 = "\r\n" if "\r\n" in pth[:2000] else "\n"
key_anchor = "    - DK_Homeland_christmas" + nl2
assert key_anchor in pth
pth = pth.replace(key_anchor, key_anchor + "    - DK_Homeland_Circus" + nl2, 1)
val_anchor = ("    - key: DK_Homeland_christmas" + nl2)
i = pth.find(val_anchor)
assert i > 0
j = pth.find("    - key:", i + len(val_anchor))
assert j > 0
val_entry = ("    - key: DK_Homeland_Circus" + nl2 +
             "      objPath: Assets/Res/Unit/WorldMap/Homeland/Homeland_Circus.prefab" + nl2)
pth = pth[:j] + val_entry + pth[j:]
open(path_path, "w", newline="").write(pth)

# ---------- 8. validations ----------
keys = re.findall(r"^    - (DK_\S+)\r?$", pth, re.M)
vals = re.findall(r"^    - key: (DK_\S+)\r?$", pth, re.M)
assert keys == vals, "Path_Model keys/values not parallel! %d vs %d" % (len(keys), len(vals))
low = [k.lower() for k in keys]
assert low == sorted(low), "Path_Model keys not sorted case-insensitively"
print("OK Path_Model parallel:", len(keys), "keys, sorted ok")
print("BAKED_GUID", BAKED_GUID)
print("CIRCUS_PREFAB_GUID", CIRCUS_PREFAB_GUID)
for root, _, fns in os.walk(CIRCUS):
    for f in fns:
        print("  ", os.path.relpath(os.path.join(root, f), HOMELAND))
print("done")
