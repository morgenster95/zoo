"""ZOO: styl zvířat v2. Pravidla viz docs/ART.md (sekce Zvířata).
- pohled z boku/3/4 doprava (doleva = zrcadlo), světlo vlevo nahoře
- tělo = koule se čtyřtónovým stínováním (světlo, základ, stín, hluboký stín) + dither na přechodech
- tenké části (krk, chobot, nohy) = stínování podle okraje masky
- „selektivní obrys“: obrys je tmavší odstín barvy sousední plochy, ne jedna barva pro všechno
- oko 2×2 + odlesk, růžový ruměnec, kopyta a drápy tmavé, vzory (skvrny, pruhy) jen uvnitř siluety
Použití: python animals.py <výstupní složka>   (arch zvířat na trávě stylu C)"""
import random, sys, os, math
from PIL import Image, ImageDraw
import zoo_art as za
from zoo_art import hx, shade_col

K = 0.9   # měřítko kreseb (1.0 = „hero“ velikost, 0.9 = velikost na mapě)

def ramp(hi, base, sh, deep): return [hx(hi), hx(base), hx(sh), hx(deep)]
R = dict(
  ele=ramp('#e3e8f7', '#bcc6e2', '#98a4ca', '#7a86b0'),
  gir=ramp('#ffe596', '#ffd35a', '#f0b03c', '#d58b2a'),
  zeb=ramp('#ffffff', '#f6f3ee', '#d9d6e4', '#bab7cc'),
  lion=ramp('#fbdc94', '#f2c06a', '#d9a04a', '#b47c33'),
  mane=ramp('#e8934a', '#cf7430', '#ac5a28', '#8a4522'),
  tig=ramp('#ffc277', '#f89d3c', '#da7a28', '#b45d20'),
  pan_w=ramp('#ffffff', '#f8f5f0', '#dcd9e6', '#bebbd0'),
  pan_b=ramp('#6a6484', '#4a4466', '#35304f', '#262240'),
  hip=ramp('#dccbea', '#c0a7d4', '#9f85b8', '#806798'),
  fla=ramp('#ffc9dd', '#ff9fc0', '#f27aa6', '#d45683'),
  pen=ramp('#6b7699', '#4c5678', '#38405f', '#2a3050'),
  mon=ramp('#c68a5a', '#a86e42', '#855230', '#653c22'),
  tan=ramp('#ffe9c4', '#f6d3a0', '#e3b378', '#c98f58'),
  ele_ear=ramp('#cfd6ee', '#a9b4d6', '#8793bb', '#6d799f'),
  rhi=ramp('#e0dce6', '#bdb7c9', '#9a94ab', '#7a758c'),
  bear=ramp('#b98660', '#96653f', '#744a2c', '#563620'),
  shell=ramp('#8fd36a', '#5fb44a', '#43923a', '#2f722e'),
  white=ramp('#ffffff', '#fff8ee', '#e6dfe8', '#cbc4d4'),
  pink=ramp('#ffd0dc', '#f9aabf', '#e68aa6', '#c96b88'),
)

