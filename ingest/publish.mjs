// Publikování reelu na Instagram (Content Publishing API, stejný systémový token jako ve frontě): fronta v marketing/queue.json.
// Video leží ve veřejném repu morgenster95/zoo-media (GitHub Pages), odtud si ho Instagram stáhne:
// https://morgenster95.github.io/zoo-media/<soubor>. Zveřejnění je veřejná akce: spouští se jen ručně (workflow publish).
// Použití: node ingest/publish.mjs <id>      (DRY_RUN=1 jen zkontroluje a nic nepošle)
// Proměnné: IG_ACCESS_TOKEN, IG_USER_ID, MEDIA_URL
import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from '../tools/lib.mjs';

const API = `https://${process.env.IG_API_HOST || 'graph.facebook.com'}/${process.env.IG_API_VERSION || 'v23.0'}`;
const TOKEN = process.env.IG_ACCESS_TOKEN, USER = process.env.IG_USER_ID;
const MEDIA = process.env.MEDIA_URL || 'https://morgenster95.github.io/zoo-media';
const QUEUE = path.join(ROOT, 'marketing', 'queue.json');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function call(method, p, params = {}) {
  const u = new URL(`${API}/${p}`);
  for (const [k, v] of Object.entries({ ...params, access_token: TOKEN })) u.searchParams.set(k, v);
  const j = await (await fetch(u, { method })).json();
  if (j.error) throw new Error(`${method} ${p}: ${j.error.message}`);
  return j;
}
async function waitReady(id) {
  for (let i = 0; i < 60; i++) {
    const s = await call('GET', id, { fields: 'status_code,status' });
    if (s.status_code === 'FINISHED') return;
    if (s.status_code === 'ERROR' || s.status_code === 'EXPIRED') throw new Error(`kontejner ${id}: ${s.status_code} ${s.status || ''}`);
    await sleep(5000);
  }
  throw new Error(`kontejner ${id}: zpracování trvá příliš dlouho`);
}

const queue = JSON.parse(fs.readFileSync(QUEUE, 'utf8'));
const item = queue.find((x) => x.id === process.argv[2]);
if (!item) { console.error('položka nenalezena'); process.exit(1); }
if (item.published) { console.log('už zveřejněno:', item.published); process.exit(0); }
if (!TOKEN || !USER) { console.error('Chybí IG_ACCESS_TOKEN nebo IG_USER_ID'); process.exit(1); }
const url = `${MEDIA}/${item.files[0]}`;
const head = await fetch(url, { method: 'HEAD' }).catch(() => null);
if (!head || !head.ok) { console.error(`soubor ještě není na webu: ${url} (${head?.status})`); process.exit(1); }
console.log(`video na webu: ${url} (${head.headers.get('content-length')} B)`);
if (process.env.DRY_RUN) { console.log('DRY_RUN: nic se neposílá'); process.exit(0); }
const creation = (await call('POST', `${USER}/media`, { media_type: 'REELS', video_url: url, caption: item.caption, share_to_feed: 'true' })).id;
console.log('kontejner', creation); await waitReady(creation);
const id = (await call('POST', `${USER}/media_publish`, { creation_id: creation })).id;
const info = await call('GET', id, { fields: 'permalink' }).catch(() => ({}));
item.published = { id, permalink: info.permalink || null, at: new Date().toISOString() };
fs.writeFileSync(QUEUE, JSON.stringify(queue, null, 2) + '\n');
console.log('ZVEŘEJNĚNO:', info.permalink || id);
