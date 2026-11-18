import test from 'node:test';
import assert from 'node:assert/strict';
import { slotTable, slotPos, regionFor, isWalk, isRoad, ringOf, GATE_J, lotBox, inRegion } from './layout.js';
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
  assert.equal(balance(s), 620);               // 500 počáteční fond + 12 × 10
  s.start = 0;
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

import { CATALOG } from './catalog.js';
import { openVote, castVote, resolveVote, tally, freePlots, ensurePlots } from './vote.js';

function zooWith(n) { const s = emptyState(); s.start = 0; for (let k = 0; k < n; k++) addVisitor(s, 'v' + k); return s; }

test('hlasování: nabídne se jen to, na co jsou mince', () => {
  const s = zooWith(12);                       // 120 mincí
  assert.throws(() => openVote(s, ['cafe', 'bench']), /dražší/);
  openVote(s, ['bench', 'flowers', 'cart']);
  assert.equal(s.vote.options.length, 3);
  assert.throws(() => openVote(s, ['bench', 'flowers']), /už běží/);
});

test('hlas: jeden na účet, platí poslední, jen návštěvník, nejasné se ignoruje', () => {
  const s = zooWith(12);
  openVote(s, ['bench', 'flowers', 'cart']);
  assert.equal(castVote(s, 'v1', 'I vote FLOWERS!').key, 'FLOWERS');
  assert.equal(castVote(s, 'v1', 'no wait, ICECREAM').key, 'ICECREAM');
  assert.equal(castVote(s, 'stranger', 'BENCH'), null);
  assert.equal(castVote(s, 'v2', 'BENCH and FLOWERS'), null);
  assert.deepEqual(tally(s.vote), { BENCH: 0, FLOWERS: 0, ICECREAM: 1 });
});

test('vyhodnocení: vítěz se zaplatí společnými mincemi a stojí hned na volné parcele', () => {
  const s = zooWith(12);
  openVote(s, ['bench', 'flowers', 'cart']);
  castVote(s, 'v1', 'ICECREAM'); castVote(s, 'v2', 'ICECREAM'); castVote(s, 'v3', 'BENCH');
  const r = resolveVote(s, 2);
  assert.equal(r.winner, 'ICECREAM'); assert.equal(r.price, 100);
  assert.equal(balance(s), 20);
  assert.equal(s.lots[r.lot].sprite, 'd_kiosk');
  assert.ok(freePlots(s).length >= 2, 'vždy aspoň 2 volné parcely');
  assert.equal(s.vote.closed, true);
});

test('bez hlasů vyhrává první možnost, kterou majitel nabídl', () => {
  const s = zooWith(12);
  openVote(s, ['flowers', 'bench']);
  assert.equal(resolveVote(s).winner, 'FLOWERS');
});

test('mince se nikdy nedostanou do mínusu a plocha se dočasně rozšíří, když dojdou parcely', () => {
  const s = zooWith(200);                      // 2000 mincí
  for (let k = 0; k < 6; k++) { s.vote = null; const aff = ['bench', 'flowers'].filter((i) => CATALOG[i].price <= balance(s)); if (aff.length < 2) break; openVote(s, aff); resolveVote(s); }
  assert.ok(balance(s) >= 0);
  assert.ok(freePlots(s).length >= 2);
});

test('když dojdou volné bloky, mapa se rozšíří o prstenec a parcely jsou vždy aspoň 2', () => {
  const s = zooWith(12);
  for (let k = 0; k < 8; k++) { s.vote = null; openVote(s, ['bench', 'lamp']); resolveVote(s); s.spent = 0; }   // 8 staveb v malé zoo
  assert.ok(freePlots(s).length >= 2);
  assert.ok(s.ring >= 2, 'ring=' + s.ring);
});

test('vylepšení vstupu se zaplatí, ale nezabere parcelu', () => {
  const s = zooWith(200);
  const plotsBefore = freePlots(s).length;
  openVote(s, ['stonegate', 'bench']);
  const r = resolveVote(s);
  assert.equal(r.winner, 'GATE');
  assert.equal(s.upgrades.gate, 'bp_gate');
  assert.equal(r.lot, null);
  assert.ok(freePlots(s).length >= plotsBefore);
  assert.equal(balance(s), 2000 - 1500);
});

import { placeLot, fenceOf, ANIMAL_MARGIN, ANIMAL_GAP } from './place.js';
import { START_LOTS, lotBox as lb } from './layout.js';

