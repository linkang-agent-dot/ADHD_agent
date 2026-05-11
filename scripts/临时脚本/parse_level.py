import json, sys
from collections import Counter

layer1_str = '{"8":{"unit":35130801},"18":{"unit":35130804},"28":{"unit":35130813},"48":{"unit":35130804},"58":{"unit":35130803},"98":{"unit":35130804},"168":{"unit":35130801},"7":{"unit":35130800},"97":{"unit":35130204,"displaykey":15118258,"drop":35140904},"107":{"unit":35130805},"167":{"unit":35130212,"displaykey":15115659,"drop":35142612},"6":{"unit":35130800},"66":{"unit":35130809},"96":{"unit":35130204,"drop":35140104},"106":{"unit":35130205,"drop":35140105},"116":{"unit":35130205,"drop":35140105},"126":{"unit":35130305,"displaykey":15115536,"drop":35141105,"mineshaft":351519001},"166":{"unit":35130212,"displaykey":15118259,"drop":35141312},"5":{"unit":35130800},"15":{"unit":35130901,"forge":351516001},"65":{"unit":35130203,"displaykey":15118258,"drop":35140903},"75":{"unit":35130202,"drop":35140102},"85":{"unit":35130203,"displaykey":15118259,"drop":35141303},"95":{"unit":35130813},"115":{"unit":35130207,"displaykey":15118258,"drop":35140907},"125":{"unit":35130208,"displaykey":15118259,"drop":35141308},"135":{"unit":35130210,"drop":35140110},"145":{"unit":35130211,"drop":35140111},"155":{"unit":35130212,"displaykey":15115530,"drop":35141012},"165":{"unit":35130211,"drop":35140111},"4":{"unit":35130800},"64":{"unit":35130202,"drop":35140102},"74":{"unit":35130202,"drop":35140102},"84":{"unit":35130203,"drop":35140103},"94":{"unit":35130204,"displaykey":15118259,"drop":35141304},"104":{"unit":35130205,"drop":35140105},"114":{"unit":35130208,"drop":35140108},"124":{"unit":35130209,"drop":35140109},"134":{"unit":35130211,"displaykey":15118257,"drop":35140811},"144":{"unit":35130210,"drop":35140110},"154":{"unit":35130211,"displaykey":15118258,"drop":35140911},"164":{"unit":35130211,"drop":35140111},"3":{"unit":35130800},"63":{"unit":35130202,"displaykey":15118259,"drop":35141302},"73":{"unit":35130203,"drop":35140103},"83":{"unit":35130203,"displaykey":15118258,"drop":35140903},"93":{"unit":35130205,"drop":35140105},"103":{"unit":35130206,"displaykey":15115530,"drop":35141006},"113":{"unit":35130207,"drop":35140107},"123":{"unit":35130209,"drop":35140109},"153":{"unit":35130210,"drop":35140110},"163":{"unit":35130212,"displaykey":15118259,"drop":35141312},"2":{"unit":35130800},"12":{"unit":35131001},"52":{"unit":35130201,"drop":35140101},"62":{"unit":35130202,"drop":35140102},"112":{"unit":35130206,"displaykey":15118258,"drop":35140906},"122":{"unit":35130209,"drop":35140109},"132":{"unit":35130805},"152":{"unit":35130211,"drop":35140111},"162":{"unit":35130212,"displaykey":151104363,"drop":35143806},"1":{"unit":35130800},"51":{"unit":35130201,"drop":35140101},"61":{"unit":35130801},"121":{"unit":35130210,"displaykey":15118259,"drop":35141310},"131":{"unit":35130210,"drop":35140110},"141":{"unit":35130211,"displaykey":151104363,"drop":35143806},"0":{"unit":35130801},"10":{"unit":35130813},"30":{"unit":35130804},"40":{"unit":35130802},"50":{"unit":35130813},"70":{"unit":35130303,"displaykey":15115549,"drop":35141103,"mineshaft":351517001},"110":{"unit":35130814},"120":{"unit":35130813},"140":{"unit":35130804},"150":{"unit":35130805},"170":{"unit":35130406,"drop":35141606,"boss":35130606}}'

