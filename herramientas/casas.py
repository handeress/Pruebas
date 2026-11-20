"""Arma los modelos 3D de las dos opciones del portal (casas/A.json y casas/B.json)
y la implantación en el lote 10 (respetando el retiro a los linderos 14-13 y 14-17).

  A · En L: malla del 3D "Casa Suesca · 3D" (fuentes/casa_L_geo.json, pasillo de vidrio 2.00).
  B · Patio interno: se levanta aquí desde la variación A del chat "Variaciones de casa con patio".

Marco local de cada casa: x a lo ancho, z hacia el frente (la vista), y hacia arriba;
piso terminado a y = P. Correr:  python3 herramientas/casas.py
"""
import json, base64, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
P = 0.40          # piso sobre el punto más alto del terreno bajo la casa
RETIRO = {"13": 10.0, "17": 20.0}   # m a cada lindero desde la esquina 14, al borde de cubierta o terraza


def b64(a, t):
    return base64.b64encode(np.ascontiguousarray(a, dtype=t).tobytes()).decode()


def normales(T):
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= (np.linalg.norm(n, axis=1)[:, None] + 1e-12)
    return np.repeat(n, 3, axis=0)


def grupo(T, C):
    T = np.asarray(T, np.float32).reshape(-1, 3, 3)
    C = np.asarray(C, np.uint8).reshape(-1, 3)
    if C.shape[0] == T.shape[0]:
        C = np.repeat(C, 3, axis=0)
    return dict(p=b64(T.reshape(-1, 3), np.float32), n=b64(normales(T), np.float32), c=b64(C, np.uint8), cnt=int(T.shape[0] * 3))


class Malla:
    def __init__(s):
        s.g = {"base": ([], []), "cub": ([], []), "vid": ([], [])}

    def tri(s, g, a, b, c, col):
        s.g[g][0].append([a, b, c]); s.g[g][1].append(col)

    def quad(s, g, a, b, c, d, col):
        s.tri(g, a, b, c, col); s.tri(g, a, c, d, col)

    def caja(s, g, x0, z0, x1, z1, y0, y1, col, top=None, ytop=None):
        """Caja en planta (x, z). ytop(x, z) permite tapa inclinada."""
        f = ytop or (lambda x, z: y1)
        P_ = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
        b = [(x, y0, z) for x, z in P_]
        t = [(x, f(x, z), z) for x, z in P_]
        s.quad(g, b[0], b[3], b[2], b[1], col)
        s.quad(g, t[0], t[1], t[2], t[3], top or col)
        for i in range(4):
            j = (i + 1) % 4
            s.quad(g, b[i], b[j], t[j], t[i], col)


# ---------------------------------------------------------------- A · en L
from modelo import construir

L_MUROS_INT = [(4.12, 0.92, 4.24, 2.80), (4.12, 3.50, 4.24, 3.72),
               (4.24, 0.92, 6.86, 1.04), (7.66, 0.92, 11.63, 1.04), (12.03, 0.92, 12.25, 1.04), (12.95, 0.92, 13.10, 1.04),
               (6.64, 1.04, 6.76, 3.72), (11.46, 1.04, 11.58, 3.72), (12.98, 1.04, 13.10, 3.72),
               (4.24, 2.24, 4.34, 2.36), (5.04, 2.24, 6.64, 2.36), (12.08, 1.04, 12.20, 1.76), (11.58, 1.64, 12.20, 1.76),
               (14.10, 0.12, 14.22, 2.40), (15.92, 0.12, 16.04, 1.64), (15.92, 2.34, 16.04, 2.86),
               (16.04, 1.32, 19.84, 1.44), (17.64, 1.44, 17.76, 2.86), (16.04, 2.74, 17.76, 2.86)]
