"""ZOO: zkouška stylů, v2 (budovy a terén blíž referenci @kingsfollowgame).
Použití: python zoo_art.py <výstupní složka>
Vyrobí pro každý styl (A, B, C): arch budov a hustou scénu. Vše procedurálně v nativním rozlišení, zvětšení bez vyhlazení."""
import random, sys, os, math
from PIL import Image, ImageDraw, ImageEnhance

def hx(s):
    s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def shade_col(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)

def mix(a, b, t):
    return tuple(int(a[k] * (1 - t) + b[k] * t) for k in range(3)) + (255,)

# ============================ STYLY ============================
STYLES = {
 # A: co nejvěrněji reference (sytá tmavší tráva, silný hnědý obrys, silná textura), jen motivy zoo
 'A_reference': dict(
   grass=['#4c9a3b', '#58a843', '#428f34'], grass_d='#367a2c', grass_l='#6bb852',
   dirt=['#b98d5c', '#ad8250', '#c49968'], dirt_d='#8f6a40',
   cobble='#8e8d97', cobble_d='#6f6e79', cobble_l='#a9a8b2',
   water=['#4f8fcf', '#5b9cd8'], ice=['#c8e4f2', '#b2d6ea'],
   line='#2a1c1a', line_wall='#3a2620',
   roofs=['#d9822b', '#c4452d', '#6c7d9c', '#7a5236', '#8a5ab5'],
   walls=['#e6d3a3', '#d9c394', '#a9a79b', '#cdbfa0'], timber='#5a3c2a',
   win='#2e2430', win_lit='#ffd86b', wood='#8a5a35', wood_l='#a8703f', wood_d='#6a4228',
   leaf=['#2f7a38', '#3d8f43', '#276a30'], pine=['#216b44', '#2d8455'],
   texture=1.0, sat=0.82, bright=0.95, sky='#2b4a2a', hud=('#3b2a28', '#ffe9a8', '#e8c458'),
   shirts=['#c8452e', '#4a6fa8', '#d9a02b', '#7a5ab0', '#c86a8a', '#3f8f60', '#d9822b', '#e8e0d0']),
 # B: světlý hravý (cukrové barvy, měkký švestkový obrys), hustota jako reference
 'B_playful': dict(
   grass=['#8fd96b', '#80cf5f', '#a3e47e'], grass_d='#69b84e', grass_l='#b8f090',
   dirt=['#f5e2ae', '#ecd395', '#f9ebc5'], dirt_d='#d6b872',
   cobble='#dcd8e8', cobble_d='#b9b3cf', cobble_l='#f1eef8',
   water=['#6fc9f2', '#9ee0fb'], ice=['#d6f3ff', '#b4e4fa'],
   line='#5b3f4a', line_wall='#7a5560',
   roofs=['#ef5b5b', '#4aa8dc', '#ffc93c', '#b57bec', '#ff8fb8', '#52c78a'],
   walls=['#fff3d6', '#ffe6e0', '#e6f6ff', '#f2ffe0'], timber='#c98a5a',
   win='#5a7fb0', win_lit='#fff2a6', wood='#d99a5b', wood_l='#f0b977', wood_d='#b87a45',
   leaf=['#4fbf5a', '#6fd66b', '#3a9e4e'], pine=['#2fa86a', '#46c07f'],
   texture=0.6, sat=1.0, bright=1.0, sky='#cdeefb', hud=('#5b3f4a', '#fff3d6', '#ffc93c'),
   shirts=['#ef5b5b', '#4aa8dc', '#ffc93c', '#b57bec', '#ff8fb8', '#52c78a', '#ff9a3c', '#ffffff']),
 # C: hybrid: struktura a textura jako reference, ale světlejší a veselejší barvy
 'C_hybrid': dict(
   grass=['#68bd48', '#5eb23f', '#76c853'], grass_d='#47993a', grass_l='#8bd965',
   dirt=['#d8ae78', '#cba06a', '#e3bd8a'], dirt_d='#a98255',
   cobble='#b4b2c2', cobble_d='#8d8ba0', cobble_l='#cecbdb',
   water=['#58b4e8', '#78cdf4'], ice=['#cdeefa', '#aedcf2'],
   line='#3d2a30', line_wall='#5a3f44',
   roofs=['#f08a30', '#e0503e', '#5b9bd8', '#8a5fc9', '#f2b53c', '#46b88a'],
   walls=['#f5e6bd', '#f2d6c4', '#d8e8f0', '#e8e4d0'], timber='#7a5238',
   win='#3a4a78', win_lit='#ffe27a', wood='#c98a52', wood_l='#e0a468', wood_d='#9c6840',
   leaf=['#3fa84a', '#55bd58', '#318f40'], pine=['#25905a', '#38ab6f'],
   texture=0.85, sat=1.0, bright=1.0, sky='#9fd4ec', hud=('#4a3430', '#fff0c8', '#f2b53c'),
   shirts=['#e0503e', '#5b9bd8', '#f2b53c', '#8a5fc9', '#ff8fb8', '#46b88a', '#f08a30', '#ffffff']),
}
S = None  # aktuální styl (slovník s barvami jako tuple)

def load_style(name):
    global S
    raw = STYLES[name]
    S = {}
    for k, v in raw.items():
        if isinstance(v, str) and v.startswith('#'): S[k] = hx(v)
        elif isinstance(v, list) and v and isinstance(v[0], str) and v[0].startswith('#'): S[k] = [hx(x) for x in v]
        else: S[k] = v
    S['skins'] = [hx('#ffd6b0'), hx('#e8a67a'), hx('#9a6a4a'), hx('#6b4530')]
    S['pants'] = [hx(x) for x in ['#3f4f80', '#5a3d30', '#3d4a5b', '#6f5a8a', '#b79a6a']]
    S['cream'] = hx('#fff3d6'); S['white'] = hx('#fff8ee'); S['gold'] = hx('#ffc93c'); S['brown'] = hx('#6b4535')

