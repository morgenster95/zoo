"""ZOO: „malovaný“ styl zvířat (test podle vzoru art/reference/animal_style_sample.png).
Rozdíl proti animals.py: siluety z polygonů (přirozené proporce), objem z mapy výšky (vzdálenost od okraje) a osvětlení,
6tónová rampa s posunem odstínu (stíny do červeno-fialova, světla do žluta), textura srsti, tmavý obrys v odstínu zvířete, stín na zemi.
Použití: python painted.py <výstupní složka>"""
import sys, os, math, random, colorsys
import numpy as np
from PIL import Image, ImageDraw

def hx(s):
    s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4))

def make_ramp(base, n=6, warm_hi=True):
    """base = střední tón; vrací n barev od nejtmavší po nejsvětlejší s posunem odstínu"""
    r, g, b = [c / 255 for c in hx(base)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    out = []
    for i in range(n):
        t = (i - 2.4) / 2.6               # -0.9 .. +1.0
        hh = (h + (0.045 * t if t > 0 else 0.055 * t)) % 1.0     # světla do žluta, stíny do červena/fialova
        ss = max(0, min(1, s * (1 + (0.25 if t < 0 else -0.28) * abs(t))))
        vv = max(0.05, min(1, v * (1 + 0.62 * t * (1 if t > 0 else .9))))
        rr, gg, bb = colorsys.hsv_to_rgb(hh, ss, vv)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return out

BAYER = np.array([[0, 2], [3, 1]]) / 4.0

def dt(mask):
    """vzdálenost od okraje uvnitř masky (chamfer 3-4)"""
    h, w = mask.shape
    INF = 10 ** 6
    d = np.where(mask, INF, 0).astype(np.int64)
    for y in range(h):
        for x in range(w):
            if d[y, x]:
                v = d[y, x]
                if y > 0: v = min(v, d[y - 1, x] + 3)
                if x > 0: v = min(v, d[y, x - 1] + 3)
                if y > 0 and x > 0: v = min(v, d[y - 1, x - 1] + 4)
                if y > 0 and x < w - 1: v = min(v, d[y - 1, x + 1] + 4)
                d[y, x] = v if v < INF else (3 if (y == 0 or x == 0 or y == h - 1 or x == w - 1) else v)
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if d[y, x]:
                v = d[y, x]
                if y < h - 1: v = min(v, d[y + 1, x] + 3)
                if x < w - 1: v = min(v, d[y, x + 1] + 3)
                if y < h - 1 and x < w - 1: v = min(v, d[y + 1, x + 1] + 4)
                if y < h - 1 and x > 0: v = min(v, d[y + 1, x - 1] + 4)
                d[y, x] = v
    return d / 3.0

def blur(a, k=1):
    for _ in range(k):
        p = np.pad(a, 1, mode='edge')
        a = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:] + 4 * p[1:-1, 1:-1]) / 8.0
    return a

