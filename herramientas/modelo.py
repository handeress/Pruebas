"""Generador común de los modelos 3D del portal (opciones A y B).

Coordenadas de planta: x a lo ancho, y (z en 3D) hacia el frente; piso terminado en 0.
Cada diseño trae bloques, muros con vanos, pasillo de vidrio, terrazas, escalera y muebles.
"""
import numpy as np

BTC = (196, 182, 158)        # muros y cubierta: bloque de tierra comprimida (el visor le dibuja las hiladas)
MARCO = (112, 114, 117)      # marcos de ventana, grises
VIDRIO = (160, 190, 205)
PISO = (186, 152, 112)       # piso interior en madera
BORDE = (168, 166, 158)      # canto de placa: concreto arquitectónico
DECK = (142, 104, 71)
MADERA = (150, 108, 68)
BLANCO = (236, 233, 226)
TELA = (122, 124, 112)
TELA2 = (168, 158, 132)
OSCURO = (70, 72, 74)
PIEDRA = (196, 194, 186)
VERDE = (118, 138, 92)


class Malla:
    def __init__(s):
        s.g = {"base": ([], []), "cub": ([], []), "vid": ([], [])}

    def tri(s, g, a, b, c, col):
        s.g[g][0].append([a, b, c]); s.g[g][1].append(col)

    def quad(s, g, a, b, c, d, col):
        s.tri(g, a, b, c, col); s.tri(g, a, c, d, col)

    def caja(s, g, x0, z0, x1, z1, y0, y1, col, top=None):
        if x1 < x0: x0, x1 = x1, x0
        if z1 < z0: z0, z1 = z1, z0
        P = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        b = [(x, y0, z) for x, z in P]; t = [(x, y1, z) for x, z in P]
        s.quad(g, b[0], b[3], b[2], b[1], col)
        s.quad(g, t[0], t[1], t[2], t[3], top or col)
        for i in range(4):
            j = (i + 1) % 4
            s.quad(g, b[i], b[j], t[j], t[i], col)

    def cilindro(s, g, cx, cz, r, y0, y1, col, n=10):
        for i in range(n):
            a0, a1 = 2 * np.pi * i / n, 2 * np.pi * (i + 1) / n
            p0 = (cx + r * np.cos(a0), cz + r * np.sin(a0)); p1 = (cx + r * np.cos(a1), cz + r * np.sin(a1))
            s.quad(g, (p0[0], y0, p0[1]), (p1[0], y0, p1[1]), (p1[0], y1, p1[1]), (p0[0], y1, p0[1]), col)
            s.tri(g, (cx, y1, cz), (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), col)

    def arrays(s):
        return {k: (np.array(v[0], np.float32), np.array(v[1], np.uint8)) for k, v in s.g.items() if v[0]}


# ------------------------------------------------------------------ vanos
VANOS = {  # antepecho, dintel (None = hasta el dintel del bloque)
    "PT": (0.0, None), "V": (0.9, 2.2), "K": (1.15, 2.2), "A": (1.7, 2.3), "D": (0.0, 2.1), "O": (0.0, 2.4), "G": (0.0, None),
}


def muro(M, r, H, ops, ext=True):
    x0, z0, x1, z1 = r; h = (x1 - x0) >= (z1 - z0)
    a0, a1 = (x0, x1) if h else (z0, z1)
    cur = a0; tr = []
    for o in sorted(ops):
        if o[0] > cur: tr.append(("S", cur, o[0]))
        tr.append((o[2], o[0], o[1])); cur = o[1]
    if cur < a1: tr.append(("S", cur, a1))
    for k, s0, s1 in tr:
        rr = (s0, z0, s1, z1) if h else (x0, s0, x1, s1)
        if k == "S":
            M.caja("base", *rr, 0, H, BTC); continue
        ant, din = VANOS[k]; din = (H - 0.3) if din is None else din
        if k == "G": din = H
        if ant > 0: M.caja("base", *rr, 0, ant, BTC)
        if din < H: M.caja("base", *rr, din, H, BTC)
        if k == "O" or (k == "D" and not ext): continue
        c = ((rr[0] + rr[2]) / 2, (rr[1] + rr[3]) / 2)
        if k == "D":    # puerta exterior en madera
            if h: M.caja("base", rr[0] + 0.04, c[1] - 0.025, rr[2] - 0.04, c[1] + 0.025, 0, din, MADERA)
            else: M.caja("base", c[0] - 0.025, rr[1] + 0.04, c[0] + 0.025, rr[3] - 0.04, 0, din, MADERA)
            continue
        ventana(M, rr, h, ant, din)