class Cv:
    def __init__(self, w, h):
        self.w, self.h = int(w * K) + 4, int(h * K) + 4
        self.im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        self.clip = None
    def s(self, v): return v * K + 2
    def px(self, x, y, c):
        x, y = int(x * K + 2), int(y * K + 2)
        if 0 <= x < self.w and 0 <= y < self.h: self.im.putpixel((x, y), c)
    def rect(self, x0, y0, x1, y1, c):
        a, b = self.s(x0), self.s(y0)
        ImageDraw.Draw(self.im).rectangle([a, b, max(a, self.s(x1) - 1), max(b, self.s(y1) - 1)], fill=c)

    def blob(self, cx, cy, rx, ry, rp, tilt=0.0, flat=None):
        """koule se stínováním, světlo vlevo nahoře; tilt natočí elipsu (rad)"""
        cx, cy, rx, ry = self.s(cx), self.s(cy), rx * K, ry * K
        ca, sa = math.cos(tilt), math.sin(tilt)
        R_ = int(max(rx, ry)) + 2
        for y in range(int(cy) - R_, int(cy) + R_ + 1):
            for x in range(int(cx) - R_, int(cx) + R_ + 1):
                dx, dy = x + .5 - cx, y + .5 - cy
                ux, uy = dx * ca + dy * sa, -dx * sa + dy * ca
                nx, ny = ux / rx, uy / ry
                if nx * nx + ny * ny <= 1.0:
                    if flat is not None: c = flat
                    else:
                        t = (dx / max(rx, ry)) * .55 + (dy / max(rx, ry)) * .75
                        d = ((x + y) % 2 == 0)
                        if t < -.50 + (.07 if d else 0): c = rp[0]
                        elif t < .18 + (.07 if d else 0): c = rp[1]
                        elif t < .60 + (.07 if d else 0): c = rp[2]
                        else: c = rp[3]
                    if 0 <= x < self.w and 0 <= y < self.h: self.im.putpixel((x, y), c)

    def mask_shape(self, draw_fn, rp, depth=2, flat=None):
        """libovolný tvar (tenké části) se stínováním podle okraje masky"""
        m = Image.new('L', (self.w, self.h), 0); d = ImageDraw.Draw(m)
        draw_fn(d, self.s)
        mp = m.load()
        def inside(x, y): return 0 <= x < self.w and 0 <= y < self.h and mp[x, y] > 0
        for y in range(self.h):
            for x in range(self.w):
                if mp[x, y]:
                    if flat is not None: c = flat
                    elif not inside(x + 1, y + 1): c = rp[3] if not inside(x, y + 2) else rp[2]
                    elif not inside(x + depth, y + depth): c = rp[2]
                    elif not inside(x - 1, y - 1) or not inside(x - depth, y - depth): c = rp[0]
                    else: c = rp[1]
                    self.im.putpixel((x, y), c)

    def limb(self, x0, y0, x1, y1, w, rp, far=False, hoof=None):
        def f(d, s):
            d.rectangle([s(x0), s(y0), s(x0 + w) - 1, s(y1) - 1], fill=255)
        rp2 = [shade_col(c, .86) for c in rp] if far else rp
        self.mask_shape(f, rp2, 1)
        if hoof:
            self.rect(x0, y1 - 2, x0 + w, y1, hoof)

    def line(self, pts, w, rp=None, flat=None, depth=1):
        def f(d, s):
            d.line([(s(x), s(y)) for x, y in pts], fill=255, width=max(1, int(round(w * K))), joint='curve')
        self.mask_shape(f, rp or [flat] * 4, depth, flat=flat if rp is None else None)

    def poly(self, pts, rp=None, flat=None, depth=2):
        def f(d, s): d.polygon([(s(x), s(y)) for x, y in pts], fill=255)
        self.mask_shape(f, rp or [flat] * 4, depth, flat=flat if rp is None else None)

    def overlay(self, fn, color):
        """vzor (skvrny/pruhy) jen tam, kde už je tělo (ne průhledné)"""
        layer = Image.new('L', (self.w, self.h), 0); d = ImageDraw.Draw(layer); fn(d, self.s)
        lp = layer.load(); ip = self.im.load()
        for y in range(self.h):
            for x in range(self.w):
                if lp[x, y] and ip[x, y][3]: ip[x, y] = color

    def eye(self, x, y, big=False):
        x, y = int(self.s(x)), int(self.s(y))
        dk = hx('#2a1f2d')
        for (a, b) in ([(0, 0), (1, 0), (0, 1), (1, 1)] if not big else [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]):
            if 0 <= x + a < self.w and 0 <= y + b < self.h: self.im.putpixel((x + a, y + b), dk)
        if 0 <= x < self.w and 0 <= y < self.h: self.im.putpixel((x, y), hx('#ffffff'))

    def blush(self, x, y, c=hx('#ff9bb0')):
        self.px(x, y, c); self.px(x + 1, y, c)

    def done(self):
        """selektivní obrys: tmavší odstín sousední barvy, spodní hrany ještě tmavší"""
        w, h = self.im.size
        out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); op = out.load(); sp = self.im.load()
        base_line = za.S['line']
        for y in range(h):
            for x in range(w):
                if sp[x, y][3]:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        X, Y = x + dx, y + dy
                        if not (0 <= X < w and 0 <= Y < h and sp[X, Y][3]):
                            c = sp[x, y]
                            f = .42 if dy >= 0 else .55
                            col = tuple(int(c[k] * f * .75 + base_line[k] * .25) for k in range(3)) + (255,)
                            if op[x + 1 + dx, y + 1 + dy][3] == 0 or dy == 1: op[x + 1 + dx, y + 1 + dy] = col
        for y in range(h):
            for x in range(w):
                if sp[x, y][3]: op[x + 1, y + 1] = sp[x, y]
        return out

