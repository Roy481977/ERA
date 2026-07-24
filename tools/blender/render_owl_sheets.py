import bpy, sys, math, mathutils, os
# ERA — render owl sprite SHEETS (horizontal strips) for the compositor.
# One FIXED camera per mesh (framed to the widest pose + margin) so frames never
# jump when the compositor swaps clips. Transparent bg, plate 3/4-from-above.
#   render_owl_sheets.py <flight_glb> <perched_glb> <outdir>
flight_glb, perched_glb, outdir = sys.argv[-3], sys.argv[-2], sys.argv[-1]
M=math
CELL=256; SAMPLES=14
os.makedirs(outdir, exist_ok=True)

def load(glb):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    for o in list(bpy.data.objects):
        if o.name=='Icosphere': bpy.data.objects.remove(o,do_unlink=True)
    arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
    for pb in arm.pose.bones: pb.rotation_mode='XYZ'
    return bpy.context.scene, arm

def world_bounds(sc):
    sc.frame_set(sc.frame_start); bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        ev=o.evaluated_get(dg); m=ev.to_mesh()
        for v in m.vertices:
            w=ev.matrix_world@v.co
            for i in range(3): mn[i]=min(mn[i],w[i]); mx[i]=max(mx[i],w[i])
        ev.to_mesh_clear()
    return mn,mx

def setup_scene(sc, center, size, scale=1.2):
    cd=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cd); sc.collection.objects.link(cam)
    cd.type='ORTHO'; cd.ortho_scale=size*scale
    ang=M.radians(22); azi=M.radians(38); d=size*8
    cam.location=center+mathutils.Vector((M.sin(azi)*M.cos(ang)*d,-M.cos(azi)*M.cos(ang)*d,M.sin(ang)*d))
    cam.rotation_euler=(center-cam.location).normalized().to_track_quat('-Z','Y').to_euler()
    sc.camera=cam
    l=bpy.data.lights.new('S','SUN'); l.energy=4.0; l.angle=M.radians(8); lo=bpy.data.objects.new('S',l); sc.collection.objects.link(lo)
    lo.rotation_euler=(M.radians(48),M.radians(12),M.radians(-55))
    w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
    bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.62,0.62,0.64,1); bg.inputs[1].default_value=0.55
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMPLES
    sc.render.film_transparent=True
    sc.render.resolution_x=CELL; sc.render.resolution_y=CELL
    sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'

def R(arm,b,x=0,y=0,z=0):
    pb=arm.pose.bones[b]; pb.rotation_euler=(M.radians(x),M.radians(y),M.radians(z))

# ---- flight mesh: soar / takeoff / land (shared fixed camera) ----
sc,arm=load(flight_glb)
mn,mx=world_bounds(sc); center=(mn+mx)/2; size=max((mx-mn)[i] for i in range(3))
setup_scene(sc, center, size, scale=1.18)
LSH,RSH,LEL,REL,ROOT,NECK='Bone_020','Bone_024','Bone_019','Bone_023','Bone_000','Bone_016'
def flap(a,el=0.4):
    R(arm,LSH,x=+a); R(arm,RSH,x=-a); R(arm,LEL,x=+a*el); R(arm,REL,x=-a*el)

def render_strip(name, frames, poser):
    imgs=[]
    for i,ph in enumerate(frames):
        poser(ph); bpy.context.view_layer.update()
        fp=os.path.join(outdir, f'_{name}_{i:02d}.png'); sc.render.filepath=fp; bpy.ops.render.render(write_still=True)
        imgs.append(fp)
    return imgs

def soar(p):
    a=14*M.sin(p); flap(a); R(arm,ROOT,x=4,z=5*M.sin(p*0.5)); R(arm,NECK,y=6*M.sin(p*0.5))
def takeoff(p):
    a=34*M.sin(p); flap(a,0.5); R(arm,ROOT,x=16+3*M.sin(p)); R(arm,NECK,y=4*M.sin(p))
def land(t):
    a=10+38*t; R(arm,LSH,x=+a,z=+8*t); R(arm,RSH,x=-a,z=-8*t); R(arm,LEL,x=+a*0.6); R(arm,REL,x=-a*0.6); R(arm,ROOT,x=-6-16*t)

NS=14; NT=8; NL=8
soar_f  =[i/NS*2*M.pi for i in range(NS)]
take_f  =[i/NT*2*M.pi for i in range(NT)]
land_f  =[i/(NL-1) for i in range(NL)]
strips={
 'soar':    render_strip('soar', soar_f, soar),
 'takeoff': render_strip('takeoff', take_f, takeoff),
 'land':    render_strip('land', land_f, land),
}

# ---- perched mesh: gentle idle (own fixed camera) ----
sc2,arm2=load(perched_glb)
mn2,mx2=world_bounds(sc2); c2=(mn2+mx2)/2; s2=max((mx2-mn2)[i] for i in range(3))
setup_scene(sc2, c2, s2, scale=1.15)
# perched idle: tiny breathing bob on the root + slow head turn. Bones are the
# perched-mesh Smart-Rig set (Bone_000 root, Bone_002 upper/head on that rig).
NP=8
perch=[]
rootpb=arm2.pose.bones.get('Bone_000'); headpb=arm2.pose.bones.get('Bone_002')
for i in range(NP):
    p=i/NP*2*M.pi
    if rootpb: rootpb.location=(0,0,0.01*M.sin(p));
    if headpb: headpb.rotation_euler=(0,0,M.radians(7*M.sin(p*0.5)))
    bpy.context.view_layer.update()
    fp=os.path.join(outdir,f'_perch_{i:02d}.png'); sc2.render.filepath=fp; bpy.ops.render.render(write_still=True)
    perch.append(fp)
strips['perch']=perch
print("STRIPS", {k:len(v) for k,v in strips.items()})
