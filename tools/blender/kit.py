"""ERA — kit-of-parts bench.
Renders a few elements close up so an iteration costs ~1 minute, not ~8.
Splices clay.py's header (materials, mesh pools, roof, façade kit) so the bench
and the town can never drift apart. Every element lives in clay.py; nothing is
defined twice.

Usage: python3 kit.py out.png [w] [h] [samples]
Env:   LENS FSTOP EXPO SUN_E SUN_A FILL_E BNC_E SKY_S SAT BLOOM
       CAM_D CAM_EL CAM_AZ CAM_TZ  LOOK  CKIND  LAMPS
"""
import sys, os, math

OUT  = sys.argv[1] if len(sys.argv) > 1 else '/tmp/kit.png'
KW   = int(sys.argv[2]) if len(sys.argv) > 2 else 900
KH   = int(sys.argv[3]) if len(sys.argv) > 3 else 600
KS   = int(sys.argv[4]) if len(sys.argv) > 4 else 40

_src = open('/home/claude/era_art/clay.py').read()
_hdr = _src.split('# ---------------------------------------------------------------- the house')[0]
sys.argv = ['clay.py', OUT, str(KW), str(KH), str(KS)]
exec(compile(_hdr, 'clay_header', 'exec'), globals())

def _E(k, d): return float(os.environ.get(k, d))

# =========================================================== bench scene
def bench_house(x, y, ang, w, d, h, slate=False):
    ca, sa = math.cos(ang), math.sin(ang)
    def W(lx, ly, lz):
        return (x + lx*ca - ly*sa, y + lx*sa + ly*ca, lz)
    _wr = R()
    if _wr < 0.66:   wallmat = M['paint'][int(R()*12)]
    elif _wr < 0.90: wallmat = M['plaster'][int(R()*5)]
    else:            wallmat = M['brick'][int(R()*5)]

    house_walls(x, y, ang, w, d, h, wallmat)
    obj('base', mesh_from_bm(lump_box(w+0.14, d+0.14, 0.42, 0.07, 4, 0.008), 'bs'),
        M['stone'][int(R()*4)], W(0, 0, 0.21), (0, 0, ang))

    rh = roof_v2(x, y, ang, w, d, h, slate)
    _cy = rr(-0.5, 0.5)
    chimney(x + math.cos(ang)*rr(-w*0.25, w*0.25) - math.sin(ang)*_cy,
            y + math.sin(ang)*rr(-w*0.25, w*0.25) + math.cos(ang)*_cy,
            ang, h + rh - abs(_cy)*0.5 - 0.05, wallmat,
            kind=os.environ.get('CKIND') or None)

    for side in (-1, 1):                       # gable ends
        bmg = bmesh.new(); t = 0.13
        pts = [(-t, -d/2-0.02, -0.04), (-t, d/2+0.02, -0.04), (-t, 0.0, rh-0.16),
               ( t, -d/2-0.02,  0.0),  ( t, d/2+0.02,  0.0),  ( t, 0.0, rh-0.16)]
        vs = [bmg.verts.new(pp) for pp in pts]
        bmg.faces.new((vs[0], vs[1], vs[2])); bmg.faces.new((vs[5], vs[4], vs[3]))
        bmg.faces.new((vs[0], vs[3], vs[4], vs[1]))
        bmg.faces.new((vs[1], vs[4], vs[5], vs[2]))
        bmg.faces.new((vs[2], vs[5], vs[3], vs[0]))
        bmg.normal_update()
        bmesh.ops.bevel(bmg, geom=list(bmg.verts)+list(bmg.edges)+list(bmg.faces),
                        offset=0.05, segments=3, profile=0.5, affect='EDGES')
        obj('gab', mesh_from_bm(bmg, 'gb'), wallmat,
            W(side*(w/2 - 0.06), 0.0, h), (0, 0, ang))

# ground
bmg = bmesh.new(); bmesh.ops.create_grid(bmg, x_segments=2, y_segments=2, size=40)
_GND = clay('kgnd', (236, 228, 210), 0.92, 0.20, 0.02)
obj('gnd', mesh_from_bm(bmg, 'gd'), _GND, (0, 0, -0.02), (0, 0, 0))

bench_house(0.0,  0.0, 0.00, 6.4, 5.0, 5.6)
bench_house(-9.0, 1.4, 0.16, 5.6, 4.6, 4.0)
bench_house(9.0, -0.9, -0.10, 6.0, 4.8, 6.2, slate=True)
if int(os.environ.get('LAMPS', '1')):
    street_lamp(-4.0, 4.8, 0.3)
    street_lamp(4.6, 4.4, -0.2)

