"""Náhledovka reelu (cover) podle vzoru @kingsfollowgame: štítek DAY N, velký dvouřádkový nadpis, podtitul a lišta s čísly.
python make_cover.py <podklad.png> <výstup.png> [řádek1] [řádek2] [podtitul]  (výchozí texty pro „Day 1“)"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import zoo_art as za
from zoo_art import hx
import mini_zoo as mz   # rozšířené písmo (A–Z, číslice, ?, !, -, =)
bg_path, out_path = sys.argv[1], sys.argv[2]
L1 = sys.argv[3] if len(sys.argv) > 3 else '1 FOLLOWER'
L2 = sys.argv[4] if len(sys.argv) > 4 else '1 VISITOR'
SUB = sys.argv[5] if len(sys.argv) > 5 else 'WHAT SHOULD WE BUILD NEXT?'
im = Image.open(bg_path).convert('RGBA'); W, H = im.size
# jemné ztmavení shora (čitelnost nadpisu) a zdola
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for y in range(0, 900):
    od.line([(0, y), (W, y)], fill=(20, 40, 20, int(110 * (1 - y / 900))))
for y in range(1250, H):
    od.line([(0, y), (W, y)], fill=(20, 30, 20, int(150 * (y - 1250) / (H - 1250))))
im.alpha_composite(ov)
d = ImageDraw.Draw(im); F = za.FONT
def width(t, sc): return sum((len(F[c][0]) + 1) * sc for c in t) - sc
def draw_text(t, cx, y, sc, col, ol=None, olw=0, shadow=None):
    x0 = cx - width(t, sc) // 2
    def pass_(dx, dy, c):
        x = x0
        for ch in t:
            for yy, row in enumerate(F[ch]):
                for k, v in enumerate(row):
                    if v == '1': d.rectangle([x + k * sc + dx, y + yy * sc + dy, x + k * sc + dx + sc - 1, y + yy * sc + dy + sc - 1], fill=c)
            x += (len(F[ch][0]) + 1) * sc
    if shadow: pass_(0, sc, shadow)
    if ol:
        for dx in range(-olw, olw + 1):
            for dy in range(-olw, olw + 1):
                if dx * dx + dy * dy <= olw * olw + 1: pass_(dx, dy, ol)
    pass_(0, 0, col)
def panel(x0, y0, x1, y1, top, bg='#4a3430', edge='#2a1c1a'):
    d.rectangle([x0, y0, x1, y1], fill=hx(edge)); d.rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], fill=hx(bg)); d.rectangle([x0 + 6, y0 + 6, x1 - 6, y0 + 16], fill=hx(top))
# DAY 1
panel(W // 2 - 190, 400, W // 2 + 190, 540, '#f2b53c')
draw_text('DAY 1', W // 2, 440, 14, hx('#ffe9a8'))
# nadpis
draw_text(L1, W // 2, 620, 19, hx('#fff0c8'), hx('#2a1c0a'), 9, hx('#2a1c0a'))
draw_text(L2, W // 2, 790, 19, hx('#ffd23c'), hx('#2a1c0a'), 9, hx('#2a1c0a'))
# podtitul na tmavém pásu
d.rectangle([0, 1330, W, 1420], fill=(20, 20, 20, 150))
draw_text(SUB, W // 2, 1352, 7, hx('#ffffff'), hx('#1a1a1a'), 3)
# lišta s čísly
def stat(x0, label, val, top, icon):
    panel(x0, 1450, x0 + 440, 1590, top)
    draw_text(label, x0 + 220, 1478, 4, hx('#e8c8a0'))
    draw_text(val, x0 + 250, 1520, 8, hx('#ffd23c') if icon == 'coin' else hx('#fff0c8'))
    ix = x0 + 40
    if icon == 'coin':
        for (dx, dy) in [(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (1, 4), (2, 4), (3, 4)]:
            d.rectangle([ix + dx * 9, 1522 + dy * 9, ix + dx * 9 + 8, 1522 + dy * 9 + 8], fill=hx('#ffc93c'))
    else:
        for (dx, dy) in [(2, 0), (3, 0), (1, 2), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), (4, 3), (1, 4), (4, 4), (1, 5), (4, 5)]:
            d.rectangle([ix + dx * 9, 1518 + dy * 9, ix + dx * 9 + 8, 1518 + dy * 9 + 8], fill=hx('#fff0c8'))
        d.rectangle([ix + 18, 1518, ix + 36, 1536], fill=hx('#fff0c8'))
stat(70, 'COINS', '500', '#f2b53c', 'coin')
stat(570, 'VISITORS', '1', '#ef5b5b', 'person')
im.convert('RGB').save(out_path)
safe = im.crop((0, 285, W, 1635)).convert('RGB'); safe.resize((W // 3, (1635 - 285) // 3)).save(out_path.replace('.png', '_grid_preview.png'))
print('ok')
