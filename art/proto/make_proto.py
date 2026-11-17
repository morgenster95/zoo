"""Proof of concept: světlý hravý izometrický pixel art ZOO (styl jako Kingsfollow, jen veselejší).
Kreslí se procedurálně v nativním rozlišení, pak se zvětší bez vyhlazení."""
import random, sys
from PIL import Image, ImageDraw

random.seed(7)
W, H = 420, 250
SCALE = 3
OX, OY = W // 2, 52           # střed horního rohu mapy
N = 13                         # mapa N x N dlaždic

def hx(s):
    s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)

C = dict(
    sky=hx('#cdeefb'),
    g1=hx('#8fd96b'), g2=hx('#80cf5f'), g3=hx('#a3e47e'), gd=hx('#6fbd52'),
    sand=hx('#f5e2ae'), sand2=hx('#ecd395'), sandd=hx('#d9bb78'),
    water=hx('#6fc9f2'), water2=hx('#9ee0fb'), waterd=hx('#4aa8dc'),
    ice=hx('#d6f3ff'), ice2=hx('#b4e4fa'),
    line=hx('#5b3f4a'),          # měkký tmavě švestkový obrys místo černé
    wood=hx('#d99a5b'), woodl=hx('#f0b977'), woodd=hx('#b87a45'),
    red=hx('#ef5b5b'), redd=hx('#c93f4a'), white=hx('#fff8ee'),
    leaf=hx('#4fbf5a'), leaf2=hx('#6fd66b'), leafd=hx('#3a9e4e'), trunk=hx('#a9714a'),
    pine=hx('#2fa86a'), pine2=hx('#46c07f'),
    skin1=hx('#ffd6b0'), skin2=hx('#e8a67a'), skin3=hx('#9a6a4a'),
    cream=hx('#fff3d6'), brown=hx('#6b4535'), gold=hx('#ffc93c'),
)
SHIRTS = [hx(x) for x in ['#ef5b5b', '#4aa8dc', '#ffc93c', '#b57bec', '#ff8fb8', '#52c78a', '#ff9a3c', '#ffffff']]
PANTS = [hx(x) for x in ['#5b6fb5', '#6b4535', '#3d4a6b', '#8a6bb5', '#c9a36b']]

img = Image.new('RGBA', (W, H), C['sky'])
d = ImageDraw.Draw(img)

def P(i, j):
    return OX + (i - j) * 16, OY + (i + j) * 8

def diamond(i, j, col, dr=d, w=1, h=1):
    x, y = P(i, j)
    pts = [(x, y), (x + 16 * w - 16 * 0 + 16 * (h - 1) * 0, y + 8 * w) if False else (x + 16 * w, y + 8 * w),
           (x + 16 * (w - h), y + 8 * (w + h)), (x - 16 * h, y + 8 * h)]
    dr.polygon(pts, fill=col)

# ---------- terén ----------
ground = [[None] * N for _ in range(N)]
mid = N // 2
for i in range(N):
    for j in range(N):
        r = random.random()
        ground[i][j] = C['g1'] if r < .55 else (C['g2'] if r < .8 else C['g3'])
# cesty (kříž + náměstí)
path = set()
for k in range(N):
    path.add((mid, k)); path.add((k, mid))
for i in range(mid - 1, mid + 2):
    for j in range(mid - 1, mid + 2):
        path.add((i, j))
# výběhy
ENC = {
    'slon':   (1, 1, 5, 5),
    'zirafa': (8, 1, 12, 5),
    'jezirko': (1, 8, 5, 12),
    'tucnaci': (8, 8, 12, 12),
}
for p in list(path):
    pass
for i in range(N):
    for j in range(N):
        if (i, j) in path:
            ground[i][j] = C['sand'] if (i + j) % 2 else C['sand2']