def ventana(M, rr, h, y0, y1):
    """Vidrio con marco perimetral y parales cada 1,20 m como máximo."""
    L = (rr[2] - rr[0]) if h else (rr[3] - rr[1])
    a0 = rr[0] if h else rr[1]
    c = (rr[1] + rr[3]) / 2 if h else (rr[0] + rr[2]) / 2
    f, e = 0.05, 0.035
    def pieza(s0, s1, ya, yb, col, g="base", esp=e):
        if h: M.caja(g, s0, c - esp, s1, c + esp, ya, yb, col)
        else: M.caja(g, c - esp, s0, c + esp, s1, ya, yb, col)
    pieza(a0 + f, a0 + L - f, y0 + f, y1 - f, VIDRIO, "vid", 0.008)
    pieza(a0, a0 + f, y0, y1, MARCO); pieza(a0 + L - f, a0 + L, y0, y1, MARCO)
    pieza(a0, a0 + L, y1 - f, y1, MARCO); pieza(a0, a0 + L, y0, y0 + f, MARCO)
    n = max(1, int(np.ceil(L / 1.2)))
    for i in range(1, n):
        s = a0 + L * i / n; pieza(s - f / 2, s + f / 2, y0, y1, MARCO)
    if y0 > 0.3:   # alféizar en concreto
        if h: M.caja("base", a0 - 0.05, c - 0.1, a0 + L + 0.05, c + 0.1, y0 - 0.05, y0, BORDE)
        else: M.caja("base", c - 0.1, a0 - 0.05, c + 0.1, a0 + L + 0.05, y0 - 0.05, y0, BORDE)


