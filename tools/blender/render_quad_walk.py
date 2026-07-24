import bpy, sys, math, mathutils, os
# ERA — render a quadruped WALK sprite sheet (horizontal strip) from a Meshy
# *_Walking_withSkin.glb. Fixed camera (plate 3/4-from-above), transparent, walks
# in place. A mid-frame doubles as the idle/still (like Milo).
#   render_quad_walk.py <walking_glb> <out_sheet.png> [ncols]
glb, outp = sys.argv[-3], sys.argv[-2]
ncols = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 16
M = math
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    if o.name == 'Icosphere': bpy.data.objects.remove(o, do_unlink=True)
act = bpy.data.actions[0]; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
sc.frame_start, sc.frame_end = f0, f1

def bounds():
    dg = bpy.context.evaluated_depsgraph_get()
    mn = mathutils.Vector((1e9,) * 3); mx = mathutils.Vector((-1e9,) * 3)
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        ev = o.evaluated_get(dg); m = ev.to_mesh()
        for v in m.vertices:
            w = ev.matrix_world @ v.co
            for i in range(3): mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
        ev.to_mesh_clear()
    return mn, mx

# union bounds across the cycle -> fixed ortho scale + center
umn = mathutils.Vector((1e9,) * 3); umx = mathutils.Vector((-1e9,) * 3)
for f in range(f0, f1 + 1, 2):
    sc.frame_set(f); bpy.context.view_layer.update()
    mn, mx = bounds()
    for i in range(3): umn[i] = min(umn[i], mn[i]); umx[i] = max(umx[i], mx[i])
center = (umn + umx) / 2; size = max((umx - umn)[i] for i in range(3))

cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam)
cd.type = 'ORTHO'; cd.ortho_scale = size * 1.5
ang = M.radians(24); azi = M.radians(40); d = size * 8
cam.location = center + mathutils.Vector((M.sin(azi) * M.cos(ang) * d, -M.cos(azi) * M.cos(ang) * d, M.sin(ang) * d))
cam.rotation_euler = (center - cam.location).normalized().to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam
l = bpy.data.lights.new('S', 'SUN'); l.energy = 4.0; l.angle = M.radians(8)
lo = bpy.data.objects.new('S', l); sc.collection.objects.link(lo)
lo.rotation_euler = (M.radians(48), M.radians(12), M.radians(-55))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.62, 0.62, 0.64, 1); bg.inputs[1].default_value = 0.55
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 14
sc.render.film_transparent = True
CELL = 256; sc.render.resolution_x = CELL; sc.render.resolution_y = CELL
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'

tmp = '/tmp/_quadframes'; os.makedirs(tmp, exist_ok=True)
paths = []
for i in range(ncols):
    f = f0 + round(i * (f1 - f0) / ncols)
    sc.frame_set(f); bpy.context.view_layer.update()
    p = os.path.join(tmp, f'q{i:02d}.png'); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    paths.append(p)
# stitch horizontal
from PIL import Image
ims = [Image.open(p).convert('RGBA') for p in paths]
W = sum(im.width for im in ims); H = max(im.height for im in ims)
sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
for im in ims: sheet.alpha_composite(im, (x, 0)); x += im.width
sheet.save(outp)
print('SHEET', outp, sheet.size, ncols, 'frames')