# jezírko a ledová plocha
pond = [(i, j) for i in range(2, 5) for j in range(9, 12)]
ice = [(i, j) for i in range(9, 12) for j in range(9, 12)]
for (i, j) in pond: ground[i][j] = C['water'] if (i + j) % 2 else C['water2']
for (i, j) in ice: ground[i][j] = C['ice'] if (i + j) % 2 else C['ice2']

for s in range(2 * N - 1):
    for i in range(N):
        j = s - i
        if 0 <= j < N:
            diamond(i, j, ground[i][j])
            x, y = P(i, j)
            # drobné trsy trávy / kamínky
            if ground[i][j] in (C['g1'], C['g2'], C['g3']):
                for _ in range(3):
                    px = x + random.randint(-12, 12); py = y + random.randint(3, 12)
                    if abs(px - x) / 2 + abs(py - (y + 8)) < 7:
                        d.point((px, py), fill=C['gd'])
                        if random.random() < .5: d.point((px, py - 1), fill=C['gd'])
            if ground[i][j] in (C['sand'], C['sand2']) and random.random() < .25:
                d.point((x + random.randint(-6, 6), y + 8 + random.randint(-3, 3)), fill=C['sandd'])
            if ground[i][j] in (C['water'], C['water2']) and random.random() < .5:
                d.line([(x - 4, y + 8), (x - 1, y + 8)], fill=C['water2'] if ground[i][j] == C['water'] else C['water'])

# ---------- sprity ----------
def outlined(sprite, col=None):
    """automatický obrys kolem silueta (4-okolí) + tvrdý spodní stín"""
    col = col or C['line']
    w, h = sprite.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    px = sprite.load(); op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                    op[x + 1 + dx, y + 1 + dy] = col if op[x + 1 + dx, y + 1 + dy][3] == 0 else op[x + 1 + dx, y + 1 + dy]
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                op[x + 1, y + 1] = px[x, y]
    return out