# ---------------------------------------------------------------- zvířata
def elephant():
    c = Cv(50, 42); r = R['ele']
    c.limb(9, 27, 36, 15, 6, r) if False else None
    c.limb(10, 26, 15, 38, 6, r, far=True); c.limb(33, 26, 38, 38, 6, r, far=True)
    c.blob(24, 19, 17, 11, r)
    c.limb(13, 27, 18, 38, 6, r); c.limb(30, 27, 35, 38, 6, r)
    for lx in (13, 30, 10, 33):
        c.px(lx + 1, 36, hx('#f1e8d8')); c.px(lx + 3, 36, hx('#f1e8d8')); c.px(lx + 5, 36, hx('#f1e8d8'))
    c.line([(7, 15), (5, 22), (6, 27)], 1.2, flat=r[3])
    c.blob(6, 28, 1.6, 2.2, R['mane'][3], flat=hx('#6a5a74'))
    c.blob(39, 17, 8, 9.5, r)
    c.line([(43, 23), (45, 28), (45, 33), (42, 37)], 5.2, rp=r, depth=2)
    for yy in (27, 30, 33):
        c.overlay(lambda d, s, yy=yy: d.line([(s(42), s(yy)), (s(47), s(yy))], fill=255), r[2])
    c.blob(32, 18, 6.5, 9, R['ele_ear'], tilt=.12)              # ucho
    c.blob(32.5, 18.5, 4, 6.5, R['pink'], tilt=.12, flat=hx('#f7b5c6'))
    c.blob(32, 17, 3.6, 5.5, R['pink'], tilt=.12, flat=hx('#fbc8d6'))
    c.line([(43, 24), (47, 27)], 1.6, flat=hx('#fff6e4'))
    c.eye(42, 15); c.blush(41, 20)
    return c.done()

def giraffe():
    c = Cv(40, 62); r = R['gir']
    c.limb(8, 38, 11, 58, 3, r, far=True, hoof=hx('#6b4535')); c.limb(23, 38, 26, 58, 3, r, far=True, hoof=hx('#6b4535'))
    c.blob(14, 34, 11.5, 7.5, r)
    c.poly([(19, 33), (25, 33), (32, 10), (26, 8)], r)             # krk
    c.line([(26, 9), (20, 31)], 1.2, flat=hx('#9a5a2a'))            # hříva
    c.limb(5, 37, 8, 58, 3, r, hoof=hx('#6b4535')); c.limb(20, 37, 23, 58, 3, r, hoof=hx('#6b4535'))
    c.line([(3, 31), (1, 38), (2, 43)], 1.2, flat=hx('#9a5a2a')); c.blob(2, 44, 1.6, 2.4, r, flat=hx('#6b4535'))
    c.blob(30, 7, 6, 3.8, r, tilt=-.25)
    c.blob(35, 9, 3.4, 2.8, R['tan'], tilt=-.2)
    c.px(37, 9, hx('#6a4a44')); c.px(36, 9, hx('#6a4a44'))
    c.line([(28, 4), (27, 0)], 1.2, flat=hx('#9a5a2a')); c.line([(31, 3), (32, -1)], 1.2, flat=hx('#9a5a2a'))
    c.blob(27, -1, 1.6, 1.6, r, flat=hx('#6b4535')); c.blob(32, -2, 1.6, 1.6, r, flat=hx('#6b4535'))
    c.blob(25.5, 6, 2.2, 1.6, r, tilt=.8, flat=hx('#f0b03c'))
    c.eye(31, 5); c.blush(31, 8)
    rng = random.Random(4)
    spots = [(8, 31), (13, 36), (17, 31), (10, 38), (21, 29), (24, 22), (27, 15), (22, 36), (6, 36), (26, 11), (24, 27), (29, 9)]
    for (sx, sy) in spots:
        c.overlay(lambda d, s, sx=sx, sy=sy: d.polygon([(s(sx), s(sy - 1.6)), (s(sx + 2.2), s(sy)), (s(sx), s(sy + 1.8)), (s(sx - 2.2), s(sy))], fill=255), hx('#c4742e'))
    for (sx, sy, ww) in [(6, 44, 3), (21, 46, 3), (9, 50, 3), (24, 52, 3)]:
        c.overlay(lambda d, s, sx=sx, sy=sy, ww=ww: d.rectangle([s(sx - 1), s(sy), s(sx + ww - 1), s(sy + 2)], fill=255), hx('#c4742e'))
    return c.done()

