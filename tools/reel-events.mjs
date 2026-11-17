// Vypíše události reelu (pro zvukové efekty): node tools/reel-events.mjs marketing/reels/hook
import fs from 'node:fs';
import path from 'node:path';
import { plan } from '../web/src/reel-script.js';
const dir = process.argv[2] || 'marketing/reels/hook';
const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'), 'utf8'));
const p = plan(tl);
fs.writeFileSync(path.join(dir, 'events.json'), JSON.stringify(p.events.map((e) => ({ t: Math.round(e.t * 1000) / 1000, type: e.type })), null, 0));
console.log(`události: ${p.events.length}, příchodů: ${p.arrivals.length}, plot dokončen ${p.fenceDone.toFixed(1)} s, mince na konci ${p.coinsAt(p.total)}, návštěvníků ${p.visitorsAt(p.total)}`);
