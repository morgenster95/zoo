// ZOO: prohlížeč zoo (PixiJS). Mapa je izometrická, vše se počítá z dat v /data (zoo.json, looks/*.bin, h/*.json, v/*.json).
import { Application, Assets, Sprite, Texture, Container, Rectangle, Graphics } from 'pixi.js';
import { slotPos, regionFor, lotBox, lotsIn, lotKey, isPlaza, isRoad, BLOCK, GATE_J, inRegion, COIN_PER_VISITOR } from '../../engine/layout.js';
import { placeLot } from '../../engine/place.js';
import { rngFor, hashString } from '../../engine/rng.js';
import { shardOf, normHandle } from '../../engine/state.js';
import { textCanvas, coinCanvas, floatCanvas } from './pixfont.js';

const DATA = import.meta.env.VITE_DATA_BASE || '/data';
const ASSETS = '/assets';
const $ = (id) => document.getElementById(id);
const sx = (i, j) => (i - j) * 16;
const sy = (i, j) => (i + j) * 8;
const mod = (a, n) => ((a % n) + n) % n;
const j$ = async (u) => { const r = await fetch(u); if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); };

const app = new Application();
await app.init({ resizeTo: window, background: '#9fd4ec', antialias: false, roundPixels: true, resolution: window.devicePixelRatio || 1, autoDensity: true });
document.body.prepend(app.canvas);

// ------------------------------------------------------------ data a sprity
const [zoo, tilesMeta, vMeta, pMeta, font] = await Promise.all([
  j$(`${DATA}/zoo.json`), j$(`${ASSETS}/tiles.json`), j$(`${ASSETS}/visitors.json`), j$(`${ASSETS}/props.json`), j$(`${ASSETS}/font.json`),
]);
const crisp = (t) => { t.source.scaleMode = 'nearest'; return t; };
const atlasTex = crisp(await Assets.load(`${ASSETS}/atlas.png`));
const visTex = atlasTex, propsTex = atlasTex;
const tilesImg = await loadImage(`${ASSETS}/tiles.png`);
function loadImage(src) { return new Promise((ok, no) => { const im = new Image(); im.onload = () => ok(im); im.onerror = no; im.src = src; }); }

const looks = new Uint16Array(zoo.visitors);
await Promise.all(Array.from({ length: zoo.lookChunks }, async (_, c) => {
  const buf = await (await fetch(`${DATA}/looks/${c}.bin`)).arrayBuffer();
  looks.set(new Uint16Array(buf), c * zoo.lookChunk);
}));

const propTex = {};
for (const [name, m] of Object.entries(pMeta)) propTex[name] = { t: new Texture({ source: propsTex.source, frame: new Rectangle(m.x, m.y, m.w, m.h) }), m };
const visFrames = new Map();
function visTexture(look, dir, frame) {
  const idx = look * 16 + dir * 4 + frame;
  let t = visFrames.get(idx);
  if (!t) {
    t = new Texture({ source: visTex.source, frame: new Rectangle((idx % vMeta.cols) * vMeta.cellW, Math.floor(idx / vMeta.cols) * vMeta.cellH, vMeta.cellW, vMeta.cellH) });
    visFrames.set(idx, t);
  }
  return t;
}

// ------------------------------------------------------------ svět
const world = new Container();
const groundLayer = new Container();
const objects = new Container(); objects.sortableChildren = true;
const overlay = new Container();
world.addChild(groundLayer, objects, overlay);
app.stage.addChild(world);

const R = Math.max(regionFor(zoo.visitors), zoo.ring || 1);
const lots = zoo.lots || {};

function tileKind(i, j) {
  if (inRegion(i, j, R)) {
    if (isPlaza(i, j)) return 'cobble';
    if (isRoad(i, j)) return 'dirt';
    const a = Math.floor(i / BLOCK), b = Math.floor(j / BLOCK), lot = lots[lotKey(a, b)];
    if (lot && lot.t === 'pond') { const bx = lotBox(a, b); if (i >= bx.i0 + 1 && i <= bx.i1 - 1 && j >= bx.j0 + 1 && j <= bx.j1 - 1) return 'water'; }
    return hashString(`p${i},${j}`) % 100 < Math.max(6, 30 - R * 3) ? 'dirt' : 'grass';
  }
  return 'grass';
}

