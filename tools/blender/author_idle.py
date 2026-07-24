import bpy, sys, math, mathutils
base = sys.argv[-2]; outdir = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=base)
sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name=='Icosphere': bpy.data.objects.remove(o, do_unlink=True)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
for pb in arm.pose.bones: pb.rotation_mode='XYZ'
N=48  # loop length
def kf(bone, frame, rot=None, loc=None):
    pb=arm.pose.bones[bone]
    if rot is not None:
        pb.rotation_euler=[math.radians(r) for r in rot]; pb.keyframe_insert('rotation_euler',frame=frame)
    if loc is not None:
        pb.location=loc; pb.keyframe_insert('location',frame=frame)
# IDLE: gentle breathing (Hips bob), slow head sway, tail sway. Sinusoidal loop.
import math as M
for f in range(0,N+1,4):
    t=f/N*2*M.pi
    kf('Hips', f, rot=(1.2*M.sin(t),0,0))
    kf('chest', f, rot=(1.0*M.sin(t+0.5),0,0))
    kf('head', f, rot=(2.0*M.sin(t*0.5), 6*M.sin(t*0.5+1), 0))
    kf('tail', f, rot=(0,0,7*M.sin(t*0.5)))
    kf('tail1', f, rot=(0,0,6*M.sin(t*0.5-0.4)))
    kf('tail3', f, rot=(0,0,8*M.sin(t*0.5-0.8)))
# make it cyclic: loop already sinusoidal over full period
sc.frame_start=0; sc.frame_end=N
# camera framing on deformed mesh at mid frame
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
cd.type='ORTHO'; cd.ortho_scale=size*1.7
ang=math.radians(24); azi=math.radians(40); d=size*7   # front 3/4, slightly above
cam.location=center+mathutils.Vector((math.sin(azi)*math.cos(ang)*d,-math.cos(azi)*math.cos(ang)*d,math.sin(ang)*d))
cam.rotation_euler=(center-cam.location).normalized().to_track_quat('-Z','Y').to_euler()
sc.camera=cam
l=bpy.data.lights.new('S','SUN'); l.energy=4.0; l.angle=math.radians(8); lo=bpy.data.objects.new('S',l); sc.collection.objects.link(lo)
lo.rotation_euler=(math.radians(48),math.radians(12),math.radians(-55))
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.62,0.62,0.64,1); bg.inputs[1].default_value=0.6
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16
sc.render.film_transparent=True
sc.render.resolution_x=400; sc.render.resolution_y=400
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
import os; os.makedirs(outdir,exist_ok=True)
for i,f in enumerate([0,12,24,36]):
    sc.frame_set(f); sc.render.filepath=os.path.join(outdir,f'idle_{i}.png'); bpy.ops.render.render(write_still=True)
print("IDLE_RENDERED")
