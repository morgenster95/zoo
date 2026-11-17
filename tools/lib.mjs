import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { publicData } from '../engine/export.js';

export const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
export const PUBLIC = path.join(ROOT, 'web', 'public', 'data');

export function loadState(file = path.join(ROOT, 'data', 'state.json')) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}
export function saveState(state, file = path.join(ROOT, 'data', 'state.json')) {
  const { _index, ...clean } = state;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(clean));
}

/** zapíše statická data webu: zoo.json, looks/N.bin, h/N.json (kompaktní, bez mezer) */
export function writePublic(state, dir = PUBLIC) {
  const { zoo, looks, shards, idx } = publicData(state);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(path.join(dir, 'looks'), { recursive: true });
  fs.mkdirSync(path.join(dir, 'h'), { recursive: true });
  fs.mkdirSync(path.join(dir, 'v'), { recursive: true });
  fs.writeFileSync(path.join(dir, 'zoo.json'), JSON.stringify(zoo));
  looks.forEach((arr, c) => fs.writeFileSync(path.join(dir, 'looks', `${c}.bin`), Buffer.from(arr.buffer)));
  shards.forEach((sh, k) => fs.writeFileSync(path.join(dir, 'h', `${k}.json`), JSON.stringify(sh)));
  idx.forEach((arr, c) => fs.writeFileSync(path.join(dir, 'v', `${c}.json`), JSON.stringify(arr)));
  return zoo;
}
