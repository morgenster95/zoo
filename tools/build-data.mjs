// Ze stavu hry (data/state.json) vyrobí statická data webu (web/public/data).
import fs from 'node:fs';
import path from 'node:path';
import { loadState, writePublic, ROOT } from './lib.mjs';
const file = path.join(ROOT, 'data', 'state.json');
if (!fs.existsSync(file)) { console.error('Chybí data/state.json (viz tools/init-state.mjs)'); process.exit(1); }
const zoo = writePublic(loadState(file));
console.log(`web/public/data: ${zoo.visitors} návštěvníků, mince ${zoo.coins}`);
