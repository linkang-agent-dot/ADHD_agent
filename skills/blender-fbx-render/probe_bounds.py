import bpy, sys, os, mathutils
argv = sys.argv[sys.argv.index('--')+1:]
for path in argv:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    try:
        bpy.ops.import_scene.fbx(filepath=path, use_anim=False)
    except Exception as e:
        print('BOUNDS', path, 'IMPORT-FAIL', str(e)[:80]); continue
    xs, ys, zs = [], [], []
    names = []
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            names.append(o.name)
            for c in o.bound_box:
                v = o.matrix_world @ mathutils.Vector(c)
                xs.append(v.x); ys.append(v.y); zs.append(v.z)
    if xs:
        print('BOUNDS', os.path.basename(path),
              'size=(%.2f, %.2f, %.2f)' % (max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)),
              'meshes=', names[:8])