def zebra():
    c = Cv(40, 34); r = R['zeb']; k = hx('#403b55')
    c.limb(9, 21, 12, 32, 3, r, far=True, hoof=k); c.limb(26, 21, 29, 32, 3, r, far=True, hoof=k)
    c.blob(17, 17, 12.5, 6.8, r)
    c.poly([(24, 16), (29, 16), (33, 6), (28, 5)], r)
    c.limb(7, 21, 10, 32, 3, r, hoof=k); c.limb(24, 21, 27, 32, 3, r, hoof=k)
    c.line([(4, 13), (2, 20), (3, 25)], 1.2, flat=k)
    c.blob(32, 7, 5, 3.4, r, tilt=-.35)
    c.blob(36, 9.5, 2.6, 2.4, ramp('#9a94b4', '#7d7796', '#675f80', '#4f4968'))
    c.line([(29, 5), (23, 15)], 1.6, flat=k)                         # hříva
    c.blob(29, 3.5, 1.5, 1.8, r, flat=k); c.eye(32, 6)
    c.blush(31, 9, hx('#f6a8bf'))
    for xx in range(7, 25, 4):
        c.overlay(lambda d, s, xx=xx: d.polygon([(s(xx), s(10)), (s(xx + 1.2), s(10)), (s(xx - 1.8), s(24)), (s(xx - 3), s(24))], fill=255), k)
    for (a, b) in [(25, 14), (29, 10)]:
        c.overlay(lambda d, s, a=a, b=b: d.line([(s(a), s(b + 3)), (s(a + 4), s(b - 1))], fill=255, width=max(1, int(K))), k)
    for yy in (25, 28):
        for lx in (7, 9, 24, 26):
            c.overlay(lambda d, s, lx=lx, yy=yy: d.line([(s(lx), s(yy)), (s(lx + 3), s(yy))], fill=255), k)
    return c.done()

def lion():
    c = Cv(40, 30); r = R['lion']; m = R['mane']
    c.limb(6, 17, 10, 27, 4, r, far=True); c.limb(20, 17, 24, 27, 4, r, far=True)
    c.blob(14, 16, 11, 6.5, r)
    c.limb(4, 18, 8, 28, 4, r); c.limb(19, 18, 23, 28, 4, r)
    c.line([(3, 13), (0, 18), (1, 24)], 1.4, flat=r[2]); c.blob(1, 25, 2, 2.6, m, flat=m[2])
    c.blob(27, 17, 7, 6, m)                                    # hříva na hrudi
    c.blob(28, 12, 9.5, 9.5, m)
    c.blob(30, 14.5, 5.5, 5, r)
    c.blob(34, 17, 3.2, 2.5, R['tan'])
    c.px(36, 16, hx('#d4607a')); c.px(37, 16, hx('#d4607a')); c.px(36, 17, hx('#6a3a3a'))
    c.blob(25, 6, 2.2, 2.2, r); c.blob(33, 6, 2.2, 2.2, r)
    c.eye(31, 12); c.blush(29, 17)
    return c.done()