layer2_str = '{"448":{"unit":35130813},"488":{"unit":35130813},"447":{"unit":35130217,"displaykey":15118258,"drop":35140917},"457":{"unit":35130216,"displaykey":151104363,"drop":35143804},"467":{"unit":35130814},"477":{"unit":35130814},"487":{"unit":35130222,"displaykey":151104363,"drop":35143804},"497":{"unit":35130223,"displaykey":15118257,"drop":35140823},"406":{"unit":35130308,"displaykey":15115543,"drop":35141108,"mineshaft":351526001},"446":{"unit":35130215,"drop":35140115},"456":{"unit":35130218,"drop":35140118},"466":{"unit":35130219,"drop":35140119},"476":{"unit":35130222,"displaykey":15118259,"drop":35141322},"486":{"unit":35130221,"drop":35140121},"496":{"unit":35130222,"displaykey":151104356,"drop":35143801},"506":{"unit":35130311,"displaykey":15115545,"drop":35141111,"mineshaft":351528001},"405":{"unit":35130211,"drop":35140111},"415":{"unit":35130213,"drop":35140113},"425":{"unit":35130215,"displaykey":15118258,"drop":35140915},"435":{"unit":35130214,"drop":35140114},"445":{"unit":35130216,"displaykey":15118259,"drop":35141316},"455":{"unit":35130803},"465":{"unit":35130219,"drop":35140119},"475":{"unit":35130220,"displaykey":15118258,"drop":35140920},"485":{"unit":35130804},"495":{"unit":35130813},"515":{"unit":35130226,"displaykey":15118258,"drop":35140926},"525":{"unit":35130227,"drop":35140127},"535":{"unit":35130228,"displaykey":15118259,"drop":35141328},"404":{"unit":35130212,"displaykey":15118259,"drop":35141312},"414":{"unit":35130211,"drop":35140111},"424":{"unit":35130213,"drop":35140113},"434":{"unit":35130803},"444":{"unit":35130217,"drop":35140117},"454":{"unit":35130219,"drop":35140119},"464":{"unit":35130220,"displaykey":15118259,"drop":35141320},"474":{"unit":35130219,"drop":35140119},"484":{"unit":35130222,"drop":35140122},"494":{"unit":35130223,"displaykey":15118259,"drop":35141323},"504":{"unit":35130224,"drop":35140124},"514":{"unit":35130225,"drop":35140125},"524":{"unit":35130226,"drop":35140126},"534":{"unit":35130227,"drop":35140127},"403":{"unit":35130210,"drop":35140110},"413":{"unit":35130211,"drop":35140111},"423":{"unit":35130813},"443":{"unit":35130216,"drop":35140116},"453":{"unit":35130219,"drop":35140119},"463":{"unit":35130219,"drop":35140119},"473":{"unit":35130220,"drop":35140120},"483":{"unit":35130221,"drop":35140121},"493":{"unit":35130222,"drop":35140122},"503":{"unit":35130223,"drop":35140123},"513":{"unit":35130803},"523":{"unit":35130225,"drop":35140125},"533":{"unit":35130228,"displaykey":15118258,"drop":35140928},"402":{"unit":35130210,"drop":35140110},"412":{"unit":35130212,"drop":35140112},"422":{"unit":35130214,"drop":35140114},"432":{"unit":35130215,"displaykey":15118259,"drop":35141315},"442":{"unit":35130217,"drop":35140117},"492":{"unit":35130223,"drop":35140123},"502":{"unit":35130224,"drop":35140124},"512":{"unit":35130225,"displaykey":15118259,"drop":35141325},"522":{"unit":35130226,"drop":35140126},"532":{"unit":35130227,"drop":35140127},"401":{"unit":35130211,"displaykey":15118258,"drop":35140911},"431":{"unit":35130216,"drop":35140116},"441":{"unit":35130218,"displaykey":15115531,"drop":35141018},"491":{"unit":35130226,"displaykey":15115532,"drop":35141026},"501":{"unit":35130224,"displaykey":151104356,"drop":35143801},"531":{"unit":35130228,"displaykey":15115659,"drop":35142628},"400":{"unit":35130804},"410":{"unit":35130805},"430":{"unit":35130813},"450":{"unit":35130310,"displaykey":15115559,"drop":35141110,"mineshaft":351527001},"490":{"unit":35130813},"510":{"unit":35130805},"530":{"unit":35130804},"540":{"unit":35130512,"drop":35142712,"shoot_boss":352810843}}'

