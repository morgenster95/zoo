// Ukázková zoo s hotovými stavbami (jen pro náhled, nezapisuje data/state.json): node tools/demo-state.mjs [počet návštěvníků]
import { emptyState, addVisitor } from '../engine/state.js';
import { openVote, resolveVote, ensurePlots } from '../engine/vote.js';
import { writePublic } from './lib.mjs';
const n = Number(process.argv[2] || 1500);
const s = emptyState();
for (let k = 0; k < n; k++) addVisitor(s, 'guest' + k, 1 + Math.floor(k / 200));
const order = ['stonegate', 'ticketbooth', 'giraffes', 'cafe', 'pandas', 'elephants', 'penguins', 'carousel', 'shop', 'monkeys', 'aviary', 'lions', 'aquarium', 'playground', 'clinic', 'ferris'];
for (const id of order) { s.vote = null; try { openVote(s, [id, 'bench']); resolveVote(s); } catch (e) { console.log('skip', id, e.message); } }
ensurePlots(s, 2);
s.updated = new Date().toISOString();
const z = writePublic(s);
console.log(`demo: ${z.visitors} návštěvníků, mince ${z.coins}, ring ${z.ring}, parcel ${Object.keys(z.lots).length}`);
