// Jedno kolo synchronizace s Instagramem: followeři → návštěvníci, komentáře → jména a hlasy, nejlepší komentář, statická data webu.
// Prostředí: IG_ACCESS_TOKEN, IG_USER_ID, IG_MEDIA_IDS (čárkou; hlídané příspěvky), IG_RECENT (kolik posledních postů navíc, výchozí 3),
//            IG_REPLY=1 (veřejně odpovědět novým návštěvníkům), DRY_RUN=1 (nic neukládat a neposílat)
import fs from 'node:fs';
import { Instagram } from './instagram.mjs';
import { syncFollowers, applyComments, topComment, welcomeReply } from '../engine/ingest.js';
import { loadState, saveState, writePublic } from '../tools/lib.mjs';

if (!process.env.IG_ACCESS_TOKEN) { console.log('IG_ACCESS_TOKEN není nastaven, nic se nedělá (viz docs/INSTAGRAM.md).'); process.exit(0); }
const ig = new Instagram({ token: process.env.IG_ACCESS_TOKEN, userId: process.env.IG_USER_ID });
const DRY = !!process.env.DRY_RUN;
const state = loadState();
const snap = () => JSON.stringify({ ...state, updated: 0, _index: 0 });      // otisk stavu bez časového razítka: smyčka nezapisuje commity, když se nic nezměnilo
const before = snap();

const prof = await ig.profile();
const added = syncFollowers(state, prof.followers_count || 0);
console.log(`@${prof.username}: followerů ${prof.followers_count}, nových návštěvníků ${added}, celkem ${state.visitors.length}`);

const ids = new Set((process.env.IG_MEDIA_IDS || '').split(',').map((s) => s.trim()).filter(Boolean));
for (const m of await ig.recentMedia(Number(process.env.IG_RECENT || 3))) ids.add(m.id);
let claims = 0, votes = 0, best = null;
for (const id of ids) {
  const comments = await ig.comments(id);
  const r = applyComments(state, comments);
  claims += r.claims.length; votes += r.votes.length;
  const t = topComment(comments); if (t && (!best || t.likes > best.likes)) best = { ...t, media: id };
  if (process.env.IG_REPLY === '1') for (const c of r.claims) (state.pendingReplies ||= []).push({ id: c.commentId, h: c.handle, tries: 0 });
}
// odpovědi: nové i dřív nepovedené (fronta se uloží, takže se neztratí, když API selže)
if (process.env.IG_REPLY === '1' && !DRY && state.pendingReplies?.length) {
  const left = [];
  for (const p of state.pendingReplies.slice(0, 15)) {
    try { await ig.reply(p.id, welcomeReply(p.h)); console.log(`odpověď odeslána: @${p.h} (komentář ${p.id})`); }
    catch (e) { console.log(`odpověď selhala pro @${p.h}: ${e.message}`); if (++p.tries < 5) left.push(p); }
  }
  state.pendingReplies = [...left, ...state.pendingReplies.slice(15)];
}
if (best) state.topComment = best;
state.followersSeen = prof.followers_count;
const changed = snap() !== before;
if (changed) state.updated = new Date().toISOString();
console.log(`převzetí jména: ${claims}, hlasů: ${votes}, nejlepší komentář: ${best ? `@${best.username} (${best.likes} lajků)` : 'žádný'}`);
if (!DRY && changed) { saveState(state); writePublic(state); console.log('uloženo'); } else console.log(changed ? 'beze změny uloženo nebylo (DRY_RUN)' : 'beze změny');
