"""Suporte modular para gabinete torre (CPU) - gera os STLs.
Edite os parametros abaixo e rode: python3 gerar_suporte.py
Requer: pip install manifold3d trimesh numpy
"""
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

# ---------------- PARAMETROS (mm) ----------------
CASE_W = 230      # largura interna do encaixe (largura do gabinete + folga)
CASE_D = 480      # profundidade interna do encaixe (profundidade do gabinete + folga)
H      = 40       # altura do suporte (piso -> onde o gabinete apoia)
LIP_T  = 6        # espessura da borda de contencao
LIP_H  = 10       # altura da borda acima do apoio
BW     = 50       # largura total da viga (inclui a borda)
MAX_SEG = 200     # comprimento maximo de cada viga (cabe em mesa 220x220)
# Chave "gravata borboleta" (dovetail)
KEY_NECK = 16     # largura no meio da chave (na junta)
KEY_WIDE = 28     # largura nas pontas
KEY_HALF = 18     # profundidade de cada metade
CLEAR   = 0.2     # folga por lado da chave
GUSSET  = 35      # reforco triangular no canto interno
WALL    = 6       # parede das vigas ocas (por baixo)
TOP     = 7       # espessura do tampo das vigas ocas
END_SOLID = 28    # trecho macico nas pontas (onde fica a chave)
# --------------------------------------------------

W_OUT = CASE_W + 2 * LIP_T
D_OUT = CASE_D + 2 * LIP_T
ARM = W_OUT / 2                      # bracos do canto (iguais -> 4 cantos identicos)
SIDE_GAP = D_OUT - 2 * ARM
N_BEAMS = max(1, math.ceil(SIDE_GAP / MAX_SEG)) if SIDE_GAP > 1 else 0
BEAM_L = SIDE_GAP / N_BEAMS if N_BEAMS else 0
KEY_C = LIP_T + (BW - LIP_T) / 2     # posicao do centro da chave na largura da viga


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def prism(pts, h, z0=0.0):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
        pts = pts[::-1]
    return Manifold.extrude(CrossSection([pts]), h).translate([0, 0, z0])


def half_slot(face_x, direction, c):
    """Encaixe meia-borboleta aberto na face x=face_x, entrando no sentido -direction."""
    d = -direction
    n, w, k = KEY_NECK / 2, KEY_WIDE / 2, KEY_HALF
    pts = [(face_x + 2 * direction, c - n),           # sai um pouco da face p/ corte limpo
           (face_x + d * k, c - w),
           (face_x + d * k, c + w),
           (face_x + 2 * direction, c + n)]
    return prism(pts, H + 2, -1)


def straight_profile(L):
    """Viga reta ao longo de X, x em [0,L]; borda externa em y=[0,LIP_T]."""
    seat = box(0, 0, 0, L, BW, H)
    lip = box(0, 0, 0, L, LIP_T, H + LIP_H)
    return seat + lip


def pocket_x(x0, x1):
    """Cavidade aberta por baixo ao longo de X (viga oca em U invertido)."""
    if x1 - x0 < 10:
        return Manifold()
    return box(x0, WALL, -1, x1, BW - WALL, H - TOP)


def beam(L):
    b = straight_profile(L) - pocket_x(END_SOLID, L - END_SOLID)
    b = b - half_slot(0, -1, KEY_C) - half_slot(L, +1, KEY_C)
    return b


def corner():
    # braco X
    ax = straight_profile(ARM)
    # braco Y (borda em x=[0,LIP_T])
    ay = box(0, 0, 0, BW, ARM, H) + box(0, 0, 0, LIP_T, ARM, H + LIP_H)
    g = prism([(BW, BW), (BW + GUSSET, BW), (BW, BW + GUSSET)], H)
    c = ax + ay + g
    px = pocket_x(BW + WALL, ARM - END_SOLID)
    c = c - px - px.mirror([1, -1, 0])
    # encaixe na ponta do braco X (face x=ARM)
    c = c - half_slot(ARM, +1, KEY_C)
    # encaixe na ponta do braco Y: mesmo corte rotacionado (espelho na diagonal)
    sy = half_slot(ARM, +1, KEY_C)
    sy = sy.mirror([1, -1, 0])  # espelha x<->y
    c = c - sy
    return c


def key():
    n, w, k = KEY_NECK / 2 - CLEAR, KEY_WIDE / 2 - CLEAR, KEY_HALF - CLEAR
    pts = [(-k, -w), (0, -n), (k, -w), (k, w), (0, n), (-k, w)]
    return prism(pts, H - 0.6)


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)


def save(m, name):
    t = to_trimesh(m)
    assert t.is_watertight, name
    t.export(name)
    ext = t.bounds[1] - t.bounds[0]
    print(f"{name}: {ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm, volume {t.volume/1000:.0f} cm3")
    return t


def assembly():
    parts = []
    cr = corner()
    # 4 cantos: origem do canto = canto externo
    parts.append(cr)                                                   # frente-esq
    parts.append(cr.mirror([1, 0, 0]).translate([W_OUT, 0, 0]))        # frente-dir
    parts.append(cr.mirror([0, 1, 0]).translate([0, D_OUT, 0]))        # tras-esq
    parts.append(cr.mirror([1, 0, 0]).mirror([0, 1, 0]).translate([W_OUT, D_OUT, 0]))
    bm = beam(BEAM_L)
    for i in range(N_BEAMS):
        y0 = ARM + i * BEAM_L
        # viga ao longo de Y, borda do lado externo
        left = bm.mirror([1, -1, 0]).translate([0, y0, 0])
        right = left.mirror([1, 0, 0]).translate([W_OUT, 0, 0])
        parts += [left, right]
    kk = key()
    joints = [(ARM, KEY_C, 0), (ARM, D_OUT - KEY_C, 0)]
    for i in range(N_BEAMS + 1):
        y = ARM + i * BEAM_L
        joints += [(KEY_C, y, 90), (W_OUT - KEY_C, y, 90)]
    for x, y, r in joints:
        parts.append(kk.rotate([0, 0, r]).translate([x, y, 0]))
    return parts, len(joints)


if __name__ == "__main__":
    print(f"Estrutura externa: {W_OUT:.0f} x {D_OUT:.0f} mm, altura {H} mm (+{LIP_H} mm de borda)")
    save(corner(), "canto.stl")
    if N_BEAMS:
        save(beam(BEAM_L), "viga.stl")
    save(key(), "chave.stl")
    parts, nkeys = assembly()
    frame, keys = parts[:-nkeys], parts[-nkeys:]
    inter = sum((k ^ f).volume() for k in keys for f in frame)
    print(f"Interferencia chave x pecas: {inter:.3f} mm3 (deve ser 0)")
    trimesh.util.concatenate([to_trimesh(p) for p in parts]).export("montagem_preview.stl")
    print(f"Imprimir: 4x canto, {2*N_BEAMS}x viga ({BEAM_L:.1f} mm), {nkeys}x chave")
