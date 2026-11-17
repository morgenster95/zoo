"""Profilovka v2 (vlastní návrh): ohrazená miniaturní zoo na plovoucí dlaždici. Návštěvníci jsou maličcí před bránou, uvnitř ohrady dva plameňáci u rybníčku.
Nativně 108×108, zvětšeno 10×. Výstup: marketing/profile/avatar_zoo_v2.png"""
import json, os, random, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import zoo_art as za, visitors
from zoo_art import hx
ROOT = os.path.join(HERE, '..', '..')
za.load_style('C_hybrid')
meta = json.load(open(f'{ROOT}/web/public/assets/props.json')); atlas = Image.open(f'{ROOT}/web/public/assets/atlas.png').convert('RGBA')
def prop(n): m = meta[n]; return atlas.crop((m['x'], m['y'], m['x'] + m['w'], m['y'] + m['h'])), (m['ax'], m['ay'])
N = 108
img = Image.new('RGBA', (N, N), hx('#ffb86b'))
d = ImageDraw.Draw(img)
d.ellipse([-5, -5, N + 4, N + 4], fill=hx('#ff9a5a'))
d.ellipse([7, 7, N - 8, N - 8], fill=hx('#ffd29a'))
d.ellipse([16, 34, N - 17, N - 8], fill=hx('#ffe6bf'))
za.OXY = (54, 40); P = za.P
L, B, R = P(0, 3), P(3, 3), P(3, 0); T = 8
d.polygon([L, B, (B[0], B[1] + T), (L[0], L[1] + T)], fill=hx('#b07a4a')); d.polygon([B, R, (R[0], R[1] + T), (B[0], B[1] + T)], fill=hx('#8a5a32'))
for k in (3, 6):
    d.line([(L[0], L[1] + k), (B[0], B[1] + k)], fill=hx('#9a6a3e')); d.line([(B[0], B[1] + k), (R[0], R[1] + k)], fill=hx('#6f4626'))
for i in range(3):
    for j in range(3):
        kind = 'water' if (i, j) in ((1, 0), (2, 0)) else ('dirt' if j == 2 and i in (0, 1, 2) and False else 'grass')
        x, y = P(i, j); img.alpha_composite(za.tile_img(kind, random.Random(5 + i * 3 + j)), (int(x - 16), int(y)))
# cestička před bránou
for (i, j) in [(1, 2), (1, 1)]:
    x, y = P(i, j); img.alpha_composite(za.tile_img('dirt', random.Random(9 + i + j)), (int(x - 16), int(y)))
def put(name, i, j, flip=False):
    im, a = prop(name)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); a = (im.width - a[0], a[1])
    x, y = P(i, j); img.alpha_composite(im, (int(x - a[0]), int(y - a[1])))
items = []   # (hloubka, funkce)
f0, f1 = 0.5, 2.5
for k in range(2):
    items.append((f0 + k + f0 + 0.1, lambda k=k: put('seg_i', f0 + k, f0)))            # zadní plot podél i
    items.append((f0 + f0 + k + 0.1, lambda k=k: put('seg_j', f0, f0 + k)))            # zadní plot podél j
    items.append((f1 + f0 + k + 0.1, lambda k=k: put('seg_j', f1, f0 + k)))            # pravý plot
for (i, j) in [(f0, f0), (1.5, f0), (f0, 1.5), (f1, f0), (f1, 1.5)]:
    items.append((i + j + 0.3, lambda i=i, j=j: put('post' + str((int(i * 2) + int(j * 2)) & 1), i, j)))
items.append((1.0 + 1.0, lambda: put('a_flamingo', 1.55, 1.05, True)))
items.append((1.1 + 1.6, lambda: put('a_flamingo', 0.95, 1.85)))
# vstup: otevřená přední strana (bez trámu), jen dva nízké sloupky po stranách cestičky
items.append((f0 + f1 + 0.4, lambda: put('post0', f0, f1)))
items.append((f1 + f1 + 0.4, lambda: put('post1', f1, f1)))
for k, (ii, jj, kind, sp, dr) in enumerate([(0.6, 3.05, 'balloon', 31, 'NE'), (1.35, 3.0, 'plain', 12, 'NE'), (2.05, 3.05, 'plain', 22, 'NE')]):
    spec = visitors.new_spec(sp, kind=kind, kid=(k == 1))
    v = visitors.visitor(spec, dr, 0, shadow=True)
    items.append((ii + jj + 0.5, lambda v=v, ii=ii, jj=jj: img.alpha_composite(v, (int(P(ii, jj)[0] - v.width // 2), int(P(ii, jj)[1] - v.height + 3)))))
for _, fn in sorted(items, key=lambda e: e[0]): fn()
for (sx_, sy_, c) in [(14, 42, '#ffffff'), (95, 40, '#fff2a6'), (92, 64, '#ffffff'), (18, 64, '#fff2a6')]:
    d.rectangle([sx_ - 1, sy_, sx_ + 1, sy_], fill=hx(c)); d.rectangle([sx_, sy_ - 1, sx_, sy_ + 1], fill=hx(c))
FONT = za.FONT
def text(txt, cx, y, sc, col, ol):
    w = sum((len(FONT[c][0]) + 1) * sc for c in txt) - sc; x0 = cx - w // 2
    for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, 2), (1, 2), (-1, 2)]:
        xx = x0
        for ch in txt:
            for yy, row in enumerate(FONT[ch]):
                for k, c in enumerate(row):
                    if c == '1': d.rectangle([xx + k * sc + dx, y + yy * sc + dy, xx + k * sc + dx + sc - 1, y + yy * sc + dy + sc - 1], fill=ol)
            xx += (len(FONT[ch][0]) + 1) * sc
    xx = x0
    for ch in txt:
        for yy, row in enumerate(FONT[ch]):
            for k, c in enumerate(row):
                if c == '1':
                    d.rectangle([xx + k * sc, y + yy * sc, xx + k * sc + sc - 1, y + yy * sc + sc - 1], fill=col)
                    d.rectangle([xx + k * sc, y + yy * sc + sc - 1, xx + k * sc + sc - 1, y + yy * sc + sc - 1], fill=hx('#d9742a'))
        xx += (len(FONT[ch][0]) + 1) * sc
text('ZOO', 54, 5, 4, hx('#fff3d6'), hx('#6a3a20'))
out = os.path.join(ROOT, 'marketing', 'profile'); big = img.resize((N * 10, N * 10), Image.NEAREST); big.save(f'{out}/avatar_zoo_v2.png')
tiny = big.resize((110, 110), Image.NEAREST); m2 = Image.new('L', (110, 110), 0); ImageDraw.Draw(m2).ellipse([0, 0, 109, 109], fill=255)
c2 = Image.new('RGBA', (110, 110), (30, 30, 30, 255)); c2.paste(tiny, (0, 0), m2); c2.save(f'{out}/avatar_zoo_v2_110px_preview.png'); print('ok')
