// ZOO: vykreslování reelu v enginu (bez webového rozhraní). Čas řídí window.__reel.setTime(t); vše je funkce t.
// Plán a časování: web/src/reel-script.js, zvuk a titulky: marketing/reels/hook/timeline.json (nástroj tools/reel-audio.py).
import { Application, Assets, Sprite, Texture, Container, Rectangle, Graphics } from 'pixi.js';
import { lotBox, lotKey, isPlaza, isRoad, BLOCK, GATE_J, inRegion, START_LOTS } from '../../engine/layout.js';
import { placeLot } from '../../engine/place.js';
import { rngFor, hashString } from '../../engine/rng.js';
import { plan, ease, lerp, START_COINS, BUS_BONUS, FENCE_COST } from './reel-script.js';
import { textCanvas, coinCanvas, floatCanvas } from './pixfont.js';

const W = 1080, H = 1920;
const sx = (i, j) => (i - j) * 16;
const sy = (i, j) => (i + j) * 8;
const j$ = async (u) => { const r = await fetch(u); if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); };
const loadImage = (src) => new Promise((ok, no) => { const im = new Image(); im.onload = () => ok(im); im.onerror = no; im.src = src; });
const q = new URLSearchParams(location.search);
const REEL = q.get('reel') || 'hook';

const app = new Application();
await app.init({ width: W, height: H, background: '#2a4a2a', antialias: false, roundPixels: true, resolution: 1, autoStart: false });
app.ticker.stop();
document.body.appendChild(app.canvas);

// ------------------------------------------------------------ data
const [tilesMeta, vMeta, pMeta, font, tl] = await Promise.all([
  j$('/assets/tiles.json'), j$('/assets/visitors.json'), j$('/assets/props.json'), j$('/assets/font.json'), j$(`/reels/${REEL}/timeline.json`),
]);
const atlasTex = await Assets.load('/assets/atlas.png'); atlasTex.source.scaleMode = 'nearest';
const tilesImg = await loadImage('/assets/tiles.png');
const P = plan(tl);

const propTex = {};
for (const [name, m] of Object.entries(pMeta)) propTex[name] = { t: new Texture({ source: atlasTex.source, frame: new Rectangle(m.x, m.y, m.w, m.h) }), m };
const visFrames = new Map();
function visTexture(look, dir, frame) {
  const idx = look * 16 + dir * 4 + frame;
  let t = visFrames.get(idx);
  if (!t) { t = new Texture({ source: atlasTex.source, frame: new Rectangle((idx % vMeta.cols) * vMeta.cellW, Math.floor(idx / vMeta.cols) * vMeta.cellH, vMeta.cellW, vMeta.cellH) }); visFrames.set(idx, t); }
  return t;
}
const canvasTex = (c) => { const t = Texture.from(c); t.source.scaleMode = 'nearest'; return t; };

// ------------------------------------------------------------ svět
const world = new Container();
const groundLayer = new Container();
const objects = new Container(); objects.sortableChildren = true;
const fx = new Graphics();
world.addChild(groundLayer, objects, fx);
const hud = new Container();
app.stage.addChild(world, hud);

const lots = JSON.parse(JSON.stringify(START_LOTS));
const R = 1;
function tileKind(i, j) {
  if (inRegion(i, j, R)) {
    if (isPlaza(i, j)) return 'cobble';
    if (isRoad(i, j)) return 'dirt';
    const a = Math.floor(i / BLOCK), b = Math.floor(j / BLOCK), lot = lots[lotKey(a, b)];
    if (lot && lot.t === 'pond') { const bx = lotBox(a, b); if (i >= bx.i0 + 1 && i <= bx.i1 - 1 && j >= bx.j0 + 1 && j <= bx.j1 - 1) return 'water'; }
    return hashString(`p${i},${j}`) % 100 < 27 ? 'dirt' : 'grass';
  }
  if (i === 0 && j >= -30 && j <= 30) return 'dirt';                         // cesta ven ze zoo (zebra uteče, autobus přijede)
  if (j === GATE_J && i >= -6 && i <= 6) return 'dirt';
  return 'grass';
}
const I0 = -30, I1 = 30, J0 = -34, J1 = 34;
(function bake() {
  const x0 = sx(I0, J1) - 16, x1 = sx(I1, J0) + 16, y0 = sy(I0, J0), y1 = sy(I1, J1) + 16;
  const cv = document.createElement('canvas'); cv.width = x1 - x0; cv.height = y1 - y0;
  const ctx = cv.getContext('2d'); ctx.imageSmoothingEnabled = false;
  for (let i = I0; i <= I1; i++) for (let j = J0; j <= J1; j++) {
    const k = tileKind(i, j), v = hashString(`v${i},${j}`) % 4;
    ctx.drawImage(tilesImg, v * 32, tilesMeta.kinds.indexOf(k) * 16, 32, 16, sx(i, j) - 16 - x0, sy(i, j) - y0, 32, 16);
  }
  const s = new Sprite(canvasTex(cv)); s.position.set(x0, y0); groundLayer.addChild(s);
})();

