import test from 'node:test';
import assert from 'node:assert/strict';
import { slotTable, slotPos, regionFor, isWalk, ringOf, GATE_J, lotBox, inRegion } from './layout.js';
import { emptyState, addVisitor, balance, lookOf, normHandle } from './state.js';
import { publicData } from './export.js';
import { hashString, rngFor } from './rng.js';

test('hash a rng jsou deterministické', () => {
  assert.equal(hashString('abc'), hashString('abc'));
  assert.notEqual(hashString('abc'), hashString('abd'));
  assert.equal(rngFor('x', 1)(), rngFor('x', 1)());
});

test('místa: pevné pořadí, všechna na chůzi, bez duplicit', () => {
  const t = slotTable();
  assert.ok(t.n > 25000);
  const seen = new Set();
  for (let k = 0; k < 3000; k++) {
    const p = slotPos(k);
    assert.ok(isWalk(p.ti, p.tj));
    assert.ok(p.tj <= GATE_J);
    const key = `${p.i.toFixed(2)},${p.j.toFixed(2)}`;
    assert.ok(!seen.has(key), 'duplicitní pozice ' + k);
    seen.add(key);
  }
});

test('prstenec roste s počtem návštěvníků a nikdy neklesá', () => {
  let prev = 0;
  for (const n of [0, 12, 100, 500, 1000, 4000, 10000, 25000]) {
    const r = regionFor(n);
    assert.ok(r >= prev && r >= 1 && r <= 16, `n=${n} r=${r}`);
    prev = r;
  }
  assert.equal(regionFor(12), 1);
  assert.ok(regionFor(4000) > regionFor(100));
});

test('každé obsazené místo leží v otevřené oblasti', () => {
  for (const n of [12, 300, 4000]) {
    const r = regionFor(n);
    for (let k = 0; k < n; k++) { const p = slotPos(k); assert.ok(inRegion(p.ti, p.tj, r), `n=${n} k=${k}`); }
  }
});

test('mince: 10 za návštěvníka minus utraceno', () => {
  const s = emptyState();
  for (let k = 0; k < 12; k++) addVisitor(s, 'user' + k);
  assert.equal(balance(s), 120);
  s.spent = 50;
  assert.equal(balance(s), 70);
});

test('jeden účet = jeden návštěvník, handle se čistí', () => {
  const s = emptyState();
  assert.equal(addVisitor(s, '@Jan.Novak'), 0);
  assert.equal(addVisitor(s, 'jan.novak'), -1);
  assert.equal(normHandle(' @A_b-C! '), 'a_bc');
  assert.ok(lookOf('jan.novak') >= 0 && lookOf('jan.novak') < 256);
});

test('veřejná data: dávky pokrývají všechny návštěvníky', () => {
  const s = emptyState();
  for (let k = 0; k < 5000; k++) addVisitor(s, 'u' + k);
  const d = publicData(s);
  assert.equal(d.zoo.visitors, 5000);
  assert.equal(d.looks.length, 2);
  assert.equal(d.shards.reduce((a, sh) => a + Object.keys(sh).length, 0), 5000);
  assert.deepEqual(d.zoo.lots['0,0'], { t: 'plot', id: 2 });
});

test('parcela má okraje uvnitř bloku', () => {
  const b = lotBox(-1, -1);
  assert.equal(b.i0, -5); assert.equal(b.i1, -1); assert.equal(b.ci, -2.5);
});