class Paint:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.lab = np.zeros((h, w), dtype=np.int32)     # id oblasti (0 = nic)
        self.regs = [None]                              # (ramp, fur, bump, edge)
        self.px = {}                                    # detaily přes (x,y)->rgb
        self.rng = np.random.RandomState(seed)
        self.shadow = None
        self.over = []                                  # (maska, barva) vzory přes tělo

    def region(self, pts, base, fur=0.045, bump=0.0, edge=False, ramp=None):
        rid = len(self.regs)
        self.regs.append((ramp or make_ramp(base), fur, bump, edge))
        m = Image.new('L', (self.w, self.h), 0); ImageDraw.Draw(m).polygon([(x, y) for x, y in pts], fill=255)
        a = np.array(m).astype(float) / 255.0
        a = blur(a, 1) > 0.42
        self.lab[a] = rid
        return rid

    def ellipse(self, cx, cy, rx, ry, base, **kw):
        n = 28
        pts = [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
        return self.region(pts, base, **kw)

    def dot(self, x, y, c):
        self.px[(int(x), int(y))] = c if isinstance(c, tuple) else hx(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(x1)): self.dot(x, y, c)

    def pattern(self, fn, color):
        """fn(draw) kreslí do masky; barva jen tam, kde už je tělo"""
        m = Image.new('L', (self.w, self.h), 0); fn(ImageDraw.Draw(m)); self.over.append((np.array(m) > 0, color if isinstance(color, tuple) else hx(color)))

    def render(self, light=(-0.55, -0.62, 0.56), shadow=None, scale=1):
        sil = self.lab > 0
        h, w = self.h, self.w
        h_map = 0.5 * np.minimum(dt(sil), 5) / 5.0
        for rid in range(1, len(self.regs)):
            m = self.lab == rid
            if m.any(): h_map += (0.5 * np.minimum(dt(m), 4) / 4.0 + self.regs[rid][2]) * m
        h_map = blur(h_map * sil, 2)
        gy, gx = np.gradient(h_map)
        k = 2.6
        nx, ny, nz = -gx * k, -gy * k, np.ones_like(h_map)
        nn = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
        L = np.array(light) / np.linalg.norm(light)
        sh = (nx * L[0] + ny * L[1] + nz * L[2]) / nn
        out = np.zeros((h + 2, w + 2, 4), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                rid = self.lab[y, x]
                if not rid: continue
                ramp, fur, bump, edge = self.regs[rid]
                n = len(ramp)
                t = (sh[y, x] - 0.50) / 0.48
                t += (self.rng.rand() - .5) * fur * 2
                t += (BAYER[y % 2, x % 2] - .4) * 0.07
                idx = int(round(max(0, min(1, t)) * (n - 1)))
                out[y + 1, x + 1] = (*ramp[idx], 255)
        for (m, col) in self.over:
            for y in range(h):
                for x in range(w):
                    if m[y, x] and self.lab[y, x]:
                        # vzor se stínuje podle stejné osvětlenosti
                        t = (sh[y, x] - 0.50) / 0.48
                        f = 0.82 + 0.35 * max(0, min(1, t))
                        out[y + 1, x + 1] = (*[min(255, int(c * f)) for c in col], 255)
        for (x, y), c in self.px.items():
            if 0 <= x < w and 0 <= y < h: out[y + 1, x + 1] = (*c, 255)
        # vnitřní obrysy oblastí s edge=True (tam, kde sousedí s jinou oblastí níž)
        for y in range(h):
            for x in range(w):
                rid = self.lab[y, x]
                if rid and self.regs[rid][3] and (x, y) not in self.px:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        X, Y = x + dx, y + dy
                        if 0 <= X < w and 0 <= Y < h and self.lab[Y, X] and self.lab[Y, X] < rid:
                            out[y + 1, x + 1] = (*[int(c * 0.9) for c in self.regs[rid][0][0]], 255); break
        # vnější obrys v odstínu sousední plochy
        res = out.copy()
        for y in range(h + 2):
            for x in range(w + 2):
                if out[y, x, 3] == 0:
                    best = None
                    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                        X, Y = x + dx, y + dy
                        if 0 <= X < w + 2 and 0 <= Y < h + 2 and out[Y, X, 3]:
                            ly, lx = Y - 1, X - 1
                            rid = self.lab[ly, lx] if 0 <= ly < h and 0 <= lx < w else 0
                            if rid: best = self.regs[rid][0][0]; break
                    if best:
                        res[y, x] = (*[max(0, int(c * 0.62)) for c in best], 255)
        img = Image.fromarray(res)
        if shadow:
            cx, cy, rx, ry = shadow
            full = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
            ImageDraw.Draw(full).ellipse([cx - rx + 1, cy - ry + 1, cx + rx + 1, cy + ry + 1], fill=(40, 90, 45, 120))
            full.alpha_composite(img); img = full
        return img

# ======================================================= zvířata
def fox():
    p = Paint(70, 46, 3)
    fx = '#d9622b'
    p.region([(1, 25), (8, 22), (17, 24), (24, 27), (25, 33), (17, 34), (9, 32), (3, 29)], fx)
    p.region([(1, 25), (8, 22), (11, 24), (10, 31), (3, 29)], '#f4eee8', fur=.06)
    far = make_ramp('#a84a22')
    p.region([(46, 31), (50, 31), (50, 43), (46, 43)], '#a84a22', ramp=far)
    p.region([(25, 31), (30, 31), (30, 43), (26, 43)], '#a84a22', ramp=far)
    p.region([(46, 38), (50, 38), (50, 43), (46, 43)], '#2a2a38', fur=.05)
    p.region([(26, 38), (30, 38), (30, 43), (26, 43)], '#2a2a38', fur=.05)
    p.region([(22, 27), (28, 22), (38, 20), (46, 21), (52, 25), (53, 31), (46, 35), (36, 36), (26, 36), (21, 33)], fx, bump=.05)
    p.region([(21, 28), (30, 27), (32, 35), (28, 37), (22, 36)], fx, bump=.18)
    p.region([(43, 33), (48, 33), (48, 43), (43, 43)], fx, bump=.1, edge=True)
    p.region([(23, 35), (28, 35), (28, 43), (22, 43)], fx, bump=.1, edge=True)
    p.region([(43, 39), (48, 39), (48, 43), (43, 43)], '#2a2a38', fur=.05)
    p.region([(22, 39), (28, 39), (28, 43), (22, 43)], '#2a2a38', fur=.05)
    p.region([(49, 27), (53, 26), (53, 34), (49, 34)], '#f4eee8', fur=.05)
    p.region([(46, 25), (47, 16), (52, 11), (58, 10), (66, 16), (67, 19), (61, 21), (56, 24), (51, 28)], fx, bump=.2)
    p.region([(48, 16), (48, 5), (53, 11)], fx, edge=True)
    p.region([(53, 11), (58, 4), (59, 11)], fx, edge=True)
    p.region([(59, 18), (67, 19), (65, 23), (57, 23)], '#f4eee8', fur=.05)
    p.dot(49, 9, '#c89a7a'); p.dot(55, 8, '#c89a7a'); p.dot(55, 9, '#c89a7a')
    p.rect(56, 14, 58, 16, '#241a28'); p.dot(56, 14, '#ffffff')
    p.rect(66, 17, 68, 19, '#241a28')
    return p.render(shadow=(34, 41, 26, 4))

def lion():
    p = Paint(76, 52, 5)
    tan = '#e3a553'; mane = '#a8522a'
    p.region([(2, 26), (6, 24), (9, 28), (8, 36), (5, 36)], tan, fur=.08)      # ocas
    p.ellipse(4, 37, 3.4, 4.2, mane, fur=.12)
    far = make_ramp('#b57e3a')
    p.region([(52, 36), (57, 36), (57, 49), (52, 49)], '#b57e3a', ramp=far)
    p.region([(24, 36), (30, 36), (30, 49), (25, 49)], '#b57e3a', ramp=far)
    p.region([(14, 28), (22, 22), (36, 20), (50, 22), (58, 27), (58, 38), (50, 42), (30, 43), (18, 42), (13, 36)], tan, bump=.1)
    p.region([(14, 30), (26, 29), (29, 40), (24, 43), (15, 42)], tan, bump=.2)       # stehno
    p.region([(40, 36), (46, 36), (46, 49), (40, 49)], tan, bump=.08, edge=True)
    p.region([(44, 36), (51, 36), (51, 50), (44, 50)], tan, bump=.1, edge=True)
    p.region([(16, 40), (23, 40), (23, 50), (16, 50)], tan, bump=.1, edge=True)
    for (a, b) in [(16, 23), (44, 51), (40, 46)]:
        p.region([(a, 46), (b, 46), (b, 50), (a, 50)], '#d9923f', fur=.06)
    p.ellipse(56, 23, 12, 13, mane, fur=.16, bump=.2)                                # hříva
    p.region([(50, 33), (60, 36), (58, 44), (49, 41)], mane, fur=.16, bump=.1)       # hříva na hrudi
    p.ellipse(60, 24, 7.5, 7, tan, bump=.25)                                          # tvář
    p.region([(61, 24), (69, 25), (70, 29), (65, 31), (59, 29)], '#f3d8a0', bump=.25) # čumák
    p.ellipse(52, 13, 2.8, 2.8, tan, edge=True); p.ellipse(64, 12, 2.6, 2.6, tan, edge=True)
    p.rect(68, 25, 71, 27, '#3a2430'); p.rect(60, 20, 62, 22, '#241a28'); p.dot(60, 20, '#ffffff')
    p.dot(66, 29, '#7a4a3a'); p.dot(67, 29, '#7a4a3a')
    return p.render(shadow=(37, 48, 28, 4))

def giraffe():
    p = Paint(64, 92, 7)
    y = '#eab552'; spot = '#8f4a22'
    p.region([(8, 40), (5, 40), (3, 52), (6, 52)], y, fur=.05)
    far = make_ramp('#c8903a')
    p.region([(14, 52), (18, 52), (18, 88), (15, 88)], '#c8903a', ramp=far)
    p.region([(38, 52), (42, 52), (42, 88), (39, 88)], '#c8903a', ramp=far)
    p.region([(10, 40), (20, 35), (34, 34), (46, 36), (49, 44), (47, 54), (34, 57), (18, 57), (11, 52)], y, bump=.1)
    p.region([(40, 38), (47, 38), (57, 14), (49, 11)], y, bump=.3)             # krk
    p.region([(10, 53), (15, 53), (15, 88), (11, 88)], y, bump=.05, edge=True)
    p.region([(34, 53), (39, 53), (39, 88), (35, 88)], y, bump=.05, edge=True)
    p.region([(10, 85), (15, 85), (15, 90), (10, 90)], '#4a3030', fur=.03)
    p.region([(34, 85), (39, 85), (39, 90), (34, 90)], '#4a3030', fur=.03)
    p.region([(14, 85), (18, 85), (18, 90), (15, 90)], '#3a2428', fur=.03)
    p.region([(38, 85), (42, 85), (42, 90), (39, 90)], '#3a2428', fur=.03)
    p.region([(48, 10), (56, 8), (63, 12), (63, 17), (55, 18), (50, 16)], y, bump=.3)   # hlava
    p.region([(56, 13), (63, 12), (63, 18), (57, 18)], '#f0d8a0', bump=.3)
    p.region([(52, 6), (53, 0), (55, 0), (55, 7)], '#6a4a3a', fur=.03)
    p.region([(57, 6), (58, 0), (60, 0), (60, 8)], '#6a4a3a', fur=.03)
    p.region([(45, 8), (50, 11), (48, 14), (44, 11)], y, edge=True)
    spots = [(16, 41), (26, 40), (36, 40), (22, 50), (31, 49), (42, 47), (13, 48), (46, 31), (51, 24), (48, 17), (44, 40), (13, 70), (37, 68), (13, 80), (37, 78), (13, 60), (37, 58)]
    for (sx, sy) in spots:
        p.pattern(lambda d, sx=sx, sy=sy: d.polygon([(sx - 3, sy - 1), (sx - 1, sy - 4), (sx + 3, sy - 3), (sx + 4, sy + 1), (sx + 1, sy + 4), (sx - 2, sy + 3)], fill=255), spot)
    p.rect(55, 12, 57, 14, '#241a28'); p.dot(55, 12, '#ffffff'); p.dot(62, 14, '#4a2a2a')
    return p.render(shadow=(30, 89, 24, 3))

def zebra():
    p = Paint(72, 58, 9)
    w = '#efeae2'; k = '#2c2a3c'
    p.region([(4, 26), (8, 24), (6, 38), (3, 38)], k, fur=.05)
    far = make_ramp('#cfc9c8')
    p.region([(24, 36), (29, 36), (29, 54), (25, 54)], '#cfc9c8', ramp=far)
    p.region([(50, 36), (55, 36), (55, 54), (51, 54)], '#cfc9c8', ramp=far)
    p.region([(10, 30), (18, 25), (34, 24), (48, 26), (56, 30), (56, 40), (48, 43), (30, 44), (16, 43), (10, 38)], w, bump=.1)
    p.region([(10, 31), (24, 30), (27, 42), (22, 45), (12, 43)], w, bump=.2)
    p.region([(44, 24), (52, 26), (60, 12), (53, 10)], w, bump=.25)
    p.region([(20, 41), (25, 41), (25, 54), (20, 54)], w, bump=.08, edge=True)
    p.region([(45, 41), (51, 41), (51, 54), (46, 54)], w, bump=.08, edge=True)
    p.region([(54, 8), (62, 7), (70, 13), (70, 18), (62, 19), (56, 15)], w, bump=.25)
    p.region([(62, 12), (70, 13), (70, 19), (63, 19)], '#6e6a82', bump=.2)
    p.region([(55, 5), (57, 0), (60, 5)], w, edge=True); p.region([(60, 6), (63, 1), (64, 7)], w, edge=True)
    for (a, b) in [(20, 25), (45, 51)]:
        p.region([(a, 52), (b, 52), (b, 56), (a, 56)], '#2c2a3c', fur=.03)
    for xx in range(13, 54, 5):
        p.pattern(lambda d, xx=xx: d.polygon([(xx, 24), (xx + 2, 24), (xx - 3, 44), (xx - 5, 44)], fill=255), k)
    for yy in (30, 36, 42, 48):
        for lx in (20, 45, 24, 50):
            p.pattern(lambda d, lx=lx, yy=yy: d.rectangle([lx, yy, lx + 5, yy + 1], fill=255), k)
    for (a, b) in [(46, 25), (49, 21), (52, 17), (55, 13)]:
        p.pattern(lambda d, a=a, b=b: d.polygon([(a, b), (a + 3, b - 1), (a + 3, b + 3), (a, b + 4)], fill=255), k)
    for (a, b) in [(56, 9), (59, 10), (62, 12)]:
        p.pattern(lambda d, a=a, b=b: d.line([(a, b), (a - 2, b + 4)], fill=255), k)
    p.rect(60, 11, 62, 13, '#241a28'); p.dot(60, 11, '#ffffff'); p.dot(67, 16, '#3a3040')
    return p.render(shadow=(34, 54, 26, 3))

def elephant():
    p = Paint(80, 62, 11)
    g = '#8c93ab'
    p.region([(8, 22), (10, 22), (7, 36), (5, 36)], '#5a5870', fur=.03)
    far = make_ramp('#6e7590')
    p.region([(16, 40), (24, 40), (24, 58), (16, 58)], '#6e7590', ramp=far)
    p.region([(50, 40), (58, 40), (58, 58), (50, 58)], '#6e7590', ramp=far)
    p.region([(8, 24), (16, 14), (34, 10), (52, 12), (62, 20), (64, 36), (60, 46), (44, 49), (24, 49), (12, 44), (8, 34)], g, bump=.12, fur=.14)
    p.region([(24, 44), (34, 44), (34, 59), (24, 59)], g, bump=.06, edge=True, fur=.14)
    p.region([(44, 44), (54, 44), (54, 59), (44, 59)], g, bump=.06, edge=True, fur=.14)
    for lx in (24, 44):
        for k in range(3): p.rect(lx + 1 + k * 3, 56, lx + 3 + k * 3, 58, '#d8d0c0')
    p.region([(54, 14), (62, 10), (70, 14), (72, 26), (68, 32), (60, 30), (54, 24)], g, bump=.22, fur=.14)   # hlava
    p.region([(66, 26), (72, 26), (72, 34), (74, 44), (72, 54), (68, 56), (66, 50), (68, 42), (66, 34)], g, bump=.2, fur=.1)  # chobot
    p.region([(40, 14), (54, 10), (58, 22), (52, 38), (44, 40), (38, 28)], '#6f7794', bump=.3, fur=.1)         # ucho
    p.region([(43, 18), (53, 15), (54, 24), (50, 34), (45, 34), (42, 26)], '#d8a0a8', bump=.3, fur=.08)
    p.region([(66, 30), (74, 36), (74, 38), (66, 34)], '#f4ecd6', bump=.2, fur=.04)                              # kel
    for yy in (34, 38, 42, 46, 50):
        p.pattern(lambda d, yy=yy: d.line([(67, yy), (72, yy + 1)], fill=255), '#5e6480')
    p.rect(66, 17, 68, 19, '#1c1822'); p.dot(66, 17, '#ffffff')
    return p.render(shadow=(36, 59, 30, 4))

ANIMALS = [('fox', fox), ('lion', lion), ('giraffe', giraffe), ('zebra', zebra), ('elephant', elephant)]

def sheet(out):
    ims = [(n, f()) for n, f in ANIMALS]
    pad = 8
    W = sum(i.width for _, i in ims) + pad * (len(ims) + 1)
    H = max(i.height for _, i in ims) + pad * 2
    sh = Image.new('RGBA', (W, H), (128, 176, 98, 255))
    rng = random.Random(1); px = sh.load()
    leaf = [(143, 190, 104), (112, 160, 84), (160, 205, 120)]
    for y in range(H):
        for x in range(W):
            if rng.random() < .10: px[x, y] = rng.choice(leaf) + (255,)
    x = pad
    for n, im in ims:
        sh.alpha_composite(im, (x, H - im.height - pad)); x += im.width + pad
    sh.resize((sh.width * 5, sh.height * 5), Image.NEAREST).save(f'{out}/painted_sheet.png')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'painted_out'
    os.makedirs(out, exist_ok=True)
    sheet(out); print('ok')
