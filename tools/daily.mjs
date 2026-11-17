// Denní tah (ráno 13:00 UTC): vyhodnotí běžící hlasování, posune den a otevře další z data/queue.json.
// node tools/daily.mjs            (zapíše data/state.json a web/public/data)
import fs from 'node:fs';
import path from 'node:path';
import { loadState, saveState, writePublic, ROOT } from './lib.mjs';
import { openVote, resolveVote, ensurePlots } from '../engine/vote.js';
import { balance } from '../engine/state.js';

const state = loadState();
const qf = path.join(ROOT, 'data', 'queue.json');
const queue = fs.existsSync(qf) ? JSON.parse(fs.readFileSync(qf, 'utf8')) : [];
if (state.vote && !state.vote.closed) {
  const r = resolveVote(state, state.day);
  console.log('Vyhodnoceno:', JSON.stringify(r));
}
state.day += 1;
ensurePlots(state, 2);
state.queueUsed ||= 0;
while (state.queueUsed < queue.length) {
  const next = queue[state.queueUsed++];
  try { openVote(state, next.options, state.day); console.log('Otevřeno hlasování:', next.options.join(', ')); break; }
  catch (e) { console.log('Přeskočeno (', e.message, ')'); }   // nedostupná nabídka se přeskočí, majitel ji vidí v logu
}
state.updated = new Date().toISOString();
saveState(state);
writePublic(state);
console.log(`Den ${state.day}, návštěvníků ${state.visitors.length}, zůstatek ${balance(state)}`);
