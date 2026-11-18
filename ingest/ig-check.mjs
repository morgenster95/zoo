// Ověření napojení (nic neukládá): node ingest/ig-check.mjs → účet, počet followerů a ID posledních příspěvků (do IG_MEDIA_IDS)
import { Instagram } from './instagram.mjs';
const ig = new Instagram({ token: process.env.IG_ACCESS_TOKEN, userId: process.env.IG_USER_ID });
const p = await ig.profile();
console.log(`účet @${p.username}, followerů ${p.followers_count}, příspěvků ${p.media_count}`);
for (const m of await ig.recentMedia(8)) console.log(`${m.id}  ${m.media_type}  ${m.timestamp}  ${(m.caption || '').slice(0, 50)}  ${m.permalink}`);
