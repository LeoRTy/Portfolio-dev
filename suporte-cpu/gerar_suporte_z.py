"""Suporte de CPU estilo "offset": 2 pernas laterais em Z, frisadas, com borda.
Padrao: Dell Pro Max Tower T2 (FCT2250) - 187,7 x 438 mm de base.
Rode: pip install manifold3d trimesh numpy && python3 gerar_suporte_z.py
"""
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, JoinType, OpType

# ---------------- PARAMETROS (mm) ----------------
CASE_W = 187.7     # largura do gabinete
CASE_D = 438.0     # profundidade do gabinete
CLR    = 1.0       # folga na profundidade (frente/tras)
H      = 55        # altura do apoio (mesa -> onde o gabinete senta)
BAR    = 75        # largura da prateleira de cima (onde o gabinete apoia)
BAR_T  = 12        # espessura da prateleira
OFF    = 32        # deslocamento da diagonal (o "offset" do Z)
SPINE  = 24        # largura horizontal da diagonal
FOOT   = 80        # largura do pe
FOOT_T = 10        # espessura do pe
LIP_T, LIP_H = 8, 14   # borda que segura o gabinete
R_OUT, R_IN = 3, 10    # arredondamentos
GROOVE_W, GROOVE_D, GROOVE_P = 2.2, 1.0, 5.0   # frisos
ESPELHADO = True   # True: pes abrindo para os dois lados; False: as duas pernas no mesmo sentido
N_SEG  = 3         # pedacos por perna (cabe em mesa 220x220)
KEY_NECK, KEY_WIDE, KEY_HALF, KEY_CLR = 12, 20, 12, 0.2
# --------------------------------------------------

D_TOT = CASE_D + CLR + 2 * LIP_T
SEG_L = D_TOT / N_SEG


def cs(pts):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return CrossSection([pts if a > 0 else pts[::-1]])


def rect(x0, z0, x1, z1):
    return cs([(x0, z0), (x1, z0), (x1, z1), (x0, z1)])


def profile(side):
    """Perfil no plano (x, z). Diagonal sempre do mesmo lado (igual a foto):
    sai do canto esquerdo da prateleira e desce para a direita ate o pe.
    side='dir': borda na ponta direita da prateleira; side='esq': na ponta esquerda."""
    bar = rect(0, H - BAR_T, BAR, H)
    foot = rect(OFF, 0, OFF + FOOT, FOOT_T)
    spine = cs([(OFF, 0), (OFF + SPINE, 0), (SPINE, H - BAR_T + 1), (0, H - BAR_T + 1)])
    lip = rect(BAR - LIP_T, H - 1, BAR, H + LIP_H) if side == "dir" else rect(0, H - 1, LIP_T, H + LIP_H)
    p = bar + foot + spine + lip
    p = p.offset(R_IN, JoinType.Round).offset(-R_IN, JoinType.Round)
    p = p.offset(-R_OUT, JoinType.Round).offset(R_OUT, JoinType.Round)
    return p ^ rect(-50, 0, 300, 300)


def extrude_y(c, y0, y1):
    m = Manifold.extrude(c, y1 - y0)            # (u,v,w) = (x,z,y)
    return m.transform([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0]])


def bowtie(clr):
    n, w, k = KEY_NECK / 2 - clr, KEY_WIDE / 2 - clr, KEY_HALF - clr
    return cs([(-w, -k), (-n, 0), (-w, k), (w, k), (n, 0), (w, -k)])


def key_slots(y):
    """Encaixes de chave na junta y: um na prateleira e um no pe."""
    s = bowtie(0)
    out = []
    for xc, z0, z1 in ((BAR / 2, H - BAR_T - 1, H + 1), (OFF + FOOT * 0.6, -1, FOOT_T + 1)):
        out.append(Manifold.extrude(s, z1 - z0).translate([xc, y, z0]))
    return out


def key(h):
    return Manifold.extrude(bowtie(KEY_CLR), h - 0.4)


