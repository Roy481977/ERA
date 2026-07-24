import bpy, sys, math, mathutils, os
# ERA — owl FLIGHT authoring on the spread-wing Smart-Rig mesh.
# Skeleton (from map_bones.py on owl_flight_rigged.glb):
#   ROOT   Bone_000            whole-body pitch/roll
#   NECK   Bone_016 -> 015     head/neck (owl faces forward/down)
#   L wing Bone_020(shoulder)->019->018->017(wrist)  [ -X ]
#   R wing Bone_024(shoulder)->023->022->021(wrist)  [ +X ]
# Wings extend along X; flap = rotate the shoulder so the tip rises/falls in Z.
# Left/right shoulders are mirrored, so the flap sign is inverted between them.
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
def Radd(bone,f,x=0,y=0,z=0):
    pb=arm.pose.bones[bone]
    e=pb.rotation_euler; pb.rotation_euler=(e[0]+M.radians(x),e[1]+M.radians(y),e[2]+M.radians(z)); pb.keyframe_insert('rotation_euler',frame=f)
def L(bone,f,x=0,y=0,z=0):
    pb=arm.pose.bones[bone]; pb.location=(x,y,z); pb.keyframe_insert('location',frame=f)

ROOT='Bone_000'; NECK='Bone_016'
LSH='Bone_020'; RSH='Bone_024'; LEL='Bone_019'; REL='Bone_023'

# flap the shoulders about local X (raise/lower the extended wing). Mirror the
# sign L vs R so both tips rise together. amp = flap amplitude (deg).
def flap(f, amp, elbow=0.4):
    R(LSH,f, x=+amp);          R(RSH,f, x=-amp)
    R(LEL,f, x=+amp*elbow);    R(REL,f, x=-amp*elbow)

if behaviour=='soar':
    # slow glide with a shallow, unhurried beat + gentle body roll
    N=48
    for f in range(0,N+1,4):
        p=f/N*2*M.pi
        flap(f, 14*M.sin(p))                 # shallow ±14 deg beat
        R(ROOT,f, x=4, z=5*M.sin(p*0.5))     # slight nose-up glide + slow roll
        R(NECK,f, y=6*M.sin(p*0.5))          # head drifts as it scans below
elif behaviour=='takeoff':
    # climbing out: deep, laboured downstrokes, body pitched nose-up, feet trailing
    N=32
    for f in range(0,N+1,4):
        p=f/N*2*M.pi
        flap(f, 34*M.sin(p), elbow=0.5)      # deep ±34 deg power beats
        R(ROOT,f, x=16+3*M.sin(p))           # steep nose-up climb attitude
        R(NECK,f, y=4*M.sin(p))
elif behaviour=='land':
    # braking flare: wings thrown UP and cupped forward, body pitched back, decel
    N=28
    for f in range(0,N+1,4):
        t=f/N                                # 0..1 progression into the flare
        amp=10+38*t                          # wings sweep up as it flares
        R(LSH,f, x=+amp, z=+8*t); R(RSH,f, x=-amp, z=-8*t)
        R(LEL,f, x=+amp*0.6);     R(REL,f, x=-amp*0.6)
        R(ROOT,f, x=-6-16*t)                 # pitch back to brake
        R(NECK,f, y=0)

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
cd.type='ORTHO'; cd.ortho_scale=size*1.25
ang=M.radians(22); azi=M.radians(38); d=size*7
cam.location=center+mathutils.Vector((M.sin(azi)*M.cos(ang)*d,-M.cos(azi)*M.cos(ang)*d,M.sin(ang)*d))
cam.rotation_euler=(center-cam.location).normalized().to_track_quat('-Z','Y').to_euler()
sc.camera=cam
l=bpy.data.lights.new('S','SUN'); l.energy=4.0; l.angle=M.radians(8); lo=bpy.data.objects.new('S',l); sc.collection.objects.link(lo)
lo.rotation_euler=(M.radians(48),M.radians(12),M.radians(-55))
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.62,0.62,0.64,1); bg.inputs[1].default_value=0.6
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16
sc.render.film_transparent=True
sc.render.resolution_x=420; sc.render.resolution_y=420
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
os.makedirs(outdir,exist_ok=True)
for i,f in enumerate([0,N//4,N//2,3*N//4]):
    sc.frame_set(f); sc.render.filepath=os.path.join(outdir,f'{behaviour}_{i}.png'); bpy.ops.render.render(write_still=True)
print("DONE",behaviour,"N=",N)
