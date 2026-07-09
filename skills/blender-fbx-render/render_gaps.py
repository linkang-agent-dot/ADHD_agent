# -*- coding: utf-8 -*-
"""Render gap skins: convert FBX->glb via FBX2glTF, import glb, render.
Run: blender -b -P render_gaps.py
"""
import bpy, os, re, sys, math, json, subprocess, traceback, mathutils

ROOT = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew"
SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRATCH, "renders")
GLB_DIR = os.path.join(SCRATCH, "glb")
os.makedirs(GLB_DIR, exist_ok=True)
FBX2GLTF = os.path.join(SCRATCH, "FBX2glTF.exe")

GAPS = ['MonkeyKingSkin']


def all_fbx(skin_dir):
    out = []
    for dp, _, fns in os.walk(skin_dir):
        for f in fns:
            if f.lower().endswith('.fbx') and '@' not in f:
                out.append(os.path.join(dp, f))
    def key(p):
        b = os.path.basename(p)
        m = re.search(r'[Ll][Vv]\s*_?(\d+(?:\.\d+)?)', b)
        lv = float(m.group(1)) if m else 0.0
        named = 0 if re.fullmatch(r'(?i)lv\d+(\.\d+)?\.fbx', b) else 1
        return (named, lv, len(b))
    out.sort(key=key, reverse=True)  # best candidate first
    return out


def collect_textures(skin_dir):
    tex = {}
    for dp, _, fns in os.walk(skin_dir):
        for f in fns:
            if re.search(r'\.(tga|png|psd|jpg)$', f, re.I):
                tex.setdefault(f.lower(), os.path.join(dp, f))
    return tex


def match_diffuse(mat_name, textures):
    mn = mat_name.lower().split('.')[0]
    for fn, p in textures.items():
        if fn.startswith(mn + '_diffuse') or fn.startswith(mn + 'diffuse'):
            return p
    for fn, p in textures.items():
        if mn in fn and 'diffuse' in fn:
            return p
    mn2 = re.sub(r'^p2_', '', mn)
    for fn, p in textures.items():
        if mn2 and mn2 in fn and 'diffuse' in fn:
            return p
    highs = [p for fn, p in sorted(textures.items()) if 'diffuse' in fn and 'high' in fn]
    if highs:
        return highs[0]
    diffs = [p for fn, p in sorted(textures.items()) if 'diffuse' in fn]
    return diffs[0] if diffs else None


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights, bpy.data.armatures):
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


def try_import(fbx):
    """Try native FBX import; fallback to FBX2glTF->glb."""
    try:
        bpy.ops.import_scene.fbx(filepath=fbx, use_anim=False)
        if any(o.type == 'MESH' for o in bpy.context.scene.objects):
            return 'fbx'
        clear_scene()
    except Exception:
        clear_scene()
    glb = os.path.join(GLB_DIR, re.sub(r'\W+', '_', os.path.basename(fbx)) + '.glb')
    if not os.path.exists(glb):
        r = subprocess.run([FBX2GLTF, '-b', '-i', fbx, '-o', glb[:-4]],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(glb):
            print('FBX2GLTF-FAIL', os.path.basename(fbx), (r.stderr or r.stdout)[:200], flush=True)
            return None
    try:
        bpy.ops.import_scene.gltf(filepath=glb)
        if any(o.type == 'MESH' for o in bpy.context.scene.objects):
            return 'glb'
    except Exception as e:
        print('GLB-IMPORT-FAIL', e, flush=True)
    clear_scene()
    return None


def render_skin(name):
    skin_dir = os.path.join(ROOT, name)
    textures = collect_textures(skin_dir)
    clear_scene()
    how = None
    for fbx in all_fbx(skin_dir):
        how = try_import(fbx)
        if how:
            print('IMPORTED', name, 'via', how, os.path.basename(fbx), flush=True)
            break
    if not how:
        return 'no-importable-fbx'
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
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
            if tp:
                try:
                    img = bpy.data.images.load(tp, check_existing=True)
                    img.alpha_mode = 'CHANNEL_PACKED'
                    texn = nt.nodes.new('ShaderNodeTexImage')
                    texn.image = img
                    nt.links.new(texn.outputs['Color'], bsdf.inputs['Base Color'])
                except Exception:
                    pass
    xs, ys, zs = [], [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in meshes:
        for c in o.bound_box:
            v = o.matrix_world @ mathutils.Vector(c)
            xs.append(v.x); ys.append(v.y); zs.append(v.z)
    cx, cy, cz = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2
    size = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)) or 1
    cam_data = bpy.data.cameras.new('cam')
    cam_data.lens = 50
    cam = bpy.data.objects.new('cam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    direction = mathutils.Vector((1.0, -1.0, 0.75)).normalized()
    dist = size * 2.1
    cam.location = mathutils.Vector((cx, cy, cz)) + direction * dist
    look = mathutils.Vector((cx, cy, cz)) - cam.location
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    cam_data.clip_end = dist * 10
    bpy.context.scene.camera = cam
    sun_data = bpy.data.lights.new('sun', 'SUN')
    sun_data.energy = 3.5
    sun = bpy.data.objects.new('sun', sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(-15), math.radians(30))
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
for s in GAPS:
    try:
        results[s] = render_skin(s)
    except Exception:
        results[s] = 'error: ' + traceback.format_exc(limit=1).replace('\n', ' ')
    print('RENDER', s, '->', results[s], flush=True)
json.dump(results, open(os.path.join(SCRATCH, 'render_gaps_results.json'), 'w'), indent=1)
print('DONE', sum(1 for v in results.values() if v == 'ok'), '/', len(results))
