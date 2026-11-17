"""ZOO: návštěvníci v2. Generátor postaviček s chůzí a 4 izometrickými směry.
- chibi proporce: dospělý 7×10 px (hlava 4 řádky), dítě 5×8, kolem selektivní obrys
- 4 směry: SE, SW (obličejem k nám), NE, NW (zády); levý/pravý = zrcadlo
- chůze: 4 snímky (stoj, levá noha, stoj, pravá noha) + houpání rukou
- typy: rodič s kočárkem, školák s batohem, fotograf, prodavač/držitel balónků, turista s mapou, dědeček s holí, dítě se zmrzlinou, podporovatel (hvězda)
- vzhled se skládá z: pleť (6), účes (7), barva vlasů, oblečení (triko/šaty/kalhoty/sukně), doplňky
Použití: python visitors.py <výstupní složka>  → galerie typů, GIF s chodícími návštěvníky, scéna"""
import random, sys, os
from PIL import Image, ImageDraw, ImageFont
import zoo_art as za
from zoo_art import hx, shade_col

SKINS = [hx(x) for x in ['#ffdcc0', '#f5c29a', '#e0a070', '#c48458', '#9a6240', '#6b432c']]
HAIRS = [hx(x) for x in ['#2e2a3a', '#4a3226', '#7a4a2c', '#b8742e', '#e8c05a', '#c8452e', '#8a8a96', '#f0f0f0']]
STYLES_H = ['short', 'short', 'long', 'ponytail', 'curly', 'bun', 'bald', 'side']
SHIRTS = [hx(x) for x in ['#e0503e', '#5b9bd8', '#f2b53c', '#8a5fc9', '#ff8fb8', '#46b88a', '#f08a30', '#f4f1ea', '#3fb5b5', '#a8d65a']]
PANTS = [hx(x) for x in ['#3f4f80', '#5a3d30', '#3d4a5b', '#6f5a8a', '#b79a6a', '#2f3a55', '#7a8a9a']]
BAL = [hx(x) for x in ['#ef5b5b', '#ffc93c', '#4aa8dc', '#ff8fb8', '#8a5fc9', '#52c78a']]
TYPES = ['plain', 'family', 'schoolkid', 'photographer', 'balloon', 'tourist', 'grandpa', 'icecream', 'supporter', 'plush', 'sitting']
DIRS = ['SE', 'SW', 'NE', 'NW']
W, H = 15, 34          # plátno: osoba x=4..10, balíky nahoře, kočárek vedle
OX = 4

def new_spec(seed, kind=None, kid=None):
    r = random.Random(seed)
    kind = kind or r.choice(['plain'] * 6 + TYPES[1:])
    s = dict(kind=kind, skin=r.choice(SKINS), hair=r.choice(HAIRS), hstyle=r.choice(STYLES_H),
             shirt=r.choice(SHIRTS), pants=r.choice(PANTS), dress=r.random() < .3, shoes=hx('#3a2a32'),
             kid=(r.random() < .22) if kid is None else kid, glasses=(r.random() < .12), hood=(r.random() < .12), plush=None, sit=False, hat=None, acc=None, balloon=None, star=False, stroller=False, seed=seed)
    if kind == 'schoolkid': s.update(kid=True, acc='backpack')
    elif kind == 'photographer': s.update(kid=False, acc='camera', hat=r.choice(SHIRTS), shirt=hx('#c9b27a'), pants=hx('#4a5a4a'))
    elif kind == 'balloon': s.update(balloon=[r.choice(BAL) for _ in range(r.choice([1, 2, 3]))])
    elif kind == 'tourist': s.update(kid=False, acc='map', hat=hx('#f2d58a'), shirt=r.choice([hx('#3fb5b5'), hx('#ff8fb8'), hx('#f08a30')]))
    elif kind == 'grandpa': s.update(kid=False, acc='cane', hair=hx('#d8d8e0'), hstyle=r.choice(['short', 'bald', 'side']), shirt=r.choice([hx('#8aa0c8'), hx('#b89a8a'), hx('#9ab08a')]), pants=hx('#6a6a7a'))
    elif kind == 'icecream': s.update(kid=True, acc='icecream')
    elif kind == 'supporter': s.update(star=True, kid=False)
    elif kind == 'plush': s.update(kid=True, plush=r.choice([hx('#c68a5a'), hx('#ff9bbd'), hx('#9ec8f0'), hx('#f2d58a')]))
    elif kind == 'sitting': s.update(sit=True, kid=False)
    elif kind == 'family': s.update(kid=False, stroller=True, dress=r.random() < .5)
    if s['kid'] and kind == 'plain': s['hstyle'] = r.choice(['short', 'ponytail', 'curly', 'bun'])
    return s

