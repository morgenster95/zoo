"""Rozřeže sheety z PixelLabu (art/pixellab/*.png) na jednotlivé sprity do art/pixellab/sprites/.
Postup: souvislé skvrny (8-okolí, slepené do 3 px kvůli stínům), seřazené po řádcích zleva doprava podle seznamu jmen.
Stín zvířat (světle šedozelená 215,219,196) se přebarví na poloprůhlednou tmavou zeleň, ať sedí na trávě."""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'pixellab')
OUT = os.path.join(SRC, 'sprites'); os.makedirs(OUT, exist_ok=True)

ANIMALS = ['elephant', 'giraffe', 'zebra', 'lion', 'tiger', 'panda', 'hippo', 'flamingo', 'penguin', 'monkey', 'rhino', 'bear']
DECOR = ['bench_wood', 'bench_green', 'bench_stone', 'bench_color', 'lamp', 'bin', 'drink', 'signpost',
         'picnic', 'planter', 'fountain', 'hedge', 'statue', 'kiosk', 'palm_pot', 'balloons']

def slice_sheet(fn, names, rows, shadow=False, prefix='', grow=2):
    im = Image.open(os.path.join(SRC, fn)).convert('RGBA'); a = np.array(im)
    if shadow:
        m = (a[:, :, 0] == 215) & (a[:, :, 1] == 219) & (a[:, :, 2] == 196) & (a[:, :, 3] > 0)
        a[m] = (40, 90, 45, 110)
    mask = a[:, :, 3] > 0
    grown = ndi.binary_dilation(mask, structure=np.ones((3, 3)), iterations=grow) if grow > 0 else mask
    lab, n = ndi.label(grown, structure=np.ones((3, 3)))
    comps = []
    for k in range(1, n + 1):
        ys, xs = np.where((lab == k) & mask)
        if len(ys) < 25: continue
        comps.append((ys.min(), ys.max(), xs.min(), xs.max(), k))
    if len(comps) != len(names):
        print(f'POZOR {fn}: nalezeno {len(comps)} skvrn, čekám {len(names)}'); 
    # řádky podle středu y
    comps.sort(key=lambda c: (c[0] + c[1]) / 2)
    per = len(names) // rows
    ordered = []
    for r in range(rows):
        chunk = sorted(comps[r * per:(r + 1) * per], key=lambda c: c[2])
        ordered += chunk
    for name, (y0, y1, x0, x1, k) in zip(names, ordered):
        sub = a[y0:y1 + 1, x0:x1 + 1].copy()
        keep = ((lab[y0:y1 + 1, x0:x1 + 1] == k) & (sub[:, :, 3] > 0))
        sub[~keep] = 0
        Image.fromarray(sub).save(os.path.join(OUT, f'{prefix}{name}.png'))
    return len(ordered)

B1 = ['lodge', 'barn', 'pagoda', 'penguin_house', 'treehouse', 'aquarium', 'cafe', 'shop', 'aviary']
B2 = ['carousel', 'ferris', 'station', 'playground', 'toilets', 'clinic', 'ticket', 'gate', 'popcorn']

def add_shadow(prefix):
    """chunky zvířata nemají stín: pod nohy přidá poloprůhlednou elipsu (stejná jako u ostatních)"""
    for fn in os.listdir(OUT):
        if not (fn.startswith(prefix) and fn.endswith('.png')): continue
        im = Image.open(os.path.join(OUT, fn)).convert('RGBA')
        out = Image.new('RGBA', (im.width + 2, im.height + 3), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(out)
        cx = out.width // 2; rx = max(5, int(im.width * 0.42))
        d.ellipse([cx - rx, im.height - 2, cx + rx, im.height + 1], fill=(40, 90, 45, 110))
        out.alpha_composite(im, (1, 0))
        out.save(os.path.join(OUT, fn))

B1 = ['lodge', 'barn', 'pagoda', 'penguin_house', 'treehouse', 'aquarium', 'cafe', 'shop', 'aviary']
B2 = ['carousel', 'ferris', 'station', 'playground', 'toilets', 'clinic', 'ticket', 'gate', 'popcorn']

if __name__ == '__main__':
    # aktuální sada = „chunky“ (hustota pixelů jako naše sprity); detailní sheety zůstávají v sprites_detailed
    print('zvířata:', slice_sheet('animals_sheet_chunky_1.png', ANIMALS, 3, prefix='a_', grow=1)); add_shadow('a_')
    print('dekorace:', slice_sheet('decor_sheet_chunky_1.png', DECOR, 4, prefix='d_', grow=0))
    print('budovy:', slice_sheet('buildings_sheet_3_chunky.png', B1, 3, prefix='bp_', grow=2), slice_sheet('buildings_sheet_4_chunky.png', B2, 3, prefix='bp_', grow=2))
    im = Image.open(os.path.join(SRC, 'ferris_chunky.png')).convert('RGBA'); im.crop(im.getbbox()).save(os.path.join(OUT, 'bp_ferris.png'))
