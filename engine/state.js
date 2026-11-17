// Stav hry: návštěvníci, utracené mince, obsah parcel. Databáze je soubor (data/state.json), ručně se neupravuje.
import { hashString } from './rng.js';
import { LOOKS, COIN_PER_VISITOR, START_LOTS } from './layout.js';

export const SHARDS = 256;        // počet souborů pro hledání @handle
export const LOOK_CHUNK = 4096;   // kolik vzhledů v jednom souboru
export const IDX_CHUNK = 256;     // kolik návštěvníků (handle, den) v jednom souboru pro kartu podle indexu

export const normHandle = (h) => String(h).trim().replace(/^@/, '').toLowerCase().replace(/[^a-z0-9._]/g, '').slice(0, 30);
export const lookOf = (handle) => hashString('look:' + handle) % LOOKS;
export const shardOf = (handle) => hashString(handle) % SHARDS;

export function emptyState() {
  return { theme: 'zoo', day: 1, visitors: [], spent: 0, lots: JSON.parse(JSON.stringify(START_LOTS)), vote: null, history: [], updated: null };
}

/** přidá návštěvníka (jen jednou na účet); vrací jeho index nebo -1 */
export function addVisitor(state, rawHandle, day = state.day) {
  const h = normHandle(rawHandle);
  if (!h) return -1;
  state._index ||= new Map(state.visitors.map((v, k) => [v.h, k]));
  if (state._index.has(h)) return -1;
  state.visitors.push({ h, d: day, l: lookOf(h) });
  state._index.set(h, state.visitors.length - 1);
  return state.visitors.length - 1;
}

export const coinsEarned = (n) => n * COIN_PER_VISITOR;
export const balance = (state) => coinsEarned(state.visitors.length) - (state.spent || 0);
