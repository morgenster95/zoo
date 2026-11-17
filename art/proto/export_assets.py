"""Export spritů pro web: python3 art/proto/export_assets.py  (potřebuje Pillow; viz docs/ART.md)
Výstup do web/public/assets:
  tiles.png + tiles.json       dlaždice terénu 32×16 (5 druhů × 4 varianty)
  visitors.png + visitors.json  256 vzhledů × 4 směry × 4 snímky chůze (index = look*16 + dir*4 + frame)
  props.png + props.json        zvířata, stavby, stromy, plot… s kotvami
  font.json                     3×5 pixelové písmo (pro tabuli mincí a HUD)"""
import json, os, sys, random
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zoo_art as za, animals, visitors, mini_zoo as mz, vegetation as veg
from zoo_art import hx

OUT = os.path.join(HERE, '..', '..', 'web', 'public', 'assets')
os.makedirs(OUT, exist_ok=True)
za.load_style('C_hybrid')

def save(im, name): im.save(os.path.join(OUT, name), optimize=True)

# ---------- dlaždice
kinds = ['grass', 'dirt', 'cobble', 'water', 'ice']
tiles = Image.new('RGBA', (32 * 4, 16 * len(kinds)), (0, 0, 0, 0))
for r, k in enumerate(kinds):
    for v in range(4):
        tiles.alpha_composite(za.tile_img(k, random.Random(v + 1)), (v * 32, r * 16))
save(tiles, 'tiles.png')
json.dump({'tw': 32, 'th': 16, 'kinds': kinds, 'variants': 4}, open(os.path.join(OUT, 'tiles.json'), 'w'))

# ---------- návštěvníci
LOOKS = 256
specs = [visitors.new_spec(5000 + i) for i in range(LOOKS)]
sprites = []
for i, sp in enumerate(specs):
    row = []
    for d in visitors.DIRS:
        for f in range(4):
            row.append(visitors.visitor(sp, d, f, shadow=True))
    sprites.append(row)
cw = max(s.width for row in sprites for s in row)
ch = max(s.height for row in sprites for s in row)
cols = 32
rows = (LOOKS * 16 + cols - 1) // cols
atlas = Image.new('RGBA', (cols * cw, rows * ch), (0, 0, 0, 0))
for i, row in enumerate(sprites):
    for k, s in enumerate(row):
        idx = i * 16 + k
        x = (idx % cols) * cw + (cw - s.width) // 2
        y = (idx // cols) * ch + (ch - s.height)
        atlas.alpha_composite(s, (x, y))
json.dump({'cellW': cw, 'cellH': ch, 'cols': cols, 'looks': LOOKS, 'dirs': visitors.DIRS, 'frames': 4,
           'anchorY': (ch - 3) / ch, 'kinds': [s['kind'] for s in specs]}, open(os.path.join(OUT, 'visitors.json'), 'w'))

# ---------- rekvizity a zvířata
props = {}
def add(name, im, anchor=None):
    props[name] = (im, anchor or (im.width // 2, im.height - 2))

for n, f in animals.ANIMALS: add('a_' + n, f())
for n, f in veg.ALL:
    im = f()
    add(n, im, (im.width // 2, im.height - 4 if n not in ('flowers', 'tuft', 'bush1', 'bush2', 'reeds') else im.height - 2))
for n, fn in [('gate', mz.gate_poor), ('bench', mz.bench), ('crate', mz.crate), ('hay', mz.hay), ('weeds', mz.weeds), ('q_sign', mz.question_sign), ('plot', mz.stake_plot)]:
    im, a = fn(); add(n, im, a)
im, a = mz.sign_board('WELCOME'); add('sign_welcome', im, a)
body, (ax, ay) = za.house(1.2, 1.0, 14, 8, hx('#c9a36b'), hx('#b8503a'), windows=0, door=None, timber=False, seed=3)
bb = body.getbbox(); body = body.crop((0, bb[1], body.width, body.height)); ay -= bb[1]
body = za.outlined(body, hx('#3d2a28')); add('kasa', body, (ax + 1, ay + 1))
add('post0', mz.rough_fence_post(0)); add('post1', mz.rough_fence_post(1))
from PIL import ImageDraw
for name, dx in (('seg_i', 16), ('seg_j', -16)):
    im = Image.new('RGBA', (40, 30), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    for lift, col in ((8, hx('#d9b57a')), (4, hx('#c49a68'))):
        g.line([(20, 14 - lift), (20 + dx, 22 - lift)], fill=col); g.line([(20, 15 - lift), (20 + dx, 23 - lift)], fill=hx('#8a5a32'))
    add(name, za.outlined(im, hx('#4a2f20')), (21, 15))
for n, (im, a) in {'b_modern': mz.modern(2.0, 1.4, 18, seed=1), 'b_african': mz.african_hut(), 'b_asian': mz.pagoda(), 'b_andes': mz.stepped_adobe(),
                   'b_classic': za.house(1.6, 1.0, 16, 10, za.S['walls'][0], za.S['roofs'][0], windows=2, door=.62, seed=1),
                   'b_dome': za.dome(1.6), 'b_carousel': za.carousel(), 'b_igloo': za.igloo(), 'b_cart': za.candy_cart()}.items():
    add(n, im, a)

# shelf packing
W = 512
items = sorted(props.items(), key=lambda kv: -kv[1][0].height)
x = y = rowh = 0
meta = {}
placed = []
for name, (im, a) in items:
    if x + im.width + 1 > W: x = 0; y += rowh + 1; rowh = 0
    placed.append((name, im, x, y)); meta[name] = {'x': x, 'y': y, 'w': im.width, 'h': im.height, 'ax': a[0], 'ay': a[1]}
    x += im.width + 1; rowh = max(rowh, im.height)
H = y + rowh + 1
# jedna textura pro všechno (návštěvníci nahoře, rekvizity pod nimi): Pixi pak kreslí seřazené sprity v pár dávkách
AW = max(W, atlas.width); AH = atlas.height + H
big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
big.alpha_composite(atlas, (0, 0))
for name, im, px, py in placed:
    big.alpha_composite(im, (px, atlas.height + py)); meta[name]['y'] += atlas.height
save(big, 'atlas.png')
json.dump(meta, open(os.path.join(OUT, 'props.json'), 'w'))
pa = big

json.dump(za.FONT, open(os.path.join(OUT, 'font.json'), 'w'))
print('visitors', atlas.size, 'cell', cw, ch, '| props', pa.size, len(meta))
