"""ZOO: výchozí pozice = absolutně malá a chudá zoo + rodiny budov (moderní, africká, asijská, andská).
Použití: python mini_zoo.py <výstupní složka> [počet_návštěvníků]
Ekonomika: 10 mincí za každého návštěvníka (followera); stav se ukazuje na tabuli nad kasou u brány."""
import random, sys, os, math
from PIL import Image, ImageDraw
import zoo_art as za
import animals, visitors
from zoo_art import hx, shade_col, new, outlined

COIN_PER_VISITOR = 10

# 3×5 písmo (rozšířená abeceda)
za.FONT.update({
 'B': ['110','101','110','101','110'], 'C': ['011','100','100','100','011'], 'E': ['111','100','110','100','111'],
 'F': ['111','100','110','100','100'], 'G': ['011','100','101','101','011'], 'H': ['101','101','111','101','101'],
 'J': ['001','001','001','101','010'], 'K': ['101','101','110','101','101'], 'L': ['100','100','100','100','111'],
 'M': ['101','111','111','101','101'], 'N': ['110','101','101','101','101'], 'P': ['110','101','110','100','100'],
 'U': ['101','101','101','101','111'], 'W': ['101','101','111','111','101'], 'X': ['101','101','010','101','101'],
 '?': ['111','001','011','000','010'], '!': ['010','010','010','000','010'], '+': ['000','010','111','010','000'],
})

def text_w(s, sc=1): return sum((len(za.FONT.get(c, za.FONT[' '])[0]) + 1) * sc for c in s) - sc

def draw_text_at(d, x, y, s, col, sc=1):
    for ch in s:
        gl = za.FONT.get(ch, za.FONT[' '])
        for yy, row in enumerate(gl):
            for xx, c in enumerate(row):
                if c == '1': d.rectangle([x + xx * sc, y + yy * sc, x + xx * sc + sc - 1, y + yy * sc + sc - 1], fill=col)
        x += (len(gl[0]) + 1) * sc

