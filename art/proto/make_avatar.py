"""Profilový obrázek IG: plovoucí izometrická dlaždice, na ní velký plameňák (hvězda), malý návštěvník, keř a květiny, nahoře nápis ZOO.
Nativně 108×108 px, zvětšeno 10× (1080²). Plameňák je 2× hrubší než dlaždice, aby byl vidět i v kruhu 110 px na profilu.
Výstup: marketing/profile/avatar_zoo.png (+ náhled v kruhu)."""
import json, os, random, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import zoo_art as za, visitors
from zoo_art import hx
ROOT = os.path.join(HERE, '..', '..')
za.load_style('C_hybrid')
meta = json.load(open(f'{ROOT}/web/public/assets/props.json')); atlas = Image.open(f'{ROOT}/web/public/assets/atlas.png').convert('RGBA')
def prop(n):
    m = meta[n]; return atlas.crop((m['x'], m['y'], m['x'] + m['w'], m['y'] + m['h'])), (m['ax'], m['ay'])
N = 108
img = Image.new('RGBA', (N, N), hx('#3fa9d6'))
d = ImageDraw.Draw(img)
d.ellipse([-5, -5, N + 4, N + 4], fill=hx('#5ec8f2'))                       # kruh, který IG ponechá
d.ellipse([7, 7, N - 8, N - 8], fill=hx('#8fe0f5'))
d.ellipse([18, 30, N - 19, N - 10], fill=hx('#b9f0fb'))                     # světlý „podstavec“ za plameňákem

za.OXY = (54, 66)
P = za.P
L, B, R = P(0, 2), P(2, 2), P(2, 0)
T = 8
d.polygon([L, B, (B[0], B[1] + T), (L[0], L[1] + T)], fill=hx('#b07a4a'))
d.polygon([B, R, (R[0], R[1] + T), (B[0], B[1] + T)], fill=hx('#8a5a32'))
for k in (3, 6):
    d.line([(L[0], L[1] + k), (B[0], B[1] + k)], fill=hx('#9a6a3e')); d.line([(B[0], B[1] + k), (R[0], R[1] + k)], fill=hx('#6f4626'))
for i in range(2):
    for j in range(2):
        x, y = P(i, j); img.alpha_composite(za.tile_img('grass', random.Random(3 + i * 2 + j)), (int(x - 16), int(y)))
d.rectangle([L[0] + 5, L[1] + 4, L[0] + 7, L[1] + 5], fill=hx('#a39782'))

def put(name, i, j, k=1, flip=False):
    im, a = prop(name)
    if k != 1: im = im.resize((im.width * k, im.height * k), Image.NEAREST); a = (a[0] * k, a[1] * k)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT); a = (im.width - a[0], a[1])
    x, y = P(i, j); img.alpha_composite(im, (int(x - a[0]), int(y - a[1])))

put('bush1', 0.25, 0.45)                      # vzadu vlevo
put('flowers', 1.75, 0.35)
put('a_flamingo', 1.15, 1.25, k=2, flip=True)   # hvězda ikony
vis = visitors.visitor(visitors.new_spec(7, kind='plain', kid=False), 'SE', 0, shadow=True)
x, y = P(0.45, 1.6); img.alpha_composite(vis, (int(x - vis.width // 2), int(y - vis.height + 3)))
put('flowers', 1.7, 1.8)

# jiskry
for (sx_, sy_, c) in [(15, 44, '#fff2a6'), (93, 40, '#fff2a6'), (88, 62, '#ffffff'), (20, 66, '#ffffff'), (80, 30, '#fff2a6')]:
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
                    d.rectangle([xx + k * sc, y + yy * sc + sc - 1, xx + k * sc + sc - 1, y + yy * sc + sc - 1], fill=hx('#e8a020'))
        xx += (len(FONT[ch][0]) + 1) * sc
text('ZOO', 54, 5, 4, hx('#ffd23c'), hx('#3d2a30'))

out = os.path.join(ROOT, 'marketing', 'profile'); os.makedirs(out, exist_ok=True)
big = img.resize((N * 10, N * 10), Image.NEAREST); big.save(f'{out}/avatar_zoo.png')
sm = big.resize((320, 320), Image.NEAREST); mask = Image.new('L', (320, 320), 0); ImageDraw.Draw(mask).ellipse([0, 0, 319, 319], fill=255)
circ = Image.new('RGBA', (320, 320), (30, 30, 30, 255)); circ.paste(sm, (0, 0), mask); circ.save(f'{out}/avatar_zoo_circle_preview.png')
tiny = big.resize((110, 110), Image.NEAREST); m2 = Image.new('L', (110, 110), 0); ImageDraw.Draw(m2).ellipse([0, 0, 109, 109], fill=255)
c2 = Image.new('RGBA', (110, 110), (30, 30, 30, 255)); c2.paste(tiny, (0, 0), m2); c2.save(f'{out}/avatar_zoo_110px_preview.png')
print('ok')
