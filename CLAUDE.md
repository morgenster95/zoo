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