DISENO_A = dict(
    bloques=[("P", 0, 0, 19.96, 3.84, 3.0), ("S", 14.10, 5.84, 19.96, 14.18, 3.5)],
    vidrio=[(14.10, 3.84, 16.04, 5.84, 2.7)], alto_vidrio=2.7,
    muros_ext=[
        ((0, 0, 19.96, 0.12), "P", [(0.6, 3.6, "A"), (4.5, 6.4, "A"), (7.0, 11.2, "A"), (11.8, 12.8, "A"), (14.57, 15.57, "D"), (16.4, 19.4, "A")]),
        ((0, 3.72, 19.96, 3.84), "P", [(0.5, 3.7, "PT"), (4.5, 6.3, "A"), (7.1, 11.1, "PT"), (11.8, 12.8, "A"), (13.2, 14.0, "PT"), (14.22, 15.92, "O"), (18.1, 19.5, "V")]),
        ((0, 0.12, 0.12, 3.72), "P", [(0.9, 2.9, "V")]),
        ((19.84, 0.12, 19.96, 3.72), "P", [(0.3, 1.2, "A"), (2.0, 3.4, "A")]),
        ((14.10, 5.84, 19.96, 5.96), "S", [(14.22, 15.92, "O"), (16.4, 19.6, "K")]),
        ((14.10, 14.06, 19.96, 14.18), "S", [(14.4, 19.66, "PT")]),
        ((14.10, 5.96, 14.22, 14.06), "S", [(7.6, 10.3, "PT"), (11.0, 13.8, "PT")]),
        ((19.84, 5.96, 19.96, 14.06), "S", [(7.0, 8.8, "V"), (10.6, 13.8, "PT")]),
        ((14.10, 3.84, 14.22, 5.84), "G", [(3.84, 5.84, "G")]),
        ((15.92, 3.84, 16.04, 5.84), "G", [(3.84, 5.84, "G")]),
    ],
    muros_int=[(r, "S" if r[1] > 5 else "P", []) for r in L_MUROS_INT],
    terrazas=[(10.1, 7.46, 14.1, 10.46, 0.0, "deck"), (10.96, 14.18, 19.96, 17.18, -2.5, "deck")],
    escaleras=[(10.96, 10.46, 11.96, 14.18, 0.0, -2.5)],
    muebles=[
        ("cama", (0.12, 1.12, 2.12, 2.72, "W")), ("mesa_noche", (0.12, 0.6, 0.57, 1.05)), ("mesa_noche", (0.12, 2.79, 0.57, 3.24)),
        ("closet", (4.4, 2.42, 6.5, 2.98)), ("bano", (4.24, 1.04, 6.64, 2.24)),
        ("cama", (7.4, 1.04, 8.3, 2.94, "N")), ("cama", (9.6, 1.04, 10.5, 2.94, "N")), ("mesa_noche", (8.7, 1.08, 9.2, 1.5)), ("closet", (10.9, 1.1, 11.44, 3.0)),
        ("bano", (11.58, 1.76, 12.98, 3.72)), ("estante", (16.1, 0.14, 19.8, 0.55)), ("bano", (16.04, 1.44, 17.64, 2.74)),
        ("lavadora", (18.0, 1.5, 18.65, 2.1)), ("lavadora", (18.7, 1.5, 19.35, 2.1)), ("meson", (19.2, 2.3, 19.82, 3.6)),
        ("meson", (16.2, 5.97, 19.82, 6.57)), ("nevera", (19.12, 6.62, 19.82, 7.32)), ("meson", (16.3, 7.6, 18.5, 8.4)),
        ("mesa", (15.9, 9.4, 17.9, 10.3)), ("tapete", (14.9, 11.0, 18.9, 13.6)), ("sofa", (15.0, 11.2, 17.6, 12.1, "N")),
        ("mesa_centro", (15.6, 12.5, 17.0, 13.2)), ("sofa", (18.3, 11.6, 19.2, 12.6, "E")),
        ("asoleadora", (10.5, 8.2, 11.2, 10.1)), ("asoleadora", (11.6, 8.2, 12.3, 10.1)),
        ("meson", (15.0, 14.3, 19.5, 14.9), -2.5), ("mesa", (15.6, 15.8, 17.8, 16.7), -2.5),
    ],
)


def casa_L():
    out = construir(DISENO_A)
    out = {k: [v] for k, v in out.items()}
    apoyos = [(0, 0, 19.96, 3.84, 0.0), (14.10, 3.84, 16.04, 5.84, 0.0), (14.10, 5.84, 19.96, 14.18, 0.0),
              (10.1, 7.46, 14.1, 10.46, 0.0), (10.96, 14.18, 19.96, 17.18, -2.5)]
    out["plataforma"] = [(-0.5, -0.6, 20.5, 8.96)]      # alcobas y mitad de la terraza 15 a nivel
    out["zref"] = 1.92
    out["pads"] = [(10.96, 14.18, 19.96, 17.18, -2.5)]
    out["escal"] = [DISENO_A["escaleras"][0]]
    return out, apoyos


