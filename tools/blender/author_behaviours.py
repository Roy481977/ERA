import bpy, sys, math, mathutils, os
base, behaviour, outdir = sys.argv[-3], sys.argv[-2], sys.argv[-1]
M=math
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=base)
sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name=='Icosphere': bpy.data.objects.remove(o,do_unlink=True)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
for pb in arm.pose.bones: pb.rotation_mode='XYZ'
def R(bone,f,x=0,y=0,z=0):
    pb=arm.pose.bones[bone]; pb.rotation_euler=(M.radians(x),M.radians(y),M.radians(z)); pb.keyframe_insert('rotation_euler',frame=f)
def L(bone,f,x=0,y=0,z=0):
    pb=arm.pose.bones[bone]; pb.location=(x,y,z); pb.keyframe_insert('location',frame=f)

FRONT=['frontleg','R_frontleg']; FRONT1=['frontleg1','R_frontleg1']
BACK=['backleg','R_backleg']; BACK1=['backleg1','R_backleg1']

if behaviour=='run':
    N=16
    for f in range(0,N+1,2):
        p=f/N*2*M.pi
        for b in FRONT: R(b,f, x=42*M.sin(p))
        for b in FRONT1: R(b,f, x=-35*max(0,M.sin(p+2)))
        for b in BACK: R(b,f, x=45*M.sin(p+M.pi))
        for b in BACK1: R(b,f, x=-40*max(0,M.sin(p+M.pi+2)))
        R('Hips',f, x=8*M.sin(2*p)); L('Hips',f, z=0.0015*abs(M.sin(2*p)))
        R('chest',f, x=-6*M.sin(2*p))
        R('head',f, x=10+4*M.sin(2*p))
        R('tail',f, x=-22, z=6*M.sin(p))
elif behaviour=='sniff':
    N=32
    for f in range(0,N+1,4):
        p=f/N*2*M.pi
        R('chest',f, x=16)
        R('head',f, x=34+3*M.sin(p), z=9*M.sin(p*0.5))
        R('Hips',f, x=-4); L('Hips',f, z=-0.001)
        for b in FRONT: R(b,f, x=6*M.sin(p))
        R('tail',f, z=5*M.sin(p*0.5))
elif behaviour=='sit':
    N=40
    for f in range(0,N+1,4):
        p=f/N*2*M.pi
        R('Hips',f, x=14); L('Hips',f, z=-0.0022)
        for b in BACK: R(b,f, x=42)
        for b in BACK1: R(b,f, x=-64)
        for b in ['backleg2','R_backleg2']: R(b,f, x=24)
        for b in FRONT: R(b,f, x=-2)
        R('chest',f, x=-16)
        R('head',f, x=-14, y=12*M.sin(p*0.5))
        R('tail',f, x=12, z=6*M.sin(p*0.5))

sc.frame_start=0; sc.frame_end=N
# camera on deformed bounds at mid
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
ang=M.radians(24); azi=M.radians(40); d=size*7
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
frames=[0,N//4,N//2,3*N//4]
for i,f in enumerate(frames):
    sc.frame_set(f); sc.render.filepath=os.path.join(outdir,f'{behaviour}_{i}.png'); bpy.ops.render.render(write_still=True)
print("DONE",behaviour)
