"""Suporte modular para gabinete torre com batentes ajustaveis por clique.
Padrao: Dell Pro Max Tower T2 (FCT2250) - 187,7 x 438 mm de base.
Edite os parametros e rode: python3 gerar_suporte.py
Requer: pip install manifold3d trimesh numpy
"""
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

# ---------------- PARAMETROS (mm) ----------------
CASE_W = 187.7    # largura do gabinete
CASE_D = 438.0    # profundidade do gabinete
H      = 40       # altura do suporte (piso -> onde o gabinete apoia)
BW     = 50       # largura da viga
MAX_SEG = 200     # comprimento maximo de cada viga (cabe em mesa 220x220)
# Chave "gravata borboleta" que une as pecas
KEY_NECK, KEY_WIDE, KEY_HALF = 16, 28, 18
CLEAR   = 0.2     # folga por lado da chave
GUSSET  = 35      # reforco triangular no canto interno
WALL, TOP, END_SOLID = 6, 7, 28   # viga oca por baixo
# Trilho + batente com clique
GW      = 16.5    # largura do trilho (canal no topo da viga)
GD      = 10      # profundidade do trilho
GL      = 34      # comprimento do trilho (a partir da face externa)
PITCH   = 2.0     # passo do clique (cada clique = 2 mm)
NOTCH   = 0.7     # profundidade dos dentes na parede do trilho
TONGUE_L = 18     # comprimento da lingueta do batente
SLIDE_CLR = 0.25  # folga por lado lingueta x trilho
ARM_T   = 1.8     # espessura das hastes-mola
ARM_GAP = 1.2     # vao atras da haste-mola
BUMP    = 0.7     # altura do dente da haste-mola
CAP_L   = 12      # espessura do batente (direcao do ajuste)
CAP_W   = 30      # largura do batente
CAP_H   = 16      # altura do batente acima do apoio
NOMINAL = 20      # distancia nominal da borda do gabinete ate a face externa da moldura
# --------------------------------------------------

