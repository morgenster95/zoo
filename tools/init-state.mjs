// Vytvoří výchozí data/state.json: absolutně malá chudá zoo s 12 ukázkovými návštěvníky.
import { emptyState, addVisitor } from '../engine/state.js';
import { saveState } from './lib.mjs';
const s = emptyState();
['demo.anna', 'demo.tom', 'demo.mia', 'demo.leo', 'demo.zoe', 'demo.max', 'demo.eva', 'demo.sam', 'demo.nina', 'demo.ben', 'demo.kate', 'demo.luke'].forEach((h) => addVisitor(s, h, 1));
s.updated = new Date().toISOString();
saveState(s);
console.log('data/state.json: 12 ukázkových návštěvníků');