test('zvířata zůstávají uvnitř plotu s odstupem, daleko od sebe a od domku, nikdy na silnici', () => {
  const widths = { bp_lodge: 58, bp_barn: 60 };
  for (const lot of [START_LOTS['-1,-1'], { t: 'paddock', animals: ['elephant', 'elephant', 'zebra', 'lion'] }, { t: 'paddock', animals: ['elephant', 'elephant'], house: 'bp_barn' }, { t: 'paddock', animals: ['monkey', 'monkey', 'monkey'], house: 'bp_lodge' }, START_LOTS['0,-1']]) {
    for (const [a, b] of [[-1, -1], [0, -1], [2, 3], [-4, -2]]) {
      const key = `${a},${b}`, r = placeLot(a, b, lot, key, (n) => widths[n] || 0);
      const f = fenceOf(a, b), animals = r.items.filter((x) => x.role === 'animal');
      for (const an of animals) {
        assert.ok(an.i >= f.i0 + (lot.t === 'pond' ? 0.4 : ANIMAL_MARGIN) - 1e-9 && an.i <= f.i1 - 0.4, `i uvnitř ${key}`);
        assert.ok(an.j >= f.j0 + 0.4 && an.j <= f.j1 - 0.4, `j uvnitř ${key}`);
        assert.ok(!isRoad(Math.floor(an.i), Math.floor(an.j)), 'zvíře na silnici');
      }
      for (let p = 0; p < animals.length; p++) for (let q = p + 1; q < animals.length; q++) assert.ok(Math.hypot(animals[p].i - animals[q].i, animals[p].j - animals[q].j) >= 0.9, 'zvířata se překrývají');
    }
  }
});

test('parcela bez obsahu je volná louka; plot má cedulku', () => {
  assert.equal(placeLot(0, 0, undefined, '0,0').free, true);
  assert.ok(placeLot(0, 0, { t: 'plot', id: 1 }, '0,0').items.some((x) => x.role === 'sign'));
});

import { syncFollowers, claimName, topComment, applyComments, anonName } from './ingest.js';

test('follower = anonymní návštěvník, počet nikdy neklesá', () => {
  const s = emptyState();
  assert.equal(syncFollowers(s, 5), 5);
  assert.equal(s.visitors[0].h, anonName(1)); assert.equal(s.visitors[0].a, 1);
  assert.equal(syncFollowers(s, 3), 0);                       // unfollow nic neubere
  assert.equal(s.visitors.length, 5);
  assert.equal(syncFollowers(s, 8), 3);
  assert.equal(balance(s), 500 + 80);
});

test('komentář se slovem ZOO převezme jméno prvního anonymního návštěvníka', () => {
  const s = emptyState(); syncFollowers(s, 3);
  const r = claimName(s, 'Jane.Doe', 'ZOO! count me in');
  assert.equal(r.handle, 'jane.doe'); assert.equal(r.renamed, true);
  assert.equal(s.visitors.length, 3); assert.equal(s.visitors[0].h, 'jane.doe'); assert.ok(!s.visitors[0].a);
  assert.equal(claimName(s, 'jane.doe', 'zoo').existing, true);       // podruhé nic
  assert.equal(claimName(s, 'bob', 'nice video'), null);               // bez klíčového slova nic
});

test('komentáře se zpracují jednou; odpovědi se přeskočí; hlasuje jen návštěvník', () => {
  const s = emptyState(); syncFollowers(s, 2);
  const { openVote } = { openVote: null };
  const cs = [{ id: '1', username: 'amy', text: 'zoo', timestamp: '2026-11-18T10:00:00' }, { id: '2', username: 'amy', text: 'zoo', parent_id: '1', timestamp: '2026-11-18T10:01:00' }];
  const a = applyComments(s, cs), b = applyComments(s, cs);
  assert.equal(a.claims.length, 1); assert.equal(a.skipped, 1); assert.equal(b.claims.length, 0);
});

test('nejlépe hodnocený komentář vyhrává; při shodě nejstarší', () => {
  const t = topComment([{ id: 'a', username: 'x', text: 'one', like_count: 5, timestamp: '2026-11-18T11:00' }, { id: 'b', username: 'y', text: 'two', like_count: 9, timestamp: '2026-11-18T12:00' }, { id: 'c', username: 'z', text: 'three', like_count: 9, timestamp: '2026-11-18T09:00' }, { id: 'd', username: 'q', text: 'reply', like_count: 99, parent_id: 'a' }]);
  assert.equal(t.id, 'c'); assert.equal(t.likes, 9);
});

import { welcomeReply } from './ingest.js';
test('uvítací odpověď: vždy obsahuje @jméno, je krátká a střídá se', () => {
  const set = new Set();
  for (const h of ['anna', 'bob', 'cyril', 'dana', 'eva', 'filip', 'gita', 'hugo']) { const t = welcomeReply(h); assert.ok(t.includes('@' + h) && t.length < 100); set.add(t.replace(h, '')); }
  assert.ok(set.size >= 3);
  assert.equal(welcomeReply('anna'), welcomeReply('anna'));
});