def draw_person(spec, view, frame):
    """kreslí osobu do plátna W×H bez převrácení; view = 'front' | 'back'; chůze frame 0..3"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = im.load()
    kid = spec['kid']
    def P(x, y, c, shade=True):
        X, Y = x + OX, y
        if 0 <= X < W and 0 <= Y < H:
            px[X, Y] = shade_col(c, .84) if shade and x >= 5 else c
    bot = H - 1
    legh = 2 if not kid else 1
    if spec['sit']: legh = 1
    bodyh = 3 if not kid else 2
    headh = 4 if not kid else 3
    total = headh + bodyh + legh + 1       # + bota
    Y0 = bot - total + 1
    sk, hr = spec['skin'], spec['hair']
    # nohy (chůze)
    lift_l = frame == 1; lift_r = frame == 3
    ly = Y0 + headh + bodyh
    xs = (1, 4) if not kid else (2, 4)
    wid = 2 if not kid else 1
    for side, x0 in enumerate(xs):
        lift = lift_l if side == 0 else lift_r
        rows = legh - (1 if lift else 0)
        for k in range(rows):
            for dx in range(wid):
                if spec['dress'] and not kid and k == 0: continue
                P(x0 + dx, ly + k, sk if spec['dress'] else spec['pants'])
        P(x0, ly + legh - (1 if lift else 0) + (0 if not lift else 0), spec['shoes'], False)
        if wid == 2: P(x0 + 1, ly + legh - (1 if lift else 0), spec['shoes'], False)
    # tělo
    by = Y0 + headh
    bx0, bx1 = (1, 5) if not kid else (2, 4)
    top = spec['shirt']
    for k in range(bodyh):
        for x in range(bx0, bx1 + 1): P(x, by + k, top)
    if spec['dress'] and not kid:
        for x in range(0, 7): P(x, by + bodyh, top)
        for x in range(0, 7): P(x, by + bodyh, top)
    # ruce (houpání)
    ax = (bx0 - 1, bx1 + 1)
    for side, x in enumerate(ax):
        swing = 1 if (frame == 1 and side == 1) or (frame == 3 and side == 0) else 0
        P(x, by + (0 if not kid else 0) + swing, top if not kid else top)
        if not kid or True:
            P(x, by + 1 + swing, sk if bodyh > 2 or kid else top)
    # hlava
    hy = Y0
    hx0, hx1 = (1, 5) if not kid else (1, 5)
    hh = headh
    for k in range(hh):
        for x in range(hx0, hx1 + 1):
            if k == hh - 1 and (x == hx0 or x == hx1): continue   # zaoblená brada
            P(x, hy + k, sk)
    dark = hx('#2a1f2d')
    hs = spec['hstyle']
    if view == 'front':
        ey = hy + (2 if not kid else 1)
        P(2, ey, dark, False); P(4, ey, dark, False)
        P(1, ey + 1, hx('#ff9bb0'), False)
        P(5, ey + 1, hx('#ff9bb0'), False)
        if spec['glasses']:
            for x in range(1, 6): P(x, ey, hx('#2a2a3a'), False)
            P(2, ey, hx('#6a8ab8'), False); P(4, ey, hx('#6a8ab8'), False)
    # vlasy
    if hs != 'bald':
        for x in range(hx0, hx1 + 1): P(x, hy, hr)
        if view == 'back':
            for k in range(1, hh):
                for x in range(hx0, hx1 + 1):
                    if not (k == hh - 1 and (x == hx0 or x == hx1)): P(x, hy + k, hr)
            if hh > 3: P(2, hy + hh - 1, sk); P(3, hy + hh - 1, sk); P(4, hy + hh - 1, sk)
        else:
            P(hx0, hy + 1, hr); P(hx1, hy + 1, hr)
            if hs in ('long', 'ponytail') or hs == 'side':
                for k in range(1, hh): P(hx0, hy + k, hr)
                if hs == 'long':
                    for k in range(1, hh + 1): P(hx1, hy + k, hr)
            if hs == 'side': P(2, hy + 1, hr); P(3, hy + 1, hr)
        if hs == 'curly':
            for x in range(0, 7): P(x, hy - 1 if hy > 0 else hy, hr)
            P(0, hy, hr); P(6, hy, hr)
        if hs == 'bun': P(3, hy - 1, hr); P(2, hy - 1, hr) if False else None
        if hs == 'ponytail' and view == 'back':
            P(6, hy + 2, hr); P(6, hy + 3, hr)
        if hs == 'ponytail' and view == 'front':
            P(6, hy + 1, hr)
    if spec['hood'] and spec['hat'] is None:
        for yy in range(hy, hy + hh):
            P(0, yy, spec['shirt']); P(6, yy, spec['shirt'])
        for x in range(hx0, hx1 + 1): P(x, hy, spec['shirt'])
    # klobouk/čepice
    if spec['hat'] is not None:
        hc = spec['hat']
        if spec['kind'] == 'tourist':
            for x in range(0, 7): P(x, hy, hc, False)
            for x in range(hx0, hx1 + 1): P(x, hy - 1, hc, False)
        else:
            for x in range(hx0, hx1 + 1): P(x, hy, hc, False)
            if view == 'front': P(2, hy + 1, shade_col(hc, .8), False); P(3, hy + 1, shade_col(hc, .8), False); P(4, hy + 1, shade_col(hc, .8), False)
    # doplňky
    a = spec['acc']
    if a == 'backpack':
        c = hx('#e0503e') if spec['seed'] % 2 else hx('#4aa8dc')
        if view == 'back':
            for k in range(0, bodyh + 1):
                for x in range(bx0 + (0 if not kid else 0), bx1 + 1): P(x, by + k, c)
        else:
            P(bx0 - 1, by + 1, c); P(bx1 + 1, by + 1, c); P(bx0 + 1, by, shade_col(c, .8), False) if not kid else None
    elif a == 'camera':
        if view == 'front':
            for x in (2, 3, 4): P(x, by + 1, hx('#3a3a48'), False)
            P(3, by + 1, hx('#a8c8e8'), False)
        else:
            P(2, by, hx('#3a3a48'), False)
    elif a == 'map':
        if view == 'front':
            for x in (2, 3, 4):
                for k in (0, 1): P(x, by + k, hx('#f4f0e0'), False)
            P(3, by, hx('#e0503e'), False)
    elif a == 'cane':
        for k in range(0, bodyh + legh + 1): P(7, by + k, hx('#8a5a3a'), False)
        P(6, by - 0, hx('#8a5a3a'), False)
    elif a == 'icecream':
        P(7, by - 1, hx('#ff9bbd'), False); P(7, by, hx('#ff9bbd'), False) if False else None
        P(7, by, hx('#e0b078'), False); P(7, by + 1, hx('#e0b078'), False)
        P(6, by - 1, hx('#ff9bbd'), False) if False else None
    if spec['plush'] is not None and view == 'front':
        pc = spec['plush']
        for x in (2, 3, 4):
            for k in (by, by + 1): P(x, k, pc, False)
        P(2, by - 1, pc, False); P(4, by - 1, pc, False); P(3, by + 1, shade_col(pc, 1.25), False)
        P(2, by, hx('#2a1f2d'), False); P(4, by, hx('#2a1f2d'), False)
    if spec['star']:
        sx, sy = 3, hy - 3
        for (dx, dy) in [(0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)]:
            X, Y = sx + dx + OX, sy + dy
            if 0 <= Y < H: px[X, Y] = hx('#ffd23c')
        if 0 <= sy < H: px[sx + OX, sy] = hx('#fff2a6')
    if spec['balloon']:
        n = len(spec['balloon'])
        for i, bc in enumerate(spec['balloon']):
            bx = 6 + (i - (n - 1) / 2) * 3 + 1
            by0 = hy - 8 - (i % 2) * 2
            for (dx, dy) in [(-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 2)]:
                X = int(bx + dx) + OX - 2 + 1; Y = by0 + dy
                if 0 <= X < W and 0 <= Y < H: px[X, Y] = bc if not (dx == -1 and dy == 0) else shade_col(bc, 1.25)
            # nit: jedna tenká čára od balónku k ruce
            dr = ImageDraw.Draw(im)
            x_s, y_s = int(bx) + OX - 2 + 1, by0 + 3
            x_h, y_h = OX + 6, by
            pts = []
            n_ = max(abs(x_h - x_s), abs(y_h - y_s), 1)
            for q in range(n_ + 1):
                xx = x_s + (x_h - x_s) * q // n_; yy = y_s + (y_h - y_s) * q // n_
                if 0 <= xx < W and 0 <= yy < H and px[xx, yy][3] == 0: px[xx, yy] = hx('#e6dcec')
    if spec['stroller']:
        sx0 = 7
        c = spec['shirt']
        for (x, y) in [(8, by), (9, by), (10, by)]: P(x - 1, y - 1 + 0, hx('#8a7a8a'), False) if False else None
        # kočárek: stříška + korba + kola
        for x in range(8, 11): P(x, by + 1, hx('#ff9bbd'), False)
        for x in range(8, 11): P(x, by + 2, hx('#ffd8e6'), False)
        P(8, by, hx('#ff9bbd'), False); P(9, by, hx('#ff9bbd'), False)
        P(8, by + 3, hx('#3a2a32'), False); P(10, by + 3, hx('#3a2a32'), False)
    return im

def outline(sprite):
    w, h = sprite.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); op = out.load(); sp = sprite.load()
    line = za.S['line']
    for y in range(h):
        for x in range(w):
            if sp[x, y][3]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + dx, y + dy
                    if not (0 <= X < w and 0 <= Y < h and sp[X, Y][3]):
                        c = sp[x, y]
                        col = tuple(int(c[k] * .45 * .8 + line[k] * .2) for k in range(3)) + (255,)
                        if op[x + 1 + dx, y + 1 + dy][3] == 0 or dy == 1: op[x + 1 + dx, y + 1 + dy] = col
    for y in range(h):
        for x in range(w):
            if sp[x, y][3]: op[x + 1, y + 1] = sp[x, y]
    return out

def visitor(spec, direction='SE', frame=0, shadow=True):
    """hotový sprite s obrysem; kotva = střed pod nohama = (W//2+1, výška-1)"""
    view = 'front' if direction in ('SE', 'SW') else 'back'
    im = draw_person(spec, view, frame)
    flip = direction in ('SW', 'NE') if True else False
    # SE = obličej doprava (kočárek a hůl vpravo), SW = zrcadlo
    if direction in ('SW', 'NW'): im = im.transpose(Image.FLIP_LEFT_RIGHT)
    bbox = im.getbbox()
    top = bbox[1]
    im = im.crop((0, top, W, H))
    sp = outline(im)
    if shadow:
        out = Image.new('RGBA', (sp.width, sp.height + 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(out)
        cx = sp.width // 2
        d.ellipse([cx - 4, sp.height - 2, cx + 4, sp.height + 1], fill=(40, 90, 40, 110))
        out.alpha_composite(sp, (0, 0))
        return out
    return sp

# kompatibilita se scénou zoo_art.make_scene2: person(shirt, pants, skin, kid=False, balloon=None, hat=None, seed=0)
def person_compat(shirt, pants, skin, kid=False, balloon=None, hat=None, seed=0):
    spec = new_spec(seed, kind='balloon' if balloon is not None else None, kid=kid or None)
    spec['shirt'], spec['pants'], spec['skin'] = shirt, pants, skin
    if balloon is not None: spec['balloon'] = [balloon]
    d = DIRS[seed % 4]
    return visitor(spec, d, 0)

def gallery(out, scale=8):
    za.load_style('C_hybrid')
    rows = []
    for k, t in enumerate(TYPES):
        spec = new_spec(100 + k * 7, kind=t)
        if t == 'plain': spec['kid'] = False
        cells = [visitor(spec, d, 0) for d in DIRS] + [visitor(spec, 'SE', f) for f in range(4)]
        rows.append((t, cells))
    cw, ch = 24, 44
    img = Image.new('RGBA', (cw * 8 + 110, ch * len(rows) + 6), za.S['grass'][0])
    px = img.load(); rng = random.Random(1)
    for y in range(img.height):
        for x in range(img.width):
            if rng.random() < .3: px[x, y] = rng.choice(za.S['grass'])
    for r, (t, cells) in enumerate(rows):
        for c, sp in enumerate(cells):
            img.alpha_composite(sp, (110 + c * cw + (cw - sp.width) // 2 + (6 if c >= 4 else 0), r * ch + ch - sp.height - 2))
    big = img.resize((img.width * scale // 2, img.height * scale // 2), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for r, (t, _) in enumerate(rows):
        d.text((6, r * ch * scale // 2 + ch * scale // 2 - 30), t, fill=(255, 255, 255, 255))
    d.text((110 * scale // 2, 2), 'SE   SW   NE   NW   |  walk 1  2  3  4', fill=(255, 255, 255, 255))
    big.save(f'{out}/visitors_types.png')

def crowd_sheet(out, n=48):
    za.load_style('C_hybrid')
    cols = 12
    cw, ch = 16, 40
    img = Image.new('RGBA', (cols * cw, (n // cols) * ch), za.S['grass'][0])
    px = img.load(); rng = random.Random(2)
    for y in range(img.height):
        for x in range(img.width):
            if rng.random() < .3: px[x, y] = rng.choice(za.S['grass'])
    for i in range(n):
        spec = new_spec(900 + i)
        sp = visitor(spec, DIRS[i % 4], 0)
        img.alpha_composite(sp, ((i % cols) * cw + (cw - sp.width) // 2, (i // cols) * ch + ch - sp.height - 2))
    img.resize((img.width * 6, img.height * 6), Image.NEAREST).save(f'{out}/visitors_crowd.png')

def walk_gif(out, nframes=80, scale=3):
    za.load_style('C_hybrid')
    Wc, Hc = 360, 230
    za.OXY = (Wc // 2, 24)
    N = 10
    tiles = {k: [za.tile_img(k, random.Random(a)) for a in range(4)] for k in ('grass', 'dirt', 'cobble')}
    bg = Image.new('RGBA', (Wc, Hc), za.S['sky'])
    rng = random.Random(5)
    for s in range(2 * N - 1):
        for i in range(N):
            j = s - i
            if 0 <= j < N:
                x, y = za.P(i, j)
                k = 'dirt' if (i == 5 or j == 5) else ('cobble' if abs(i - 5) < 2 and abs(j - 5) < 2 else 'grass')
                bg.alpha_composite(rng.choice(tiles[k]), (int(x - 16), int(y)))
    agents = []
    ar = random.Random(7)
    for a in range(34):
        spec = new_spec(300 + a)
        d = DIRS[a % 4]
        line = ar.choice([5.5, 5.5, 4.9, 6.1])
        agents.append((spec, d, line, ar.uniform(0, N), 1.0 + ar.uniform(-.1, .1) * 0))
    frames = []
    for f in range(nframes):
        im = bg.copy(); ents = []
        for (spec, d, line, off, sp_) in agents:
            t = (off + f * 0.125) % N
            if d == 'SE': i, j = t, line
            elif d == 'NW': i, j = (N - t) % N, line
            elif d == 'SW': i, j = line, t
            else: i, j = line, (N - t) % N
            frame = int((f + int(off * 8)) // 2) % 4
            spr = visitor(spec, d, frame)
            x, y = za.P(i, j)
            ents.append((i + j, spr, int(x - spr.width // 2), int(y - spr.height + 1)))
        ents.sort(key=lambda e: e[0])
        for _, spr, x, y in ents: im.alpha_composite(spr, (x, y))
        frames.append(im.resize((im.width * scale, im.height * scale), Image.NEAREST).convert('P', palette=Image.ADAPTIVE, colors=128))
    frames[0].save(f'{out}/visitors_walk.gif', save_all=True, append_images=frames[1:], duration=90, loop=0, disposal=2)

def scene(out):
    import animals
    za.load_style('C_hybrid')
    for n in ('elephant', 'giraffe', 'zebra', 'lion', 'panda', 'flamingo', 'penguin'):
        setattr(za, n, dict(animals.ANIMALS)[n])
    za.person = person_compat
    sc = za.make_scene2()
    sc = za.tone(sc, za.S['sat'], za.S['bright']); za.hud(sc, None)
    sc.resize((sc.width * 3, sc.height * 3), Image.NEAREST).save(f'{out}/C_hybrid_scene_visitors.png')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'visitors_out'
    os.makedirs(out, exist_ok=True)
    gallery(out); crowd_sheet(out); walk_gif(out); scene(out)
    print('ok')
