// Pravidla pro napojení na Instagram (čisté funkce, bez sítě):
//  - počet followerů = počet návštěvníků: nový follower = anonymní návštěvník „visitor.N“ (nikdy neubývá)
//  - komentář s klíčovým slovem ZOO / VISIT = převzetí jména: první anonymní návštěvník dostane @jméno (a podle něj nový vzhled)
//  - při otevřeném hlasování o stavbách komentář s klíčovým slovem = hlas (viz engine/vote.js)
//  - otevřená otázka (jako ve vzoru): vyhrává komentář s nejvíc lajky (`topComment`)
import { addVisitor, normHandle, lookOf } from './state.js';
import { castVote } from './vote.js';

const CLAIM_RE = /\b(zoo|visit)\b/i;
export const anonName = (n) => 'visitor.' + String(n).padStart(5, '0');
export const isAnon = (v) => v.a === 1;

/** zajistí, že je návštěvníků aspoň tolik, kolik je followerů; vrací počet nově přidaných */
export function syncFollowers(state, followers, day = state.day) {
  let added = 0;
  state.followers = Math.max(state.followers || 0, followers);
  state._index ||= new Map(state.visitors.map((v, k) => [v.h, k]));
  while (state.visitors.length < followers) {
    const n = state.visitors.length + 1;
    const h = anonName(n);
    state.visitors.push({ h, d: day, l: lookOf(h), a: 1 });
    state._index.set(h, state.visitors.length - 1);
    added++;
  }
  return added;
}

/** komentář s ZOO/VISIT: převezme jméno prvního anonymního návštěvníka; bez volného se přidá nový (follower, který teprve přijde) */
export function claimName(state, username, text, day = state.day) {
  const h = normHandle(username);
  if (!h || !CLAIM_RE.test(String(text))) return null;
  state._index ||= new Map(state.visitors.map((v, k) => [v.h, k]));
  if (state._index.has(h)) return { handle: h, existing: true };
  const k = state.visitors.findIndex(isAnon);
  if (k >= 0) {
    state._index.delete(state.visitors[k].h);
    state.visitors[k] = { h, d: state.visitors[k].d, l: lookOf(h) };
    state._index.set(h, k);
    return { handle: h, index: k, renamed: true };
  }
  const idx = addVisitor(state, h, day);
  return idx >= 0 ? { handle: h, index: idx, renamed: false } : null;
}

/** nejlépe hodnocený komentář (bez odpovědí); při shodě nejstarší */
export function topComment(comments) {
  const top = comments.filter((c) => !c.parent_id && c.text).sort((a, b) => (b.like_count || 0) - (a.like_count || 0) || String(a.timestamp).localeCompare(String(b.timestamp)))[0];
  return top ? { id: top.id, username: top.username, text: top.text, likes: top.like_count || 0 } : null;
}

/** zpracuje nové komentáře (id ještě neviděné): převzetí jména, hlas; vrací co se stalo (pro odpovědi) */
export function applyComments(state, comments) {
  state.seen ||= [];
  const seen = new Set(state.seen);
  const out = { claims: [], votes: [], skipped: 0 };
  const fresh = comments.filter((c) => c.id && !seen.has(c.id)).sort((a, b) => String(a.timestamp).localeCompare(String(b.timestamp)));
  for (const c of fresh) {
    seen.add(c.id); state.seen.push(c.id);
    if (c.parent_id) { out.skipped++; continue; }
    const claim = claimName(state, c.username, c.text);
    if (claim && !claim.existing) out.claims.push({ ...claim, commentId: c.id });
    if (state.vote && !state.vote.closed) {
      const opt = castVote(state, normHandle(c.username), c.text);
      if (opt) out.votes.push({ handle: normHandle(c.username), key: opt.key, commentId: c.id });
    }
  }
  if (state.seen.length > 4000) state.seen = state.seen.slice(-3000);
  return out;
}