# ---------------------------------------------------------------- B · patio interno
B_DATOS = dict(
    blocks=[("W", 0, 2.60, 3.84, 15.70, "W"), ("N", 3.84, 2.60, 9.00, 3.84, "N"),
            ("NE", 9.00, 0, 14.86, 3.84, "N"), ("S", 5.84, 9.76, 14.18, 15.70, "N")],
    glass=[(9.00, 3.84, 10.94, 9.76)],
    walls=[
        ((0, 2.60, 0.12, 15.70), "W", [(3.0, 3.8, "A"), (5.5, 7.6, "V"), (9.3, 10.0, "A"), (12.4, 14.6, "V")]),
        ((0, 2.60, 3.84, 2.72), "W", []),
        ((0, 15.58, 3.84, 15.70), "W", [(0.4, 3.4, "PT")]),
        ((3.72, 2.72, 3.84, 15.58), "W", [(2.72, 3.72, "O"), (3.90, 9.70, "PT"), (11.9, 15.3, "PT")]),
        ((2.80, 2.72, 2.92, 11.46), "W", [(3.2, 3.95, "D"), (4.6, 5.45, "D")]),
        ((0.12, 4.12, 2.80, 4.24), "W", []),
        ((0.12, 8.94, 2.80, 9.06), "W", []),
        ((0.12, 10.18, 2.80, 10.30), "W", [(1.9, 2.6, "D")]),
        ((0.12, 11.46, 3.72, 11.58), "W", [(1.6, 2.4, "D"), (2.92, 3.72, "D")]),
        ((3.84, 2.60, 9.00, 2.72), "N", [(4.5, 8.5, "A")]),
        ((3.84, 3.72, 9.00, 3.84), "N", [(3.9, 8.95, "PT")]),
        ((9.00, 0, 14.86, 0.12), "NE", [(9.35, 10.35, "D"), (12.9, 14.2, "A")]),
        ((9.00, 0.12, 9.12, 3.72), "NE", [(2.72, 3.72, "O")]),
        ((14.74, 0.12, 14.86, 3.72), "NE", [(2.0, 3.2, "V")]),
        ((9.00, 3.72, 14.86, 3.84), "NE", [(9.12, 10.82, "O"), (12.9, 14.4, "V")]),
        ((10.82, 0.12, 10.94, 3.72), "NE", [(0.3, 1.1, "D"), (2.0, 2.75, "D")]),
        ((10.94, 1.32, 14.74, 1.44), "NE", [(12.7, 13.45, "D")]),
        ((12.34, 1.44, 12.46, 3.72), "NE", []),
        ((9.00, 3.84, 9.12, 9.76), "G", [(3.84, 9.76, "G")]),
        ((10.82, 3.84, 10.94, 9.76), "G", [(3.84, 9.76, "G")]),
        ((5.84, 9.76, 14.18, 9.88), "S", [(6.2, 8.9, "PT"), (9.12, 10.82, "O"), (11.6, 13.8, "K")]),
        ((5.84, 15.58, 14.18, 15.70), "S", [(6.1, 13.9, "PT")]),
        ((5.84, 9.88, 5.96, 15.58), "S", [(10.4, 15.2, "PT")]),
        ((14.06, 9.88, 14.18, 15.58), "S", [(10.0, 10.9, "D"), (12.0, 14.6, "V")]),
    ],
    patio=(3.84, 3.84, 9.00, 9.76), deck=(4.96, 6.76, 8.96, 9.76), bbq=(6.38, 15.70, 15.38, 18.70),
    stairs=(14.18, 9.88, 15.38, 15.70, 1.0),
)
INTERIORES_B = {"W": [4, 5, 6, 7, 8], "NE": [15, 16, 17]}   # índices de muros interiores en B_DATOS["walls"]


def casa_patio():
    D = B_DATOS; alto = {"W": 3.0, "N": 3.0, "NE": 3.0, "S": 3.4}
    ints = {i for v in INTERIORES_B.values() for i in v}
    sx0, sz0, sx1, sz1, ld = D["stairs"]
    d = dict(
        bloques=[(b[0], b[1], b[2], b[3], b[4], alto[b[0]]) for b in D["blocks"]],
        vidrio=[tuple(D["glass"][0]) + (2.7,)], alto_vidrio=2.7,
        muros_ext=[w for i, w in enumerate(D["walls"]) if i not in ints],
        muros_int=[w for i, w in enumerate(D["walls"]) if i in ints],
        terrazas=[tuple(D["patio"]) + (0.0, "patio"), tuple(D["deck"]) + (0.02, "deck"), tuple(D["bbq"]) + (-2.5, "deck"),
                  (sx0, sz0, sx1, sz0 + ld, 0.0, "deck")],
        escaleras=[(sx0, sz0 + ld, sx1, sz1, 0.0, -2.5)],
        muebles=[
            ("closet", (0.12, 4.3, 1.9, 4.85)), ("cama", (0.12, 5.2, 2.02, 6.1, "W")), ("cama", (0.12, 7.4, 2.02, 8.3, "W")), ("mesa_noche", (0.12, 6.5, 0.55, 6.95)),
            ("bano", (0.12, 2.72, 2.80, 4.12)), ("bano", (0.12, 9.06, 2.80, 10.18)), ("closet", (0.12, 10.35, 0.72, 11.42)),
            ("cama", (0.12, 12.8, 2.12, 14.4, "W")), ("mesa_noche", (0.12, 12.25, 0.55, 12.7)), ("mesa_noche", (0.12, 14.5, 0.55, 14.95)),
            ("estante", (11.9, 0.14, 14.7, 0.55)), ("bano", (10.94, 1.44, 12.34, 3.72)),
            ("lavadora", (12.6, 3.0, 13.25, 3.65)), ("lavadora", (13.3, 3.0, 13.95, 3.65)), ("meson", (14.1, 1.5, 14.72, 2.9)),
            ("meson", (11.0, 9.89, 14.05, 10.49)), ("nevera", (10.3, 9.95, 10.95, 10.6)), ("meson", (11.4, 11.3, 13.2, 12.1)),
            ("mesa", (11.4, 13.3, 13.2, 14.2)), ("tapete", (6.4, 11.0, 9.4, 13.8)),
            ("sofa", (6.3, 11.2, 7.1, 13.4, "W")), ("sofa", (8.6, 11.2, 9.4, 13.4, "E")), ("mesa_centro", (7.4, 11.7, 8.3, 12.9)),
            ("asoleadora", (5.4, 7.2, 6.1, 9.1)), ("asoleadora", (6.5, 7.2, 7.2, 9.1)),
            ("meson", (6.6, 16.0, 7.2, 18.4), -2.5), ("mesa", (10.0, 16.6, 12.0, 17.6), -2.5),
        ])
    out = {k: [v] for k, v in construir(d).items()}
    out["plataforma"] = [(0.0, 3.0, 3.84, 15.70), (0.0, 0.0, 14.86, 8.26)]   # ala de alcobas y mitad de la terraza
    out["zref"] = 9.0
    out["pads"] = [tuple(D["bbq"]) + (-2.5,)]
    out["escal"] = d["escaleras"]
    apoyos = [(b[1], b[2], b[3], b[4], 0.0) for b in D["blocks"]] + [tuple(D["glass"][0]) + (0.0,), tuple(D["patio"]) + (0.0,), tuple(D["bbq"]) + (-2.5,)]
    return out, apoyos


