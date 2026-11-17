// Mapa zoo: nekonečná izometrická mřížka dlaždic (i, j), počátek = střed náměstí.
// Silnice leží na každé 6. čáře (i % 6 == 0 nebo j % 6 == 0), mezi nimi jsou bloky 5×5 (parcely).
// Brána je na jihu (0, GATE_J). Otevřená oblast roste po prstencích r (viz regionFor), podle toho, kolik míst je zabrané návštěvníky.
// Nic tu nezávisí na prohlížeči: stejný kód používá web i Node (build dat, testy).

export const BLOCK = 6;
export const GATE_J = 6;
export const LOOKS = 256;
export const COIN_PER_VISITOR = 10;
export const START_COINS = 500;   // počáteční fond (rozhodnutí 17. 11. 2026, podle vzorového videa); mění se jednou konstantou
export const R_MAX = 16;           // největší připravený prstenec (≈ 30 000 míst); dál je potřeba rozšířit
export const CAP_ROAD = 5;         // návštěvníků na dlaždici silnice
export const CAP_PLAZA = 8;        // návštěvníků na dlaždici náměstí

const mod = (a, n) => ((a % n) + n) % n;

export const inRegion = (i, j, r) => i >= -BLOCK * r && i <= BLOCK * r && j >= -BLOCK * r && j <= GATE_J;
export const isPlaza = (i, j) => Math.abs(i) <= 1 && Math.abs(j) <= 1;
export const isRoad = (i, j) => mod(i, BLOCK) === 0 || mod(j, BLOCK) === 0;
export const isWalk = (i, j) => isRoad(i, j) || isPlaza(i, j);
export const blockOf = (i, j) => ({ a: Math.floor(i / BLOCK), b: Math.floor(j / BLOCK) });
export const lotKey = (a, b) => `${a},${b}`;
/** nejmenší prstenec, který obsahuje dlaždici */
export const ringOf = (i, j) => Math.max(1, Math.ceil(Math.max(Math.abs(i), j < 0 ? -j : 0) / BLOCK));

/** parcely (bloky) uvnitř prstence r */
export function lotsIn(r) {
  const out = [];
  for (let a = -r; a < r; a++) for (let b = -r; b <= 0; b++) out.push({ a, b });
  return out;
}

/** vnitřek parcely: dlaždice i∈[6a+1, 6a+5], j∈[6b+1, 6b+5]; rohy plotu */
export function lotBox(a, b) {
  return { i0: BLOCK * a + 1, j0: BLOCK * b + 1, i1: BLOCK * a + 5, j1: BLOCK * b + 5, ci: BLOCK * a + 3.5, cj: BLOCK * b + 3.5 };
}

// ---- místa pro návštěvníky: pevné pořadí, nezávislé na tom, co je kde postaveno (nikdo se nikdy nepřesune)
const OFFS = [[0.5, 0.5], [0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75], [0.5, 0.15], [0.15, 0.5], [0.85, 0.5]];
let _slots = null;
export function slotTable() {
  if (_slots) return _slots;
  const tiles = [];
  for (let i = -BLOCK * R_MAX; i <= BLOCK * R_MAX; i++) {
    for (let j = -BLOCK * R_MAX; j <= GATE_J; j++) {
      if (!isWalk(i, j)) continue;
      const d = Math.hypot(i, (j - 2) * 1.0);
      tiles.push({ i, j, d });
    }
  }
  tiles.sort((p, q) => p.d - q.d || p.i - q.i || p.j - q.j);
  const si = [], sj = [], ss = [];
  for (const t of tiles) {
    const cap = isPlaza(t.i, t.j) ? CAP_PLAZA : CAP_ROAD;
    for (let s = 0; s < cap; s++) { si.push(t.i); sj.push(t.j); ss.push(s); }
  }
  _slots = { n: si.length, i: si, j: sj, s: ss };
  return _slots;
}

/** světové souřadnice místa k (dlaždice + posun uvnitř ní) */
export function slotPos(k) {
  const t = slotTable();
  if (k >= t.n) return null;
  const o = OFFS[t.s[k] % OFFS.length];
  return { i: t.i[k] + o[0], j: t.j[k] + o[1], ti: t.i[k], tj: t.j[k], road: !isPlaza(t.i[k], t.j[k]), alongI: mod(t.j[k], BLOCK) === 0 };
}

/** prstenec otevřené oblasti pro n návštěvníků (+ rezerva, aby zoo „dýchalo“) */
export function regionFor(n) {
  const t = slotTable();
  let r = 1;
  const last = Math.min(n, t.n) - 1;
  // nejvzdálenější dlaždice mezi obsazenými místy rostou monotónně s indexem po prstencích, stačí zkontrolovat průběžně
  for (let k = Math.max(0, last - 40); k <= last; k++) r = Math.max(r, ringOf(t.i[k], t.j[k]));
  const maxRing = (() => { let m = 1; for (let k = 0; k <= last; k += 25) m = Math.max(m, ringOf(t.i[k], t.j[k])); return m; })();
  r = Math.max(r, maxRing);
  return Math.min(R_MAX, r);
}

/** výchozí obsah parcel (absolutně malá a chudá zoo) */
export const START_LOTS = {
  '-1,-1': { t: 'paddock', animals: ['alpaca', 'alpaca'] },
  '0,-1': { t: 'pond', animals: ['flamingo', 'flamingo'] },
  '-1,0': { t: 'plot', id: 1 },
  '0,0': { t: 'plot', id: 2 },
};
