// Plán reelu „Hook: Day 1“ (struktura podle vzorového virálního videa, téma zoo). Čistý JS bez DOM:
// používá ho vykreslování (web/src/reel.js) i Node (tools/reel-events.mjs → efekty pro zvuk).
// Vše je funkce času t (s), takže snímek lze vykreslit v libovolném pořadí.
import { slotPos, START_LOTS } from '../../engine/layout.js';
import { fenceOf, placeLot } from '../../engine/place.js';
import { hashString } from '../../engine/rng.js';

export const START_COINS = 500;
export const FENCE_COST = 200;
export const BUS_BONUS = 20;
export const GATE_J = 6;

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
export const lerp = (a, b, k) => a + (b - a) * k;

/** body cesty → funkce času (konstantní rychlost); vrací {i, j, dir, moving} */
export function walker(points, t0, speed) {
  const seg = [];
  let len = 0;
  for (let k = 1; k < points.length; k++) { const d = Math.hypot(points[k][0] - points[k - 1][0], points[k][1] - points[k - 1][1]); seg.push(d); len += d; }
  const dur = len / speed;
  const at = (t) => {
    let s = clamp((t - t0) * speed, 0, len);
    let k = 0;
    while (k < seg.length - 1 && s > seg[k]) { s -= seg[k]; k++; }
    const a = points[k], b = points[k + 1] || points[k], f = seg[k] ? s / seg[k] : 0;
    const di = b[0] - a[0], dj = b[1] - a[1];
    // směr sprite: SE = +i, SW = +j, NE = −j, NW = −i
    const dir = Math.abs(di) > Math.abs(dj) ? (di > 0 ? 0 : 3) : (dj > 0 ? 1 : 2);
    return { i: lerp(a[0], b[0], f), j: lerp(a[1], b[1], f), dir, moving: t > t0 && t < t0 + dur };
  };
  return { at, t0, t1: t0 + dur, dur };
}

/** cesta od brány na místo k (po silnicích: vždy po osách) */
export function routeTo(k) {
  const p = slotPos(k);
  const gate = [0.5 + ((k % 3) - 1) * 0.12, GATE_J + 4.5], door = [0.5 + ((k % 3) - 1) * 0.12, GATE_J + 1.4];
  const pts = [gate, door, [0.5, GATE_J - 0.6]];
  const Ti = p.ti, Tj = p.tj, mod6 = (a) => ((a % 6) + 6) % 6;
  if (Ti === 0 && mod6(Tj) !== 0 || (Ti === 0 && Tj === 0)) pts.push([p.i, p.j]);             // na vstupní silnici
  else if (mod6(Ti) === 0) { pts.push([0.5, 0.5], [Ti + 0.5, 0.5], [p.i, p.j]); }                 // jiná silnice podél j
  else { pts.push([0.5, Tj + 0.5], [p.i, p.j]); }                                                  // silnice podél i
  return pts;
}