function prop(name, i, j, z = 0, dx = 0, dy = 0) {
  const p = propTex[name]; const s = new Sprite(p.t);
  s.anchor.set(p.m.ax / p.m.w, p.m.ay / p.m.h);
  s.position.set(Math.round(sx(i, j) + dx), Math.round(sy(i, j) + dy));
  s.zIndex = (i + j) * 10 + z; s.__i = i; s.__j = j; s.__z = z;
  objects.addChild(s); return s;
}

// statická scéna: poslední dva výběhy (plot se staví v reelu), parcely, vstup, les
const TREES = ['oak1', 'oak2', 'oak3', 'pine1', 'birch'];
let zebraA = null, zebraB = null, previewPlot = null;
for (const [key, lot] of Object.entries(lots)) {
  const [a, b] = key.split(',').map(Number);
  const r = placeLot(a, b, lot, key, (n) => propTex[n]?.m.w || 0);
  r.items.forEach((it) => {
    if (!propTex[it.name]) return;
    const s = prop(it.name, it.i, it.j, it.z); if (it.flip) s.scale.x = -1;
    if (it.name === 'a_zebra') { if (!zebraA) zebraA = s; else zebraB = s; }
    if (it.name === 'plot' && key === '-1,0') previewPlot = { a, b };
  });
}
(function forest() {
  const rng = rngFor('reel-forest');
  for (let i = I0 + 4; i <= I1 - 4; i++) for (let j = J0 + 4; j <= J1 - 8; j++) {
    if (inRegion(i, j, R) || (i >= -8 && i <= 8 && j >= -8 && j <= 9)) continue;
    if (i >= -1 && i <= 2) continue;                                          // cesta
    if (j >= GATE_J - 1 && j <= GATE_J + 2 && i >= -6 && i <= 6) continue;
    const dist = Math.hypot(i, j * 0.9); if (rng() > 0.03 + Math.max(0, Math.min(1, (dist - 9) / 14)) * 0.24) continue;
    prop(TREES[Math.floor(rng() * TREES.length)], i + rng(), j + rng(), 1);
  }
  for (let k = 0; k < 14; k++) { const i = -5 + rng() * 11, j = -5 + rng() * 11; if (!isRoad(Math.floor(i), Math.floor(j)) && !isPlaza(Math.floor(i), Math.floor(j))) { /* volná louka uvnitř zoo */ } }
})();
// vstup: brána v ose cesty, kasa s plovoucí částkou
prop('gate_post', -0.5, GATE_J + 0.9, 6); prop('gate_post', 1.5, GATE_J + 0.9, 6);
{ const b = prop('gate_beam', -0.5, GATE_J + 0.9, 7, 0, -29); b.anchor.set(1 / propTex.gate_beam.m.w, 1 / propTex.gate_beam.m.h); }
prop('sign_welcome', -2.6, GATE_J + 1.6, 4); prop('crate', -3.2, GATE_J + 0.9, 1); prop('crate', -2.8, GATE_J + 1.2, 1); prop('hay', -4.4, GATE_J + 0.5, 1);
const KI = 4.2, KJ = GATE_J + 1.7;
const kasa = prop('kasa', KI, KJ, 2);
const coinFloat = new Sprite(); coinFloat.anchor.set(0.5, 1); coinFloat.zIndex = 99999; objects.addChild(coinFloat);
const coinFloatBase = { x: Math.round(sx(KI, KJ)), y: Math.round(sy(KI, KJ)) - kasa.height + 7 };
prop('d_bench_wood', -1.8, 1.5, 1); prop('d_bench_green', 2.0, 1.5, 1); prop('d_lamp', -1.5, -1.5, 1); prop('d_lamp', 2.5, -1.4, 1); prop('d_bin', 2.6, 0.9, 1);
prop('tuft', 2.0, 3.0, 1); prop('flowers', -4.1, 5.3, 1); prop('tuft', 4.4, 5.2, 1); prop('pine1', -5.6, 4.8, 1);

