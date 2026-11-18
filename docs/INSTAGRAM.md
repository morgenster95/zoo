# Napojení na Instagram (follower = návštěvník)

## Jak to funguje
| Co se stane na IG | Co se stane v zoo |
|---|---|
| Nový follower | Nový **anonymní návštěvník** („visitor.00042“) a +10 mincí. Počet nikdy neklesá (unfollow nic neubere). |
| Komentář se slovem **ZOO** nebo **VISIT** | Komentující dostane **své jméno**: první anonymní návštěvník se přejmenuje na @jméno a dostane vzhled podle něj. Bot veřejně odpoví („Welcome, @jméno!“, volitelně). |
| Komentář s klíčovým slovem při otevřeném hlasování (např. `CAFE`) | Hlas (jeden na účet, platí poslední), viz `docs/MECHANICS.md`. |
| Otevřená otázka (jako ve vzoru) | Vítězí **nejlépe hodnocený komentář** (`state.topComment`); ty ho potvrdíš a zapíšeš do hry. |

**Omezení Instagramu (podle mých znalostí, ověř):** API nedává seznam followerů ani upozornění na nový follow, jen celkový **počet** (`followers_count`). Proto jsou noví followeři zatím anonymní a jméno dostanou, až se přihlásí komentářem. Seznam followerů jinak získat nelze (a scraping porušuje podmínky IG).

## Co musíš udělat ty (já nemám přístup k tvým účtům)
1. **Profesionální účet** (Tvůrce nebo Firma), veřejný. Máš.
2. **Meta aplikace.** Můžeš **znovu použít tu z fronty** (developers.facebook.com) a přidat do ní nový účet, nebo založit novou. Typ Business.
3. **Firemní portfolio** (business.facebook.com): přidej Instagram účet zoo jako aktivum (Nastavení → Účty → Instagramové účty).
4. **Systémový uživatel + token** (Nastavení firmy → Uživatelé → Systémoví uživatelé): přiřaď mu aplikaci i IG účet a vygeneruj token s oprávněními `instagram_basic`, `instagram_manage_comments`, (pro budoucí automatické publikování `instagram_content_publish`). Systémový token nevyprší.
5. **ID IG účtu:** Business Suite → Nastavení → Instagramové účty (číslo). To je `IG_USER_ID`.
6. **GitHub repo → Settings → Secrets and variables → Actions**
   - Secrets: `IG_ACCESS_TOKEN`, `IG_USER_ID`
   - Variables: `IG_ENABLED=true`, `IG_MEDIA_IDS` (ID prvního reelu, viz níže), volitelně `IG_REPLY=1`
7. **Zjisti ID reelu:** v terminálu (token jen pro tuto relaci, nikam se neukládá)
   ```bash
   IG_ACCESS_TOKEN=... IG_USER_ID=... node ingest/ig-check.mjs
   ```
   vypíše účet, počet followerů a ID posledních příspěvků.
8. **Zkouška na sucho:** `DRY_RUN=1 IG_ACCESS_TOKEN=... IG_USER_ID=... node ingest/sync.mjs` (nic neuloží).

Tokeny patří jen do GitHub Secrets (repo je soukromé, ale přesto). Token nikdy nepiš do chatu ani do souborů.

## Soubory
`engine/ingest.js` (pravidla, testy), `ingest/instagram.mjs` (klient API), `ingest/sync.mjs` (jedno kolo), `ingest/ig-check.mjs` (ověření), `.github/workflows/sync.yml` (každých 10 min, spí, dokud není `IG_ENABLED`).

## Co ještě chybí
- **Nasazení webu** (Cloudflare Pages): bez něj nikdo mapu neuvidí. Workflow `deploy.yml` je připravený, čeká na tvůj účet.
- **Denní tah** (`tools/daily.mjs`) zatím spouštíš ručně; až poběží sync, přidáme ho na 13:00 UTC.
- **Zveřejňování z kódu** (`instagram_content_publish`) a reakce na stav hry v komentářích (odpovídání na hlasy) jsou další krok.
