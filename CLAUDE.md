# ZOO: pokyny pro Claude

Hra „každý follower = návštěvník zoo“, kopie mechaniky repa `morgenster95/fronta` (Mud & Iron). Čti `docs/DESIGN.md`, `docs/ARCHITECTURE.md`, `docs/ART.md`.

- Uživatel píše česky; hra a web jsou zatím otevřená otázka (viz DESIGN, otevřené otázky).
- Zdrojové repo fronty: `gh repo clone morgenster95/fronta`. Při přebírání kódu vždy odstranit boj/smrt, nic válečného.
- Grafika: světlá, hravá, izometrická 2:1, viz `docs/ART.md`. Generace v PixelLabu jsou omezené, před generováním vždy ledger (vzor ve frontě).
- Hosting: ne Firebase. Cloudflare Pages + R2 + Worker/D1 (viz ARCHITECTURE). Data nikdy neposílat jako jeden velký soubor, jen dávky.
- Tokeny a klíče jen v GitHub Secrets, nikdy do repa.
- Stav a rozhodnutí průběžně psát sem a do `docs/`.

## Stav (17. 11. 2026)

Fáze 1 hotová: `engine/` (layout, state, export, testy), `tools/` (fake-roster, build-data, init-state), `web/` (PixiJS), `art/proto/` (generátory + `export_assets.py`).
Pravidla světa: mapa je nekonečná mřížka, silnice každých 6 dlaždic, parcela = blok 5×5, místa návštěvníků jsou pevné pořadí (`slotTable`), oblast se otevírá podle počtu (`regionFor`).
Před změnou grafiky: `npm run assets` a ověřit měřítko (`art/proto/styles/scale_check_visitors_vs_animals.png`). Preview: `.claude/launch.json` → zoo-dev.
Pozor: v prohlížeči Claude se při skrytém panelu zpomalí `requestAnimationFrame`, výkon měřit přes `app.ticker.update()` v JS, ne podle fps.
Další kroky: Instagram (follower count → návštěvníci, komentář = převzetí jména), denní tah a noviny, hlasování o stavbách, Cloudflare nasazení.

## Umístění staveb na mapě (pravidlo)
Sprite má kotvu v předním rohu základny. Aby stál ve středu parcely (`ci, cj`), dáváme přední roh do `střed + w/64` na obou osách (`placeCentered` v `web/src/main.js`, w = šířka spritu). Plot výběhu je 4×4 dílky vystředěný v bloku 5×5 (po 0,5 dílku od silnic). Domek výběhu stojí vzadu (`střed − 0,8`), zvířata před ním. Pokladna stojí vedle cesty (`KI 4,2; KJ GATE_J+1,7`).
Ladění: `http://localhost:5173/?debug=lots` vykreslí hranice parcel a středy.

## Reely (viz docs/REEL.md)
Reel se natáčí v enginu: `web/reel.html` + `web/src/reel.js` kreslí snímek podle času (`window.__reel.setTime(t)`), plán a časování jsou v `web/src/reel-script.js`, hlas/hudba/efekty v `tools/reel-audio.py`, nahrávání `tools/record-reel.mjs` (puppeteer-core + ffmpeg). Vzorové video je ve složce projektu (`ScreenRecording_*.mp4`, není v gitu).
Pravidlo hry z reelu: start = 500 mincí (`START_COINS`), 1 follower = 10 mincí, plot stojí 200, sdílení = +20 mincí (autobus).
Pozor: ve videu dělat bránu a zvířata jako ve hře (`engine/place.js`), nic nekreslit zvlášť.

## STAV K 18. 11. 2026 (čti první)
**Hotovo:** engine (`engine/`: layout, state, vote, catalog, place, ingest; 25 testů + `ingest/instagram.test.mjs`), web (PixiJS, `web/`), grafika (`art/`, PixelLab chunky sprity), reel „Day 1“ (`marketing/reels/hook/`, verze s hlasem Andrew `hook_day1_v4.mp4` a holčičkou `hook_day1_v5_girl.mp4`), popisek (`caption.md`), profilovky a náhledovka (`marketing/profile/`, `marketing/reels/hook/cover_day1.png`), napojení Instagramu (`@zoofollow`, workflow `sync`, GitHub Secrets/Variables nastavené, bot odpovídá jen na komentář se ZOO/VISIT).
**Pravidla hry:** start 500 mincí, 1 follower = 1 návštěvník = 10 mincí (nikdy neubývá), plot 200, sdílení = +20 (autobus), komentář ZOO = jméno, otevřená otázka: vyhrává nejlépe hodnocený komentář (`state.topComment`), potvrzuje majitel. Katalog staveb: `engine/catalog.js`.
**Další kroky:** (1) nasadit web na Cloudflare Pages (`deploy.yml`, čeká na Cloudflare účet + `CF_PAGES_PROJECT` + tajemství), (2) Day 2 reel podle komentáře „Lions“ (700 mincí, teď ~520), (3) denní tah automaticky (`tools/daily.mjs` na 13:00 UTC), (4) vyměnit token a PixelLab klíč, které byly v chatu, (5) vybrat hlas reelu (Andrew vs. holčička), (6) další dílčí věci v `docs/`.
**Pozor:** frontový token a ten zoo jsou od stejného systémového uživatele „front-bot“; nikdy nemačkat „Odvolat tokeny“, rozbilo by to oba. Klíče nikdy do repa. PixelLab: jen přes `tools/pixellab.py` s ledgerem, jeden sheet = jedna úloha; zůstatek ~1 130 generací.
Podrobnosti: `docs/DESIGN.md`, `ARCHITECTURE.md`, `ART.md`, `MECHANICS.md`, `REEL.md`, `INSTAGRAM.md`.