# ============================ NÁSTROJE ============================
def new(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def outlined(sprite, col=None):
    col = col or S['line']
    w, h = sprite.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    px = sprite.load(); op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + 1 + dx, y + 1 + dy
                    if op[X, Y][3] == 0: op[X, Y] = col
    for y in range(h):
        for x in range(w):
            if px[x, y][3]: op[x + 1, y + 1] = px[x, y]
    return out

def tone(im, sat=1.0, bright=1.0):
    if sat == 1.0 and bright == 1.0: return im
    a = im.split()[3]
    rgb = im.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(sat); rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    out = rgb.convert('RGBA'); out.putalpha(a); return out

def jitter_fill(im, region_mask_color, cols, density, rng):
    """posype pixely stejné barvy náhodnými odstíny (textura)"""
    px = im.load(); w, h = im.size
    for y in range(h):
        for x in range(w):
            if px[x, y] == region_mask_color and rng.random() < density:
                px[x, y] = rng.choice(cols)

# ============================ TERÉN ============================
TW, TH = 32, 16
def tile_img(kind, rng, i=0, j=0):
    im = Image.new('RGBA', (TW, TH), (0, 0, 0, 0)); px = im.load()
    t = S['texture']
    base = {'grass': S['grass'][0], 'dirt': S['dirt'][0], 'cobble': S['cobble'], 'water': S['water'][0], 'ice': S['ice'][0]}[kind]
    for y in range(TH):
        for x in range(TW):
            # uvnitř kosočtverce
            if abs(x - 15.5) / 16 + abs(y - 7.5) / 8 <= 1.0:
                c = base
                r = rng.random()
                if kind == 'grass':
                    c = rng.choice(S['grass']) if r < .5 * (0.6 + t) else base
                    if r > 1 - .07 * t: c = S['grass_d']
                    elif r > 1 - .11 * t: c = S['grass_l']
                elif kind == 'dirt':
                    c = rng.choice(S['dirt']) if r < .5 else base
                    if r > 1 - .08 * t: c = S['dirt_d']
                elif kind == 'cobble':
                    # kameny 5x3 s posunem po řádcích
                    row = y // 3
                    off = 2 if row % 2 else 0
                    if (x + off) % 5 == 0 or y % 3 == 0: c = S['cobble_d'] if r < .85 else base
                    elif r < .25 * t + .05: c = S['cobble_l']
                    elif r > .93: c = S['cobble_d']
                elif kind == 'water':
                    c = S['water'][1] if (r < .06 and (x + y) % 2 == 0) else (S['water'][0] if (x // 3 + y // 2) % 3 else S['water'][1] if r < .03 else S['water'][0])
                elif kind == 'ice':
                    c = S['ice'][1] if r < .15 else base
                px[x, y] = c
    return im

# ============================ BUDOVY ============================
def wall_rect(dr, P0, P1, f, w, yb, hh, col):
    """obdélník na stěně (P0 → P1 je spodní hrana; stěna se po obrazovce svažuje)"""
    x0 = int(P0[0] + (P1[0] - P0[0]) * f)
    slope = (P1[1] - P0[1]) / (P1[0] - P0[0]) if P1[0] != P0[0] else 0
    for k in range(w):
        x = x0 + k
        yb_screen = P0[1] + slope * (x - P0[0])
        y1 = int(yb_screen - yb); y0 = y1 - hh + 1
        dr.line([(x, y0), (x, y1)], fill=col)

def house(wi=1.0, dj=1.0, wh=14, rh=9, wall=None, roof=None, mirror=False, windows=2, door=None, timber=True,
          awning=None, chimney=False, flag=None, seed=0, sign=None, big_door=False):
    """izometrický dům se sedlovou střechou, hřeben rovnoběžný s osou u; vrací (sprite, kotva = přední spodní roh)"""
    rng = random.Random(seed)
    wall = wall or S['walls'][0]; roof = roof or S['roofs'][0]
    lw, rw = shade_col(wall, 1.0), shade_col(wall, 0.78)
    if mirror: lw, rw = rw, lw
    pad = 6
    W = int(16 * (wi + dj)) + pad * 2 + 4
    Hh = int(8 * (wi + dj)) + wh + rh + pad * 2 + 10
    im, g = new(W, Hh)
    ax, ay = pad + 16 * dj, pad + rh + wh + 4
    A = (ax, ay); B = (ax + 16 * wi, ay + 8 * wi); D = (ax - 16 * dj, ay + 8 * dj); C = (B[0] - 16 * dj, B[1] + 8 * dj)
    up = lambda p, h: (p[0], p[1] - h)
    mid = lambda p, q: ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    RA = up(mid(A, D), wh + rh); RB = up(mid(B, C), wh + rh)
    roof_l, roof_d = roof, shade_col(roof, 0.74)
    roof_back = shade_col(roof, 0.62)
    ov = 2
    # zadní rovina střechy
    g.polygon([up(A, wh), up(B, wh), RB, RA], fill=roof_back)
    # levá (dlouhá) stěna D-C
    g.polygon([D, C, up(C, wh), up(D, wh)], fill=lw)
    # pravá štítová stěna B-C
    g.polygon([B, C, up(C, wh), RB, up(B, wh)], fill=rw)
    # přední rovina střechy s přesahem
    e1 = (D[0] - ov, D[1] - wh + ov // 2 + 1); e2 = (C[0] + 1, C[1] - wh + 1)
    g.polygon([e1, e2, (RB[0] + 2, RB[1]), (RA[0] - 1, RA[1])], fill=roof_l)
    # šindel: řady rovnoběžné s okapem
    steps = max(3, (wh + rh) // 3)
    nrows = int(rh * 1.0)
    for k in range(1, 6):
        t = k / 6.0
        p1 = (e1[0] + (RA[0] - e1[0]) * t, e1[1] + (RA[1] - e1[1]) * t)
        p2 = (e2[0] + (RB[0] - e2[0]) * t, e2[1] + (RB[1] - e2[1]) * t)
        g.line([p1, p2], fill=roof_d)
        # světlé „hrany šindelů“
        n = int((p2[0] - p1[0]) / 3)
        for q in range(n):
            if (q + k) % 2 == 0:
                x = p1[0] + (p2[0] - p1[0]) * q / max(1, n); y = p1[1] + (p2[1] - p1[1]) * q / max(1, n)
                g.point((x, y - 1), fill=shade_col(roof, 1.15))
    g.line([e1, e2], fill=shade_col(roof, 0.55))
    g.line([RA, RB], fill=shade_col(roof, 1.25))
    g.line([(RB[0], RB[1]), (B[0], B[1] - wh)], fill=shade_col(roof, 0.55))  # hrana štítu
    # textura stěn
    if timber:
        tc = S['timber']
        # levá stěna: svislé trámy + vodorovný pás
        for f in [0.04, 0.5, 0.96]:
            wall_rect(g, D, C, f, 1, 0, wh - 1, tc)
        wall_rect(g, D, C, 0.0, int(C[0] - D[0]), wh // 2, 1, tc)
        # štít
        for f in [0.04, 0.96]:
            wall_rect(g, B, C, 0, 1, 0, 0, tc)
        g.line([up(B, wh // 2), up(C, wh // 2)], fill=tc)
        g.line([up(mid(B, C), 0), up(mid(B, C), wh)], fill=tc)
    # okna na dlouhé stěně
    L = int(C[0] - D[0])
    for n in range(windows):
        f = (n + 1) / (windows + 1)
        wx = int(L * f) - 1
        wall_rect(g, D, C, wx / L, 4, wh // 2 - 1, 5, S['win'])
        wall_rect(g, D, C, wx / L + 1 / L, 2, wh // 2, 3, S['win_lit'] if rng.random() < .35 else shade_col(S['win'], 1.35))
        wall_rect(g, D, C, wx / L - 1 / L, 1, wh // 2 - 2, 1, S['timber'])
    # dveře / velká vrata na štítu
    Lr = int(B[0] - C[0]) if B[0] > C[0] else 0
    # (štít leží vpravo-dole směrem B→C míří doleva-dolů, proto zrcadlově)
    if big_door:
        wall_rect(g, C, D, 0.0, 0, 0, 0, S['win'])
        # velká vrata na dlouhé stěně uprostřed
        dw = max(6, int(L * 0.28)); fx = (L // 2 - dw // 2) / L
        wall_rect(g, D, C, fx, dw, 0, wh - 3, shade_col(S['wood'], .8))
        wall_rect(g, D, C, fx, dw, wh - 4, 1, S['wood_l'])
        wall_rect(g, D, C, fx + (dw // 2) / L, 1, 0, wh - 3, S['wood_d'])
    elif door is not None:
        wall_rect(g, D, C, door, 4, 0, 8, shade_col(S['wood'], .85))
        wall_rect(g, D, C, door, 4, 8, 1, S['wood_l'])
    # markýza
    if awning:
        a1, a2 = awning
        for k in range(0, int(C[0] - D[0]) - 2, 3):
            col = a1 if (k // 3) % 2 == 0 else a2
            wall_rect(g, D, C, (k + 1) / L, 3, wh // 2 - 4, 3, col)
        for k in range(0, int(C[0] - D[0]) - 2, 3):
            col = a1 if (k // 3) % 2 == 0 else a2
            wall_rect(g, D, C, (k + 1) / L, 3, wh // 2 - 7, 1, col)
    if chimney:
        cx, cy = int(RA[0] + (RB[0] - RA[0]) * .7), int(RA[1] + (RB[1] - RA[1]) * .7)
        g.rectangle([cx - 1, cy - 7, cx + 2, cy + 1], fill=hx('#9a8a84'))
        g.rectangle([cx - 1, cy - 8, cx + 2, cy - 7], fill=hx('#6a5a54'))
    if flag:
        fx_, fy_ = int(RB[0]), int(RB[1])
        g.line([(fx_, fy_), (fx_, fy_ - 9)], fill=S['wood_d'])
        g.polygon([(fx_, fy_ - 9), (fx_ + 6, fy_ - 7), (fx_, fy_ - 5)], fill=flag)
    sp = outlined(im, S['line_wall'])
    return sp, (int(C[0]) + 1, int(C[1]) + 1)

def tower(wi=0.9, wh=30, roof=None, wall=None, flag=None, seed=0):
    """vysoká věž se čtvercovým půdorysem a kuželovou/jehlanovou střechou (jako fialová věž v referenci)"""
    roof = roof or S['roofs'][4]; wall = wall or S['walls'][2]
    rng = random.Random(seed)
    pad = 8
    W = int(32 * wi) + pad * 2 + 6; rh = 22
    H = int(16 * wi) + wh + rh + pad * 2 + 6
    im, g = new(W, H)
    ax, ay = pad + 16 * wi + 2, pad + rh + wh + 2
    A = (ax, ay); B = (ax + 16 * wi, ay + 8 * wi); D = (ax - 16 * wi, ay + 8 * wi); C = (ax, ay + 16 * wi)
    up = lambda p, h: (p[0], p[1] - h)
    lw, rw = shade_col(wall, 1.0), shade_col(wall, 0.76)
    g.polygon([D, C, up(C, wh), up(D, wh)], fill=lw)
    g.polygon([B, C, up(C, wh), up(B, wh)], fill=rw)
    # kameny
    for y in range(int(C[1]) - wh, int(C[1])):
        for x in range(int(D[0]), int(B[0]) + 1):
            if g.im.getpixel((x, y))[:3] in (lw[:3], rw[:3]) and ((x + (y // 3) * 2) % 5 == 0 or y % 3 == 0) and rng.random() < .55:
                g.point((x, y), fill=shade_col(lw if x < C[0] else rw, 0.82))
    # okénka
    wall_rect(g, D, C, 0.45, 3, wh - 12, 5, S['win'])
    wall_rect(g, C, B, 0.40, 3, wh - 12, 5, shade_col(S['win'], .9))
    wall_rect(g, D, C, 0.45, 3, wh - 22, 4, S['win'])
    # cimbuří / římsa
    g.polygon([up(D, wh), up(C, wh), (C[0] + 0, C[1] - wh - 3), (D[0], D[1] - wh - 3)], fill=shade_col(wall, 1.1))
    # kuželová střecha
    cx = ax; base_y = A[1] + 8 * wi - wh   # střed horní plochy
    apex = (cx, base_y - rh)
    rx = 16 * wi + 3
    g.polygon([(cx - rx, base_y - 1), (cx, base_y + int(8 * wi) + 3), (cx + rx, base_y - 1), apex], fill=roof)
    g.polygon([(cx, base_y + int(8 * wi) + 3), (cx + rx, base_y - 1), apex], fill=shade_col(roof, .72))
    for k in range(1, 5):
        yy = base_y - k * rh // 5
        g.line([(cx - rx * (1 - k / 5), yy + 1), (cx + rx * (1 - k / 5), yy + 1)], fill=shade_col(roof, .85))
    g.line([apex, (apex[0], apex[1] - 5)], fill=S['wood_d'])
    if flag: g.polygon([(apex[0], apex[1] - 5), (apex[0] + 6, apex[1] - 3), (apex[0], apex[1] - 1)], fill=flag)
    return outlined(im, S['line_wall']), (int(C[0]) + 1, int(C[1]) + 1)

def dome(wi=1.4, seed=0, col=None):
    """skleněná voliéra: kupole nad nízkým soklem"""
    col = col or hx('#bfe9f7')
    pad = 6
    W = int(32 * wi) + pad * 2; H = int(16 * wi) + 44
    im, g = new(W, H)
    cx = W // 2; cy = H - pad - int(8 * wi) - 2
    rx = int(16 * wi) + 1; ry = int(8 * wi) + 1
    g.ellipse([cx - rx, cy - ry + 4, cx + rx, cy + ry + 4], fill=shade_col(S['walls'][3], .8))
    g.rectangle([cx - rx, cy - 3 + 4, cx + rx, cy + 4], fill=shade_col(S['walls'][3], .95))
    g.ellipse([cx - rx, cy - ry - 3 + 4, cx + rx, cy + ry - 3 + 4], fill=S['walls'][3])
    # kupole
    hgt = 30
    g.pieslice([cx - rx + 1, cy - hgt - 3, cx + rx - 1, cy + hgt - 3], 180, 360, fill=col)
    g.ellipse([cx - rx + 1, cy - ry - 3, cx + rx - 1, cy + ry - 3], fill=shade_col(col, 1.0))
    g.pieslice([cx - rx + 1, cy - hgt - 3, cx + rx - 1, cy + hgt - 3], 270, 360, fill=shade_col(col, .86))
    for k in range(-3, 4):
        g.line([(cx + k * rx // 4, cy - 3 + ry * 0.6 * (1 - abs(k) / 4) * 0), (cx + k * rx // 12, cy - hgt - 2)], fill=shade_col(col, .62))
    g.arc([cx - rx + 1, cy - hgt - 3 + 10, cx + rx - 1, cy + hgt - 3 - 10], 180, 360, fill=shade_col(col, .62))
    for (x, y) in [(cx - 6, cy - 12), (cx + 4, cy - 8), (cx - 2, cy - 18)]:
        g.point((x, y), fill=hx('#ff7aa5'))  # ptáčci uvnitř
    g.point((cx - 7, cy - 16), fill=S['white']); g.point((cx - 6, cy - 17), fill=S['white'])
    return outlined(im, S['line_wall']), (cx, cy + ry + 2)

def carousel(seed=0):
    pad = 4
    im, g = new(60, 60)
    cx, cy = 30, 46
    g.ellipse([cx - 24, cy - 10, cx + 24, cy + 10], fill=S['wood_l'])
    g.ellipse([cx - 22, cy - 9, cx + 22, cy + 8], fill=S['cream'])
    g.ellipse([cx - 22, cy - 9 + 5, cx + 22, cy + 8 + 3], fill=shade_col(S['cream'], .85)) if False else None
    for k in range(6):
        a = k * math.pi / 3
        px, py = cx + math.cos(a) * 17, cy + math.sin(a) * 6
        col = S['roofs'][k % len(S['roofs'])]
        g.line([(px, py), (px, py - 20)], fill=S['gold'])
        g.ellipse([px - 2, py - 8, px + 2, py - 3], fill=col)  # zvířátko
    g.line([(cx, cy), (cx, cy - 28)], fill=S['wood_d'], width=2)
    top = cy - 24
    # pruhovaná stříška
    for k in range(12):
        a0 = k * math.pi / 6; a1 = (k + 1) * math.pi / 6
        col = S['roofs'][0] if k % 2 == 0 else S['white']
        if math.sin((a0 + a1) / 2) >= -0.15:
            g.polygon([(cx, top - 12), (cx + math.cos(a0) * 26, top + math.sin(a0) * 9), (cx + math.cos(a1) * 26, top + math.sin(a1) * 9)], fill=col)
    g.line([(cx, top - 12), (cx, top - 17)], fill=S['wood_d'])
    g.polygon([(cx, top - 17), (cx + 6, top - 15), (cx, top - 13)], fill=S['roofs'][1])
    return outlined(im, S['line_wall']), (cx, cy + 10)

def igloo():
    im, g = new(40, 30)
    cx, cy = 20, 22
    g.ellipse([cx - 16, cy - 14, cx + 16, cy + 6], fill=hx('#e6f6ff'))
    g.pieslice([cx - 16, cy - 14, cx + 16, cy + 6], 90, 270, fill=hx('#f4fbff'))
    for yy in (cy - 10, cy - 5, cy):
        g.arc([cx - 15, yy - 7, cx + 15, yy + 4], 0, 180, fill=hx('#b4dcf2'))
    for k in range(-3, 4):
        g.line([(cx + k * 4, cy - 10), (cx + k * 5, cy + 4)], fill=hx('#b4dcf2')) if False else None
    g.ellipse([cx - 4, cy - 2, cx + 4, cy + 6], fill=hx('#4a5a7a'))
    g.rectangle([cx - 4, cy + 2, cx + 4, cy + 6], fill=hx('#4a5a7a'))
    return outlined(im, S['line_wall']), (cx, cy + 6)

def candy_cart():
    im, g = new(24, 26)
    g.rectangle([3, 12, 20, 22], fill=S['cream']); g.rectangle([3, 18, 20, 22], fill=shade_col(S['cream'], .85))
    for k in range(0, 22, 4):
        g.polygon([(k, 12), (min(k + 4, 23), 12), (min(k + 3, 22), 5), (max(k + 1, 1), 5)], fill=S['roofs'][0] if (k // 4) % 2 == 0 else S['white'])
    g.ellipse([8, 0, 15, 6], fill=hx('#ff8fd0'))
    g.rectangle([11, 6, 12, 10], fill=S['wood_l'])
    g.ellipse([2, 22, 7, 26], fill=S['wood_d']); g.ellipse([16, 22, 21, 26], fill=S['wood_d'])
    return outlined(im, S['line_wall']), (12, 24)

def fence_post():
    im, g = new(5, 12)
    g.rectangle([1, 2, 3, 10], fill=S['wood_l']); g.rectangle([3, 2, 3, 10], fill=S['wood'])
    g.rectangle([0, 1, 4, 2], fill=S['cream'])
    return outlined(im, S['line_wall'])

# ============================ ZVÍŘATA, STROMY, LIDÉ ============================
def shade(im, base, dark, light=None, frac=.5):
    px = im.load(); w, h = im.size
    ys = [y for y in range(h) for x in range(w) if px[x, y] == base]
    if not ys: return
    top, bot = min(ys), max(ys)
    for y in range(h):
        for x in range(w):
            if px[x, y] == base:
                t = (y - top) / max(1, bot - top)
                if t > frac: px[x, y] = dark
                elif light and t < .18 and (x + y) % 2 == 0: px[x, y] = light

def elephant():
    im, g = new(34, 28)
    grey, dk, lt = hx('#b9c3e0'), hx('#97a3c9'), hx('#d5ddf2')
    for lx in (8, 13, 21, 26):
        g.rectangle([lx, 18, lx + 3, 25], fill=grey); g.rectangle([lx, 24, lx + 3, 25], fill=dk)
    g.ellipse([7, 6, 29, 22], fill=grey); g.ellipse([0, 5, 12, 17], fill=grey)
    g.rectangle([1, 14, 4, 22], fill=grey); g.rectangle([0, 20, 3, 23], fill=grey)
    g.ellipse([6, 8, 15, 20], fill=dk); g.ellipse([7, 9, 13, 17], fill=hx('#f4aabd'))
    g.line([(29, 12), (31, 20)], fill=dk); g.point((31, 21), fill=S['brown'])
    shade(im, grey, dk, lt, .55)
    g.rectangle([3, 14, 4, 15], fill=S['white']); g.point((3, 10), fill=S['line']); g.point((4, 10), fill=S['line'])
    return outlined(im, S['line'])

def giraffe():
    im, g = new(26, 42)
    y1, y2, sp = hx('#ffd35a'), hx('#f2b53c'), hx('#c97b3a')
    for lx in (6, 9, 15, 18):
        g.rectangle([lx, 24, lx + 1, 38], fill=y1); g.rectangle([lx, 36, lx + 1, 38], fill=S['brown'])
    g.ellipse([4, 17, 21, 29], fill=y1)
    g.polygon([(16, 21), (22, 21), (20, 6), (16, 6)], fill=y1)
    g.ellipse([15, 1, 25, 9], fill=y1); g.rectangle([22, 5, 25, 8], fill=hx('#f8e0a6'))
    g.line([(17, 0), (17, -1)], fill=S['brown']); g.point((20, 0), fill=S['brown'])
    g.line([(4, 20), (2, 27)], fill=S['brown'])
    shade(im, y1, y2, None, .6)
    for (sx, sy) in [(8, 20), (13, 23), (17, 19), (10, 26), (18, 14), (18, 9), (6, 24)]:
        g.rectangle([sx, sy, sx + 1, sy + 1], fill=sp)
    g.point((20, 3), fill=S['line'])
    return outlined(im, S['line'])

def zebra():
    im, g = new(26, 22)
    w, k = hx('#fffaf0'), hx('#4b4560')
    for lx in (6, 9, 16, 19):
        g.rectangle([lx, 13, lx + 1, 19], fill=w); g.rectangle([lx, 18, lx + 1, 19], fill=k)
    g.ellipse([4, 6, 20, 16], fill=w); g.polygon([(17, 8), (21, 3), (24, 5), (21, 10)], fill=w)
    g.ellipse([19, 2, 25, 8], fill=w); g.rectangle([22, 6, 25, 8], fill=hx('#7a7390'))
    g.line([(3, 8), (1, 15)], fill=k)
    for x in range(6, 18, 3): g.line([(x, 7), (x - 1, 14)], fill=k)
    g.line([(19, 4), (22, 3)], fill=k); g.point((22, 4), fill=S['line'])
    return outlined(im, S['line'])

def flamingo():
    im, g = new(14, 26)
    p, pd = hx('#ff9bbd'), hx('#f2709f')
    g.line([(6, 25), (6, 15)], fill=hx('#ff7aa5')); g.ellipse([2, 9, 11, 17], fill=p)
    g.line([(9, 10), (10, 6)], fill=p, width=2); g.ellipse([8, 2, 12, 6], fill=p)
    g.rectangle([12, 4, 13, 5], fill=S['line']); g.ellipse([3, 12, 8, 17], fill=pd); g.point((10, 3), fill=S['line'])
    return outlined(im, S['line'])

def penguin():
    im, g = new(10, 14)
    k, w = hx('#46506e'), S['white']
    g.ellipse([1, 1, 8, 12], fill=k); g.ellipse([2, 4, 7, 12], fill=w)
    g.rectangle([3, 12, 4, 12], fill=hx('#ffa23c')); g.rectangle([6, 12, 7, 12], fill=hx('#ffa23c'))
    g.rectangle([4, 3, 6, 4], fill=hx('#ffa23c')); g.point((3, 2), fill=w); g.point((6, 2), fill=w)
    return outlined(im, S['line'])

def lion():
    im, g = new(26, 20)
    body, dk, mane = hx('#f2c06a'), hx('#d9a04a'), hx('#c9702e')
    for lx in (5, 8, 15, 18): g.rectangle([lx, 11, lx + 1, 16], fill=body)
    g.ellipse([3, 5, 18, 14], fill=body); g.line([(3, 8), (0, 14)], fill=dk); g.rectangle([0, 14, 1, 15], fill=mane)
    g.ellipse([14, 1, 25, 13], fill=mane); g.ellipse([17, 4, 24, 12], fill=body)
    g.point((20, 7), fill=S['line']); g.point((23, 8), fill=hx('#7a3d2e')); g.point((18, 5), fill=S['line'])
    shade(im, body, dk, None, .6)
    return outlined(im, S['line'])

def panda():
    im, g = new(16, 18)
    w, k = hx('#fffaf0'), hx('#3b3650')
    g.ellipse([2, 7, 14, 17], fill=w); g.ellipse([3, 8, 13, 12], fill=k) if False else None
    g.rectangle([2, 12, 4, 16], fill=k); g.rectangle([11, 12, 13, 16], fill=k)
    g.ellipse([3, 1, 13, 9], fill=w); g.ellipse([2, 0, 5, 3], fill=k); g.ellipse([11, 0, 14, 3], fill=k)
    g.ellipse([4, 4, 6, 6], fill=k); g.ellipse([10, 4, 12, 6], fill=k); g.point((8, 6), fill=k)
    return outlined(im, S['line'])

def tree_round():
    im, g = new(26, 34)
    L = S['leaf']
    g.rectangle([11, 22, 14, 31], fill=S['wood_d']); g.rectangle([11, 22, 12, 31], fill=S['wood'])
    g.ellipse([2, 3, 24, 26], fill=L[0]); g.ellipse([5, 4, 17, 14], fill=L[1]); g.ellipse([14, 12, 23, 24], fill=L[2])
    r = random.Random(3)
    for _ in range(14 if S['texture'] > .7 else 6):
        x, y = r.randint(5, 21), r.randint(6, 22); g.point((x, y), fill=L[1] if r.random() < .5 else L[2])
    return outlined(im, S['line'])

def tree_pine():
    im, g = new(20, 34)
    P = S['pine']
    g.rectangle([8, 27, 11, 32], fill=S['wood_d'])
    for (yy, ww) in [(2, 5), (9, 7), (16, 9)]:
        g.polygon([(10, yy), (10 + ww, yy + 12), (10 - ww, yy + 12)], fill=P[1])
        g.polygon([(10, yy), (10 + ww, yy + 12), (10, yy + 12)], fill=P[0])
    return outlined(im, S['line'])

def bush():
    im, g = new(14, 9); L = S['leaf']
    g.ellipse([0, 2, 13, 8], fill=L[0]); g.ellipse([2, 0, 10, 5], fill=L[1])
    for (x, y) in [(3, 4), (9, 5), (6, 2)]: g.point((x, y), fill=hx('#ff8fb8'))
    return outlined(im, S['line'])

def person(shirt, pants, skin, kid=False, balloon=None, hat=None, seed=0):
    r = random.Random(seed)
    hair = r.choice([hx('#5b3a2e'), hx('#2e2a3a'), hx('#e8b04a'), hx('#c9602e'), hx('#8a5a3a')])
    off = 14 if balloon else 0
    im, g = new(8, (7 if kid else 9) + off)
    g.rectangle([2, off, 5, off + 2], fill=skin); g.rectangle([2, off, 5, off], fill=hair)
    if hat: g.rectangle([1, off, 6, off], fill=hat)
    if not kid:
        g.rectangle([1, off + 3, 6, off + 6], fill=shirt)
        g.rectangle([2, off + 7, 3, off + 8], fill=pants); g.rectangle([4, off + 7, 5, off + 8], fill=pants)
    else:
        g.rectangle([2, off + 3, 5, off + 5], fill=shirt)
        g.rectangle([2, off + 6, 3, off + 6], fill=pants); g.rectangle([4, off + 6, 5, off + 6], fill=pants)
    if balloon:
        g.ellipse([0, 0, 6, 7], fill=balloon); g.point((2, 2), fill=S['white']); g.line([(3, 8), (3, off + 2)], fill=S['line'])
    return outlined(im, S['line'])

# ============================ SCÉNA ============================
OXY = None
def P(i, j): return OXY[0] + (i - j) * 16, OXY[1] + (i + j) * 8

def make_scene(N=14, W=480, H=290):
    global OXY
    rng = random.Random(11)
    OXY = (W // 2, 60)
    img = Image.new('RGBA', (W, H), S['sky'])
    mid = N // 2
    kinds = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            kinds[i][j] = 'grass'
    for k in range(N):
        kinds[mid][k] = 'dirt'; kinds[k][mid] = 'dirt'
    for i in range(mid - 2, mid + 3):
        for j in range(mid - 2, mid + 3): kinds[i][j] = 'cobble'
    for i in range(2, 5):
        for j in range(9, 12): kinds[i][j] = 'water'
    for i in range(9, 12):
        for j in range(9, 12): kinds[i][j] = 'ice'
    tiles = {k: [tile_img(k, random.Random(a)) for a in range(4)] for k in ('grass', 'dirt', 'cobble', 'water', 'ice')}
    for s in range(2 * N - 1):
        for i in range(N):
            j = s - i
            if 0 <= j < N:
                x, y = P(i, j)
                t = rng.choice(tiles[kinds[i][j]])
                img.alpha_composite(t, (int(x - 16), int(y)))
    ents = []
    def put(spr, anchor, i, j, off=0.0, dx=0, dy=0):
        sp = spr
        x, y = P(i, j)
        ents.append((i + j + off, sp, int(x - anchor[0] + dx), int(y - anchor[1] + dy)))
    def put_bottom(sp, i, j, off=0.0, dx=0, dy=0):
        put(sp, (sp.size[0] // 2, sp.size[1] - 2), i, j, off, dx, dy)

    # ploty
    fp = fence_post()
    def fence_rect(i0, j0, i1, j1, gap=None):
        pts = set()
        for i in range(i0, i1 + 1): pts |= {(i, j0), (i, j1)}
        for j in range(j0, j1 + 1): pts |= {(i0, j), (i1, j)}
        segs = []
        for i in range(i0, i1): segs += [((i, j0), (i + 1, j0)), ((i, j1), (i + 1, j1))]
        for j in range(j0, j1): segs += [((i0, j), (i0, j + 1)), ((i1, j), (i1, j + 1))]
        for (a, b) in segs:
            if gap and gap == (a, b): continue
            xa, ya = P(*a); xb, yb = P(*b)
            im = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); gg = ImageDraw.Draw(im)
            ox_, oy_ = 20, 14
            for lift, col in ((9, S['wood_l']), (5, S['wood'])):
                gg.line([(ox_, oy_ - lift), (ox_ + xb - xa, oy_ + yb - ya - lift)], fill=col)
                gg.line([(ox_, oy_ - lift + 1), (ox_ + xb - xa, oy_ + yb - ya - lift + 1)], fill=S['wood_d'])
            ents.append(((a[0] + a[1] + b[0] + b[1]) / 2 + .2, outlined(im, S['line_wall']), int(xa - 21), int(ya - 15)))
        for (i, j) in pts: put_bottom(fp, i, j, .3)
    fence_rect(1, 1, 6, 6, gap=((3, 6), (4, 6)))
    fence_rect(8, 1, 13, 6)
    fence_rect(1, 8, 6, 13)
    fence_rect(8, 8, 13, 13)

    # zvířata
    for (spr, i, j, dx) in [(elephant(), 3, 3, -2), (elephant(), 4.3, 4.6, 2), (giraffe(), 10.5, 3, 0), (giraffe(), 9.5, 4.6, -1),
                            (zebra(), 12, 4.8, 0), (lion(), 11.6, 2.8, 0), (panda(), 5.2, 2.6, 0)]:
        put_bottom(spr, i, j, .1, dx=dx)
    for (i, j) in [(3.2, 10), (4.6, 9.4), (2.4, 11)]: put_bottom(flamingo(), i, j, .1)
    for (i, j) in [(9.5, 9.5), (10.5, 10), (11, 9.2), (10, 11), (11.3, 11), (12.2, 10.2)]: put_bottom(penguin(), i, j, .1)

    # budovy kolem náměstí (kotva = přední roh na zemi)
    R = S['roofs'] * 2; Wl = S['walls']
    def bld(spa, i, j, off=0.5):   # (sprite, anchor) → ground point (i,j) je přední roh
        put(spa[0], spa[1], i, j, off)
    # brána / pokladna (dole u vstupu), obchod, kavárna, slonárna, věž, ...
    bld(house(1.6, 1.0, 16, 10, Wl[0], R[0], windows=2, door=0.62, seed=1, chimney=True, flag=R[1]), 6.0, 13.8)       # pokladna
    bld(house(1.4, 1.0, 14, 9, Wl[1], R[1], windows=2, awning=(R[0], S['white']), seed=2), 4.4, 8.0 + 0.2)           # obchod se suvenýry
    bld(house(1.2, 1.0, 14, 9, Wl[3], R[2], windows=1, awning=(R[4], S['white']), seed=3, mirror=True), 9.8, 7.8)   # kavárna
    bld(house(2.0, 1.4, 18, 12, Wl[3], R[3], windows=0, big_door=True, seed=4, flag=R[0]), 7.6, 3.6)               # slonárna (u výběhu slonů)
    bld(tower(0.9, 34, R[4], Wl[2], flag=R[0]), 7.7, 7.6)                                                         # věž s vyhlídkou na žirafy
    bld(dome(1.6), 4.0, 12.4)
    bld(carousel(), 9.8, 6.2) if False else None
    bld(carousel(), 8.9, 9.6)
    bld(igloo(), 10.6, 12.4)
    bld(house(1.0, 1.0, 12, 8, Wl[2], R[5], windows=1, door=0.4, seed=5), 12.8, 8.4)
    bld(house(1.0, 1.0, 12, 8, Wl[1], R[2], windows=1, door=0.4, seed=6, mirror=True), 0.9, 7.2)
    bld(house(1.1, 1.0, 13, 8, Wl[0], R[4], windows=1, seed=7), 0.9, 4.5)
    bld(candy_cart(), 5.9, 7.0)
    bld(candy_cart(), 8.3, 5.1)

    # stromy v hustých houštinách po okrajích (jako v referenci) a podél cest
    spots = []
    for k in range(70):
        i, j = rng.uniform(-.2, N + .2), rng.uniform(-.2, N + .2)
        edge = min(i, j, N - i, N - j) < 1.2
        in_fence = any(a - .3 < i < c + .3 and b - .3 < j < d + .3 for (a, b, c, d) in [(1, 1, 6, 6), (8, 1, 13, 6), (1, 8, 6, 13), (8, 8, 13, 13)])
        near_path = abs(i - mid) < 0.9 or abs(j - mid) < 0.9
        plaza = abs(i - mid) < 3 and abs(j - mid) < 3
        if near_path or plaza: continue
        if in_fence and rng.random() < .8: continue
        if edge or rng.random() < .3: spots.append((i, j))
    for (i, j) in spots:
        spr = tree_pine() if rng.random() < .35 else tree_round()
        put_bottom(spr, i, j, .2)
    for _ in range(26):
        i, j = rng.uniform(.3, N - .3), rng.uniform(.3, N - .3)
        if abs(i - mid) < .8 or abs(j - mid) < .8: continue
        put_bottom(bush(), i, j, .15)

    # návštěvníci: hodně, v davech u brány, na cestách, u výběhů
    shirts = S['shirts']
    def spot(i, j, **kw):
        put_bottom(person(rng.choice(shirts), rng.choice(S['pants']), rng.choice(S['skins']), seed=rng.randint(0, 999), **kw), i, j, .45)
    for _ in range(80):
        if rng.random() < .5: i, j = mid + rng.uniform(-.4, .4), rng.uniform(.3, N - .3)
        else: i, j = rng.uniform(.3, N - .3), mid + rng.uniform(-.4, .4)
        kw = {}
        r = rng.random()
        if r < .25: kw['kid'] = True
        elif r < .35: kw['balloon'] = hx(rng.choice(['#ef5b5b', '#ffc93c', '#4aa8dc', '#ff8fb8']))
        spot(i, j, **kw)
    for _ in range(26):   # náměstí
        spot(mid + rng.uniform(-2.3, 2.3), mid + rng.uniform(-2.3, 2.3), **({'kid': True} if rng.random() < .3 else {}))
    for _ in range(14):   # fronta u pokladny
        spot(5.4 + rng.uniform(0, 1.6), 12.4 + rng.uniform(-.3, .6))

    ents.sort(key=lambda e: e[0])
    for key, sp, x, y in ents:
        img.alpha_composite(sp, (x, y))
    return img

def gate_arch():
    im, g = new(84, 60)
    for px in (2, 70):
        g.rectangle([px, 14, px + 11, 56], fill=S['wood_l']); g.rectangle([px + 7, 14, px + 11, 56], fill=S['wood'])
        g.rectangle([px - 1, 10, px + 12, 15], fill=S['roofs'][0])
    g.rectangle([8, 5, 76, 24], fill=S['cream']); g.rectangle([8, 19, 76, 24], fill=shade_col(S['cream'], .88))
    g.rectangle([6, 2, 78, 6], fill=S['roofs'][0])
    for k in range(7, 78, 8): g.rectangle([k, 2, k + 3, 6], fill=S['white'])
    gl = {'Z': ['111', '001', '010', '100', '111'], 'O': ['111', '101', '101', '101', '111']}
    x = 24
    for ch in 'ZOO':
        for yy, row in enumerate(gl[ch]):
            for xx, c in enumerate(row):
                if c == '1': g.rectangle([x + xx * 3, 9 + yy * 2, x + xx * 3 + 2, 9 + yy * 2 + 1], fill=S['roofs'][0] if ch == 'Z' else S['roofs'][1])
        x += 13
    return outlined(im, S['line_wall']), (42, 58)

def make_scene2(N=17, W=560, H=372):
    global OXY
    rng = random.Random(21)
    OXY = (W // 2, 78)
    img = Image.new('RGBA', (W, H), S['sky'])
    mid = N // 2
    kinds = [['grass'] * N for _ in range(N)]
    for k in range(N): kinds[mid][k] = 'dirt'; kinds[k][mid] = 'dirt'
    for i in range(mid - 2, mid + 3):
        for j in range(mid - 2, mid + 3): kinds[i][j] = 'cobble'
    for i in range(2, 5):
        for j in range(12, 15): kinds[i][j] = 'water'
    for i in range(12, 15):
        for j in range(12, 15): kinds[i][j] = 'ice'
    tiles = {k: [tile_img(k, random.Random(a)) for a in range(4)] for k in ('grass', 'dirt', 'cobble', 'water', 'ice')}
    for s in range(2 * N - 1):
        for i in range(N):
            j = s - i
            if 0 <= j < N:
                x, y = P(i, j)
                img.alpha_composite(rng.choice(tiles[kinds[i][j]]), (int(x - 16), int(y)))
    ents = []; occupied = []
    def put(spr, anchor, i, j, off=0.0, dx=0, dy=0):
        x, y = P(i, j)
        ents.append((i + j + off, spr, int(x - anchor[0] + dx), int(y - anchor[1] + dy)))
    def put_bottom(sp, i, j, off=0.0, dx=0, dy=0):
        put(sp, (sp.size[0] // 2, sp.size[1] - 2), i, j, off, dx, dy)
    def bld(spa, i, j, wi=1.0, dj=1.0, off=0.5):
        put(spa[0], spa[1], i, j, off); occupied.append((i - wi - .3, j - dj - .3, i + .3, j + .3))
    fp = fence_post()
    ENC = [(1, 1, 6, 6), (11, 1, 16, 6), (1, 11, 6, 16), (11, 11, 16, 16)]
    def fence_rect(i0, j0, i1, j1, gap=None):
        pts = set()
        for i in range(i0, i1 + 1): pts |= {(i, j0), (i, j1)}
        for j in range(j0, j1 + 1): pts |= {(i0, j), (i1, j)}
        segs = []
        for i in range(i0, i1): segs += [((i, j0), (i + 1, j0)), ((i, j1), (i + 1, j1))]
        for j in range(j0, j1): segs += [((i0, j), (i0, j + 1)), ((i1, j), (i1, j + 1))]
        for (a, b) in segs:
            xa, ya = P(*a); xb, yb = P(*b)
            im = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); gg = ImageDraw.Draw(im)
            for lift, col in ((9, S['wood_l']), (5, S['wood'])):
                gg.line([(20, 14 - lift), (20 + xb - xa, 14 + yb - ya - lift)], fill=col)
                gg.line([(20, 14 - lift + 1), (20 + xb - xa, 14 + yb - ya - lift + 1)], fill=S['wood_d'])
            ents.append(((a[0] + a[1] + b[0] + b[1]) / 2 + .2, outlined(im, S['line_wall']), int(xa - 21), int(ya - 15)))
        for (i, j) in pts: put_bottom(fp, i, j, .3)
    for e in ENC: fence_rect(*e)

    # zvířata: NE slon, NW žirafy+zebra+lev+panda, SW jezírko, SE tučňáci
    for (spr, i, j, dx) in [(elephant(), 13.0, 3.0, -2), (elephant(), 14.3, 4.6, 2), (elephant(), 12.2, 4.8, 0)]:
        put_bottom(spr, i, j, .1, dx=dx)
    for (spr, i, j) in [(giraffe(), 3.0, 3.0), (giraffe(), 4.4, 4.3), (zebra(), 2.4, 4.8), (lion(), 4.8, 2.2), (panda(), 1.9, 2.4)]:
        put_bottom(spr, i, j, .1)
    for (i, j) in [(3.0, 13.0), (4.2, 12.4), (2.6, 14.2), (4.6, 14.0)]: put_bottom(flamingo(), i, j, .1)
    for (i, j) in [(12.5, 12.5), (13.5, 13.2), (14.4, 12.4), (13.0, 14.3), (14.6, 14.6), (15.3, 13.4), (12.2, 14.9)]: put_bottom(penguin(), i, j, .1)

    R = S['roofs'] * 2; Wl = S['walls']
    # severovýchodní rameno
    bld(house(1.4, 1.0, 14, 9, Wl[1], R[1], windows=2, awning=(R[0], S['white']), seed=2), 8.0, 3.2, 1.4, 1.0)           # suvenýry
    bld(house(1.9, 1.4, 18, 12, Wl[3], R[3], windows=0, big_door=True, seed=4, flag=R[0]), 10.9, 4.4, 1.9, 1.4)           # slonárna
    bld(house(1.0, 1.0, 12, 8, Wl[0], R[2], windows=1, door=.4, seed=9), 7.9, 5.9, 1.0, 1.0)
    # severozápadní rameno (i < 6)
    bld(house(1.2, 1.0, 14, 9, Wl[3], R[2], windows=1, awning=(R[4], S['white']), seed=3, mirror=True), 4.2, 8.0, 1.2, 1.0)  # kavárna
    bld(dome(1.6), 3.6, 9.9, 1.4, 1.4)
    bld(house(1.0, 1.0, 12, 8, Wl[1], R[0], windows=1, door=.4, seed=11, mirror=True), 6.0, 7.8, 1.0, 1.0)
    # jihovýchodní rameno (i > 10)
    bld(house(1.0, 1.0, 12, 8, Wl[2], R[5], windows=1, door=.4, seed=5), 13.6, 8.0, 1.0, 1.0)
    bld(igloo(), 13.2, 9.9, 1.2, 1.2)
    # jihozápadní rameno (j > 10)
    bld(house(1.6, 1.0, 16, 10, Wl[0], R[0], windows=2, door=.62, seed=1, chimney=True, flag=R[1]), 8.0, 14.4, 1.6, 1.0)  # pokladna
    bld(house(1.4, 1.0, 14, 9, Wl[2], R[4], windows=2, awning=(R[5], S['white']), seed=12), 10.6, 13.2, 1.4, 1.0)       # obchod
    bld(gate_arch(), 8.5, 17.9, 2.0, 0.5)
    # náměstí
    bld(carousel(), 8.5, 8.7, 2.2, 2.2)
    bld(tower(0.9, 34, R[4], Wl[2], flag=R[0]), 10.5, 7.1, 1.0, 1.0)
    bld(candy_cart(), 6.7, 9.9, .8, .8); bld(candy_cart(), 10.3, 10.0, .8, .8)

    def free(i, j, pad=0.0):
        for (a, b, c, d) in occupied:
            if a - pad < i < c + pad and b - pad < j < d + pad: return False
        return True
    # stromy: houštiny po okrajích a mezi výběhy
    for _ in range(260):
        i, j = rng.uniform(-.6, N + .3), rng.uniform(-.6, N + .3)
        d_edge = min(i, j, N - i, N - j)
        in_enc = any(a - .2 < i < c + .2 and b - .2 < j < d + .2 for (a, b, c, d) in ENC)
        near_road = abs(i - (mid + .5)) < 1.0 or abs(j - (mid + .5)) < 1.0
        plaza = abs(i - (mid + .5)) < 3.2 and abs(j - (mid + .5)) < 3.2
        if in_enc and not (d_edge < 0.9): continue
        if near_road or plaza or not free(i, j, .6): continue
        if d_edge < 1.6 or rng.random() < .10:
            put_bottom(tree_pine() if rng.random() < .35 else tree_round(), i, j, .2)
    for _ in range(50):
        i, j = rng.uniform(.3, N - .3), rng.uniform(.3, N - .3)
        if abs(i - (mid + .5)) < 1.0 or abs(j - (mid + .5)) < 1.0 or not free(i, j, .3): continue
        if any(a < i < c and b < j < d for (a, b, c, d) in ENC): continue
        put_bottom(bush(), i, j, .15)

    shirts = S['shirts']
    def spot(i, j, **kw):
        put_bottom(person(rng.choice(shirts), rng.choice(S['pants']), rng.choice(S['skins']), seed=rng.randint(0, 999), **kw), i, j, .45)
    c = mid + .5
    for _ in range(150):
        if rng.random() < .5: i, j = c + rng.uniform(-.38, .38), rng.uniform(.4, N - .2)
        else: i, j = rng.uniform(.4, N - .2), c + rng.uniform(-.38, .38)
        if not free(i, j, .0): continue
        kw = {}
        r = rng.random()
        if r < .25: kw['kid'] = True
        elif r < .36: kw['balloon'] = hx(rng.choice(['#ef5b5b', '#ffc93c', '#4aa8dc', '#ff8fb8']))
        spot(i, j, **kw)
    for _ in range(46):
        i, j = c + rng.uniform(-2.4, 2.4), c + rng.uniform(-2.4, 2.4)
        if abs(i - 8.5) < 1.2 and abs(j - 8.7) < 1.2: continue
        spot(i, j, **({'kid': True} if rng.random() < .3 else {}))
    for _ in range(22): spot(rng.uniform(6.6, 9.2), rng.uniform(15.0, 16.4))
    for k in range(12):  # u plotů diváci
        spot(rng.uniform(11.4, 15.6), 6.5 + rng.uniform(0, .5)); spot(6.5 + rng.uniform(0, .5), rng.uniform(1.4, 5.6))

    ents.sort(key=lambda e: e[0])
    for key, sp, x, y in ents:
        img.alpha_composite(sp, (x, y))
    return img

# HUD
FONT = {
 'A': ['010','101','111','101','101'], 'D': ['110','101','101','101','110'], 'I': ['111','010','010','010','111'],
 'O': ['111','101','101','101','111'], 'R': ['110','101','110','101','101'], 'S': ['011','100','010','001','110'],
 'T': ['111','010','010','010','010'], 'V': ['101','101','101','101','010'], 'Y': ['101','101','010','010','010'],
 'Z': ['111','001','010','100','111'], ':': ['0','1','0','1','0'], ',': ['0','0','0','1','1'], ' ': ['00','00','00','00','00'],
 '0': ['111','101','101','101','111'], '1': ['010','110','010','010','111'], '2': ['110','001','010','100','111'],
 '3': ['110','001','010','001','110'], '4': ['101','101','111','001','001'], '5': ['111','100','110','001','110'],
 '6': ['011','100','111','101','111'], '7': ['111','001','010','010','010'], '8': ['111','101','111','101','111'],
 '9': ['111','101','111','001','110'],
}
def draw_text(d, cx, y, s, col, sc):
    w = sum((len(FONT.get(c, FONT[' '])[0]) + 1) * sc for c in s) - sc
    x = cx - w // 2
    for ch in s:
        gl = FONT.get(ch, FONT[' '])
        for yy, row in enumerate(gl):
            for xx, c in enumerate(row):
                if c == '1': d.rectangle([x + xx * sc, y + yy * sc, x + xx * sc + sc - 1, y + yy * sc + sc - 1], fill=col)
        x += (len(gl[0]) + 1) * sc

def hud(img, label_cols):
    d = ImageDraw.Draw(img); W = img.size[0]
    bg, fg, accent = [hx(c) for c in S['hud']]
    d.rectangle([W // 2 - 66, 6, W // 2 + 66, 52], fill=bg)
    d.rectangle([W // 2 - 66, 6, W // 2 + 66, 8], fill=accent)
    d.rectangle([W // 2 - 64, 10, W // 2 + 64, 50], fill=shade_col(bg, 1.0))
    d.rectangle([W // 2 - 66, 50, W // 2 + 66, 52], fill=accent) if False else None
    draw_text(d, W // 2, 13, 'TODAY:', fg, 1)
    draw_text(d, W // 2, 22, 'VISITORS', fg, 2)
    draw_text(d, W // 2, 36, '12,408', accent, 2)

def sheet():
    items = [house(1.6, 1.0, 16, 10, S['walls'][0], S['roofs'][0], windows=2, door=0.62, seed=1, chimney=True, flag=S['roofs'][1]),
             house(1.4, 1.0, 14, 9, S['walls'][1], S['roofs'][1], windows=2, awning=(S['roofs'][0], S['white']), seed=2),
             house(1.2, 1.0, 14, 9, S['walls'][3], S['roofs'][2], windows=1, awning=(S['roofs'][4], S['white']), seed=3, mirror=True),
             house(2.0, 1.4, 18, 12, S['walls'][3], S['roofs'][3], windows=0, big_door=True, seed=4, flag=S['roofs'][0]),
             tower(0.9, 34, S['roofs'][4], S['walls'][2], flag=S['roofs'][0]), dome(1.6), carousel(), igloo(), candy_cart()]
    W = sum(s[0].size[0] for s in items) + 8 * (len(items) + 1); H = max(s[0].size[1] for s in items) + 16
    sh = Image.new('RGBA', (W, H), S['grass'][0]); x = 8
    for sp, a in items:
        sh.alpha_composite(sp, (x, H - sp.size[1] - 6)); x += sp.size[0] + 8
    return sh

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'out'
    os.makedirs(out, exist_ok=True)
    only = sys.argv[2:] or list(STYLES)
    for name in only:
        load_style(name)
        sc = make_scene2()
        sc = tone(sc, S['sat'], S['bright'])
        hud(sc, None)
        sc.resize((sc.width * 3, sc.height * 3), Image.NEAREST).save(f'{out}/{name}_scene.png')
        sh = tone(sheet(), S['sat'], S['bright'])
        sh.resize((sh.width * 3, sh.height * 3), Image.NEAREST).save(f'{out}/{name}_buildings.png')
        print('ok', name)