layer1 = json.loads(layer1_str)
layer2 = json.loads(layer2_str)

def parse_unit(uid):
    base = uid - 35130000
    cat = base // 100
    sub = base % 100
    cats = {2:'ore', 3:'mine', 4:'gate', 5:'end', 6:'boss', 8:'wall', 9:'forge', 10:'cannon'}
    return cats.get(cat, f'unk{cat}'), sub

def get_drop_type(drop_id):
    d = drop_id - 35140000
    d_cat = d // 100
    d_sub = d % 100
    dtypes = {1:'jin',9:'yao',8:'bao',13:'ji',10:'te',11:'dongbao',16:'dibao',26:'te2',27:'tongbao',38:'baika'}
    return dtypes.get(d_cat, f'?{d_cat}'), d_sub

for name, layer in [("LAYER 1 (X=0~17)", layer1), ("LAYER 2 (X=40~54)", layer2)]:
    print(f"\n{'='*60}")
    print(f" {name}")
    print(f"{'='*60}")

    ores = []
    nodes = []
    walls = []

    for pos_str, data in layer.items():
        pos = int(pos_str)
        x = pos // 10
        y = pos % 10
        uid = data['unit']
        cat, sub = parse_unit(uid)

        drop_str = ""
        if 'drop' in data:
            dt, ds = get_drop_type(data['drop'])
            drop_str = f"{dt}{ds}"

        if cat == 'ore':
            ores.append((x, y, sub, drop_str))
        elif cat in ('mine','gate','end','boss'):
            extra = []
            if 'mineshaft' in data: extra.append('mineshaft')
            if 'boss' in data: extra.append('boss')
            if 'shoot_boss' in data: extra.append('shoot_boss')
            nodes.append((x, y, cat, sub, ','.join(extra)))
        elif cat == 'wall':
            walls.append((x, y, sub))

    # Visual grid map (Y=0 bottom, Y=8 top)
    print("\n--- Visual Grid (rows=Y 8->0, cols=X) ---")
    xs = set()
    grid = {}
    for x, y, lv, _ in ores:
        grid[(x,y)] = f"M{lv:02d}"
        xs.add(x)
    for x, y, cat, sub, _ in nodes:
        label = {'mine':'D','gate':'G','end':'E','boss':'B'}[cat]
        grid[(x,y)] = f"{label}{sub:02d}"
        xs.add(x)
    for x, y, sub in walls:
        grid[(x,y)] = f"W{sub:02d}"
        xs.add(x)

    if xs:
        min_x, max_x = min(xs), max(xs)
        # Print header
        print(f"Y\\X", end="")
        for x in range(min_x, max_x+1):
            print(f" {x:>4}", end="")
        print()

        for y in range(8, -1, -1):
            print(f" {y} ", end="")
            for x in range(min_x, max_x+1):
                cell = grid.get((x,y), "  . ")
                print(f" {cell}", end="")
            print()

    # Shortest path analysis
    print("\n--- Shortest Path (Y=3~5 middle rows) ---")
    path_ores = [(x, y, lv) for x, y, lv, _ in sorted(ores) if 3 <= y <= 5]
    if path_ores:
        for x, y, lv in path_ores:
            print(f"  ({x},{y}): ore {lv}")
        path_levels = [lv for _,_,lv in path_ores]
        print(f"\n  Path ore levels: {' -> '.join(str(l) for l in path_levels)}")
        print(f"  Max ore on path: {max(path_levels)}")

    # Stats
    levels = [sub for _,_,sub,_ in ores]
    print(f"\n--- Stats ---")
    print(f"  Total ores: {len(ores)}")
    print(f"  Level range: {min(levels)} ~ {max(levels)}")
    dist = Counter(levels)
    print(f"  Distribution: {dict(sorted(dist.items()))}")

    print("\n--- Key Nodes ---")
    for x, y, cat, sub, extra in sorted(nodes):
        print(f"  ({x},{y}): {cat}{sub} {extra}")
