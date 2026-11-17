// Falešná soupiska pro vývoj a měření: node tools/fake-roster.mjs 4000  → web/public/data
import { emptyState, addVisitor } from '../engine/state.js';
import { mulberry32 } from '../engine/rng.js';
import { writePublic } from './lib.mjs';

const n = Number(process.argv[2] || 4000);
const rng = mulberry32(12345);
const A = ['lucy', 'tom', 'anna', 'jake', 'mia', 'leo', 'zoe', 'max', 'eva', 'sam', 'nina', 'ben', 'kate', 'luke', 'ivy', 'omar', 'yuki', 'sara', 'dan', 'lola'];
const B = ['loves', 'plays', 'draws', 'cooks', 'reads', 'runs', 'wanders', 'snaps', 'sings', 'dreams'];
const C = ['pandas', 'zoo', 'coffee', 'books', 'cats', 'art', 'bikes', 'tea', 'music', 'trips'];
const s = emptyState();
s.day = 1 + Math.floor(n / 800);
let made = 0, guard = 0;
while (made < n && guard++ < n * 20) {
  const a = A[Math.floor(rng() * A.length)], r = rng();
  const h = r < .35 ? `${a}_${B[Math.floor(rng() * B.length)]}${C[Math.floor(rng() * C.length)]}` : r < .7 ? `${a}${Math.floor(rng() * 9999)}` : `${a}.${C[Math.floor(rng() * C.length)]}${Math.floor(rng() * 99)}`;
  const day = 1 + Math.floor((made / n) * s.day);
  if (addVisitor(s, h, day) >= 0) made++;
}
s.updated = new Date().toISOString();
const zoo = writePublic(s);
console.log(`web/public/data: ${zoo.visitors} návštěvníků, mince ${zoo.coins}, dávek vzhledů ${zoo.lookChunks}`);
