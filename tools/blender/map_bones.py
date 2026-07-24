#!/usr/bin/env python3
# ERA — position-map a generic (Smart-Rig) skeleton.
# Meshy's Smart Rig names bones Bone_000..025 with no semantics, so before
# authoring bird/generic-rig behaviours, dump each bone's world head position,
# length, and parent, plus the mesh bounds, and read off which bone is the
# root / spine / a wing chain by its normalized position (rel x/y/z of the
# head relative to mesh center, scaled by mesh size).
#
# Usage: python3 map_bones.py <Character_output.glb>
import bpy, sys, mathutils
glb=sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
# mesh bounds for scale ref
import mathutils
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for o in bpy.data.objects:
    if o.type=='MESH' and o.name!='Icosphere':
        for v in o.data.vertices:
            w=o.matrix_world@v.co
            for i in range(3): mn[i]=min(mn[i],w[i]); mx[i]=max(mx[i],w[i])
ctr=(mn+mx)/2; size=max((mx-mn)[i] for i in range(3))
print(f"BOUNDS size={size:.4f} center=({ctr.x:.3f},{ctr.y:.3f},{ctr.z:.3f}) minZ={mn.z:.3f} maxZ={mx.z:.3f} minX={mn.x:.3f} maxX={mx.x:.3f}")
# per bone: head world pos, length, parent
for b in arm.data.bones:
    h=arm.matrix_world@b.head_local; t=arm.matrix_world@b.tail_local
    par=b.parent.name if b.parent else '-'
    # normalize position relative to center & size
    rx=(h.x-ctr.x)/size; ry=(h.y-ctr.y)/size; rz=(h.z-ctr.z)/size
    print(f"{b.name} par={par:9s} head=({h.x:+.3f},{h.y:+.3f},{h.z:+.3f}) rel=(x{rx:+.2f},y{ry:+.2f},z{rz:+.2f}) len={b.length:.4f}")
