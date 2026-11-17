// Hlasování o stavbách. Majitel hry (ne algoritmus) vybírá možnosti; mince jsou společné.
// Rytmus jako ve frontě: večer se hlasování otevře, ráno se vyhodnotí a stavba stojí hned (viz docs/MECHANICS.md).
import { CATALOG, itemByKey } from './catalog.js';
import { balance } from './state.js';
import { regionFor, lotsIn, lotKey } from './layout.js';

/** otevře hlasování; možnosti jsou id položek z katalogu, každá musí být ze zůstatku zaplacená */
export function openVote(state, itemIds, day = state.day) {
  if (state.vote && !state.vote.closed) throw new Error('Hlasování už běží');
  if (itemIds.length < 2 || itemIds.length > 4) throw new Error('Nabídni 2 až 4 možnosti');
  const options = itemIds.map((id) => {
    const it = CATALOG[id];
    if (!it) throw new Error('Neznámá položka ' + id);
    if (it.price > balance(state)) throw new Error(`${id} (${it.price}) je dražší než zůstatek ${balance(state)}`);
    return { id, key: it.key, name: it.name, price: it.price };
  });
  if (new Set(options.map((o) => o.key)).size !== options.length) throw new Error('Klíčová slova se opakují');
  state.vote = { day, options, votes: {}, closed: false };
  return state.vote;
}

/** komentář s klíčovým slovem → hlas; vrací zvolenou možnost nebo null. Hlasuje jen návštěvník, platí poslední hlas. */
export function castVote(state, handle, text) {
  const v = state.vote;
  if (!v || v.closed) return null;
  state._index ||= new Map(state.visitors.map((x, k) => [x.h, k]));
  if (!state._index.has(handle)) return null;
  const words = String(text).toUpperCase().match(/[A-Z]+/g) || [];
  const hits = v.options.filter((o) => words.includes(o.key));
  if (hits.length !== 1) return null;       // žádné nebo víc různých slov = nejasné
  v.votes[handle] = hits[0].key;
  return hits[0];
}

export function tally(vote) {
  const c = Object.fromEntries(vote.options.map((o) => [o.key, 0]));
  Object.values(vote.votes).forEach((k) => { if (k in c) c[k]++; });
  return c;
}

/** volné parcely (plot) podle čísla; když žádná není, vrací null */
export function freePlots(state) {
  return Object.entries(state.lots).filter(([, l]) => l.t === 'plot').sort((a, b) => a[1].id - b[1].id).map(([k]) => k);
}

/** zajistí, že jsou volné aspoň `n` parcely (nejbližší volné bloky v otevřené oblasti od středu) */
export function ensurePlots(state, n = 2) {
  let have = freePlots(state).length;
  let r = Math.max(state.ring || 1, regionFor(state.visitors.length));
  let nextId = Math.max(0, ...Object.values(state.lots).map((l) => l.id || 0)) + 1;
  while (have < n && r <= 16) {
    const free = lotsIn(r).filter(({ a, b }) => !state.lots[lotKey(a, b)])
      .sort((p, q) => Math.hypot(p.a + 0.5, p.b + 0.5) - Math.hypot(q.a + 0.5, q.b + 0.5) || p.a - q.a || p.b - q.b);
    while (have < n && free.length) { const { a, b } = free.shift(); state.lots[lotKey(a, b)] = { t: 'plot', id: nextId++ }; have++; }
    if (have < n) r++;          // došly volné bloky: mapa se rozšíří o další prstenec
  }
  state.ring = Math.max(state.ring || 1, r);   // web otevře aspoň tento prstenec, i když návštěvníků ještě tolik není
}

/** vyhodnotí hlasování: vítěz = nejvíc hlasů; remíza nebo nula hlasů = první v pořadí, jak nabídl majitel */
export function resolveVote(state, day = state.day) {
  const v = state.vote;
  if (!v || v.closed) return null;
  const counts = tally(v);
  let best = v.options.filter((o) => balance(state) >= o.price)[0];     // pojistka: bez peněz se bere nejlevnější možný
  if (!best) { v.closed = true; v.result = { none: true, counts }; return v.result; }
  let top = -1;
  for (const o of v.options) if (counts[o.key] > top && balance(state) >= o.price) { top = counts[o.key]; best = o; }
  const item = CATALOG[best.id];
  let lotId = null;
  state.spent = (state.spent || 0) + item.price;
  if (item.lot.t === 'upgrade') {                 // vstupní brána, pokladna: mění stávající budovu, parcelu nezabírá
    (state.upgrades ||= {})[item.lot.what] = item.lot.sprite;
  } else {
    if (!freePlots(state).length) ensurePlots(state, 1);
    lotId = freePlots(state)[0];
    state.lots[lotId] = { ...JSON.parse(JSON.stringify(item.lot)), item: best.id, day };
  }
  ensurePlots(state, 2);
  v.closed = true;
  v.result = { winner: best.key, id: best.id, lot: lotId, price: item.price, counts, total: Object.values(counts).reduce((a, b) => a + b, 0) };
  (state.history ||= []).push({ day, ...v.result });
  return v.result;
}
