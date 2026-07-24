import bpy, sys
glb = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arms=[o for o in bpy.data.objects if o.type=='ARMATURE']
meshes=[o for o in bpy.data.objects if o.type=='MESH']
print("OBJECTS:", [(o.name,o.type) for o in bpy.data.objects])
for a in arms:
    print(f"ARMATURE {a.name}: {len(a.data.bones)} bones ->", [b.name for b in a.data.bones])
for m in meshes:
    print(f"MESH {m.name}: verts={len(m.data.vertices)} polys={len(m.data.polygons)} mats={[mm.name for mm in m.data.materials]}")
print("ACTIONS:", [(a.name, round(a.frame_range[0]),round(a.frame_range[1])) for a in bpy.data.actions])
