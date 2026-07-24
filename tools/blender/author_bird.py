#!/usr/bin/env python3
# ERA — bird behaviour authoring (Meshy Smart-Rig skeleton).
# Birds (owl/crow/heron/hedgehog) come off Meshy's Smart Rig (Beta), which is
# fully automatic but produces a GENERIC skeleton: bones named Bone_000..025 in
# a "UniRigArmature", and NO Meshy motion library. So every clip is authored
# here. Because the bone names carry no semantics, run map_bones.py first to
# identify root / spine / wing chains by position before editing WING* below.
#
# Proven on the owl 2026-07-24 (perch + soar -> owl_bird_set.png).
#   ROOT   Bone_000  (whole-body pitch/roll for soar attitude)
#   spine  Bone_002  (head/upper turn for perch)
#   WING*  Bone_005 / Bone_009  (long fore/aft chains — CANDIDATE wing bones;
#          on the owl these read as a slow beat from the plate's overhead view
#          but do NOT yet spread the wing. Confirm true wing bones per animal
#          with map_bones.py before relying on wing-spread.)
#
# Usage: blender-less bpy module:
#   python3 author_bird.py <Character_output.glb> <perch|soar> <outdir>
#
# Roy's flight requirement (birds soar slowly across the sky, then land):
#   soar = the airborne glide clip here. Take-off + land clips and the
#   compositor sky-path traversal are the remaining pieces (see README).
import bpy, sys, math, mathutils, os
glb, behaviour, outdir = sys.argv[-3], sys.argv[-2], sys.argv[-1]
M=math
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name=='Icosphere': bpy.data.objects.remove(o,do_unlink=True)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
for pb in arm.pose.bones: pb.rotation_mode='XYZ'
def R(bone,f,x=0,y=0,z=0):
    pb=arm.pose.bones[bone]; pb.rotation_euler=(M.radians(x),M.radians(y),M.radians(z)); pb.keyframe_insert('rotation_euler',frame=f)
def L(bone,f,x=0,y=0,z=0):
    pb=arm.pose.bones[bone]; pb.location=(x,y,z); pb.keyframe_insert('location',frame=f)
ROOT='Bone_000'
# candidate wing chains (long fore/aft) and spine
WINGL='Bone_005'; WINGR='Bone_009'   # the two long chains off the upper body
if behaviour=='perch':
    N=48
    for f in range(0,N+1,6):
        p=f/N*2*M.pi
        L(ROOT,f, z=0.02*M.sin(p))            # gentle breathing bob
        R('Bone_002',f, y=8*M.sin(p*0.5))     # slow head/upper turn
elif behaviour=='soar':
    N=40
    for f in range(0,N+1,4):
        p=f/N*2*M.pi
        R(ROOT,f, x=62, z=6*M.sin(p))         # pitch to gliding attitude + slow roll
        L(ROOT,f, z=0.05*M.sin(p))            # gentle rise/fall
        R(WINGL,f, x=18+14*M.sin(p))          # slow wing beat
        R(WINGR,f, x=18+14*M.sin(p+0.2))
sc.frame_start=0; sc.frame_end=N
sc.frame_set(N//2); bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for o in bpy.data.objects:
    if o.type!='MESH': continue
    ev=o.evaluated_get(dg); m=ev.to_mesh()
    for v in m.vertices:
        w=ev.matrix_world@v.co
        for i in range(3): mn[i]=min(mn[i],w[i]); mx[i]=max(mx[i],w[i])
    ev.to_mesh_clear()
center=(mn+mx)/2; size=max((mx-mn)[i] for i in range(3))
cd=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cd); sc.collection.objects.link(cam)
cd.type='ORTHO'; cd.ortho_scale=size*1.5
ang=M.radians(20); azi=M.radians(40); d=size*7
cam.location=center+mathutils.Vector((M.sin(azi)*M.cos(ang)*d,-M.cos(azi)*M.cos(ang)*d,M.sin(ang)*d))
cam.rotation_euler=(center-cam.location).normalized().to_track_quat('-Z','Y').to_euler()
sc.camera=cam
l=bpy.data.lights.new('S','SUN'); l.energy=4.0; l.angle=M.radians(8); lo=bpy.data.objects.new('S',l); sc.collection.objects.link(lo)
lo.rotation_euler=(M.radians(48),M.radians(12),M.radians(-55))
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.62,0.62,0.64,1); bg.inputs[1].default_value=0.6
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16
sc.render.film_transparent=True
sc.render.resolution_x=400; sc.render.resolution_y=400
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
os.makedirs(outdir,exist_ok=True)
for i,f in enumerate([0,N//4,N//2,3*N//4]):
    sc.frame_set(f); sc.render.filepath=os.path.join(outdir,f'{behaviour}_{i}.png'); bpy.ops.render.render(write_still=True)
print("DONE",behaviour)
