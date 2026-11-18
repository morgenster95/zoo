import test from 'node:test';
import assert from 'node:assert/strict';
import { Instagram } from './instagram.mjs';

const fakeFetch = (pages) => { const calls = []; const f = async (url, opts) => { calls.push({ url: String(url), opts }); const p = pages.shift(); return { json: async () => p }; }; f.calls = calls; return f; };

test('profil a komentáře se stránkováním a tokenem v parametru; token není v kódu', async () => {
  const f = fakeFetch([{ username: 'zoo', followers_count: 7 }, { data: [{ id: '1', text: 'a' }], paging: { next: 'https://graph.facebook.com/next' } }, { data: [{ id: '2', text: 'b' }] }]);
  const ig = new Instagram({ token: 'T', userId: 'U', fetchImpl: f });
  assert.equal((await ig.profile()).followers_count, 7);
  assert.deepEqual((await ig.comments('M')).map((c) => c.id), ['1', '2']);
  assert.ok(f.calls[0].url.includes('access_token=T') && f.calls[0].url.includes('/U?'));
});

test('chyba API vyhodí výjimku, odpověď jde přes POST s Bearer tokenem', async () => {
  const bad = new Instagram({ token: 'T', userId: 'U', fetchImpl: fakeFetch([{ error: { message: 'Invalid token' } }]) });
  await assert.rejects(() => bad.profile(), /Invalid token/);
  const f = fakeFetch([{ id: 'r1' }]); const ig = new Instagram({ token: 'T', userId: 'U', fetchImpl: f });
  await ig.reply('C1', 'hi');
  assert.equal(f.calls[0].opts.method, 'POST'); assert.equal(f.calls[0].opts.headers.Authorization, 'Bearer T');
  assert.ok(f.calls[0].url.endsWith('/C1/replies'));
});

test('bez tokenu se klient nevytvoří', () => { assert.throws(() => new Instagram({}), /Chybí/); });
