# -*- coding: utf-8 -*-
"""Blender headless: render each P2 city skin's highest-Lv FBX to PNG.
Run: blender -b -P blender_render_skins.py -- [only_skin_name]
"""
import bpy, os, re, sys, math, json, traceback

ROOT = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRATCH, "renders")
os.makedirs(OUT_DIR, exist_ok=True)

EXCLUDE = {'Animation', 'DrillGround', 'MonkeyNest', 'ResourceStation', 'SecurityBox',
           'SecurityBoxMap', 'SurvivorCamp', 'TreasureChest', 'WonderCity',
           'MaincitySkin', 'CityHallLV6'}

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ONLY = argv[0] if argv else None


def find_fbx(skin_dir):
    """Pick highest-Lv fbx; prefer files with skin-name prefix over bare LV1.FBX."""
    cands = []
    for dp, _, fns in os.walk(skin_dir):
        for f in fns:
            if f.lower().endswith('.fbx'):
                cands.append(os.path.join(dp, f))
    if not cands:
        return None
    def key(p):
        b = os.path.basename(p)
        m = re.search(r'[Ll][Vv]\s*_?(\d+(?:\.\d+)?)', b)
        lv = float(m.group(1)) if m else 0.0
        named = 0 if re.fullmatch(r'(?i)lv\d+(\.\d+)?\.fbx', b) else 1  # prefer named
        return (named, lv, len(b))
    cands.sort(key=key)
    return cands[-1]


def collect_textures(skin_dir):
    tex = {}
    for dp, _, fns in os.walk(skin_dir):
        for f in fns:
            if re.search(r'\.(tga|png|psd|jpg)$', f, re.I):
                tex.setdefault(f.lower(), os.path.join(dp, f))
    return tex


def match_diffuse(mat_name, textures):
    """textures: {lower_filename: path}. Find best diffuse for material name."""
    mn = mat_name.lower().split('.')[0]
    # exact: {mat}_diffuse*
    pats = [mn + '_diffuse', mn + 'diffuse']
    for fn, p in textures.items():
        for pat in pats:
            if fn.startswith(pat):
                return p
    # contains mat name and diffuse
    for fn, p in textures.items():
        if mn in fn and 'diffuse' in fn:
            return p
    # material name without p2_ prefix
    mn2 = re.sub(r'^p2_', '', mn)
    for fn, p in textures.items():
        if mn2 and mn2 in fn and 'diffuse' in fn:
            return p
    # any _high diffuse
    highs = [p for fn, p in sorted(textures.items()) if 'diffuse' in fn and 'high' in fn]
    if highs:
        return highs[0]
    diffs = [p for fn, p in sorted(textures.items()) if 'diffuse' in fn]
    return diffs[0] if diffs else None


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for x in list(coll):
            if x.users == 0:
                coll.remove(x)


def setup_world():
    w = bpy.data.worlds['World'] if 'World' in bpy.data.worlds else bpy.data.worlds.new('World')
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (1, 1, 1, 1)
        bg.inputs[1].default_value = 0.7


def render_skin(name):
    skin_dir = os.path.join(ROOT, name)
    fbx = find_fbx(skin_dir)
    if not fbx:
        return 'no-fbx'
    textures = collect_textures(skin_dir)
    clear_scene()
    try:
        bpy.ops.import_scene.fbx(filepath=fbx, use_anim=False)
    except Exception as e:
        return 'import-fail: %s' % e
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        return 'no-mesh'
    # bind diffuse textures
    for o in meshes:
        for slot in o.material_slots:
            mat = slot.material
            if mat is None:
                mat = bpy.data.materials.new('m')
                slot.material = mat
            mat.use_nodes = True
            nt = mat.node_tree
            for n in list(nt.nodes):
                nt.nodes.remove(n)
            out = nt.nodes.new('ShaderNodeOutputMaterial')
            bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
            bsdf.inputs['Roughness'].default_value = 0.85
            nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
            tp = match_diffuse(mat.name, textures)
            print('MAT', o.name, '|', mat.name, '->', os.path.basename(tp) if tp else 'NONE', flush=True)
            if tp:
                try:
                    img = bpy.data.images.load(tp, check_existing=True)
                    img.alpha_mode = 'CHANNEL_PACKED'  # Unity packs mask into alpha; stop Blender premultiplying RGB to black
                    texn = nt.nodes.new('ShaderNodeTexImage')
                    texn.image = img
                    nt.links.new(texn.outputs['Color'], bsdf.inputs['Base Color'])
                except Exception as e:
                    print('TEXFAIL', tp, e, flush=True)
    # bounding box in world space
    xs, ys, zs = [], [], []
    for o in meshes:
        for c in o.bound_box:
            v = o.matrix_world @ __import__('mathutils').Vector(c)
            xs.append(v.x); ys.append(v.y); zs.append(v.z)
    cx, cy, cz = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2
    size = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)) or 1
    # camera 3/4 view
    cam_data = bpy.data.cameras.new('cam')
    cam_data.lens = 50
    cam = bpy.data.objects.new('cam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    import mathutils
    direction = mathutils.Vector((1.0, -1.0, 0.75)).normalized()
    dist = size * 2.1
    cam.location = mathutils.Vector((cx, cy, cz)) + direction * dist
    look = mathutils.Vector((cx, cy, cz)) - cam.location
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    cam_data.clip_end = dist * 10
    bpy.context.scene.camera = cam
    # sun light
    sun_data = bpy.data.lights.new('sun', 'SUN')
    sun_data.energy = 3.5
    sun = bpy.data.objects.new('sun', sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(-15), math.radians(30))
    # render settings
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 512
    sc.render.resolution_y = 512
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.filepath = os.path.join(OUT_DIR, name + '.png')
    bpy.ops.render.render(write_still=True)
    return 'ok'


setup_world()
results = {}
skins = [ONLY] if ONLY else sorted(
    d for d in os.listdir(ROOT)
    if os.path.isdir(os.path.join(ROOT, d)) and d not in EXCLUDE)
for s in skins:
    try:
        results[s] = render_skin(s)
    except Exception:
        results[s] = 'error: ' + traceback.format_exc(limit=1).replace('\n', ' ')
    print('RENDER', s, '->', results[s], flush=True)

json.dump(results, open(os.path.join(SCRATCH, 'render_results.json'), 'w'), indent=1)
print('DONE', sum(1 for v in results.values() if v == 'ok'), '/', len(results))
