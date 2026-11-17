// Kde co v parcele stojí (čistá funkce, používá web i reel i testy). Souřadnice jsou dílky (i, j) mapy.
// Pravidla: plot je 4×4 vystředěný v bloku 5×5; zvířata zůstávají uvnitř plotu s odstupem a nepřekrývají domek ani sebe;
// zvířata nikdy nestojí na silnici (tam chodí návštěvníci).
import { lotBox } from './layout.js';
import { rngFor } from './rng.js';

export const ANIMAL_MARGIN = 1.0;     // odstup středu zvířete od plotu (dílků)
export const ANIMAL_GAP = 1.25;       // nejmenší vzdálenost zvířat od sebe
export const SPRITE_FP = (w) => Math.min(1.1, (w || 48) / 64);   // přední roh základny budovy: střed + w/64

export function fenceOf(a, b) {
  const bx = lotBox(a, b);
  return { i0: bx.i0 + 0.5, j0: bx.j0 + 0.5, i1: bx.i1 + 0.5, j1: bx.j1 + 0.5 };
}

/** vrací { fence, items:[{role,name,i,j,flip,z}] } pro parcelu; `widthOf(name)` = šířka spritu v px */
export function placeLot(a, b, lot, key, widthOf = () => 48) {
  const bx = lotBox(a, b), ci = bx.ci, cj = bx.cj, rng = rngFor('lot', key);
  const items = [];
  const fp = (name) => SPRITE_FP(widthOf(name));
  let fence = null;
  if (!lot) return { fence, items, free: true };
  if (lot.t === 'plot') {
    items.push({ role: 'plot', name: 'plot', i: ci + 1, j: cj + 1, z: 0 }, { role: 'sign', name: 'q_sign', i: ci - 1.9, j: cj + 1.0, z: 4 });
    return { fence, items };
  }
  const placed = [];
  const free = (i, j, r) => placed.every((p) => Math.hypot(p.i - i, p.j - j) >= Math.max(r, p.r));
  if (lot.t === 'paddock' || lot.t === 'pond') {
    fence = fenceOf(a, b);
    if (lot.t === 'pond') {
      items.push({ role: 'deco', name: 'reeds', i: ci - 1.5, j: cj + 1.3, z: 3 }, { role: 'deco', name: 'reeds', i: ci + 1.5, j: cj - 1.2, z: 1 });
    }
    if (lot.house && widthOf(lot.house)) {                // domek vzadu (v rohu u silnice s nižším i+j), zvířata před ním
      const o = fp(lot.house);
      items.push({ role: 'house', name: lot.house, i: ci - 0.8 + o, j: cj - 0.8 + o, z: 1 });
      placed.push({ i: ci - 0.8, j: cj - 0.8, r: 1.3 });
    }
    const lo = ANIMAL_MARGIN, ix0 = fence.i0 + lo, ix1 = fence.i1 - lo, jy0 = fence.j0 + lo, jy1 = fence.j1 - lo;
    const names = lot.animals || [], n = names.length, spots = [];
    let ok = true;
    for (let k = 0; k < n && ok; k++) {
      let pos = null;
      for (let t = 0; t < 120 && !pos; t++) {
        const gap = t < 40 ? ANIMAL_GAP : t < 80 ? 1.05 : 0.9;        // když je málo místa, zvířata se přiblíží, ale nepřekryjí
        const i = lot.t === 'pond' ? ci - 1.0 + rng() * 2.0 : ix0 + rng() * (ix1 - ix0);
        const j = lot.t === 'pond' ? cj - 0.8 + rng() * 1.6 : jy0 + rng() * (jy1 - jy0);
        if (free(i, j, gap)) pos = { i, j };
      }
      if (!pos) ok = false; else { placed.push({ ...pos, r: 0.9 }); spots.push(pos); }
    }
    if (!ok) {                                                           // nouzově pravidelná mřížka přes celý výběh (všechna zvířata)
      spots.length = 0;
      const cols = Math.ceil(Math.sqrt(n)), rows = Math.ceil(n / cols);
      for (let k = 0; k < n; k++) { const c = k % cols, r = Math.floor(k / cols); spots.push({ i: ix0 + ((c + 0.5) / cols) * (ix1 - ix0), j: jy0 + ((r + 0.5) / rows) * (jy1 - jy0) }); }
    }
    names.forEach((an, k) => items.push({ role: 'animal', name: 'a_' + an, i: spots[k].i, j: spots[k].j, flip: rng() < 0.5, z: 2 }));
    return { fence, items };
  }
  if (lot.t === 'build') {
    const o = fp(lot.sprite);
    items.push({ role: 'building', name: lot.sprite, i: ci + o, j: cj + o, z: 1 });
    const spots = [[1.6, -0.2], [-0.2, 1.6], [1.5, 1.5], [1.9, 0.8], [0.8, 1.9]];
    (lot.animals || []).forEach((an, k) => {
      const s = spots[k % spots.length];
      items.push({ role: 'animal', name: 'a_' + an, i: ci + s[0], j: cj + s[1], flip: k % 2 === 1, z: 3 });
    });
    return { fence, items };
  }
  return { fence, items };
}