def tiger():
    c = Cv(40, 30); r = R['tig']; k = hx('#3a2a32')
    c.limb(6, 17, 10, 27, 4, r, far=True); c.limb(21, 17, 25, 27, 4, r, far=True)
    c.blob(14, 16, 11.5, 6.5, r)
    c.limb(4, 18, 8, 28, 4, r); c.limb(20, 18, 24, 28, 4, r)
    c.line([(3, 13), (0, 18), (1, 25)], 1.4, flat=r[2]); c.px(1, 25, k); c.px(1, 26, k)
    c.blob(28.5, 13, 6.8, 6, r)
    c.blob(31.5, 16, 4, 3.2, R['white'])
    c.px(34, 15, hx('#d4607a')); c.px(35, 15, hx('#d4607a'))
    c.blob(24, 7.5, 2.4, 2.4, r); c.blob(32, 7, 2.4, 2.4, r)
    c.eye(30, 11); c.blush(28, 16)
    for xx in range(7, 23, 4):
        c.overlay(lambda d, s, xx=xx: d.polygon([(s(xx), s(10)), (s(xx + 1.0), s(10)), (s(xx - .2), s(19)), (s(xx - 1.2), s(19))], fill=255), k)
    for yy in (22,):
        for lx in (4, 6, 20, 22):
            c.overlay(lambda d, s, lx=lx, yy=yy: d.line([(s(lx), s(yy)), (s(lx + 3), s(yy))], fill=255), k)
    for a in (26, 28.5, 31):
        c.overlay(lambda d, s, a=a: d.line([(s(a), s(7)), (s(a), s(9.5))], fill=255), k)
    return c.done()

def panda():
    c = Cv(30, 30); w = R['pan_w']; b = R['pan_b']
    c.blob(7, 25, 4.5, 3.2, b); c.blob(21, 25, 4.5, 3.2, b)
    c.blob(14, 19, 9.5, 8.5, w)
    c.blob(6, 19, 3.2, 5.5, b, tilt=.15); c.blob(22, 19, 3.2, 5.5, b, tilt=-.15)
    c.blob(14, 9, 8.5, 7, w)
    c.blob(7, 3.5, 3, 3, b); c.blob(21, 3.5, 3, 3, b)
    c.blob(10, 9, 2.5, 3.2, b, tilt=.5); c.blob(18, 9, 2.5, 3.2, b, tilt=-.5)
    c.px(10, 8, hx('#ffffff')); c.px(18, 8, hx('#ffffff'))
    c.px(14, 11, hx('#2a2640')); c.px(13, 11, hx('#2a2640')); c.px(14, 12, hx('#2a2640'))
    c.px(12, 13, hx('#c96b88')); c.px(16, 13, hx('#c96b88'))
    c.line([(23, 12), (24, 24)], 1.8, flat=hx('#6fc060'))
    c.px(23.5, 17, hx('#4a9a48')); c.px(23.5, 21, hx('#4a9a48'))
    return c.done()

def hippo():
    c = Cv(46, 28); r = R['hip']
    c.limb(9, 17, 15, 26, 5, r, far=True); c.limb(26, 17, 32, 26, 5, r, far=True)
    c.blob(20, 15, 15.5, 8.5, r)
    c.limb(6, 17, 12, 26, 5.5, r); c.limb(24, 17, 30, 26, 5.5, r)
    c.line([(5, 12), (3, 15)], 1.3, flat=r[2])
    c.blob(35, 14, 8, 7, r)
    c.blob(40, 17, 5.5, 5, ramp('#f2c6d8', '#e6a8c2', '#c98aa6', '#a96b88'))
    c.px(40, 14, hx('#4a2f4a')); c.px(43, 14, hx('#4a2f4a')); c.px(41, 14, hx('#4a2f4a'))
    c.line([(36, 19), (44, 19)], 1.2, flat=hx('#7a4a66'))
    c.px(37, 20, hx('#fff6e4')); c.px(42, 20, hx('#fff6e4'))
    c.blob(31, 8, 2.2, 2.2, r); c.blob(37, 8.5, 2.4, 2.4, r, flat=r[1]); c.eye(36, 8)
    c.blush(34, 16, hx('#f2a0c0'))
    return c.done()