export function plan(tl) {
  const L = Object.fromEntries(tl.lines.map((l) => [l.id, l]));
  const total = tl.total;
  const cue = {
    intro: L.intro.start, visitor: L.visitor.start, coins: L.coins.start, poor: L.poor.start, escape: L.escape.start,
    fence: L.fence.start, vote: L.vote.start, bus: L.bus.start, cta: L.cta.start,
  };
  // ---- příchody návštěvníků (zrychlují; každý přidá 10 mincí v okamžiku, kdy projde bránou)
  const arrivals = [];
  let t = cue.visitor + 0.1, gap = 2.4, k = 0;
  while (t < total - 7.5 && k < 13) {          // jen ilustrativně: pár návštěvníků, ne celý dav
    const w = walker(routeTo(k), t, 2.1);
    arrivals.push({ k, t0: t, walk: w, tGate: t + (4.5 - 1.4) / 2.1, look: hashString('r' + k) % 256 });
    t += gap; gap = Math.max(1.5, gap * 0.9); k++;
  }
  // ---- zebra, která uteče
  const pad = fenceOf(-1, -1);                                               // plot výběhu pro zebry
  const zl = placeLot(-1, -1, START_LOTS['-1,-1'], '-1,-1').items.filter((x) => x.role === 'animal');
  const zebraStart = [zl[0].i, zl[0].j], zj = zl[0].j;
  const zebraRun = walker([zebraStart, [-1.0, zj], [0.5, zj], [0.5, -16]], cue.escape + 0.35, 3.4);
  const zebraBack = walker([[0.5, -12], [0.5, zj], [-1.0, zj], zebraStart], cue.fence + 2.0, 4.0);
  // ---- plot: pořadí dílů (obchází výběh), poslední díl uzavře mezeru u východní silnice
  const f = fenceOf(-1, -1);
  const steps = [];
  const sidesI = [], sidesJ = [];
  for (let i = f.i0; i < f.i1 - 1e-6; i++) sidesI.push(i);
  for (let j = f.j0; j < f.j1 - 1e-6; j++) sidesJ.push(j);
  // jižní strana (j = j1), východní (i = i1), severní (j = j0), západní (i = i0): zleva dolů dokola
  sidesI.forEach((i) => steps.push({ seg: 'seg_i', i, j: f.j1, post: [i, f.j1] }));
  sidesJ.slice().reverse().forEach((j) => steps.push({ seg: 'seg_j', i: f.i1, j, post: [f.i1, j + 1] }));
  sidesI.slice().reverse().forEach((i) => steps.push({ seg: 'seg_i', i, j: f.j0, post: [i + 1, f.j0] }));
  sidesJ.forEach((j) => steps.push({ seg: 'seg_j', i: f.i0, j, post: [f.i0, j] }));
  const fenceStart = cue.fence + 0.4, fenceDur = 3.2;
  steps.forEach((s, n) => { s.t = fenceStart + (n / steps.length) * fenceDur; });
  // dva díly na východní straně (mezera pro zebru) se dokončí až po jejím návratu
  const gapIdx = steps.map((s, n) => (s.seg === 'seg_j' && s.i === f.i1 && s.j >= zj - 1.2 && s.j <= zj + 0.4 ? n : -1)).filter((n) => n >= 0);
  gapIdx.forEach((n) => { steps[n].t = zebraBack.t1 - 0.2 + (n - gapIdx[0]) * 0.18; });
  const fenceDone = Math.max(...steps.map((s) => s.t)) + 0.3;
  // ---- mince: bilance v čase
  const events = [];
  const ledger = [{ t: 0, d: 0, v: 0 }];
  arrivals.forEach((a, n) => { ledger.push({ t: a.tGate, d: 10, v: 1 }); if (n < 2) events.push({ t: a.tGate, type: 'coin' }); });   // cinká jen u prvních dvou, ať to neruší
  const tBuy = cue.fence + 0.15;
  ledger.push({ t: tBuy, d: -FENCE_COST, v: 0 }); events.push({ t: tBuy, type: 'thunk' });
  const tBus = cue.bus + 2.3;
  ledger.push({ t: tBus + 0.5, d: BUS_BONUS, v: 0 }); events.push({ t: tBus - 0.3, type: 'honk' }, { t: tBus + 0.5, type: 'coin' }, { t: tBus + 0.55, type: 'spark' });
  ledger.sort((a, b) => a.t - b.t);
  const coinsAt = (tt) => START_COINS + ledger.filter((e) => e.t <= tt).reduce((a, e) => a + e.d, 0);
  const visitorsAt = (tt) => ledger.filter((e) => e.t <= tt).reduce((a, e) => a + e.v, 0);
  events.push({ t: cue.escape + 0.3, type: 'boing' }, { t: cue.escape + 0.6, type: 'whoosh' });
  steps.forEach((s) => events.push({ t: s.t, type: 'tick' }));
  events.push({ t: fenceDone - 0.2, type: 'thunk' }, { t: fenceDone, type: 'spark' });
  // ---- náhledy staveb (ghost) na volné parcele při hlasování
  const previews = [
    { name: 'bp_cafe', label: 'CAFE', price: 300, t: cue.vote + 2.0 },
    { name: 'bp_playground', label: 'PLAYGROUND', price: 250, t: cue.vote + 3.4 },
    { name: 'bp_penguin_house', label: 'PENGUINS', price: 500, t: cue.vote + 4.8 },
  ];
  previews.forEach((p) => events.push({ t: p.t, type: 'pop' }, { t: p.t + 0.05, type: 'spark' }));
  const bus = walker([[0.5, 21], [0.5, 10.4]], cue.bus - 0.2, 4.2);
  events.push({ t: cue.bus - 0.2, type: 'whoosh' });
  events.sort((a, b) => a.t - b.t);
  return { total, cue, lines: tl.lines, arrivals, zebraRun, zebraBack, zebraStart, steps, fenceDone, tBuy, tBus, previews, bus, events, coinsAt, visitorsAt, ledger, pad };
}