function bakeGround() {
  const M = 8;
  const i0 = -BLOCK * R - M, i1 = BLOCK * R + M, j0 = -BLOCK * R - M, j1 = GATE_J + M;
  const x0 = sx(i0, j1) - 16, x1 = sx(i1, j0) + 16, y0 = sy(i0, j0), y1 = sy(i1, j1) + 16;
  const cv = document.createElement('canvas'); cv.width = x1 - x0; cv.height = y1 - y0;
  const ctx = cv.getContext('2d'); ctx.imageSmoothingEnabled = false;
  const row = (k) => tilesMeta.kinds.indexOf(k);
  for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
    const k = tileKind(i, j), v = hashString(`v${i},${j}`) % 4;
    ctx.drawImage(tilesImg, v * 32, row(k) * 16, 32, 16, sx(i, j) - 16 - x0, sy(i, j) - y0, 32, 16);
  }
  const s = new Sprite(Texture.from(cv)); s.texture.source.scaleMode = 'nearest';
  s.position.set(x0, y0); groundLayer.addChild(s);
}

// ?sprites=old ukáže původní sprity (moje procedurální) místo PixelLabu; jen pro srovnání
const OLD = new URLSearchParams(location.search).get('sprites') === 'old';
const OLD_ALIAS = { bp_lodge: 'b_african', bp_barn: 'b_classic', bp_pagoda: 'b_asian', bp_penguin_house: 'b_igloo', bp_treehouse: 'b_andes', bp_aquarium: 'b_modern',
  bp_cafe: 'b_modern', bp_shop: 'b_classic', bp_aviary: 'b_dome', bp_carousel: 'b_carousel', bp_ferris: 'b_dome', bp_station: 'b_classic', bp_playground: 'b_cart',
  bp_toilets: 'b_classic', bp_clinic: 'b_modern', bp_ticket: 'kasa', bp_gate: 'gate', bp_popcorn: 'b_cart',
  d_bench_wood: 'bench', d_bench_green: 'bench', d_bench_stone: 'bench', d_bench_color: 'bench', d_kiosk: 'b_cart', d_planter: 'flowers', d_lamp: 'bench', d_bin: 'crate',
  d_fountain: 'b_igloo', d_statue: 'bench', d_balloons: 'b_cart', d_picnic: 'bench' };
function prop(name, i, j, z = 0, dx = 0, dy = 0) {
  if (OLD) name = name.startsWith('a_') ? 'old_' + name : (OLD_ALIAS[name] || name);
  const p = propTex[name];
  const s = new Sprite(p.t);
  s.anchor.set(p.m.ax / p.m.w, p.m.ay / p.m.h);
  s.position.set(Math.round(sx(i, j) + dx), Math.round(sy(i, j) + dy));
  s.zIndex = (i + j) * 10 + z;
  objects.addChild(s);
  return s;
}

function fenceRect(i0, j0, i1, j1, gaps = []) {
  const gap = (a, b) => gaps.some((g) => g[0] === a && g[1] === b);
  for (let i = i0; i < i1; i++) { if (!gap('i', i)) { prop('seg_i', i, j0, 2); } prop('seg_i', i, j1, 2); }
  for (let j = j0; j < j1; j++) { prop('seg_j', i0, j, 2); prop('seg_j', i1, j, 2); }
  for (let i = i0; i <= i1; i++) for (const j of [j0, j1]) prop('post' + ((i + j) & 1), i, j, 3);
  for (let j = j0 + 1; j < j1; j++) for (const i of [i0, i1]) prop('post' + ((i + j) & 1), i, j, 3);
}

const TREES = ['oak1', 'oak2', 'oak3', 'pine1', 'birch'];
const SMALL = ['bush1', 'bush2', 'flowers', 'tuft', 'flowers', 'tuft'];
function pickDecor(rng) { return rng() < 0.3 ? TREES[Math.floor(rng() * TREES.length)] : SMALL[Math.floor(rng() * SMALL.length)]; }