def flamingo():
    c = Cv(18, 40); r = R['fla']
    c.line([(8, 35), (8, 25)], 1.0, flat=hx('#ff7aa5'))
    c.line([(10, 35), (11, 31), (9, 26)], 1.0, flat=hx('#ff7aa5'))
    c.blob(8, 21, 6.5, 5, r, tilt=-.2)
    c.poly([(2, 20), (-1, 24), (4, 23)], r)
    c.blob(7, 21, 4, 3, ramp('#ffb5cf', '#f986ab', '#e8628f', '#c8467a'), tilt=-.2)
    c.line([(5, 23), (3, 25)], 1.0, flat=hx('#3a2a3a'))
    c.line([(12, 18), (14, 13), (10, 9), (11, 5)], 2.4, rp=r, depth=1)
    c.blob(12, 3.5, 2.6, 2.3, r)
    c.poly([(13, 3), (17, 5.5), (15, 7), (13, 6)], flat=hx('#fff0f5')); c.px(16, 6, hx('#2a1f2d')); c.px(15, 6, hx('#2a1f2d'))
    c.eye(11, 2.5)
    return c.done()

def penguin():
    c = Cv(14, 18); r = R['pen']
    c.blob(7, 11, 5.4, 6.8, r)
    c.blob(7.4, 12, 3.6, 5.2, R['white'])
    c.blob(7, 4.5, 4.2, 3.6, r)
    c.poly([(9, 5), (13, 6.3), (9, 7.5)], flat=hx('#ffa23c'))
    c.line([(2, 9), (0.5, 13)], 1.6, flat=r[2]); c.line([(12, 9), (13.5, 13)], 1.6, flat=r[2])
    c.rect(4, 17, 7, 18, hx('#ffa23c')); c.rect(8, 17, 11, 18, hx('#ffa23c'))
    c.eye(7, 3.2); c.blush(5, 7, hx('#ff9bb0'))
    return c.done()

def monkey():
    c = Cv(24, 28); r = R['mon']
    c.line([(15, 22), (20, 19), (21, 12), (18, 9)], 2.2, rp=r, depth=1)
    c.blob(10, 19, 5.5, 5.8, r)
    c.blob(6, 25, 2.8, 2, r); c.blob(14, 25, 2.8, 2, r)
    c.blob(10, 9, 5.2, 5, r)
    c.blob(10, 10, 3.6, 3.6, R['tan'])
    c.blob(4, 9, 2, 2.4, R['tan']); c.blob(16, 9, 2, 2.4, R['tan'])
    c.eye(8, 8); c.px(12, 8, hx('#2a1f2d')); c.px(10, 12, hx('#6a3a3a')); c.px(11, 12, hx('#6a3a3a'))
    c.blush(7, 11); c.blush(12, 11)
    c.blob(10, 20, 3, 3.4, R['tan'])
    return c.done()


def rhino():
    c = Cv(48, 30); r = R['rhi']
    c.limb(10, 18, 16, 27, 5, r, far=True); c.limb(28, 18, 34, 27, 5, r, far=True)
    c.blob(21, 16, 16, 9, r)
    c.limb(7, 18, 13, 28, 5.5, r); c.limb(26, 18, 32, 28, 5.5, r)
    c.line([(5, 12), (3, 18)], 1.3, flat=r[2])
    c.blob(37, 17, 8.5, 7, r, tilt=.12)
    c.blob(43, 20, 4.5, 4, r)
    c.poly([(40, 14), (44, 5), (45, 15)], ramp('#fff6e4', '#f1dcb4', '#d8bd8a', '#b89a68'))   # roh
    c.poly([(36, 12), (38, 8), (39, 13)], flat=hx('#e6d2a8'))
    c.blob(32, 10, 2.4, 3, r, tilt=-.3); c.eye(37, 14); c.px(45, 20, hx('#4a3a4a')); c.px(44, 19, hx('#4a3a4a'))
    c.line([(38, 22), (46, 22)], 1.0, flat=hx('#6a5a74'))
    c.blush(35, 18, hx('#f2a0c0'))
    return c.done()

