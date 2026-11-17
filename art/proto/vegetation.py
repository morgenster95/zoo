"""ZOO: vegetace v2. Stromy a keře s objemem (renderer z painted.py): kupy listí se stínováním, vnitřní obrysy mezi kupami,
kůra, stín na zemi, tropické a savanové druhy pro rodiny výběhů.
Použití: python vegetation.py <výstupní složka>   (arch vegetace + srovnání se starými stromy)"""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw
import painted as pt
from painted import Paint, make_ramp, hx

SHADOW = (30, 80, 40, 120)

def finish(p, shadow=None):
    im = p.render()
    if shadow:
        cx, cy, rx, ry = shadow
        full = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(full).ellipse([cx - rx + 1, cy - ry + 1, cx + rx + 1, cy + ry + 1], fill=SHADOW)
        full.alpha_composite(im); im = full
    return im

def speckle(p, pts, color, rng, n=10, box=None):
    """světlé tečky listí v levé horní části (dojem jednotlivých listů)"""
    for _ in range(n):
        x, y = rng.choice(pts)
        p.dot(x + rng.randint(-2, 1), y + rng.randint(-3, 0), color)

def puffs(p, centers, base, rng, edge=True, light=None, fur=0.06):
    """kupy listí (zadní nahoře, přední dole); každá kupa má vlastní objem a vnitřní obrys"""
    ramp = make_ramp(base)
    for (cx, cy, rx, ry) in centers:
        p.ellipse(cx, cy, rx, ry, base, ramp=ramp, edge=edge, bump=.15, fur=fur)
    return ramp