def new(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def shade(im, base, dark, light=None, frac=.5):
    """spodní polovina tvaru base tmavší, horní okraj světlejší"""
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
    for lx in (8, 13, 21, 26):  # nohy
        g.rectangle([lx, 18, lx + 3, 25], fill=grey)
        g.rectangle([lx, 24, lx + 3, 25], fill=dk)
    g.ellipse([7, 6, 29, 22], fill=grey)       # tělo
    g.ellipse([0, 5, 12, 17], fill=grey)       # hlava
    g.rectangle([1, 14, 4, 22], fill=grey)     # chobot
    g.rectangle([0, 20, 3, 23], fill=grey)
    g.ellipse([6, 8, 15, 20], fill=dk)         # ucho
    g.ellipse([7, 9, 13, 17], fill=hx('#f4aabd'))  # růžové ucho zevnitř
    g.line([(29, 12), (31, 20)], fill=dk)      # ocas
    g.point((31, 21), fill=C['brown'])
    shade(im, grey, dk, lt, .55)
    g.rectangle([3, 14, 4, 15], fill=C['white'])  # kel
    g.point((3, 10), fill=C['line']); g.point((4, 10), fill=C['line'])  # oko
    g.point((1, 13), fill=hx('#ff9bb0')); g.point((2, 13), fill=hx('#ff9bb0'))
    return outlined(im)

def giraffe():
    im, g = new(26, 42)
    y1, y2, sp = hx('#ffd35a'), hx('#f2b53c'), hx('#c97b3a')
    for lx in (6, 9, 15, 18):
        g.rectangle([lx, 24, lx + 1, 38], fill=y1)
        g.rectangle([lx, 36, lx + 1, 38], fill=C['brown'])
    g.ellipse([4, 17, 21, 29], fill=y1)
    g.polygon([(16, 21), (22, 21), (20, 6), (16, 6)], fill=y1)  # krk
    g.ellipse([15, 1, 25, 9], fill=y1)         # hlava
    g.rectangle([22, 5, 25, 8], fill=hx('#f8e0a6'))  # čumák
    g.line([(17, 0), (17, -1)], fill=C['brown']); g.line([(20, 0), (20, 0)], fill=C['brown'])
    g.line([(4, 20), (2, 27)], fill=C['brown'])  # ocas
    shade(im, y1, y2, None, .6)
    for (sx, sy) in [(8, 20), (13, 23), (17, 19), (10, 26), (18, 14), (18, 9), (6, 24)]:
        g.rectangle([sx, sy, sx + 1, sy + 1], fill=sp)
    g.point((20, 3), fill=C['line'])
    return outlined(im)

def zebra():
    im, g = new(26, 22)
    w, k = hx('#fffaf0'), hx('#4b4560')
    for lx in (6, 9, 16, 19):
        g.rectangle([lx, 13, lx + 1, 19], fill=w); g.rectangle([lx, 18, lx + 1, 19], fill=k)
    g.ellipse([4, 6, 20, 16], fill=w)
    g.polygon([(17, 8), (21, 3), (24, 5), (21, 10)], fill=w)
    g.ellipse([19, 2, 25, 8], fill=w)
    g.rectangle([22, 6, 25, 8], fill=hx('#7a7390'))
    g.line([(3, 8), (1, 15)], fill=k)
    for x in range(6, 18, 3): g.line([(x, 7), (x - 1, 14)], fill=k)
    g.line([(19, 4), (22, 3)], fill=k)
    g.point((22, 4), fill=C['line'])
    return outlined(im)

def flamingo():
    im, g = new(14, 26)
    p, pd = hx('#ff9bbd'), hx('#f2709f')
    g.line([(6, 25), (6, 15)], fill=hx('#ff7aa5'))
    g.ellipse([2, 9, 11, 17], fill=p)
    g.line([(9, 10), (10, 6)], fill=p, width=2)
    g.ellipse([8, 2, 12, 6], fill=p)
    g.rectangle([12, 4, 13, 5], fill=C['line'])
    g.ellipse([3, 12, 8, 17], fill=pd)
    g.point((10, 3), fill=C['line'])
    return outlined(im)

def penguin():
    im, g = new(10, 14)
    k, w = hx('#46506e'), C['white']
    g.ellipse([1, 1, 8, 12], fill=k)
    g.ellipse([2, 4, 7, 12], fill=w)
    g.rectangle([3, 12, 4, 12], fill=hx('#ffa23c')); g.rectangle([6, 12, 7, 12], fill=hx('#ffa23c'))
    g.rectangle([4, 3, 6, 4], fill=hx('#ffa23c'))
    g.point((3, 2), fill=C['white']); g.point((6, 2), fill=C['white'])
    return outlined(im)

def tree_round(sz=1.0):
    im, g = new(26, 34)
    g.rectangle([11, 22, 14, 31], fill=C['trunk'])
    g.ellipse([2, 3, 24, 26], fill=C['leaf'])
    g.ellipse([5, 4, 17, 14], fill=C['leaf2'])
    g.ellipse([14, 12, 23, 24], fill=C['leafd'])
    for (x, y) in [(18, 8), (6, 16), (13, 18)]: g.point((x, y), fill=C['red'])
    return outlined(im)

def tree_pine():
    im, g = new(20, 34)
    g.rectangle([8, 27, 11, 32], fill=C['trunk'])
    for k, (yy, ww) in enumerate([(2, 5), (9, 7), (16, 9)]):
        g.polygon([(10, yy), (10 + ww, yy + 12), (10 - ww, yy + 12)], fill=C['pine'])
        g.polygon([(10, yy), (10 + ww, yy + 12), (10, yy + 12)], fill=hx('#269a5c'))
    return outlined(im)

def bush():
    im, g = new(14, 9)
    g.ellipse([0, 2, 13, 8], fill=C['leaf']); g.ellipse([2, 0, 10, 5], fill=C['leaf2'])
    for (x, y) in [(3, 4), (9, 5), (6, 2)]: g.point((x, y), fill=hx('#ff8fb8'))
    return outlined(im)

def person(shirt, pants, skin, kid=False, hair=None, balloon=None, hat=None):
    h = 9 if not kid else 7
    im, g = new(8, h + (14 if balloon else 0))
    oy = 14 if balloon else 0
    hair = hair or random.choice([hx('#5b3a2e'), hx('#2e2a3a'), hx('#e8b04a'), hx('#c9602e'), hx('#8a5a3a')])
    if not kid:
        g.rectangle([2, oy + 0, 5, oy + 2], fill=skin)
        g.rectangle([2, oy + 0, 5, oy + 0], fill=hair)
        g.rectangle([1, oy + 3, 6, oy + 6], fill=shirt)
        g.rectangle([2, oy + 7, 3, oy + 8], fill=pants); g.rectangle([4, oy + 7, 5, oy + 8], fill=pants)
        g.point((1, oy + 3), fill=skin) if False else None
    else:
        g.rectangle([2, oy + 0, 5, oy + 2], fill=skin); g.rectangle([2, oy + 0, 5, oy + 0], fill=hair)
        g.rectangle([2, oy + 3, 5, oy + 5], fill=shirt)
        g.rectangle([2, oy + 6, 3, oy + 6], fill=pants); g.rectangle([4, oy + 6, 5, oy + 6], fill=pants)
    if hat:
        g.rectangle([1, oy - 0, 6, oy + 0], fill=hat)
    if balloon:
        g.ellipse([0, 0, 6, 7], fill=balloon)
        g.point((2, 2), fill=C['white'])
        g.line([(3, 8), (3, oy + 3)], fill=C['line'])
    return outlined(im)

def booth():
    im, g = new(34, 40)
    g.rectangle([4, 18, 29, 36], fill=hx('#fff0c9'))
    g.rectangle([4, 30, 29, 36], fill=hx('#f6d98f'))
    g.rectangle([10, 22, 23, 29], fill=hx('#5a3d52'))
    g.rectangle([8, 29, 25, 31], fill=C['wood'])
    # pruhovaná stříška
    for k in range(8):
        col = C['red'] if k % 2 == 0 else C['white']
        g.polygon([(1 + k * 4, 18), (5 + k * 4, 18), (6 + k * 4 - 3 + 2, 10), (4 + k * 4 - 3 + 2, 10)], fill=col) if False else None
    g.polygon([(0, 18), (33, 18), (28, 8), (5, 8)], fill=C['white'])
    for k in range(0, 34, 8):
        g.polygon([(k, 18), (min(k + 4, 33), 18), (min(5 + k * 23 / 33 + 2, 28), 8), (5 + k * 23 / 33 - 2 + 2 if False else 5 + k * 23 / 33, 8)], fill=C['red'])
    g.polygon([(17, 1), (21, 8), (13, 8)], fill=C['red'])
    g.line([(17, 1), (17, -1)], fill=C['brown'])
    g.rectangle([17, -1, 22, 1], fill=C['gold'])
    return outlined(im)

def candy_stand():
    im, g = new(20, 26)
    g.rectangle([3, 14, 16, 24], fill=hx('#ffd6e8')); g.rectangle([3, 20, 16, 24], fill=hx('#ffb3d4'))
    g.polygon([(0, 14), (19, 14), (16, 6), (3, 6)], fill=hx('#7fd6f2'))
    g.polygon([(0, 14), (6, 14), (7, 6), (3, 6)], fill=C['white']); g.polygon([(13, 14), (19, 14), (16, 6), (12, 6)], fill=C['white'])
    g.ellipse([7, 0, 12, 5], fill=hx('#ff8fd0')); g.rectangle([9, 5, 10, 8], fill=C['woodl'])
    g.rectangle([6, 16, 13, 19], fill=hx('#7a5a7a'))
    return outlined(im)

def gate():
    im, g = new(76, 56)
    for px in (2, 62):
        g.rectangle([px, 12, px + 10, 52], fill=C['woodl']); g.rectangle([px + 6, 12, px + 10, 52], fill=C['wood'])
        g.rectangle([px - 1, 8, px + 11, 13], fill=C['red'])
    g.rectangle([8, 4, 66, 20], fill=C['cream']); g.rectangle([8, 16, 66, 20], fill=hx('#f6d98f'))
    g.rectangle([6, 2, 68, 5], fill=C['red'])
    for k in range(7, 68, 8): g.rectangle([k, 2, k + 3, 5], fill=C['white'])
    # nápis ZOO
    gl = {'Z': ['111', '001', '010', '100', '111'], 'O': ['111', '101', '101', '101', '111']}
    x = 22
    for ch in 'ZOO':
        for yy, row in enumerate(gl[ch]):
            for xx, c in enumerate(row):
                if c == '1': g.rectangle([x + xx * 3, 7 + yy * 2 + 0, x + xx * 3 + 2, 7 + yy * 2 + 1], fill=hx('#ef5b5b') if ch == 'Z' else hx('#4aa8dc'))
        x += 13
    # vlajky
    g.line([(7, 3), (7, -0)], fill=C['brown'])
    return outlined(im)

def balloon_bunch():
    im, g = new(12, 24)
    for (x, y, c) in [(1, 1, '#ef5b5b'), (6, 0, '#ffc93c'), (4, 5, '#4aa8dc')]:
        g.ellipse([x, y, x + 5, y + 7], fill=hx(c)); g.point((x + 1, y + 2), fill=C['white'])
    g.line([(3, 12), (6, 23)], fill=C['line']); g.line([(8, 8), (6, 23)], fill=C['line']); g.line([(6, 13), (6, 23)], fill=C['line'])
    return outlined(im)

def bench():
    im, g = new(16, 10)
    g.rectangle([0, 3, 15, 5], fill=C['woodl']); g.rectangle([1, 0, 14, 2], fill=C['wood'])
    g.rectangle([1, 6, 2, 9], fill=C['woodd']); g.rectangle([13, 6, 14, 9], fill=C['woodd'])
    return outlined(im)

def flowers():
    im, g = new(10, 6)
    for (x, y, c) in [(1, 2, '#ff8fb8'), (4, 1, '#ffc93c'), (7, 3, '#ffffff'), (3, 4, '#b57bec')]:
        g.point((x, y), fill=hx(c)); g.point((x, y + 1), fill=C['leafd'])
    return im

# ---------- entity (depth sort) ----------
ents = []
def put(sp, i, j, key_off=0.0, dx=0, dy=0):
    x, y = P(i, j)
    ents.append((i + j + key_off, sp, int(x - sp.size[0] // 2 + dx), int(y - sp.size[1] + 1 + dy)))

def fence_post(i, j):
    im, g = new(5, 12)
    g.rectangle([1, 2, 3, 10], fill=C['woodl']); g.rectangle([3, 2, 3, 10], fill=C['wood'])
    g.rectangle([0, 1, 4, 2], fill=hx('#fff0c9'))
    return outlined(im)
FP = fence_post(0, 0)

def fence_rect(i0, j0, i1, j1, gate_side=None):
    # sloupky po obvodu + laťky mezi nimi
    pts = []
    for i in range(i0, i1 + 1): pts += [(i, j0), (i, j1)]
    for j in range(j0 + 1, j1): pts += [(i0, j), (i1, j)]
    segs = []
    for i in range(i0, i1): segs += [((i, j0), (i + 1, j0)), ((i, j1), (i + 1, j1))]
    for j in range(j0, j1): segs += [((i0, j), (i0, j + 1)), ((i1, j), (i1, j + 1))]
    for (a, b) in segs:
        if gate_side and a[1] == j1 and b[1] == j1 and a[0] == gate_side:  # branka = mezera
            continue
        xa, ya = P(*a); xb, yb = P(*b)
        key = (a[0] + a[1] + b[0] + b[1]) / 2 + .2
        im = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); gg = ImageDraw.Draw(im)
        ox = 20; oy = 14
        ax, ay = ox, oy; bx, by = ox + (xb - xa), oy + (yb - ya)
        for lift, col in ((9, C['woodl']), (5, C['wood'])):
            gg.line([(ax, ay - lift), (bx, by - lift)], fill=col); gg.line([(ax, ay - lift + 1), (bx, by - lift + 1)], fill=C['woodd'])
        ents.append((key, outlined(im), int(xa - 20 - 1), int(ya - 14 - 1)))
    for (i, j) in set(pts):
        if gate_side and j == j1 and i == gate_side: pass
        put(FP, i, j, .3, dy=0)

fence_rect(1, 1, 6, 6, gate_side=None)
fence_rect(8, 1, 12, 6)
fence_rect(1, 8, 6, 12)
fence_rect(8, 8, 12, 12)

# zvířata
put(elephant(), 3, 3, 0.1, dx=-2)
put(elephant(), 4.3, 4.6, 0.1, dx=2)
put(giraffe(), 10, 3, 0.1)
put(giraffe(), 9.2, 4.6, 0.1, dx=-1)
put(zebra(), 11, 4.8, 0.1)
for (i, j) in [(3.2, 10), (4.6, 9.4), (2.4, 11)]:
    put(flamingo(), i, j, 0.1)
for (i, j) in [(9.5, 9.5), (10.5, 10), (11, 9.2), (10, 11), (11.3, 11)]:
    put(penguin(), i, j, 0.1)

# stromy a keře
trs = [(0, 6.5), (0, 4), (0.5, 9.5), (6.5, 0), (7, 12.5), (12.8, 7), (12.7, 12.5), (6.5, 6.5 + 0.0) , (0, 12.3), (12.8, 0.4), (7.2, 0.3)]
for k, (i, j) in enumerate(trs):
    if (i, j) == (6.5, 6.5): continue
    put(tree_pine() if k % 3 == 0 else tree_round(), i, j, 0.2)
for (i, j) in [(0.4, 7.7), (7.6, 4.4), (5.8, 7.4), (7.6, 9.6), (6.4, 4), (12.6, 5.4), (4.6, 6.8), (8.0, 7.2)]:
    put(bush(), i, j, 0.2)
for (i, j) in [(0.6, 0.6), (6.5, 7.0), (7.4, 7.2), (0.5, 12.7), (12.4, 6.8), (7.6, 6)]:
    put(flowers(), i, j, 0.05)

# středové náměstí: kasa, cukrová vata, lavičky, balónky, brána
put(booth(), 6.6, 5.6, 0.4)
put(candy_stand(), 7.5, 7.6, 0.4)
put(bench(), 5.2, 7.6, 0.3); put(bench(), 7.5, 5.2, 0.3)
put(balloon_bunch(), 5.4, 6.6, 0.5)
put(gate(), 13.4, 6.6, 0.6)

# návštěvníci
pal = list(zip(SHIRTS * 3, PANTS * 5))
skins = [C['skin1'], C['skin2'], C['skin3']]
def spot(i, j, **kw):
    s = random.choice(SHIRTS); pn = random.choice(PANTS)
    put(person(s, pn, random.choice(skins), **kw), i + random.uniform(-.15, .15), j + random.uniform(-.15, .15), 0.45)

for k in range(34):   # lidé na cestách
    if random.random() < .5: i, j = mid + random.uniform(-.4, .4), random.uniform(.5, N - .5)
    else: i, j = random.uniform(.5, N - .5), mid + random.uniform(-.4, .4)
    if 4 < i < 9 and 4 < j < 9 and random.random() < .5: continue
    kw = {}
    r = random.random()
    if r < .25: kw['kid'] = True
    elif r < .35: kw['balloon'] = random.choice(SHIRTS[:6])
    elif r < .42: kw['hat'] = random.choice(SHIRTS[:6])
    spot(i, j, **kw)
for (i, j) in [(6.3, 12.2), (6.8, 12.4), (6.0, 11.8), (7.1, 11.6), (6.5, 11.2)]:
    spot(i, j, kid=random.random() < .4)
for (i, j) in [(6.2, 6.0), (6.9, 6.3), (5.9, 6.8), (7.1, 6.9), (6.4, 7.2)]:
    spot(i, j, kid=random.random() < .3)

ents.sort(key=lambda e: e[0])
for key, sp, x, y in ents:
    img.alpha_composite(sp, (x, y))

# ---------- HUD (světlý, hravý) ----------
FONT = {
 'A': ['010','101','111','101','101'], 'D': ['110','101','101','101','110'], 'I': ['111','010','010','010','111'],
 'O': ['111','101','101','101','111'], 'R': ['110','101','110','101','101'], 'S': ['011','100','010','001','110'],
 'T': ['111','010','010','010','010'], 'V': ['101','101','101','101','010'], 'Y': ['101','101','010','010','010'],
 'Z': ['111','001','010','100','111'], ':': ['0','1','0','1','0'], ',': ['0','0','0','1','1'], ' ': ['00','00','00','00','00'],
 '0': ['111','101','101','101','111'], '1': ['010','110','010','010','111'], '2': ['110','001','010','100','111'],
 '3': ['110','001','010','001','110'], '4': ['101','101','111','001','001'], '5': ['111','100','110','001','110'],
 '6': ['011','100','111','101','111'], '7': ['111','001','010','010','010'], '8': ['111','101','111','101','111'],
 '9': ['111','101','111','001','110'], 'E': ['111','100','110','100','111'], 'N': ['110','101','101','101','101'],
}
def text(dr, x, y, s, col, sc=1, shadow=None):
    cx = x
    for ch in s:
        gl = FONT.get(ch, FONT[' '])
        for yy, row in enumerate(gl):
            for xx, c in enumerate(row):
                if c == '1':
                    if shadow: dr.rectangle([cx + xx * sc, y + yy * sc + sc, cx + xx * sc + sc - 1, y + yy * sc + 2 * sc - 1], fill=shadow)
        for yy, row in enumerate(gl):
            for xx, c in enumerate(row):
                if c == '1': dr.rectangle([cx + xx * sc, y + yy * sc, cx + xx * sc + sc - 1, y + yy * sc + sc - 1], fill=col)
        cx += (len(gl[0]) + 1) * sc
    return cx - x

def panel(x0, y0, x1, y1):
    d.rectangle([x0, y0 + 2, x1, y1], fill=C['line'])
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=C['cream'])
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + 2], fill=C['gold'])
    d.rectangle([x0 + 1, y1 - 3, x1 - 1, y1 - 1], fill=hx('#f6d98f'))