// ------------------------------------------------------------ plot: ghost → pevný díl
const fenceParts = P.steps.map((s) => {
  const seg = prop(s.seg, s.i, s.j, 2), post = prop('post' + ((Math.round(s.post[0]) + Math.round(s.post[1])) & 1), s.post[0], s.post[1], 3);
  seg.visible = post.visible = false;
  return { s, seg, post };
});

// ------------------------------------------------------------ náhledy staveb (hlasování)
const pl = previewPlot ? placeLot(previewPlot.a, previewPlot.b, { t: 'build', sprite: 'bp_cafe' }, '-1,0', (n) => propTex[n]?.m.w || 0) : null;
const previewSprites = P.previews.map((p) => {
  const w = propTex[p.name].m.w; const o = Math.min(1.1, w / 64);
  const bx = lotBox(previewPlot.a, previewPlot.b);
  const s = prop(p.name, bx.ci + o, bx.cj + o, 1); s.visible = false; return s;
});

// ------------------------------------------------------------ návštěvníci, zebra, autobus
const visSprites = P.arrivals.map((a) => { const s = new Sprite(visTexture(a.look, 0, 0)); s.anchor.set(0.5, vMeta.anchorY); s.visible = false; objects.addChild(s); return s; });
const busSprite = prop('bus', 0.5, 21, 5); busSprite.visible = false;
const exclam = new Sprite(canvasTex(textCanvas(font, '!', 1, '#ef5b5b'))); exclam.anchor.set(0.5, 1); exclam.visible = false; objects.addChild(exclam);

// ------------------------------------------------------------ HUD, titulky, panely (obrazovkové souřadnice)
const mk = (c, x, y, ax = 0, ay = 0) => { const s = new Sprite(canvasTex(c)); s.anchor.set(ax, ay); s.position.set(x, y); return s; };
function panel(w, h, bg = '#4a3430', top = '#f2b53c', edge = '#2a1c1a') {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d');
  x.fillStyle = edge; x.fillRect(0, 0, w, h); x.fillStyle = bg; x.fillRect(6, 6, w - 12, h - 12); x.fillStyle = top; x.fillRect(6, 6, w - 12, 8);
  return c;
}
const scaled = (c, k) => { const o = document.createElement('canvas'); o.width = c.width * k; o.height = c.height * k; const x = o.getContext('2d'); x.imageSmoothingEnabled = false; x.drawImage(c, 0, 0, o.width, o.height); return o; };
function hudBox(label, icon, value, x, y, col) {
  const g = new Container(); g.position.set(x, y);
  g.addChild(mk(panel(450, 132), 0, 0));
  g.addChild(mk(textCanvas(font, label, 4, '#e8c8a0'), 24, 22));
  if (icon) g.addChild(mk(icon, 24, 62));
  g.__val = null; g.__col = col; g.__lab = null;
  return g;
}
const personIcon = (() => { const c = document.createElement('canvas'); c.width = 6; c.height = 8; const x = c.getContext('2d'); x.fillStyle = '#fff0c8'; x.fillRect(2, 0, 2, 2); x.fillRect(1, 2, 4, 3); x.fillRect(1, 5, 1, 3); x.fillRect(4, 5, 1, 3); return scaled(c, 7); })();
const coinHud = hudBox('COINS', scaled(coinCanvas(1), 8), 0, 40, 230, '#ffd23c');
const visHud = hudBox('VISITORS', personIcon, 0, 590, 230, '#fff0c8');
hud.addChild(coinHud, visHud);
function setHudValue(box, v) {
  if (box.__val === v) return; box.__val = v;
  if (box.__num) { box.removeChild(box.__num); box.__num.destroy(); }
  box.__num = mk(textCanvas(font, v.toLocaleString('en-US'), 8, box.__col), 118, 62);
  box.addChild(box.__num);
}