# ------------------------------------------------------------------ muebles
def mueble(M, tipo, r, y=0.0):
    r = tuple(r) + (0.0,) * max(0, 4 - len(r))
    x0, z0, x1, z1 = r[:4]; rot = r[4] if len(r) > 4 else "N"   # rot: lado de la cabecera o del espaldar
    C = M.caja
    if tipo == "cama":
        C("base", x0, z0, x1, z1, y, y + 0.3, MADERA); C("base", x0 + 0.03, z0 + 0.03, x1 - 0.03, z1 - 0.03, y + 0.3, y + 0.52, BLANCO)
        # cobija sobre los dos tercios del pie y cabecera
        if rot in "NS":
            zc = z0 + (z1 - z0) * (0.35 if rot == "N" else 0.0); zd = z1 - (z1 - z0) * (0.0 if rot == "N" else 0.35)
            C("base", x0 + 0.02, zc, x1 - 0.02, zd, y + 0.52, y + 0.56, TELA2)
            zz = z0 if rot == "N" else z1 - 0.08; C("base", x0, zz, x1, zz + 0.08, y, y + 1.0, MADERA)
        else:
            xc = x0 + (x1 - x0) * (0.35 if rot == "W" else 0.0); xd = x1 - (x1 - x0) * (0.0 if rot == "W" else 0.35)
            C("base", xc, z0 + 0.02, xd, z1 - 0.02, y + 0.52, y + 0.56, TELA2)
            xx = x0 if rot == "W" else x1 - 0.08; C("base", xx, z0, xx + 0.08, z1, y, y + 1.0, MADERA)
    elif tipo == "mesa_noche": C("base", x0, z0, x1, z1, y, y + 0.5, MADERA)
    elif tipo == "closet": C("base", x0, z0, x1, z1, y, y + 2.2, MADERA)
    elif tipo == "estante": C("base", x0, z0, x1, z1, y, y + 1.9, (176, 160, 130))
    elif tipo == "meson":
        C("base", x0, z0, x1, z1, y, y + 0.86, BLANCO); C("base", x0 - 0.02, z0 - 0.02, x1 + 0.02, z1 + 0.02, y + 0.86, y + 0.9, OSCURO)
    elif tipo == "nevera": C("base", x0, z0, x1, z1, y, y + 1.85, (200, 202, 204))
    elif tipo == "mesa":
        C("base", x0, z0, x1, z1, y + 0.72, y + 0.76, MADERA)
        for px, pz in ((x0 + 0.05, z0 + 0.05), (x1 - 0.1, z0 + 0.05), (x0 + 0.05, z1 - 0.1), (x1 - 0.1, z1 - 0.1)):
            C("base", px, pz, px + 0.05, pz + 0.05, y, y + 0.72, MADERA)
        # sillas a los lados largos
        lx, lz = x1 - x0, z1 - z0
        if lx >= lz:
            n = max(1, int(lx // 0.65))
            for i in range(n):
                cx = x0 + lx * (i + 0.5) / n
                for zz in (z0 - 0.5, z1 + 0.05): C("base", cx - 0.2, zz, cx + 0.2, zz + 0.45, y, y + 0.45, TELA)
        else:
            n = max(1, int(lz // 0.65))
            for i in range(n):
                cz = z0 + lz * (i + 0.5) / n
                for xx in (x0 - 0.5, x1 + 0.05): C("base", xx, cz - 0.2, xx + 0.45, cz + 0.2, y, y + 0.45, TELA)
    elif tipo == "sofa":
        C("base", x0, z0, x1, z1, y, y + 0.42, TELA)
        if rot == "N": C("base", x0, z0, x1, z0 + 0.22, y, y + 0.8, TELA)
        if rot == "S": C("base", x0, z1 - 0.22, x1, z1, y, y + 0.8, TELA)
        if rot == "W": C("base", x0, z0, x0 + 0.22, z1, y, y + 0.8, TELA)
        if rot == "E": C("base", x1 - 0.22, z0, x1, z1, y, y + 0.8, TELA)
    elif tipo == "mesa_centro": C("base", x0, z0, x1, z1, y + 0.3, y + 0.38, MADERA); C("base", x0 + 0.1, z0 + 0.1, x1 - 0.1, z1 - 0.1, y, y + 0.3, OSCURO)
    elif tipo == "tapete": C("base", x0, z0, x1, z1, y, y + 0.012, (205, 196, 176))
    elif tipo == "asoleadora": C("base", x0, z0, x1, z1, y, y + 0.32, MADERA); C("base", x0 + 0.05, z0 + 0.05, x1 - 0.05, z1 - 0.05, y + 0.32, y + 0.38, BLANCO)
    elif tipo == "lavadora": C("base", x0, z0, x1, z1, y, y + 0.85, BLANCO)
    elif tipo == "bano":
        # sanitario, lavamanos y ducha con vidrio, según el lado largo
        lx, lz = x1 - x0, z1 - z0
        if lx >= lz:
            M.caja("base", x0 + 0.1, z0 + 0.1, x0 + 0.9, z1 - 0.1, y, y + 0.03, PIEDRA)
            M.caja("vid", x0 + 0.95, z0 + 0.1, x0 + 0.97, z1 - 0.1, y, y + 2.0, VIDRIO)
            C("base", x0 + 1.15, z1 - 0.65, x0 + 1.55, z1 - 0.05, y, y + 0.42, BLANCO)
            C("base", x1 - 0.75, z1 - 0.5, x1 - 0.1, z1 - 0.05, y, y + 0.85, BLANCO)
        else:
            M.caja("base", x0 + 0.1, z0 + 0.1, x1 - 0.1, z0 + 0.9, y, y + 0.03, PIEDRA)
            M.caja("vid", x0 + 0.1, z0 + 0.95, x1 - 0.1, z0 + 0.97, y, y + 2.0, VIDRIO)
            C("base", x1 - 0.65, z0 + 1.15, x1 - 0.05, z0 + 1.55, y, y + 0.42, BLANCO)
            C("base", x1 - 0.5, z1 - 0.75, x1 - 0.05, z1 - 0.1, y, y + 0.85, BLANCO)
    elif tipo == "arbol":
        cx, cz, s = x0, z0, x1
        C("base", cx - 0.07, cz - 0.07, cx + 0.07, cz + 0.07, y, y + 1.4 * s, (110, 88, 62))
        M.cilindro("base", cx, cz, 0.75 * s, y + 1.2 * s, y + 2.6 * s, VERDE, 8)
    elif tipo == "arbusto":
        M.cilindro("base", x0, z0, x1, y, y + 0.6, (128, 148, 98), 7)


# ------------------------------------------------------------------ casa completa
def construir(D):
    M = Malla()
    alto = {b[0]: b[5] for b in D["bloques"]}
    for b in D["bloques"]:
        _, x0, z0, x1, z1, H = b
        M.caja("base", x0, z0, x1, z1, -0.25, 0, BORDE, top=PISO)
        M.caja("cub", x0, z0, x1, z1, H, H + 0.18, BTC)
    for g in D.get("vidrio", []):
        x0, z0, x1, z1, H = g
        M.caja("base", x0, z0, x1, z1, -0.25, 0, BORDE, top=PISO)
        M.caja("vid", x0, z0, x1, z1, H, H + 0.03, VIDRIO)
        for zz in np.arange(z0 + 0.15, z1, 0.9):
            M.caja("cub", x0 - 0.05, zz, x1 + 0.05, zz + 0.1, H + 0.03, H + 0.2, MADERA)
    for r, bid, ops in D["muros_ext"]:
        muro(M, r, alto.get(bid, D["alto_vidrio"]), ops, True)
    for r, bid, ops in D.get("muros_int", []):
        muro(M, r, alto[bid], ops, False)
    for t in D.get("terrazas", []):
        x0, z0, x1, z1, y, tipo = t
        if tipo == "patio": M.caja("base", x0, z0, x1, z1, y - 0.25, y - 0.02, BORDE, top=PIEDRA)
        else: M.caja("base", x0, z0, x1, z1, y - 0.2, y + 0.02, DECK)
    for e in D.get("escaleras", []):
        x0, z0, x1, z1, ya, yb = e      # baja en +z de ya a yb
        n = int(round((ya - yb) / 0.18)); run = (z1 - z0) / n
        for i in range(n):
            za = z0 + i * run; tp = ya - (i + 1) * (ya - yb) / n
            M.caja("base", x0, za, x1, za + run + 0.02, tp - 0.06, tp, DECK)
        for xx in (x0, x1 - 0.06):   # zancas
            for i in range(n):
                za = z0 + i * run; tp = ya - (i + 1) * (ya - yb) / n
                M.caja("base", xx, za, xx + 0.06, za + run, tp - 0.3, tp - 0.06, MADERA)
    for f in D.get("muebles", []):
        mueble(M, f[0], f[1], f[2] if len(f) > 2 else 0.0)
    return M.arrays()
