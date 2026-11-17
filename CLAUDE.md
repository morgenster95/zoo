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