const caps = [];  // titulky po 2–3 slovech
for (const ln of tl.lines) {
  let cur = [];
  const flush = () => { if (!cur.length) return; caps.push({ text: cur.map((w) => w.w.toUpperCase()).join(' '), t0: cur[0].t0, t1: cur[cur.length - 1].t1 }); cur = []; };
  for (const w of ln.words) {
    const len = cur.reduce((a, x) => a + x.w.length + 1, 0) + w.w.length;
    if (cur.length >= 3 || (cur.length >= 1 && len > 15)) flush();
    cur.push(w);
  }
  flush();
}
let capSprite = null, capKey = -1;
function captionAt(t) {
  let k = -1;
  for (let n = 0; n < caps.length; n++) if (t >= caps[n].t0 - 0.05 && t < caps[n].t1 + 0.25) k = n;
  if (k === capKey) return;
  capKey = k;
  if (capSprite) { hud.removeChild(capSprite); capSprite.destroy(); capSprite = null; }
  if (k < 0) return;
  const text = caps[k].text, sc = 11;
  const c = textCanvas(font, text, sc, '#ffe9a8'), o = document.createElement('canvas'); o.width = c.width + 40; o.height = c.height + 40;
  const x = o.getContext('2d'); x.imageSmoothingEnabled = false;
  const tint = textCanvas(font, text, sc, '#2a1c0a');
  for (const [dx, dy] of [[-sc, 0], [sc, 0], [0, -sc], [0, sc], [sc, sc], [-sc, sc], [sc, -sc], [-sc, -sc], [0, 2 * sc], [sc, 2 * sc], [-sc, 2 * sc]]) x.drawImage(tint, 20 + dx, 20 + dy);
  const shade = textCanvas(font, text, sc, '#d9902a'); x.drawImage(shade, 20, 20 + sc * 0.6);
  x.drawImage(c, 20, 20);
  capSprite = mk(o, W / 2, 1560, 0.5, 0.5); hud.addChild(capSprite);
}

// info panely: [id, t0, t1, y, lines, kolor rámu]
const boxes = [
  { t0: P.cue.coins - 0.1, t1: P.cue.coins + 3.3, y: 430, lines: ['1 FOLLOWER =', '1 VISITOR + 10 COINS'], top: '#f2b53c' },
  { t0: P.cue.escape - 0.2, t1: P.cue.fence + 0.3, y: 430, lines: ['NO FENCE!'], top: '#ef5b5b', bg: '#7a2a2a', sc: 9 },
  { t0: P.cue.vote - 0.1, t1: P.cue.bus - 0.4, y: 430, lines: ['MOST LIKED COMMENT', 'DECIDES WHAT WE', 'BUILD NEXT'], top: '#f2b53c' },
  { t0: P.cue.bus - 0.1, t1: P.cue.cta - 0.2, y: 430, lines: ['1 SHARE =', 'SCHOOL BUS +20 COINS'], top: '#f2b53c' },
  { t0: P.cue.cta - 0.1, t1: P.total, y: 430, lines: ['WHAT SHOULD WE', 'CALL OUR ZOO?'], top: '#ffd23c', bg: '#4a3430' },
].map((b) => {
  const sc = b.sc || 6, cs = b.lines.map((l) => textCanvas(font, l, sc, '#fff0c8'));
  const w = Math.max(...cs.map((c) => c.width)) + 90, h = cs.length * (5 * sc + 22) + 70;
  const g = new Container(); g.addChild(mk(panel(w, h, b.bg || '#4a3430', b.top), 0, 0));
  cs.forEach((c, k) => g.addChild(mk(c, w / 2 - c.width / 2, 40 + k * (5 * sc + 22))));
  g.pivot.set(w / 2, 0); g.position.set(W / 2, b.y); g.visible = false; hud.addChild(g);
  return { ...b, g, w, h };
});
// karty možností hlasování
const cards = P.previews.map((p, k) => {
  const g = new Container();
  g.addChild(mk(panel(300, 330, '#4a3430', '#f2b53c'), 0, 0));
  const spr = new Sprite(propTex[p.name].t); spr.scale.set(3); spr.anchor.set(0.5, 1); spr.position.set(150, 220); g.addChild(spr);
  g.addChild(mk(textCanvas(font, p.label, 5, '#fff0c8'), 150 - textCanvas(font, p.label, 5, '#fff').width / 2, 242));
  const pr = textCanvas(font, String(p.price), 6, '#ffd23c'), cn = scaled(coinCanvas(1), 6);
  g.addChild(mk(cn, 150 - (pr.width + cn.width + 14) / 2, 282)); g.addChild(mk(pr, 150 - (pr.width + cn.width + 14) / 2 + cn.width + 14, 282));
  g.position.set(60 + k * 330, 1100); g.visible = false; g.pivot.set(0, 0); hud.addChild(g); return g;
});
// CTA lišta
const cta = (() => { const c = textCanvas(font, 'FOLLOW TO VISIT', 9, '#fff0c8'); const g = new Container(); g.addChild(mk(panel(c.width + 110, 150, '#c43a6a', '#ff8fb8'), 0, 0)); g.addChild(mk(c, 55, 50)); g.pivot.set((c.width + 110) / 2, 0); g.position.set(W / 2, 1690); g.visible = false; hud.addChild(g); return g; })();
// kolo „DAY 1“ štítek
const dayTag = mk(textCanvas(font, 'DAY 1', 7, '#fff0c8'), 40, 160); hud.addChild(dayTag);