def bear():
    c = Cv(40, 32); r = R['bear']
    c.limb(8, 19, 13, 29, 5, r, far=True); c.limb(24, 19, 29, 29, 5, r, far=True)
    c.blob(17, 17, 12.5, 8, r)
    c.limb(6, 20, 11, 30, 5, r); c.limb(22, 20, 27, 30, 5, r)
    c.blob(4, 14, 2.2, 2.2, r)
    c.blob(30, 15, 7.2, 6.8, r)
    c.blob(35, 18, 3.6, 3, R['tan'])
    c.px(37, 17, hx('#2a1f2d')); c.px(38, 17, hx('#2a1f2d')); c.px(36, 20, hx('#6a3a3a'))
    c.blob(25, 9, 2.6, 2.6, r); c.blob(33, 8.5, 2.6, 2.6, r)
    c.blob(25, 9, 1.2, 1.2, R['tan']); c.blob(33, 8.5, 1.2, 1.2, R['tan'])
    c.eye(32, 13); c.blush(30, 18)
    return c.done()

def turtle():
    c = Cv(26, 16); r = R['shell']; sk = ramp('#d9e8a0', '#bcd477', '#98b457', '#7a9440')
    c.blob(21, 9, 3.2, 2.8, sk)
    c.blob(5, 13, 2.4, 1.8, sk); c.blob(17, 13, 2.4, 1.8, sk)
    c.blob(12, 8, 9.5, 6, r)
    for (x, y) in [(9, 6), (14, 5.5), (12, 9), (7, 9.5), (17, 9.5)]:
        c.overlay(lambda d, s, x=x, y=y: d.ellipse([s(x - 1.6), s(y - 1.2), s(x + 1.6), s(y + 1.2)], outline=255), r[3])
    c.eye(22, 8); c.blush(21, 10)
    return c.done()

ANIMALS_EXTRA = [('rhino', rhino), ('bear', bear), ('turtle', turtle)]
ANIMAL_K = dict(giraffe=0.76, elephant=0.9, hippo=0.9, rhino=0.9, penguin=1.0, flamingo=0.95)

def _wrap(fn, k):
    def f():
        global K
        old = K; K = k
        try: return fn()
        finally: K = old
    f.__name__ = fn.__name__
    return f

ANIMALS = [('elephant', elephant), ('giraffe', giraffe), ('zebra', zebra), ('lion', lion), ('tiger', tiger),
           ('panda', panda), ('hippo', hippo), ('flamingo', flamingo), ('penguin', penguin), ('monkey', monkey)] + ANIMALS_EXTRA
ANIMALS = [(n, _wrap(f, ANIMAL_K.get(n, 0.9))) for n, f in ANIMALS]

def sheet(scale=5):
    items = [(n, f()) for n, f in ANIMALS]
    pad = 10
    W = sum(im.width * 2 + pad * 3 for _, im in items) // 2 + pad
    cols = 7
    cellw = max(im.width for _, im in items) * 2 + 3 * pad
    cellh = max(im.height for _, im in items) + 2 * pad
    sh = Image.new('RGBA', (cols * cellw, 2 * cellh), za.S['grass'][0])
    px = sh.load()
    rng = random.Random(1)
    for y in range(sh.height):
        for x in range(sh.width):
            if rng.random() < .35: px[x, y] = rng.choice(za.S['grass'])
    for k, (n, im) in enumerate(items):
        cx, cy = (k % cols) * cellw + pad, (k // cols) * cellh + pad
        sh.alpha_composite(im, (cx, cy + cellh - pad * 2 - im.height + 8))
        fl = im.transpose(Image.FLIP_LEFT_RIGHT)
        sh.alpha_composite(fl, (cx + im.width + pad, cy + cellh - pad * 2 - im.height + 8))
    return sh.resize((sh.width * scale, sh.height * scale), Image.NEAREST)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'animals_out'
    os.makedirs(out, exist_ok=True)
    za.load_style('C_hybrid')
    sheet(4).save(f'{out}/animals_sheet.png')
    print('ok')


def scene_with_new_animals(out):
    """scéna stylu C s novými zvířaty (přepíše staré funkce v zoo_art)"""
    za.load_style('C_hybrid')
    for n in ('elephant', 'giraffe', 'zebra', 'lion', 'panda', 'flamingo', 'penguin'):
        setattr(za, n, dict(ANIMALS)[n])
    sc = za.make_scene2()
    sc = za.tone(sc, za.S['sat'], za.S['bright']); za.hud(sc, None)
    sc.resize((sc.width * 3, sc.height * 3), Image.NEAREST).save(out)