const DEBUG = new URLSearchParams(location.search).get('debug') === 'lots';
function buildLots() {
  for (const { a, b } of lotsIn(R)) {
    const key = lotKey(a, b), lot = lots[key], bx = lotBox(a, b), rng = rngFor('lot', key);
    if (DEBUG) {
      const g = new Graphics();
      const P = (i, j) => [sx(i, j), sy(i, j)];
      g.poly([...P(bx.i0, bx.j0), ...P(bx.i1 + 1, bx.j0), ...P(bx.i1 + 1, bx.j1 + 1), ...P(bx.i0, bx.j1 + 1)]).stroke({ width: 1, color: 0xff00ff });
      g.circle(...P(bx.ci, bx.cj), 2).fill(0xff0000);
      overlay.addChild(g);
    }
    const r = placeLot(a, b, lot, key, (n) => propTex[n]?.m.w || 0);   // polohy počítá engine (testované: zvířata uvnitř plotu, bez překryvů)
    if (r.fence) fenceRect(r.fence.i0, r.fence.j0, r.fence.i1, r.fence.j1);
    r.items.forEach((it) => { if (!propTex[it.name]) return; const sp = prop(it.name, it.i, it.j, it.z); if (it.flip) sp.scale.x = -1; });
    if (r.free || !lot) {
      // volná louka: pár stromů, keřů a plevele
      const n = 3 + Math.floor(rng() * 3);
      for (let k = 0; k < n; k++) {
        const i = bx.i0 + 0.5 + rng() * (bx.i1 - bx.i0 - 1), j = bx.j0 + 0.5 + rng() * (bx.j1 - bx.j0 - 1);
        prop(pickDecor(rng, i, j), i, j, 1);
      }
    }
  }
}

function buildBorder() {
  // neotevřená krajina za hranicí: řídký les
  const M = 8, rng = rngFor('border');
  const i0 = -BLOCK * R - M, i1 = BLOCK * R + M, j0 = -BLOCK * R - M, j1 = GATE_J + M;
  for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
    if (inRegion(i, j, R) || rng() > 0.07) continue;
    if (j > GATE_J && j < GATE_J + 6 && Math.abs(i) < 9) continue;   // prostranství před bránou zůstane volné
    prop(TREES[Math.floor(rng() * TREES.length)], i + rng(), j + rng(), 1);
  }
}

let boardSprite, boardBase = { x: 0, y: 0 };
function buildEntrance() {
  const up = zoo.upgrades || {};
  if (up.gate && propTex[up.gate]) prop(up.gate, 0.5, GATE_J + 1.3, 6);
  else {                                         // chudá brána v ose cesty: dva sloupky přes silnici a šikmý trám s nápisem
    const gj = GATE_J + 0.9;
    prop('gate_post', -0.5, gj, 6); prop('gate_post', 1.5, gj, 6);
    const beam = prop('gate_beam', -0.5, gj, 7, 0, -29);
    beam.anchor.set(1 / propTex.gate_beam.m.w, 1 / propTex.gate_beam.m.h);
  }
  prop('sign_welcome', -2.6, GATE_J + 1.6, 4);
  prop('crate', -3.2, GATE_J + 0.9, 1); prop('crate', -2.8, GATE_J + 1.2, 1); prop('hay', -4.4, GATE_J + 0.5, 1);
  const KI = 4.2, KJ = GATE_J + 1.7;                       // pokladna stojí vedle cesty, ne na ní
  const k = prop(up.kasa && propTex[up.kasa] ? up.kasa : 'kasa', KI, KJ, 2);
  // částka se jen vznáší nad pokladnou (bez cedule); houpe se v ticker smyčce
  boardSprite = new Sprite(); boardSprite.anchor.set(0.5, 1);
  boardBase = { x: Math.round(sx(KI, KJ)), y: Math.round(sy(KI, KJ)) - k.height + 7 };
  boardSprite.position.set(boardBase.x, boardBase.y);
  boardSprite.zIndex = 99999;
  objects.addChild(boardSprite);
  setBoard(zoo.coins);
  prop('d_bench_wood', -1.8, 1.5, 1); prop('d_bench_green', 2.0, 1.5, 1); prop('d_lamp', -1.5, -1.5, 1); prop('d_lamp', 2.5, -1.4, 1); prop('d_bin', 2.6, 0.9, 1);
  prop('tuft', 2.0, 3.0, 1); prop('flowers', -4.1, 5.3, 1); prop('tuft', 4.4, 5.2, 1); prop('pine1', -5.6, 4.8, 1);
}
function setBoard(coins) {
  const t = Texture.from(floatCanvas(font, coins)); t.source.scaleMode = 'nearest';
  boardSprite.texture = t;
}