# =========================================================== light + camera
if S.world is None:
    S.world = bpy.data.worlds.new('kw')
S.world.use_nodes = True
_wnt = S.world.node_tree
for n in list(_wnt.nodes):
    if n.type != 'OUTPUT_WORLD': _wnt.nodes.remove(n)
_bg = _wnt.nodes.new('ShaderNodeBackground')
_bg.inputs[0].default_value = (0.80, 0.86, 0.92, 1.0)
_bg.inputs[1].default_value = _E('SKY_S', 0.26)
_wnt.links.new(_bg.outputs[0], _wnt.nodes['World Output'].inputs[0])

sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = _E('SUN_E', 4.2)
sun.angle = math.radians(_E('SUN_A', 11.0)); sun.color = (1.0, 0.94, 0.86)
so = bpy.data.objects.new('sun', sun); COL.objects.link(so)
so.rotation_euler = (math.radians(56), 0, math.radians(-44))

fill = bpy.data.lights.new('fill', 'AREA'); fill.energy = _E('FILL_E', 380)
fill.size = 26; fill.color = (0.90, 0.94, 1.0)
fo = bpy.data.objects.new('fill', fill); COL.objects.link(fo)
fo.location = (-16, 18, 16); fo.rotation_euler = (math.radians(44), 0, math.radians(-140))

bnc = bpy.data.lights.new('bnc', 'AREA'); bnc.energy = _E('BNC_E', 320)
bnc.size = 24; bnc.color = (1.0, 0.95, 0.88)
bo = bpy.data.objects.new('bnc', bnc); COL.objects.link(bo)
bo.location = (14, -16, 6); bo.rotation_euler = (math.radians(96), 0, math.radians(40))

cam = bpy.data.cameras.new('cam'); cam.lens = _E('LENS', 85)
cam.dof.use_dof = True
_cd  = _E('CAM_D', 26.0)
cam.dof.focus_distance = _cd; cam.dof.aperture_fstop = _E('FSTOP', 5.0)
co = bpy.data.objects.new('cam', cam); COL.objects.link(co)
_cel, _caz, _ctz = _E('CAM_EL', 22.0), _E('CAM_AZ', 62.0), _E('CAM_TZ', 3.2)
_cp, _ca = math.radians(_cel), math.radians(_caz)
co.location = (_cd*math.cos(_cp)*math.cos(_ca), _cd*math.cos(_cp)*math.sin(_ca),
               _ctz + _cd*math.sin(_cp))
co.rotation_euler = (math.radians(90.0-_cel), 0, math.radians(_caz+90.0))
S.camera = co

S.render.engine = 'CYCLES'; S.cycles.device = 'CPU'
S.cycles.samples = KS
S.cycles.use_adaptive_sampling = True; S.cycles.adaptive_threshold = 0.02
S.cycles.use_denoising = True
S.cycles.max_bounces = 6; S.cycles.diffuse_bounces = 4
S.render.resolution_x = KW; S.render.resolution_y = KH
S.view_settings.view_transform = 'AgX'
for _lk in (os.environ.get('LOOK', 'AgX - Medium Low Contrast'),
            'AgX - Base Contrast', 'AgX - Medium Contrast'):
    try:
        S.view_settings.look = _lk; break
    except Exception: pass
S.view_settings.exposure = _E('EXPO', -0.30)
S.render.filepath = OUT

_ng = bpy.data.node_groups.new('cmp', 'CompositorNodeTree')
_ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
_rl = _ng.nodes.new('CompositorNodeRLayers')
_go = _ng.nodes.new('NodeGroupOutput')
_hs = _ng.nodes.new('CompositorNodeHueSat')
_hs.inputs['Saturation'].default_value = _E('SAT', 1.06)
_hs.inputs['Value'].default_value = _E('VAL', 1.0)
_gl = _ng.nodes.new('CompositorNodeGlare')
_gl.inputs['Type'].default_value = 'Fog Glow'
_gl.inputs['Quality'].default_value = 'Medium'
_gl.inputs['Threshold'].default_value = 0.92
_gl.inputs['Size'].default_value = 0.40
_gl.inputs['Strength'].default_value = _E('BLOOM', 0.18)
_ng.links.new(_rl.outputs['Image'], _hs.inputs['Image'])
_ng.links.new(_hs.outputs['Image'], _gl.inputs['Image'])
_ng.links.new(_gl.outputs['Image'], _go.inputs['Image'])
S.use_nodes = True
S.compositing_node_group = _ng

print('objects:', len(bpy.data.objects), flush=True)
if int(os.environ.get('BUILD_ONLY', '0')): raise SystemExit(0)
bpy.ops.render.render(write_still=True)
print('WROTE', OUT)