// ------------------------------------------------------------ plovoucí texty ve světě (+10, −200, ...)
const floaters = [];
function addFloater(text, color, i, j, t0, dur = 1.0, rise = 18, sc = 1) {
  const s = new Sprite(canvasTex(floatLike(text, color))); s.anchor.set(0.5, 1); s.visible = false; objects.addChild(s);
  floaters.push({ s, i, j, t0, dur, rise });
}
function floatLike(text, color) {
  const c = textCanvas(font, text, 1, color), o = document.createElement('canvas'); o.width = c.width + 4; o.height = c.height + 4;
  const x = o.getContext('2d'); const d = textCanvas(font, text, 1, '#2a1c1a');
  for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [1, 1], [-1, -1], [1, -1], [-1, 1]]) x.drawImage(d, 2 + dx, 2 + dy);
  x.drawImage(c, 2, 2); return o;
}
P.arrivals.forEach((a) => addFloater('+10', '#ffd23c', 0.5, GATE_J + 0.3, a.tGate, 0.9, 16));
addFloater('-200', '#ff6a6a', KI, KJ - 0.2, P.tBuy, 1.4, 22);
addFloater('+20', '#ffd23c', 0.5, GATE_J + 3.2, P.tBus + 0.5, 1.3, 22);

// ------------------------------------------------------------ částice
function dust(i, j, t0, t, n = 6) {
  const u = t - t0; if (u < 0 || u > 0.5) return;
  for (let k = 0; k < n; k++) { const a = (k / n) * 6.28, r = 2 + u * 14; fx.rect(sx(i, j) + Math.cos(a) * r - 1, sy(i, j) + Math.sin(a) * r * 0.5 - 2, 2, 2).fill({ color: 0xf2e6c8, alpha: 1 - u * 2 }); }
}
function spark(i, j, t0, t, h = 16, n = 6) {
  const u = t - t0; if (u < 0 || u > 0.7) return;
  for (let k = 0; k < n; k++) { const a = (k / n) * 6.28 + 0.4, r = 4 + u * 26; const x = sx(i, j) + Math.cos(a) * r, y = sy(i, j) - h + Math.sin(a) * r * 0.7 - u * 6; fx.rect(x - 1, y - 1, 3, 1).fill({ color: 0xfff2a6, alpha: 1 - u * 1.3 }); fx.rect(x, y - 2, 1, 3).fill({ color: 0xfff2a6, alpha: 1 - u * 1.3 }); }
}

// ------------------------------------------------------------ kamera
const camKeys = [
  { t: 0, i: 0.5, j: 3.2, z: 3.2 }, { t: P.cue.visitor, i: 0.5, j: 4.6, z: 4.4 }, { t: P.cue.coins, i: 1.5, j: 5.8, z: 5.0 },
  { t: P.cue.poor, i: -1.6, j: 1.0, z: 3.8 }, { t: P.cue.escape, i: -0.8, j: -2.0, z: 4.6 }, { t: P.cue.escape + 2.6, i: 0.5, j: -5.0, z: 3.6 },
  { t: P.cue.fence, i: -2.5, j: -2.5, z: 5.2 }, { t: P.cue.fence + 4.2, i: -2.5, j: -2.2, z: 4.8 }, { t: P.cue.vote, i: -0.5, j: 1.0, z: 3.4 },
  { t: P.cue.bus - 0.2, i: -0.5, j: 1.0, z: 3.4 }, { t: P.cue.bus + 1.2, i: 0.5, j: 7.4, z: 4.2 }, { t: P.cue.cta, i: 0.5, j: 2.4, z: 3.2 }, { t: P.total, i: 0.5, j: 2.2, z: 3.0 },
];
function camAt(t) {
  let a = camKeys[0], b = camKeys[0];
  for (let k = 0; k < camKeys.length; k++) { if (camKeys[k].t <= t) a = camKeys[k]; if (camKeys[k].t > t) { b = camKeys[k]; break; } b = camKeys[k]; }
  const f = a === b || b.t === a.t ? 0 : ease((t - a.t) / (b.t - a.t));
  return { i: lerp(a.i, b.i, f), j: lerp(a.j, b.j, f), z: lerp(a.z, b.z, f) };
}