bakeGround(); buildLots(); buildBorder(); buildEntrance();

// ------------------------------------------------------------ návštěvníci
const N = zoo.visitors;
const vs = new Array(N);
const base = { i: new Float32Array(N), j: new Float32Array(N), ax: new Uint8Array(N), road: new Uint8Array(N), phase: new Float32Array(N), speed: new Float32Array(N), mode: new Uint8Array(N), dir0: new Uint8Array(N) };
for (let k = 0; k < N; k++) {
  const p = slotPos(k);
  if (!p) { vs[k] = null; continue; }
  const h = hashString('w' + k);
  base.i[k] = p.i; base.j[k] = p.j; base.road[k] = p.road ? 1 : 0;
  const inter = mod(p.ti, BLOCK) === 0 && mod(p.tj, BLOCK) === 0;
  base.ax[k] = inter ? (h & 1) : p.alongI ? 1 : 0;       // 1 = chodí po ose i, 0 = po ose j
  base.phase[k] = (h % 1000) / 1000; base.speed[k] = 0.045 + ((h >> 10) % 100) / 100 * 0.03;
  base.mode[k] = ((h >> 17) % 100) < 55 ? 1 : 0; base.dir0[k] = (h >> 20) & 3;
  const s = new Sprite(visTexture(looks[k], 0, 0));
  s.anchor.set(0.5, vMeta.anchorY);
  s.visible = false; objects.addChild(s); vs[k] = s;
}
const WALK = 2.4, SPEED_FRAMES = 6;
let selected = -1;
const markerTex = (() => {
  const c = document.createElement('canvas'); c.width = 9; c.height = 8; const x = c.getContext('2d');
  x.fillStyle = '#3d2a30'; x.fillRect(0, 0, 9, 3); x.fillRect(1, 3, 7, 1); x.fillRect(2, 4, 5, 1); x.fillRect(3, 5, 3, 1); x.fillRect(4, 6, 1, 2);
  x.fillStyle = '#ef5b5b'; x.fillRect(1, 1, 7, 1); x.fillRect(2, 2, 5, 1); x.fillRect(3, 3, 3, 1); x.fillRect(4, 4, 1, 1);
  const t = Texture.from(c); t.source.scaleMode = 'nearest'; return t;
})();
const marker = new Sprite(markerTex); marker.anchor.set(0.5, 1); marker.visible = false; overlay.addChild(marker);
function updateVisitors(t, view) {
  for (let k = 0; k < N; k++) {
    const s = vs[k]; if (!s) continue;
    const bi = base.i[k], bj = base.j[k];
    const bxs = sx(bi, bj), bys = sy(bi, bj);
    if (bxs < view.l - 60 || bxs > view.r + 60 || bys < view.t - 50 || bys > view.b + 70) { if (s.visible) s.visible = false; continue; }
    let i = bi, j = bj, dir = base.dir0[k], frame = 0;
    if (base.mode[k]) {
      if (base.road[k]) {
        const u = (t * base.speed[k] + base.phase[k]) % 1, fwd = u < 0.5, tri = fwd ? u * 2 : 2 - 2 * u, off = (tri - 0.5) * 2 * WALK;
        if (base.ax[k]) { i = bi + off; dir = fwd ? 0 : 3; } else { j = bj + off; dir = fwd ? 1 : 2; }   // SE,NW | SW,NE
        frame = Math.floor(t * SPEED_FRAMES + base.phase[k] * 4) & 3;
      } else {
        const a = t * 0.5 + base.phase[k] * 6.28;
        i = bi + Math.cos(a) * 0.4; j = bj + Math.sin(a) * 0.4;
        const di = -Math.sin(a), dj = Math.cos(a);
        dir = Math.abs(di) > Math.abs(dj) ? (di > 0 ? 0 : 3) : (dj > 0 ? 1 : 2);
        frame = Math.floor(t * SPEED_FRAMES + base.phase[k] * 4) & 3;
      }
    }
    s.texture = visTexture(looks[k], dir, frame);
    s.position.set(Math.round(sx(i, j)), Math.round(sy(i, j)));
    s.zIndex = (i + j) * 10 + 5;
    if (!s.visible) s.visible = true;
  }
}