# ---------------------------------------------------------------- implantación
def implantar(grupos, apoyos, sitio):
    """Lleva la casa al marco local (x, z >= 0, piso en y = P) y calcula el origen en el lote."""
    plat = grupos.pop("plataforma"); zref = grupos.pop("zref"); pads = grupos.pop("pads"); escal = grupos.pop("escal")
    todos = np.concatenate([T.reshape(-1, 3) for g in grupos.values() for T, C in g])
    mn = todos.min(0); mx = todos.max(0)
    sh = np.array([-mn[0], P, -mn[2]], np.float32)
    res = {}
    for k, lst in grupos.items():
        TT = np.concatenate([T.reshape(-1, 3, 3) for T, C in lst]) + sh
        CC = np.concatenate([np.asarray(C, np.uint8).reshape(-1, 3) for T, C in lst])   # un color por triángulo
        res[k] = grupo(TT, CC)
    ap = [[round(float(a[0] + sh[0]), 3), round(float(a[1] + sh[2]), 3), round(float(a[2] + sh[0]), 3), round(float(a[3] + sh[2]), 3), round(float(a[4] + P), 3)] for a in apoyos]
    Lw, Fd = float(mx[0] - mn[0]), float(mx[2] - mn[2])
    # huella en planta (todos los vértices) -> retiro a linderos 14-13 y 14-17
    xz = todos[:, [0, 2]] + sh[[0, 2]]
    V = {n: np.array([x, y]) for n, x, y in sitio["vertices"]}
    d = np.array(sitio["sitio"]["frente"]); d /= np.linalg.norm(d); ex = np.array([-d[1], d[0]])
    R = np.stack([ex, d], 1)                    # local (x, z) -> plano
    filas, b = [], []
    for otro in ("13", "17"):
        u = V[otro] - V["14"]; u /= np.linalg.norm(u)
        n = np.array([-u[1], u[0]])
        cen = np.mean([V[k] for k in V], 0)
        if n @ (cen - V["14"]) < 0: n = -n
        filas.append(n); b.append(RETIRO[otro] + n @ V["14"] - (xz @ R.T @ n).min())
    O = np.linalg.solve(np.array(filas), np.array(b))
    huella = xz @ R.T + O
    dist = {o: float(min((huella - V["14"]) @ f)) for o, f in zip(("13", "17"), filas)}
    return dict(L=round(Lw, 3), fondo=round(Fd, 3), P=P, grupos=res, apoyos=ap,
                origen=[round(float(O[0]), 3), round(float(O[1]), 3)], frente=[round(float(d[0]), 4), round(float(d[1]), 4)],
                retiros=dist, plataforma=[[round(float(r[0] + sh[0]), 2), round(float(r[1] + sh[2]), 2), round(float(r[2] + sh[0]), 2), round(float(r[3] + sh[2]), 2)] for r in plat],
                zref=round(float(zref + sh[2]), 2),
                pads=[[round(float(r[0] + sh[0]), 2), round(float(r[1] + sh[2]), 2), round(float(r[2] + sh[0]), 2), round(float(r[3] + sh[2]), 2), round(float(r[4] + P), 2)] for r in pads],
                escal=[[round(float(e[0] + sh[0]), 2), round(float(e[1] + sh[2]), 2), round(float(e[2] + sh[0]), 2), round(float(e[3] + sh[2]), 2), round(float(e[4] + P), 2), round(float(e[5] + P), 2)] for e in escal]), sh


VISTA_PLANO = (-153.0, 382.0)   # dirección de la vista principal marcada por Andrés en el plano del lote (px, 14 arriba a la izq.)
BARRA_PLANO = (265.0, 93.0)     # línea azul con la que se alinea la barra de alcobas (px, mismo plano)
ACCESO = (16.0, 7.0)            # zona de acceso en la esquina 14: m a lo largo de 14-13 y de 14-17
ENTRADA = (3.5, 6.5)            # tramo del lindero 14-17 (m desde 14) por donde se entra desde la vía peatonal