// ------------------------------------------------------------ hlavní funkce snímku
function smoothTotals(t) {
  let c = START_COINS, v = 0;
  for (const e of P.ledger) { if (e.t > t + 0.01) continue; const f = ease((t - e.t) / 0.4); c += e.d * f; v += e.v * (t >= e.t ? 1 : 0); }
  return { coins: Math.round(c), visitors: v };
}
const frameDir = (t, ph) => Math.floor(t * 8 + ph) & 3;
let lastCoinShown = null;

function setTime(t) {
  fx.clear();
  const cam = camAt(t);
  world.scale.set(cam.z);
  world.position.set(Math.round(W / 2 - sx(cam.i, cam.j) * cam.z), Math.round(H * 0.47 - sy(cam.i, cam.j) * cam.z));

  // ---- počty
  const tot = smoothTotals(t);
  setHudValue(coinHud, tot.coins); setHudValue(visHud, tot.visitors);
  if (lastCoinShown !== tot.coins) { lastCoinShown = tot.coins; coinFloat.texture = canvasTex(floatCanvas(font, tot.coins)); }
  coinFloat.position.set(coinFloatBase.x, coinFloatBase.y - 2 - Math.round(Math.sin(t * 2.2) * 1.5));

  // ---- návštěvníci
  P.arrivals.forEach((a, n) => {
    const s = visSprites[n]; const w = a.walk;
    if (t < a.t0) { s.visible = false; return; }
    const st = w.at(t);
    s.visible = true;
    s.texture = visTexture(a.look, st.dir, st.moving ? (Math.floor(t * 7 + n) & 3) : 0);
    s.position.set(Math.round(sx(st.i, st.j)), Math.round(sy(st.i, st.j)));
    s.zIndex = (st.i + st.j) * 10 + 5;
  });

  // ---- zebra (A uteče a vrací se), B stojí
  const zr = P.zebraRun, zb = P.zebraBack;
  if (zebraA) {
    let pos, moving = false, face = 1;
    if (t < zr.t0) pos = { i: P.zebraStart[0], j: P.zebraStart[1] };
    else if (t < zr.t1) { pos = zr.at(t); moving = true; face = pos.dir === 1 || pos.dir === 3 ? -1 : 1; }
    else if (t < zb.t0) pos = null;
    else if (t < zb.t1) { pos = zb.at(t); moving = true; face = pos.dir === 1 || pos.dir === 3 ? -1 : 1; }
    else pos = { i: P.zebraStart[0], j: P.zebraStart[1] };
    if (pos) {
      zebraA.visible = true;
      const hop = moving ? Math.abs(Math.sin(t * 11)) * 3 : 0;
      zebraA.position.set(Math.round(sx(pos.i, pos.j)), Math.round(sy(pos.i, pos.j) - hop));
      zebraA.scale.x = moving ? face : (zebraA.scale.x || 1);
      zebraA.zIndex = (pos.i + pos.j) * 10 + 2;
    } else zebraA.visible = false;
    // vykřičník nad zebrou na začátku útěku
    const e0 = P.cue.escape + 0.05;
    exclam.visible = t > e0 && t < e0 + 0.9;
    if (exclam.visible) { exclam.position.set(sx(P.zebraStart[0], P.zebraStart[1]), sy(P.zebraStart[0], P.zebraStart[1]) - 26 - Math.abs(Math.sin((t - e0) * 14)) * 3); exclam.zIndex = 99998; exclam.scale.set(1.5 + Math.sin((t - e0) * 12) * 0.15); }
  }

  // ---- plot
  fenceParts.forEach(({ s, seg, post }) => {
    const u = t - s.t;
    if (u < -0.28) { seg.visible = post.visible = false; return; }
    seg.visible = post.visible = true;
    if (u < 0) { seg.tint = post.tint = 0x7fffe8; seg.alpha = post.alpha = 0.5; seg.scale.set(1); post.scale.set(1); }
    else {
      seg.tint = post.tint = 0xffffff; seg.alpha = post.alpha = 1;
      const k = u < 0.28 ? 1 + Math.sin((u / 0.28) * Math.PI) * 0.18 - (1 - ease(u / 0.28)) * 0.35 : 1;
      seg.scale.set(1, k); post.scale.set(1, k);
      dust(s.post[0], s.post[1], s.t, t, 4);
    }
  });

  // ---- náhledy staveb (pop efekt na parcele)
  P.previews.forEach((p, k) => {
    const spr = previewSprites[k], next = P.previews[k + 1], tEnd = next ? next.t : P.cue.bus - 0.4;
    const u = t - p.t, on = t >= p.t && t < tEnd;
    spr.visible = on;
    if (on) {
      const pop = u < 0.38 ? 0.15 + ease(u / 0.38) * 1.0 + Math.sin(u / 0.38 * Math.PI) * 0.18 : 1;
      spr.scale.set(pop); spr.alpha = 0.78 + Math.sin(t * 6) * 0.08; spr.tint = 0xffffff;
      const bx = lotBox(previewPlot.a, previewPlot.b);
      dust(bx.ci + 0.9, bx.cj + 0.9, p.t, t, 8); spark(bx.ci + 0.9, bx.cj + 0.9, p.t + 0.1, t, 34, 7);
    }
    const c = cards[k], cu = t - (p.t - 0.2);
    c.visible = cu >= 0 && t < P.cue.bus - 0.4;
    if (c.visible) { const sc = 0.2 + ease(cu / 0.35) * 0.8 + Math.sin(Math.min(1, cu / 0.35) * Math.PI) * 0.12; c.scale.set(sc); c.pivot.set(150, 330); c.position.set(45 + k * 330 + 150, 1130 + 330); c.alpha = 1; }
  });

  // ---- autobus
  const bs = P.bus;
  if (t >= bs.t0) {
    const st = bs.at(t); busSprite.visible = true;
    busSprite.position.set(Math.round(sx(st.i, st.j)), Math.round(sy(st.i, st.j) + (st.moving ? Math.sin(t * 18) * 0.6 : 0))); busSprite.zIndex = (st.i + st.j) * 10 + 5;
    if (!st.moving && t > bs.t1 && t < bs.t1 + 0.5) dust(st.i, st.j, bs.t1, t, 6);
    if (t > P.tBus + 0.4) spark(0.5, GATE_J + 3.2, P.tBus + 0.5, t, 20, 8);
  } else busSprite.visible = false;

  // ---- plovoucí texty
  floaters.forEach((f) => {
    const u = (t - f.t0) / f.dur; f.s.visible = u >= 0 && u < 1;
    if (f.s.visible) { f.s.position.set(Math.round(sx(f.i, f.j)), Math.round(sy(f.i, f.j) - 20 - ease(u) * f.rise)); f.s.alpha = u < 0.7 ? 1 : 1 - (u - 0.7) / 0.3; f.s.zIndex = 99999; f.s.scale.set(1.0 + (u < 0.15 ? (0.15 - u) * 3 : 0)); }
  });

  // ---- HUD prvky
  boxes.forEach((b) => { const on = t >= b.t0 && t < b.t1; b.g.visible = on; if (on) { const u = clampk((t - b.t0) / 0.3); b.g.scale.set(0.6 + ease(u) * 0.4 + Math.sin(u * Math.PI) * 0.06); b.g.alpha = u; } });
  cta.visible = t >= P.cue.cta + 0.7; if (cta.visible) { cta.scale.set(1 + Math.sin(t * 6) * 0.03); cta.alpha = 0.55 + 0.45 * Math.abs(Math.sin(t * 3.2)) + 0.0; cta.alpha = 1; }
  dayTag.visible = t < P.cue.coins;
  captionAt(t);
  app.render();
}
const clampk = (x) => Math.max(0, Math.min(1, x));

window.__reel = { setTime, total: P.total, fps: 30, ready: true };
setTime(Number(q.get('t') || 0));