// ------------------------------------------------------------ kamera
let cam = { x: 0, y: sy(0, 2), z: 3 };
const view = { l: 0, r: 0, t: 0, b: 0 };
function applyCam() {
  const W = app.screen.width, H = app.screen.height;
  world.scale.set(cam.z);
  world.position.set(Math.round(W / 2 - cam.x * cam.z), Math.round(H / 2 - cam.y * cam.z));
  view.l = cam.x - W / 2 / cam.z; view.r = cam.x + W / 2 / cam.z; view.t = cam.y - H / 2 / cam.z; view.b = cam.y + H / 2 / cam.z;
}
function zoomAt(nz, px, py) {
  nz = Math.max(1, Math.min(8, nz));
  const wx = cam.x + (px - app.screen.width / 2) / cam.z, wy = cam.y + (py - app.screen.height / 2) / cam.z;
  cam.z = nz; cam.x = wx - (px - app.screen.width / 2) / nz; cam.y = wy - (py - app.screen.height / 2) / nz;
}
let drag = null;
app.canvas.addEventListener('pointerdown', (e) => { drag = { x: e.clientX, y: e.clientY, cx: cam.x, cy: cam.y, moved: false }; app.canvas.setPointerCapture(e.pointerId); });
app.canvas.addEventListener('pointermove', (e) => {
  if (!drag) return;
  const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
  if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
  cam.x = drag.cx - dx / cam.z; cam.y = drag.cy - dy / cam.z;
});
app.canvas.addEventListener('pointerup', (e) => { if (drag && !drag.moved) clickAt(e.clientX, e.clientY); drag = null; });
app.canvas.addEventListener('wheel', (e) => { e.preventDefault(); zoomAt(cam.z + (e.deltaY < 0 ? 1 : -1), e.clientX, e.clientY); }, { passive: false });
$('zin').onclick = () => zoomAt(cam.z + 1, app.screen.width / 2, app.screen.height / 2);
$('zout').onclick = () => zoomAt(cam.z - 1, app.screen.width / 2, app.screen.height / 2);
$('home').onclick = () => { cam = { x: 0, y: sy(0, 2), z: 3 }; };

// ------------------------------------------------------------ HUD, hledání, karta
function drawHud() {
  const h = $('hud'); h.innerHTML = '';
  const add = (c) => h.appendChild(c);
  add(textCanvas(font, 'VISITORS', 2, '#fff0c8'));
  add(textCanvas(font, String(zoo.visitors), 4, '#ef5b5b'));
  const row = document.createElement('div'); row.className = 'row';
  row.appendChild(coinCanvas(3)); row.appendChild(textCanvas(font, zoo.coins.toLocaleString('en-US'), 3, '#f2b53c'));
  h.appendChild(row);
  add(textCanvas(font, `+${COIN_PER_VISITOR} PER VISITOR`, 1, '#fff0c8'));
}
drawHud();
function drawVote() {
  const el = $('vote'), v = zoo.vote;
  if (!v || v.closed) { el.style.display = 'none'; return; }
  el.style.display = 'block';
  el.innerHTML = `<b>TONIGHT'S VOTE</b><br>${v.options.map((o) => `<div class="opt"><span><b>${o.key}</b> ${o.name}</span><span>${o.price}c · ${v.counts[o.key] || 0}</span></div>`).join('')}<div class="hint">Comment a keyword on our post. Coins are shared by all visitors.</div>`;
}
drawVote();