def coin_icon(d, x, y):
    g, gd, gl = hx('#ffc93c'), hx('#d9962a'), hx('#fff2a6')
    for (dx, dy) in [(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (1, 4), (2, 4), (3, 4)]:
        d.point((x + dx, y + dy), fill=g)
    for (dx, dy) in [(4, 1), (4, 2), (4, 3), (3, 4), (2, 4), (1, 4)]: d.point((x + dx, y + dy), fill=gd)
    d.point((1, y + 1) if False else (x + 1, y + 1), fill=gl); d.point((x + 1, y + 2), fill=gl)
    d.point((x + 2, y + 1), fill=gd); d.point((x + 2, y + 2), fill=gd); d.point((x + 2, y + 3), fill=gd)

# ---------------------------------------------------------------- základ: izometrický kvádr
def box(g, A, wi, dj, wh, left, right, top, edge=None):
    up = lambda p, h: (p[0], p[1] - h)
    B = (A[0] + 16 * wi, A[1] + 8 * wi); D = (A[0] - 16 * dj, A[1] + 8 * dj); C = (B[0] - 16 * dj, B[1] + 8 * dj)
    g.polygon([D, C, up(C, wh), up(D, wh)], fill=left)
    g.polygon([B, C, up(C, wh), up(B, wh)], fill=right)
    g.polygon([up(A, wh), up(B, wh), up(C, wh), up(D, wh)], fill=top)
    if edge:
        g.line([up(D, wh), up(C, wh), up(B, wh)], fill=edge)
    return A, B, C, D

def wall_rect(g, P0, P1, f, w, yb, hh, col):
    za.wall_rect(g, P0, P1, f, w, yb, hh, col)

# ---------------------------------------------------------------- moderní budova
def modern(wi=2.0, dj=1.4, wh=18, accent=None, seed=0):
    rng = random.Random(seed)
    accent = accent or hx('#2fb5a5')
    pad = 10
    W = int(16 * (wi + dj)) + pad * 2; H = int(8 * (wi + dj)) + wh + 30 + pad
    im, g = new(W, H)
    A = (pad + 16 * dj, H - int(8 * (wi + dj)) - 8)
    wl, wr, top = hx('#f3f1ea'), hx('#cfd0cc'), hx('#dcdad2')
    A_, B, C, D = box(g, A, wi, dj, wh, wl, wr, top, edge=hx('#a9aaa8'))
    L = int(C[0] - D[0]); R_ = int(B[0] - C[0])
    # pásový pás v barvě akcentu pod střechou
    wall_rect(g, D, C, 0, L, wh - 3, 3, accent)
    wall_rect(g, C, B, 0, R_, wh - 3, 3, shade_col(accent, .8))
    # velká prosklení na dlouhé stěně
    glass, glass2 = hx('#8fdde8'), hx('#c4f0f5')
    n = max(2, int(wi * 1.6))
    for k in range(n):
        f = (k + .5) / n
        w_ = max(4, int(L / n) - 3)
        x0 = int(L * f - w_ / 2)
        wall_rect(g, D, C, x0 / L, w_, 2, wh - 8, glass)
        wall_rect(g, D, C, x0 / L, w_, 2 + (wh - 8) - 2, 1, hx('#6ab8c8'))
        for q in range(0, w_, 4):
            wall_rect(g, D, C, (x0 + q) / L, 1, 3 + (q // 2) % (wh - 10), 2, glass2)
    # dřevěné lamely na pravé stěně
    for q in range(1, R_, 2):
        wall_rect(g, C, B, q / R_, 1, 1, wh - 6, hx('#c98a52') if q % 4 == 1 else hx('#a87038'))
    # stříška nad vchodem (deska) + sloupek
    up = lambda p, h: (p[0], p[1] - h)
    cx0 = D[0] + L * 0.62; cy0 = D[1] + (C[1] - D[1]) * 0.62 - 9
    g.polygon([(cx0 - 6, cy0), (cx0 + 8, cy0 + 7), (cx0 + 8, cy0 + 9), (cx0 - 6, cy0 + 2)], fill=accent)
    g.line([(cx0 + 7, cy0 + 9), (cx0 + 7, cy0 + 16)], fill=hx('#7a7a82'))
    # střecha: solární panely a klimatizace
    tp = lambda i, j: (A[0] + 16 * i - 16 * j, A[1] + 8 * i + 8 * j - wh)
    g.polygon([tp(.3, .25), tp(wi * .55, .25), tp(wi * .55, dj * .55), tp(.3, dj * .55)], fill=hx('#2f4a8a'))
    for k in range(1, 4):
        g.line([tp(.3 + k * (wi * .25 / 4), .25), tp(.3 + k * (wi * .25 / 4), dj * .55)], fill=hx('#5a7ac0'))
    g.line([tp(.3, .4), tp(wi * .55, .4)], fill=hx('#5a7ac0'))
    bx, by = tp(wi * .75, dj * .4)
    g.rectangle([bx - 3, by - 5, bx + 3, by], fill=hx('#b8bcc4')); g.rectangle([bx - 3, by - 5, bx + 3, by - 4], fill=hx('#dfe3ea'))
    return outlined(im, hx('#4a4a58')), (int(C[0]) + 1, int(C[1]) + 1)

# ---------------------------------------------------------------- africká kulatá chýše
def african_hut(seed=0):
    rng = random.Random(seed)
    im, g = new(44, 46)
    cx, wall_top, base = 22, 26, 38
    wc = hx('#d9894a')
    g.ellipse([cx - 13, base - 6, cx + 13, base + 5], fill=shade_col(wc, .8))
    g.rectangle([cx - 13, wall_top, cx + 13, base], fill=wc)
    g.ellipse([cx - 13, base - 5, cx + 13, base + 5], fill=wc)
    px = im.load()
    for y in range(wall_top, base + 6):
        for x in range(cx - 13, cx + 14):
            if px[x, y][3]:
                if x > cx + 4: px[x, y] = shade_col(wc, .74)
                elif x < cx - 8: px[x, y] = shade_col(wc, 1.1)
    # bílý klikatý vzor
    for k, x in enumerate(range(cx - 12, cx + 13)):
        y = base - 10 + (k % 4 if (k // 2) % 2 == 0 else 3 - k % 4) // 2
        if px[x, y][3]: px[x, y] = hx('#fff4e0') if x < cx + 5 else hx('#e8d8c0')
    for x in range(cx - 11, cx + 13, 4):
        y = base - 4
        if px[x, y][3]: px[x, y] = hx('#fff4e0')
    # dveře
    g.rectangle([cx - 4, base - 12, cx + 4, base + 3], fill=hx('#4a2a24'))
    g.ellipse([cx - 4, base - 15, cx + 4, base - 9], fill=hx('#4a2a24'))
    # sláma
    th, thd, thl = hx('#dcb85a'), hx('#b08a38'), hx('#f0d98a')
    g.polygon([(cx - 16, wall_top + 1), (cx, 5), (cx + 16, wall_top + 1)], fill=th)
    g.ellipse([cx - 16, wall_top - 5, cx + 16, wall_top + 7], fill=th)
    for x in range(cx - 16, cx + 17):
        tt = abs(x - cx) / 16
        ytop = 5 + (wall_top + 1 - 5) * tt
        for y in range(int(ytop), wall_top + 6):
            if px[x, y][3] and ((x * 7 + y * 3) % 5 == 0): px[x, y] = thd
            elif px[x, y][3] and ((x + y * 2) % 11 == 0): px[x, y] = thl
            if px[x, y][3] and x > cx + 5: px[x, y] = shade_col(px[x, y], .8)
    for x in range(cx - 16, cx + 17, 2):   # střapec okraje
        g.line([(x, wall_top + 5), (x, wall_top + 6 + (x % 3 == 0))], fill=thd)
    g.line([(cx, 5), (cx, 1)], fill=hx('#6a4a2a')); g.ellipse([cx - 1, 0, cx + 1, 2], fill=hx('#6a4a2a'))
    return outlined(im, hx('#5a3a24')), (cx + 1, base + 5)

# ---------------------------------------------------------------- asijská pagoda
def pagoda(seed=0):
    im, g = new(84, 90)
    cx = 42
    red, redd, gold = hx('#d24545'), hx('#a63232'), hx('#ffc93c')
    roof, roofd, roofl = hx('#2fa58a'), hx('#1f7a68'), hx('#5fd0b0')
    def tier(cy, w, h=7):
        # spodní strana převisu
        g.polygon([(cx - w, cy), (cx, cy + w // 2), (cx + w, cy), (cx + w, cy + 3), (cx, cy + w // 2 + 3), (cx - w, cy + 3)], fill=roofd)
        # horní plocha s vyzdviženými rohy
        g.polygon([(cx - w - 3, cy - 4), (cx, cy - w // 2 - 2), (cx + w + 3, cy - 4), (cx + w, cy), (cx, cy + w // 2), (cx - w, cy)], fill=roof)
        g.polygon([(cx, cy - w // 2 - 2), (cx + w + 3, cy - 4), (cx + w, cy), (cx, cy + w // 2)], fill=shade_col(roof, .8))
        g.line([(cx - w - 3, cy - 4), (cx, cy + w // 2 - 1), (cx + w + 3, cy - 4)], fill=gold)
        g.line([(cx - w, cy), (cx, cy - w // 2 - 1)], fill=roofl)
    # spodní patro
    A = (cx, 56)
    box(g, A, 1.1, 1.1, 16, hx('#e83c3c'), redd, hx('#8a2a2a'))
    box(g, (cx, 40 - 4), 0.7, 0.7, 12, hx('#e83c3c'), redd, hx('#8a2a2a'))
    tier(60 - 18 + 2, 26)
    tier(34, 19)
    tier(14, 11)
    g.line([(cx, 6), (cx, 0)], fill=gold); g.ellipse([cx - 2, 3, cx + 2, 7], fill=gold)
    # dveře a lucerny
    g.rectangle([cx - 8, 64, cx - 4, 72], fill=hx('#4a1a1a'))
    for (x, y) in [(cx - 20, 58), (cx + 18, 58)]:
        g.ellipse([x - 2, y, x + 2, y + 5], fill=hx('#ff6a3c')); g.point((x, y + 1), fill=hx('#fff2a6'))
    return outlined(im, hx('#4a1f24')), (cx + 1, 84)

# ---------------------------------------------------------------- andská stupňovitá stavba
def stepped_adobe(seed=0):
    im, g = new(96, 74)
    terr, terrd = hx('#d98a5a'), hx('#b0663c')
    top = hx('#e8a070')
    stripes = [hx('#2fb5a5'), hx('#ff5a8a'), hx('#ffc93c')]
    A = (48, 28)
    levels = [(2.1, 1.7, 11), (1.5, 1.2, 10), (0.9, 0.8, 9)]
    cur = A
    base_y = 0
    # spočítáme polohy od spodku: dole největší
    ys = []
    y = A[1] + 8 * (levels[0][0] + levels[0][1])  # umístění přední hrany
    pos = []
    # A nejspodnějšího patra tak, aby C bylo na (48, 68)
    wi, dj, wh = levels[0]
    A0 = (48 + 16 * (dj - wi), 68 - 8 * (wi + dj))
    Ax, Ay = A0
    for (wi, dj, wh) in levels:
        A1, B, C, D = box(g, (Ax, Ay), wi, dj, wh, terr, terrd, top, edge=hx('#8a4a2a'))
        L = int(C[0] - D[0]); R_ = int(B[0] - C[0])
        for k, col in enumerate(stripes):
            wall_rect(g, D, C, 0, L, 2 + k * 3, 2, col)
            wall_rect(g, C, B, 0, R_, 2 + k * 3, 2, shade_col(col, .78))
        # další patro: střed půdorysu
        nxt = None
        pos.append((Ax, Ay, wi, dj, wh, C))
        if (wi, dj, wh) != levels[-1]:
            wi2, dj2, _ = levels[levels.index((wi, dj, wh)) + 1]
            Ax, Ay = Ax + 16 * (wi - wi2) / 2 - 16 * (dj - dj2) / 2, Ay + 8 * (wi - wi2) / 2 + 8 * (dj - dj2) / 2 - wh
    # dveře na spodním patře
    Ax0, Ay0, wi0, dj0, wh0, C0 = pos[0]
    D0 = (Ax0 - 16 * dj0, Ay0 + 8 * dj0)
    wall_rect(g, D0, C0, 0.45, 6, 0, 8, hx('#3a1a20'))
    # prapůrky na horní plošině
    top3 = pos[-1]
    fx, fy = int(top3[0]), int(top3[1] - top3[4]) + 6
    g.line([(fx, fy), (fx, fy - 14)], fill=hx('#6a4a2a'))
    g.polygon([(fx, fy - 14), (fx + 8, fy - 12), (fx, fy - 9)], fill=hx('#ff5a8a'))
    return outlined(im, hx('#5a2a1e')), (int(C0[0]) + 1, int(C0[1]) + 1)

# ---------------------------------------------------------------- kasa (pokladna s tabulí mincí)
def kasa(coins):
    s, (ax, ay) = za.house(1.2, 1.0, 14, 8, hx('#c9a36b'), hx('#b8503a'), windows=0, door=None, timber=False, seed=3)
    bb = s.getbbox(); s = s.crop((0, bb[1], s.width, s.height)); ay -= bb[1]
    # okénko pokladny na dlouhé stěně
    W0, H0 = s.size
    board_w, board_h = 38, 16
    W0, H0 = s.size
    out = Image.new('RGBA', (max(W0, board_w + 6), H0 + board_h + 8), (0, 0, 0, 0))
    ox = (out.width - W0) // 2
    out.alpha_composite(s, (ox, board_h + 8))
    d = ImageDraw.Draw(out)
    # okénko
    sp = out.load()
    # tabule na dvou sloupcích nad střechou
    bx = (out.width - board_w) // 2
    d.rectangle([bx + 6, board_h - 2, bx + 7, board_h + 12], fill=hx('#7a5230'))
    d.rectangle([bx + board_w - 8, board_h - 2, bx + board_w - 7, board_h + 12], fill=hx('#7a5230'))
    d.rectangle([bx, 0, bx + board_w - 1, board_h - 1], fill=hx('#3d2a28'))
    d.rectangle([bx + 1, 1, bx + board_w - 2, board_h - 2], fill=hx('#fff3d6'))
    d.rectangle([bx + 1, 1, bx + board_w - 2, 2], fill=hx('#ffc93c'))
    d.rectangle([bx + 1, board_h - 4, bx + board_w - 2, board_h - 2], fill=hx('#f6d98f'))
    coin_icon(d, bx + 3, 5)
    num = f'{coins:,}'
    draw_text_at(d, bx + 10, 5, num, hx('#d9742a'), 1)
    return outlined(out, hx('#3d2a28')), (ox + ax + 1, board_h + 8 + ay + 1)

# ---------------------------------------------------------------- chudé rekvizity
def stake_plot():
    """parcela k zastavění: dřevěné kolíky se provazem a cedulí „?“"""
    im, g = new(70, 44)
    pts = [(35, 4), (66, 20), (35, 36), (4, 20)]
    g.polygon(pts, fill=hx('#c49a68'))
    g.polygon([(35, 8), (58, 20), (35, 32), (12, 20)], fill=hx('#d6ae7a'))
    for (x, y) in pts:
        g.rectangle([x - 1, y - 3, x, y + 1], fill=hx('#8a5a3a'))
    for a, b in zip(pts, pts[1:] + pts[:1]):
        g.line([(a[0], a[1] - 2), (b[0], b[1] - 2)], fill=hx('#f0e6d0'))
    return outlined(im, hx('#5a3a24')), (35, 36)

def question_sign():
    im, g = new(14, 24)
    g.rectangle([6, 8, 7, 22], fill=hx('#8a5a3a'))
    g.rectangle([0, 0, 13, 10], fill=hx('#fff3d6')); g.rectangle([0, 0, 13, 1], fill=hx('#ffc93c'))
    draw_text_at(g, 5, 3, '?', hx('#d9742a'), 1)
    return outlined(im, hx('#3d2a28')), (7, 22)

def crate():
    im, g = new(12, 12)
    g.rectangle([0, 3, 10, 11], fill=hx('#c98a52')); g.polygon([(0, 3), (3, 0), (11, 0), (10, 3)], fill=hx('#e0a468'))
    g.line([(0, 7), (10, 7)], fill=hx('#9c6840')); g.line([(5, 3), (5, 11)], fill=hx('#9c6840'))
    return outlined(im, hx('#5a3a24')), (6, 11)

def hay():
    im, g = new(16, 12)
    g.ellipse([0, 2, 15, 11], fill=hx('#e8c458')); g.ellipse([0, 0, 15, 8], fill=hx('#f2d878'))
    for x in range(2, 14, 3): g.line([(x, 3), (x - 1, 8)], fill=hx('#c9a038'))
    return outlined(im, hx('#6a4a24')), (8, 11)

def rough_fence_post(tilt=0):
    im, g = new(6, 13)
    g.rectangle([1, 2 + tilt, 3, 11], fill=hx('#b8884e')); g.rectangle([3, 2 + tilt, 3, 11], fill=hx('#8a5a32'))
    g.rectangle([0, 1 + tilt, 4, 2 + tilt], fill=hx('#d9b57a'))
    return outlined(im, hx('#4a2f20'))

def bench():
    im, g = new(18, 10)
    g.rectangle([0, 3, 17, 5], fill=hx('#d9a066')); g.rectangle([1, 0, 16, 2], fill=hx('#c98a52'))
    g.rectangle([1, 6, 2, 9], fill=hx('#8a5a32')); g.rectangle([15, 6, 16, 9], fill=hx('#8a5a32'))
    return outlined(im, hx('#4a2f20')), (9, 9)

def weeds():
    im, g = new(10, 7)
    for (x, h_) in [(1, 4), (3, 6), (5, 5), (7, 4), (4, 3)]:
        g.line([(x, 6), (x + (1 if x % 2 else -1), 6 - h_)], fill=hx('#7fb04a'))
    return im, (5, 6)

def sign_board(text, w=None):
    w = w or text_w(text) + 8
    im, g = new(w, 14 + 12)
    g.rectangle([w // 2 - 1, 12, w // 2, 24], fill=hx('#8a5a3a'))
    g.rectangle([0, 0, w - 1, 11], fill=hx('#fff3d6')); g.rectangle([0, 0, w - 1, 1], fill=hx('#ffc93c'))
    draw_text_at(g, 4, 4, text, hx('#a63232'), 1)
    return outlined(im, hx('#3d2a28')), (w // 2, 24)

def gate_poor():
    """chudá brána z klád s prkenným nápisem (úzká, přes jednu cestu)"""
    im, g = new(58, 56)
    for px in (2, 46):
        g.rectangle([px, 16, px + 7, 52], fill=hx('#b8884e')); g.rectangle([px + 4, 16, px + 7, 52], fill=hx('#8a5a32'))
        g.rectangle([px - 1, 13, px + 8, 16], fill=hx('#d9b57a'))
    g.rectangle([5, 6, 52, 20], fill=hx('#c98a52')); g.rectangle([5, 6, 52, 7], fill=hx('#e0a468')); g.rectangle([5, 18, 52, 20], fill=hx('#8a5a32'))
    gl = {'Z': ['111', '001', '010', '100', '111'], 'O': ['111', '101', '101', '101', '111']}
    x = 14
    for ch in 'ZOO':
        for yy, row in enumerate(gl[ch]):
            for xx, c in enumerate(row):
                if c == '1': g.rectangle([x + xx * 3, 9 + yy * 2, x + xx * 3 + 2, 9 + yy * 2 + 1], fill=hx('#fff3d6'))
        x += 13
    for k in range(5):
        col = [hx('#ef5b5b'), hx('#ffc93c'), hx('#4aa8dc')][k % 3]
        x = 7 + k * 9
        g.polygon([(x, 21), (x + 7, 21), (x + 3, 26)], fill=col)
    return outlined(im, hx('#4a2f20')), (29, 54)

# ---------------------------------------------------------------- mini zoo
def make_mini(n_visitors=12, W=420, H=262):
    za.load_style('C_hybrid')
    rng = random.Random(33)
    N = 11
    za.OXY = (W // 2, 70)
    img = Image.new('RGBA', (W, H), za.S['sky'])
    mid = 5
    # povrch: hodně holé hlíny (chudá zoo)
    kinds = [[('dirt' if rng.random() < .32 else 'grass') for _ in range(N)] for _ in range(N)]
    for k in range(N): kinds[mid][k] = 'dirt'; kinds[k][mid] = 'dirt'
    for i in range(mid - 1, mid + 2):
        for j in range(mid - 1, mid + 2): kinds[i][j] = 'cobble'
    for (i, j) in [(7, 2), (8, 2), (7, 3), (8, 3)]: kinds[i][j] = 'water'
    tiles = {k: [za.tile_img(k, random.Random(a)) for a in range(4)] for k in ('grass', 'dirt', 'cobble', 'water')}
    for s in range(2 * N - 1):
        for i in range(N):
            j = s - i
            if 0 <= j < N:
                x, y = za.P(i, j)
                img.alpha_composite(rng.choice(tiles[kinds[i][j]]), (int(x - 16), int(y)))
    ents = []
    def put(sp_anchor, i, j, off=0.0, dx=0, dy=0):
        sp, a = sp_anchor
        x, y = za.P(i, j)
        ents.append((i + j + off, sp, int(x - a[0] + dx), int(y - a[1] + dy)))
    def put_b(sp, i, j, off=0.0, dx=0):
        put((sp, (sp.size[0] // 2, sp.size[1] - 2)), i, j, off, dx)
    # kasa a brána
    coins = n_visitors * COIN_PER_VISITOR
    put(kasa(coins), 8.4, 10.8, .5)
    put(gate_poor(), 5.5, 11.2, .6)
    put(sign_board('WELCOME'), 3.7, 10.2, .4)
    # výběh zeber (vlevo nahoře), chudý plot s dírou
    ENC = (1, 1, 5, 5)
    fp = [visitors_outline for visitors_outline in []]
    posts = set()
    def fence_poor(i0, j0, i1, j1, gaps):
        for i in range(i0, i1):
            for (a, b) in (((i, j0), (i + 1, j0)), ((i, j1), (i + 1, j1))):
                if (a, b) in gaps: continue
                seg(a, b)
        for j in range(j0, j1):
            for (a, b) in (((i0, j), (i0, j + 1)), ((i1, j), (i1, j + 1))):
                if (a, b) in gaps: continue
                seg(a, b)
        for i in range(i0, i1 + 1): posts.update({(i, j0), (i, j1)})
        for j in range(j0, j1 + 1): posts.update({(i0, j), (i1, j)})
    def seg(a, b):
        xa, ya = za.P(*a); xb, yb = za.P(*b)
        im = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); gg = ImageDraw.Draw(im)
        for lift, col in ((8, hx('#d9b57a')), (4, hx('#c49a68'))):
            gg.line([(20, 14 - lift), (20 + xb - xa, 14 + yb - ya - lift)], fill=col)
            gg.line([(20, 14 - lift + 1), (20 + xb - xa, 14 + yb - ya - lift + 1)], fill=hx('#8a5a32'))
        ents.append(((a[0] + a[1] + b[0] + b[1]) / 2 + .2, outlined(im, hx('#4a2f20')), int(xa - 21), int(ya - 15)))
    fence_poor(1, 1, 5, 5, gaps={((2, 5), (3, 5)), ((1, 3), (1, 4))})
    fence_poor(7, 1, 10, 4, gaps={((7, 4), (8, 4))})
    for k, (i, j) in enumerate(sorted(posts)):
        put_b(rough_fence_post(k % 2), i, j, .3)
    # zvířata: dvě zebry a dva plameňáci na loužičce
    A = dict(animals.ANIMALS)
    put_b(A['zebra'](), 2.3, 2.4, .1); put_b(A['zebra'](), 4.2, 4.1, .1)
    put_b(A['flamingo'](), 8.0, 2.6, .1); put_b(A['flamingo'](), 8.9, 3.4, .1)
    # parcely k zastavění (hlasování)
    put(stake_plot(), 3.2, 6.8, .1); put(question_sign(), 2.2, 7.2, .45)
    put(stake_plot(), 10.2, 10.0, .1); put(question_sign(), 9.2, 10.4, .45)
    put(stake_plot(), 9.8, 6.8, .1); put(question_sign(), 8.8, 7.2, .45)
    put(stake_plot(), 8.7, 5.7, .1) if False else None
    # rekvizity
    put(bench(), 4.1, 5.9, .3); put(bench(), 6.9, 5.9, .3)
    put(crate(), 0.6, 8.2, .3); put(crate(), 0.9, 8.5, .3); put(hay(), 0.3, 9.2, .3)
    put(weeds(), 3.2, 7.4, .2); put(weeds(), 7.6, 6.8, .2); put(weeds(), 9.4, 7.4, .2); put(weeds(), 5.2, 9.0, .2)
    put((za.tree_round(), (13, 31)), 0.2, 4.0, .2); put((za.tree_pine(), (10, 31)), 9.8, 0.4, .2)
    put((za.tree_round(), (13, 31)), 10.4, 6.2, .2); put((za.bush(), (7, 8)), 9.6, 9.8, .2); put((za.bush(), (7, 8)), 0.5, 9.0, .2)
    put((za.tree_pine(), (10, 31)), 0.0, 0.8, .2)
    # návštěvníci
    rr = random.Random(9)
    spots = [(5.5, 9.6), (5.8, 9.1), (5.2, 8.6), (5.6, 8.0), (5.4, 7.0), (4.6, 5.2), (6.4, 5.6), (3.2, 5.5), (7.6, 5.4), (8.4, 6.8)]
    spots += [(5.3 + rr.uniform(-.3, .3), 11.8 + rr.uniform(-.2, .5)) for _ in range(6)]
    for k in range(min(n_visitors, len(spots))):
        i, j = spots[k]
        spec = visitors.new_spec(1000 + k)
        spr = visitors.visitor(spec, visitors.DIRS[k % 4], 0)
        put_b(spr, i, j, .45)
    ents.sort(key=lambda e: e[0])
    for key, sp, x, y in ents:
        img.alpha_composite(sp, (x, y))
    # HUD: návštěvníci + mince
    d = ImageDraw.Draw(img)
    bg, fg, ac = [hx(c) for c in za.S['hud']]
    d.rectangle([W // 2 - 72, 6, W // 2 + 72, 46], fill=bg); d.rectangle([W // 2 - 72, 6, W // 2 + 72, 8], fill=ac)
    za.draw_text(d, W // 2, 12, 'VISITORS', fg, 1)
    za.draw_text(d, W // 2, 20, f'{n_visitors}', hx('#ef5b5b'), 2)
    d.line([(W // 2 - 60, 33), (W // 2 + 60, 33)], fill=shade_col(bg, 1.5))
    coin_icon(d, W // 2 - 62, 36)
    draw_text_at(d, W // 2 - 53, 36, f'{coins}', ac, 1)
    draw_text_at(d, W // 2 - 53 + text_w(f'{coins}') + 6, 36, '+10 PER VISITOR', hx('#fff0c8'), 1)
    return img

def families(out):
    za.load_style('C_hybrid')
    items = [('kasa', kasa(120)), ('modern', modern(2.0, 1.4, 18, seed=1)), ('modern2', modern(1.4, 1.2, 14, hx('#ff7a59'), seed=2)),
             ('african', african_hut()), ('asian', pagoda()), ('andes', stepped_adobe()), ('classic', za.house(1.6, 1.0, 16, 10, za.S['walls'][0], za.S['roofs'][0], windows=2, door=.62, seed=1))]
    W = sum(s[0].width + 14 for _, s in items) + 14
    H = max(s[0].height for _, s in items) + 24
    sh = Image.new('RGBA', (W, H), za.S['grass'][0]); x = 14
    for n, (sp, a) in items:
        sh.alpha_composite(sp, (x, H - sp.height - 8)); x += sp.width + 14
    sh.resize((sh.width * 4, sh.height * 4), Image.NEAREST).save(f'{out}/building_families.png')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'mini_out'
    nv = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    os.makedirs(out, exist_ok=True)
    families(out)
    sc = make_mini(nv)
    sc.resize((sc.width * 3, sc.height * 3), Image.NEAREST).save(f'{out}/mini_zoo_start.png')
    print('ok')