W_OUT = CASE_W + 2 * NOMINAL
D_OUT = CASE_D + 2 * NOMINAL
ARM = W_OUT / 2
SIDE_GAP = D_OUT - 2 * ARM
N_BEAMS = max(1, math.ceil(SIDE_GAP / MAX_SEG)) if SIDE_GAP > 1 else 0
BEAM_L = SIDE_GAP / N_BEAMS if N_BEAMS else 0
KEY_C = BW / 2
CORNER_GROOVE_X = ARM - END_SOLID - 14       # posicao do trilho no braco do canto
GROOVE_SOLID = GW / 2 + WALL                 # regiao macica em volta do trilho


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def prism(pts, h, z0=0.0):
    area = sum(a * d - c * b for (a, b), (c, d) in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
        pts = pts[::-1]
    return Manifold.extrude(CrossSection([pts]), h).translate([0, 0, z0])


def union(ms):
    out = Manifold()
    for m in ms:
        out = out + m
    return out


# ---------- juntas ----------
def half_slot(face_x, direction, c):
    d = -direction
    n, w, k = KEY_NECK / 2, KEY_WIDE / 2, KEY_HALF
    pts = [(face_x + 2 * direction, c - n), (face_x + d * k, c - w),
           (face_x + d * k, c + w), (face_x + 2 * direction, c + n)]
    return prism(pts, H + 2, -1)


def key():
    n, w, k = KEY_NECK / 2 - CLEAR, KEY_WIDE / 2 - CLEAR, KEY_HALF - CLEAR
    return prism([(-k, -w), (0, -n), (k, -w), (k, w), (0, n), (-k, w)], H - 0.6)


# ---------- trilho com dentes ----------
def groove(xc):
    """Canal no topo, aberto na face externa (y=0), paredes com dentes em zigue-zague."""
    g = box(xc - GW / 2, -1, H - GD, xc + GW / 2, GL, H + 1)
    teeth = []
    y = TONGUE_L - 6
    while y + PITCH <= GL + 1e-6:
        for s in (-1, 1):
            xw = xc + s * GW / 2
            teeth.append(prism([(xw, y), (xw + s * NOTCH, y + PITCH / 2), (xw, y + PITCH)],
                               GD + 1, H - GD))
        y += PITCH
    return g + union(teeth)


def pockets_along(x0, x1, grooves):
    """Cavidades por baixo de x0 a x1, pulando a regiao macica dos trilhos."""
    cuts, a = [], x0
    for g in sorted(grooves):
        b = g - GROOVE_SOLID
        if b - a > 10:
            cuts.append(box(a, WALL, -1, b, BW - WALL, H - TOP))
        a = g + GROOVE_SOLID
    if x1 - a > 10:
        cuts.append(box(a, WALL, -1, x1, BW - WALL, H - TOP))
    return union(cuts)


def beam(L):
    gx = L / 2
    b = box(0, 0, 0, L, BW, H)
    b = b - pockets_along(END_SOLID, L - END_SOLID, [gx]) - groove(gx)
    return b - half_slot(0, -1, KEY_C) - half_slot(L, +1, KEY_C)


def corner():
    ax = box(0, 0, 0, ARM, BW, H)
    ay = box(0, 0, 0, BW, ARM, H)
    g = prism([(BW, BW), (BW + GUSSET, BW), (BW, BW + GUSSET)], H)
    c = ax + ay + g
    cut = pockets_along(BW + WALL, ARM - END_SOLID, [CORNER_GROOVE_X]) \
        + groove(CORNER_GROOVE_X) + half_slot(ARM, +1, KEY_C)
    return c - cut - cut.mirror([1, -1, 0])


# ---------- batente deslizante com clique ----------
def stop():
    """Coordenadas de montagem: y=0 na face externa, lingueta dentro do trilho.
    Hastes-mola laterais com dente estalam nos dentes do trilho a cada PITCH mm."""
    tw = GW - 2 * SLIDE_CLR
    t_bot, t_top = H - GD + 0.3, H + 0.3            # lingueta apoia no fundo do trilho
    tongue = box(-tw / 2, 0, t_bot, tw / 2, TONGUE_L, t_top)
    # vaos que liberam as hastes (abertos na ponta, presos em y<4)
    xi = tw / 2 - ARM_T
    for s in (-1, 1):
        x0, x1 = sorted([s * xi, s * (xi - ARM_GAP)])
        tongue = tongue - box(x0, 4, t_bot - 1, x1, TONGUE_L + 1, t_top - 1.5)
        # separa a haste do batente por cima (vao de 1,5 mm), exceto na raiz
        x0, x1 = sorted([s * (xi - ARM_GAP), s * (tw / 2 + 1)])
        tongue = tongue - box(x0, 4, t_top - 1.5, x1, TONGUE_L + 1, t_top + 0.01)
        # dente na ponta da haste
        xo = s * tw / 2
        yb = TONGUE_L - 3
        bump_h = BUMP + SLIDE_CLR
        tongue = tongue + prism([(xo, yb - 1.2), (xo + s * bump_h, yb), (xo, yb + 1.2)],
                                t_top - 1.5 - t_bot, t_bot)
    # cabeca do batente (chanfro 45 graus por baixo para imprimir sem suporte)
    ch = (CAP_W - tw) / 2
    prof = [(-tw / 2, t_top), (tw / 2, t_top), (CAP_W / 2, t_top + ch),
            (CAP_W / 2, H + CAP_H), (-CAP_W / 2, H + CAP_H), (-CAP_W / 2, t_top + ch)]
    cap = prism([(x, z) for x, z in prof], CAP_L).rotate([90, 0, 0]).translate([0, CAP_L, 0])
    # chanfro guia no topo, lado do gabinete
    guide = prism([(CAP_L - 4, H + CAP_H + 1), (CAP_L + 1, H + CAP_H + 1),
                   (CAP_L + 1, H + CAP_H - 5)], CAP_W + 2, -(CAP_W / 2 + 1))
    guide = guide.rotate([90, 0, 0]).rotate([0, 0, 90]).mirror([1, 0, 0])
    return tongue + cap - guide


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


def save(m, name):
    t = to_trimesh(m)
    assert t.is_watertight and t.volume > 0, name
    t.export(name)
    e = t.bounds[1] - t.bounds[0]
    print(f"{name}: {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm, volume {t.volume/1000:.0f} cm3")


def place_x(m, x):           # peca na borda frontal (y=0 externo)
    return m.translate([x, 0, 0])


def frame_and_stops(stop_pos=None):
    """Monta tudo. stop_pos = deslocamento dos batentes (0..GL-TONGUE_L)."""
    s = (NOMINAL - CAP_L) if stop_pos is None else stop_pos
    cr, frame, stops, keys = corner(), [], [], []
    frame += [cr, cr.mirror([1, 0, 0]).translate([W_OUT, 0, 0]),
              cr.mirror([0, 1, 0]).translate([0, D_OUT, 0]),
              cr.mirror([1, 0, 0]).mirror([0, 1, 0]).translate([W_OUT, D_OUT, 0])]
    st = stop().translate([0, s, 0])
    # trilhos na frente/tras (bracos X) e nas laterais (bracos Y e vigas)
    front = [st.translate([x, 0, 0]) for x in (CORNER_GROOVE_X, W_OUT - CORNER_GROOVE_X)]
    stops += front + [m.mirror([0, 1, 0]).translate([0, D_OUT, 0]) for m in front]
    side_y = [CORNER_GROOVE_X, D_OUT - CORNER_GROOVE_X]
    bm = beam(BEAM_L)
    for i in range(N_BEAMS):
        y0 = ARM + i * BEAM_L
        left = bm.mirror([1, -1, 0]).translate([0, y0, 0])
        frame += [left, left.mirror([1, 0, 0]).translate([W_OUT, 0, 0])]
        side_y.append(y0 + BEAM_L / 2)
    for y in side_y:
        l = st.mirror([1, -1, 0]).translate([0, y, 0])
        stops += [l, l.mirror([1, 0, 0]).translate([W_OUT, 0, 0])]
    kk = key()
    joints = [(ARM, KEY_C, 0), (ARM, D_OUT - KEY_C, 0)]
    for i in range(N_BEAMS + 1):
        y = ARM + i * BEAM_L
        joints += [(KEY_C, y, 90), (W_OUT - KEY_C, y, 90)]
    keys = [kk.rotate([0, 0, r]).translate([x, y, 0]) for x, y, r in joints]
    return frame, stops, keys


if __name__ == "__main__":
    travel = GL - TONGUE_L
    lo, hi = CAP_L, CAP_L + travel
    print(f"Moldura externa: {W_OUT:.1f} x {D_OUT:.1f} mm, altura {H} mm (+{CAP_H} mm batentes)")
    print(f"Ajuste: {travel/PITCH:.0f} cliques de {PITCH} mm por batente "
          f"-> aceita gabinete de {W_OUT-2*hi:.1f} a {W_OUT-2*lo:.1f} mm de largura "
          f"e {D_OUT-2*hi:.1f} a {D_OUT-2*lo:.1f} mm de profundidade")
    save(corner(), "canto.stl")
    save(beam(BEAM_L), "viga.stl")
    save(key(), "chave.stl")
    # batente impresso de pe (lingueta na mesa)
    save(stop().translate([0, 0, -(H - GD + 0.3)]), "batente.stl")
    for pos in (0, travel):
        frame, stops, keys = frame_and_stops(pos)
        inter = sum((a ^ b).volume() for a in stops + keys for b in frame)
        print(f"Interferencia c/ batente em {pos} mm: {inter:.3f} mm3 (deve ser ~0)")
    frame, stops, keys = frame_and_stops()
    trimesh.util.concatenate([to_trimesh(p) for p in frame + stops + keys]) \
        .export("montagem_preview.stl")
    print(f"Imprimir: 4x canto, {2*N_BEAMS}x viga ({BEAM_L:.1f} mm), "
          f"{len(keys)}x chave, {len(stops)}x batente")