panel(W // 2 - 62, 6, W // 2 + 62, 52)
def ctext(y, s, col, sc):
    w = sum((len(FONT.get(c, FONT[' '])[0]) + 1) * sc for c in s) - sc
    text(d, W // 2 - w // 2, y, s, col, sc)
ctext(12, 'TODAY:', C['brown'], 1)
ctext(21, 'VISITORS', hx('#ef5b5b'), 2)
ctext(35, '12,408', hx('#4aa8dc'), 2)

out = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
out.save(sys.argv[1] if len(sys.argv) > 1 else 'zoo_proto.png')

# arch spritů pro kontrolu
sheet = Image.new('RGBA', (360, 120), hx('#a3e47e'))
x = 4
for sp in [elephant(), giraffe(), zebra(), flamingo(), penguin(), tree_round(), tree_pine(), booth(), candy_stand(), balloon_bunch(), person(SHIRTS[0], PANTS[0], C['skin1']), person(SHIRTS[1], PANTS[1], C['skin2'], kid=True), person(SHIRTS[3], PANTS[2], C['skin3'], balloon=SHIRTS[0])]:
    sheet.alpha_composite(sp, (x, 4)); x += sp.size[0] + 6
sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save((sys.argv[1] if len(sys.argv) > 1 else 'zoo_proto.png').replace('.png', '_sheet.png'))
