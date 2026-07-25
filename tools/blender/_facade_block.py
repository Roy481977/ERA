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
            open_a = rr(0.30, 1.30) if R() < 0.62 else 0.0
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

def window_mats(wallmat):
    return [_DRESS, _JOIN, M['glass'], TEAL[int(R()*5)], M['timber'], _IRONB]

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
    plan = [(0.0,  d/2, math.pi,     w, True),
            (0.0, -d/2, 0.0,         w, False),
            ( w/2, 0.0, math.pi/2,   d, False),
            (-w/2, 0.0, -math.pi/2,  d, False)]
    for (lx0, ly0, rel, pw, is_front) in plan:
        pang = ang + rel
        pcs, psn = math.cos(pang), math.sin(pang)
        org = W(lx0, ly0, 0.0)
        nwin = max(1, int(round(pw / 2.15)))
        slots = [-pw/2 + (k + 0.5) * (pw / nwin) for k in range(nwin)]
        dslot = int(R() * nwin) if is_front else -1
        opens, units = [], []
        for k, cx in enumerate(slots):
            for fi, cz in enumerate(rows):
                if k == dslot and fi == 0:
                    continue
                if not is_front and R() < 0.18:
                    continue
                ww_ = WIN_W * rr(0.94, 1.08)
                wh_ = WIN_H * rr(0.94, 1.06)
                if fi == 0 and pw / nwin > 2.6 and R() < 0.30:
                    ww_ *= 1.5                       # the occasional wide opening
                opens.append((cx - ww_/2, cx + ww_/2, cz - wh_/2, cz + wh_/2))
                units.append((cx, cz, ww_, wh_, fi))
        dh_ = 2.10
        if dslot >= 0:
            dcx = slots[dslot]
            opens.append((dcx - 0.48, dcx + 0.48, 0.0, dh_))
        for (a, b, c, e) in list(opens):                      # keep it out of the roof
            if e > h - 0.20:
                opens.remove((a, b, c, e))
                units = [u for u in units if abs(u[1] - (c + e) / 2) > 1e-9]
        bmp = wall_panel(pw, h, t, opens)
        obj('wal', _flat(mesh_from_bm(bmp, 'wal')), wallmat, org, (0, 0, pang))
        for (cx, cz, ww_, wh_, fi) in units:
            bal = (balconies and fi == 1 and is_front and R() < 0.55)
            bm = window_mesh(ww_, wh_, t,
                             shutters=(R() < 0.90),
                             box=(not bal and R() < 0.38),
                             arch=(R() < 0.18))
            multi(bm, 'win', window_mats(wallmat),
                  (org[0] + cx*pcs, org[1] + cx*psn, cz), (0, 0, pang))
            if bal:
                multi(balcony_mesh(ww_ + 0.62), 'bal', balcony_mats(),
                      (org[0] + cx*pcs, org[1] + cx*psn, cz - wh_/2 - 0.16),
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

