# Web a hosting bez limitů Firebase

## Co bolelo ve frontě (z `fronta/docs/SCALING.md`, měřeno 11. 11. 2026)

| Problém | Důsledek |
|---|---|
| Firebase Hosting Spark: 360 MB přenosu/den, po vyčerpání web neodpovídá | reálně jen ~1 500–3 000 hráčů; při virálním postu web padne |
| `state.json` v gitu: 15 MB zpomaluje smyčku, 100 MB GitHub odmítne | při 10 000 hráčích za ~12 dní |
| Firestore + Google login jen pro „převzetí“ | další limity a závislost na jedné platformě |
| Cloudflare Pages zdarma: 500 sestavení/měsíc | nesmí se nasazovat po každém kole smyčky (~85×/den) |

Fronta sama došla k závěru: hra je tahová, takže **statické soubory na CDN** jsou nejlevnější a nejrychlejší.

## Doporučení pro ZOO (vše na Cloudflare, bez Firebase)

| Vrstva | Řešení | Proč |
|---|---|---|
| Kód + obrázky | **Cloudflare Pages** (nasazuje se jen při změně kódu, ne dat) | neomezený přenos statiky zdarma, 500 sestavení/měs. stačí, protože data se nenasazují |
| Data (soupiska, zápisy po dávkách, noviny) | **Cloudflare R2** (smyčka nahrává jen změněné soubory) | 10 GB, přenos ven zdarma; web čte JSON dávky ~25 návštěvníků |
| Převzetí návštěvníka, profil | **Cloudflare Worker + D1** (SQLite), ověření kódem z IG komentáře, **bez Google loginu** | zdarma stačí na desítky tisíc požadavků/den, žádný Firestore |
| Stav hry | **R2 jako zdroj pravdy** (sharded JSON); v gitu jen konfigurace, texty, denní snímek souhrnů | git nikdy nepřeroste 100 MB |
| Smyčka | GitHub Actions `loop.sh` jako ve frontě (veřejné repo = minuty zdarma) | ověřeno provozem |
| Obrázky na IG | GitHub Pages zrcadlo `marketing/promo/` jako ve frontě | funguje |

Alternativa pro login/profily: Supabase Auth (funguje na jakékoli doméně), ale jeho zdarma tarif má malý přenos; pro čtení dat se nehodí, jen pro přihlášení.

**Upozornění:** čísla Cloudflare limitů jsou z dokumentace fronty (stav 11/2026) a z paměti, před nasazením je ověřit v aktuálním ceníku.
Potřebujeme od uživatele: Cloudflare účet (Pages, R2, Workers, D1), doménu, token pro GitHub Actions.

## Datový model webu

Převzato z principu fronty (malé dávky, nikdy celá soupiska), konkrétní soubory viz „Stav implementace“ níže. Cache: dávky `max-age=60`, sprity `max-age=3600`, testovací data `npm run data:fake`.

## Stav implementace (17. 11. 2026)

Hotovo: statický web + data po dávkách (viz README). `VITE_DATA_BASE` přepíná odkud web čte data (výchozí `/data`, později R2).
Rozložení souborů, které web stahuje: `zoo.json` (malé, jen souhrn a obsah parcel), `looks/N.bin` (4 096 vzhledů po 2 bajtech = 8 kB, neměnné), `h/0..255.json` (hledání handle), `v/N.json` (karta podle indexu, 256 návštěvníků).
Při 100 000 návštěvnících: ~25 souborů vzhledů (200 kB) při startu, jinak jen malé dávky na požádání. Nasazení: `deploy.yml` (Cloudflare Pages) zapne proměnná `CF_PAGES_PROJECT`.
Další: smyčka (komentáře/follow → `state.json`), nahrávání dávek do R2 mimo build, převzetí návštěvníka (Worker + D1).
