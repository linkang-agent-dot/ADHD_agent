import bpy, os, math, mathutils

FBX = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew\anniversary2024\Common\Fbx\Anniversary2024.fbx"
TEX = r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew\anniversary2024\High\Texture\P2_Anniversary2024_Diffuse_High.tga"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath=FBX, use_anim=True)

# keep only Lv2 family meshes (body + LV2 cars + top), drop Lv1/shadow
for o in list(bpy.context.scene.objects):
    if o.type == 'MESH':
        n = o.name.lower()
        if ('lv1' in n and 'lv2' not in n) or 'shadow' in n:
            bpy.data.objects.remove(o, do_unlink=True)

img = bpy.data.images.load(TEX)
img.alpha_mode = 'CHANNEL_PACKED'
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
print('MESHES:', [o.name for o in meshes])
for o in meshes:
    for slot in o.material_slots:
        mat = slot.material or bpy.data.materials.new('m')
        slot.material = mat
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        outn = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Roughness'].default_value = 0.85
        nt.links.new(bsdf.outputs['BSDF'], outn.inputs['Surface'])
        texn = nt.nodes.new('ShaderNodeTexImage')
        texn.image = img
        nt.links.new(texn.outputs['Color'], bsdf.inputs['Base Color'])

bpy.context.scene.frame_set(1)
dg = bpy.context.evaluated_depsgraph_get()
xs, ys, zs = [], [], []
for o in meshes:
    oe = o.evaluated_get(dg)
    for c in oe.bound_box:
        v = oe.matrix_world @ mathutils.Vector(c)
        xs.append(v.x); ys.append(v.y); zs.append(v.z)
cx, cy, cz = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2
size = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)) or 1

cam_data = bpy.data.cameras.new('cam'); cam_data.lens = 50
cam = bpy.data.objects.new('cam', cam_data)
bpy.context.scene.collection.objects.link(cam)
direction = mathutils.Vector((1.0, -1.0, 0.75)).normalized()
cam.location = mathutils.Vector((cx, cy, cz)) + direction * size * 2.1
look = mathutils.Vector((cx, cy, cz)) - cam.location
cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
cam_data.clip_end = size * 20
bpy.context.scene.camera = cam
sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.5
sun = bpy.data.objects.new('sun', sun_d)
bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(-15), math.radians(30))

w = bpy.data.worlds['World'] if 'World' in bpy.data.worlds else bpy.data.worlds.new('World')
bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get('Background')
if bg:
    bg.inputs[0].default_value = (1, 1, 1, 1); bg.inputs[1].default_value = 0.7

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 640
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'
for frame, tag in [(1, 'f1'), (30, 'f30')]:
    sc.frame_set(frame)
    sc.render.filepath = os.path.join(OUT, 'AnnivLv2_%s.png' % tag)
    bpy.ops.render.render(write_still=True)
    print('RENDERED', tag)
print('DONE')
