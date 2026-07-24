import bpy, sys, math, mathutils
glb, out = sys.argv[-2], sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name=='Icosphere': bpy.data.objects.remove(o, do_unlink=True)
sc.frame_set(12)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
mn=mathutils.Vector((1e9,1e9,1e9)); mx=mathutils.Vector((-1e9,-1e9,-1e9))
for o in bpy.data.objects:
    if o.type!='MESH': continue
    ev=o.evaluated_get(dg); m=ev.to_mesh()
    for v in m.vertices:
        w=ev.matrix_world @ v.co
        for i in range(3): mn[i]=min(mn[i],w[i]); mx[i]=max(mx[i],w[i])
    ev.to_mesh_clear()
center=(mn+mx)/2; size=max((mx-mn)[i] for i in range(3))
print("WORLD BOUNDS min",tuple(round(x,3) for x in mn),"max",tuple(round(x,3) for x in mx),"size",round(size,3))
cam_data=bpy.data.cameras.new('Cam'); cam=bpy.data.objects.new('Cam',cam_data); sc.collection.objects.link(cam)
cam_data.type='ORTHO'; cam_data.ortho_scale=size*1.5
ang=math.radians(30); azi=math.radians(35); d=size*6
cam.location=center+mathutils.Vector((math.sin(azi)*math.cos(ang)*d,-math.cos(azi)*math.cos(ang)*d,math.sin(ang)*d))
cam.rotation_euler=(center-cam.location).normalized().to_track_quat('-Z','Y').to_euler()
sc.camera=cam
l=bpy.data.lights.new('Sun','SUN'); l.energy=4.0; l.angle=math.radians(8); lo=bpy.data.objects.new('Sun',l); sc.collection.objects.link(lo)
lo.rotation_euler=(math.radians(48),math.radians(12),math.radians(-55))
world=bpy.data.worlds.new('W'); sc.world=world; world.use_nodes=True
bg=world.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.62,0.62,0.64,1); bg.inputs[1].default_value=0.6
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24
sc.render.film_transparent=True
sc.render.resolution_x=640; sc.render.resolution_y=640
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
sc.render.filepath=out
bpy.ops.render.render(write_still=True)
print("RENDERED", out)