def oak(seed=1, base='#58b84a'):
    rng = random.Random(seed)
    p = Paint(36, 44, seed)
    trunk = '#8a5a3a'
    p.region([(15, 24), (21, 24), (22, 36), (24, 40), (12, 40), (14, 36)], trunk, fur=.05)
    p.region([(15, 26), (17, 26), (17, 38), (15, 38)], '#a87048', fur=.03)
    cs = [(18, 11, 8, 7), (10, 17, 8, 7), (26, 17, 8, 7), (18, 19, 11, 8), (8, 24, 6, 5), (28, 24, 6, 5), (18, 26, 8, 5)]
    if seed % 2: cs = [(17, 10, 8, 7), (26, 14, 8, 7), (9, 16, 8, 7), (18, 19, 10, 8), (27, 24, 6, 5), (9, 24, 6, 5)]
    puffs(p, cs, base, rng)
    ramp = make_ramp(base)
    speckle(p, [(c[0] - c[2] // 2, c[1] - c[3] // 2) for c in cs], ramp[5], rng, 16)
    for (x, y) in [(12, 21), (22, 14), (25, 23)]:
        if seed == 3: p.dot(x, y, '#ff6a6a')
    return finish(p, (18, 40, 11, 3))

def pine(seed=1):
    rng = random.Random(seed)
    p = Paint(30, 46, seed)
    p.region([(13, 36), (17, 36), (17, 43), (13, 43)], '#7a4a2e', fur=.04)
    for k, (y, w) in enumerate([(24, 12), (15, 10), (7, 8)]):
        p.region([(15, y - 14 + 2), (15 + w, y + 6), (15 - w, y + 6)], '#2e9a5a' if k != 1 else '#33a560', edge=True, bump=.12, fur=.07)
    p.region([(15, 1), (18, 9), (12, 9)], '#3aae68', edge=True, bump=.12, fur=.07)
    return finish(p, (15, 43, 9, 2))

def birch(seed=1):
    rng = random.Random(seed)
    p = Paint(30, 44, seed)
    p.region([(14, 20), (17, 20), (18, 41), (13, 41)], '#ece6dc', fur=.03)
    for yy in (24, 28, 32, 36):
        p.pattern(lambda d, yy=yy: d.rectangle([13, yy, 15 + (yy % 3), yy + 1], fill=255), '#4a4048')
    cs = [(15, 9, 6, 6), (8, 14, 6, 6), (22, 14, 6, 6), (15, 16, 8, 7), (9, 21, 4, 4), (21, 21, 4, 4)]
    puffs(p, cs, '#8fd060', rng)
    return finish(p, (15, 41, 9, 2))

def palm(seed=1):
    rng = random.Random(seed)
    p = Paint(44, 48, seed)
    p.region([(20, 18), (23, 18), (25, 30), (26, 43), (21, 43), (20, 32)], '#a8784a', fur=.05)
    for yy in range(22, 42, 4):
        p.pattern(lambda d, yy=yy: d.line([(19, yy), (27, yy + 1)], fill=255), '#7a5030')
    leaf = '#3fa84a'
    fronds = [(-1, -4, 15), (-1, 0, 16), (-1, 4, 14), (1, -4, 15), (1, 0, 16), (1, 4, 14), (0, -6, 6)]
    for (sgn, dy, ln) in fronds:
        x0, y0 = 22, 16
        pts = [(x0, y0), (x0 + sgn * ln * 0.5, y0 - 5 + dy * 0.4), (x0 + sgn * ln, y0 + 2 + dy), (x0 + sgn * ln * 0.55, y0 - 1 + dy * 0.3)]
        p.region(pts, leaf, edge=True, bump=.05, fur=.05)
    p.region([(20, 15), (24, 15), (24, 19), (20, 19)], '#3aa045', edge=True)
    p.ellipse(21, 19, 1.6, 1.6, '#7a5030'); p.ellipse(24, 19, 1.6, 1.6, '#7a5030')
    return finish(p, (22, 44, 10, 2))

def acacia(seed=1):
    rng = random.Random(seed)
    p = Paint(50, 38, seed)
    p.region([(24, 18), (27, 18), (28, 34), (30, 36), (22, 36), (24, 34)], '#7a5030', fur=.05)
    p.region([(24, 22), (14, 14), (15, 12), (26, 19)], '#7a5030', fur=.05)
    p.region([(26, 22), (36, 14), (35, 12), (25, 19)], '#7a5030', fur=.05)
    for (cx, cy, rx, ry) in [(25, 10, 20, 5), (12, 12, 9, 4), (38, 12, 9, 4), (25, 14, 14, 4)]:
        p.ellipse(cx, cy, rx, ry, '#7fb84a', edge=True, bump=.12, fur=.07)
    return finish(p, (26, 36, 12, 2))

def baobab(seed=1):
    rng = random.Random(seed)
    p = Paint(46, 54, seed)
    p.region([(14, 52), (18, 36), (17, 22), (21, 14), (29, 14), (33, 22), (32, 36), (36, 52)], '#9a7a5a', fur=.07, bump=.25)
    for (x, y) in [(20, 30), (28, 26), (24, 40), (18, 46), (30, 44)]:
        p.pattern(lambda d, x=x, y=y: d.line([(x, y), (x + 1, y + 6)], fill=255), '#6a4e38')
    for (x0, y0, x1, y1) in [(21, 14, 12, 7), (29, 14, 36, 7), (25, 14, 25, 5)]:
        p.region([(x0 - 1, y0), (x0 + 1, y0), (x1 + 1, y1), (x1 - 1, y1)], '#7a5a3a', fur=.04)
    for (cx, cy, rx, ry) in [(12, 6, 6, 4), (36, 6, 6, 4), (25, 4, 7, 4)]:
        p.ellipse(cx, cy, rx, ry, '#5fb04a', edge=True, bump=.12)
    return finish(p, (25, 52, 14, 2))

def bamboo(seed=1):
    rng = random.Random(seed)
    p = Paint(34, 48, seed)
    xs = [8, 13, 18, 23, 27]
    for k, x in enumerate(xs):
        top = 4 + (k * 7) % 10
        p.region([(x, top), (x + 3, top), (x + 3, 44), (x, 44)], '#78b848' if k % 2 else '#68a83c', edge=(k > 0), bump=.06, fur=.04)
        for yy in range(top + 6, 44, 8):
            p.pattern(lambda d, x=x, yy=yy: d.rectangle([x, yy, x + 3, yy], fill=255), '#3e7a2c')
        for (dx, dy) in [(-4, top + 5), (4, top + 12)]:
            sgn = 1 if dx > 0 else -1
            p.region([(x + 1, dy), (x + 1 + sgn * 7, dy - 3), (x + 1 + sgn * 6, dy + 1)], '#58c050', edge=True)
    return finish(p, (18, 44, 13, 2))

def cherry(seed=1):
    rng = random.Random(seed)
    p = Paint(40, 44, seed)
    p.region([(17, 24), (22, 24), (23, 37), (25, 41), (14, 41), (16, 37)], '#7a5240', fur=.05)
    p.region([(18, 26), (11, 17), (13, 16), (19, 23)], '#7a5240', fur=.04)
    p.region([(21, 26), (29, 17), (27, 16), (20, 23)], '#7a5240', fur=.04)
    cs = [(20, 11, 9, 7), (10, 16, 8, 6), (30, 16, 8, 6), (20, 19, 11, 7), (11, 23, 6, 4), (29, 23, 6, 4)]
    puffs(p, cs, '#f4a0c0', rng, fur=.08)
    for (x, y) in [(8, 29), (33, 31), (15, 34), (26, 33)]: p.dot(x, y, '#ffd0e0')
    return finish(p, (20, 41, 11, 3))

def bush(seed=1, base='#4fb04a', berries=None):
    rng = random.Random(seed)
    p = Paint(22, 14, seed)
    puffs(p, [(8, 7, 7, 5), (15, 7, 6, 5), (11, 5, 6, 4)], base, rng)
    for (x, y) in (berries or []): p.dot(x, y, '#ff6a8a')
    return finish(p, (11, 12, 8, 1))

def flowers(seed=1):
    rng = random.Random(seed)
    im = Image.new('RGBA', (16, 8), (0, 0, 0, 0))
    px = im.load()
    for _ in range(7):
        x, y = rng.randint(1, 14), rng.randint(2, 6)
        px[x, y] = (70, 150, 60, 255); px[x, y - 1] = rng.choice([(255, 120, 150, 255), (255, 210, 70, 255), (255, 255, 255, 255), (180, 130, 240, 255)])
    return im

def reeds(seed=1):
    p = Paint(18, 24, seed)
    for k, x in enumerate([3, 7, 11, 14]):
        top = 3 + (k * 5) % 9
        p.region([(x, top + 6), (x + 1.6, top + 6), (x + 1.6, 22), (x, 22)], '#6aa84a', fur=.03)
        if k % 2 == 0: p.region([(x - .6, top), (x + 2.2, top), (x + 2.2, top + 7), (x - .6, top + 7)], '#8a5a3a', fur=.03)
    return finish(p)

def tuft(seed=1):
    p = Paint(14, 9, seed)
    for k, x in enumerate([2, 5, 8, 11]):
        p.region([(x, 8 - (k % 2) * 2), (x + 1.8, 8 - (k % 2) * 2), (x + 3, 1 + k % 3), (x + 1, 1 + k % 3)], '#5cb048' if k % 2 else '#74c458', fur=.03)
    return finish(p)

ALL = [('oak1', lambda: oak(1)), ('oak2', lambda: oak(2)), ('oak3', lambda: oak(3, '#6cc24e')), ('pine1', lambda: pine(1)), ('birch', birch),
       ('palm', palm), ('acacia', acacia), ('baobab', baobab), ('bamboo', bamboo), ('cherry', cherry),
       ('bush1', lambda: bush(1)), ('bush2', lambda: bush(2, '#5cb858', [(6, 5), (14, 6), (10, 3)])), ('flowers', flowers), ('reeds', reeds), ('tuft', tuft)]

def sheet(out, scale=5):
    import zoo_art as za, visitors, animals
    za.load_style('C_hybrid')
    ims = [(n, f()) for n, f in ALL]
    old = [za.tree_round(), za.tree_pine(), za.bush()]
    person = visitors.visitor(visitors.new_spec(11), 'SE', 0)
    pad = 8
    items = [('old', o) for o in old] + [('person', person)] + ims
    W = sum(i.width + pad for _, i in items) + pad
    H = max(i.height for _, i in items) + pad * 2
    cols = 2
    sh = Image.new('RGBA', (W, H), za.S['grass'][0])
    px = sh.load(); rng = random.Random(1)
    for y in range(H):
        for x in range(W):
            if rng.random() < .3: px[x, y] = rng.choice(za.S['grass'])
    x = pad
    for n, im in items:
        sh.alpha_composite(im, (x, H - im.height - pad)); x += im.width + pad
    sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST).save(f'{out}/vegetation_sheet.png')
    # řádky po 8 pro čitelnost
    return sh

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'veg_out'
    os.makedirs(out, exist_ok=True)
    sheet(out); print('ok')