def frente_y_acceso(sitio):
    V = {n: np.array([x, y]) for n, x, y in sitio["vertices"]}
    img = {"14": (118, 312), "13": (604, 234), "17": (282, 872), "18": (764, 795)}
    A = np.array([np.r_[V[n], 1] for n in img]); B = np.array([img[n] for n in img], float)
    M = np.linalg.lstsq(A, B, rcond=None)[0][:2].T; U, _, Vt = np.linalg.svd(M); Q = U @ Vt
    v = np.array(VISTA_PLANO); v /= np.linalg.norm(v)
    e = np.array(BARRA_PLANO); e /= np.linalg.norm(e); ds = np.array([-e[1], e[0]])
    if ds @ v < 0: ds = -ds                                  # frente perpendicular a la barra, hacia la vista
    d = ds @ Q
    sitio["sitio"]["frente"] = [round(float(d[0]), 4), round(float(d[1]), 4)]
    u13 = (V["13"] - V["14"]) / np.linalg.norm(V["13"] - V["14"]); u17 = (V["17"] - V["14"]) / np.linalg.norm(V["17"] - V["14"])
    a, b = ACCESO
    sitio["acceso"] = [[round(float(q[0]), 2), round(float(q[1]), 2)] for q in (V["14"], V["14"] + a * u13, V["14"] + a * u13 + b * u17, V["14"] + b * u17)]
    # entrada: del lindero 14-17 hacia afuera hasta el eje de la vía peatonal
    n = np.array([-u17[1], u17[0]])
    if n @ (V["13"] - V["14"]) > 0: n = -n            # hacia afuera del lote
    pe = np.array(sitio["peatonal"])[:, :2]
    def hasta_via(p0):
        for t in np.arange(0, 25, 0.1):
            q = p0 + t * n
            if np.min(np.linalg.norm(pe - q, axis=1)) < 0.3: return q + 0.75 * n
        return p0 + 5 * n
    e0, e1 = V["14"] + ENTRADA[0] * u17, V["14"] + ENTRADA[1] * u17
    sitio["entrada"] = [[round(float(q[0]), 2), round(float(q[1]), 2)] for q in (e0, e1, hasta_via(e1), hasta_via(e0))]
    json.dump(sitio, open(os.path.join(RAIZ, "terreno", "sitio.json"), "w"), separators=(",", ":"))