def segment(side, i):
    y0, y1 = i * SEG_L, (i + 1) * SEG_L
    prof = profile(side)
    body = extrude_y(prof, y0, y1)
    # bordas de frente e de tras (so nos pedacos das pontas)
    if i == 0:
        body = body + Manifold.cube([BAR, LIP_T, LIP_H + 1]).translate([0, y0, H - 1])
    if i == N_SEG - 1:
        body = body + Manifold.cube([BAR, LIP_T, LIP_H + 1]).translate([0, y1 - LIP_T, H - 1])
    body = body ^ extrude_y(profile(side) + rect(0, H - 1, BAR, H + LIP_H), y0, y1)  # arredonda
    # frisos ao longo do perfil, sem mexer na sola
    band = (prof - prof.offset(-GROOVE_D, JoinType.Miter)) - rect(-50, -1, 300, 1.5)
    n = int((y1 - y0 - 6) // GROOVE_P)
    s0 = y0 + (y1 - y0 - n * GROOVE_P) / 2
    cuts = [extrude_y(band, s0 + k * GROOVE_P - GROOVE_W / 2, s0 + k * GROOVE_P + GROOVE_W / 2)
            for k in range(n + 1)]
    body = body - Manifold.batch_boolean(cuts, OpType.Add)
    for y in (y0, y1):
        if 0 < y < D_TOT - 1e-6:
            for s in key_slots(y):
                body = body - s
    return body


def to_tm(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3],
                           np.asarray(mesh.tri_verts), process=False)


def x_offset_right():
    # gabinete encosta na borda esquerda (x = LIP_T) e na direita
    return LIP_T + CASE_W - (BAR - LIP_T)


def leg_segment(side, i):
    """Pedaco da perna na posicao de montagem (perna esquerda com x a partir de 0)."""
    if ESPELHADO and side == "esq":
        return segment("dir", i).mirror([1, 0, 0]).translate([BAR, 0, 0])
    return segment(side, i)


def leg_keys(side):
    kb, kf = key(BAR_T), key(FOOT_T)
    ks = []
    for i in range(1, N_SEG):
        y = i * SEG_L
        ks += [kb.translate([BAR / 2, y, H - BAR_T + 0.2]),
               kf.translate([OFF + FOOT * 0.6, y, 0.2])]
    if ESPELHADO and side == "esq":
        ks = [k.mirror([1, 0, 0]).translate([BAR, 0, 0]) for k in ks]
    return ks


if __name__ == "__main__":
    names = ["frente", "meio", "tras"] if N_SEG == 3 else [str(i) for i in range(N_SEG)]
    xr = x_offset_right()
    frame, keys = [], []
    for side in ("esq", "dir"):
        dx = 0 if side == "esq" else xr
        for i in range(N_SEG):
            seg = leg_segment(side, i)
            assert seg.status().name == "NoError"
            frame.append(seg.translate([dx, 0, 0]))
            # imprimir em pe: perfil na mesa (pontas com a borda para baixo)
            p = seg.translate([0, -i * SEG_L, 0]).rotate([90, 0, 0])
            if i == N_SEG - 1:
                p = p.rotate([180, 0, 0])
            bb = p.bounding_box()
            p = p.translate([-bb[0], -bb[1], -bb[2]])
            t = to_tm(p)
            assert t.is_watertight
            fn = f"perna_{side}_{names[i]}.stl"
            t.export(fn)
            e = t.bounds[1] - t.bounds[0]
            print(f"{fn}: {e[0]:.0f} x {e[1]:.0f} x {e[2]:.0f} mm, {t.volume/1000:.0f} cm3")
        keys += [k.translate([dx, 0, 0]) for k in leg_keys(side)]
    to_tm(key(BAR_T)).export("chave_prateleira.stl")
    to_tm(key(FOOT_T)).export("chave_pe.stl")
    inter = sum((a ^ b).volume() for a in keys for b in frame)
    print(f"Interferencia chaves: {inter:.3f} mm3")
    trimesh.util.concatenate([to_tm(m) for m in frame + keys]).export("montagem_preview.stl")
    bb = trimesh.load("montagem_preview.stl").bounds
    print(f"Medidas totais {bb[1][0]-bb[0][0]:.0f} x {bb[1][1]-bb[0][1]:.0f} mm, altura {H} mm "
          f"(+{LIP_H} borda). Vao livre no meio: {xr - BAR:.0f} mm. x0={bb[0][0]:.1f}")
