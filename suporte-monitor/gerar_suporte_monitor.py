"""Suporte de monitor (riser) com 2 pernas em "Z" frisadas + tampo de madeira.
O tampo (MDF/madeira) entra nas luvas de cima das pernas.
Edite os parametros e rode: python3 gerar_suporte_monitor.py
Requer: pip install manifold3d trimesh numpy
"""
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, JoinType, OpType

# ---------------- PARAMETROS (mm) ----------------
BOARD_T = 18      # espessura do tampo de madeira
BOARD_D = 200     # profundidade do tampo
FIT     = 0.4     # folga total do tampo dentro da luva
HEIGHT  = 110     # altura total (mesa -> topo da perna)
LEG_W   = 75      # largura de cada perna
CAP     = 5       # parede lateral externa da luva (fecha a ponta do tampo)
WALL    = 6       # paredes da luva
FOOT_T  = 9       # espessura do pe
SLANT_W = 26      # largura (horizontal) da diagonal
R_OUT   = 4       # arredondamento das quinas externas
R_IN    = 10      # concordancia nas juncoes
GROOVE_W, GROOVE_D, GROOVE_P = 2.2, 1.0, 5.0   # frisos
# --------------------------------------------------

D = BOARD_D + 2 * WALL                 # comprimento da luva
SLOT_H = BOARD_T + FIT
Z_S = HEIGHT - (SLOT_H + 2 * WALL)     # base da luva
FOOT_Y0 = 0.18 * D                     # inicio do pe (atras)
SL_BOT = 0.38 * D                      # diagonal: posicao na mesa
SL_TOP = 0.02 * D                      # diagonal: posicao na luva


def cs(pts):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return CrossSection([pts if a > 0 else pts[::-1]])


def rect(y0, z0, y1, z1):
    return cs([(y0, z0), (y1, z0), (y1, z1), (y0, z1)])


def outer_profile():
    sleeve = rect(0, Z_S, D, HEIGHT)
    foot = rect(FOOT_Y0, 0, D, FOOT_T)
    slant = cs([(SL_BOT, 0), (SL_BOT + SLANT_W, 0),
                (SL_TOP + SLANT_W, Z_S + 1), (SL_TOP, Z_S + 1)])
    p = sleeve + foot + slant
    p = p.offset(R_IN, JoinType.Round).offset(-R_IN, JoinType.Round)    # concordancias
    p = p.offset(-R_OUT, JoinType.Round).offset(R_OUT, JoinType.Round)  # quinas
    # garante base reta (o arredondamento nao mexe no plano z=0, mas corta qualquer sobra)
    return p ^ rect(-50, 0, D + 50, HEIGHT)


def extrude_x(c, x0, x1):
    m = Manifold.extrude(c, x1 - x0)   # (u,v,w)=(y,z,x)
    return m.transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


def leg():
    prof = outer_profile()
    body = extrude_x(prof, 0, LEG_W)
    slot = extrude_x(rect(WALL, Z_S + WALL, D - WALL, Z_S + WALL + SLOT_H), CAP, LEG_W + 1)
    body = body - slot
    # frisos: faixa na borda externa do perfil, sem a sola do pe
    band = (prof - prof.offset(-GROOVE_D, JoinType.Miter)) - rect(-50, -1, D + 50, 1.5)
    n = int((LEG_W - 8) // GROOVE_P)
    x0 = (LEG_W - n * GROOVE_P) / 2
    cuts = [extrude_x(band, x0 + i * GROOVE_P - GROOVE_W / 2, x0 + i * GROOVE_P + GROOVE_W / 2)
            for i in range(n + 1)]
    return body - Manifold.batch_boolean(cuts, OpType.Add)


def to_tm(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3],
                           np.asarray(mesh.tri_verts), process=False)


if __name__ == "__main__":
    L = leg()
    t = to_tm(L)
    assert L.status().name == "NoError" and t.is_watertight
    # arquivos para imprimir: deitada, face lateral externa (tampa da luva) na mesa
    for nome, m in (("perna_esquerda.stl", L), ("perna_direita.stl", L.mirror([1, 0, 0]))):
        m = m.rotate([0, -90, 0]) if nome.startswith("perna_esq") else m.rotate([0, 90, 0])
        bb = m.bounding_box()
        m = m.translate([-bb[0], -bb[1], -bb[2]])
        tm = to_tm(m)
        assert tm.is_watertight
        tm.export(nome)
        e = tm.bounds[1] - tm.bounds[0]
        print(f"{nome}: {e[0]:.0f} x {e[1]:.0f} x {e[2]:.0f} mm, volume {tm.volume/1000:.0f} cm3")
    print(f"Tampo: {BOARD_T} mm de espessura x {BOARD_D} mm de profundidade; "
          f"entra {LEG_W-CAP:.0f} mm em cada perna")
    # montagem para visualizar (tampo de 600 mm)
    BL = 600
    legs = [L.mirror([1, 0, 0]).translate([BL / 2 + CAP, 0, 0]),
            L.translate([-BL / 2 - CAP, 0, 0])]
    board = Manifold.cube([BL, BOARD_D, BOARD_T]).translate([-BL / 2, WALL, Z_S + WALL + FIT / 2])
    trimesh.util.concatenate([to_tm(m) for m in legs]).export("preview_pernas.stl")
    to_tm(board).export("preview_tampo.stl")
