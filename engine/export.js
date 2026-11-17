// Převod stavu na statické soubory pro web (malé dávky, ať nikdy nestahujeme celou soupisku).
import { balance, SHARDS, LOOK_CHUNK, IDX_CHUNK, shardOf } from './state.js';

export function publicData(state) {
  const n = state.visitors.length;
  const zoo = {
    v: 1, updated: state.updated, day: state.day, visitors: n, coins: balance(state), spent: state.spent || 0,
    lots: state.lots, shards: SHARDS, lookChunk: LOOK_CHUNK, lookChunks: Math.ceil(n / LOOK_CHUNK), idxChunk: IDX_CHUNK,
  };
  const looks = [];
  for (let c = 0; c * LOOK_CHUNK < n; c++) {
    const arr = new Uint16Array(Math.min(LOOK_CHUNK, n - c * LOOK_CHUNK));
    for (let k = 0; k < arr.length; k++) arr[k] = state.visitors[c * LOOK_CHUNK + k].l;
    looks.push(arr);
  }
  const shards = Array.from({ length: SHARDS }, () => ({}));
  state.visitors.forEach((v, k) => { shards[shardOf(v.h)][v.h] = [k, v.d]; });
  const idx = [];
  for (let c = 0; c * IDX_CHUNK < n; c++) idx.push(state.visitors.slice(c * IDX_CHUNK, (c + 1) * IDX_CHUNK).map((v) => [v.h, v.d]));
  return { zoo, looks, shards, idx };
}
