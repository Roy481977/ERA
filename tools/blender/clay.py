"""ERA — clay-diorama proof. Blender/Cycles, headless.
Implements the seven laws in era/design/visual-law-clay-diorama.md.
Usage: python3 clay.py out.png [width] [height] [samples]
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Euler

OUT   = sys.argv[1] if len(sys.argv) > 1 else '/tmp/clay.png'
W     = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
H     = int(sys.argv[3]) if len(sys.argv) > 3 else 800
SAMP  = int(sys.argv[4]) if len(sys.argv) > 4 else 96

rng = random.Random(1337)
R   = rng.random
def rr(a, b): return a + (b - a) * R()

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
COL = bpy.context.collection

# ---------------------------------------------------------------- materials
def srgb(c):
    return tuple(((x/255.0)**2.2) for x in c)

def clay(name, rgb255, rough=0.82, sheen=0.0, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    c = srgb(rgb255)
    b.inputs['Base Color'].default_value = (*c, 1)
    b.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.25
    if sss > 0 and 'Subsurface Weight' in b.inputs:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.12, 0.08, 0.05)
    if sheen > 0 and 'Sheen Weight' in b.inputs:
        b.inputs['Sheen Weight'].default_value = sheen
        b.inputs['Sheen Roughness'].default_value = 0.6
    return m

def brick(name, c1, c2, mortar, scale=1.0, rough=0.86, bump=0.55):
    """Red brick with real coursing — English town, not fairytale plaster."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    mp.inputs['Location'].default_value = (rr(0,4), rr(0,4), rr(0,4))
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*srgb(c1), 1)
    br.inputs['Color2'].default_value = (*srgb(c2), 1)
    br.inputs['Mortar'].default_value  = (*srgb(mortar), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.015
    br.inputs['Mortar Smooth'].default_value = 0.35
    br.inputs['Bias'].default_value = 0.0
    br.inputs['Brick Width'].default_value = 0.225
    br.inputs['Row Height'].default_value = 0.075
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
    cmb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['X'], add.inputs[0])
    nt.links.new(sep.outputs['Y'], add.inputs[1])
    nt.links.new(add.outputs[0], cmb.inputs['X'])
    nt.links.new(sep.outputs['Z'], cmb.inputs['Y'])
    nt.links.new(cmb.outputs['Vector'], br.inputs['Vector'])
    nt.links.new(br.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(br.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.22
    return m

# Law 5 — warm, muted, narrow
M = {}
M['plaster'] = [clay('pl%d'%i, c, 0.86, 0.22, 0.06) for i, c in enumerate(
    [(250,244,230), (244,236,218), (252,248,238), (246,238,220), (240,230,210)])]
# painted render — the joy. Seaside-terrace colours, saturated but chalky.
# render walls: creams and warm sands, with a few sun-baked accents
M['paint'] = [clay('pa%d'%i, c, 0.86, 0.24, 0.06) for i, c in enumerate(
    [(250,244,230), (246,238,216), (252,248,240), (242,232,212), (248,240,224),
     (244,196,120), (238,214,168), (250,232,196), (232,180,128), (246,226,186),
     (206,224,216), (244,206,176)])]
# front doors — every one a different colour
# doors, shutters, window frames — the teal signature of the reference
M['door'] = [clay('do%d'%i, c, 0.66, 0.40) for i, c in enumerate(
    [( 46,168,178), ( 30,144,158), ( 68,190,196), ( 22,124,140), ( 92,204,204),
     (166, 88, 56), (140, 72, 48), ( 40,158,170), ( 56,178,186), (184,110, 66)])]
TEAL  = [clay('tl%d'%i, c, 0.62, 0.35) for i, c in enumerate(
    [( 52,176,186), ( 36,150,164), ( 74,196,200), ( 28,132,148), ( 90,206,206)])]
# red brick — the 1980s English town. Five stocks, all a bit different.
M['brick'] = [
    brick('bk0', (206,148,104), (186,128, 88), (238,232,218), 1.00),
    brick('bk1', (216,160,116), (194,138, 96), (240,234,220), 0.94),
    brick('bk2', (196,136, 96), (176,118, 80), (236,230,216), 1.06),
    brick('bk3', (222,168,124), (200,146,102), (242,236,222), 0.90),
    brick('bk4', (210,152,108), (190,132, 92), (238,232,218), 1.02)]
M['roof_t']  = [clay('rt%d'%i, c, 0.82, 0.10) for i, c in enumerate(
    [(214, 98, 52), (196, 84, 46), (232,124, 70), (204,116, 82), (222,142, 86)])]
M['roof_s']  = [clay('rs%d'%i, c, 0.74, 0.14) for i, c in enumerate(
    [(108,120,132), ( 92,104,118), (124,136,148), ( 84, 96,110), (114,128,142)])]
M['timber']  = clay('tim', (172,132, 96), 0.84, 0.18)
M['stone']   = [clay('st%d'%i, c, 0.86, 0.15) for i, c in enumerate(
    [(236,228,212), (226,216,198), (244,238,224), (218,208,190)])]
M['moss']    = [clay('mo%d'%i, c, 0.94, 0.35, 0.05) for i, c in enumerate(
    [( 96,162, 62), ( 78,140, 54), (112,178, 74), ( 64,124, 48), (128,190, 84)])]
M['grass']   = [clay('gr%d'%i, c, 0.93, 0.32, 0.04) for i, c in enumerate(
    [(104,172, 66), ( 88,152, 56), (120,186, 78), ( 76,138, 50)])]
M['leaf']    = [clay('lf%d'%i, c, 0.92, 0.30, 0.06) for i, c in enumerate(
    [( 88,156, 64), ( 70,134, 54), (104,170, 74), (120,184, 86), ( 58,116, 50)])]
M['bark']    = clay('bk', (122, 92, 66), 0.88, 0.12)
M['glass']   = clay('gl', (36, 92,104), 0.55)
M['flower']  = [clay('fl%d'%i, c, 0.85, 0.4) for i, c in enumerate(
    [(252,250,244), (250,140,132), (250,196, 90), (244,164,182), (252,158, 96),
     (246,120,104), (250,208,138), (238,132,150)])]
M['dirt']    = clay('dt', (150,128,102), 0.94)
WHITE        = clay('wht', (246,244,238), 0.55)
# --- the finesse palette: solid saturated greens, crisp neutral paving ---
CANOPY = [clay('cn%d'%i, c, 0.90, 0.14, 0.03) for i, c in enumerate(
    [( 66,132, 52), ( 52,112, 46), ( 80,150, 60), ( 42, 96, 42), ( 92,162, 68),
     ( 58,122, 48)])]
CONIF  = [clay('pn%d'%i, c, 0.88, 0.22, 0.04) for i, c in enumerate(
    [( 46,104, 64), ( 34, 86, 54), ( 58,120, 72), ( 28, 72, 48)])]
LAWN   = clay('lawn', (120,186, 70), 0.93, 0.18, 0.02)
PAVEM  = clay('pavm', (232,225,208), 0.84, 0.08)
HEDGE  = clay('hdg',  ( 62,124, 52), 0.92, 0.20, 0.04)
# A hedge is a clipped *mass*, not a wall. Four tones and a heavy bevel is what
# separates a hedgerow from a green fence at this scale.
HEDGES = [clay('hd%d'%i, c, 0.92, 0.22, 0.05) for i, c in enumerate(
    [( 58,118, 50), ( 72,138, 58), ( 46,100, 44), ( 84,150, 66)])]
SOIL   = clay('soil', (156,122, 86), 0.95, 0.04)
# Reference 4's ground is not one green — it is a quilt of *differently managed*
# parcels: mown, grazed, cut for hay, ploughed. That variation is what makes the
# open ground read as land instead of a tablecloth.
FIELD  = [clay('fd%d'%i, c, 0.94, 0.16, 0.02) for i, c in enumerate(
    [( 96,178, 52), ( 48,110, 40), (162,214, 84), ( 74,150, 44),
     (186,206, 92), (234,214,112), (204,198, 76), (206,166, 72),
     (148,110, 70), (118,190, 58), ( 40, 96, 44), (238,224,140)])]
M['water']   = clay('wt', (150,176,164), 0.14)

# ---------------------------------------------------------------- geometry helpers
def mesh_from_bm(bm, name):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.shade_smooth()
    return me

def lump_box(w, d, h, bev=0.09, seg=4, wobble=0.0):
    """A thumb-pressed box — Law 1."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co.x *= w; v.co.y *= d; v.co.z *= h
    bmesh.ops.bevel(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                    offset=bev, segments=seg, profile=0.5, affect='EDGES')
    if wobble:
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
        for v in bm.verts:
            v.co += Vector((rr(-1,1), rr(-1,1), rr(-1,1))) * wobble
    return bm

def lump_sphere(r, subd=2, wobble=0.22, squash=1.0):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subd, radius=r)
    for v in bm.verts:
        v.co *= 1.0 + rr(-wobble, wobble)
        v.co.z *= squash
    return bm

def obj(name, me, mat, loc=(0,0,0), rot=(0,0,0), sc=(1,1,1)):
    o = bpy.data.objects.new(name, me)
    if mat is not None and len(me.materials) == 0:
        me.materials.append(mat)
    o.location = loc; o.rotation_euler = rot; o.scale = sc
    COL.objects.link(o)
    return o

def linked(name, me, loc, rot=(0,0,0), sc=(1,1,1)):
    o = bpy.data.objects.new(name, me)
    o.location = loc; o.rotation_euler = rot; o.scale = sc
    COL.objects.link(o)
    return o

# ---------------------------------------------------------------- shared meshes
# moss clumps — Law 2. Five shades, several shapes, all reusable.
MOSS = []
for i in range(10):
    bm = lump_sphere(0.26, 2, 0.34, 0.62)
    me = mesh_from_bm(bm, 'moss%d' % i)
    me.materials.append(M['moss'][i % 5])
    MOSS.append(me)

TUFT = []
for i in range(8):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=5,
                          radius1=0.13, radius2=0.008, depth=0.62)
    for v in bm.verts:
        if v.co.z > 0: v.co.x += rr(-0.11, 0.11); v.co.y += rr(-0.11, 0.11)
    me = mesh_from_bm(bm, 'tuft%d' % i)
    me.materials.append(M['grass'][i % 4])
    TUFT.append(me)

SHRUB = []
for i in range(8):
    bm = lump_sphere(0.62, 2, 0.30, 0.74)
    me = mesh_from_bm(bm, 'shrub%d' % i)
    me.materials.append(M['leaf'][i % 5])
    SHRUB.append(me)

FLOWER = []
for i in range(10):
    bm = lump_sphere(0.070, 1, 0.3, 0.8)
    me = mesh_from_bm(bm, 'fl%d' % i)
    me.materials.append(M['flower'][i % 8])
    FLOWER.append(me)

COBBLE = []
for i in range(8):
    bm = lump_sphere(0.185, 2, 0.16, 0.34)
    me = mesh_from_bm(bm, 'cb%d' % i)
    me.materials.append(M['stone'][i % 4])
    COBBLE.append(me)

TILE_T, TILE_S = [], []
for i in range(5):
    bm = lump_box(0.135, 0.115, 0.020, 0.014, 2)
    me = mesh_from_bm(bm, 'tt%d' % i); me.materials.append(M['roof_t'][i]); TILE_T.append(me)
    bm = lump_box(0.135, 0.115, 0.020, 0.014, 2)
    me = mesh_from_bm(bm, 'ts%d' % i); me.materials.append(M['roof_s'][i]); TILE_S.append(me)

STONE = []
for i in range(6):
    bm = lump_sphere(0.34, 2, 0.24, 0.72)
    me = mesh_from_bm(bm, 'sn%d' % i); me.materials.append(M['stone'][i % 4]); STONE.append(me)

# ---------------------------------------------------------------- scatterers
def scatter_moss(pts, n_each=1, scale=(0.6, 1.5)):
    """Retired. The micro-lush read as dirt; the reference is clean stone."""
    return
    for (x, y, z) in pts:
        for _ in range(n_each):
            s = rr(*scale)
            linked('mo', MOSS[int(R()*10)],
                   (x+rr(-0.07,0.07), y+rr(-0.07,0.07), z+rr(-0.02,0.02)),
                   (rr(0,3.14), rr(0,3.14), rr(0,6.28)),
                   (s, s, s*rr(0.6,1.0)))

def moss_line(a, b, density=9.0, jitter=0.10, clump=0.55, scale=(0.55,1.5)):
    """Uneven band of moss along a seam — thick in places, absent in others."""
    a, b = Vector(a), Vector(b)
    L = (b-a).length
    n = max(2, int(L*density))
    pts = []
    for i in range(n):
        t = i/(n-1)
        if R() > clump: continue
        p = a.lerp(b, t) + Vector((rr(-jitter,jitter), rr(-jitter,jitter), rr(-0.02,0.02)))
        pts.append(tuple(p))
    scatter_moss(pts, 1, scale)

def ground_cover(cx, cy, rad, n, ground_z=0.0, tufts=True, flowers=0.25, shrubs=0.06):
    """Law 4 — no bare ground."""
    for _ in range(n):
        a = R()*6.283; d = rad*math.sqrt(R())
        x, y = cx+math.cos(a)*d, cy+math.sin(a)*d
        r = R()
        if r < shrubs:
            s = rr(0.6, 1.5)
            linked('sh', SHRUB[int(R()*8)], (x, y, ground_z+0.16*s),
                   (rr(-0.15,0.15), rr(-0.15,0.15), rr(0,6.28)), (s, s, s*rr(0.7,1.1)))
        elif r < shrubs+flowers:
            linked('fl', FLOWER[int(R()*10)], (x, y, ground_z+rr(0.10,0.26)),
                   (0,0,0), (1,1,1))
            linked('tf', TUFT[int(R()*8)], (x, y, ground_z+0.13),
                   (rr(-0.25,0.25), rr(-0.25,0.25), rr(0,6.28)), (1,1,rr(0.7,1.3)))
        elif tufts and r < shrubs+flowers+0.18:
            s = rr(0.8, 1.5)
            linked('sh', SHRUB[int(R()*8)], (x, y, ground_z+0.16*s),
                   (rr(-0.1,0.1), rr(-0.1,0.1), rr(0,6.28)), (s, s, s*0.9))

def _nrm(wr):
    return (-math.sin(wr), math.cos(wr))


# ---------------------------------------------------------------- the roof
# One corrugated mesh per slope instead of ~900 tile sticks per house.
# Pantile: a rounded barrel roll every TILE_W with a flat pan between,
# courses stepping at the tile butt, closed off at eave and ridge.
TILE_W  = 0.33      # roll-to-roll pitch across the slope
ROLL_F  = 0.52      # fraction of that occupied by the round roll
ROLL_H  = 0.052     # roll height
COURSE  = 0.34      # course length down the slope
LIP     = 0.050     # how proud a tile butt sits
RTHICK  = 0.075     # slab thickness
_VRG = clay('vrg', (248, 242, 228), 0.84, 0.16, 0.04)

def _pan(u, v, slen=None):
    """Height of the tile surface above the bare slope plane."""
    ci = int(v / COURSE)
    cs = (v / COURSE) - ci
    ri = int(math.floor(u / TILE_W))
    ph = (u / TILE_W) - ri
    roll = ROLL_H * math.sin(math.pi * ph / ROLL_F) if ph < ROLL_F else 0.0
    roll *= 0.93 + 0.14 * (((ri * 7919) % 7) / 6.0)      # hand-laid, each roll its own
    z = roll + LIP * (cs ** 5)
    if slen is not None:
        e = min(1.0, max(0.0, (v - (slen - 0.16)) / 0.16))
        r = min(1.0, max(0.0, (0.14 - v) / 0.14))
        k = max(e, r)
        z = z * (1.0 - k) + (ROLL_H * 1.02) * k          # eave + ridge closure
    return z

def roof_slope(span, slen, mat, base, side, pitch, apex, ang, sag=0.05):
    """One tiled slope, authored in HOUSE-LOCAL coords so the only object
    rotation is ang about Z."""
    cp, sp = math.cos(pitch), math.sin(pitch)
    nu = max(6, int(span / 0.070))
    nv = max(4, int(slen / 0.075))
    bm = bmesh.new()
    grid = []
    for j in range(nv + 1):
        v = slen * j / nv
        row = []
        for i in range(nu + 1):
            u = -span/2 + span * i / nu
            dz = _pan(u, v, slen) + sag * (1.0 - math.cos(u / max(0.8, span*0.55) * 1.4))
            row.append(bm.verts.new((u, side*(v*cp + dz*sp), apex - v*sp + dz*cp)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = (grid[j][i], grid[j][i+1], grid[j+1][i+1], grid[j+1][i])
            bm.faces.new(f if side > 0 else tuple(reversed(f)))
    bm.normal_update()
    r = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    vs = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vs, vec=(0, -side*sp*RTHICK, -cp*RTHICK))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = mesh_from_bm(bm, 'rfs')
    o = obj('slope', me, mat, base, (0, 0, ang))
    for pg in me.polygons: pg.use_smooth = True
    return o

def ridge_cap(span, mat, origin, ang, rad=0.185, cap=0.40):
    """A rounded half-tube of ridge tiles, radius pulsing per cap."""
    bm = bmesh.new()
    nL = max(6, int(span / 0.075)); nA = 9
    grid = []
    for i in range(nL + 1):
        u = -span/2 + span * i / nL
        rd = rad * (0.96 + 0.10 * abs(math.sin(math.pi * u / cap)))
        row = []
        for k in range(nA + 1):
            a = math.pi * k / nA
            row.append(bm.verts.new((u, math.cos(a)*rd*1.18, math.sin(a)*rd)))
        grid.append(row)
    for i in range(nL):
        for k in range(nA):
            bm.faces.new((grid[i][k], grid[i][k+1], grid[i+1][k+1], grid[i+1][k]))
    bm.normal_update()
    r = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    vs = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vs, vec=(0, 0, -0.05))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = mesh_from_bm(bm, 'rdg')
    o = obj('ridge', me, mat, origin, (0, 0, ang))
    for pg in me.polygons: pg.use_smooth = True
    return o

def roof_v2(x, y, ang, w, d, h, slate=False, over=0.30):
    """Returns ridge_h. Builds both slopes, fascias, verges and the ridge."""
    ca, sa = math.cos(ang), math.sin(ang)
    def W(lx, ly, lz):
        return (x + lx*ca - ly*sa, y + lx*sa + ly*ca, lz)
    pitch   = rr(0.42, 0.54)
    ridge_h = (d/2) * math.tan(pitch)
    mats = M['roof_s'] if slate else M['roof_t']
    mat  = mats[int(R()*5)]
    span = w + 0.46
    slen = (d/2 + over) / math.cos(pitch)
    apex = h + ridge_h + 0.18          # battens lift the tile plane clear of the wall head
    for side in (-1, 1):
        roof_slope(span, slen, mat, (x, y, 0.0), side, pitch, apex, ang)
        ey = side * (d/2 + over - 0.06)
        ez = apex - slen * math.sin(pitch)
        obj('fas', mesh_from_bm(lump_box(span - 0.04, 0.14, 0.26, 0.05, 3, 0.004), 'fa'),
            _VRG, W(0, ey, ez - 0.21), (0, 0, ang))
        _cp2, _sp2 = math.cos(pitch), math.sin(pitch)
        _th = -pitch if side > 0 else math.pi + pitch
        for _sx in (-1, 1):
            _mid = slen * 0.5
            obj('vrg', mesh_from_bm(lump_box(0.11, slen + 0.06, 0.19, 0.04, 3, 0.004), 'vg'),
                _VRG, W(_sx*(span/2 - 0.045), side*_mid*_cp2, apex - _mid*_sp2 - 0.075),
                (_th, 0, ang))
    ridge_cap(span + 0.06, mat, W(0, 0, apex + 0.045), ang)
    return ridge_h + 0.10

# ================================================================ the façade kit
# Walls are no longer solid boxes with decals stuck on them. Every opening is a
# REAL hole through a wall of real thickness, so a window has a reveal, a jamb
# and a shadow. That single change is most of the distance to the reference.
from mathutils import Matrix

WTHK   = 0.30                      # wall thickness -> depth of every reveal
WIN_W  = 0.74
WIN_H  = 1.06
_DRESS = clay('drs', (244, 237, 222), 0.84, 0.16, 0.03)   # dressed stone surround
_JOIN  = clay('joi', (250, 246, 236), 0.58, 0.30)         # painted joinery
_IRONB = clay('irb', (50, 54, 52), 0.48, 0.10)            # wrought iron
_POT   = clay('pot', (198, 108,  62), 0.78, 0.12)
_IRON  = _IRONB
_LGLS  = clay('lgls', (250, 238, 206), 0.30, 0.06)

def cube_into(bm, w, d, h, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Add one box to an existing bmesh. Many parts, one mesh, one object."""
    m = (Matrix.Translation(Vector(loc))
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Matrix.Diagonal(Vector((w, d, h, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)

def _mi(bm, n0, idx):
    bm.faces.ensure_lookup_table()
    for f in bm.faces[n0:]:
        f.material_index = idx

def _face(bm, vs):
    try:
        bm.faces.new(vs)
    except ValueError:
        pass

def _flat(me):
    for p in me.polygons:
        p.use_smooth = False
    return me

def _seal(bm, bev=0.010, seg=2):
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if bev:
        bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                        offset=bev, segments=seg, profile=0.5, affect='EDGES',
                        clamp_overlap=True)
    return bm

def multi(bm, name, mats, loc, rot):
    me = mesh_from_bm(bm, name)
    for m in mats:
        me.materials.append(m)
    _flat(me)
    return obj(name, me, None, loc, rot)

# ---------------------------------------------------------------- wall panel
def wall_panel(width, height, t, openings, bev=0.022):
    """A wall slab in the XZ plane: outer face at y=0, mass extruded to +y.
    `openings` are (x0, x1, z0, z1) rectangles punched clean through."""
    bm = bmesh.new()
    xs = sorted({-width/2, width/2} | {v for o in openings for v in (o[0], o[1])})
    zs = sorted({0.0, height}       | {v for o in openings for v in (o[2], o[3])})
    F = [[bm.verts.new((xs[i], 0.0, zs[j])) for i in range(len(xs))] for j in range(len(zs))]
    B = [[bm.verts.new((xs[i], t,   zs[j])) for i in range(len(xs))] for j in range(len(zs))]
    def hole(cx, cz):
        for (a, b, c, e) in openings:
            if a < cx < b and c < cz < e:
                return True
        return False
    for j in range(len(zs) - 1):
        for i in range(len(xs) - 1):
            if hole((xs[i] + xs[i+1]) / 2, (zs[j] + zs[j+1]) / 2):
                continue
            _face(bm, (F[j][i], F[j][i+1], F[j+1][i+1], F[j+1][i]))
            _face(bm, (B[j][i], B[j+1][i], B[j+1][i+1], B[j][i+1]))
    def ring(i0, i1, j0, j1):
        for i in range(i0, i1):
            _face(bm, (F[j0][i], F[j0][i+1], B[j0][i+1], B[j0][i]))
            _face(bm, (F[j1][i], B[j1][i], B[j1][i+1], F[j1][i+1]))
        for j in range(j0, j1):
            _face(bm, (F[j][i0], B[j][i0], B[j+1][i0], F[j+1][i0]))
            _face(bm, (F[j][i1], F[j+1][i1], B[j+1][i1], B[j][i1]))
    ring(0, len(xs) - 1, 0, len(zs) - 1)
    for (a, b, c, e) in openings:
        ring(xs.index(a), xs.index(b), zs.index(c), zs.index(e))
    bm.normal_update()
    return _seal(bm, bev, 2)

# ---------------------------------------------------------------- window unit
# material slots: 0 dressed stone   1 joinery   2 glass   3 shutter   4 timber
#                 5 iron            6 flower
def window_mesh(ow, oh, t, sill=True, shutters=True, box=False, open_a=None,
                arch=False):
    bm = bmesh.new()
    gy = t * 0.70                       # how far back in the reveal the sash sits

    n = len(bm.faces)                                        # --- glass
    cube_into(bm, ow - 0.03, 0.035, oh - 0.03, (0, gy + 0.06, 0))
    _mi(bm, n, 2)

    n = len(bm.faces)                                        # --- casement
    fr = 0.060
    for (cx, cz, bw, bh) in ((0, oh/2 - fr/2, ow, fr), (0, -oh/2 + fr/2, ow, fr),
                             (-ow/2 + fr/2, 0, fr, oh), (ow/2 - fr/2, 0, fr, oh)):
        cube_into(bm, bw, 0.060, bh, (cx, gy, cz))
    cube_into(bm, 0.034, 0.055, oh - fr*2, (0, gy - 0.006, 0))          # mullion
    cube_into(bm, ow - fr*2, 0.055, 0.030, (0, gy - 0.006, oh * 0.16))  # transom
    _mi(bm, n, 1)

    n = len(bm.faces)                                        # --- dressed surround
    sw = 0.105
    cube_into(bm, ow + 2*sw, 0.055, sw, (0, -0.024, oh/2 + sw/2))
    for sx in (-1, 1):
        cube_into(bm, sw, 0.055, oh + sw, (sx * (ow + sw) / 2, -0.024, sw/2))
    if arch:                                                  # keystone
        cube_into(bm, 0.16, 0.075, 0.20, (0, -0.034, oh/2 + sw))
    if sill:
        cube_into(bm, ow + 0.34, 0.22, 0.080, (0, -0.062, -oh/2 - 0.045))
        cube_into(bm, ow + 0.26, 0.17, 0.050, (0, -0.038, -oh/2 - 0.105))
    _mi(bm, n, 0)

    if shutters:                                             # --- louvred shutters
        n = len(bm.faces)
        if open_a is None:
            open_a = rr(0.55, 1.45) if R() < 0.78 else 0.0
        lw = ow / 2 + 0.03
        lh = oh + 0.07
        for d_ in (1, -1):
            th_ = open_a * (0.55 + 0.45 * R())
            hx = -d_ * (ow / 2 + 0.040)
            n0 = len(bm.verts)
            cube_into(bm, lw, 0.042, lh, (lw/2, 0, 0))                  # backing
            for sx in (-1, 1):                                          # stiles
                cube_into(bm, 0.055, 0.060, lh, (lw/2 + sx*(lw/2 - 0.028), 0, 0))
            for sz in (-1, 1):                                          # rails
                cube_into(bm, lw, 0.060, 0.075, (lw/2, 0, sz*(lh/2 - 0.038)))
            nsl = 7
            for k in range(nsl):
                zz = -lh/2 + 0.085 + (k + 0.5) * (lh - 0.17) / nsl
                cube_into(bm, lw - 0.09, 0.052, (lh - 0.17) / nsl * 0.66,
                          (lw/2, -0.016, zz), (0.34, 0, 0))
            bm.verts.ensure_lookup_table()
            phi = math.atan2(-math.sin(th_), d_ * math.cos(th_))
            mx = Matrix.Translation(Vector((hx, -0.048, 0))) @ Matrix.Rotation(phi, 4, 'Z')
            bmesh.ops.transform(bm, verts=bm.verts[n0:], matrix=mx)
        _mi(bm, n, 3)

    if box:                                                  # --- flower box
        n = len(bm.faces)
        cube_into(bm, ow + 0.10, 0.17, 0.15, (0, -0.145, -oh/2 - 0.21))
        cube_into(bm, ow + 0.16, 0.20, 0.035, (0, -0.145, -oh/2 - 0.14))
        _mi(bm, n, 4)

    return _seal(bm, 0.009, 2)

SHUTTER = TEAL + [clay('sh%d'%i, c, 0.60, 0.34) for i, c in enumerate(
    [(104, 132, 106), (74, 104,  92), (168, 122,  74),
     (140,  86,  62), (188, 158, 104), (92, 118, 138)])]

def window_mats(wallmat, shm=None):
    return [_DRESS, _JOIN, M['glass'], shm or SHUTTER[int(R()*len(SHUTTER))],
            M['timber'], _IRONB]

# ---------------------------------------------------------------- door unit
def door_mesh(ow, oh, t, planks=6):
    bm = bmesh.new()
    gy = t * 0.62
    n = len(bm.faces)                                        # --- leaf + planks
    cube_into(bm, ow - 0.04, 0.055, oh - 0.05, (0, gy, 0))
    pw_ = (ow - 0.12) / planks
    for k in range(planks):
        cube_into(bm, pw_ * 0.86, 0.030, oh - 0.16,
                  (-((ow - 0.12) / 2) + (k + 0.5) * pw_, gy - 0.040, -0.02))
    _mi(bm, n, 3)
    n = len(bm.faces)                                        # --- ironmongery
    cube_into(bm, ow - 0.16, 0.045, 0.055, (0, gy - 0.062, oh * 0.22))
    cube_into(bm, ow - 0.16, 0.045, 0.055, (0, gy - 0.062, -oh * 0.26))
    cube_into(bm, 0.075, 0.070, 0.075, (ow * 0.30, gy - 0.070, -0.02))
    _mi(bm, n, 5)
    n = len(bm.faces)                                        # --- fanlight
    cube_into(bm, ow - 0.16, 0.035, 0.22, (0, gy + 0.02, oh/2 - 0.20))
    _mi(bm, n, 2)
    n = len(bm.faces)                                        # --- surround + step
    sw = 0.135
    cube_into(bm, ow + 2*sw, 0.070, sw, (0, -0.030, oh/2 + sw/2))
    for sx in (-1, 1):
        cube_into(bm, sw, 0.070, oh + sw, (sx * (ow + sw) / 2, -0.030, sw/2))
    cube_into(bm, ow + 0.44, 0.44, 0.09, (0, -0.20, -oh/2 + 0.045))
    cube_into(bm, ow + 0.62, 0.62, 0.09, (0, -0.28, -oh/2 - 0.045))
    _mi(bm, n, 0)
    return _seal(bm, 0.010, 2)

def door_mats():
    return [_DRESS, _JOIN, M['glass'], M['door'][int(R()*10)], M['timber'], _IRONB]

# ---------------------------------------------------------------- balcony
def balcony_mesh(bw, proj=0.62, hgt=0.86):
    """Corbelled stone slab with a wrought-iron rail. Slots: 0 stone, 5 iron."""
    bm = bmesh.new()
    n = len(bm.faces)
    cube_into(bm, bw, proj, 0.10, (0, -proj/2 + 0.02, 0))
    cube_into(bm, bw - 0.10, proj - 0.10, 0.05, (0, -proj/2 + 0.02, -0.075))
    for sx in (-1, 1):                                       # corbels
        cube_into(bm, 0.16, proj * 0.62, 0.20,
                  (sx * (bw/2 - 0.14), -proj * 0.30, -0.20), (0.38, 0, 0))
    _mi(bm, n, 0)
    n = len(bm.faces)
    nb = max(5, int(bw / 0.17))
    for k in range(nb):                                      # balusters
        bx = -bw/2 + 0.09 + k * (bw - 0.18) / (nb - 1)
        cube_into(bm, 0.030, 0.030, hgt, (bx, -proj + 0.11, hgt/2 + 0.05))
    for sy in (0, 1):                                        # returns
        for k in range(3):
            cube_into(bm, 0.030, 0.030, hgt,
                      (-bw/2 + 0.09 + sy * (bw - 0.18),
                       -proj + 0.11 + k * (proj - 0.16) / 2.6, hgt/2 + 0.05))
    cube_into(bm, bw - 0.10, 0.055, 0.055, (0, -proj + 0.11, hgt + 0.05))
    cube_into(bm, bw - 0.10, 0.045, 0.045, (0, -proj + 0.11, 0.30))
    for sy in (0, 1):
        cube_into(bm, 0.055, proj - 0.16, 0.055,
                  (-bw/2 + 0.09 + sy * (bw - 0.18), -proj/2 + 0.03, hgt + 0.05))
    _mi(bm, n, 5)
    return _seal(bm, 0.008, 2)

def balcony_mats():
    return [M['stone'][int(R()*4)], _JOIN, M['glass'], TEAL[int(R()*5)],
            M['timber'], _IRONB]

# ---------------------------------------------------------------- the shell
def house_walls(x, y, ang, w, d, h, wallmat, t=WTHK, balconies=True):
    """Four punched wall panels + every opening's furniture. Returns nothing;
    the roof and base course are still the caller's business."""
    ca, sa = math.cos(ang), math.sin(ang)
    def W(lx, ly, lz):
        return (x + lx*ca - ly*sa, y + lx*sa + ly*ca, lz)
    two = h > 3.7
    rows = [1.24] + ([h - 1.28] if two else [])
    shm = SHUTTER[int(R()*5)] if R() < 0.62 else SHUTTER[int(R()*len(SHUTTER))]
    quoin = R() < 0.34
    strng = two and R() < 0.55
    plan = [(0.0,  d/2, math.pi,     w, True),
            (0.0, -d/2, 0.0,         w, False),
            ( w/2, 0.0, math.pi/2,   d, False),
            (-w/2, 0.0, -math.pi/2,  d, False)]
    for (lx0, ly0, rel, pw, is_front) in plan:
        pang = ang + rel
        pcs, psn = math.cos(pang), math.sin(pang)
        org = W(lx0, ly0, 0.0)
        # openings never crowd a corner: keep 0.80 of solid wall at each end
        usable = pw - 1.60
        nwin = max(1, int(round(usable / 1.85)))
        step = usable / nwin
        slots = [-usable/2 + (k + 0.5) * step for k in range(nwin)]
        dslot = int(R() * nwin) if is_front else -1
        opens, units = [], []
        for k, cx in enumerate(slots):
            for fi, cz in enumerate(rows):
                if k == dslot and fi == 0:
                    continue
                if not is_front and R() < 0.20:
                    continue
                ww_ = min(WIN_W * rr(0.94, 1.08), step - 0.55)
                wh_ = WIN_H * rr(0.94, 1.06)
                # upper-storey french door onto a balcony — the signature detail
                bal = (balconies and fi > 0 and (is_front or R() < 0.25) and R() < 0.60)
                if bal:
                    head = cz + wh_/2
                    ww_  = min(max(ww_, 0.92), step - 0.45)
                    wh_  = min(1.92, head - 0.42)
                    cz   = head - wh_/2
                if cz + wh_/2 > h - 0.22:
                    continue
                opens.append((cx - ww_/2, cx + ww_/2, cz - wh_/2, cz + wh_/2))
                units.append((cx, cz, ww_, wh_, fi, bal))
        dh_ = 2.10
        if dslot >= 0:
            dcx = slots[dslot]
            opens.append((dcx - 0.48, dcx + 0.48, 0.0, dh_))
        bmp = wall_panel(pw, h, t, opens)
        obj('wal', _flat(mesh_from_bm(bmp, 'wal')), wallmat, org, (0, 0, pang))
        btm = bmesh.new()
        cube_into(btm, pw + 0.10, 0.11, 0.15, (0, -0.038, h - 0.11))       # cornice
        cube_into(btm, pw + 0.05, 0.07, 0.07, (0, -0.020, h - 0.23))
        if strng:
            cube_into(btm, pw + 0.04, 0.075, 0.10, (0, -0.022, rows[1] - 0.86))
        if quoin:
            nq = max(4, int(h / 0.52))
            for sx in (-1, 1):
                for q in range(nq):
                    qw = 0.34 if q % 2 else 0.22
                    cube_into(btm, qw, 0.055, 0.26,
                              (sx * (pw/2 - qw/2 + 0.012), -0.024, 0.16 + q * 0.52))
        obj('trm', _flat(mesh_from_bm(_seal(btm, 0.014, 2), 'trm')),
            _DRESS, org, (0, 0, pang))
        for (cx, cz, ww_, wh_, fi, bal) in units:
            bm = window_mesh(ww_, wh_, t,
                             sill=(not bal),
                             shutters=(R() < 0.88),
                             box=(not bal and R() < 0.34),
                             arch=(R() < 0.16),
                             open_a=(rr(0.85, 1.5) if bal and R() < 0.85 else None))
            multi(bm, 'win', window_mats(wallmat, shm),
                  (org[0] + cx*pcs, org[1] + cx*psn, cz), (0, 0, pang))
            if bal:
                multi(balcony_mesh(ww_ + 0.66), 'bal', balcony_mats(),
                      (org[0] + cx*pcs, org[1] + cx*psn, cz - wh_/2 - 0.05),
                      (0, 0, pang))
        if dslot >= 0:
            dcx = slots[dslot]
            multi(door_mesh(0.96, dh_, t), 'dor', door_mats(),
                  (org[0] + dcx*pcs, org[1] + dcx*psn, dh_/2), (0, 0, pang))

# ---------------------------------------------------------------- the chimney
# Mediterranean, not Victorian: a squat plastered shaft, a corbelled cap slab,
# and either terracotta pots or a little tiled hood on four legs.
def chimney(x, y, ang, top_z, mat, kind=None, scale=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    def W(lx, ly, lz):
        return (x + lx*ca - ly*sa, y + lx*sa + ly*ca, lz)
    if kind is None:
        kind = 'hood' if R() < 0.45 else 'pot'
    sw = 0.60 * scale
    sd = 0.52 * scale
    sh = rr(0.62, 0.92) * scale
    obj('cfl', mesh_from_bm(lump_box(sw+0.16, sd+0.16, 0.12, 0.03, 3, 0.004), 'cf'),
        _VRG, W(0, 0, top_z + 0.03), (0, 0, ang))
    obj('chm', mesh_from_bm(lump_box(sw, sd, sh, 0.055, 4, 0.006), 'cs'),
        mat, W(0, 0, top_z + sh/2 + 0.06), (0, 0, ang))
    obj('ccb', mesh_from_bm(lump_box(sw+0.13, sd+0.13, 0.075, 0.028, 3, 0.003), 'c1'),
        mat, W(0, 0, top_z + sh + 0.10), (0, 0, ang))
    cap_z = top_z + sh + 0.14
    if kind == 'pot':
        n = 1 if R() < 0.6 else 2
        for i in range(n):
            ox = 0.0 if n == 1 else (-1 + 2*i) * sw * 0.26
            ph = rr(0.24, 0.40) * scale
            obj('cpt', mesh_from_bm(lump_sphere(0.105*scale, 2, 0.10, 2.6), 'cp'),
                _POT, W(ox, 0, cap_z + ph*0.55), (0, 0, rr(0, 3.14)),
                (1.0, 1.0, ph/0.26))
            obj('cpr', mesh_from_bm(lump_box(0.20*scale, 0.20*scale, 0.05, 0.02, 3), 'cr'),
                _POT, W(ox, 0, cap_z + ph + 0.02), (0, 0, ang))
    else:
        lh = 0.24 * scale
        for gx in (-1, 1):
            for gy in (-1, 1):
                obj('clg', mesh_from_bm(lump_box(0.085, 0.085, lh, 0.02, 2), 'cl'),
                    mat, W(gx*sw*0.36, gy*sd*0.36, cap_z + lh/2), (0, 0, ang))
        hz = cap_z + lh
        hw, hd = sw + 0.34, sd + 0.30
        hp = 0.40
        for side in (-1, 1):
            sl = (hd/2) / math.cos(hp)
            bm = bmesh.new()
            cp2, sp2 = math.cos(hp), math.sin(hp)
            g = []
            for j in range(3):
                v = sl * j / 2.0
                g.append([bm.verts.new((-hw/2 + hw*i/4.0, side*v*cp2, hz + 0.10 - v*sp2))
                          for i in range(5)])
            for j in range(2):
                for i in range(4):
                    f = (g[j][i], g[j][i+1], g[j+1][i+1], g[j+1][i])
                    bm.faces.new(f if side > 0 else tuple(reversed(f)))
            bm.normal_update()
            rr_ = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
            vs = [e for e in rr_['geom'] if isinstance(e, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, verts=vs, vec=(0, -side*sp2*0.085, -cp2*0.085))
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
            obj('chd', mesh_from_bm(bm, 'cd'), _POT, (x, y, 0), (0, 0, ang))

# ---------------------------------------------------------------- street lamp
def _loft(bm, rings, close=True):
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i+1]
        n = len(a)
        for k in range(n if close else n - 1):
            bm.faces.new((a[k], a[(k+1) % n], b[(k+1) % n], b[k]))

def _ring(bm, z, r, n=8, rot=0.0, sq=1.0):
    return [bm.verts.new((math.cos(rot + 2*math.pi*k/n) * r,
                          math.sin(rot + 2*math.pi*k/n) * r * sq, z)) for k in range(n)]

def street_lamp(px, py, ang, hgt=2.62):
    obj('lpb', mesh_from_bm(lump_box(0.30, 0.30, 0.20, 0.05, 3, 0.006), 'lb'),
        M['stone'][int(R()*4)], (px, py, 0.10), (0, 0, ang))
    bm = bmesh.new()
    rings = [_ring(bm, 0.16, 0.075, 8), _ring(bm, 0.34, 0.055, 8),
             _ring(bm, 0.44, 0.040, 8), _ring(bm, hgt*0.72, 0.032, 8),
             _ring(bm, hgt, 0.028, 8)]
    _loft(bm, rings)
    bmesh.ops.contextual_create(bm, geom=rings[0])
    bm.normal_update()
    me = mesh_from_bm(bm, 'lp')
    obj('lp', me, _IRON, (px, py, 0), (0, 0, ang))
    for pg in me.polygons:
        pg.use_smooth = True
    obj('lpc', mesh_from_bm(lump_box(0.13, 0.13, 0.07, 0.02, 2), 'lc'),
        _IRON, (px, py, hgt + 0.02), (0, 0, ang))
    bm = bmesh.new()
    g0 = _ring(bm, hgt + 0.06, 0.145, 4, math.pi/4)
    g1 = _ring(bm, hgt + 0.40, 0.108, 4, math.pi/4)
    _loft(bm, [g0, g1])
    bmesh.ops.contextual_create(bm, geom=g0)
    bm.normal_update()
    obj('lpg', mesh_from_bm(bm, 'lg'), _LGLS, (px, py, 0), (0, 0, ang))
    bm = bmesh.new()
    r0 = _ring(bm, hgt + 0.40, 0.165, 4, math.pi/4)
    r1 = _ring(bm, hgt + 0.46, 0.150, 4, math.pi/4)
    r2 = _ring(bm, hgt + 0.60, 0.030, 4, math.pi/4)
    _loft(bm, [r0, r1, r2])
    bmesh.ops.contextual_create(bm, geom=r0)
    bm.normal_update()
    obj('lpr', mesh_from_bm(bm, 'lr'), _IRON, (px, py, 0), (0, 0, ang))
    obj('lpf', mesh_from_bm(lump_sphere(0.048, 2, 0.05, 1.0), 'lf'),
        _IRON, (px, py, hgt + 0.63), (0, 0, 0))


# ---------------------------------------------------------------- the house
def house(x, y, ang, w, d, h, slate=False, jetty=False):
    """Law 1 + 2 + 3 in one object."""
    ca, sa = math.cos(ang), math.sin(ang)
    def W(lx, ly, lz):                      # local -> world
        return (x + lx*ca - ly*sa, y + lx*sa + ly*ca, lz)

    lean = rr(-0.012, 0.012)                # Law 3 — nothing is plumb

    _wr = R()
    rendered = _wr < 0.86
    if _wr < 0.62:      wallmat = M['paint'][int(R()*12)]
    elif _wr < 0.86:    wallmat = M['plaster'][int(R()*5)]
    else:               wallmat = M['brick'][int(R()*5)]
    house_walls(x, y, ang, w, d, h, wallmat)
    body = None

    # --- THE PLOT (reference 4): nothing floats on undifferentiated ground.
    # A crisply cut panel of mown lawn, and a paved apron tight to the walls.
    _pw, _pd = w + rr(2.1, 3.4), d + rr(1.9, 3.0)
    obj('plot', mesh_from_bm(lump_box(_pw, _pd, 0.10, 0.028, 2), 'plt'),
        LAWN, W(0, 0, 0.05), (0, 0, ang))
    obj('apr', mesh_from_bm(lump_box(w + 1.30, d + 1.20, 0.16, 0.026, 2), 'apr'),
        PAVEM, W(0, 0, 0.080), (0, 0, ang))
    # a clipped hedge round the plot — this is what draws the boundary
    if R() < 0.78:
        _hh = rr(0.58, 0.86)
        for (_hx, _hy, _hw, _hd) in ((0, _pd/2, _pw, 0.34), (0, -_pd/2, _pw, 0.34),
                                     (_pw/2, 0, 0.34, _pd), (-_pw/2, 0, 0.34, _pd)):
            if R() < 0.26: continue
            obj('hdg', mesh_from_bm(lump_box(_hw, _hd, _hh, 0.085, 2), 'hd'),
                HEDGE, W(_hx, _hy, _hh/2 + 0.08), (0, 0, ang))
    # a specimen tree in the garden, the way every plot in the reference has one
    if R() < 0.62:
        _gx = _pw/2 * rr(-0.72, 0.72)
        _gy = (_pd/2 + 0.6) * (1 if R() < 0.5 else -1) * rr(0.62, 0.86)
        tree(x + _gx*ca - _gy*sa, y + _gx*sa + _gy*ca, rr(0.42, 0.66))

    # stone base course, slightly proud and irregular
    obj('base', mesh_from_bm(lump_box(w+0.16, d+0.16, 0.40, 0.035, 2), 'bs'),
        M['stone'][int(R()*4)], W(0, 0, 0.20), (0, 0, ang))

    # --- roof: rounded pantiles, one mesh per slope (see roof_v2) ---
    ridge_h = roof_v2(x, y, ang, w, d, h, slate)

    # gable ends: proper triangles under the ridge, not slabs
    for side in (-1, 1):
        bmg = bmesh.new()
        t = 0.11
        pts = [(-t, -d/2-0.02, -0.04), (-t, d/2+0.02, -0.04), (-t, 0.0, ridge_h-0.26),
               ( t, -d/2-0.02, -0.04), ( t, d/2+0.02, -0.04), ( t, 0.0, ridge_h-0.26)]
        vs = [bmg.verts.new(pp) for pp in pts]
        bmg.faces.new((vs[0], vs[1], vs[2]))
        bmg.faces.new((vs[5], vs[4], vs[3]))
        bmg.faces.new((vs[0], vs[3], vs[4], vs[1]))
        bmg.faces.new((vs[1], vs[4], vs[5], vs[2]))
        bmg.faces.new((vs[2], vs[5], vs[3], vs[0]))
        bmg.normal_update()
        bmesh.ops.bevel(bmg, geom=list(bmg.verts)+list(bmg.edges)+list(bmg.faces),
                        offset=0.05, segments=3, profile=0.5, affect='EDGES')
        obj('gab', mesh_from_bm(bmg, 'gb'), wallmat,
            W(side*(w/2 - 0.05), 0.0, h), (0, 0, ang))
        if R() < 0.25:
            moss_line(W(side*(w/2-0.05), -d/2, h+0.04),
                      W(side*(w/2-0.05), 0, h+ridge_h-0.1),
                      density=3, clump=0.15, scale=(0.28,0.6))

    # --- chimney: plastered shaft, corbelled cap, pots or a tiled hood ---
    _cyc = rr(-0.45, 0.45)
    chimney(x + math.cos(ang)*rr(-w*0.26, w*0.26) - math.sin(ang)*_cyc,
            y + math.sin(ang)*rr(-w*0.26, w*0.26) + math.cos(ang)*_cyc,
            ang, h + ridge_h - abs(_cyc)*0.5 - 0.05, wallmat)

    # --- half-timbering on the upper storey of some houses (Law 3/5)
    if jetty and rendered:
        for side in (-1, 1):
            zt = h*0.56
            for k in range(7):
                lx = -w/2 + (k+0.5)*(w/7)
                obj('tv', mesh_from_bm(lump_box(0.055, 0.04, (h-zt)/2, 0.015, 2), 'tv'),
                    M['timber'], W(lx+rr(-0.05,0.05), side*(d/2+0.03), zt+(h-zt)/2),
                    (0,0,ang))
            for zz in (zt, h-0.16):
                obj('th', mesh_from_bm(lump_box(w/2, 0.05, 0.085, 0.02, 2), 'th'),
                    M['timber'], W(0, side*(d/2+0.03), zz), (0,0,ang))
            for k in range(3):
                lx = -w/2 + (k*2+1.2)*(w/7)
                obj('td', mesh_from_bm(lump_box(0.05, 0.04, (h-zt)*0.45, 0.015, 2), 'td'),
                    M['timber'], W(lx, side*(d/2+0.03), zt+(h-zt)*0.5),
                    (0, rr(0.45,0.62)*(1 if k%2 else -1), ang))

    # --- Law 2: moss + ivy at the base, only where the wall meets the earth ---
    for (ax, ay, bx, by) in [(-w/2, -d/2, w/2, -d/2), (w/2, -d/2, w/2, d/2),
                             (w/2, d/2, -w/2, d/2), (-w/2, d/2, -w/2, -d/2)]:
        moss_line(W(ax, ay, 0.08), W(bx, by, 0.08), density=4, clump=0.30, scale=(0.4,1.0))
    # ivy up one wall, one house in three
    if R() < 0.12:
        side = 1 if R() < 0.5 else -1
        for _ in range(34):
            t = R()
            lx = rr(-w*0.42, w*0.42)
            lz = 0.15 + (h-0.4)*(t**1.35)
            spread = 0.55*(1-t)+0.12
            s = rr(0.45,1.1)*(1.15-t*0.5)
            linked('iv', SHRUB[int(R()*8)],
                   W(lx*spread/0.6, side*(d/2+0.06), lz),
                   (rr(-0.1,0.1), rr(-0.1,0.1), rr(0,6.28)), (s*0.5,s*0.5,s*0.5))
    return body

# ---------------------------------------------------------------- the tree
# Reference standard: a tree is ONE clean solid mass in a real green, with a
# readable silhouette. Not 46 pale lobes and a pile of undergrowth. Two species:
# a rounded broadleaf and a faceted conifer (reference 1).
def _cone_into(bm, r1, r2, dep, z0, seg=9):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg,
                          radius1=r1, radius2=r2, depth=dep,
                          matrix=Matrix.Translation(Vector((0, 0, z0 + dep/2))))

def _ico_into(bm, r, loc, squash=1.0, subd=2):
    bmesh.ops.create_icosphere(
        bm, subdivisions=subd, radius=1.0,
        matrix=Matrix.Translation(Vector(loc)) @ Matrix.Diagonal(Vector((r, r, r*squash, 1.0))))

def tree(x, y, scale=1.0, kind=None, ang=None):
    if kind is None:
        kind = 'conifer' if R() < 0.30 else 'broad'
    if ang is None:
        ang = R() * 6.283
    bm = bmesh.new()
    if kind == 'conifer':
        th = 0.9 * scale
        _cone_into(bm, 0.15*scale, 0.11*scale, th, 0.0, 8)
        _mi(bm, 0, 0)
        n = len(bm.faces)
        tiers = 6
        H = 5.4 * scale
        for k in range(tiers):
            f = k / (tiers - 1.0)
            r0 = (1.28 - 0.98*f) * scale
            hh = (1.72 - 0.62*f) * scale
            z0 = th*0.45 + f * (H - th*0.45 - hh)
            _cone_into(bm, r0, r0*0.14, hh, z0, 9)
        _mi(bm, n, 1)
        mats = [M['bark'], CONIF[int(R()*4)]]
        nm = 'conifer'
    else:
        th = 2.15 * scale
        _cone_into(bm, 0.26*scale, 0.155*scale, th, 0.0, 10)
        _mi(bm, 0, 0)
        n = len(bm.faces)
        CR = 1.62 * scale
        cz = th + CR * 0.66
        _ico_into(bm, CR, (0, 0, cz), 0.86, 3)
        for k in range(5):
            a = k/5.0*6.283 + rr(-0.28, 0.28)
            rl = CR * rr(0.50, 0.70)
            dd = CR * rr(0.58, 0.82)
            _ico_into(bm, rl, (math.cos(a)*dd, math.sin(a)*dd,
                               cz + rr(-0.34, 0.26)*CR), 0.92, 2)
        _mi(bm, n, 1)
        mats = [M['bark'], CANOPY[int(R()*6)]]
        nm = 'tree'
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = mesh_from_bm(bm, nm)
    for m in mats: me.materials.append(m)
    if kind == 'conifer':
        _flat(me)
    obj(nm, me, None, (x, y, 0.0), (0, 0, ang))

# a clipped street tree: same mass, smaller, on a square earth pit
def street_tree(x, y, scale=0.52):
    obj('pit', mesh_from_bm(lump_box(1.05, 1.05, 0.14, 0.022, 2), 'pit'),
        SOIL, (x, y, 0.10), (0, 0, 0))
    tree(x, y, scale, 'broad')

# ---------------------------------------------------------------- build the scene
# ground shell
bm = bmesh.new()
PAVE_R = 6.6
PLATE_R = 48.0                     # kept: legacy radius used by a few scatterers
PLATE_X, PLATE_Y, PLATE_N = 51.0, 43.0, 5.0     # a rounded rectangle, not a disc
TOWN_R  = 40.0
def plate_t(px, py):
    """0 at the centre of the plate, 1.0 exactly on its edge."""
    return ((abs(px)/PLATE_X)**PLATE_N + (abs(py)/PLATE_Y)**PLATE_N)**(1.0/PLATE_N)
def inplate(px, py, m=0.0):
    return ((abs(px)/max(1.0, PLATE_X-m))**PLATE_N +
            (abs(py)/max(1.0, PLATE_Y-m))**PLATE_N) <= 1.0
def gz(gx, gy):
    """Ground height. Flat under the whole town, rolling only at the wild edge."""
    t = plate_t(gx, gy)
    k = min(1.0, max(0.0, (t-0.78)/0.12)) * min(1.0, max(0.0, (1.0-t)/0.06))
    return -0.02 + k*(math.sin(gx*0.13)*0.24 + math.cos(gy*0.11)*0.20)

bmesh.ops.create_grid(bm, x_segments=148, y_segments=148, size=PLATE_X + 1.4)
_kill = [v for v in bm.verts if not inplate(v.co.x, v.co.y)]
bmesh.ops.delete(bm, geom=_kill, context='VERTS')
for v in bm.verts:
    v.co.z = gz(v.co.x, v.co.y)          # no vertex noise: a mown lawn is flat
_bnd = [e for e in bm.edges if e.is_boundary]
_nf0 = len(bm.faces)
_ext = bmesh.ops.extrude_edge_only(bm, edges=_bnd)
for v in [g for g in _ext['geom'] if isinstance(g, bmesh.types.BMVert)]:
    _l = math.hypot(v.co.x, v.co.y) or 1.0
    v.co.x *= (_l + 0.26)/_l; v.co.y *= (_l + 0.26)/_l; v.co.z = -0.44
bm.faces.ensure_lookup_table()
for _f in bm.faces[_nf0:]: _f.material_index = 1      # the cut-earth band
GRND = clay('gnd', (104,168, 62), 0.94, 0.20, 0.02)
me = mesh_from_bm(bm, 'ground')
me.materials.append(GRND); me.materials.append(SOIL)
for _pg in me.polygons: _pg.use_smooth = False
obj('ground', me, None, (0,0,0))

# --- the plate itself: a shallow glazed dish the town sits in (Law 7)
_pb = bmesh.new()
bmesh.ops.create_grid(_pb, x_segments=110, y_segments=110, size=PLATE_X + 2.4)
_pk = [v for v in _pb.verts
       if ((abs(v.co.x)/(PLATE_X+0.85))**PLATE_N +
           (abs(v.co.y)/(PLATE_Y+0.85))**PLATE_N) > 1.0]
bmesh.ops.delete(_pb, geom=_pk, context='VERTS')
for v in _pb.verts: v.co.z = -0.34
_pbe = bmesh.ops.extrude_edge_only(_pb, edges=[e for e in _pb.edges if e.is_boundary])
_pbv = [g for g in _pbe['geom'] if isinstance(g, bmesh.types.BMVert)]
for v in _pbv: v.co.z = -2.30
_pbe2 = bmesh.ops.extrude_edge_only(_pb, edges=[e for e in _pb.edges if e.is_boundary])
for v in [g for g in _pbe2['geom'] if isinstance(g, bmesh.types.BMVert)]:
    v.co.x *= 0.985; v.co.y *= 0.985; v.co.z = -2.62
bmesh.ops.bevel(_pb, geom=list(_pb.verts)+list(_pb.edges)+list(_pb.faces),
                offset=0.10, segments=2, affect='EDGES', profile=0.5)
PLATE = clay('plate', (238, 230, 214), 0.60, 0.22, 0.03)
_pm = mesh_from_bm(_pb, 'plate'); _pm.materials.append(PLATE)
obj('plate', _pm, None, (0, 0, 0))
# The rim is a designed cut, not a rubble heap. A sparse handful of boulders
# only, sunk into the earth band where the ground rolls at the wild edge.
for _i in range(0):
    _a = (_i/760.0)*6.283 + rr(-0.004, 0.004)
    _ux, _uy = math.cos(_a), math.sin(_a)
    _sc = 1.0/max(1e-6, ((abs(_ux)/PLATE_X)**PLATE_N + (abs(_uy)/PLATE_Y)**PLATE_N)**(1.0/PLATE_N))
    _rd = _sc * rr(0.985, 1.028)
    _bs = rr(0.55, 1.45)
    linked('bld', STONE[int(R()*6)],
           (_ux*_rd, _uy*_rd, rr(-1.35, -0.10)),
           (rr(0,0.5), rr(0,0.5), rr(0,6.28)), (_bs, _bs, _bs*rr(0.7,1.0)))

# ============================================================ THE STREET PLAN
# An English town is a street with buildings on it, not a ring around a green.
# One high street; a mill lane down to the football ground; a market square off
# the high street; and irregular back lanes that grew rather than were planned.
import os as _osx
NIGHT = int(_osx.environ.get('NIGHT', '0'))

def emit(name, rgb255, power):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs[0].default_value = (*srgb(rgb255), 1)
    e.inputs[1].default_value = power
    nt.links.new(e.outputs[0], nt.nodes['Material Output'].inputs[0])
    return m

GLOW  = [emit('gw%d' % i, c, p) for i, (c, p) in enumerate(
         [((255,192,104), 34.0), ((255,206,132), 27.0),
          ((255,166, 78), 42.0), ((250,214,160), 23.0),
          ((255,148, 96), 32.0), ((150,200,255), 26.0),
          ((190,150,255), 24.0), ((140,255,214), 22.0)])]
LAMPG = emit('lampg', (255, 196, 120), 90.0)
FLOOD = emit('flood', (232, 240, 255), 160.0)

TARMAC = clay('tar', (142,144,148), 0.84)
FLAG   = clay('flg', (240,234,220), 0.86, 0.06)
CONC   = clay('cnc', (244,238,226), 0.88, 0.06)
POST   = clay('pst', (176,180,186), 0.46)
PITCH1 = clay('pt1', (148,180, 88), 0.94, 0.24)
PITCH2 = clay('pt2', (132,166, 76), 0.94, 0.24)

HIGH = [(-35.0, 10.4), (-27.0, 9.6), (-19.0, 8.0), (-11.0, 6.2), (-3.0, 4.8),
        (6.0, 4.0), (14.5, 2.8), (23.0, 1.0), (31.0, -1.6), (37.0, -4.8)]
MILL = [(1.4, 4.3), (0.4, -3.6), (-1.8, -11.0), (-3.6, -18.0), (-4.2, -24.5)]
KIRK = [(-19.6, 8.2), (-21.4, 15.0), (-20.2, 22.0), (-22.6, 28.0), (-20.8, 33.0)]
STREETS = [HIGH, MILL, KIRK]
def _chaikin(pts, n=2):
    """Corner-cutting. Endpoints are preserved so lanes stay welded to streets."""
    for _ in range(n):
        out = [pts[0]]
        for i in range(len(pts)-1):
            (ax, ay), (bx, by) = pts[i], pts[i+1]
            out.append((ax + 0.25*(bx-ax), ay + 0.25*(by-ay)))
            out.append((ax + 0.75*(bx-ax), ay + 0.75*(by-ay)))
        out.append(pts[-1]); pts = out
    return pts

LANES = [[(-27.4, 9.6), (-29.2, 3.4), (-27.4, -2.6), (-30.0, -8.4), (-28.2, -13.6)],
         [(24.4, -9.2), (27.8, -13.8), (25.6, -19.2)],
         [(-11.0, 6.2), (-9.0, 12.4), (-12.4, 17.6), (-10.2, 22.4)],
         [(23.0, 1.0), (26.2, 7.0), (23.4, 12.6), (26.0, 18.4)],
         [(6.0, 4.0), (7.8, 10.2), (4.8, 15.4), (6.8, 21.0), (4.2, 26.4)],
         [(-3.0, 4.8), (-4.6, 10.6), (-1.8, 15.2)],
         [(31.0, -1.6), (33.4, -7.4), (30.6, -12.8)],
         [(-21.4, 15.0), (-14.6, 16.4), (-8.8, 14.2)],
         [(-29.2, 3.4), (-22.6, 1.4), (-16.0, 2.6)],
         [(-1.8, -11.0), (-8.6, -12.8), (-14.2, -10.4)]]
LANES = [_chaikin(_p, 2) for _p in LANES]
SQ_C, SQ_R = (-21.0, 19.4), 10.2

# --- THE TOWN SQUARE. The church green above is a churchyard; this is the
# market place: a rectangle, because a square is a *room*, and rooms have
# straight walls. It hangs off the south side of the High Street where the
# town actually gathers, and opens south onto the football ground.
TSQ_C, TSQ_A = (15.5, -7.6), -0.26
TSQ_HW, TSQ_HD = 11.0, 5.6
def tsq_local(px, py):
    _c, _s = math.cos(TSQ_A), math.sin(TSQ_A)
    dx, dy = px-TSQ_C[0], py-TSQ_C[1]
    return dx*_c + dy*_s, -dx*_s + dy*_c
def in_tsq(px, py, pad=0.0):
    lx, ly = tsq_local(px, py)
    return abs(lx) < TSQ_HW+pad and abs(ly) < TSQ_HD+pad
def tsq_w(lx, ly, z=0.0):
    _c, _s = math.cos(TSQ_A), math.sin(TSQ_A)
    return (TSQ_C[0] + lx*_c - ly*_s, TSQ_C[1] + lx*_s + ly*_c, z)
STAD, STAD_A = (-2.6, -30.0), 0.14
SEATA = clay('sta', ( 42,  78, 148), 0.62)     # club colours: it is a real club
SEATB = clay('stb', (232, 228, 218), 0.60)
ROAD_HW, PAVE_W, LANE_HW = 3.1, 1.9, 2.10

def _segd(px, py, ax, ay, bx, by):
    vx, vy = bx-ax, by-ay; wx, wy = px-ax, py-ay
    L = vx*vx + vy*vy
    t = 0.0 if L == 0 else max(0.0, min(1.0, (wx*vx + wy*vy)/L))
    return math.hypot(px-(ax+t*vx), py-(ay+t*vy))

def polyd(px, py, pts):
    return min(_segd(px, py, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
               for i in range(len(pts)-1))

def in_square(px, py):
    return math.hypot(px-SQ_C[0], py-SQ_C[1]) < SQ_R

def in_stadium(px, py, pad=0.0):
    ca_, sa_ = math.cos(-STAD_A), math.sin(-STAD_A)
    lx = (px-STAD[0])*ca_ - (py-STAD[1])*sa_
    ly = (px-STAD[0])*sa_ + (py-STAD[1])*ca_
    return abs(lx) < 19.6+pad and abs(ly) < 14.6+pad

def paved(px, py):
    if in_square(px, py): return True
    if in_tsq(px, py, 0.3): return True
    if any(polyd(px, py, _S) < ROAD_HW+PAVE_W+0.15 for _S in STREETS): return True
    return any(polyd(px, py, L) < LANE_HW+1.15 for L in LANES)

def built(px, py):
    return paved(px, py) or in_stadium(px, py, 1.0)

def resample(pts, ds=0.25):
    out = []
    for i in range(len(pts)-1):
        ax, ay = pts[i]; bx, by = pts[i+1]
        L = math.hypot(bx-ax, by-ay); n = max(1, int(L/ds))
        tg = math.atan2(by-ay, bx-ax)
        for k in range(n):
            t = k/n
            out.append((ax+(bx-ax)*t, ay+(by-ay)*t, tg))
    out.append((pts[-1][0], pts[-1][1], out[-1][2]))
    return out

def ribbon(pts, o1, o2, z, mat, name='rd', thick=0.0, ds=0.5):
    """A flat strip between two signed perpendicular offsets of a polyline."""
    smp = resample(pts, ds)
    bmr = bmesh.new(); rows = []
    for (px, py, tg) in smp:
        nx, ny = -math.sin(tg), math.cos(tg)
        rows.append((bmr.verts.new((px+nx*o1, py+ny*o1, z)),
                     bmr.verts.new((px+nx*o2, py+ny*o2, z))))
    for i in range(len(rows)-1):
        try: bmr.faces.new((rows[i][0], rows[i+1][0], rows[i+1][1], rows[i][1]))
        except Exception: pass
    bmr.normal_update()
    if thick:
        _ex = bmesh.ops.extrude_face_region(bmr, geom=bmr.faces[:])
        _vs = [g for g in _ex['geom'] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bmr, verts=_vs, vec=(0, 0, -thick))
        bmesh.ops.recalc_face_normals(bmr, faces=list(bmr.faces))
    me_ = mesh_from_bm(bmr, name); me_.materials.append(mat)
    for _p in me_.polygons: _p.use_smooth = False    # roads are flat, not domed
    obj(name, me_, None, (0, 0, 0))

def cobble_patch(test, x0, x1, y0, y1, z=0.055, step=0.44):
    nx_ = int((x1-x0)/step); ny_ = int((y1-y0)/step)
    for i in range(nx_):
        for j in range(ny_):
            px = x0 + i*step + (j % 2)*step*0.5 + rr(-0.035, 0.035)
            py = y0 + j*step + rr(-0.030, 0.030)
            if not test(px, py): continue
            sc = rr(0.82, 1.15)
            linked('cb', COBBLE[int(R()*8)], (px, py, z+rr(-0.012, 0.012)),
                   (rr(-0.06, 0.06), rr(-0.06, 0.06), rr(0, 6.28)),
                   (sc, sc*rr(0.9, 1.1), rr(0.7, 1.1)))

# ---------------------------------------------------------------- the car kit
# Reference 2, 3 and 5 all read as *circulation* long before they read as
# architecture. Cars parked along a kerb are what tell the eye a road is a road.
KERB     = clay('krb', (214, 210, 200), 0.70, 0.04)
CARPAINT = [clay('cp%d' % i, c, 0.26, 0.60) for i, c in enumerate(
    [(196, 62, 52), (238, 236, 230), ( 40, 72, 130), ( 46, 50, 56),
     (214, 168, 58), ( 70, 128, 96), (152, 156, 162), (186, 196, 206)])]
CARGLASS = clay('cgl', ( 40, 52, 60), 0.12, 0.35)
TYRE     = clay('tyr', ( 30, 30, 32), 0.72)

def _wheel_into(bm, r, wid, loc, seg=10):
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=wid,
        matrix=Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(90), 4, 'X'))

def _make_car(paint, est=False):
    bm = bmesh.new()
    L, Wd = (4.90, 1.94) if est else (4.15, 1.80)
    cube_into(bm, L, Wd, 0.74, (0, 0, 0.70))                 # body
    cube_into(bm, L*0.47, Wd*0.90, 0.16, (-L*0.06, 0, 1.62))  # roof cap
    bmesh.ops.bevel(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                    offset=0.085, segments=2, profile=0.6, affect='EDGES',
                    clamp_overlap=True)
    _mi(bm, 0, 0)
    n1 = len(bm.faces)
    cube_into(bm, L*0.50, Wd*0.93, 0.60, (-L*0.06, 0, 1.32))  # glasshouse
    _mi(bm, n1, 1)
    n2 = len(bm.faces)
    for _sx in (1, -1):
        for _sy in (1, -1):
            _wheel_into(bm, 0.335, 0.28, (_sx*L*0.315, _sy*Wd*0.475, 0.335))
    _mi(bm, n2, 2)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = mesh_from_bm(bm, 'car')
    for _m in (paint, CARGLASS, TYRE): me.materials.append(_m)
    return me

CARS = [_make_car(CARPAINT[_i], est=(_i % 3 == 2)) for _i in range(8)]

# --- carriageway, kerbs, pavements: the kerb is the whole trick. A road that
# sits flush in the grass reads as a painted stripe; a road held by a raised
# stone edge reads as engineering.
for _si, _pl in enumerate(STREETS):
    _dz = _si * 0.009
    ribbon(_pl,  ROAD_HW, ROAD_HW+PAVE_W, 0.150+_dz, PAVEM, 'pvl', thick=0.55)
    ribbon(_pl, -(ROAD_HW+PAVE_W), -ROAD_HW, 0.150+_dz, PAVEM, 'pvr', thick=0.55)
    ribbon(_pl,  ROAD_HW-0.03, ROAD_HW+0.30, 0.186+_dz, KERB, 'kbl', thick=0.42)
    ribbon(_pl, -(ROAD_HW+0.30), -(ROAD_HW-0.03), 0.186+_dz, KERB, 'kbr', thick=0.42)
    ribbon(_pl, -ROAD_HW-0.06, ROAD_HW+0.06, 0.030+_dz, TARMAC, 'road')
    ribbon(_pl,  ROAD_HW-0.46, ROAD_HW-0.32, 0.052+_dz, WHITE, 'edl')
    ribbon(_pl, -(ROAD_HW-0.32), -(ROAD_HW-0.46), 0.052+_dz, WHITE, 'edr')

# --- centre line: painted, even, dead true (the model-maker standard)
_LNM = mesh_from_bm(lump_box(1.6, 0.14, 0.014, 0.005, 2), 'lnm')
_LNM.materials.append(WHITE)
for _pl, _n in ((HIGH, 96), (MILL, 40), (KIRK, 32)):
    _smp = resample(_pl, 0.25)
    _stride = max(1, len(_smp)//_n)
    for _k in range(0, len(_smp)-2, _stride):
        _px, _py, _tg = _smp[_k]
        linked('ln', _LNM, (_px, _py, 0.044), (0, 0, _tg))

# --- zebra crossings: three on the high street, one on each of the others
_ZBR = mesh_from_bm(lump_box(2.60, 0.52, 0.018, 0.006, 2), 'zbr')
_ZBR.materials.append(WHITE)
for _pl, _ts in ((HIGH, (0.26, 0.56, 0.84)), (MILL, (0.40,)), (KIRK, (0.52,))):
    _smp = resample(_pl, 0.25)
    for _t in _ts:
        _k = int(_t * (len(_smp) - 3))
        _px, _py, _tg = _smp[_k]
        _nx, _ny = -math.sin(_tg), math.cos(_tg)
        _q = -ROAD_HW + 0.52
        while _q < ROAD_HW - 0.52:
            linked('zb', _ZBR, (_px + _nx*_q, _py + _ny*_q, 0.048), (0, 0, _tg))
            _q += 0.94

# --- PARKED CARS tight to the kerb, plus a few on the move down the lane
for _pl, _sp in ((HIGH, 10.5), (MILL, 13.0), (KIRK, 14.0)):
    _smp = resample(_pl, 0.30)
    _step = max(1, int(_sp / 0.30))
    for _k in range(_step // 3, len(_smp) - 3, _step):
        _px, _py, _tg = _smp[_k]
        _nx, _ny = -math.sin(_tg), math.cos(_tg)
        for _sd in (1, -1):
            if R() < 0.36: continue
            _off = _sd * (ROAD_HW - 1.14)
            _cx, _cy = _px + _nx*_off, _py + _ny*_off
            if not inplate(_cx, _cy, 2.0) or in_stadium(_cx, _cy, 1.0): continue
            linked('car', CARS[int(R()*8)], (_cx, _cy, 0.046),
                   (0, 0, _tg + (0.0 if _sd > 0 else math.pi) + rr(-0.015, 0.015)))
    for _k in range(_step, len(_smp) - 3, _step * 3):
        _px, _py, _tg = _smp[_k]
        _nx, _ny = -math.sin(_tg), math.cos(_tg)
        _sd = 1 if R() < 0.5 else -1
        _cx, _cy = _px + _nx*_sd*1.52, _py + _ny*_sd*1.52
        if not inplate(_cx, _cy, 2.0): continue
        linked('car', CARS[int(R()*8)], (_cx, _cy, 0.046),
               (0, 0, _tg + (0.0 if _sd > 0 else math.pi)))

# --- STREET TREES: an evenly spaced row down each pavement (references 3/4/5).
# Rhythm is what makes a street read as designed rather than grown.
for _pl, _sp in ((HIGH, 8.0), (MILL, 9.0), (KIRK, 9.5)):
    _smp = resample(_pl, 0.30)
    _step = max(1, int(_sp / 0.30))
    for _k in range(_step // 2, len(_smp) - 2, _step):
        _px, _py, _tg = _smp[_k]
        _nx, _ny = -math.sin(_tg), math.cos(_tg)
        for _sd in (1, -1):
            _off = _sd * (ROAD_HW + PAVE_W + 1.35)
            _tx2, _ty2 = _px + _nx*_off, _py + _ny*_off
            if not inplate(_tx2, _ty2, 3.0) or built(_tx2, _ty2): continue
            if in_square(_tx2, _ty2) or in_stadium(_tx2, _ty2, 2.0): continue
            street_tree(_tx2, _ty2, rr(0.76, 0.92))

# --- the back lanes. A lane made of 3,600 loose pebbles is gravel mush; a lane
# made of one laid ribbon with a kerb strip and cross joints reads as a lane at
# plate distance and costs 30 objects instead of 400. Law: precision, not jitter.
LANESET = clay('lnst', (170, 158, 138), 0.86, 0.05)
LANEDGE = clay('lned', (218, 213, 202), 0.84, 0.04)
LANEVRG = clay('lnvg', ( 96, 158,  58), 0.92, 0.16, 0.03)
LANEGW = clay('lngw', (150, 118,  80), 0.80, 0.12)
for _li, _L in enumerate(LANES):
    _ldz = _li * 0.003
    # verge 0.024 -> surface 0.072 -> joints 0.112 -> kerb 0.128. Every step is
    # at least 27 mm, because two surfaces within ~10 mm render pure black.
    ribbon(_L, -(LANE_HW+1.05), (LANE_HW+1.05), 0.170+_ldz, LANEVRG, 'lnvg', 0.22, 0.5)
    ribbon(_L, -LANE_HW, LANE_HW, 0.218+_ldz, LANESET, 'lnsf', 0.14, 0.4)
    ribbon(_L, -(LANE_HW+0.24), -LANE_HW, 0.258+_ldz, LANEDGE, 'lnkl', 0.16, 0.4)
    ribbon(_L,  LANE_HW, (LANE_HW+0.24), 0.258+_ldz, LANEDGE, 'lnkr', 0.16, 0.4)
    _smp = resample(_L, 0.25)
    # a lane has to STOP somewhere. A five-bar gate between two posts says the
    # lane ends here on purpose, instead of the tarmac just running out.
    for _ei in (0, -1):
        _gx, _gy = _L[_ei]
        if min(polyd(_gx, _gy, _S) for _S in STREETS) < ROAD_HW + PAVE_W + 2.0: continue
        if not inplate(_gx, _gy, 1.2) or in_stadium(_gx, _gy, 1.0): continue
        _oxp, _oyp = _L[1] if _ei == 0 else _L[-2]
        _ga = math.atan2(_gy-_oyp, _gx-_oxp)
        _gn = _ga + math.pi/2
        _gnx, _gny = math.cos(_gn), math.sin(_gn)
        for _gs in (-1, 1):
            obj('gtp', mesh_from_bm(lump_box(0.22, 0.22, 1.36, 0.04, 2), 'gtp'), POST,
                (_gx+_gnx*_gs*(LANE_HW+0.20), _gy+_gny*_gs*(LANE_HW+0.20), 0.82),
                (0, 0, _ga))
        for _gk in range(4):
            obj('gtr', mesh_from_bm(lump_box(2*LANE_HW-0.06, 0.07, 0.12, 0.02, 2), 'gtr'),
                LANEGW, (_gx, _gy, 0.46+_gk*0.30), (0, 0, _gn))
    # a clipped hedge down the open flank: what actually tells the eye it is a lane
    for _k in range(2, len(_smp)-3, 5):
        _px, _py, _tg = _smp[_k]
        _nx, _ny = -math.sin(_tg), math.cos(_tg)
        _hsd = -1 if _li % 2 == 0 else 1
        _hgx, _hgy = _px + _nx*_hsd*(LANE_HW+1.35), _py + _ny*_hsd*(LANE_HW+1.35)
        if not inplate(_hgx, _hgy, 1.4) or in_stadium(_hgx, _hgy, 1.0): continue
        if in_square(_hgx, _hgy) or in_tsq(_hgx, _hgy, 0.6): continue
        obj('lhg', mesh_from_bm(lump_box(1.28, 0.44, rr(0.86, 1.06), 0.17, 3), 'lhg'),
            HEDGES[_k % 4], (_hgx, _hgy, 0.46), (0, 0, _tg))

# ------------------------------------------------------- THE MARKET SQUARE
# Law 4 and Law 8. A square is a *designed room*, not a patch of loose stones.
# It gets: a laid floor with concentric bands, a raised kerb that defines its
# edge, a rhythm of trees round the rim, benches facing in, and market stalls.
SQPAV = clay('sqpv', (232, 224, 208), 0.80, 0.06)
SQBND = clay('sqbd', (162, 150, 134), 0.78, 0.05)
SQRED = clay('sqrd', (186, 116,  88), 0.80, 0.05)

def disc(nm, r, h, mat, loc, seg=44, rot=0.0):
    _bd = bmesh.new()
    bmesh.ops.create_cone(_bd, cap_ends=True, segments=seg, radius1=r, radius2=r,
                          depth=h, matrix=Matrix.Rotation(rot, 4, 'Z'))
    _me = mesh_from_bm(_bd, nm); _me.materials.append(mat)
    for _p in _me.polygons: _p.use_smooth = False
    obj(nm, _me, None, loc)

disc('sqk', SQ_R + 0.42, 0.34, KERB,  (SQ_C[0], SQ_C[1], 0.03))   # top 0.20
disc('sqb', SQ_R,        0.28, SQBND, (SQ_C[0], SQ_C[1], 0.02))   # border band
disc('sqp', SQ_R - 1.15, 0.28, SQPAV, (SQ_C[0], SQ_C[1], 0.03))   # the floor
disc('sqr', SQ_R*0.36,   0.28, SQRED, (SQ_C[0], SQ_C[1], 0.04))   # medallion
disc('sqi', SQ_R*0.14,   0.28, SQBND, (SQ_C[0], SQ_C[1], 0.05))   # the cross base

# Kirk Street runs across the square; keep the furniture out of the carriageway.
_sq_kirk = resample(KIRK, 0.7)
_SQ_CIVIC = [(SQ_C[0]-4.4, SQ_C[1]+4.2, 3.6),      # the clock tower
             (SQ_C[0]+3.6, SQ_C[1]+6.0, 5.2),      # the church nave
             (SQ_C[0]+1.7, SQ_C[1]+2.2, 2.8),      # the south porch
             (SQ_C[0],     SQ_C[1],     2.2)]      # the market cross
def _sq_clear(px, py, rad=3.6):
    for (_qx, _qy, _tq) in _sq_kirk:
        if (px-_qx)**2 + (py-_qy)**2 < rad*rad: return False
    for (_qx, _qy, _qr) in _SQ_CIVIC:
        if (px-_qx)**2 + (py-_qy)**2 < _qr*_qr: return False
    return True

# --- the bench, built once and instanced
BENCHW = clay('bnw', (150, 106,  66), 0.74, 0.14)
def _make_bench():
    _bm = bmesh.new()
    cube_into(_bm, 1.90, 0.48, 0.09, (0, 0, 0.46))
    cube_into(_bm, 1.90, 0.09, 0.46, (0, -0.20, 0.73))
    _mi(_bm, 0, 0)
    _n1 = len(_bm.faces)
    for _sx in (-1, 1):
        cube_into(_bm, 0.08, 0.46, 0.46, (_sx*0.88, 0, 0.23))
    _mi(_bm, _n1, 1)
    bmesh.ops.recalc_face_normals(_bm, faces=list(_bm.faces))
    _me = mesh_from_bm(_bm, 'bnc')
    _me.materials.append(BENCHW); _me.materials.append(POST)
    return _me
BENCH = _make_bench()

# --- the market stall, four canvas colourways
STALLC = [clay('sc%d' % i, c, 0.80, 0.06) for i, c in enumerate(
    [(198,  66,  58), (238, 234, 224), ( 46,  94, 156), (232, 176,  62)])]
def _make_stall(canvas):
    _bm = bmesh.new()
    cube_into(_bm, 1.86, 1.02, 0.06, (0, 0, 0.80))          # trestle top
    _mi(_bm, 0, 0)
    _n1 = len(_bm.faces)
    cube_into(_bm, 1.66, 0.84, 0.74, (0, 0, 0.40))          # goods below the cloth
    for _sx in (-1, 1):
        for _sy in (-1, 1):
            cube_into(_bm, 0.06, 0.06, 1.94, (_sx*0.87, _sy*0.45, 0.97))
    _mi(_bm, _n1, 1)
    _n2 = len(_bm.faces)
    cube_into(_bm, 2.08, 1.26, 0.08, (0, 0, 1.98))          # canopy
    cube_into(_bm, 2.08, 0.08, 0.24, (0, -0.63, 1.82))      # valance
    _mi(_bm, _n2, 2)
    bmesh.ops.recalc_face_normals(_bm, faces=list(_bm.faces))
    _me = mesh_from_bm(_bm, 'stl')
    for _m in (BENCHW, M['plaster'][2], canvas): _me.materials.append(_m)
    return _me
STALLS = [_make_stall(_c) for _c in STALLC]

# --- trees round the rim, in a deliberate rhythm (Law 7)
for _k in range(18):
    _a = _k/18.0*6.283 + 0.14
    _tx = SQ_C[0] + math.cos(_a)*(SQ_R - 0.62)
    _ty = SQ_C[1] + math.sin(_a)*(SQ_R - 0.62)
    if not _sq_clear(_tx, _ty, 3.4): continue
    street_tree(_tx, _ty, 0.58)

# --- bollards keeping the paving edge crisp between the trees
_BOL = mesh_from_bm(lump_box(0.19, 0.19, 0.68, 0.08, 3), 'bol')
_BOL.materials.append(M['brick'][4])
for _k in range(24):
    _a = _k/24.0*6.283 + 0.05
    _bx = SQ_C[0] + math.cos(_a)*(SQ_R - 0.52)
    _by = SQ_C[1] + math.sin(_a)*(SQ_R - 0.52)
    if not _sq_clear(_bx, _by, 2.6): continue
    linked('bol', _BOL, (_bx, _by, 0.50))

# --- benches on the medallion ring, all facing the cross
for _k in range(10):
    _a = _k/10.0*6.283 + 0.31
    _bx = SQ_C[0] + math.cos(_a)*(SQ_R*0.50)
    _by = SQ_C[1] + math.sin(_a)*(SQ_R*0.50)
    if not _sq_clear(_bx, _by, 2.8): continue
    linked('bnc', BENCH, (_bx, _by, 0.17), (0, 0, _a + math.pi/2))

# --- the stalls, laid out as straight rows either side of the carriageway and
# facing it, the way a real market day works. An arc of stalls on a small radius
# puts a 2.1 m canopy every 2.4 m and reads as one crumpled silver mass.
for (_row_x, _fdir) in ((4.30, -1), (-6.10, 1)):
    for _k in range(4):
        _sy2 = SQ_C[1] - 5.20 + _k*2.65
        _sx2 = SQ_C[0] + _row_x
        if math.hypot(_sx2-SQ_C[0], _sy2-SQ_C[1]) > SQ_R - 1.9: continue
        if not _sq_clear(_sx2, _sy2, 2.6): continue
        linked('stl', STALLS[(_k + (0 if _fdir < 0 else 2)) % 4], (_sx2, _sy2, 0.17),
               (0, 0, math.pi/2 if _fdir < 0 else -math.pi/2))

# --- street lamps down both pavements (Law 6 at night, silhouette by day)
def lamp(px, py, ang):
    obj('lp', mesh_from_bm(lump_box(0.16, 0.16, 4.2, 0.05, 3, 0.008), 'lp'),
        POST, (px, py, 2.1), (rr(-0.02, 0.02), rr(-0.02, 0.02), ang))
    obj('lph', mesh_from_bm(lump_box(0.46, 0.34, 0.30, 0.10, 3), 'lh'),
        POST, (px, py, 4.28), (0, 0, ang))
    obj('lpg', mesh_from_bm(lump_box(0.34, 0.24, 0.16, 0.06, 2), 'lg'),
        (LAMPG if NIGHT else WHITE), (px, py, 4.14), (0, 0, ang))
    if NIGHT:
        _ld = bpy.data.lights.new('lampL', 'POINT')
        _ld.energy = 420.0; _ld.color = (1.00, 0.74, 0.44); _ld.shadow_soft_size = 0.30
        _lo = bpy.data.objects.new('lampL', _ld); _lo.location = (px, py, 4.05)
        COL.objects.link(_lo)
for _pl in STREETS:
    _smp = resample(_pl, 0.25)
    for _k in range(0, len(_smp), 17):
        _px, _py, _tg = _smp[_k]
        _sd = 1 if (_k // 17) % 2 == 0 else -1
        _nx, _ny = -math.sin(_tg), math.cos(_tg)
        lamp(_px+_nx*_sd*(ROAD_HW+1.1), _py+_ny*_sd*(ROAD_HW+1.1), _tg)


# ---------------------------------------------- THE TOWN SQUARE (market place)
# A square is a room. It gets a laid floor with real joints, a hard kerb edge,
# one thing worth walking to (the fountain), one thing that says the town has
# fun (the bandstand), a market, a cafe terrace under bright parasols, planted
# colour, and shopfronts closing the east wall. It opens south onto the ground.
TSQPAV = clay('tqpv', (238, 231, 216), 0.80, 0.06)
TSQBND = clay('tqbd', (176, 166, 150), 0.78, 0.05)
TSQMED = clay('tqmd', (196, 128,  96), 0.80, 0.05)
GAY = [clay('gay%d' % i, c, 0.78, 0.08) for i, c in enumerate(
    [(220,  74,  62), (240, 182,  66), ( 62, 134, 182), (240, 234, 222),
     ( 86, 162,  98), (200,  94, 150)])]

def _tslab(nm, w, d, h, mat, lx, ly, z):
    _wx, _wy, _ = tsq_w(lx, ly)
    obj(nm, mesh_from_bm(lump_box(w, d, h, 0.045, 2), nm), mat,
        (_wx, _wy, z), (0, 0, TSQ_A))

_tslab('tqk', 2*TSQ_HW+0.94, 2*TSQ_HD+0.94, 0.30, KERB,   0, 0, 0.020)
_tslab('tqb', 2*TSQ_HW,      2*TSQ_HD,      0.28, TSQBND, 0, 0, 0.034)
_tslab('tqp', 2*TSQ_HW-1.5,  2*TSQ_HD-1.5,  0.28, TSQPAV, 0, 0, 0.046)
for _tqjx in (-7.8, -5.2, -2.6, 2.6, 5.2, 7.8):        # a 2.6 m paving grid,
    _tslab('tqj', 0.34, 2*TSQ_HD-1.6, 0.30, TSQBND, _tqjx, 0, 0.058)
for _tqjy in (-2.6, 0.0, 2.6):                          # banded courses standing
    _tslab('tqj', 2*TSQ_HW-1.6, 0.34, 0.30, TSQBND, 0, _tqjy, 0.058)   # 20 mm proud
_tslab('tqm', 5.2, 2.2, 0.30, TSQMED, 0, 0, 0.072)      # the inlay panel

# --- keepout bookkeeping: claim in priority order and let the square arrange
_TQOCC = []
def _tq_take(lx, ly, rad):
    if abs(lx) > TSQ_HW - 0.55 or abs(ly) > TSQ_HD - 0.55: return False
    _wx, _wy, _ = tsq_w(lx, ly)
    if polyd(_wx, _wy, HIGH) < ROAD_HW + PAVE_W + 0.4: return False
    if polyd(_wx, _wy, MILL) < ROAD_HW + PAVE_W + 0.4: return False
    for (_ox, _oy, _o2) in _TQOCC:
        if (lx-_ox)**2 + (ly-_oy)**2 < (rad+_o2)**2: return False
    _TQOCC.append((lx, ly, rad)); return True

# The room is 22 x 11.2 m. It is zoned like a real market place: a fountain
# holding the west end, a bandstand holding the east, a cafe terrace down the
# whole north side, the market row down the whole south side, and a clear
# middle you could walk a horse through. Claims run in priority order.

# --- the fountain: the one thing in the square worth walking to
_tq_take(-6.6, 0.0, 2.60)
_fnx, _fny, _ = tsq_w(-6.6, 0.0)
disc('fnb', 2.45, 0.60, KERB,       (_fnx, _fny, 0.22), 32)
disc('fnw', 2.10, 0.56, M['water'], (_fnx, _fny, 0.20), 32)
disc('fnp', 0.60, 1.10, TSQBND,     (_fnx, _fny, 1.03), 16)
disc('fnc', 1.10, 0.26, TSQPAV,     (_fnx, _fny, 1.68), 20)
disc('fnu', 0.92, 0.18, M['water'], (_fnx, _fny, 1.70), 20)
disc('fnf', 0.20, 0.75, TSQBND,     (_fnx, _fny, 2.16), 12)

# --- the bandstand. Nothing says a town enjoys itself like somewhere to play.
_tq_take(6.6, 0.0, 2.65)
_bsx, _bsy, _ = tsq_w(6.6, 0.0)
disc('bsb', 2.40, 0.44, TSQBND, (_bsx, _bsy, 0.20), 8, math.pi/8)
disc('bsd', 2.18, 0.30, BENCHW, (_bsx, _bsy, 0.52), 8, math.pi/8)
for _bsk in range(8):
    _bsa = _bsk/8.0*6.283 + math.pi/8
    obj('bsp', mesh_from_bm(lump_box(0.13, 0.13, 2.30, 0.03, 2), 'bsp'), POST,
        (_bsx+math.cos(_bsa)*1.88, _bsy+math.sin(_bsa)*1.88, 1.82), (0, 0, _bsa))
disc('bsr', 2.54, 0.16, TSQMED, (_bsx, _bsy, 3.02), 8, math.pi/8)
_bsm = bmesh.new()
bmesh.ops.create_cone(_bsm, cap_ends=True, segments=8, radius1=2.42, radius2=0.06,
                      depth=1.24, matrix=Matrix.Rotation(math.pi/8, 4, 'Z'))
_bsme = mesh_from_bm(_bsm, 'bsrf'); _bsme.materials.append(M['roof_s'][2])
for _bsp in _bsme.polygons: _bsp.use_smooth = False
obj('bsrf', _bsme, None, (_bsx, _bsy, 3.72))
obj('bsf', mesh_from_bm(lump_box(0.15, 0.15, 0.62, 0.05, 2), 'bsf'), POST,
    (_bsx, _bsy, 4.59))

# --- four benches around the open middle, facing in across the inlay panel
for (_bnl, _bna) in ((-3.4, 1.7), (-3.4, -1.7), (3.4, 1.7), (3.4, -1.7)):
    if not _tq_take(_bnl, _bna, 1.05): continue
    _bwx, _bwy, _ = tsq_w(_bnl, _bna)
    linked('bnc', BENCH, (_bwx, _bwy, 0.17),
           (0, 0, TSQ_A + math.atan2(_bnl, _bna) + math.pi))

# --- lamps standing in the four corners of the room
for (_lmx, _lmy) in ((-9.9, 4.9), (9.9, 4.9), (-9.9, -4.9), (9.9, -4.9)):
    if _tq_take(_lmx, _lmy, 0.70):
        _lwx, _lwy, _ = tsq_w(_lmx, _lmy)
        lamp(_lwx, _lwy, TSQ_A)

# --- planted colour, in a container, on a defined edge (Law 4)
def planter(lx, ly):
    _plx, _ply, _ = tsq_w(lx, ly)
    obj('plt', mesh_from_bm(lump_box(2.20, 0.92, 0.60, 0.07, 3), 'plt'), TSQBND,
        (_plx, _ply, 0.34), (0, 0, TSQ_A))
    obj('pls', mesh_from_bm(lump_box(1.96, 0.70, 0.16, 0.05, 2), 'pls'), SOIL,
        (_plx, _ply, 0.68), (0, 0, TSQ_A))
    for _plk in range(7):
        _pfx, _pfy, _ = tsq_w(lx - 0.84 + _plk*0.28, ly + rr(-0.20, 0.20))
        obj('plf', mesh_from_bm(lump_box(0.30, 0.34, 0.26, 0.11, 3), 'plf'),
            M['flower'][(_plk*3) % 8], (_pfx, _pfy, 0.84))

for (_ptx, _pty) in ((-9.9, 2.6), (-9.9, -2.6), (9.9, 2.6), (9.9, -2.6)):
    if _tq_take(_ptx, _pty, 1.25): planter(_ptx, _pty)

# --- the cafe terrace: the whole north side, under bright parasols.
#     Parasols are the cheapest joy per object anywhere in the frame.
def cafe_set(lx, ly, ci):
    _cx, _cy, _ = tsq_w(lx, ly)
    _ca0 = rr(0, 6.28)
    obj('cfl', mesh_from_bm(lump_box(0.11, 0.11, 0.72, 0.03, 2), 'cfl'), POST,
        (_cx, _cy, 0.42))
    disc('cft', 0.46, 0.07, WHITE, (_cx, _cy, 0.81), 12)
    for _ck in range(3):
        _cha = _ca0 + _ck*2.094
        obj('cfc', mesh_from_bm(lump_box(0.34, 0.34, 0.42, 0.05, 2), 'cfc'),
            GAY[(ci+_ck) % 6],
            (_cx+math.cos(_cha)*0.80, _cy+math.sin(_cha)*0.80, 0.27), (0, 0, _cha))
    obj('cfp', mesh_from_bm(lump_box(0.09, 0.09, 2.30, 0.02, 2), 'cfp'), POST,
        (_cx, _cy, 1.20))
    _cum = bmesh.new()
    bmesh.ops.create_cone(_cum, cap_ends=True, segments=8, radius1=1.26, radius2=0.05,
                          depth=0.46, matrix=Matrix.Rotation(math.pi/8, 4, 'Z'))
    _cume = mesh_from_bm(_cum, 'cfu'); _cume.materials.append(GAY[ci % 6])
    for _cup in _cume.polygons: _cup.use_smooth = False
    obj('cfu', _cume, None, (_cx, _cy, 2.42))

_tqci = 0
_tqcx = -6.6
while _tqcx < 7.0:
    if _tq_take(_tqcx, 3.95, 1.20):
        cafe_set(_tqcx, 3.95, _tqci); _tqci += 1
    _tqcx += 2.7

# --- market day: one long row down the south side, all of it facing the square
_tqsx = -6.6
_tqsk = 0
while _tqsx < 7.0:
    if _tq_take(_tqsx, -4.05, 1.28):
        _stx, _sty, _ = tsq_w(_tqsx, -4.05)
        linked('stl', STALLS[_tqsk % 4], (_stx, _sty, 0.17), (0, 0, TSQ_A))
        _tqsk += 1
    _tqsx += 2.7

# --- bollards holding the north edge crisp against the High Street pavement
_TQBOL = mesh_from_bm(lump_box(0.19, 0.19, 0.68, 0.08, 3), 'tqbol')
_TQBOL.materials.append(M['brick'][4])
_tqbx = -9.90
while _tqbx < 10.0:
    _bwx2, _bwy2, _ = tsq_w(_tqbx, TSQ_HD - 0.30)
    if polyd(_bwx2, _bwy2, HIGH) > ROAD_HW + PAVE_W + 0.15:
        linked('bol', _TQBOL, (_bwx2, _bwy2, 0.50), (0, 0, TSQ_A))
    _tqbx += 1.50

# --- a low railing along the south edge, where the square looks over the ground
for _rlk in range(18):
    _rwx, _rwy, _ = tsq_w(-10.20 + _rlk*1.20, -(TSQ_HD - 0.10))
    obj('rlp', mesh_from_bm(lump_box(0.10, 0.10, 0.88, 0.03, 2), 'rlp'), POST,
        (_rwx, _rwy, 0.50), (0, 0, TSQ_A))
for _rlk in range(17):
    _rwx, _rwy, _ = tsq_w(-9.60 + _rlk*1.20, -(TSQ_HD - 0.10))
    obj('rlb', mesh_from_bm(lump_box(1.22, 0.07, 0.09, 0.02, 2), 'rlb'), POST,
        (_rwx, _rwy, 0.84), (0, 0, TSQ_A))

# --- shopfronts closing the east wall of the square, facing in
_tqsy = -5.00
while _tqsy < 2.50:
    _tqsw = rr(4.2, 5.8)
    _tqsl = _tqsy + _tqsw/2
    if _tqsl + _tqsw/2 > 2.80: break
    _tqsd = rr(4.8, 6.0); _tqsh = rr(4.6, 7.0)
    _shx2, _shy2, _ = tsq_w(TSQ_HW + 1.30 + _tqsd/2, _tqsl)
    _shok = inplate(_shx2, _shy2, 1.0) and not in_stadium(_shx2, _shy2, 1.6)
    if _shok and polyd(_shx2, _shy2, HIGH) < ROAD_HW + PAVE_W + _tqsd/2: _shok = False
    if _shok and any(polyd(_shx2, _shy2, _SL) < LANE_HW + _tqsd/2 + 0.5 for _SL in LANES):
        _shok = False
    if _shok:
        house(_shx2, _shy2, TSQ_A + math.pi/2, _tqsw, _tqsd, _tqsh, R() < 0.30)
    _tqsy += _tqsw + rr(0.18, 0.55)


# ------------------------------------------------------------ THE FRONTAGES
_HOCC = []

def _obb_hit(P, Q, m=0.05):
    """True if two (x, y, w, d, ang) footprints overlap, allowing a terrace gap."""
    for (A, B) in ((P, Q), (Q, P)):
        _c, _s = math.cos(A[4]), math.sin(A[4])
        _qc, _qs = math.cos(B[4]), math.sin(B[4])
        _dx, _dy = B[0]-A[0], B[1]-A[1]
        for (_ux, _uy, _he) in ((_c, _s, A[2]/2), (-_s, _c, A[3]/2)):
            _d = _dx*_ux + _dy*_uy
            _r = abs(_qc*_ux + _qs*_uy)*B[2]/2 + abs(-_qs*_ux + _qc*_uy)*B[3]/2
            if abs(_d) > _he + _r + m: return False
    return True

def _hfree(hx, hy, w, d, ang):
    """Claim ground for a house. False if a neighbour already owns it."""
    _n = (hx, hy, w, d, ang)
    for _o in _HOCC:
        if _obb_hit(_n, _o): return False
    _HOCC.append(_n); return True

def frontage(pts, side, s_from, s_to, avoid=None, terrace=0.44, depth=0.0):
    smp = resample(pts, 0.25); total = (len(smp)-1)*0.25
    s = s_from
    while s < min(s_to, total-3.0):
        w = rr(5.2, 8.4); d = rr(5.0, 6.4); h = rr(3.7, 5.8)
        i = int((s + w/2)/0.25)
        if i >= len(smp): break
        px, py, tg = smp[i]
        nx, ny = -math.sin(tg), math.cos(tg)
        off = ROAD_HW + PAVE_W + rr(0.5, 1.4) + d/2 + depth
        hx, hy = px + side*nx*off, py + side*ny*off
        F = (-side*nx, -side*ny)
        ang = math.atan2(-F[0], F[1]) + rr(-0.035, 0.035)
        if math.hypot(hx, hy) > TOWN_R - 1.0 or (avoid and avoid(hx, hy)) \
           or not _hfree(hx, hy, w + 0.02, d + 1.30, ang):
            s += w + rr(0.3, 1.4); continue
        house(hx, hy, ang, w, d, h, R() < 0.24, jetty=(R() < 0.10))
        s += w + (rr(0.15, 0.55) if R() < terrace else rr(2.6, 6.2))

def _avoid_civic(hx, hy):
    return in_square(hx, hy) or in_stadium(hx, hy, 1.2) or in_tsq(hx, hy, 2.0) or \
           math.hypot(hx-SQ_C[0], hy-SQ_C[1]) < SQ_R + 1.2

def _lane_core(pts, d=5.0):
    """A lane minus its junction throat and its gate end."""
    _sm = resample(pts, 0.5); _n = int(d/0.5)
    _c = [(_q[0], _q[1]) for _q in _sm[_n:len(_sm)-_n]]
    return _c if len(_c) >= 2 else [(_sm[len(_sm)//2][0], _sm[len(_sm)//2][1])]*2

LANECORE = [_lane_core(_p) for _p in LANES]

def _avoid_lane(hx, hy, pad=4.2):
    """Keep a house AND its plot off the back lanes. Half a plot is ~4.4 m."""
    return any(polyd(hx, hy, _AL) < LANE_HW + pad for _AL in LANECORE)

def _avoid_all(hx, hy):
    return _avoid_civic(hx, hy) or _avoid_lane(hx, hy)

frontage(HIGH,  1, 1.0, 76.0, _avoid_all)
frontage(HIGH, -1, 2.4, 76.0, _avoid_all)
frontage(MILL,  1, 1.5, 24.0, _avoid_all, terrace=0.34)
frontage(KIRK,  1, 1.5, 26.0, _avoid_all, terrace=0.38)
frontage(MILL, -1, 2.0, 24.0, _avoid_all, terrace=0.34)
frontage(KIRK, -1, 2.6, 26.0, _avoid_all, terrace=0.38)
frontage(HIGH,  1, 5.0, 72.0, _avoid_all, terrace=0.52, depth=11.4)
frontage(HIGH, -1, 8.5, 72.0, _avoid_all, terrace=0.52, depth=12.0)

# --- cottages down the back lanes. ONE flank per lane, set well back: a lane
# with houses hard against both sides is a 3 m slot and cannot read as a lane.
for _lni, _L in enumerate(LANES):
    _LC = LANECORE[_lni]
    _smp = resample(_L, 0.25); _tot = (len(_smp)-1)*0.25
    for _side in (1, -1):
        _s = rr(3.0, 5.5) + (0.0 if _side == 1 else 6.4)
        while _s < _tot - 3.0:
            _w = rr(4.6, 6.6); _d = rr(4.4, 5.6); _h = rr(3.4, 4.8)
            _i = int((_s + _w/2)/0.25)
            if _i >= len(_smp): break
            _px, _py, _tg = _smp[_i]
            _nx, _ny = -math.sin(_tg), math.cos(_tg)
            _off = LANE_HW + rr(2.6, 4.2) + _d/2
            _hx, _hy = _px + _side*_nx*_off, _py + _side*_ny*_off
            if math.hypot(_hx, _hy) > TOWN_R - 1.0 or _avoid_civic(_hx, _hy) \
               or paved(_hx, _hy) or any(polyd(_hx, _hy, _AL) < LANE_HW + 4.2
                                         for _AL in LANECORE if _AL is not _LC):
                _s += _w + rr(0.8, 2.4); continue
            _F = (-_side*_nx, -_side*_ny)
            _ha = math.atan2(-_F[0], _F[1]) + rr(-0.10, 0.10)
            if not _hfree(_hx, _hy, _w + 0.02, _d + 1.30, _ha):
                _s += _w + rr(0.8, 2.4); continue
            house(_hx, _hy, _ha, _w, _d, _h, R() < 0.7, jetty=(R() < 0.26))
            _s += _w + rr(1.8, 5.0)

# ------------------------------------------------- THE SQUARE: church + clock
# ---------------------------------------------------- THE CIVIC BUILDINGS
# Law 6, the Google-model construction order: plinth -> a repeated bay module ->
# a crisp cap -> then, and only then, props. No jitter anywhere; these two are
# the buildings the eye lands on, so they carry the standard for everything.
def clock_tower(px, py, ang=0.0):
    _BR, _ST = M['brick'][2], M['stone'][0]
    # 1. plinth: two crisp steps
    obj('twp', mesh_from_bm(lump_box(4.40, 4.40, 0.34, 0.05, 2), 'tp'),
        _ST, (px, py, 0.17), (0, 0, ang))
    obj('twp', mesh_from_bm(lump_box(3.96, 3.96, 0.30, 0.05, 2), 'tp'),
        _ST, (px, py, 0.49), (0, 0, ang))
    # 2. the repeated bay: shaft stage + tall recessed panel + string course
    _z = 0.64
    for _k in range(3):
        _w = 3.36 - _k*0.16
        obj('tws', mesh_from_bm(lump_box(_w, _w, 2.95, 0.06, 2), 'ts'),
            _BR, (px, py, _z + 1.475), (0, 0, ang))
        for _f in range(4):
            _fa = ang + _f*math.pi/2
            obj('twn', mesh_from_bm(lump_box(_w*0.40, 0.10, 1.85, 0.16, 3), 'tn'),
                (GLOW[2] if NIGHT else M['glass']),
                (px - math.sin(_fa)*(_w/2 + 0.01), py + math.cos(_fa)*(_w/2 + 0.01),
                 _z + 1.42), (0, 0, _fa))
            obj('twz', mesh_from_bm(lump_box(_w*0.56, 0.14, 0.12, 0.03, 2), 'tz'),
                _ST, (px - math.sin(_fa)*(_w/2 + 0.02), py + math.cos(_fa)*(_w/2 + 0.02),
                      _z + 2.44), (0, 0, _fa))
        obj('twc', mesh_from_bm(lump_box(_w + 0.30, _w + 0.30, 0.20, 0.035, 2), 'tc'),
            _ST, (px, py, _z + 3.05), (0, 0, ang))
        _z += 3.15
    # 3. the clock stage — the one moment of ornament, kept to four faces
    _cw = 2.90
    obj('twk', mesh_from_bm(lump_box(_cw, _cw, 2.20, 0.06, 2), 'tk'),
        _ST, (px, py, _z + 1.10), (0, 0, ang))
    for _f in range(4):
        _fa = ang + _f*math.pi/2
        _fx = px - math.sin(_fa)*(_cw/2 + 0.05)
        _fy = py + math.cos(_fa)*(_cw/2 + 0.05)
        obj('clr', mesh_from_bm(lump_box(1.62, 0.10, 1.62, 0.40, 4), 'cr'),
            M['stone'][2], (_fx, _fy, _z + 1.15), (0, 0, _fa))
        obj('clk', mesh_from_bm(lump_box(1.34, 0.09, 1.34, 0.34, 4), 'ck'),
            (GLOW[3] if NIGHT else WHITE),
            (_fx - math.sin(_fa)*0.05, _fy + math.cos(_fa)*0.05, _z + 1.15), (0, 0, _fa))
        for (_hl, _hh, _ha) in ((0.52, 0.055, 0.9), (0.36, 0.07, -1.9)):
            obj('clh', mesh_from_bm(lump_box(_hl, 0.05, _hh, 0.02, 2), 'ch'),
                M['brick'][4],
                (_fx - math.sin(_fa)*0.10 + math.cos(_fa)*math.cos(_ha)*_hl*0.5,
                 _fy + math.cos(_fa)*0.10 + math.sin(_fa)*math.cos(_ha)*_hl*0.5,
                 _z + 1.15 + math.sin(_ha)*_hl*0.5), (0, _ha, _fa))
    _z += 2.20
    # 4. the crisp cap: cornice, then a true four-sided pyramid, then a finial
    obj('twx', mesh_from_bm(lump_box(3.50, 3.50, 0.26, 0.04, 2), 'tx'),
        _ST, (px, py, _z + 0.13), (0, 0, ang))
    _z += 0.26
    _bp = bmesh.new()
    bmesh.ops.create_cone(_bp, cap_ends=True, segments=4, radius1=2.30, radius2=0.03,
                          depth=2.60, matrix=Matrix.Rotation(ang + math.pi/4, 4, 'Z'))
    _mp = mesh_from_bm(_bp, 'tcp'); _mp.materials.append(M['roof_s'][1])
    for _pg in _mp.polygons: _pg.use_smooth = False
    obj('tcp', _mp, None, (px, py, _z + 1.30))
    obj('twf', mesh_from_bm(lump_box(0.10, 0.10, 1.00, 0.03, 2), 'tf'),
        POST, (px, py, _z + 3.05), (0, 0, ang))
    obj('twg', mesh_from_bm(lump_sphere(0.20, 2, 0.0, 1.0), 'tg'),
        M['stone'][2], (px, py, _z + 3.62))

def church(px, py, ang):
    ca_, sa_ = math.cos(ang), math.sin(ang)
    def Wc(lx, ly, lz): return (px + lx*ca_ - ly*sa_, py + lx*sa_ + ly*ca_, lz)
    _ST, _S2 = M['stone'][1], M['stone'][0]
    L, Wd, H = 11.0, 6.4, 5.4
    # 1. plinth
    obj('chp', mesh_from_bm(lump_box(L + 1.0, Wd + 1.0, 0.34, 0.05, 2), 'cp'),
        _S2, Wc(0, 0, 0.17), (0, 0, ang))
    # 2. the nave, then the repeated bay: buttress, weathering, lancet between
    obj('nav', mesh_from_bm(lump_box(L, Wd, H, 0.08, 3), 'nv'),
        _ST, Wc(0, 0, 0.34 + H/2), (0, 0, ang))
    for _k in range(7):
        _lx = -L/2 + _k*(L/6.0)
        for _sy in (-1, 1):
            obj('bts', mesh_from_bm(lump_box(0.62, 0.60, H*0.84, 0.05, 2), 'bt'),
                _S2, Wc(_lx, _sy*(Wd/2 + 0.24), 0.34 + H*0.42), (0, 0, ang))
            obj('btc', mesh_from_bm(lump_box(0.80, 0.78, 0.16, 0.035, 2), 'bc'),
                _S2, Wc(_lx, _sy*(Wd/2 + 0.24), 0.34 + H*0.84 + 0.08), (0, 0, ang))
    for _k in range(6):
        _lx = -L/2 + (_k + 0.5)*(L/6.0)
        for _sy in (-1, 1):
            obj('cwr', mesh_from_bm(lump_box(1.00, 0.12, 3.00, 0.44, 4), 'cr'),
                _S2, Wc(_lx, _sy*(Wd/2 + 0.02), 0.34 + 2.90), (0, 0, ang))
            obj('cwn', mesh_from_bm(lump_box(0.74, 0.12, 2.72, 0.34, 4), 'cw'),
                (GLOW[2] if NIGHT else M['glass']),
                Wc(_lx, _sy*(Wd/2 + 0.06), 0.34 + 2.90), (0, 0, ang))
    # 3. the crisp cap: one clean slate prism with a verge, not a scatter of tiles
    _RH = 3.10
    _br = bmesh.new()
    _RX, _RY = L/2 + 0.30, Wd/2 + 0.32
    _pt = [(-_RX, -_RY, 0.0), (_RX, -_RY, 0.0), (_RX, _RY, 0.0), (-_RX, _RY, 0.0),
           (-_RX, 0.0, _RH), (_RX, 0.0, _RH)]
    _vv = [_br.verts.new(_q) for _q in _pt]
    _br.faces.new((_vv[0], _vv[1], _vv[5], _vv[4]))
    _br.faces.new((_vv[2], _vv[3], _vv[4], _vv[5]))
    _br.faces.new((_vv[0], _vv[4], _vv[3]))
    _br.faces.new((_vv[1], _vv[2], _vv[5]))
    _br.faces.new((_vv[0], _vv[3], _vv[2], _vv[1]))
    _br.normal_update()
    bmesh.ops.recalc_face_normals(_br, faces=list(_br.faces))
    _mr = mesh_from_bm(_br, 'crf'); _mr.materials.append(M['roof_s'][2])
    for _pg in _mr.polygons: _pg.use_smooth = False
    obj('crf', _mr, None, Wc(0, 0, 0.34 + H), (0, 0, ang))
    obj('crd', mesh_from_bm(lump_box(2*_RX + 0.12, 0.22, 0.16, 0.05, 3), 'cd'),
        _S2, Wc(0, 0, 0.34 + H + _RH + 0.02), (0, 0, ang))
    # 4. props: a south porch onto the square, and a bellcote over the west gable
    obj('cpo', mesh_from_bm(lump_box(2.30, 1.80, 2.90, 0.08, 3), 'po'),
        _S2, Wc(-L/2 + 3.4, -(Wd/2 + 0.90), 0.34 + 1.45), (0, 0, ang))
    obj('cpd', mesh_from_bm(lump_box(1.05, 0.14, 2.00, 0.44, 4), 'pd'),
        M['door'][1], Wc(-L/2 + 3.4, -(Wd/2 + 1.82), 0.34 + 1.05), (0, 0, ang))
    _pr = bmesh.new()
    bmesh.ops.create_cone(_pr, cap_ends=True, segments=4, radius1=1.75, radius2=0.02,
                          depth=1.10, matrix=Matrix.Rotation(math.pi/4, 4, 'Z') @
                          Matrix.Scale(0.78, 4, Vector((1, 0, 0))))
    _mpr = mesh_from_bm(_pr, 'cpr'); _mpr.materials.append(M['roof_s'][2])
    for _pg in _mpr.polygons: _pg.use_smooth = False
    obj('cpr', _mpr, None, Wc(-L/2 + 3.4, -(Wd/2 + 0.90), 0.34 + 2.90 + 0.55))
    obj('cbl', mesh_from_bm(lump_box(1.80, 0.66, 2.50, 0.06, 3), 'bl'),
        _S2, Wc(-L/2 - 0.06, 0, 0.34 + H + _RH*0.5 + 1.25), (0, 0, ang))
    obj('cbo', mesh_from_bm(lump_box(0.94, 0.72, 1.25, 0.42, 4), 'bo'),
        M['brick'][4], Wc(-L/2 - 0.06, 0, 0.34 + H + _RH*0.5 + 1.45), (0, 0, ang))
    obj('cbc', mesh_from_bm(lump_box(2.10, 0.90, 0.18, 0.04, 2), 'bk'),
        _S2, Wc(-L/2 - 0.06, 0, 0.34 + H + _RH*0.5 + 2.59), (0, 0, ang))

clock_tower(SQ_C[0]-4.4, SQ_C[1]+4.2, 0.18)
church(SQ_C[0]+3.6, SQ_C[1]+6.0, 0.10)
# market cross in the middle of the square
obj('mkb', mesh_from_bm(lump_box(2.2, 2.2, 0.42, 0.08, 3, 0.02), 'mk'),
    M['stone'][1], (SQ_C[0], SQ_C[1], 0.26), (0, 0, 0.2))
obj('mkp', mesh_from_bm(lump_box(0.44, 0.44, 3.1, 0.06, 3, 0.01), 'mp'),
    M['stone'][2], (SQ_C[0], SQ_C[1], 2.0), (0.01, -0.012, 0.2))
scatter_moss([(SQ_C[0]+rr(-1.1, 1.1), SQ_C[1]+rr(-1.1, 1.1), 0.44) for _ in range(9)],
             1, (0.3, 0.8))
# a terrace of shops closing the north side of the square
for _k in range(5):
    _a = -0.9 + _k*0.45
    _sx = SQ_C[0] + math.cos(_a)*(SQ_R+3.6)
    _sy = SQ_C[1] + math.sin(_a)*(SQ_R+3.6)
    house(_sx, _sy, _a + math.pi, rr(5.4, 6.8), rr(5.2, 6.0), rr(5.4, 6.4),
          R() < 0.5, jetty=(_k % 2 == 0))

# --------------------------------------------------------------- THE GROUND
def stadium(px, py, ang):
    ca_, sa_ = math.cos(ang), math.sin(ang)
    def Ws(lx, ly, lz): return (px+lx*ca_-ly*sa_, py+lx*sa_+ly*ca_, lz)
    PW, PL = 9.2, 14.2                       # half-width, half-length of pitch
    # mown pitch in stripes
    for k in range(14):
        lx = -PL + (k+0.5)*(2*PL/14)
        obj('ptc', mesh_from_bm(lump_box(2*PL/14, 2*PW, 0.10, 0.02, 2), 'pc'),
            PITCH1 if k % 2 == 0 else PITCH2, Ws(lx, 0, 0.06), (0, 0, ang))

    # --- PITCH MARKINGS. A green rectangle is a lawn; a marked one is a pitch.
    _LN = mesh_from_bm(lump_box(1.0, 1.0, 0.014, 0.004, 2), 'pln')
    _LN.materials.append(WHITE)
    def mark(lx, ly, lw, ld, rot=0.0):
        linked('pln', _LN, Ws(lx, ly, 0.112), (0, 0, ang + rot), (lw, ld, 1.0))
    _mx, _my, _t = PL*0.93, PW*0.90, 0.11
    mark(0,  _my, 2*_mx, _t); mark(0, -_my, 2*_mx, _t)      # touchlines
    mark(-_mx, 0, _t, 2*_my); mark(_mx, 0, _t, 2*_my)        # goal lines
    mark(0, 0, _t, 2*_my)                                    # halfway
    for _k in range(28):                                     # centre circle
        _a = _k/28.0*6.283
        mark(math.cos(_a)*2.55, math.sin(_a)*2.55, 0.60, _t, _a + math.pi/2)
    for _sg in (-1, 1):                                      # penalty + goal areas
        for (_bd, _bw) in ((3.30, 5.40), (1.30, 2.90)):
            mark(_sg*(_mx - _bd), 0, _t, 2*_bw)
            mark(_sg*(_mx - _bd/2),  _bw, _bd, _t)
            mark(_sg*(_mx - _bd/2), -_bw, _bd, _t)
        mark(_sg*(_mx - 2.30), 0, 0.22, 0.22)                # penalty spot
    mark(0, 0, 0.24, 0.24)                                   # centre spot
    # goals
    for sgn in (-1, 1):
        obj('gl1', mesh_from_bm(lump_box(0.10, 4.4, 0.10, 0.03, 2), 'g1'),
            WHITE, Ws(sgn*(PL-0.4), 0, 1.45), (0, 0, ang))
        for gy in (-2.2, 2.2):
            obj('gl2', mesh_from_bm(lump_box(0.10, 0.10, 1.5, 0.03, 2), 'g2'),
                WHITE, Ws(sgn*(PL-0.4), gy, 0.75), (0, 0, ang))
    # terracing: four banks of stepped concrete
    for (dx, dy, steps, along, half) in [(0, 1, 5, PL+0.8, PW+0.6),
                                         (0, -1, 5, PL+0.8, PW+0.6),
                                         (1, 0, 4, PW+0.6, PL+0.8),
                                         (-1, 0, 4, PW+0.6, PL+0.8)]:
        for st in range(steps):
            depth = 1.05
            o = half + 0.5 + st*depth
            hgt = 0.34 + st*0.46
            _seat = SEATA if st % 2 == 0 else SEATB
            if dy:
                obj('trc', mesh_from_bm(lump_box(2*along, depth, hgt, 0.04, 2), 'tr'),
                    CONC, Ws(0, dy*o, hgt/2), (0, 0, ang))
                obj('sea', mesh_from_bm(lump_box(2*along*0.97, depth*0.46, 0.26, 0.05, 2), 'se'),
                    _seat, Ws(0, dy*(o - dy*dy*depth*0.20), hgt + 0.13), (0, 0, ang))
            else:
                obj('trc', mesh_from_bm(lump_box(depth, 2*along, hgt, 0.04, 2), 'tr'),
                    CONC, Ws(dx*o, 0, hgt/2), (0, 0, ang))
                obj('sea', mesh_from_bm(lump_box(depth*0.46, 2*along*0.97, 0.26, 0.05, 2), 'se'),
                    _seat, Ws(dx*(o - dx*dx*depth*0.20), 0, hgt + 0.13), (0, 0, ang))
    # main stand: a pitched roof on posts down the near side
    obj('stf', mesh_from_bm(lump_box(2*PL+2.0, 7.2, 0.30, 0.08, 3, 0.02), 'sf'),
        M['roof_s'][1], Ws(0, PW+3.6, 4.6), (0.13, 0, ang))
    for k in range(9):
        obj('stp', mesh_from_bm(lump_box(0.26, 0.26, 4.4, 0.05, 2), 'sp'),
            POST, Ws(-PL-0.6 + k*(2*PL+1.2)/8, PW+5.1, 2.2), (0, 0, ang))
    obj('stb', mesh_from_bm(lump_box(2*PL+2.0, 0.5, 1.5, 0.06, 3), 'sb'),
        M['brick'][0], Ws(0, PW+5.4, 0.75), (0, 0, ang))
    # perimeter wall: four straight runs with a coping, not a ring of rubble
    _WX, _WY = PL + 6.2, PW + 6.4
    for (_wx, _wy, _ww, _wd) in ((0, _WY, 2*_WX, 0.38), (0, -_WY, 2*_WX, 0.38),
                                 (_WX, 0, 0.38, 2*_WY), (-_WX, 0, 0.38, 2*_WY)):
        obj('swl', mesh_from_bm(lump_box(_ww, _wd, 1.70, 0.05, 2), 'sw'),
            M['brick'][2], Ws(_wx, _wy, 0.85), (0, 0, ang))
        obj('swc', mesh_from_bm(lump_box(_ww+0.16, _wd+0.16, 0.14, 0.035, 2), 'sc'),
            KERB, Ws(_wx, _wy, 1.77), (0, 0, ang))

    # --- the car park: this is what makes a stadium read as a destination
    obj('cpk', mesh_from_bm(lump_box(2*PL+2.0, 8.6, 0.10, 0.03, 2), 'cp'),
        TARMAC, Ws(0, -(PW + 11.6), 0.05), (0, 0, ang))
    _CPB = mesh_from_bm(lump_box(0.10, 4.10, 0.012, 0.004, 2), 'cpb')
    _CPB.materials.append(WHITE)
    for _row in (-1, 1):
        for _k in range(19):
            _bx = -PL - 0.4 + _k*(2*PL+0.8)/18.0
            linked('cpb', _CPB, Ws(_bx, -(PW + 11.6) + _row*2.15, 0.102), (0, 0, ang))
            if _k < 18 and R() < 0.62:
                linked('car', CARS[int(R()*8)],
                       Ws(_bx + (2*PL+0.8)/36.0, -(PW + 11.6) + _row*2.15, 0.10),
                       (0, 0, ang + (math.pi/2 if _row > 0 else -math.pi/2)))
    # floodlight pylons
    for (fx, fy) in [(-PL-4.4, -PW-4.0), (PL+4.4, -PW-4.0),
                     (-PL+2.0, PW+6.6), (PL-2.0, PW+6.6)]:   # north pair pulled
        # in off the corners: the old NE mast stood inside the town square.
        for k in range(7):
            t = k/7.0
            obj('fpy', mesh_from_bm(lump_box(0.55*(1-t*0.5), 0.55*(1-t*0.5), 2.0,
                0.04, 2), 'fp'), POST, Ws(fx, fy, 1.0 + k*2.0), (0, 0, ang))
        obj('fhd', mesh_from_bm(lump_box(2.6, 0.5, 1.7, 0.06, 2), 'fh'),
            POST, Ws(fx, fy, 15.6), (0, 0, ang))
        obj('flt', mesh_from_bm(lump_box(2.4, 0.22, 1.5, 0.05, 2), 'fl'),
            (FLOOD if NIGHT else WHITE), Ws(fx, fy - 0.30, 15.6), (0, 0, ang))

stadium(STAD[0], STAD[1], STAD_A)
if NIGHT:
    _fl = bpy.data.lights.new('floodL', 'AREA'); _fl.energy = 780.0
    _fl.size = 15.0; _fl.color = (1.00, 0.96, 0.88)
    _fo = bpy.data.objects.new('floodL', _fl)
    _fo.location = (STAD[0], STAD[1], 21.0)
    COL.objects.link(_fo)

# --- low brick garden walls where a plot meets the street, not a ring
for _pl in STREETS:
    _smp = resample(_pl, 0.25)
    for _k in range(0, len(_smp), 4):
        _px, _py, _tg = _smp[_k]
        for _sd in (1, -1):
            if R() > 0.30: continue
            _nx, _ny = -math.sin(_tg), math.cos(_tg)
            _wx = _px + _sd*_nx*(ROAD_HW+PAVE_W+0.35)
            _wy = _py + _sd*_ny*(ROAD_HW+PAVE_W+0.35)
            if math.hypot(_wx, _wy) > TOWN_R: continue
            obj('wl', mesh_from_bm(lump_box(1.0, 0.26, rr(0.5, 0.66), 0.05, 3, 0.012), 'wl'),
                M['brick'][int(R()*5)], (_wx, _wy, rr(0.30, 0.38)), (0, 0, _tg))
            if R() < 0.28:
                scatter_moss([(_wx+rr(-0.2, 0.2), _wy+rr(-0.2, 0.2), rr(0.62, 0.78))],
                             1, (0.3, 0.7))

# --- street trees and the big ones on the open ground
for (_tx, _ty, _ts) in [(-19.6, 12.0, 0.78), (-10.2, 17.4, 0.66), (-6.4, 9.4, 0.58),
                        (5.6, 9.0, 0.60), (13.6, 8.2, 0.70), (21.0, 7.0, 0.80),
                        (-21.4, 1.2, 0.90), (-13.0, -4.6, 0.76), (-8.6, -13.0, 0.66),
                        (6.2, -6.2, 0.82), (15.4, -6.0, 0.92), (19.8, -14.6, 0.86),
                        (-20.0, -14.0, 0.95), (4.0, 19.6, 0.72), (-24.4, 18.0, 0.80),
                        (22.6, 14.2, 0.76), (10.0, -20.0, 0.82), (30.0, 9.0, 0.90),
                        (-33.0, 6.0, 0.95), (-30.0, -18.0, 1.00), (12.0, -26.0, 0.90),
                        (26.0, -20.0, 0.95), (-13.0, 27.0, 0.80), (9.0, 30.0, 0.90),
                        (33.0, -12.0, 0.85), (-6.0, 34.0, 0.90), (20.0, 26.0, 0.85)]:
    if built(_tx, _ty): continue
    tree(_tx, _ty, _ts)

# --- a few rocks at the wild rim only; the lawn itself stays clean
for _ in range(34):
    _sx, _sy = rr(-PLATE_X, PLATE_X), rr(-PLATE_Y, PLATE_Y)
    s = rr(0.7, 1.9)
    if not inplate(_sx, _sy, 1.2) or inplate(_sx, _sy, 7.0): continue
    if built(_sx, _sy): continue
    linked('sn', STONE[int(R()*6)], (_sx, _sy, gz(_sx,_sy)+0.12*s),
           (rr(0,0.4), rr(0,0.4), rr(0,6.28)), (s,s,s*0.7))
for _ in range(0):
    _cx, _cy = rr(-PLATE_X, PLATE_X), rr(-PLATE_Y, PLATE_Y)
    if not inplate(_cx, _cy, 3.5) or math.hypot(_cx,_cy) < 7.0: continue
    if built(_cx, _cy): continue
    ground_cover(_cx, _cy, 1.7, 34, gz(_cx,_cy), flowers=0.30, shrubs=0.34)

# --- the lush mat: the whole plate is covered, not just patches (Law 4)
# Planting reads as designed only when it clumps into beds with clean ground
# between them. An even sprinkle of small things is what makes a frame look
# messy, no matter how good each little thing is.
_beds = 0
while _beds < 30:
    _bx, _by = rr(-PLATE_X, PLATE_X), rr(-PLATE_Y, PLATE_Y)
    if not inplate(_bx, _by, 3.2) or inplate(_bx, _by, 12.0): continue
    if built(_bx, _by): continue
    _beds += 1
    _brad = rr(1.4, 3.4)
    _bn = int(_brad*_brad*rr(2.2, 4.0))
    for _ in range(_bn):
        _t = math.sqrt(R())
        _aa = R()*6.283
        gx = _bx + math.cos(_aa)*_brad*_t
        gy = _by + math.sin(_aa)*_brad*_t
        if built(gx, gy): continue
        zz = gz(gx, gy)
        q = R()
        if q < 0.62:
            sc = rr(0.70, 1.35)*(1.15 - 0.4*_t)
            linked('sh', SHRUB[int(R()*8)], (gx, gy, zz+0.28*sc),
                   (rr(-0.06,0.06), rr(-0.06,0.06), rr(0,6.28)), (sc, sc, sc*0.9))
        elif q < 0.86:
            sc = rr(0.40, 0.85)
            linked('tf', TUFT[int(R()*8)], (gx, gy, zz+0.30*sc),
                   (rr(-0.15,0.15), rr(-0.15,0.15), rr(0,6.28)), (sc, sc, sc))
        else:
            linked('fl', FLOWER[int(R()*10)], (gx, gy, zz+rr(0.10,0.22)),
                   (rr(-0.12,0.12), rr(-0.12,0.12), rr(0,6.28)))

# ---------------------------------------------------------- THE OPEN GROUND
# Reference 4 is elegant because the green is *organised*: everything belongs to
# a parcel. Outside the town the parcels are fields, divided by hedgerows, with
# a conifer belt (reference 1) holding the edge of the plate.
_FA = math.radians(17.0)
_fc, _fs = math.cos(_FA), math.sin(_FA)
_FW, _FD = 8.6, 10.4
_fields = []
for _i in range(-9, 10):
    for _j in range(-8, 9):
        _u, _v = (_i + 0.5)*_FW, (_j + 0.5)*_FD
        _fx = _u*_fc - _v*_fs
        _fy = _u*_fs + _v*_fc
        if math.hypot(_fx, _fy) < 24.5: continue
        _ok = True
        for _sx in (-1, 1):
            for _sy in (-1, 1):
                _cx = _fx + (_sx*_FW/2)*_fc - (_sy*_FD/2)*_fs
                _cy = _fy + (_sx*_FW/2)*_fs + (_sy*_FD/2)*_fc
                if not inplate(_cx, _cy, 1.6): _ok = False
        # a field may not run over anything the town has already claimed
        for _tu in range(4):
            for _tv in range(4):
                _cx = _fx + (_tu/3.0-0.5)*_FW*_fc - (_tv/3.0-0.5)*_FD*_fs
                _cy = _fy + (_tu/3.0-0.5)*_FW*_fs + (_tv/3.0-0.5)*_FD*_fc
                if built(_cx, _cy): _ok = False
        if not _ok: continue
        _fields.append((_fx, _fy))
        _fk = (_i*5 + _j*3) % 12
        _fdz = ((_i + 6) * 11 + (_j + 5)) % 7 * 0.004      # never coplanar
        obj('fld', mesh_from_bm(lump_box(_FW-0.5, _FD-0.5, 0.11, 0.030, 2), 'fld'),
            FIELD[_fk], (_fx, _fy, 0.055 + _fdz), (0, 0, _FA))
        # a managed field is *striped* — mown, drilled or ploughed. Reference 4
        # again: the eye reads the direction of work long before it reads colour.
        if _fk in (0, 3, 9, 10):                           # mown grass, striped
            _sn = 7
            for _k in range(_sn):
                if _k % 2: continue
                _sy2 = -(_FD-0.7)/2 + (_k+0.5)*(_FD-0.7)/_sn
                obj('fst', mesh_from_bm(lump_box(_FW-0.7, (_FD-0.7)/_sn, 0.02, 0.006, 2), 'fs'),
                    FIELD[1], (_fx - _sy2*_fs, _fy + _sy2*_fc, 0.122 + _fdz), (0, 0, _FA))
        elif _fk == 8:                                     # ploughed: soil furrows
            _sn = 13
            for _k in range(_sn):
                if _k % 2: continue
                _sx2 = -(_FW-0.7)/2 + (_k+0.5)*(_FW-0.7)/_sn
                obj('fst', mesh_from_bm(lump_box((_FW-0.7)/_sn, _FD-0.7, 0.02, 0.006, 2), 'fs'),
                    SOIL, (_fx + _sx2*_fc, _fy + _sx2*_fs, 0.122 + _fdz), (0, 0, _FA))
        elif _fk in (5, 11):                               # cut for hay: bales
            for _k in range(6):
                _bx, _by = rr(-_FW*0.36, _FW*0.36), rr(-_FD*0.38, _FD*0.38)
                obj('bal', mesh_from_bm(lump_box(1.05, 0.80, 0.78, 0.30, 3), 'bl'),
                    FIELD[11], (_fx + _bx*_fc - _by*_fs, _fy + _bx*_fs + _by*_fc,
                                0.50 + _fdz), (0, 0, _FA + rr(-0.25, 0.25)))
        # HEDGEROWS. These are the drawn lines of the landscape; at plate scale a
        # 0.8m hedge is invisible. A real field boundary is chest-high and solid.
        for (_hx, _hy, _hw, _hd) in ((0, _FD/2-0.22, _FW-0.44, 0.42),
                                     (0, -(_FD/2-0.22), _FW-0.44, 0.42),
                                     (_FW/2-0.22, 0, 0.42, _FD-0.44),
                                     (-(_FW/2-0.22), 0, 0.42, _FD-0.44)):
            if R() < 0.14: continue
            _hgt = rr(0.95, 1.20)
            obj('hrw', mesh_from_bm(lump_box(_hw, _hd, _hgt, 0.19, 3, 0.02), 'hr'),
                HEDGES[int(R()*4)], (_fx + _hx*_fc - _hy*_fs, _fy + _hx*_fs + _hy*_fc,
                                     _hgt/2 + 0.09), (0, 0, _FA))
        for _nt in range(2):                 # standards left in the hedge line
            if R() < 0.52: continue
            _ox, _oy = rr(-_FW*0.34, _FW*0.34), (_FD/2-0.3)*(1 if R() < 0.5 else -1)
            tree(_fx + _ox*_fc - _oy*_fs, _fy + _ox*_fs + _oy*_fc, rr(0.80, 1.15))

# --- THE NEAR RING. Between the last house and the first field there was one
# flat sheet of green. Reference 4 has no such thing: right up to the edge of
# the built area the ground is still parcelled — paddocks, allotments, orchards,
# a pony field. Small cells fit between the lanes where a full field cannot.
_GW, _GD = 4.4, 5.2
RAIL = clay('rail', (206, 196, 178), 0.80, 0.06)
for _i in range(-13, 14):
    for _j in range(-12, 13):
        _u, _v = (_i + 0.5)*_GW, (_j + 0.5)*_GD
        _px2 = _u*_fc - _v*_fs
        _py2 = _u*_fs + _v*_fc
        _rd2 = math.hypot(_px2, _py2)
        if _rd2 < 15.0 or _rd2 > 24.0: continue
        _ok2 = True
        for _tu in range(3):
            for _tv in range(3):
                _cx = _px2 + (_tu/2.0-0.5)*(_GW-0.3)*_fc - (_tv/2.0-0.5)*(_GD-0.3)*_fs
                _cy = _py2 + (_tu/2.0-0.5)*(_GW-0.3)*_fs + (_tv/2.0-0.5)*(_GD-0.3)*_fc
                if built(_cx, _cy) or not inplate(_cx, _cy, 2.0): _ok2 = False
        if not _ok2: continue
        _gk = (_i*7 + _j*5) % 12
        _gdz = ((_i + 9)*13 + (_j + 8)) % 6 * 0.004
        obj('prc', mesh_from_bm(lump_box(_GW-0.4, _GD-0.4, 0.10, 0.028, 2), 'pr'),
            FIELD[_gk], (_px2, _py2, 0.05 + _gdz), (0, 0, _FA))
        _kind = R()
        if _kind < 0.36:                       # allotments: drilled beds
            for _b in range(4):
                _by2 = -(_GD-0.8)/2 + (_b+0.5)*(_GD-0.8)/4
                obj('alb', mesh_from_bm(lump_box(_GW-0.9, (_GD-0.8)/4*0.54, 0.14, 0.04, 2), 'ab'),
                    SOIL, (_px2 - _by2*_fs, _py2 + _by2*_fc, 0.13 + _gdz), (0, 0, _FA))
                if R() < 0.72:
                    obj('alr', mesh_from_bm(lump_box(_GW-1.3, (_GD-0.8)/4*0.28, 0.20, 0.08, 2), 'ar'),
                        M['grass'][int(R()*4)], (_px2 - _by2*_fs, _py2 + _by2*_fc,
                                                 0.28 + _gdz), (0, 0, _FA))
        elif _kind < 0.62:                     # an orchard: a grid of small trees
            for _oi in range(2):
                for _oj in range(2):
                    _ox = (_oi-0.5)*(_GW*0.46); _oy = (_oj-0.5)*(_GD*0.46)
                    tree(_px2 + _ox*_fc - _oy*_fs, _py2 + _ox*_fs + _oy*_fc,
                         rr(0.42, 0.54), 'broad')
        elif _kind < 0.80:                     # a paddock with a field shelter
            _shx, _shy = _GW*0.20, _GD*0.24
            obj('shd', mesh_from_bm(lump_box(1.90, 1.40, 1.75, 0.06, 2), 'sh'),
                M['timber'], (_px2 + _shx*_fc - _shy*_fs,
                              _py2 + _shx*_fs + _shy*_fc, 0.88), (0, 0, _FA))
            obj('shr', mesh_from_bm(lump_box(2.24, 1.72, 0.15, 0.04, 2), 'sr'),
                M['roof_s'][3], (_px2 + _shx*_fc - _shy*_fs,
                                 _py2 + _shx*_fs + _shy*_fc, 1.80), (0, 0, _FA))
        # every parcel is bounded — post-and-rail here, hedge there
        _post = R() < 0.45
        for (_hx, _hy, _hw, _hd) in ((0, _GD/2-0.18, _GW-0.36, 0.44),
                                     (0, -(_GD/2-0.18), _GW-0.36, 0.44),
                                     (_GW/2-0.18, 0, 0.44, _GD-0.36),
                                     (-(_GW/2-0.18), 0, 0.44, _GD-0.36)):
            _wx2 = _px2 + _hx*_fc - _hy*_fs
            _wy2 = _py2 + _hx*_fs + _hy*_fc
            if _post:
                for _rz in (0.48, 0.86):
                    obj('rl', mesh_from_bm(lump_box(_hw if _hw > _hd else 0.09,
                                                    _hd if _hd > _hw else 0.09,
                                                    0.10, 0.03, 2), 'rl'),
                        RAIL, (_wx2, _wy2, _rz), (0, 0, _FA))
            else:
                _hg2 = rr(0.85, 1.15)
                obj('phg', mesh_from_bm(lump_box(_hw, _hd, _hg2, 0.26, 3, 0.02), 'ph'),
                    HEDGES[int(R()*4)], (_wx2, _wy2, _hg2/2 + 0.08), (0, 0, _FA))

# a conifer belt holding the rim, thickening toward the corners
for _i in range(230):
    _a = R()*6.283
    _sc = 1.0/max(1e-6, ((abs(math.cos(_a))/PLATE_X)**PLATE_N +
                         (abs(math.sin(_a))/PLATE_Y)**PLATE_N)**(1.0/PLATE_N))
    _rd = _sc * rr(0.865, 0.985)
    _bx, _by = math.cos(_a)*_rd, math.sin(_a)*_rd
    if math.hypot(_bx, _by) < 30.0 or built(_bx, _by): continue
    tree(_bx, _by, rr(0.66, 1.05), 'conifer' if R() < 0.72 else 'broad')

# ---------------------------------------------------------------- light (Law 6)
import os as _os0
def _E2(k,d): return float(_os0.environ.get(k,d))
world = bpy.data.worlds.new('w'); S.world = world; world.use_nodes = True
nt = world.node_tree
bg = nt.nodes['Background']
sky = nt.nodes.new('ShaderNodeTexSky')
_types = sky.bl_rna.properties['sky_type'].enum_items.keys()
for _t in ('MULTIPLE_SCATTERING', 'NISHITA', 'SINGLE_SCATTERING', 'HOSEK_WILKIE'):
    if _t in _types:
        sky.sky_type = _t; break
def _set(o, k, v):
    if hasattr(o, k):
        try: setattr(o, k, v)
        except Exception: pass
_set(sky, 'sun_elevation', math.radians(16))
_set(sky, 'sun_rotation', math.radians(150))
_set(sky, 'altitude', 200)
_set(sky, 'air_density', 2.2)
_set(sky, 'dust_density', 3.4)
bgc = nt.nodes.new('ShaderNodeBackground')
bgc.inputs[0].default_value = (0.74, 0.78, 0.80, 1.0)
bgc.inputs[1].default_value = 1.05
_tc = nt.nodes.new('ShaderNodeTexCoord')
_sxyz = nt.nodes.new('ShaderNodeSeparateXYZ')
_ramp = nt.nodes.new('ShaderNodeValToRGB')
nt.links.new(_tc.outputs['Window'], _sxyz.inputs[0])
nt.links.new(_sxyz.outputs['Y'], _ramp.inputs['Fac'])
_ramp.color_ramp.elements[0].position = 0.0
_ramp.color_ramp.elements[0].color = (0.052, 0.072, 0.078, 1.0)
_ramp.color_ramp.elements[1].position = 1.0
_ramp.color_ramp.elements[1].color = (0.128, 0.158, 0.166, 1.0)
nt.links.new(_ramp.outputs['Color'], bgc.inputs[0])
mixw = nt.nodes.new('ShaderNodeMixShader')
lp = nt.nodes.new('ShaderNodeLightPath')
out = nt.nodes['World Output']
nt.links.new(sky.outputs[0], bg.inputs[0])
nt.links.new(lp.outputs['Is Camera Ray'], mixw.inputs[0])
nt.links.new(bg.outputs[0], mixw.inputs[1])
nt.links.new(bgc.outputs[0], mixw.inputs[2])
nt.links.new(mixw.outputs[0], out.inputs[0])
bg.inputs[1].default_value = _E2('SKY_S', 0.24)

import os as _os
def _E(k, d): return float(_os.environ.get(k, d))
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = _E('SUN_E', 4.6)
sun.angle = math.radians(_E('SUN_A', 15.0))          # a big soft key, near-shadowless
sun.color = (1.0, 0.93, 0.84)
so = bpy.data.objects.new('sun', sun); COL.objects.link(so)
so.rotation_euler = (math.radians(70), 0, math.radians(-44))

fill = bpy.data.lights.new('fill', 'AREA'); fill.energy = _E('FILL_E', 340)
fill.size = 60; fill.color = (0.92, 0.95, 1.0)
fo = bpy.data.objects.new('fill', fill); COL.objects.link(fo)
fo.location = (-34, 38, 34); fo.rotation_euler = (math.radians(44), 0, math.radians(-140))

bounce = bpy.data.lights.new('bnc', 'AREA'); bounce.energy = _E('BNC_E', 560)
bounce.size = 66; bounce.color = (1.0, 0.94, 0.86)
bo = bpy.data.objects.new('bnc', bounce); COL.objects.link(bo)
bo.location = (30, -34, 14); bo.rotation_euler = (math.radians(96), 0, math.radians(40))

# ---------------------------------------------------------------- camera (Law 7)
cam = bpy.data.cameras.new('cam'); cam.lens = _E('LENS', 76)
cam.dof.use_dof = True
cam.dof.focus_distance = _E('FOCUS', _E('CAM_D', 197.0)); cam.dof.aperture_fstop = _E('FSTOP', 0.80)
co = bpy.data.objects.new('cam', cam); COL.objects.link(co)
_tx, _ty, _tz = _E('CAM_TX', 0.0), _E('CAM_TY', 0.0), _E('CAM_TZ', 0.0)
_cd, _cel, _caz = _E('CAM_D', 197.0), _E('CAM_EL', 33.0), _E('CAM_AZ', 132.0)
_cp, _ca = math.radians(_cel), math.radians(_caz)
co.location = (_tx + _cd*math.cos(_cp)*math.cos(_ca),
               _ty + _cd*math.cos(_cp)*math.sin(_ca),
               _tz + _cd*math.sin(_cp))
co.rotation_euler = (math.radians(90.0-_cel), 0, math.radians(_caz+90.0))
S.camera = co

# ---------------------------------------------------------------- render
S.render.engine = 'CYCLES'
S.cycles.device = 'CPU'
S.cycles.samples = SAMP
S.cycles.use_adaptive_sampling = True
S.cycles.adaptive_threshold = 0.02
S.cycles.use_denoising = True
S.cycles.max_bounces = 6
S.cycles.diffuse_bounces = 4
S.render.resolution_x = W; S.render.resolution_y = H
S.render.film_transparent = False
S.view_settings.view_transform = 'AgX'
for _lk in (__import__('os').environ.get('LOOK', 'AgX - Medium Low Contrast'),
            'AgX - Base Contrast', 'AgX - Medium Contrast'):
    try:
        S.view_settings.look = _lk; break
    except Exception: pass
S.view_settings.exposure = float(__import__('os').environ.get('EXPO', -0.10))
S.render.filepath = OUT
if NIGHT:
    bgc.inputs[0].default_value = (0.034, 0.026, 0.072, 1.0)
    bgc.inputs[1].default_value = 0.90
    bg.inputs[1].default_value  = _E2('SKY_S', 0.011)
    sun.energy  = _E('SUN_E', 0.60); sun.color = (0.46, 0.56, 1.00)
    fill.energy = _E('FILL_E', 46.0); bounce.energy = _E('BNC_E', 105.0)
    S.view_settings.exposure = float(__import__('os').environ.get('EXPO', 1.30))

# --- compositor: global saturation + a little bloom on the lights ---
_ng = bpy.data.node_groups.new('cmp', 'CompositorNodeTree')
_ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
_rl = _ng.nodes.new('CompositorNodeRLayers')
_go = _ng.nodes.new('NodeGroupOutput')
_hs = _ng.nodes.new('CompositorNodeHueSat')
_hs.inputs['Saturation'].default_value = float(__import__('os').environ.get('SAT', 1.16))
_hs.inputs['Value'].default_value = float(__import__('os').environ.get('VAL', 1.02))
_gl = _ng.nodes.new('CompositorNodeGlare')
_gl.inputs['Type'].default_value = 'Fog Glow'
_gl.inputs['Quality'].default_value = 'Medium'
_gl.inputs['Threshold'].default_value = 0.90
_gl.inputs['Size'].default_value = 0.42
_gl.inputs['Strength'].default_value = float(__import__('os').environ.get('BLOOM', 0.26))
_ng.links.new(_rl.outputs['Image'], _hs.inputs['Image'])
_ng.links.new(_hs.outputs['Image'], _gl.inputs['Image'])
_ng.links.new(_gl.outputs['Image'], _go.inputs['Image'])
S.use_nodes = True
S.compositing_node_group = _ng

print('objects:', len(bpy.data.objects), flush=True)
if int(__import__('os').environ.get('BUILD_ONLY', '0')): raise SystemExit(0)
bpy.ops.render.render(write_still=True)
print('WROTE', OUT)