if __name__ == "__main__":
    sitio = json.load(open(os.path.join(RAIZ, "terreno", "sitio.json")))
    frente_y_acceso(sitio)
    os.makedirs(os.path.join(RAIZ, "casas"), exist_ok=True)
    for k, fn in (("A", casa_L), ("B", casa_patio)):
        g, ap = fn()
        o, sh = implantar(g, ap, sitio)
        o["corrimiento"] = [float(sh[0]), float(sh[2])]
        json.dump(o, open(os.path.join(RAIZ, "casas", k + ".json"), "w"), separators=(",", ":"))
        print(k, "L", o["L"], "fondo", o["fondo"], "origen", o["origen"], "retiros", {a: round(v, 2) for a, v in o["retiros"].items()},
              "tri", {a: v["cnt"] // 3 for a, v in o["grupos"].items()}, "kB", os.path.getsize(os.path.join(RAIZ, "casas", k + ".json")) // 1024)


# ================================================================ plantas (SVG) y plano del lote
# Coordenadas de planta de cada diseño (como en sus planos): x a lo ancho, y hacia el frente.
L_MUROS_INT = [(4.12, 0.92, 4.24, 2.80), (4.12, 3.50, 4.24, 3.72),
               (4.24, 0.92, 6.86, 1.04), (7.66, 0.92, 11.63, 1.04), (12.03, 0.92, 12.25, 1.04), (12.95, 0.92, 13.10, 1.04),
               (6.64, 1.04, 6.76, 3.72), (11.46, 1.04, 11.58, 3.72), (12.98, 1.04, 13.10, 3.72),
               (4.24, 2.24, 4.34, 2.36), (5.04, 2.24, 6.64, 2.36), (12.08, 1.04, 12.20, 1.76), (11.58, 1.64, 12.20, 1.76),
               (14.10, 0.12, 14.22, 2.40), (15.92, 0.12, 16.04, 1.64), (15.92, 2.34, 16.04, 2.86),
               (16.04, 1.32, 19.84, 1.44), (17.64, 1.44, 17.76, 2.86), (16.04, 2.74, 17.76, 2.86)]
L_MUROS_EXT = [(0, 0, 19.96, 0.12), (0, 3.72, 14.22, 3.84), (15.92, 3.72, 19.96, 3.84), (0, 0.12, 0.12, 3.72), (19.84, 0.12, 19.96, 3.72),
               (14.10, 5.84, 14.22, 5.96), (15.92, 5.84, 19.96, 5.96), (14.10, 14.06, 19.96, 14.18), (14.10, 5.96, 14.22, 14.06), (19.84, 5.96, 19.96, 14.06)]
L_PLAN = (0.0, 0.0)         # la malla ya está en coordenadas de planta


def tri_planta(grupo_b64, sh, pl):
    T = np.frombuffer(base64.b64decode(grupo_b64["p"]), np.float32).reshape(-1, 3, 3)
    C = np.frombuffer(base64.b64decode(grupo_b64["c"]), np.uint8).reshape(-1, 3, 3)[:, 0]
    T = T.copy(); T[:, :, 0] -= sh[0] + pl[0]; T[:, :, 2] -= sh[1] + pl[1]; T[:, :, 1] -= P
    return T, C


def svg_planta(o, k):
    sh = o["corrimiento"]; pl = L_PLAN if k == "A" else (0.0, 0.0)
    S = 100.0; out = []
    Tb, Cb = tri_planta(o["grupos"]["base"], sh, pl)
    n = np.cross(Tb[:, 1] - Tb[:, 0], Tb[:, 2] - Tb[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
    hz = (np.abs(n[:, 1]) > 0.95) & (Tb[:, :, 1].max(1) < 0.07)
    idx = np.where(hz)[0]; idx = idx[np.argsort(Tb[idx, :, 1].mean(1))]
    xs, ys = [], []
    def col(c):
        c = tuple(int(v) for v in c)
        if c in ((142, 104, 71), (168, 119, 76), (119, 81, 51)): return "#EADBC0"
        if c in ((200, 198, 190),): return "#E6E4DC"
        if c in ((90, 90, 90), (51, 51, 51), (43, 43, 43)): return "#8E8F86"
        return "#FFFFFF"
    for i in idx:
        t = Tb[i]
        if t[:, 1].max() > 0.07: continue
        pts = " ".join(f"{t[j,0]*S:.0f},{t[j,2]*S:.0f}" for j in range(3))
        f = col(Cb[i])
        out.append(f'<polygon points="{pts}" fill="{f}" stroke="{f}" stroke-width="2"/>')
        xs += list(t[:, 0]); ys += list(t[:, 2])
    # muros y vanos
    def rect(r, f):
        return f'<rect x="{r[0]*S:.0f}" y="{r[1]*S:.0f}" width="{(r[2]-r[0])*S:.0f}" height="{(r[3]-r[1])*S:.0f}" fill="{f}"/>'
    if k == "A":   # en la malla de la L los pisos interiores tienen el color del deck: se tapan en blanco
        for r in [(0.12, 0.12, 19.84, 3.72), (14.10, 3.72, 16.04, 5.96), (14.22, 5.96, 19.84, 14.06)]:
            out.append(rect(r, "#FFFFFF"))
    vanos = []
    if k == "A":
        for r in L_MUROS_EXT + L_MUROS_INT: out.append(rect(r, "#595959"))
        Tv, _ = tri_planta(o["grupos"]["vid"], sh, pl)
        for t in Tv:
            if np.ptp(t[:, 1]) < 0.3: continue
            x0, x1, z0, z1 = t[:, 0].min(), t[:, 0].max(), t[:, 2].min(), t[:, 2].max()
            if x1 - x0 > z1 - z0 and x1 - x0 > 0.3: vanos.append((x0, (z0 + z1) / 2, x1, (z0 + z1) / 2))
            elif z1 - z0 > 0.3: vanos.append(((x0 + x1) / 2, z0, (x0 + x1) / 2, z1))
    else:
        for r, bid, ops in B_DATOS["walls"]:
            x0, z0, x1, z1 = r; h = (x1 - x0) >= (z1 - z0); a0, a1 = (x0, x1) if h else (z0, z1); cur = a0
            tr = []
            for op in sorted(ops):
                if op[0] > cur: tr.append(("S", cur, op[0]))
                tr.append((op[2], op[0], op[1])); cur = op[1]
            if cur < a1: tr.append(("S", cur, a1))
            for kk, s0, s1 in tr:
                rr = (s0, z0, s1, z1) if h else (x0, s0, x1, s1)
                if kk == "S": out.append(rect(rr, "#595959"))
                elif kk in ("PT", "V", "A", "G"):
                    vanos.append((rr[0], (rr[1] + rr[3]) / 2, rr[2], (rr[1] + rr[3]) / 2) if h else ((rr[0] + rr[2]) / 2, rr[1], (rr[0] + rr[2]) / 2, rr[3]))
    # une los tramos de vidrio contiguos de un mismo paño
    vs = sorted(set((round(a, 2), round(b, 2), round(c, 2), round(d, 2)) for a, b, c, d in vanos))
    for a, b, c, d in vs:
        out.append(f'<path d="M{a*S:.0f} {b*S:.0f}L{c*S:.0f} {d*S:.0f}" stroke="#ABAC8A" stroke-width="5"/>')
    xs = np.array(xs); ys = np.array(ys)
    bx = [float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())]
    return dict(svg="".join(out), caja=[round(v, 2) for v in bx])


def similitud(sitio):
    """Plano del lote orientado como el plano de la parcelación (14 arriba a la izquierda)."""
    V = {n: np.array([x, y]) for n, x, y in sitio["vertices"]}
    img = {"14": (118, 312), "13": (604, 234), "17": (282, 872), "18": (764, 795)}   # px del plano enviado
    A = np.array([np.r_[V[n], 1] for n in img]); B = np.array([img[n] for n in img], float)
    X = np.linalg.lstsq(A, B, rcond=None)[0]; M = X[:2].T
    U, s, Vt = np.linalg.svd(M); Q = U @ Vt               # rotación (+ espejo por el eje y de la imagen)
    return lambda p: (np.asarray(p) - V["14"]) @ Q.T


def svg_lote(sitio, oA, detalle=False):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    f = similitud(sitio); g = sitio["grilla"]
    V = {n: np.array([x, y]) for n, x, y in sitio["vertices"]}
    lote = np.array([[p[0], p[1]] for p in sitio["lote"]])
    Lq = f(lote); xs, ys = Lq[:, 0], Lq[:, 1]
    mg = 14; x0, y0, x1, y1 = xs.min() - mg, ys.min() - mg, xs.max() + mg, ys.max() + mg
    S = 6.0   # px por metro
    if detalle:   # acercamiento a la esquina 14 con la casa
        d_ = np.array(oA["frente"]); ex_ = np.array([-d_[1], d_[0]]); O_ = np.array(oA["origen"])
        cj = [O_ + a * ex_ + b * d_ for a in (0, oA["L"]) for b in (0, oA["fondo"])] + [V["14"]] + [np.array(q) for q in sitio["entrada"]]
        q = f(np.array(cj)); x0, y0 = q.min(0) - 7; x1, y1 = q.max(0) + 7
        S = 930.0 / (x1 - x0)
    def X(q): return (q[..., 0] - x0) * S
    def Y(q): return (q[..., 1] - y0) * S
    W, H = (x1 - x0) * S, (y1 - y0) * S
    cid = "vDet" if detalle else "vLote"
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{"Detalle de la esquina 14 con los retiros" if detalle else "Plano del lote 10 con la casa en L implantada"}">']
    o.append(f'<defs><clipPath id="{cid}"><rect width="{W:.0f}" height="{H:.0f}"/></clipPath></defs><g clip-path="url(#{cid})">')
    # curvas de nivel cada 2 m
    H_ = np.array([np.nan if v is None else v / 100 for v in g["h"]]).reshape(g["ny"], g["nx"])
    gx = g["x0"] + np.arange(g["nx"]) * g["d"]; gy = g["y0"] - np.arange(g["ny"]) * g["d"]
    GX, GY = np.meshgrid(gx, gy)
    niv = np.arange(np.floor(np.nanmin(H_) / 2) * 2, np.nanmax(H_) + 2, 2)
    cs = plt.contour(GX, GY, H_, levels=niv)
    for lev, segs in zip(cs.levels, cs.allsegs):
        mayor = int(round(lev)) % 10 == 0
        for sg in segs:
            if len(sg) < 2: continue
            q = f(sg); d = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in zip(X(q), Y(q)))
            o.append(f'<path d="{d}" fill="none" stroke="#B9BAA8" stroke-width="{1.4 if mayor else 0.7}"/>')
    plt.close("all")
    # vías
    for nom, an, c in (("vehicular", 5.0, "#D6D6D0"), ("peatonal", 1.5, "#E2E2DC")):
        q = f(np.array(sitio[nom])[:, :2]); d = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in zip(X(q), Y(q)))
        o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{an*S:.0f}" stroke-linejoin="round" stroke-linecap="round"/>')
        o.append(f'<path d="{d}" fill="none" stroke="#9A9A92" stroke-width="0.8" stroke-dasharray="6 5"/>')
    # lindero
    d = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in zip(X(Lq), Y(Lq))) + "Z"
    o.append(f'<path d="{d}" fill="rgba(255,255,255,.35)" stroke="#424D22" stroke-width="2.4" stroke-linejoin="round"/>')
    # zona de acceso y entrada
    for nom in ("entrada", "acceso"):
        q = f(np.array(sitio[nom]))
        o.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in zip(X(q), Y(q)))}" fill="#CFCFC8" stroke="#595959" stroke-width="1.2"/>')
    q = f(np.mean(sitio["acceso"], 0))
    o.append(f'<text x="{X(q):.1f}" y="{Y(q)+5:.1f}" font-size="{18 if detalle else 10}" fill="#424D22" font-weight="500" text-anchor="middle" letter-spacing=".12em">ACCESO</text>')
    # casa en L
    d_ = np.array(oA["frente"]); ex = np.array([-d_[1], d_[0]]); O = np.array(oA["origen"])
    def loc2sit(x, z): return O + np.multiply.outer(x, ex) + np.multiply.outer(z, d_) if np.ndim(x) else O + x * ex + z * d_
    pl2loc = (oA["corrimiento"][0] + L_PLAN[0], oA["corrimiento"][1] + L_PLAN[1])
    def rect_plan(r, fill, st="#595959", sw=1.2, extra=""):
        pts = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
        q = f(np.array([loc2sit(a + pl2loc[0], b + pl2loc[1]) for a, b in pts]))
        return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in zip(X(q), Y(q)))}" fill="{fill}" stroke="{st}" stroke-width="{sw}"{extra}/>'
    # huella completa (cubiertas y terrazas): envolvente punteada
    T = np.concatenate([np.frombuffer(base64.b64decode(gg["p"]), np.float32).reshape(-1, 3) for gg in oA["grupos"].values()])
    pts = O + np.outer(T[:, 0], ex) + np.outer(T[:, 2], d_)
    from scipy.spatial import ConvexHull
    hull = pts[ConvexHull(pts).vertices]; q = f(hull)
    o.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in zip(X(q), Y(q)))}" fill="none" stroke="#595959" stroke-width="1" stroke-dasharray="4 3"/>')
    for r in [(10.1, 7.46, 14.1, 10.46), (10.96, 14.18, 19.96, 17.18)]:
        o.append(rect_plan(r, "#EADBC0", "#A9743E", 1))
    for r in [(0, 0, 19.96, 3.84), (14.10, 5.84, 19.96, 14.18)]:
        o.append(rect_plan(r, "#ABAC8A", "#424D22", 1.4))
    o.append(rect_plan((14.10, 3.84, 16.04, 5.84), "#DCE6EC", "#424D22", 1.2))
    # retiros: desde el punto de la huella más cercano a cada lindero
    for otro in ("13", "17"):
        u = V[otro] - V["14"]; u /= np.linalg.norm(u); n = np.array([-u[1], u[0]])
        if n @ (np.mean(list(V.values()), 0) - V["14"]) < 0: n = -n
        dd = (hull - V["14"]) @ n; i = int(np.argmin(dd)); a = hull[i]; b = a - n * dd[i]
        qa, qb = f(np.array([a, b]))
        o.append(f'<path d="M{X(qa):.1f} {Y(qa):.1f}L{X(qb):.1f} {Y(qb):.1f}" stroke="#C0392B" stroke-width="1.4"/>')
        for qq in (qa, qb): o.append(f'<circle cx="{X(qq):.1f}" cy="{Y(qq):.1f}" r="2.6" fill="#C0392B"/>')
        m = (qa + qb) / 2; ang = math.degrees(math.atan2(qb[1] - qa[1], qb[0] - qa[0]))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        fz = 22 if detalle else 13
        o.append(f'<text x="{X(m):.1f}" y="{Y(m):.1f}" transform="rotate({ang:.1f} {X(m):.1f} {Y(m):.1f})" dy="-6" font-size="{fz}" fill="#C0392B" text-anchor="middle" font-weight="500">{dd[i]:.2f} m</text>')
    # vista
    c = O + oA["L"] / 2 * ex + (oA["fondo"] + 1.0) * d_; c2 = c + (6 if detalle else 22) * d_; qa, qb = f(np.array([c, c2]))
    o.append(f'<path d="M{X(qa):.1f} {Y(qa):.1f}L{X(qb):.1f} {Y(qb):.1f}" stroke="#424D22" stroke-width="2.4" marker-end="url(#fl)"/>')
    o.append(f'<text x="{X(qb)+8:.1f}" y="{Y(qb)+4:.1f}" font-size="{20 if detalle else 13}" fill="#424D22" font-weight="500">vista principal</text>')
    o.append('</g><defs><marker id="fl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#424D22"/></marker></defs>')
    # mojones
    for n_, p in V.items():
        if detalle and n_ != "14": continue
        q = f(p); o.append(f'<circle cx="{X(q):.1f}" cy="{Y(q):.1f}" r="4.5" fill="#fff" stroke="#424D22" stroke-width="2"/>')
        dx = -16 if n_ in ("14", "17") else 10
        o.append(f'<text x="{X(q)+dx:.1f}" y="{Y(q)-8:.1f}" font-size="16" fill="#424D22" font-weight="500">{n_}</text>')
    cq = f(lote.mean(0) + 0.0); 
    q = f(np.mean([V[k] for k in V], 0) + 0.28 * (V["18"] - V["14"]))
    if not detalle: o.append(f'<text x="{X(q):.1f}" y="{Y(q):.1f}" font-size="30" fill="#595959" font-weight="300" text-anchor="middle">LOTE 10</text>')
    else:
        for nom, pos in (("Lindero 14–13", 0.25), ("Lindero 14–17", 0.18)):
            pass
    # escala
    sx, sy = 16, H - 18
    e1, e2, fz = (5, 10, 16) if detalle else (10, 20, 11)
    o.append(f'<path d="M{sx} {sy}h{e2*S:.0f}" stroke="#595959" stroke-width="3"/><path d="M{sx} {sy}h{e1*S:.0f}" stroke="#fff" stroke-width="1.2"/>')
    o.append(f'<text x="{sx}" y="{sy-7}" font-size="{fz}" fill="#595959">0</text><text x="{sx+e1*S:.0f}" y="{sy-7}" font-size="{fz}" fill="#595959" text-anchor="middle">{e1}</text><text x="{sx+e2*S:.0f}" y="{sy-7}" font-size="{fz}" fill="#595959" text-anchor="middle">{e2} m</text>')
    o.append("</svg>")
    return "".join(o)


def plantas_y_lote():
    sitio = json.load(open(os.path.join(RAIZ, "terreno", "sitio.json")))
    for k in "AB":
        p = os.path.join(RAIZ, "casas", k + ".json"); o = json.load(open(p))
        o["planta"] = svg_planta(o, k)
        json.dump(o, open(p, "w"), separators=(",", ":"))
    oA = json.load(open(os.path.join(RAIZ, "casas", "A.json")))
    svg = svg_lote(sitio, oA) + '<p class="lote-det">Detalle de la esquina 14</p>' + svg_lote(sitio, oA, detalle=True)
    h = os.path.join(RAIZ, "index.html"); s = open(h, encoding="utf-8").read()
    a, b = s.index("<!--LOTE-->") + len("<!--LOTE-->"), s.index("<!--/LOTE-->")
    open(h, "w", encoding="utf-8").write(s[:a] + svg + s[b:])
    print("plantas y plano del lote listos")


if __name__ == "__main__":
    plantas_y_lote()
