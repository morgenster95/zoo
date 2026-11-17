"""Profilový obrázek IG: jedna plovoucí izometrická dlaždice (tráva + hlína) s plameňákem, návštěvníkem, palmou a nápisem ZOO.
Nativně 90×90 px, zvětšeno 12× (1080²). Výstup: marketing/profile/avatar_zoo.png (+ 320px náhled)."""
import json, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import zoo_art as za, visitors
from zoo_art import hx
ROOT = os.path.join(HERE, '..', '..')
za.load_style('C_hybrid')
meta = json.load(open(f'{ROOT}/web/public/assets/props.json')); atlas = Image.open(f'{ROOT}/web/public/assets/atlas.png').convert('RGBA')
def prop(n): m = meta[n]; return atlas.crop((m['x'], m['y'], m['x'] + m['w'], m['y'] + m['h'])), (m['ax'], m['ay'])
N = 120
img = Image.new('RGBA', (N, N), hx('#3fa9d6'))
d = ImageDraw.Draw(img)
d.ellipse([-4, -4, N + 3, N + 3], fill=hx('#5ec8f2'))          # kruhový „obal“ (IG ořízne do kruhu)
d.ellipse([8, 8, N - 9, N - 9], fill=hx('#8fe0f5'))
za.OXY = (60, 54)
# tlouštka hlíny pod dlaždicí
def P(i, j): return za.P(i, j)
L, B, R = P(0, 3), P(3, 3), P(3, 0)
T = 10
d.polygon([L, B, (B[0], B[1] + T), (L[0], L[1] + T)], fill=hx('#b07a4a'))
d.polygon([B, R, (R[0], R[1] + T), (B[0], B[1] + T)], fill=hx('#8a5a32'))
for k in (3, 6):                                                   # vrstvy hlíny
    d.line([(L[0], L[1] + k), (B[0], B[1] + k)], fill=hx('#9a6a3e')); d.line([(B[0], B[1] + k), (R[0], R[1] + k)], fill=hx('#6f4626'))
import random
for i in range(3):
    for j in range(3):
        x, y = P(i, j); img.alpha_composite(za.tile_img('grass', random.Random(3 + i * 2 + j)), (int(x - 16), int(y)))
# kameny na okraji
d.rectangle([L[0] + 6, L[1] + 4, L[0] + 8, L[1] + 5], fill=hx('#a39782'))
def put(name, i, j, flip=False, k=2):
    im, a = prop(name)
    im = im.resize((im.width * k, im.height * k), Image.NEAREST); a = (a[0] * k, a[1] * k)        # ikona: objekty 2× hrubší než dlaždice
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); a = (im.width - a[0], a[1])
    x, y = P(i, j); img.alpha_composite(im, (int(x - a[0]), int(y - a[1])))
items = [('d_palm_pot', 2.35, 0.95), ('a_flamingo', 0.95, 1.45)]
vis = visitors.visitor(visitors.new_spec(7, kind='plain', kid=False), 'SW', 0, shadow=True)
draw_list = [(i + j, 'p', n, i, j) for n, i, j in items] + [(1.9 + 2.3, 'v', None, 1.9, 2.3)]
for _, kind, n, i, j in sorted(draw_list, key=lambda e: e[0]):
    if kind == 'p': put(n, i, j)
    else:
        x, y = P(i, j); v2 = vis.resize((vis.width * 2, vis.height * 2), Image.NEAREST); img.alpha_composite(v2, (int(x - v2.width // 2), int(y - v2.height + 4)))
# nápis ZOO nahoře (zlatá, tmavý obrys, stín)
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
                    d.rectangle([xx + k * sc, y + yy * sc + sc - 1, xx + k * sc + sc - 1, y + yy * sc + sc - 1], fill=hx('#e8a020'))
        xx += (len(FONT[ch][0]) + 1) * sc
text('ZOO', 60, 8, 5, hx('#ffd23c'), hx('#3d2a30'))
out = os.path.join(ROOT, 'marketing', 'profile'); os.makedirs(out, exist_ok=True)
big = img.resize((N * 9, N * 9), Image.NEAREST); big.save(f'{out}/avatar_zoo.png')
# náhled v kruhu 320 (jak ho uvidí IG)
sm = big.resize((320, 320), Image.NEAREST); mask = Image.new('L', (320, 320), 0); ImageDraw.Draw(mask).ellipse([0, 0, 319, 319], fill=255)
circ = Image.new('RGBA', (320, 320), (30, 30, 30, 255)); circ.paste(sm, (0, 0), mask); circ.save(f'{out}/avatar_zoo_circle_preview.png')
print('ok')
