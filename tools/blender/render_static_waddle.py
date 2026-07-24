import bpy, sys, math, mathutils, os
glb, outp = sys.argv[-2], sys.argv[-1]
M=math; N=8; CELL=256
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name=='Icosphere': bpy.data.objects.remove(o,do_unlink=True)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
root=meshes[0]
while root.parent: root=root.parent
# bounds (static)
dg=bpy.context.evaluated_depsgraph_get()
mn=mathutils.Vector((1e9,)*3); mx=mathutils.Vector((-1e9,)*3)
for o in meshes:
    ev=o.evaluated_get(dg); m=ev.to_mesh()
    for v in m.vertices:
        w=ev.matrix_world@v.co
        for i in range(3): mn[i]=min(mn[i],w[i]); mx[i]=max(mx[i],w[i])
    ev.to_mesh_clear()
center=(mn+mx)/2; size=max((mx-mn)[i] for i in range(3))
cd=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cd); sc.collection.objects.link(cam)
cd.type='ORTHO'; cd.ortho_scale=size*1.5
ang=M.radians(24); azi=M.radians(40); d=size*8
cam.location=center+mathutils.Vector((M.sin(azi)*M.cos(ang)*d,-M.cos(azi)*M.cos(ang)*d,M.sin(ang)*d))
cam.rotation_euler=(center-cam.location).normalized().to_track_quat('-Z','Y').to_euler()
sc.camera=cam
l=bpy.data.lights.new('S','SUN'); l.energy=4.0; l.angle=M.radians(8); lo=bpy.data.objects.new('S',l); sc.collection.objects.link(lo)
lo.rotation_euler=(M.radians(48),M.radians(12),M.radians(-55))
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.62,0.62,0.64,1); bg.inputs[1].default_value=0.55
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=12
sc.render.film_transparent=True
sc.render.resolution_x=CELL; sc.render.resolution_y=CELL
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
base_rot=tuple(root.rotation_euler); base_loc=tuple(root.location)
tmp='/tmp/_hh'; os.makedirs(tmp,exist_ok=True); paths=[]
for i in range(N):
    p=i/N*2*M.pi
    root.rotation_euler=(base_rot[0], base_rot[1], base_rot[2]+M.radians(5*M.sin(p)))   # waddle yaw
    root.location=(base_loc[0], base_loc[1], base_loc[2]+size*0.012*abs(M.sin(p)))       # tiny bob
    bpy.context.view_layer.update()
    fp=os.path.join(tmp,f'h{i:02d}.png'); sc.render.filepath=fp; bpy.ops.render.render(write_still=True); paths.append(fp)
from PIL import Image
ims=[Image.open(p).convert('RGBA') for p in paths]
W=sum(im.width for im in ims); H=max(im.height for im in ims)
sheet=Image.new('RGBA',(W,H),(0,0,0,0)); x=0
for im in ims: sheet.alpha_composite(im,(x,0)); x+=im.width
sheet.save(outp); print('SHEET',outp,sheet.size,N)