function msg(t) { const m = $('msg'); m.textContent = t || ''; m.style.display = t ? 'block' : 'none'; if (t) setTimeout(() => { if (m.textContent === t) m.style.display = 'none'; }, 4000); }
async function visitorAt(k) {
  const c = Math.floor(k / zoo.idxChunk);
  const arr = await j$(`${DATA}/v/${c}.json`);
  return arr[k % zoo.idxChunk];
}
async function find(raw) {
  const h = normHandle(raw);
  if (!h) return;
  try {
    const sh = await j$(`${DATA}/h/${shardOf(h)}.json`);
    const hit = sh[h];
    if (!hit) { msg(`No visitor "${h}" yet. Follow us to get in!`); return; }
    msg(''); select(hit[0], true);
  } catch (e) { msg('Could not load data.'); }
}
$('search').addEventListener('submit', (e) => { e.preventDefault(); find($('q').value); });
$('cx').onclick = () => { $('card').style.display = 'none'; selected = -1; marker.visible = false; };

async function select(k, fly) {
  selected = k;
  const p = slotPos(k); if (!p) return;
  if (fly) { cam.x = sx(p.i, p.j); cam.y = sy(p.i, p.j) - 6; cam.z = Math.max(cam.z, 5); }
  let who = ['?', 1];
  try { who = await visitorAt(k); } catch {}
  const kind = vMeta.kinds[looks[k]] || 'plain';
  const names = { plain: 'Visitor', family: 'Parent with stroller', schoolkid: 'School kid', photographer: 'Photographer', balloon: 'Balloon fan', tourist: 'Tourist', grandpa: 'Grandpa', icecream: 'Ice cream kid', supporter: 'Friend of the zoo', plush: 'Plush lover', sitting: 'Bench sitter' };
  $('ch').textContent = '@' + who[0];
  $('cm').innerHTML = `${names[kind] || 'Visitor'}<br>Visitor #${(k + 1).toLocaleString('en-US')}<br>Joined day ${who[1]}<br>Earned the zoo ${COIN_PER_VISITOR} coins`;
  const cp = $('cprev'), ctx = cp.getContext('2d'); ctx.imageSmoothingEnabled = false;
  const idx = looks[k] * 16 + 0;
  cp.width = vMeta.cellW * 4; cp.height = vMeta.cellH * 4;
  const im = await loadImage(`${ASSETS}/atlas.png`);
  ctx.drawImage(im, (idx % vMeta.cols) * vMeta.cellW, Math.floor(idx / vMeta.cols) * vMeta.cellH, vMeta.cellW, vMeta.cellH, 0, 0, cp.width, cp.height);
  $('card').style.display = 'block';
}
function clickAt(px, py) {
  const wx = cam.x + (px - app.screen.width / 2) / cam.z, wy = cam.y + (py - app.screen.height / 2) / cam.z;
  let best = -1, bd = 14 * 14;
  for (let k = 0; k < N; k++) {
    const s = vs[k]; if (!s || !s.visible) continue;
    const dx = s.position.x - wx, dy = s.position.y - 5 - wy, d = dx * dx + dy * dy;
    if (d < bd) { bd = d; best = k; }
  }
  if (best >= 0) select(best, false);
}

// ------------------------------------------------------------ smyčka
let frames = 0, last = performance.now(), updMs = 0;
app.ticker.add(() => {
  const t = performance.now() / 1000;
  const u0 = performance.now(); applyCam(); updateVisitors(t, view); updMs = performance.now() - u0;
  if (selected >= 0 && vs[selected]) {
    const s = vs[selected];
    marker.visible = true;
    marker.position.set(s.position.x, s.position.y - 14 - Math.abs(Math.sin(t * 4)) * 2);
  }
  if (boardSprite) boardSprite.y = boardBase.y - 2 - Math.round(Math.sin(t * 2.2) * 1.5);
  frames++;
  if (performance.now() - last > 1000) { $('fps').textContent = `${frames} fps · ${N} visitors · r${R} · upd ${updMs.toFixed(1)} ms`; frames = 0; last = performance.now(); }
});
window.__zoo = { app, cam: () => cam, zoo, R, select, find };
